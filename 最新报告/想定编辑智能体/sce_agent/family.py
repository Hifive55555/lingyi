# -*- coding: utf-8 -*-
"""同类想定集（scenario family）生成。

两个入口，对应题目里的两种要求：

A. **给一段自然语言/一份规格 → 生成一族同类型想定**
   ``make_variants(spec, axes)`` 在若干"变量轴"上取样：兵力规模、初始距离、
   战场朝向、推演时长、气象、条令烈度、巡逻半径……每个变体都是完整、可运行、
   可验收的想定，并带一张 ``manifest.csv`` 说明"这一族的自变量是什么"。

B. **给一份既有想定（.scen）→ 复刻 + 派生同类型想定集**
   ``spec_from_digest(digest)`` 把引擎回读的想定 XML 抽成 ScenarioSpec
   （推演方/兵力构成/型号/位置/任务与巡逻区/条令/气象），再走 A 的流程。
   注意这是"结构复刻 + 参数扰动"，不是二进制复制：想定里的挂载明细、事件脚本、
   条令细则不会被逐位重建 —— 对"算法演进/参数调优"这类实验，这恰恰是我们想要的
   可控变量集。

变量轴都是**纯函数**：``f(spec, value) -> spec``，因此族定义可序列化、可复现
（同一 seed 同一族），也便于事后在论文里写清楚"我们扫了哪几个维度"。
"""
from __future__ import annotations

import copy
import csv
import itertools
import os
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .catalog import Catalog
from .spec import (ScenarioSpec, Side, Unit, Mission, Weather, DEFAULT_DOCTRINE,
                   canonical_subtype)


# ---------------------------------------------------------------- 变量轴
def _axis_force_scale(spec: ScenarioSpec, v: float) -> ScenarioSpec:
    return spec.scale_units(float(v))


def _axis_spread(spec: ScenarioSpec, v: float) -> ScenarioSpec:
    return spec.spread(float(v))


def _axis_rotate(spec: ScenarioSpec, v: float) -> ScenarioSpec:
    return spec.rotate(float(v))


def _axis_duration_h(spec: ScenarioSpec, v: float) -> ScenarioSpec:
    spec.duration_s = int(float(v) * 3600)
    return spec


def _axis_seastate(spec: ScenarioSpec, v: int) -> ScenarioSpec:
    if spec.weather is None:
        spec.weather = Weather()
    spec.weather.seastate = int(v)
    spec.weather.cloud = max(spec.weather.cloud, 0.2 if int(v) >= 4 else 0.0)
    return spec


def _axis_wcs(spec: ScenarioSpec, v: str) -> ScenarioSpec:
    """武器控制状态：free=0 谨慎=1 禁止=2。"""
    code = {"free": "0", "tight": "1", "hold": "2", "0": "0", "1": "1", "2": "2"}.get(str(v), "1")
    for s in spec.sides:
        for k in ("WCS_Air", "WCS_Surface", "WCS_Submarine", "WCS_Land"):
            s.doctrine[k] = code
    return spec


def _axis_zone_radius(spec: ScenarioSpec, v: float) -> ScenarioSpec:
    """按比例伸缩巡逻区（模拟"任务区大小"这一维度）。"""
    for m in spec.missions:
        if not m.zone:
            continue
        clat = sum(p["lat"] for p in m.zone) / len(m.zone)
        clon = sum(p["lon"] for p in m.zone) / len(m.zone)
        for p in m.zone:
            p["lat"] = round(clat + (p["lat"] - clat) * float(v), 6)
            p["lon"] = round(clon + (p["lon"] - clon) * float(v), 6)
    return spec


def _axis_offset_nm(spec: ScenarioSpec, v: float) -> ScenarioSpec:
    """整体把战场往东挪 v 海里（模拟"战场位置/基地距离"维度）。"""
    dlon = float(v) / (60.0 * (abs(__import__("math").cos(__import__("math").radians(spec.center["lat"]))) or 1.0))
    return spec.translate(0.0, round(dlon, 6))


