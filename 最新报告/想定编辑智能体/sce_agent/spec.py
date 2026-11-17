# -*- coding: utf-8 -*-
"""想定规格（ScenarioSpec）—— 想定编辑智能体的中间表示（IR）。

设计要点
--------
1. **可序列化**：整份想定规格是纯 JSON，可 diff、可版本管理、可批量生成；
2. **可校验**：`validate()` 在**下发引擎之前**就拦住绝大多数结构性错误
   （缺推演方、任务无巡逻区、经纬度越界、DBID 未登记……），把"引擎报错"
   变成"规格报错"，这是智能体迭代效率的关键；
3. **可变换**：`translate / rotate / scale_units / clone_for_variant`
   是"一份想定 → 同类想定集"的算子基座（见 family.py）；
4. **与引擎解耦**：本模块不依赖 gRPC，可离线单测。

字段与灵弈 Lua 接口的对应关系（lua_gen.py 实现）：
    spec.title        -> SetScenarioInfo{TITLE}
    spec.sides[]      -> AddSide + SetSidePosture + SetSideOptions + SetDoctrine
    spec.units[]      -> AddUnit (+ SetLoadout)
    spec.missions[]   -> AddMission + AddReferencePoint + SetMission{patrolZone}
                         + AssignUnitListToMission
    spec.weather      -> SetWeather(temp, rainfall, cloud, seastate)
"""
from __future__ import annotations

import copy
import json
import math
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------- 常量词表
KINDS = ("Aircraft", "Ship", "Submarine", "Facility", "Satellite")
KIND_ZH = {"Aircraft": "飞机", "Ship": "水面舰艇", "Submarine": "潜艇",
           "Facility": "设施", "Satellite": "卫星"}

#: Patrol 任务合法子类型（LuaAPIDoc §10.1）
PATROL_SUBTYPES = {
    "AAW": "防空", "AIR": "防空", "NAVAL": "反舰", "SUR_SEA": "反舰",
    "ASUW_NAVAL": "反舰", "SUB": "反潜", "ASW": "反潜", "LAND": "对地",
    "SUR_LAND": "对地", "ASUW_LAND": "对地", "SEACONTROL": "制海",
    "SEA": "制海", "SEAD": "反辐射",
}
#: Strike 任务合法子类型（LuaAPIDoc §10.2）
STRIKE_SUBTYPES = {
    "AIR_INTERCEPT": "空中截击", "AAW": "空中截击", "AIR": "空中截击",
    "LAND": "对地打击", "SUR_LAND": "对地打击", "LAND_STRIKE": "对地打击",
    "NAVAL": "反舰打击", "SUR_SEA": "反舰打击", "MARITIME_STRIKE": "反舰打击",
    "SUB_STRIKE": "反潜打击", "SUB": "反潜打击", "ASW": "反潜打击",
}

#: 子类型别名归一化（引擎把 AAW/AIR、ASW/SUB 等当同一个东西，回读时只给一个码）
_SUBTYPE_CANON = {
    "AIR": "AAW", "ASW": "SUB", "SEA": "SEACONTROL",
    "SUR_SEA": "NAVAL", "ASUW_NAVAL": "NAVAL", "SUR_LAND": "LAND",
    "ASUW_LAND": "LAND", "MARITIME_STRIKE": "NAVAL", "LAND_STRIKE": "LAND",
}


def canonical_subtype(mtype: str, subtype: str) -> str:
    """把子类型别名收敛成引擎回读时给出的那个规范值。"""
    st = (subtype or "").strip().upper()
    st = _SUBTYPE_CANON.get(st, st)
    if (mtype or "").lower().startswith("strike"):
        if st in ("AIR", "AAW", "AIR_INTERCEPT"):
            return "AIR_INTERCEPT"
        if st in ("SUB", "ASW", "SUB_STRIKE"):
            return "SUB_STRIKE"
        if st in ("NAVAL", "MARITIME_STRIKE"):
            return "NAVAL"
        if st in ("LAND", "SUR_LAND", "LAND_STRIKE"):
            return "LAND"
        return st or "NAVAL"
    if st == "AIR_INTERCEPT":
        return "AAW"
    if st == "SUB_STRIKE":
        return "SUB"
    return st or "NAVAL"


#: 姿态码（引擎内部枚举，实测：N=0 F=1 U=2 H=3）
POSTURE_CODES = {"N": 0, "F": 1, "U": 2, "H": 3}
POSTURE_ZH = {"H": "敌对", "F": "友好", "N": "中立", "U": "不友好"}

