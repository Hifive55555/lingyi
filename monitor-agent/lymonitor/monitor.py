# -*- coding: utf-8 -*-
"""
监控智能体 —— **可嵌入组件**（给其他智能体调用）。

跟 ``agent.py`` 里那个“独立智能体”是同一套判定，区别只在包装方式：

    MonitorAgent（agent.py）  = 平台里的一个独立智能体，自己算、自己推小窗
    Monitor    （本文件）      = 一个普通对象，主智能体 ``self.monitor = Monitor(self)``
                                 之后按需查询，不占智能体名额、不单独决策

**只读**：不调用任何 ``attack_*`` / ``set_*`` / ``plotted_course`` 等下发接口。

典型用法（和参考方案里 BattlefieldMonitor + SamBattalionDefense 的写法一致）：

    from lymonitor.monitor import Monitor

    class Agent(RuleAgentBase):
        def __init__(self, side_name, params=None):
            RuleAgentBase.__init__(self, side_name)
            self.monitor = Monitor(self)

        def initial(self, situation):
            self.monitor.setup(situation)          # 开局登记本方单位清单

        def step(self, time_elapse, situation):
            self.monitor.ensure(situation)         # 每周期只算一次，重复调用不重算
            for guid, u in self.aircrafts.items():
                if self.monitor.has_incoming(guid):        # ← 有没有弹朝我来
                    name, speed = self.monitor.incoming(guid)   # ← 弹型 + 当前弹速
                    ...

完整 API 见 ``monitor-agent/API.md``。
"""

import logging

from . import core

log = logging.getLogger("监控")