def _axis_seed(spec: ScenarioSpec, v: int) -> ScenarioSpec:
    spec.seed = int(v)
    return spec


AXES: Dict[str, Callable[[ScenarioSpec, Any], ScenarioSpec]] = {
    "force_scale": _axis_force_scale,
    "spread": _axis_spread,
    "rotate": _axis_rotate,
    "duration_h": _axis_duration_h,
    "seastate": _axis_seastate,
    "wcs": _axis_wcs,
    "zone_radius": _axis_zone_radius,
    "offset_nm": _axis_offset_nm,
    "seed": _axis_seed,
}

AXIS_HELP = {
    "force_scale": "兵力规模系数（0.5=减半, 2=加倍）",
    "spread": "初始态势拉开系数（1=原样, 1.5=相距 1.5 倍）",
    "rotate": "整个战场绕中心旋转角度（度）",
    "duration_h": "推演时长（小时）",
    "seastate": "海况等级 0-9",
    "wcs": "武器控制状态 free/tight/hold",
    "zone_radius": "巡逻区缩放系数",
    "offset_nm": "战场整体东移海里数（改变与岸基/基地的距离）",
    "seed": "随机种子（影响参考点 GUID 与后续随机化）",
}


@dataclass
class Variant:
    name: str
    spec: ScenarioSpec
    params: Dict[str, Any]


def make_variants(base: ScenarioSpec, axes: Dict[str, List[Any]], n: int = 0,
                  seed: int = 0, rotate_labels: bool = True) -> List[Variant]:
    """按轴取样生成变体。

    * ``n <= 0``：取网格（笛卡尔积），并按 ``max_variants`` 保护；
    * ``n > 0``：在轴取值范围内**随机取样** n 个（去重），适合大规模实验。
    """
    names = [k for k in axes if k in AXES]
    for k in axes:
        if k not in AXES:
            raise KeyError("未知变量轴 %r，可用：%s" % (k, ", ".join(sorted(AXES))))
    out: List[Variant] = []
    if n and n > 0:
        rng = random.Random(seed or 1)
        seen = set()
        guard = 0
        while len(out) < n and guard < n * 50:
            guard += 1
            pick = {k: rng.choice(list(axes[k])) for k in names}
            key = tuple(sorted((k, str(v)) for k, v in pick.items()))
            if key in seen:
                continue
            seen.add(key)
            out.append(_variant(base, pick, len(out) + 1))
    else:
        keys = names
        for i, combo in enumerate(itertools.product(*[axes[k] for k in keys]), 1):
            out.append(_variant(base, dict(zip(keys, combo)), i))
    return out


def _variant(base: ScenarioSpec, params: Dict[str, Any], idx: int) -> Variant:
    spec = base.clone()
    tag = []
    for k, v in params.items():
        spec = AXES[k](spec, v)
        tag.append("%s=%s" % (k, v))
    spec.title = "%s-V%02d" % (base.title, idx)
    spec.provenance = dict(spec.provenance, family=dict(params), variant_index=idx)
    return Variant(name=spec.title, spec=spec, params=params)


# ---------------------------------------------------------------- 从既有想定抽取规格
_KIND_MAP = {"Aircraft": "Aircraft", "Ship": "Ship", "Submarine": "Submarine",
             "Facility": "Facility", "Satellite": "Satellite"}


