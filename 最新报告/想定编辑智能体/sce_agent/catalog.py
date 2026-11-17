# -*- coding: utf-8 -*-
"""平台词表 / DBID 知识库。

三个能力：
1. **别名解析**：``resolve("052D")`` -> Platform(kind=Ship, dbid=2296, class=...)
   词表在 ``data/aliases.json``，可自由扩充；
2. **在线复核**：``verify(platform)`` 用 gRPC ``queryDatabase`` 向引擎确认
   "这个 dbid 在当前 DB 版本里到底是什么"，避免硬编码 DBID 漂移
   （实测：同一条目在不同版本里含义会变，例如 173 在本机 DB 里是
   "PSKR 司腾卡巡逻艇"而不是某些文档里写的 052D）；
3. **语义检索**：``search("052D")`` 在 ``data/db_catalog.json``（全量扫描结果，
   3532 艘舰 / 5494 架机 / 672 潜艇 / 3365 设施 / 140 卫星）里按类名模糊查，
   用于"给我找一个反潜巡逻机"这类自然语言需求。

``data/db_catalog.json`` 由 ``cli.py catalog scan`` 生成，来源是引擎自身的
``queryDatabase``，因此**与世界库版本严格一致**。
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEFAULT_LOADOUT = 3   #: 引擎内置的通用挂载方案（预备飞行）
_KIND_OF = {"ship": "Ship", "aircraft": "Aircraft", "submarine": "Submarine",
            "facility": "Facility", "satellite": "Satellite"}


@dataclass
class Platform:
    alias: str
    kind: str
    dbid: int
    klass: str = ""
    source: str = "alias"      # alias / search / user

    def as_dict(self):
        return {"alias": self.alias, "kind": self.kind, "dbid": self.dbid,
                "class": self.klass, "source": self.source}

    def __str__(self):
        return "%s(%s #%d %s)" % (self.alias, self.kind, self.dbid, self.klass)


class Catalog(object):
    """词表 + 全量平台目录 + 在线复核缓存。"""

    def __init__(self, data_dir: str = _DATA, aliases: Optional[dict] = None):
        self.data_dir = data_dir
        with open(os.path.join(data_dir, "aliases.json"), encoding="utf-8") as f:
            self.lex = json.load(f)
        if aliases:
            self.lex.setdefault("platforms", {}).update(aliases)
        self.platforms: Dict[str, dict] = self.lex.get("platforms", {})
        self.mission_types: Dict[str, dict] = self.lex.get("mission_types", {})
        self.places: Dict[str, dict] = self.lex.get("places", {})
        self.side_templates: Dict[str, str] = self.lex.get("templates", {})
        self._db: Optional[Dict[str, List[dict]]] = None
        self._lock = threading.Lock()
        self._verified: Dict[tuple, str] = {}
        self._loadouts = None

    # ------------------------------------------------------------ 全量目录
    @property
    def db(self) -> Dict[str, List[dict]]:
        if self._db is None:
            p = os.path.join(self.data_dir, "db_catalog.json")
            self._db = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        return self._db

    def search(self, keyword: str, kind: Optional[str] = None, limit: int = 20) -> List[Platform]:
        """在全量平台目录里按类名模糊检索。"""
        kw = keyword.lower()
        out: List[Platform] = []
        kinds = [kind.lower()] if kind else list(self.db.keys())
        for k in kinds:
            for row in self.db.get(k, []):
                if kw in (row.get("class") or "").lower():
                    out.append(Platform(keyword, _KIND_OF.get(k, k), row["dbid"],
                                        row.get("class", ""), "search"))
        out.sort(key=lambda p: len(p.klass))
        return out[:limit]

    # ------------------------------------------------------------ 别名解析
    def resolve(self, alias: str, kind: Optional[str] = None) -> Platform:
        """别名 -> Platform。先查词表（精确/去空格/大小写），再退回目录检索。"""
        key = (alias or "").strip()
        for cand in (key, key.upper(), key.lower(), key.replace(" ", "")):
            if cand in self.platforms:
                d = self.platforms[cand]
                p = Platform(cand, d["kind"], int(d["dbid"]), d.get("class", ""), "alias")
                if kind and p.kind.lower() != kind.lower():
                    raise KeyError("别名 %s 是 %s，与期望的 %s 不符" % (alias, p.kind, kind))
                return p
        hits = self.search(key, kind=kind, limit=5)
        if len(hits) == 1:
            hits[0].alias = key
            return hits[0]
        if hits:
            # 多个候选：优先类名最短（通常是最通用的型号名）
            hits[0].alias = key
            return hits[0]
        raise KeyError("词表与平台目录里都找不到 %r%s；可用 cli.py catalog search <关键词> 查找"
                       % (alias, ("（类型 %s）" % kind) if kind else ""))

    # ------------------------------------------------------------ 挂载方案
    #: 任务角色 -> 挂载方案类名里的关键词（用在"语义选挂载"上）
    LOADOUT_ROLE_KEYWORDS = {
        "NAVAL": ("反舰", "ASM", "AGM-84", "Kh-31", "Kh-35", "鹰击", "YJ-", "鱼叉", "Harpoon"),
        "LAND": ("对地", "GBU", "JDAM", "AGM-65", "AGM-154", "SDB", "Kh-29", "Kh-59", "空地"),
        "AAW": ("空空", "AIM-120", "AIM-9", "AA-12", "R-77", "AAM", "AIM-132"),
        "AIR_INTERCEPT": ("空空", "AIM-120", "AIM-9", "AA-12", "R-77", "AAM"),
        "SUB": ("反潜", "鱼雷", "ASW", "声呐", "Torpedo", "Mk-46", "Mk-54"),
        "SUB_STRIKE": ("反潜", "鱼雷", "ASW", "Torpedo"),
        "SEAD": ("反辐射", "Kh-31P", "AGM-88", "ARM"),
        "SEACONTROL": ("反舰", "ASM", "AGM-84", "鹰击"),
        "AEW": ("预警", "AEW"),
        "EW": ("干扰", "DECM", "电子"),
        "ISR": ("侦察", "ISR", "光电"),
    }

    @property
    def loadouts(self) -> Dict[str, List[dict]]:
        if self._loadouts is None:
            p = os.path.join(self.data_dir, "loadouts.json")
            self._loadouts = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        return self._loadouts

    def loadout_for(self, aircraft_dbid: int, role: Optional[str] = None):
        """按机型 + 任务角色挑一个真实想定里出现过的挂载方案。

        数据来自 17 份官方/竞赛想定里 ``<Loadout><DBID>`` 的统计（data/loadouts.json），
        因此"用过的方案一定是对的"。返回 (loadoutid, name) 或 (None, "")。
        """
        items = self.loadouts.get(str(int(aircraft_dbid))) or []
        if role:
            kws = self.LOADOUT_ROLE_KEYWORDS.get(role.upper(), ())
            for kw in kws:
                for it in items:
                    if kw.lower() in (it.get("name") or "").lower():
                        return int(it["loadout"]), it.get("name", "")
        if items:
            return int(items[0]["loadout"]), items[0].get("name", "")
        # 没查到该机型的真实挂载方案时，退到引擎的通用"预备飞行"方案（DBID=3）。
        # 实测：loadoutid=0 的飞机**无法被分配到任务**（AssignUnitListToMission
        # 会把这个单元的 GUID 当作失败项返回）；而 DBID=3 的"预备飞行[可用]"对所有
        # 机型都成立，可以正常编入任务。
        return DEFAULT_LOADOUT, "(预备飞行[可用])"

    def suggest(self, keyword: str, kind: Optional[str] = None, limit: int = 8) -> List[str]:
        return ["%d %s" % (p.dbid, p.klass) for p in self.search(keyword, kind, limit)]

    # ------------------------------------------------------------ 在线复核
    def verify(self, client, p: Platform) -> Platform:
        """用引擎 queryDatabase 复核 (kind,dbid) 的真实类名，失败抛异常。"""
        if not client:
            return p
        ck = (p.kind.lower(), int(p.dbid))
        with self._lock:
            if ck in self._verified:
                p.klass = self._verified[ck] or p.klass
                return p
        ok, klass = client.query_db(p.kind, p.dbid)
        if not ok:
            raise KeyError("引擎里不存在该平台：%s / dbid=%s" % (p.kind, p.dbid))
        with self._lock:
            self._verified[ck] = klass
        p.klass = klass or p.klass
        return p

    def add(self, alias: str, kind: str, dbid: int, klass: str = "",
            persist: bool = True) -> Platform:
        p = Platform(alias, kind, int(dbid), klass, "user")
        self.platforms[alias] = {"kind": kind, "dbid": int(dbid), "class": klass}
        if persist:
            path = os.path.join(self.data_dir, "aliases.json")
            lex = json.load(open(path, encoding="utf-8"))
            lex.setdefault("platforms", {})[alias] = self.platforms[alias]
            json.dump(lex, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return p

    # ------------------------------------------------------------ 其他词表
    def place(self, name: str) -> Optional[dict]:
        for k, v in self.places.items():
            if k in name or name in k:
                return dict(v, name=k)
        return None

    def mission_type(self, name: str):
        """中文任务类型 -> (mtype, subtype)。"""
        for k, v in self.mission_types.items():
            if k in name or name in k:
                return v["mtype"], v["subtype"]
        return None