#: 条令默认值（与竞赛想定常见的"自由开火+自动规避"一致）
DEFAULT_DOCTRINE = {
    "WCS_Air": "1", "WCS_Surface": "1", "WCS_Submarine": "1", "WCS_Land": "1",
    "Nukes": "0", "BTAT": "2", "BingoJokerRTB": "2",
    "WinchesterShotgunRTB": "1", "AE": "1", "MS": "1",
}


class SpecError(ValueError):
    """规格不合法（结构性错误）。"""


# ---------------------------------------------------------------- 数据结构
@dataclass
class Side:
    name: str
    posture: Dict[str, str] = field(default_factory=dict)   # 对方名 -> F/N/U/H
    doctrine: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_DOCTRINE))
    camera: Optional[Dict[str, float]] = None               # {lat,lon,alt}
    is_ai_only: bool = True

    def to_dict(self):
        return asdict(self)


@dataclass
class Unit:
    side: str
    kind: str                     # Aircraft/Ship/Submarine/Facility/Satellite
    name: str
    dbid: int
    lat: float
    lon: float
    alt: Optional[float] = None
    heading: Optional[float] = None
    count: int = 1
    loadoutid: Optional[int] = None
    base: Optional[str] = None    # 基地/航母单元名
    mission: Optional[str] = None # 归属任务名
    alias: Optional[str] = None   # 自然语言里的原始说法（留痕用）
    role: Optional[str] = None    # 语义角色：striker/escort/awacs/...

    def to_dict(self):
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class Mission:
    side: str
    name: str
    mtype: str = "Patrol"         # Patrol / Strike
    subtype: str = "NAVAL"        # 见 PATROL_SUBTYPES / STRIKE_SUBTYPES
    zone: List[Dict[str, float]] = field(default_factory=list)  # [{lat,lon},...]
    units: List[str] = field(default_factory=list)              # 单元名
    isactive: bool = True

    def to_dict(self):
        return asdict(self)


@dataclass
class Weather:
    temp: int = 20
    rainfall: int = 0
    cloud: float = 0.0
    seastate: int = 2

    def to_dict(self):
        return asdict(self)