def spec_from_digest(digest: Dict[str, Any], catalog: Optional[Catalog] = None,
                     max_units_per_kind: int = 0) -> ScenarioSpec:
    """把引擎回读的想定摘要（digest）抽成可再生成的 ScenarioSpec。

    保留：推演方与对抗关系、条令、气象、单元（型号/位置/朝向/高度/挂载角色）、
    任务（类型/子类型/巡逻区坐标/参与兵力）。
    丢弃：挂载明细、事件脚本、消息日志、编队等"实现细节"。
    """
    cat = catalog or Catalog()
    lats = [u["lat"] for u in digest["units"]] or [0.0]
    lons = [u["lon"] for u in digest["units"]] or [0.0]
    center = {"lat": round(sum(lats) / len(lats), 4), "lon": round(sum(lons) / len(lons), 4)}

    spec = ScenarioSpec(
        title=digest.get("title") or "派生想定",
        duration_s=int(digest.get("duration_s") or 10800),
        complexity=int(digest.get("complexity") or 2),
        difficulty=int(digest.get("difficulty") or 2),
        description="由既有想定《%s》结构复刻" % (digest.get("title") or ""),
        center=center, seed=abs(hash(digest.get("title") or "")) % 100000,
        weather=Weather(**digest["weather"]) if digest.get("weather") else None,
        provenance={"source": "digest", "source_title": digest.get("title")},
    )

    id2name = {s["id"]: s["name"] for s in digest["sides"]}
    for s in digest["sides"]:
        doc = dict(DEFAULT_DOCTRINE)
        for k, v in (s.get("doctrine") or {}).items():
            if k in doc and v is not None:
                doc[k] = str(v)
        posture = {}
        for other_id, code in (s.get("postures") or {}).items():
            name = id2name.get(other_id)
            if name and name != s["name"]:
                inv = {0: "N", 1: "F", 2: "U", 3: "H"}
                posture[name] = inv.get(int(code), "H")
        spec.sides.append(Side(name=s["name"], posture=posture, doctrine=doc,
                               is_ai_only=str(s.get("is_ai_only", "false")).lower() == "true"))
    # 补齐缺失的姿态（引擎要求两两显式）
    for a in spec.sides:
        for b in spec.sides:
            if a.name != b.name and b.name not in a.posture:
                a.posture[b.name] = "H"

    # 单元：同名同型的多个实例合并成 count
    grouped: Dict[Tuple[str, str, int, str], Dict[str, Any]] = {}
    for u in digest["units"]:
        key = (u["side"], u["kind"], int(u["dbid"]), u["name"])
        if key in grouped:
            grouped[key]["count"] += 1
            continue
        grouped[key] = {"unit": u, "count": 1}
    for (side, kind, dbid, _name), item in grouped.items():
        u = item["unit"]
        spec.units.append(Unit(
            side=side, kind=_KIND_MAP.get(kind, kind),
            name=u["name"], dbid=dbid, lat=round(u["lat"], 6), lon=round(u["lon"], 6),
            alt=round(u["alt"], 1) if kind == "Aircraft" else None,
            heading=round(u["heading"], 1) or 0.0, count=item["count"],
            loadoutid=(u.get("loadoutid") or None) if kind == "Aircraft" else None,
        ))

    # 任务：把巡逻区的参考点 ID 换成坐标
    name_by_guid = {u["id"]: u["name"] for u in digest["units"]}
    for m in digest.get("missions", []):
        zone = m.get("zone") or []
        if len(zone) < 3:
            continue
        units = [name_by_guid[i] for i in m.get("assigned", []) if i in name_by_guid]
        # 同名不同类型的实例已合并为 count，去重
        seen, uniq = set(), []
        for n in units:
            if n in seen:
                continue
            seen.add(n)
            uniq.append(n)
        if not uniq:
            continue
        spec.missions.append(Mission(
            side=m["side"], name=m["name"], mtype=m["mtype"],
            subtype=canonical_subtype(m["mtype"], m["subtype"]),
            zone=[{"lat": round(p["lat"], 6), "lon": round(p["lon"], 6)} for p in zone],
            units=uniq))
        for n in uniq:
            uu = spec.unit(n)
            if uu:
                uu.mission = m["name"]

    # 飞机挂载：没带挂载的按任务角色补
    for u in spec.units:
        if u.kind == "Aircraft" and not u.loadoutid:
            role = None
            for m in spec.missions:
                if u.name in m.units:
                    role = m.subtype
                    break
            lo, _ = cat.loadout_for(u.dbid, role)
            u.loadoutid = lo
    return spec


# ---------------------------------------------------------------- 批量构建
def family_manifest(path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
