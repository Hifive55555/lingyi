# -*- coding: utf-8 -*-
"""自然语言 -> 想定规格（ScenarioSpec）。

两条通道：

* **RuleParser（默认，离线可复现）**：中文规则解析。用词表（平台/战区/任务类型/
  方位/数量词）做"槽位填充"，把一段作战描述变成 ``ScenarioSpec``。特点：
  - 完全确定性：同一段话永远得到同一份规格（配合 spec.seed 连 GUID 都一致）；
  - 可解释：``ParseResult.log`` 逐条记录"识别到什么、缺省补了什么、哪里没懂"，
    这一点对想定工程很重要 —— 想定错了要能一眼看出是理解错了还是引擎不给；
  - 无需联网/无需大模型。
* **LLMParser（可选，可插拔）**：把同一份 JSON Schema 交给任意 OpenAI 兼容模型，
  让它直接吐 spec。接口在 ``parse_with_llm``，没配 key 就报错并回退规则解析。
  规则解析器同时也是 LLM 输出的事后校验器（``spec.validate()``）。

自然语言里能识别的要素
----------------------
标题 / 开始时间 / 时长 / 复杂度 / 难度 / 战区或经纬度 / 推演方与对抗关系 /
兵力（平台型号 + 数量 + 部署方位与距离 + 高度）/ 任务（巡逻或打击 + 子类型 +
巡逻半径 + 参与兵力）/ 气象 / 条令（武器控制状态）。

例：
    设定 2026 年 3 月 1 日 8 时，东海中部。红方 2 艘 052D、1 艘 054A 从西侧
    110 海里进入，执行反舰巡逻，巡逻半径 40 海里；蓝方 1 个航母打击群
    （1 艘福特级、2 艘伯克级）在东侧 130 海里，4 架 F-35C 挂载反舰导弹执行
    反舰打击。海况 4 级，云量 0.6。持续 3 小时。
"""
from __future__ import annotations

import json
import math
import re
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .catalog import Catalog, Platform
from .spec import (ScenarioSpec, Side, Unit, Mission, Weather, SpecError,
                   DEFAULT_DOCTRINE, offset)


# ---------------------------------------------------------------- 文本预处理
_CN_NUM = {"零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5,
           "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn2int(s: str) -> Optional[int]:
    s = s.strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s in _CN_NUM:
        return _CN_NUM[s]
    if s.startswith("十") and len(s) == 2:
        return 10 + _CN_NUM.get(s[1], 0)
    if len(s) == 2 and s[0] == "十":
        return 10 + _CN_NUM.get(s[1], 0)
    if len(s) == 3 and s[1] == "十":
        return _CN_NUM.get(s[0], 0) * 10 + _CN_NUM.get(s[2], 0)
    return None


def normalize(text: str) -> str:
    t = text.replace("，", ",").replace("。", ".").replace("；", ";").replace("：", ":")
    t = t.replace("（", "(").replace("）", ")").replace("、", ",").replace("“", '"').replace("”", '"')
    t = re.sub(r"[ \t\u3000]+", " ", t)
    return t


def split_clauses(text: str) -> List[str]:
    # 注意：句号同时是小数点，必须只在小数点"不是数字之间"时才断句
    parts = re.split(r"[;\n]|(?<!\d)\.(?!\d)", text)
    out = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p)
    return out


# ---------------------------------------------------------------- 方位词
BEARINGS = {
    "北": 0, "东北": 45, "东": 90, "东南": 135, "南": 180,
    "西南": 225, "西": 270, "西北": 315,
    "北方": 0, "东方": 90, "南方": 180, "西方": 270,
    "北部": 0, "东部": 90, "南部": 180, "西部": 270,
    "东侧": 90, "西侧": 270, "南侧": 180, "北侧": 0,
    "东北方向": 45, "西北方向": 315, "东南方向": 135, "西南方向": 225,
}


@dataclass
class ParseResult:
    spec: ScenarioSpec
    log: List[str] = field(default_factory=list)
    unparsed: List[str] = field(default_factory=list)
    source_text: str = ""

    def note(self, msg: str):
        self.log.append(msg)

    def to_dict(self):
        return {"spec": self.spec.to_dict(), "log": self.log,
                "unparsed": self.unparsed, "source_text": self.source_text}