@dataclass
class ScenarioSpec:
    title: str
    start_time: str = "2026-03-01 08:00:00"
    duration_s: int = 7200
    complexity: int = 2
    difficulty: int = 2
    description: str = ""
    center: Dict[str, float] = field(default_factory=lambda: {"lat": 0.0, "lon": 0.0})
    seed: int = 0
    sides: List[Side] = field(default_factory=list)
    units: List[Unit] = field(default_factory=list)
    missions: List[Mission] = field(default_factory=list)
    weather: Optional[Weather] = None
    #: 生成留痕：来源自然语言 / 解析器 / 变量取值等
    provenance: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------ 序列化
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "start_time": self.start_time,
            "duration_s": self.duration_s,
            "complexity": self.complexity,
            "difficulty": self.difficulty,
            "description": self.description,
            "center": self.center,
            "seed": self.seed,
            "sides": [s.to_dict() for s in self.sides],
            "units": [u.to_dict() for u in self.units],
            "missions": [m.to_dict() for m in self.missions],
            "weather": self.weather.to_dict() if self.weather else None,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ScenarioSpec":
        return cls(
            title=d["title"],
            start_time=d.get("start_time", "2026-03-01 08:00:00"),
            duration_s=int(d.get("duration_s", 7200)),
            complexity=int(d.get("complexity", 2)),
            difficulty=int(d.get("difficulty", 2)),
            description=d.get("description", ""),
            center=dict(d.get("center") or {"lat": 0.0, "lon": 0.0}),
            seed=int(d.get("seed", 0)),
            sides=[Side(**s) for s in d.get("sides", [])],
            units=[Unit(**u) for u in d.get("units", [])],
            missions=[Mission(**m) for m in d.get("missions", [])],
            weather=Weather(**d["weather"]) if d.get("weather") else None,
            provenance=dict(d.get("provenance") or {}),
        )

    @classmethod
    def from_json(cls, path: str) -> "ScenarioSpec":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=1)

    def clone(self) -> "ScenarioSpec":
        return ScenarioSpec.from_dict(self.to_dict())

    # ------------------------------------------------------------ 便捷查询
    def side(self, name: str) -> Optional[Side]:
        for s in self.sides:
            if s.name == name:
                return s
        return None

    def side_names(self) -> List[str]:
        return [s.name for s in self.sides]

    def unit(self, name: str) -> Optional[Unit]:
        for u in self.units:
            if u.name == name:
                return u
        return None

    def mission(self, name: str) -> Optional[Mission]:
        for m in self.missions:
            if m.name == name:
                return m
        return None

    def counts(self) -> Dict[str, Dict[str, int]]:
        out: Dict[str, Dict[str, int]] = {}
        for s in self.sides:
            out[s.name] = {k: 0 for k in KINDS}
        for u in self.units:
            out.setdefault(u.side, {k: 0 for k in KINDS})
            out[u.side][u.kind] = out[u.side].get(u.kind, 0) + int(u.count)
        return out

    # ------------------------------------------------------------ 几何算子
    def translate(self, dlat: float, dlon: float) -> "ScenarioSpec":
        """整体平移（度）。中心点、单元、巡逻区一起动。"""
        self.center["lat"] = round(self.center.get("lat", 0.0) + dlat, 6)
        self.center["lon"] = round(self.center.get("lon", 0.0) + dlon, 6)
        for u in self.units:
            u.lat = round(u.lat + dlat, 6)
            u.lon = round(u.lon + dlon, 6)
        for m in self.missions:
            for p in m.zone:
                p["lat"] = round(p["lat"] + dlat, 6)
                p["lon"] = round(p["lon"] + dlon, 6)
        for s in self.sides:
            if s.camera:
                s.camera["lat"] = round(s.camera.get("lat", 0.0) + dlat, 6)
                s.camera["lon"] = round(s.camera.get("lon", 0.0) + dlon, 6)
        return self

    def rotate(self, deg: float) -> "ScenarioSpec":
        """绕想定中心整体旋转（度，正北顺时针）。"""
        clat, clon = self.center["lat"], self.center["lon"]
        k = math.cos(math.radians(clat)) or 1.0
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))

        def rt(lat, lon):
            dy, dx = lat - clat, (lon - clon) * k
            return (round(clat + dx * s + dy * c, 6),
                    round(clon + (-dx * c + dy * s) / k, 6))

        for u in self.units:
            u.lat, u.lon = rt(u.lat, u.lon)
            if u.heading is not None:
                u.heading = round((u.heading + deg) % 360, 3)
        for m in self.missions:
            for p in m.zone:
                p["lat"], p["lon"] = rt(p["lat"], p["lon"])
        return self

    def scale_units(self, factor: float, min_count: int = 1) -> "ScenarioSpec":
        """兵力规模缩放：按单元 count 缩放（不小于 min_count）。"""
        for u in self.units:
            u.count = max(min_count, int(round(u.count * factor)))
        return self

    def spread(self, factor: float) -> "ScenarioSpec":
        """相对中心拉开/收拢初始态势（距离缩放，不动任务区）。"""
        clat, clon = self.center["lat"], self.center["lon"]
        for u in self.units:
            u.lat = round(clat + (u.lat - clat) * factor, 6)
            u.lon = round(clon + (u.lon - clon) * factor, 6)
        return self

    # ------------------------------------------------------------ 校验
    def validate(self) -> List[str]:
        """结构性校验，返回错误列表（空列表=通过）。"""
        e: List[str] = []
        if not self.title or not self.title.strip():
            e.append("title 为空")
        if not self.sides:
            e.append("没有任何推演方（sides 为空）")
        names = [s.name for s in self.sides]
        if len(names) != len(set(names)):
            e.append("推演方重名：%s" % names)
        for s in self.sides:
            if not s.name:
                e.append("存在空名称推演方")
            for opp, code in s.posture.items():
                if opp not in names:
                    e.append("推演方 %s 的姿态指向了不存在的 %s" % (s.name, opp))
                if code not in POSTURE_CODES:
                    e.append("推演方 %s 对 %s 的姿态码非法：%s" % (s.name, opp, code))
            if s.camera:
                la, lo = s.camera.get("lat", 0), s.camera.get("lon", 0)
                if not (-90 <= la <= 90 and -180 <= lo <= 180):
                    e.append("推演方 %s 相机视点越界" % s.name)
        # 双向姿态完整性
        for a in self.sides:
            for b in self.sides:
                if a.name == b.name:
                    continue
                if b.name not in a.posture:
                    e.append("缺少姿态设置：%s -> %s（引擎要求两两显式设置）" % (a.name, b.name))
        # 单元
        if not self.units:
            e.append("没有任何单元（units 为空）")
        unames = [u.name for u in self.units]
        pairs = [(u.side, u.name) for u in self.units]
        if len(pairs) != len(set(pairs)):
            dup = sorted({"%s/%s" % k for k in pairs if pairs.count(k) > 1})
            e.append("同一推演方内单元重名（引擎按 (方,名) 查询会取第一个）：%s" % dup)
        uname_set = set(unames)
        per_side: Dict[str, int] = {}
        for u in self.units:
            if u.side not in names:
                e.append("单元 %s 归属的推演方 %s 不存在" % (u.name, u.side))
            per_side[u.side] = per_side.get(u.side, 0) + int(u.count)
            if u.kind not in KINDS:
                e.append("单元 %s 的类型非法：%s" % (u.name, u.kind))
            if not isinstance(u.dbid, int) or u.dbid <= 0:
                e.append("单元 %s 的 dbid 非法：%s" % (u.name, u.dbid))
            if not (-90 <= u.lat <= 90 and -180 <= u.lon <= 180):
                e.append("单元 %s 坐标越界：%s,%s" % (u.name, u.lat, u.lon))
            if u.count < 1:
                e.append("单元 %s 数量 <1" % u.name)
            if u.kind == "Aircraft" and u.alt is None and not u.base:
                e.append("飞机 %s 既没有高度也没有基地（引擎要求二者之一）" % u.name)
            if u.mission and u.mission not in [m.name for m in self.missions]:
                e.append("单元 %s 指向不存在的任务 %s" % (u.name, u.mission))
        for s in self.sides:
            if per_side.get(s.name, 0) == 0:
                e.append("推演方 %s 没有部署任何单元" % s.name)
        # 任务
        mnames = [m.name for m in self.missions]
        if len(mnames) != len(set(mnames)):
            e.append("任务重名：%s" % sorted({n for n in mnames if mnames.count(n) > 1}))
        for m in self.missions:
            if m.side not in names:
                e.append("任务 %s 归属推演方不存在" % m.name)
            if m.mtype not in ("Patrol", "Strike"):
                e.append("任务 %s 类型非法：%s" % (m.name, m.mtype))
            table = PATROL_SUBTYPES if m.mtype == "Patrol" else STRIKE_SUBTYPES
            if m.subtype not in table:
                e.append("任务 %s 子类型非法：%s（合法值：%s）"
                         % (m.name, m.subtype, ",".join(sorted(table))))
            if len(m.zone) < 3:
                e.append("任务 %s 的巡逻区少于 3 个参考点（引擎要求 3~10）" % m.name)
            if len(m.zone) > 10:
                e.append("任务 %s 的巡逻区超过 10 个参考点" % m.name)
            for u in m.units:
                if u not in uname_set:
                    e.append("任务 %s 引用了不存在的单元 %s" % (m.name, u))
                else:
                    uu = self.unit(u)
                    if uu and uu.side != m.side:
                        e.append("任务 %s（%s）分到了敌方/友方单元 %s（%s）"
                                 % (m.name, m.side, u, uu.side))
            if not m.units:
                e.append("任务 %s 没有分配任何单元（任务将无人执行）" % m.name)
        # 任务覆盖率告警（不阻断）
        assigned = {u for m in self.missions for u in m.units}
        for u in self.units:
            if u.name not in assigned:
                e.append("警告：单元 %s 未分配到任何任务（将原地待机）" % u.name)
        return e

    def raise_if_invalid(self) -> None:
        errs = [x for x in self.validate() if not x.startswith("警告")]
        if errs:
            raise SpecError("想定规格校验未通过：\n  - " + "\n  - ".join(errs))

    # ------------------------------------------------------------ 生成辅助
    def new_guid(self, salt: str = "") -> str:
        """由 (seed, salt) 确定性地生成 GUID —— 保证同一规格重复生成同结果。"""
        h = uuid.uuid5(uuid.NAMESPACE_URL, "%s|%s|%s" % (self.title, self.seed, salt))
        return str(h)

    def zone_ring(self, lat: float, lon: float, radius_nm: float,
                  n: int = 4, start_deg: float = 45.0) -> List[Dict[str, float]]:
        """以 (lat,lon) 为心生成规则多边形巡逻区（默认菱形/正方形）。"""
        pts = []
        for i in range(n):
            brg = math.radians(start_deg + i * 360.0 / n)
            dlat = radius_nm * math.cos(brg) / 60.0
            dlon = radius_nm * math.sin(brg) / (60.0 * (math.cos(math.radians(lat)) or 1.0))
            pts.append({"lat": round(lat + dlat, 6), "lon": round(lon + dlon, 6)})
        return pts


# ---------------------------------------------------------------- 便利函数
def offset(lat: float, lon: float, bearing_deg: float, dist_nm: float):
    """给定起点、方位、距离（海里）求终点经纬度。"""
    brg = math.radians(bearing_deg)
    dlat = dist_nm * math.cos(brg) / 60.0
    dlon = dist_nm * math.sin(brg) / (60.0 * (math.cos(math.radians(lat)) or 1.0))
    return round(lat + dlat, 6), round(lon + dlon, 6)