class Monitor(object):
    """物理作战域三维监控（可嵌入组件）。"""

    ENABLE = True
    # 不设门限：对方弹的射程未知，“朝我就算”。
    # 想收紧就改成 {'cpa_km':3.0,'max_km':90.0,'tgo_s':900.0}，None 表示全关。
    GATE = None
    # 一条情报算“在飞的弹”的最低速度（km/h ≈ 27 节）。
    # 用来挡掉平台里速度恒为 0 的杂项/平台类情报（实测会混进来）。
    MIN_MISSILE_KMH = 50.0
    # 实测（2026-11-17 诺曼底）：情报里除了真正的弹（'防空导弹#40', db=890），
    # 还会混进平台的“来袭告警”条目（'警告来袭#70' 等，也是 Type=1）。
    # 若确认它和真弹是同一件事的两种表示，把关键字填进来即可去重：
    #     IGNORE_NAME_KEYS = ('警告来袭',)
    IGNORE_NAME_KEYS = ()

    def __init__(self, agent=None, gate=None):
        self.agent = agent
        self.gate = gate if gate is not None else self.GATE
        self._cycle = 0
        self._last_sit = None
        self._now = 0.0
        self._own = []            # [{id,n,g,pos,hdg,spd,alt,dmg}]
        self._missiles = []       # [{id,n,db,pos,hdg,hdg_ok,spd,alt}]
        self._prev = {}           # {(unit_id,missile_id): (距离, 时间)}
        self._rows = []           # analyse() 的输出
        self._threats = {}        # unit_id -> [{'id','n','db','spd','d','cpa','tgo'}]
        self._ready = False
        self._stats = {'own': 0, 'missiles': 0, 'pairs': 0, 'hits': 0}

    # ================================================================ 生命周期
    @property
    def ready(self):
        """是否已成功跑过至少一次扫描。"""
        return self._ready

    def setup(self, situation):
        """开局调用：登记本方单位清单并空跑一次。返回自检摘要。"""
        if not self.ENABLE:
            return {}
        try:
            self.step(situation)
            self._ready = bool(self._own)
        except Exception as e:
            log.error("监控初始化异常: %s", e)
            self._ready = False
            return {}
        rep = {'本方单位': len(self._own), '敌方弹药': len(self._missiles),
               '被瞄准': len(self._threats)}
        log.info("监控就绪：%s", rep)
        return rep

    def ensure(self, situation, time_elapse=None):
        """
        保证本周期已经算过一次。多个下游共用同一份态势时只算一次。

        :return: bool, 本次是否真的重算
        """
        if not self.ENABLE:
            return False
        if situation is self._last_sit and time_elapse is None:
            return False
        if situation is self._last_sit and time_elapse == self._now:
            return False
        self.step(situation, time_elapse)
        return True

    def step(self, situation, time_elapse=None):
        """每个决策周期算一次。返回 {'own','missiles','pairs','hits'}。"""
        if not self.ENABLE:
            return {}
        self._cycle += 1
        self._last_sit = situation
        if time_elapse is not None:
            self._now = core.num(time_elapse)
        try:
            own = self._collect_own(situation)
            if own:
                self._own = own
            self._missiles = self._collect_missiles(situation)
            self._rows = core.analyse(self._own, self._missiles,
                                      prev=self._prev, now=self._now,
                                      gate=self.gate)
            self._prev = core.prev_of(self._own, self._missiles, self._now)
            self._threats = {r['id']: r['ms'] for r in self._rows if r['ms']}
            self._stats = {'own': len(self._own), 'missiles': len(self._missiles),
                           'pairs': len(self._own) * len(self._missiles),
                           'hits': sum(len(v) for v in self._threats.values())}
            self._ready = True
        except Exception as e:
            log.error("监控扫描异常: %s", e)
        return dict(self._stats)

    # ================================================================ 数据采集
    def _collect_own(self, situation):
        """
        本方单元：优先用主智能体身上的 Player 容器（对象属性最全），
        没有就退回 situation[0] 的摘要字典（组件单独跑时也能工作）。
        """
        out, seen = [], set()
        kinds = (('air', 'aircrafts'), ('sea', 'ships'),
                 ('sea', 'submarines'), ('land', 'facilitys'))
        for kind, attr in kinds:
            for guid, u in list((getattr(self.agent, attr, None) or {}).items()):
                p = core.pos(u)
                if p is None:
                    continue
                out.append({'id': guid,
                            'n': str(core.get(u, 'Name', '') or guid),
                            'g': kind, 'pos': p,
                            'hdg': core.num(core.get(u, 'CurrentHeading', 0)),
                            'spd': core.use_speed_kmh(core.get(u, 'CurrentSpeed', 0)),
                            'alt': core.num(core.get(u, 'CurrentAltitude', 0)),
                            'dmg': core.num(core.get(u, 'DamagePercent', 0))})
                seen.add(guid)
        if out:
            return out
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        for guid, u in (units or {}).items():
            if not isinstance(u, dict):
                continue
            cat = str(u.get('category') or u.get('Category') or '').lower()
            kind = {'aircraft': 'air', 'ship': 'sea', 'submarine': 'sea',
                    'facility': 'land'}.get(cat)
            if kind is None:
                continue
            p = core.pos(u)
            if p is None or guid in seen:
                continue
            out.append({'id': u.get('guid') or guid,
                        'n': str(u.get('name') or u.get('Name') or guid),
                        'g': kind, 'pos': p,
                        'hdg': core.num(core.get(u, 'CurrentHeading', 0)),
                        'spd': core.use_speed_kmh(core.get(u, 'CurrentSpeed', 0)),
                        'alt': core.num(core.get(u, 'CurrentAltitude', 0)),
                        'dmg': core.num(core.get(u, 'DamagePercent', 0))})
        return out

    def _collect_missiles(self, situation):
        """敌方弹药：情报里 Type==1（或名字像弹）。"""
        cts = situation[1] if isinstance(situation, (tuple, list)) and len(situation) > 1 else None
        if not isinstance(cts, dict):
            cts = getattr(self.agent, 'Contacts', None) or {}
        out = []
        for cid, c in cts.items():
            if not core.is_missile(c):
                continue
            _nm = str(core.get(c, 'Name', '') or '')
            if any(k in _nm for k in self.IGNORE_NAME_KEYS):
                continue
            p = core.pos(c)
            if p is None:
                continue
            spd = core.use_speed_kmh(core.get(c, 'CurrentSpeed', 0))
            if spd < self.MIN_MISSILE_KMH:
                # 速度 ≈ 0 的“弹”不是弹（平台里残留/舰船类的杂项情报）
                continue
            try:
                db = int(core.get(c, 'DBID'))
            except (TypeError, ValueError):
                db = None
            hdg_raw = core.get(c, 'CurrentHeading')
            out.append({'id': str(core.get(c, 'ID', cid) or cid),
                        'n': str(core.get(c, 'Name', '') or ''),
                        'db': db, 'pos': p,
                        'hdg': core.num(hdg_raw),
                        'hdg_ok': hdg_raw is not None,
                        'spd': spd,
                        'alt': core.num(core.get(c, 'CurrentAltitude', 0))})
        return out

    # ================================================================ 对外接口
    def incoming(self, target_guid):
        """
        **最严格的接口**：该目标是否正被弹朝我飞，返回最紧迫的一枚。

        :return: tuple 或 None, (弹型, 当前弹速 km/h)
        """
        rows = self._threats.get(target_guid)
        if not rows:
            return None
        r = rows[0]
        return (r['n'] or ('弹%s' % r['db']), r['spd'])

    def incoming_list(self, target_guid):
        """该目标当前所有朝它飞的弹：[(弹型, 当前弹速 km/h), ...]，按紧急度排序。"""
        return [(r['n'] or ('弹%s' % r['db']), r['spd'])
                for r in self._threats.get(target_guid, ())]

    def has_incoming(self, target_guid):
        """该目标是否被任何一枚弹朝我飞（bool）。"""
        return bool(self._threats.get(target_guid))

    def threats_for(self, target_guid):
        """
        给下游**动作**用的扩展：在弹型/弹速之外，额外给出情报 guid 与几何量。
        下游要真发弹、要算规避方向，必须拿到 ``id``（情报 guid）。

        :return: list of {'id','n','db','spd','d','cpa','tgo'}
                 id  : 情报 guid（直接当 attack_* 的 target 用）
                 spd : 当前弹速 km/h
                 d   : 当前弹目距离 km
                 cpa : 最近接近距离 km
                 tgo : 预计到最近接近点的时间 s（None = 无航向且算不出）
        """
        return list(self._threats.get(target_guid, ()))

    def route(self, category):
        """
        按作用对象类别取“当前确实被瞄准”的目标清单（报告里的“一进三出”三路）。

        :param category: 'air'/'aircraft' 或 'sea'/'ship'/'submarine' 或 'land'/'facility'
        :return: list of (guid, 单元名)
        """
        cat = str(category or '').lower()
        want = {'aircraft': 'air', 'air': 'air',
                'ship': 'sea', 'sea': 'sea', 'submarine': 'sea',
                'facility': 'land', 'land': 'land'}.get(cat)
        if want is None:
            return []
        return [(r['id'], r['n']) for r in self._rows if r['g'] == want and r['hit']]

    def rows(self):
        """本周期全量快照（空/海/陆三组、含未被攻击的），给小窗 / 日志用。"""
        return list(self._rows)

    def missiles(self):
        """本周期枚举到的敌方弹药（诊断用）。"""
        return list(self._missiles)

    def bare_contacts(self):
        """没被判成“朝我方任何单元飞来”的弹药（诊断用：看漏了什么）。"""
        hit = set()
        for rows in self._threats.values():
            for r in rows:
                hit.add(r['id'])
        return [m for m in self._missiles if m['id'] not in hit]

    def status(self):
        """本周期扫描摘要，供主智能体打日志或赛后核对。"""
        return {'cycle': self._cycle,
                'own': len(self._own),
                'missiles': len(self._missiles),
                'threatened': {g: len(v) for g, v in self._threats.items()},
                'stats': dict(self._stats),
                'gate': self.gate or 'none'}