# ---------------------------------------------------------------- 规则解析器
class RuleParser(object):
    def __init__(self, catalog: Optional[Catalog] = None, strike_as_patrol: bool = True):
        self.cat = catalog or Catalog()
        #: True = 把 NL 里的"打击"折算成等价 Patrol（AI 版想定推荐做法）
        self.strike_as_patrol = strike_as_patrol
        self.aliases = sorted(self.cat.platforms.keys(), key=len, reverse=True)

    # ------------------------------------------------------------ 入口
    def parse(self, text: str, default_title: str = "NL想定") -> ParseResult:
        raw = text
        t = normalize(text)
        res = ParseResult(spec=None, source_text=raw)  # type: ignore
        clauses = split_clauses(t)

        title = self._title(t) or default_title
        start_time = self._start_time(t, res)
        duration = self._duration(t, res)
        center, place = self._center(t, res)
        complexity, difficulty = self._levels(t)
        weather = self._weather(t, res)
        sides, posture = self._sides(t, res)
        spans = self._spans(clauses)
        unit_specs, geoms = self._forces(spans, sides, res)
        missions = self._missions(spans, sides, unit_specs, res)
        center = self._fix_center(center, unit_specs, place, missions)

        spec = ScenarioSpec(
            title=title, start_time=start_time, duration_s=duration,
            complexity=complexity, difficulty=difficulty,
            description=raw.strip(), center=center, seed=abs(hash(title)) % 100000,
            weather=weather, provenance={"parser": "rule", "source_text": raw},
        )
        # --- 推演方
        names = sides or ["红方", "蓝方"]
        for n in names:
            spec.sides.append(Side(name=n, posture={}, doctrine=dict(DEFAULT_DOCTRINE)))
        for a in spec.sides:
            for b in spec.sides:
                if a.name == b.name:
                    continue
                code = posture.get((a.name, b.name))
                a.posture[b.name] = code or ("H" if self._hostile(a.name, b.name) else "N")
        res.note("推演方：%s；对抗关系：%s" % (
            "/".join(names),
            ", ".join("%s->%s:%s" % (a.name, b, c) for a in spec.sides for b, c in a.posture.items())))

        # --- 兵力部署
        spec.units = self._layout(unit_specs, geoms, spec, res)

        # --- 任务（含巡逻区）
        spec.missions = self._build_missions(missions, spec, res)

        # --- 飞机挂载：按所归任务的子类型"语义选挂载"
        self._assign_loadouts(spec, res)

        res.spec = spec
        # 每个推演方都要有任务：没写任务的一方按兵力构成补默认巡逻任务
        missing = [s.name for s in spec.sides
                   if not any(m.side == s.name for m in spec.missions)]
        if missing:
            res.note("以下推演方未描述任务，按兵力构成自动生成默认巡逻任务：%s" % "/".join(missing))
            spec.missions.extend(self._default_missions(spec, res, only=missing))
        # 未分配到任务的单元，并入**本方**第一个任务
        assigned = {u for m in spec.missions for u in m.units}
        for u in spec.units:
            if u.name in assigned:
                continue
            mine = [m for m in spec.missions if m.side == u.side]
            if mine:
                mine[0].units.append(u.name)
                u.mission = mine[0].name
                res.note("单元 %s 未指明任务，已并入本方任务 %s" % (u.name, mine[0].name))
        res.note("规模：%d 型单元 / %d 个；任务 %d 个" % (
            len(spec.units), sum(u.count for u in spec.units), len(spec.missions)))
        return res

    # ------------------------------------------------------------ 元信息
    def _title(self, t: str) -> Optional[str]:
        m = re.search(r'(?:标题|想定名|名称为|名为)[: ]*"?([^",.\n]{2,40})"?', t)
        return m.group(1).strip() if m else None

    def _start_time(self, t: str, res: ParseResult) -> str:
        m = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*'
                      r'(?:(上午|下午|凌晨|夜间|傍晚)\s*)?(\d{1,2})\s*[时点:]\s*(\d{0,2})', t)
        if m:
            y, mo, d, hh, mi = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(5)), int(m.group(6) or 0)
            hh = hh + 12 if (m.group(4) in ("下午", "傍晚") and hh < 12) else hh
            res.note("开始时间：%04d-%02d-%02d %02d:%02d:00" % (y, mo, d, hh, mi))
            return "%04d-%02d-%02d %02d:%02d:00" % (y, mo, d, hh, mi)
        m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})[ T](\d{1,2}):(\d{1,2})', t)
        if m:
            res.note("开始时间（ISO）：%s" % m.group(0))
            return "%04d-%02d-%02d %02d:%02d:00" % tuple(int(x) for x in m.groups())
        res.note("未给出时间：默认 2026-03-01 08:00:00")
        return "2026-03-01 08:00:00"

    def _duration(self, t: str, res: ParseResult) -> int:
        m = re.search(r'(?:持续|推演时长|时长|历时)\s*(\d+(?:\.\d+)?)\s*(小时|分钟|天|h|min)', t)
        if m:
            v = float(m.group(1))
            unit = m.group(2)
            sec = {"小时": 3600, "h": 3600, "分钟": 60, "min": 60, "天": 86400}[unit]
            res.note("推演时长：%s %s = %d 秒" % (m.group(1), unit, int(v * sec)))
            return int(v * sec)
        res.note("未给出时长：默认 7200 秒（2 小时）")
        return 7200

    def _center(self, t: str, res: ParseResult) -> Tuple[Dict[str, float], Optional[dict]]:
        m = re.search(r'北纬\s*(\d+(?:\.\d+)?)\s*度?[, ]*东经\s*(\d+(?:\.\d+)?)', t)
        if m:
            c = {"lat": float(m.group(1)), "lon": float(m.group(2))}
            res.note("中心坐标（显式经纬度）：%s" % c)
            return c, None
        for name in sorted(self.cat.places.keys(), key=len, reverse=True):
            if name in t:
                p = self.cat.places[name]
                res.note("战区：%s -> (%.2f, %.2f)" % (name, p["lat"], p["lon"]))
                return {"lat": p["lat"], "lon": p["lon"]}, dict(p, name=name)
        m = re.search(r'(?:太平洋|大西洋|印度洋)[^,.]{0,12}海域', t)
        if m:
            res.note("只识别到'%s'，无精确坐标：暂用 (18.0, 128.0) 并提示补充" % m.group(0))
            return {"lat": 18.0, "lon": 128.0}, None
        res.note("未给出战区：默认 (25.0, 122.0)（台湾海峡东北口）")
        return {"lat": 25.0, "lon": 122.0}, None

    def _levels(self, t: str) -> Tuple[int, int]:
        c = re.search(r'复杂度\s*[:为]?\s*(\d)', t)
        d = re.search(r'难度\s*[:为]?\s*(\d)', t)
        return (int(c.group(1)) if c else 2), (int(d.group(1)) if d else 2)

    def _weather(self, t: str, res: ParseResult) -> Optional[Weather]:
        sea = re.search(r'海况\s*(\d)', t)
        cloud = re.search(r'云量\s*([01](?:\.\d+)?)', t)
        rain = re.search(r'降雨(?:率)?\s*(\d+)', t)
        temp = re.search(r'气温\s*(-?\d+)', t)
        if not any([sea, cloud, rain, temp]):
            return None
        w = Weather(temp=int(temp.group(1)) if temp else 20,
                    rainfall=int(rain.group(1)) if rain else 0,
                    cloud=float(cloud.group(1)) if cloud else 0.0,
                    seastate=int(sea.group(1)) if sea else 2)
        res.note("气象：气温 %d℃ / 降雨 %d / 云量 %.1f / 海况 %d"
                 % (w.temp, w.rainfall, w.cloud, w.seastate))
        return w

    # ------------------------------------------------------------ 推演方
    def _sides(self, t: str, res: ParseResult):
        found: List[str] = []
        for kw, side in self.cat.side_templates.items():
            if kw in t and side not in found:
                found.append(side)
        order = ["红方", "蓝方"]
        found = [s for s in order if s in found] + [s for s in found if s not in order]
        posture: Dict[Tuple[str, str], str] = {}
        if re.search(r'中立|不敌对|和平', t):
            for a in found:
                for b in found:
                    if a != b:
                        posture[(a, b)] = "N"
            res.note("对抗关系：中立（N）")
        elif re.search(r'友好|联合演习|盟军', t):
            for a in found:
                for b in found:
                    if a != b:
                        posture[(a, b)] = "F"
            res.note("对抗关系：友好（F）")
        else:
            res.note("对抗关系：默认敌对（H）")
        return found, posture

    @staticmethod
    def _hostile(a: str, b: str) -> bool:
        return {a, b} == {"红方", "蓝方"}

    def _wcs(self, t: str) -> Dict[str, str]:
        if re.search(r'禁止开火|武器管控|不开火', t):
            return dict(DEFAULT_DOCTRINE, WCS_Air="2", WCS_Surface="2", WCS_Submarine="2", WCS_Land="2")
        if re.search(r'谨慎开火|限制开火|有限交战', t):
            return dict(DEFAULT_DOCTRINE, WCS_Air="1", WCS_Surface="1", WCS_Submarine="1", WCS_Land="1")
        if re.search(r'自由开火|武器自由|自主交战', t):
            return dict(DEFAULT_DOCTRINE, WCS_Air="0", WCS_Surface="0", WCS_Submarine="0", WCS_Land="0")
        return dict(DEFAULT_DOCTRINE)

    # ------------------------------------------------------------ 兵力
    def _spans(self, clauses: List[str]) -> List[Tuple[Optional[str], str]]:
        """把每句按"推演方关键词"切成若干片段，每段带归属。

        典型 NL 是一句里塞多方：``红方 2 艘 052D 在西侧, 蓝方 2 艘伯克级在东侧``。
        按"最近的前置推演方关键词"切段，兵力与任务才不会被算到对方头上；
        整句都没提推演方时，继承上一句的归属（"另有岸基 S-400 营位于……"）。
        """
        kws = sorted(self.cat.side_templates.items(), key=lambda kv: -len(kv[0]))
        out: List[Tuple[Optional[str], str]] = []
        cur: Optional[str] = None
        for c in clauses:
            hits = []
            i = 0
            while i < len(c):
                for kw, side in kws:
                    if c.startswith(kw, i):
                        hits.append((i, side, len(kw)))
                        i += len(kw)
                        break
                else:
                    i += 1
            if not hits:
                out.append((cur, c))
                continue
            if hits[0][0] > 0:
                out.append((cur, c[:hits[0][0]]))
            for j, (pos, side, ln) in enumerate(hits):
                end = hits[j + 1][0] if j + 1 < len(hits) else len(c)
                out.append((side, c[pos:end]))
                cur = side
        return out

    def _forces(self, spans, sides: List[str], res: ParseResult):
        """返回 [(side, Platform, count, extras)] 与 {side: 几何信息}。"""
        out: List[Tuple[str, Platform, int, dict]] = []
        geoms: Dict[str, dict] = {}
        sides = sides or ["红方", "蓝方"]
        last_side = None
        for side, c in spans:
            side = side or last_side
            if side and side in [s for s in sides] + [self.cat.side_templates.get(k, k)
                                                      for k in self.cat.side_templates]:
                last_side = side
            geom = self._geometry(c) or {}
            # 只有"显式坐标"或"方位+距离"才算锚点；单纯的巡逻半径/高度不算
            if side and ("pos" in geom or ("dist_nm" in geom and "bearing" in geom)):
                geoms[side] = dict(geoms.get(side) or {}, **{k: v for k, v in geom.items()
                                                              if k in ("pos", "dist_nm", "bearing")})
            if not side:
                continue
            # 一段里可能出现多个"北纬X、东经Y"（岸基设施逐个给坐标），按坐标再切一次
            coords = [(m.start(), {"lat": float(m.group(1)), "lon": float(m.group(2))})
                      for m in re.finditer(r'北纬\s*(\d+(?:\.\d+)?)\s*度?[, ]*东经\s*(\d+(?:\.\d+)?)', c)]
            for alias, count, pos in self._platforms_in(c, res):
                # 同一方同一型号在后面又被"提及"（"从该机场起飞"）时，若无数量词则忽略
                if any(x[0] == side and x[3].get("alias") == alias for x in out) and count <= 1:
                    res.note("平台 %s 在 %s 处被重复提及，按同一批兵力处理（忽略）" % (alias, side))
                    continue
                try:
                    p = self.cat.resolve(alias)
                except KeyError as e:
                    res.unparsed.append("%s（%s）" % (alias, e))
                    continue
                g2 = dict(geom)
                if coords and p.kind in ("Facility", "Satellite"):
                    # 岸基/固定设施常逐个给"北纬X、东经Y"，取离它最近的那个坐标
                    nearest = min(coords, key=lambda kv: abs(kv[0] - pos))
                    g2["pos"] = nearest[1]
                    g2.pop("dist_nm", None)
                    g2.pop("bearing", None)
                elif coords and abs(min(coords, key=lambda kv: abs(kv[0] - pos))[0] - pos) < 18:
                    # 机动单元只有在坐标"紧挨着"它的时候才认（"红方舰队位于北纬..、东经.."）
                    g2["pos"] = min(coords, key=lambda kv: abs(kv[0] - pos))[1]
                    g2.pop("dist_nm", None)
                    g2.pop("bearing", None)
                out.append((side, p, count, {"clause": c, "geom": g2, "alias": alias}))
        if not out:
            res.note("未识别到具体平台：按典型兵力补 1 艘驱逐舰 + 1 支航空兵")
            out = [
                ("红方", self.cat.resolve("052D"), 2, {}),
                ("蓝方", self.cat.resolve("伯克级"), 1, {}),
                ("蓝方", self.cat.resolve("F-35C"), 2, {}),
            ]
        return out, geoms

    @staticmethod
    def _split_by_coords(c: str):
        """把一段按"北纬…东经…"切分，返回 [(coord|None, 子段)]。"""
        pat = re.compile(r'北纬\s*(\d+(?:\.\d+)?)\s*度?[, ]*东经\s*(\d+(?:\.\d+)?)')
        ms = list(pat.finditer(c))
        if len(ms) <= 1:
            return [(dict(lat=float(ms[0].group(1)), lon=float(ms[0].group(2))) if ms else None, c)]
        out = []
        if ms[0].start() > 0:
            out.append((None, c[:ms[0].start()]))
        for i, m in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else len(c)
            out.append(({"lat": float(m.group(1)), "lon": float(m.group(2))}, c[m.start():end]))
        return out

    def _clause_side(self, c: str, sides: List[str]) -> Optional[str]:
        hits = [(c.find(kw), side) for kw, side in self.cat.side_templates.items() if kw in c]
        hits = [h for h in hits if h[1] in (sides or [])] or hits
        if not hits:
            return None
        return sorted(hits)[0][1]

    def _platforms_in(self, c: str, res: ParseResult) -> List[Tuple[str, int, int]]:
        """在一句话里找 '数量+平台' 组合，返回 [(别名, 数量, 出现位置)]。"""
        found: List[Tuple[str, int, int]] = []
        used: List[Tuple[int, int]] = []
        for alias in self.aliases:
            for m in re.finditer(re.escape(alias), c):
                s, e = m.span()
                if any(not (e <= u0 or s >= u1) for u0, u1 in used):
                    continue
                count = self._count_before(c[:s]) or self._count_after(c[e:]) or 1
                found.append((alias, count, s))
                used.append((s, e))
        found.sort(key=lambda kv: kv[2])
        return found

    @staticmethod
    def _count_before(prefix: str) -> Optional[int]:
        m = re.search(r'(\d+|[一二两三四五六七八九十])\s*(?:艘|架|个|座|部|型|条|支|批)?\s*$', prefix.strip())
        if m:
            v = cn2int(m.group(1))
            return v if v and v > 0 else None
        return None

    @staticmethod
    def _count_after(suffix: str) -> Optional[int]:
        m = re.match(r'\s*(?:型)?(?:[^\d,.;]{0,8}?)\s*(\d+|[一二两三四五六七八九十])\s*(?:艘|架|个|座|部|条|支)', suffix)
        if m:
            v = cn2int(m.group(1))
            return v if v and v > 0 else None
        return None

    def _geometry(self, c: str) -> Optional[dict]:
        """从一句话里抽几何信息：巡逻半径 / 部署方位与距离 / 显式经纬度 / 高度。

        注意：``巡逻半径 35 海里`` 里的 35 不能被当成"距中心 35 海里"，
        否则部署锚点会被任务的巡逻半径污染（实测踩过）。
        """
        g: dict = {}
        m = re.search(r'半径\s*(\d+(?:\.\d+)?)\s*海里', c)
        if m:
            g["radius_nm"] = float(m.group(1))
        c2 = re.sub(r'半径\s*\d+(?:\.\d+)?\s*海里', '', c)
        m = re.search(r'(?:距离?|距)[^,]{0,6}?(\d+(?:\.\d+)?)\s*海里', c2) or             re.search(r'(\d+(?:\.\d+)?)\s*海里', c2)
        if m:
            g["dist_nm"] = float(m.group(1))
        for kw, brg in sorted(BEARINGS.items(), key=lambda kv: -len(kv[0])):
            if kw in c2:
                g["bearing"] = brg
                break
        m = re.search(r'北纬\s*(\d+(?:\.\d+)?)\s*度?[, ]*东经\s*(\d+(?:\.\d+)?)', c)
        if m:
            g["pos"] = {"lat": float(m.group(1)), "lon": float(m.group(2))}
        m = re.search(r'(?:高度|高空|升限)\s*(\d+)\s*米', c)
        if m:
            g["alt"] = float(m.group(1))
        return g or None

    # ------------------------------------------------------------ 部署
    def _layout(self, unit_specs, geoms, spec: ScenarioSpec, res: ParseResult) -> List[Unit]:
        units: List[Unit] = []
        clat, clon = spec.center["lat"], spec.center["lon"]
        per_side_index: Dict[str, int] = {}
        default_bearing = {"红方": 225, "蓝方": 45}

        # 每方默认锚点
        anchor: Dict[str, Tuple[float, float]] = {}
        for u_side, p, cnt, _ in unit_specs:
            anchor.setdefault(u_side, (clat, clon))
        for s, g in geoms.items():
            if "pos" in g:
                anchor[s] = (g["pos"]["lat"], g["pos"]["lon"])
            else:
                brg = g.get("bearing", default_bearing.get(s, 225))
                dist = g.get("dist_nm", 100.0)
                anchor[s] = offset(clat, clon, brg, dist)
                res.note("%s 部署：方位 %s（%d°）距中心 %s 海里 -> (%.4f, %.4f)"
                         % (s, self._bearing_name(brg), brg, dist, anchor[s][0], anchor[s][1]))

        for u_side, p, cnt, extra in unit_specs:
            i = per_side_index.get(u_side, 0)
            per_side_index[u_side] = i + 1
            g = extra.get("geom") or {}
            if "pos" in g:                      # 该平台自带坐标（岸基设施常用）
                alat, alon = g["pos"]["lat"], g["pos"]["lon"]
                lat, lon = alat, alon
                i_off = False
            else:
                alat, alon = anchor[u_side]
                i_off = True
            # 同一方多个型号按小圆散开（避免叠在一个点上被引擎合并显示）
            brg = (default_bearing.get(u_side, 225) + 40 * i) % 360
            if i_off:
                lat, lon = offset(alat, alon, brg, 8.0 * i) if i else (alat, alon)
            # 朝向：指向对方（红->东北，蓝->西南）
            head = (default_bearing.get(u_side, 225) + 180) % 360
            alt = None
            if p.kind == "Aircraft":
                alt = float(g.get("alt") or 8000.0)
            name = "%s %s #%d" % (u_side, p.alias, i + 1)
            units.append(Unit(side=u_side, kind=p.kind, name=name, dbid=p.dbid,
                              lat=round(lat, 6), lon=round(lon, 6), alt=alt,
                              heading=head, count=cnt, alias=p.alias))
            res.note("单元 %s：%s ×%d（%s #%d）@ (%.4f, %.4f)%s"
                     % (name, p.alias, cnt, p.kind, p.dbid, lat, lon,
                        " alt=%sm" % alt if alt else ""))
        return units

    @staticmethod
    def _bearing_name(brg: int) -> str:
        for k, v in BEARINGS.items():
            if v == brg:
                return k
        return str(brg)

    def _fix_center(self, center, unit_specs, place, missions):
        return center

    # ------------------------------------------------------------ 任务
    def _missions(self, spans, sides, unit_specs, res: ParseResult):
        out = []
        for side, c in spans:
            if not re.search(r'任务|巡逻|警戒|打击|截击|封锁|掩护|侦察', c):
                continue
            # "岸基/兵力部署"这类句子里的'打击'不是任务，靠"执行/进行/担任"过滤
            if not re.search(r'执行|进行|担任|负责|实施|展开|投入|任务', c):
                continue
            mt = None
            for k, v in self.cat.mission_types.items():
                if k in c:
                    mt = (k, v["mtype"], v["subtype"])
                    break
            if not mt:
                if "打击" in c or "截击" in c:
                    mt = ("打击", "Strike", "NAVAL")
                elif "反潜" in c:
                    mt = ("反潜巡逻", "Patrol", "SUB")
                elif "防空" in c:
                    mt = ("防空巡逻", "Patrol", "AAW")
                elif "制海" in c:
                    mt = ("制海巡逻", "Patrol", "SEACONTROL")
                else:
                    mt = ("海上巡逻", "Patrol", "NAVAL")
                res.note("任务类型未在词表中命中，按关键词推断为 %s/%s" % (mt[1], mt[2]))
            g = self._geometry(c) or {}
            out.append({"side": side, "name": mt[0], "mtype": mt[1], "subtype": mt[2],
                        "radius_nm": g.get("radius_nm", 35.0), "clause": c})
            res.note("任务：%s（%s/%s）%s" % (mt[0], mt[1], mt[2],
                                              "，半径 %s 海里" % g.get("radius_nm") if g.get("radius_nm") else ""))
        return out

    def _build_missions(self, missions, spec: ScenarioSpec, res: ParseResult) -> List[Mission]:
        out: List[Mission] = []
        clat, clon = spec.center["lat"], spec.center["lon"]
        for i, m in enumerate(missions):
            # AI 版想定的经验做法（见方法手册 §6.3）：引擎初期没有敌方情报，
            # Strike 任务没有目标就不动，所以默认把"打击"折成等价的 Patrol。
            if self.strike_as_patrol and m["mtype"] == "Strike":
                conv = {"AIR_INTERCEPT": "AAW", "LAND": "LAND",
                        "NAVAL": "NAVAL", "SUB_STRIKE": "SUB"}.get(m["subtype"], "NAVAL")
                res.note("任务 %s 由 Strike/%s 折算为 Patrol/%s（无目标情报时 Strike 不会行动，"
                         "AI 版想定统一用 Patrol）" % (m["name"], m["subtype"], conv))
                m = dict(m, mtype="Patrol", subtype=conv)
            side = m["side"] or spec.side_names()[0]
            # 参与兵力：默认取本方全部单元
            mine = [u for u in spec.units if u.side == side]
            pref = {"AAW": ("Aircraft",), "AIR": ("Aircraft",),
                    "NAVAL": ("Aircraft", "Ship"), "SUB": ("Submarine",),
                    "LAND": ("Aircraft",), "SEACONTROL": ("Ship",),
                    "SEAD": ("Aircraft",)}.get(m["subtype"], ())
            pick = [u for u in mine if u.kind in pref] or mine
            if not pick:
                res.note("任务 %s 所属 %s 没有可用兵力，跳过" % (m["name"], side))
                continue
            # 巡逻区：以任务方兵力重心为心
            glat = sum(u.lat for u in pick) / len(pick)
            glon = sum(u.lon for u in pick) / len(pick)
            radius = float(m.get("radius_nm") or 35.0)
            ring = spec.zone_ring(glat, glon, radius, n=4, start_deg=45)
            name = "%s-%s" % (side, m["name"])
            same = [x for x in out if x.side == side and x.mtype == m["mtype"]]
            if any(x.name == name for x in same):
                # 同一方同类任务重复描述：并进已有任务（不新建，避免同名任务）
                tgt = next(x for x in same if x.name == name)
                for u in pick:
                    if u.name not in tgt.units:
                        tgt.units.append(u.name)
                        u.mission = tgt.name
                res.note("任务 %s 重复描述，已合并" % name)
                continue
            out.append(Mission(side=side, name=name, mtype=m["mtype"], subtype=m["subtype"],
                               zone=ring, units=[u.name for u in pick]))
            for u in pick:
                u.mission = name
            res.note("巡逻区：%s 4 点菱形，半径 %.0f 海里，中心 (%.4f, %.4f)"
                     % (name, radius, glat, glon))
        return out

    def _assign_loadouts(self, spec: ScenarioSpec, res: ParseResult) -> None:
        for u in spec.units:
            if u.kind != "Aircraft" or u.loadoutid:
                continue
            role = None
            for m in spec.missions:
                if u.name in m.units:
                    role = m.subtype
                    break
            lo, name = self.cat.loadout_for(u.dbid, role)
            u.loadoutid = lo
            res.note("挂载：%s -> 方案 %s（%s）" % (u.name, lo, (name or "")[:40]))

    def _default_missions(self, spec: ScenarioSpec, res: ParseResult,
                          only: Optional[List[str]] = None) -> List[Mission]:
        out = []
        for s in spec.sides:
            if only and s.name not in only:
                continue
            mine = [u for u in spec.units if u.side == s.name]
            if not mine:
                continue
            kinds = {u.kind for u in mine}
            aliases = " ".join((u.alias or "") for u in mine if u.kind == "Aircraft")
            if kinds == {"Submarine"}:
                sub, tag = "SUB", "反潜巡逻"
            elif kinds == {"Aircraft"} and re.search(r'反潜|P-3C|伊尔-38|卡-28|MH-60R|直-9C|直-18', aliases):
                sub, tag = "SUB", "反潜巡逻"
            elif "Ship" in kinds:
                sub, tag = "NAVAL", "反舰巡逻"
            else:
                sub, tag = "AAW", "防空巡逻"
            glat = sum(u.lat for u in mine) / len(mine)
            glon = sum(u.lon for u in mine) / len(mine)
            ring = spec.zone_ring(glat, glon, 35.0, n=4, start_deg=45)
            name = "%s-%s" % (s.name, tag)
            out.append(Mission(side=s.name, name=name, mtype="Patrol", subtype=sub,
                               zone=ring, units=[u.name for u in mine]))
            for u in mine:
                u.mission = name
            res.note("默认任务：%s（%s）" % (name, sub))
        return out


