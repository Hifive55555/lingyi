# -*- coding: utf-8 -*-
"""想定文件 / 态势 XML 解析（.scen 的"可读视图"）。

想定文件 ``.scen`` 是「UTF-8 明文外壳 + LZ4 压缩体」，压缩体**不要自己解**
（实测 zlib/lz4/zstd/lzma 全部失败，见方法手册 §2.3）。正确做法是让引擎解：
``GetScenarioContent('x.scen')`` 返回完整的 ``<Scenario>`` XML，本模块把它解析成
结构化摘要（digest），用于：

* **验证**：生成的想定与规格逐项比对（verify.py）；
* **派生**：从既有想定里学到"它到底放了什么"（兵力构成、任务区、条令），
  再据此生成同类型想定集（family.py）；
* **实验报告**：给出"自然语言 → 想定"的可核对证据（单元数/任务数/坐标）。

XML 关键结构（实测）::

    <Scenario>
      <Title> <Description> <StartTime> <Duration> ...
      <Sides>
        <Side><ID><Name><IsAIOnly>
              <Postures><Posture_<对方GUID>>3</Posture_...></Postures>
              <Doctrine><WCS_Air>1</WCS_Air>...
              <ReferencePoints><RPoint><ID><Lon><Lat><Name>...</RPoint></ReferencePoints>
        </Side>
      </Sides>
      <ActiveUnits>
        <Aircraft><ID><Name><Side><DBID><Lon><Lat><DA 高度><CH 航向><Loadout>...
        <Ship> <Submarine> <Facility> <Satellite>
      </ActiveUnits>
      <Missions>
        <Patrol><ID><Name><Type>(0=SUB,1=NAVAL,2=AAW,3=LAND,5=SEAD,6=SEACONTROL)
                <AssignedUnitsList><ID>...
                <PatrolArea><RPoint><ID>...
        <Strike><Type>(0=AIR_INTERCEPT,1=LAND,2=NAVAL,3=SUB_STRIKE)
      </Missions>
      <GlobalWeather><WeatherProfile><Temp><RFR 降雨><FUR 云量><SS 海况>
    </Scenario>
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

#: 任务类型码（实测，见方法手册 §4.2）
PATROL_CODE = {0: "SUB", 1: "NAVAL", 2: "AAW", 3: "LAND", 4: "AIR", 5: "SEAD", 6: "SEACONTROL"}
STRIKE_CODE = {0: "AIR_INTERCEPT", 1: "LAND", 2: "NAVAL", 3: "SUB_STRIKE"}
CODE_OF_PATROL = {v: k for k, v in PATROL_CODE.items()}
CODE_OF_STRIKE = {v: k for k, v in STRIKE_CODE.items()}

UNIT_TAGS = {"Aircraft": "Aircraft", "Ship": "Ship", "Submarine": "Submarine",
             "Facility": "Facility", "Satellite": "Satellite"}
MISSION_TAGS = {"Patrol": "Patrol", "Strike": "Strike", "SupportMission": "Support",
                "Ferry": "Ferry", "Mining": "Mining", "MineClearing": "MineClearing",
                "Cargo": "Cargo"}


def _f(txt: Optional[str], default: float = 0.0) -> float:
    try:
        return float(txt)
    except (TypeError, ValueError):
        return default


def _child_text(e: ET.Element, tag: str, default: str = "") -> str:
    v = e.findtext(tag)
    return v if v is not None else default


def parse_scenario_xml(xml: str) -> Dict[str, Any]:
    """把 ``<Scenario>`` XML 解析成 digest 字典。"""
    root = ET.fromstring(xml)
    d: Dict[str, Any] = {
        "title": _child_text(root, "Title"),
        "description": _child_text(root, "Description"),
        "start_time_ticks": _child_text(root, "StartTime"),
        "duration_s": int(_f(_child_text(root, "Duration"), 0) / 1e7),   # 引擎用 100ns ticks
        "complexity": int(_f(_child_text(root, "Complexity"), 0)),
        "difficulty": int(_f(_child_text(root, "Difficulty"), 0)),
        "sides": [], "units": [], "missions": [], "reference_points": [],
        "weather": {}, "counts": {}, "raw_sizes": {"xml_bytes": len(xml)},
    }

    # ---------------- 气象
    wp = root.find("GlobalWeather/WeatherProfile")
    if wp is not None:
        d["weather"] = {"temp": int(_f(_child_text(wp, "Temp"), 0)),
                        "rainfall": int(_f(_child_text(wp, "RFR"), 0)),
                        "cloud": round(_f(_child_text(wp, "FUR"), 0.0), 3),
                        "seastate": int(_f(_child_text(wp, "SS"), 0))}

    # ---------------- 推演方
    id2side: Dict[str, str] = {}
    sides_el = root.find("Sides")
    for s in (sides_el.findall("Side") if sides_el is not None else []):
        sid = _child_text(s, "ID")
        name = _child_text(s, "Name")
        id2side[sid] = name
        postures = {}
        pe = s.find("Postures")
        if pe is not None:
            for ch in list(pe):
                tag = ch.tag
                if tag.startswith("Posture_"):
                    postures[tag[len("Posture_"):]] = ch.text
        doctrine = {}
        de = s.find("Doctrine")
        if de is not None:
            for ch in list(de):
                if not ch.tag.endswith("_Player") and len(list(ch)) == 0:
                    doctrine[ch.tag] = ch.text
        rps = []
        rpe = s.find("ReferencePoints")
        if rpe is not None:
            for rp in rpe.findall("RPoint"):
                item = {"id": _child_text(rp, "ID"), "name": _child_text(rp, "Name"),
                        "lat": _f(_child_text(rp, "Lat")), "lon": _f(_child_text(rp, "Lon")),
                        "side": name, "highlighted": _child_text(rp, "IH")}
                rps.append(item)
        d["reference_points"].extend(rps)
        d["sides"].append({"id": sid, "name": name, "postures": postures,
                           "doctrine": doctrine,
                           "is_ai_only": _child_text(s, "IsAIOnly", "false"),
                           "reference_point_count": len(rps)})

    # ---------------- 单元
    au = root.find("ActiveUnits")
    if au is not None:
        for kind_tag, kind in UNIT_TAGS.items():
            for u in au.findall(kind_tag):
                item = {
                    "id": _child_text(u, "ID"), "name": _child_text(u, "Name"),
                    "kind": kind, "side": _child_text(u, "Side"),
                    "dbid": int(_f(_child_text(u, "DBID"), 0)),
                    "lat": _f(_child_text(u, "Lat")), "lon": _f(_child_text(u, "Lon")),
                    "heading": _f(_child_text(u, "CH")), "alt": _f(_child_text(u, "DA")),
                    "loadoutid": int(_f(_child_text(u, "Loadout"), 0)),
                    "mission": _child_text(u, "AssignedMission"),
                }
                d["units"].append(item)
                c = d["counts"].setdefault(item["side"], {})
                c[kind] = c.get(kind, 0) + 1

    # ---------------- 任务（注意：<Missions> 挂在 <Side> 下面，不是 Scenario 直下）
    ms_all = []
    for s_el in (sides_el.findall("Side") if sides_el is not None else []):
        side_name = _child_text(s_el, "Name")
        for ms in s_el.findall("Missions"):
            for mt_tag, mtype in MISSION_TAGS.items():
                for m in ms.findall(mt_tag):
                    code = _child_text(m, "Type")
                    subtype = ""
                    if mtype == "Patrol":
                        subtype = PATROL_CODE.get(int(_f(code, -1)), code)
                    elif mtype == "Strike":
                        subtype = STRIKE_CODE.get(int(_f(code, -1)), code)
                    assigned = [(x.text or "").strip()
                                for x in m.findall("AssignedUnitsList/ID")]
                    zone = []
                    for area_tag in ("PatrolArea", "ProsecutionArea", "StrikeArea"):
                        area = m.find(area_tag)
                        if area is not None:
                            for rp in area.findall("RPoint"):
                                zone.append(_child_text(rp, "ID"))
                            if zone:
                                break
                    ms_all.append({
                        "id": _child_text(m, "ID"), "name": _child_text(m, "Name"),
                        "side": side_name, "mtype": mtype, "subtype": subtype,
                        "type_code": code, "assigned": assigned, "zone_ids": zone,
                    })
    d["missions"] = ms_all

    # ---------------- 单元上的 AssignedMission 是任务 GUID，换成任务名更好读
    mission_name = {m["id"]: m["name"] for m in d["missions"]}
    for u in d["units"]:
        if u.get("mission"):
            u["mission_name"] = mission_name.get(u["mission"], u["mission"])

    # ---------------- 由参考点 ID 回填巡逻区坐标
    rp_by_id = {rp["id"]: rp for rp in d["reference_points"]}
    for m in d["missions"]:
        pts = []
        for pid in m["zone_ids"]:
            rp = rp_by_id.get(pid)
            if rp:
                pts.append({"lat": rp["lat"], "lon": rp["lon"]})
        m["zone"] = pts
    return d


def digest_summary(d: Dict[str, Any]) -> str:
    """一行摘要，便于日志/表格。"""
    per_side = ", ".join("%s[%s]" % (s["name"], " ".join("%s:%d" % (k, v) for k, v in d["counts"].get(s["name"], {}).items()))
                         for s in d["sides"])
    mis = ", ".join("%s:%s/%s" % (m["name"], m["mtype"], m["subtype"]) for m in d["missions"])
    return "《%s》 %d 方 %d 单元（%s）；任务 %d 个（%s）；参考点 %d" % (
        d["title"], len(d["sides"]), len(d["units"]), per_side,
        len(d["missions"]), mis or "无", len(d["reference_points"]))
