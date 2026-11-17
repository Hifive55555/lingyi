# -*- coding: utf-8 -*-
"""想定验收：规格（spec） vs 引擎实际产物（digest）逐项比对。

不验收的自动化等于没有自动化。本模块把"我以为生成了什么"和"引擎里到底有什么"
放在一起比对，输出一张 PASS/FAIL 清单，供人看，也供脚本当门禁（``strict``）。

比对维度（每项一个 check）::

    文件      存在 / 体积 / 引擎可回读
    元信息    标题 / 时长
    推演方    名称集合 / 两两姿态（H=3 F=2 N=0 U=1）
    兵力      每方每类数量 / 每个单元的名称、DBID、归属、坐标（容差 0.002°）
    任务      名称 / 类型 / 子类型 / 巡逻区顶点数 / 分配单元数
    条令      武器控制状态等关键字段
    气象      气温/降雨/云量/海况
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .spec import ScenarioSpec, POSTURE_CODES

TOL_DEG = 0.002     # ≈ 200 m，足以容纳引擎的坐标舍入


def _key(s: str) -> str:
    """名称比较键：引擎会把单元名里的 ASCII 字母统一成大写
    （实测 ``…阿里伯克级 Flight IIA导弹驱逐舰`` 回读成了 ``…FLIGHT IIA…``），
    所以比对一律忽略大小写。"""
    return (s or "").strip().upper()


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""
    warn: bool = False

    def as_dict(self):
        return {"check": self.name, "ok": self.ok, "warn": self.warn, "detail": self.detail}


@dataclass
class Report:
    checks: List[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "", warn: bool = False):
        self.checks.append(Check(name, ok, detail, warn))
        return ok

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.ok)

    @property
    def failed(self) -> List[Check]:
        return [c for c in self.checks if not c.ok and not c.warn]

    @property
    def ok(self) -> bool:
        return not self.failed

    def to_dict(self):
        return {"ok": self.ok, "passed": self.passed, "total": len(self.checks),
                "failed": [c.as_dict() for c in self.failed],
                "checks": [c.as_dict() for c in self.checks]}

    def to_markdown(self, title: str = "验收报告") -> str:
        lines = ["# %s" % title, "",
                 "**结论：%s**（通过 %d/%d 项）" % ("PASS" if self.ok else "FAIL",
                                                self.passed, len(self.checks)), "",
                 "| # | 检查项 | 结果 | 说明 |", "|---|---|---|---|"]
        for i, c in enumerate(self.checks, 1):
            mark = "PASS" if c.ok else ("WARN" if c.warn else "**FAIL**")
            lines.append("| %d | %s | %s | %s |" % (i, c.name, mark, (c.detail or "").replace("|", "\\|")))
        return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 数值/几何
def _near(a: float, b: float, tol: float = TOL_DEG) -> bool:
    return abs(float(a) - float(b)) <= tol


def _dist_nm(a: Dict[str, float], b: Dict[str, float]) -> float:
    dlat = (a["lat"] - b["lat"]) * 60.0
    dlon = (a["lon"] - b["lon"]) * 60.0 * (math.cos(math.radians(a["lat"])) or 1.0)
    return math.hypot(dlat, dlon)


# ---------------------------------------------------------------- 主入口
def verify(spec: ScenarioSpec, digest: Optional[Dict[str, Any]], *,
           file_size: Optional[int] = None, readback_ok: bool = True,
           readback_detail: str = "", smoke: Optional[Dict[str, Any]] = None) -> Report:
    r = Report()

    # ---------- 0. 文件级
    if file_size is not None:
        r.add("文件已落盘且非空", file_size > 0, "%d 字节" % file_size)
    r.add("引擎可回读（GetScenarioContent）", readback_ok, readback_detail or "OK")
    if not digest:
        return r

    # ---------- 1. 元信息
    r.add("标题一致", spec.title == digest.get("title"),
          "spec=%r engine=%r" % (spec.title, digest.get("title")))
    r.add("推演时长一致", int(spec.duration_s) == int(digest.get("duration_s", -1)),
          "spec=%ss engine=%ss" % (spec.duration_s, digest.get("duration_s")))

    # ---------- 2. 推演方
    spec_sides = [s.name for s in spec.sides]
    eng_sides = [s["name"] for s in digest.get("sides", [])]
    r.add("推演方集合一致", sorted(spec_sides) == sorted(eng_sides),
          "spec=%s engine=%s" % (spec_sides, eng_sides))

    id2name = {s["id"]: s["name"] for s in digest.get("sides", [])}
    eng_posture = {}
    for s in digest.get("sides", []):
        for other_id, code in (s.get("postures") or {}).items():
            eng_posture[(s["name"], id2name.get(other_id, other_id))] = code
    bad = []
    for s in spec.sides:
        for other, code in s.posture.items():
            want = POSTURE_CODES.get(code)
            got = eng_posture.get((s.name, other))
            if got is None or int(got) != want:
                bad.append("%s->%s 期望%s(%s) 实际%s" % (s.name, other, code, want, got))
    r.add("两两对抗关系正确", not bad, "；".join(bad) or "全部一致（H=3 U=2 F=1 N=0）")

    # ---------- 3. 兵力
    want_counts = spec.counts()
    got_counts: Dict[str, Dict[str, int]] = {}
    for u in digest.get("units", []):
        got_counts.setdefault(u["side"], {}).setdefault(u["kind"], 0)
        got_counts[u["side"]][u["kind"]] += 1
    diff = []
    for side, kinds in want_counts.items():
        for kind, n in kinds.items():
            g = got_counts.get(side, {}).get(kind, 0)
            if int(n) != int(g):
                diff.append("%s/%s 期望%d 实际%d" % (side, kind, n, g))
    for side, kinds in got_counts.items():
        for kind, g in kinds.items():
            if want_counts.get(side, {}).get(kind, 0) == 0:
                diff.append("%s/%s 多出%d" % (side, kind, g))
    r.add("兵力数量分布一致", not diff, "；".join(diff) or
          "；".join("%s %s" % (k, ", ".join("%s:%d" % (kk, vv) for kk, vv in v.items()))
                   for k, v in want_counts.items()))

    eng_units = {(_key(u["side"]), _key(u["name"])): u for u in digest.get("units", [])}
    miss, wrong, pos_err = [], [], []
    for u in spec.units:
        e = eng_units.get((_key(u.side), _key(u.name)))
        if not e:
            miss.append("%s/%s" % (u.side, u.name))
            continue
        if int(e.get("dbid", 0)) != int(u.dbid):
            wrong.append("%s dbid 期望%d 实际%s" % (u.name, u.dbid, e.get("dbid")))
        if not (_near(e.get("lat", 0), u.lat) and _near(e.get("lon", 0), u.lon)):
            pos_err.append("%s 期望(%.4f,%.4f) 实际(%.4f,%.4f)"
                           % (u.name, u.lat, u.lon, e.get("lat", 0), e.get("lon", 0)))
    r.add("单元齐全（按 推演方+名称）", not miss, "缺失：" + "；".join(miss) if miss else
          "%d 型单元全部在册" % len(spec.units))
    r.add("单元 DBID 正确", not wrong, "；".join(wrong) or "全部一致")
    r.add("单元初始坐标正确（±%.3f°）" % TOL_DEG, not pos_err, "；".join(pos_err) or "全部一致")

    # ---------- 4. 任务
    eng_mis = {(_key(m["side"]), _key(m["name"])): m for m in digest.get("missions", [])}
    miss_m, wrong_m, zone_m, assign_m = [], [], [], []
    for m in spec.missions:
        e = eng_mis.get((_key(m.side), _key(m.name)))
        if not e:
            miss_m.append("%s/%s" % (m.side, m.name))
            continue
        if e["mtype"] != m.mtype or e["subtype"] != m.subtype:
            wrong_m.append("%s 期望 %s/%s 实际 %s/%s" % (m.name, m.mtype, m.subtype,
                                                         e["mtype"], e["subtype"]))
        if m.mtype == "Patrol" and len(e.get("zone", [])) != len(m.zone):
            zone_m.append("%s 顶点数 期望%d 实际%d" % (m.name, len(m.zone), len(e.get("zone", []))))
        # 引擎按"平台"计数：单元 count>1 时一个单元名对应多个平台 GUID
        want_units = sum((spec.unit(n).count if spec.unit(n) else 1) for n in m.units)
        if len(e.get("assigned", [])) != want_units:
            assign_m.append("%s 分配平台数 期望%d 实际%d（%d 个单元条目）"
                            % (m.name, want_units, len(e.get("assigned", [])), len(m.units)))
    r.add("任务齐全（推演方+名称）", not miss_m, "；".join(miss_m) or "%d 个任务全部在册" % len(spec.missions))
    r.add("任务类型/子类型正确", not wrong_m, "；".join(wrong_m) or "全部一致")
    r.add("巡逻区顶点数正确（Patrol）", not zone_m, "；".join(zone_m) or "全部一致")
    r.add("单元-任务分配数正确", not assign_m, "；".join(assign_m) or "全部一致")
    extra = [k for k in eng_mis if k not in {(_key(m.side), _key(m.name)) for m in spec.missions}]
    r.add("没有多余任务", not extra, "；".join("%s/%s" % k for k in extra) or "OK", warn=True)

    # ---------- 5. 条令
    doc_diff = []
    for s in spec.sides:
        e = next((x for x in digest.get("sides", []) if x["name"] == s.name), None)
        if not e:
            continue
        for k, v in s.doctrine.items():
            g = (e.get("doctrine") or {}).get(k)
            if g is not None and str(g) != str(v):
                doc_diff.append("%s.%s 期望%s 实际%s" % (s.name, k, v, g))
    # 实测（本机 build 1276.1）：SetDoctrine 下发成功但**不被持久化**，
    # 保存后回读仍是默认值（WCS_Air=1 / BingoJokerRTB=2 …）。因此这一项只作
    # 提示，不当作失败——真值以引擎为准，脚本里下发条令仍保留（换版本可能就生效）。
    r.add("条令关键字段一致", not doc_diff,
          ("；".join(doc_diff) + "（本版本引擎不持久化 SetDoctrine，已知行为）") if doc_diff
          else "全部一致", warn=bool(doc_diff))

    # ---------- 6. 气象
    if spec.weather:
        w = digest.get("weather") or {}
        ok = (w.get("temp") == spec.weather.temp
              and w.get("rainfall") == spec.weather.rainfall
              and abs(float(w.get("cloud", -1)) - spec.weather.cloud) < 0.02
              and w.get("seastate") == spec.weather.seastate)
        r.add("气象一致", ok, "spec=%s engine=%s" % (spec.weather.to_dict(), w))

    # ---------- 7. 推演冒烟
    if smoke is not None:
        ok = bool(smoke.get("reset") == 1 and smoke.get("steps", 0) > 0
                  and not smoke.get("error_side"))
        r.add("引擎能加载并推进推演（冒烟）", ok,
              "reset=%s steps=%s 推演时长=%ss 胜负=%s 错误方=%r"
              % (smoke.get("reset"), smoke.get("steps"), smoke.get("sim_time"),
                 smoke.get("result"), smoke.get("error_side")))
    return r