# ---------------------------------------------------------------- LLM 通道
SPEC_SCHEMA_HINT = """{
 "title": str, "start_time": "YYYY-MM-DD HH:MM:SS", "duration_s": int,
 "complexity": 1-5, "difficulty": 1-5, "description": str,
 "center": {"lat": float, "lon": float}, "seed": int,
 "sides": [{"name": "红方", "posture": {"蓝方": "H"},
            "doctrine": {"WCS_Air": "1", "...": "..."}, "camera": {"lat":..,"lon":..,"alt":..}}],
 "units": [{"side": "红方", "kind": "Ship|Aircraft|Submarine|Facility|Satellite",
            "name": str, "dbid": int, "lat": float, "lon": float,
            "alt": float|null, "heading": float|null, "count": int}],
 "missions": [{"side": "红方", "name": str, "mtype": "Patrol|Strike",
               "subtype": "AAW|NAVAL|SUB|LAND|SEACONTROL|SEAD|AIR_INTERCEPT|...",
               "zone": [{"lat":..,"lon":..} x3-10], "units": [str]}]
}"""


def parse_with_llm(text: str, base_url: str, api_key: str, model: str,
                   catalog: Optional[Catalog] = None, timeout: float = 120.0) -> ParseResult:
    """用 OpenAI 兼容接口把自然语言直接翻成 spec JSON（可选通道）。

    典型用法（环境变量）::

        export SCE_LLM_BASE=https://openrouter.ai/api/v1
        export SCE_LLM_KEY=sk-...
        export SCE_LLM_MODEL=openai/gpt-4o-mini
        python cli.py nl2scen "……" --parser llm
    """
    cat = catalog or Catalog()
    vocab = ", ".join(sorted(cat.platforms.keys()))
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content":
             "你是兵棋想定编辑专家，把中文作战描述翻译成灵弈平台的想定 JSON。"
             "只输出 JSON，不要解释。可用平台别名与 dbid 见用户消息；"
             "未给坐标时按地名推断经纬度。JSON Schema:" + SPEC_SCHEMA_HINT},
            {"role": "user", "content":
             "可用平台别名（需映射到 dbid）：%s\n\n作战描述：\n%s" % (vocab, text)},
        ],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key})
    with urllib.request.urlopen(req, timeout=timeout) as f:
        data = json.loads(f.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        raise SpecError("LLM 没有返回 JSON：%s" % content[:400])
    d = json.loads(m.group(0))
    # 用规则解析器补齐/校正 LLM 漏掉的字段（尤其是巡逻区与姿态双向性）
    spec = ScenarioSpec.from_dict(d)
    rr = RuleParser(cat).parse(text, default_title=spec.title)
    if not spec.missions:
        spec.missions = rr.spec.missions
        for m2 in spec.missions:
            m2.side = m2.side if m2.side in spec.side_names() else spec.side_names()[0]
    if not spec.units:
        spec.units = rr.spec.units
    for s in spec.sides:
        for t in spec.sides:
            if t.name != s.name and t.name not in s.posture:
                s.posture[t.name] = "H"
    return ParseResult(spec=spec, log=rr.log + ["LLM 通道：%s/%s" % (base_url, model)],
                       source_text=text)


# ---------------------------------------------------------------- 工厂
def parse(text: str, parser: str = "rule", catalog: Optional[Catalog] = None,
          llm: Optional[Dict[str, str]] = None, title: str = "NL想定") -> ParseResult:
    if parser == "llm":
        if not llm or not llm.get("key"):
            raise SpecError("llm 通道需要 SCE_LLM_BASE / SCE_LLM_KEY / SCE_LLM_MODEL")
        return parse_with_llm(text, llm["base"], llm["key"], llm["model"], catalog)
    return RuleParser(catalog).parse(text, default_title=title)
