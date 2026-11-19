# -*- coding: utf-8 -*-
"""
离线自测：用假的 entitys.player / agent_base 驱动 Mission_all_red.Agent，
检查 26+5 个任务、挂载、WRA、BOL、舰船航线是否按预期下发。

运行： python tools/selftest_offline.py
"""
import os
import re
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ---------------- 假平台对象 ----------------
EVENTS = []          # [(kind, payload)]
LOADOUTS = {}        # unit_name -> loadout_id
ASSIGNED = {}        # mission_name -> [unit names]
MISSIONS = {}        # mission_name -> kind


class Reply(object):
    def __init__(self, code=0):
        self.code = code
        self.result = b'{}'


class Recorder(object):
    """任何未显式定义的方法都记录一次调用并返回成功。"""

    def __init__(self, tag):
        self._tag = tag

    def __getattr__(self, item):
        def fn(*a, **k):
            EVENTS.append((self._tag, item, a, k))
            return Reply(0)
        return fn


class FakeMission(Recorder):
    def __init__(self, name, kind):
        Recorder.__init__(self, kind)
        self.Name = name
        self._game_server = None


class FakeUnit(Recorder):
    def __init__(self, guid, name, category, dbid):
        Recorder.__init__(self, 'unit')
        self.ID = guid
        self.Name = name
        self.DBID = dbid
        self.category = category
        self.Mounts = {}
        self.Magazines = {}
        self.Loadouts = {}
        self._course = []

    # 需要真实返回值的几个
    def get_way_points_info(self):
        return list(self._course)

    def plotted_course(self, course_list):
        self._course = list(course_list)
        EVENTS.append(('unit', 'plotted_course', (self.Name, course_list), {}))
        return Reply(0)

    def clear_plotted_course(self):
        self._course = []
        return Reply(0)

    def set_desired_speed(self, spd):
        EVENTS.append(('unit', 'set_desired_speed', (self.Name, spd), {}))
        return Reply(0)

    def withdraw_from_mission(self):
        EVENTS.append(('unit', 'withdraw_from_mission', (self.Name,), {}))
        return Reply(0)

    def assign_to_mission(self, mission_name):
        EVENTS.append(('unit', 'assign_to_mission', (self.Name, mission_name), {}))
        return Reply(0)


class FakeServer(object):
    # True = 真的扣弹（模拟正常平台）；False = 回“成功”但不扣弹（模拟蓝方踩过的坑）
    AMMO_DECREMENT = True

    def __init__(self):
        self.created = []

    def __getattr__(self, item):
        def fn(*a, **k):
            if item == 'api_create_support_mission':
                m = FakeMission(a[1], 'support')
                self.created.append(m)
                MISSIONS[a[1]] = 'support'
                EVENTS.append(('create', a[1], a[2], {}))
                return m
            if item == 'api_create_patrol_mission':
                m = FakeMission(a[1], 'patrol')
                self.created.append(m)
                MISSIONS[a[1]] = 'patrol'
                EVENTS.append(('create', a[1], a[3], {}))
                return m
            if item == 'api_assign_units_to_mission':
                ASSIGNED.setdefault(a[2], []).extend(a[1])
                EVENTS.append(('assign', a[2], len(a[1]), {}))
                return Reply(0)
            if item == 'api_attack_BOL':
                unit, lat, lon, mount, weapon, qty = a[:6]
                course = k.get('course') or []
                pts = course or [(lat, lon)]
                # 模拟平台硬限制：单条指令 300 字符
                cmd_len = R.Agent._bol_cmd_len(unit.ID, mount, weapon, qty,
                                               lat, lon, pts)
                EVENTS.append(('bol_try', unit, cmd_len, len(pts)))
                if cmd_len > 300:
                    return Reply(-1)
                if self.AMMO_DECREMENT:
                    _consume(unit, weapon, qty)
                EVENTS.append(('bol', unit, lat, lon, mount, weapon, qty, course))
                return Reply(0)
            EVENTS.append(('api', item, a, k))
            return Reply(0)
        return fn


def _consume(unit, weapon, qty):
    """模拟平台扣弹：Mounts/Magazines 里对应武器 CurrentLoad -= qty"""
    for attr in ('Mounts', 'Magazines'):
        cont = getattr(unit, attr, {}) or {}
        for mv in cont.values():
            for rec in (mv.get('WeaponRecs') or {}).values():
                if rec.get('WeaponDBID') == weapon:
                    rec['CurrentLoad'] = max(0, int(rec.get('CurrentLoad', 0)) - qty)


class FakePlayer(object):
    Name = '红方'

    def __init__(self, side_name):
        self.Name = side_name
        self.log = None
        self._game_server = FakeServer()
        self.created_missions = []
        self.units_of_name = {}
        self.aircrafts = {}
        self.ships = {}
        self.submarines = {}
        self.facilitys = {}
        self.satellites = {}
        self.weapons = {}
        self.groups = {}
        self._units = {}

    # ---- 平台接口 ----
    def get_unit(self, guid):
        return self._units.get(guid)

    def create_support_mission(self, name, points):
        return self._game_server.api_create_support_mission(self, name, points)

    def create_patrol_mission(self, name, mtype, area):
        return self._game_server.api_create_patrol_mission(self, name, mtype, area)

    def assign_units_to_mission(self, unit_list, mission_name, is_escort=False):
        return self._game_server.api_assign_units_to_mission(
            self, unit_list, mission_name, is_escort)

    def set_aircraft_loadout_plan_time(self, unit_id, loadout_id):
        LOADOUTS[unit_id] = loadout_id
        EVENTS.append(('loadout', unit_id, loadout_id, {}))
        return Reply(0)

    def __getattr__(self, item):
        # doctrine_* / wra_* 等一律记录
        if item.startswith('_'):
            raise AttributeError(item)

        def fn(*a, **k):
            EVENTS.append(('side', item, a, k))
            return Reply(0)
        return fn


# ---------------- 注入桩模块 ----------------
agent_base = types.ModuleType('entitys.agent_base')
agent_base.RuleAgentBase = type('RuleAgentBase', (FakePlayer,), {})
sys.modules['entitys.agent_base'] = agent_base

player_mod = types.ModuleType('entitys.player')
player_mod.Player = FakePlayer
sys.modules['entitys.player'] = player_mod

import entitys  # noqa: E402
entitys.agent_base = agent_base
entitys.player = player_mod

import Mission_all_red as R  # noqa: E402


# ---------------- 构造态势 ----------------
# (name, category, dbid)
UNITS = [
    # 戴高乐航母
    ('卡-27M型“蜗牛A”反潜直升机 #1', 'Aircraft', 4327),
    ('卡-27M型“蜗牛A”反潜直升机 #2', 'Aircraft', 4327),
    ('“阵风”M型战斗机 #1', 'Aircraft', 3231),
    ('“阵风”M型战斗机 #2', 'Aircraft', 3231),
    ('“阵风”M型战斗机 #3', 'Aircraft', 3231),
    ('“阵风”M型战斗机 #4', 'Aircraft', 3231),
    ('“阵风”M型战斗机 #5', 'Aircraft', 3231),
    ('“阵风”M型战斗机 #6', 'Aircraft', 3231),
    # NK
    ('苏-34型“鸭嘴兽”攻击机 #1', 'Aircraft', 4960),
    ('苏-34型“鸭嘴兽”攻击机 #2', 'Aircraft', 4960),
    ('苏-34型“鸭嘴兽”攻击机 #3', 'Aircraft', 4960),
    ('苏-75 战斗机 #1', 'Aircraft', 5327),
    ('苏-75 战斗机 #2', 'Aircraft', 5327),
    ('苏-35S型“侧卫E”战斗机 #1', 'Aircraft', 50002),
    ('苏-35S型“侧卫E”战斗机 #2', 'Aircraft', 50002),
    # BL
    ('苏-24MP型“击剑手F”电子情报侦察机 #1', 'Aircraft', 476),
    ('苏-27SM/SM3型战斗机 #1', 'Aircraft', 4696),
    ('苏-27SM/SM3型战斗机 #2', 'Aircraft', 4696),
    ('苏-27SM/SM3型战斗机 #5', 'Aircraft', 4696),
    ('苏-27SM/SM3型战斗机 #6', 'Aircraft', 4696),
    ('“苏霍伊”S-70无人侦察攻击机 #1', 'Aircraft', 4906),
    ('“苏霍伊”S-70无人侦察攻击机 #2', 'Aircraft', 4906),
    ('“苏霍伊”S-70无人侦察攻击机 #3', 'Aircraft', 4906),
    ('“苏霍伊”S-70无人侦察攻击机 #4', 'Aircraft', 4906),
    # CT
    ('伊尔-96-400TZ型加油机 #1', 'Aircraft', 4440),
    ('伊尔-96-400TZ型加油机 #2', 'Aircraft', 4440),
    ('伊尔-22PP型“伐木人”侦察机 #1', 'Aircraft', 4607),
    ('苏-30SM“侧卫G”战斗机 #1', 'Aircraft', 4959),
    ('苏-30SM“侧卫G”战斗机 #2', 'Aircraft', 4959),
    ('苏-30SM“侧卫G”战斗机 #3', 'Aircraft', 4959),
    ('苏-30SM“侧卫G”战斗机 #4', 'Aircraft', 4959),
    ('苏-57型隐身战斗机 #1', 'Aircraft', 7574),
    ('苏-57型隐身战斗机 #2', 'Aircraft', 7574),
    ('苏-57型隐身战斗机 #3', 'Aircraft', 7574),
    # BM
    ('苏-75 战斗机 #3', 'Aircraft', 5327),
    ('Tu-160M Blackjack 轰炸机 #1', 'Aircraft', 5554),
    # TF
    ('“阵风”C型战斗机 #1', 'Aircraft', 3230),
    ('“阵风”C型战斗机 #2', 'Aircraft', 3230),
    ('“阵风”C型战斗机 #3', 'Aircraft', 3230),
    ('“阵风”C型战斗机 #4', 'Aircraft', 3230),
    # BT
    ('JAS 39E 型“鹰狮NG”战斗机 #1', 'Aircraft', 3201),
    ('JAS 39E 型“鹰狮NG”战斗机 #2', 'Aircraft', 3201),
    ('JAS 39E 型“鹰狮NG”战斗机 #3', 'Aircraft', 3201),
    ('JAS 39E 型“鹰狮NG”战斗机 #4', 'Aircraft', 3201),
    ('苏-35S型“侧卫E”战斗机 #5', 'Aircraft', 50002),
    ('苏-35S型“侧卫E”战斗机 #6', 'Aircraft', 50002),
    # 野战机场
    ('“神经元”无人机 #1', 'Aircraft', 3900),
    ('“神经元”无人机 #2', 'Aircraft', 3900),
    ('“神经元”无人机 #3', 'Aircraft', 3900),
    ('“神经元”无人机 #4', 'Aircraft', 3900),
    ('Bayraktar TB2 作战无人机 #1', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #2', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #3', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #4', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #5', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #6', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #7', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #8', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #9', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #10', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #13', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #14', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #15', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #16', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #17', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #18', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #19', 'Aircraft', 5394),
    ('Bayraktar TB2 作战无人机 #20', 'Aircraft', 5394),
    ('Forpost“前哨-R”无人机 #1', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #2', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #3', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #4', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #5', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #6', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #7', 'Aircraft', 50008),
    ('Forpost“前哨-R”无人机 #8', 'Aircraft', 50008),
    # 23900
    ('卡-29RLD 型“蜗牛”预警直升机 #1', 'Aircraft', 52),
    # 水面舰艇
    ('“雷鸣”号护卫舰 #1', 'Ship', 1),
    ('“雷鸣”号护卫舰 #2', 'Ship', 1),
    ('“雷鸣”号护卫舰 #3', 'Ship', 1),
    ('“雷鸣”号护卫舰 #4', 'Ship', 1),
    ('“雷鸣”号护卫舰 #5', 'Ship', 1),
    ('“雷鸣”号护卫舰 #8', 'Ship', 1),
    ('“雷鸣”号护卫舰 #10', 'Ship', 1),
    ('“蟾蜍”I级坦克登陆舰 #1', 'Ship', 2),
    ('“蟾蜍”I级坦克登陆舰 #2', 'Ship', 2),
    ('“蟾蜍”I级坦克登陆舰 #3', 'Ship', 2),
    ('“蟾蜍”I级坦克登陆舰 #4', 'Ship', 2),
    ('“蟾蜍”I级坦克登陆舰 #5', 'Ship', 2),
    ('“蟾蜍”I级坦克登陆舰 #6', 'Ship', 2),
    ('“蟾蜍”I级坦克登陆舰 #7', 'Ship', 2),
    ('23900型船坞登陆舰 #1', 'Ship', 3238),
    ('PR.2235.0护卫舰 #1', 'Ship', 2816),
    ('PR.2235.0护卫舰 #2', 'Ship', 2816),
    ('R 91“戴高乐”号航空母舰#1', 'Ship', 2754),
    ('S 107“特拉法尔加”号攻击型核潜艇', 'Submarine', 586),
    ('S-400地空导弹营#1', 'Facility', 1882),
    ('S-400地空导弹营#2', 'Facility', 1882),
    # 地面
    ('伊斯坎德尔导弹营 #2', 'Facility', 3222),
    ('沙赫德无人机发射车 #2', 'Facility', 4142),
    ('鸡窝雷达', 'Facility', 1439),
]


def build_situation():
    units = {}
    for i, (name, cat, dbid) in enumerate(UNITS):
        guid = 'g%03d' % i
        units[guid] = {'guid': guid, 'name': name, 'category': cat, 'dbid': dbid}
    return (units, {})


class AgentProxy(R.Agent):
    """把假单元对象塞进 Player 的 get_unit。"""

    def __init__(self, units):
        R.Agent.__init__(self, '红方', None)
        for guid, d in units.items():
            u = FakeUnit(guid, d['name'], d['category'], d['dbid'])
            self._units[guid] = u
        # 给 BOL 相关单元配武器（按名字找，避免增删单元后 guid 序号错位）
        #   实测复刻：111.txt 说“PR.2235.0护卫舰#1 打 12 发锆石”，但想定里
        #   12 发锆石其实在 #2 上，#1 上根本没有 3361 —— 检验“自动换同型单元”。
        def _by_name(kw):
            for g, u in self._units.items():
                if kw in u.Name:
                    return g
            return None

        g1 = _by_name('PR.2235.0护卫舰 #1')
        g2 = _by_name('PR.2235.0护卫舰 #2')
        gi = _by_name('伊斯坎德尔导弹营 #2') or _by_name('伊斯坎德尔')
        gs = _by_name('见证者') or _by_name('沙赫德')
        if g1:
            self._units[g1].Mounts = {  # PR.2235.0 #1：没有锆石
                'm0': {'Component': {'DBID': 9000},
                       'WeaponRecs': {'w': {'WeaponDBID': 1227, 'CurrentLoad': 32}}}}
        if g2:
            self._units[g2].Mounts = {  # PR.2235.0 #2：12 发锆石
                'm1': {'Component': {'DBID': 9001},
                       'WeaponRecs': {'w': {'WeaponDBID': 3361, 'CurrentLoad': 12}}}}
        if gi:
            self._units[gi].Mounts = {  # 伊斯坎德尔营：6 发 SS-26“石头”
                'm2': {'Component': {'DBID': 9002},
                       'WeaponRecs': {'w': {'WeaponDBID': 1235, 'CurrentLoad': 6}}}}
        if gs:
            self._units[gs].Mounts = {  # 沙赫德发射车
                'm3': {'Component': {'DBID': 9003},
                       'WeaponRecs': {'w': {'WeaponDBID': 4142, 'CurrentLoad': 12}}}}


def main():
    sit = build_situation()
    a = AgentProxy(sit[0])

    # --- initial ---
    a.initial(sit)
    print('support missions :', sum(1 for m in MISSIONS.values() if m == 'support'))
    print('patrol missions  :', sum(1 for m in MISSIONS.values() if m == 'patrol'))

    # --- step（BOL 在开局后；要跑多轮：停车→下发→核对弹药）---
    a.step(0, sit)      # 地面发射车本周期只停车；舰船直接开火
    a.step(30, sit)     # 地面发射车开火
    a.step(60, sit)     # 核对弹药，确认发射

    # ---- 断言 ----
    n_support = len([n for n, k in MISSIONS.items() if k == 'support'])
    n_patrol = len([n for n, k in MISSIONS.items() if k == 'patrol'])
    assert n_support == 22, n_support
    assert n_patrol == 16, n_patrol

    # 每个任务至少分配了单元；这些是“只建任务、暂不分配”的
    NO_UNIT = ('北阵风-1', '北阵风-2', 'C2')
    empty = [n for n in MISSIONS if n not in NO_UNIT and not ASSIGNED.get(n)]
    assert not empty, '这些任务没有分配到单元: %s' % empty
    for n in NO_UNIT:
        assert not ASSIGNED.get(n), n

    # 中间保船：前哨 #1~#4 + #7#8 共 6 架；#5#6 已改去 北制空
    mid = [a._units[g].Name for g in ASSIGNED.get('中间保船', [])]
    print('中间保船 units    :', len(mid), mid)
    assert len(mid) == 6, mid
    assert all('前哨' in n or 'Forpost' in n for n in mid), mid
    nb1 = [a._units[g].Name for g in ASSIGNED.get('北阵风-1', [])]
    print('北阵风-1 units    :', nb1)
    assert not nb1, nb1          # 前哨#5#6 已改去「北制空」，这里应留空

    # 登陆编队支援任务 A/B/C1/D/E 的舰船数量（23900 已移出 C1；E 加了 PR.2235.0#1）
    assert len(ASSIGNED.get('A', [])) == 2
    assert len(ASSIGNED.get('B', [])) == 2
    assert len(ASSIGNED.get('C1', [])) == 3
    assert len(ASSIGNED.get('D', [])) == 3
    assert any('PR.2235.0' in a._units[g].Name for g in ASSIGNED.get('E', []))
    assert not any('23900' in a._units[g].Name for g in ASSIGNED.get('C1', []))

    # 左阵风5：阵风M#5 + 特拉法尔加潜艇 + 雷鸣#1 + 戴高乐#1
    #   （PR.2235.0#2 已移出：它留在原地把 12 发锆石 BOL 打完）
    zj5 = [a._units[g].Name for g in ASSIGNED.get('左阵风5', [])]
    print('左阵风5 units    :', zj5)
    assert len(zj5) == 4, zj5
    assert any('特拉法尔加' in n for n in zj5), zj5
    assert not any('PR.2235.0' in n for n in zj5), zj5
    assert any('戴高乐' in n for n in zj5), zj5
    # 左阵风5 的潜艇/舰艇油门都设为最大（Flank）：2 舰 + 2 潜 = 4 条指令
    max_th = [e for e in EVENTS
              if e[1] in ('support_set_throttle_transit_ship',
                          'support_set_throttle_station_ship',
                          'support_set_throttle_transit_submarine',
                          'support_set_throttle_station_submarine')
              and e[2] and getattr(e[2][0], 'name', '') == 'Flank']
    print('max throttle     :', len(max_th))
    assert len(max_th) == 4, len(max_th)
    # 23900 型船坞登陆舰#1：三点航线、22 节
    plots = [e for e in EVENTS if e[0] == 'unit' and e[1] == 'plotted_course']
    assert len(plots) == 1, plots
    assert '23900' in plots[0][2][0], plots[0][2][0]
    assert plots[0][2][1] == [(50.084713, -0.857245), (49.678446, -1.022172),
                              (49.638315, -0.997032)], plots[0][2][1]

    # 战前移动：先 15 个单元（2+4+3+2+3+1），A~E 重新分配前再归位 14 次
    moves = [e for e in EVENTS if e[1] == 'unit_new_position']
    print('prewar moves     :', len(moves))
    assert len(moves) == 29, len(moves)

    def _dest(e):
        k = e[3] or {}
        return k.get('lon_lat') or k.get('long_lat')

    dests = sorted(set(tuple(_dest(e)) for e in moves))
    print('prewar dests     :', dests)
    # 平台接口要 (经度, 纬度)，所以下发值应是 (lon, lat)
    for d in ((50.239722, -1.176534), (50.226962, -0.757203),
              (50.459180, 0.102357), (49.101122, -3.245283),
              (51.679603, 1.513794), (53.281799, 1.746800)):
        assert d[::-1] in dests, (d, dests)

    # 战前移动之后：每艘船都要“取消分配单元”一次（否则平台会把船拉回默认起点）；
    # 分配完 A~E 之后还要再来一轮“取消分配 → 重新分配”
    wd = [e for e in EVENTS if e[0] == 'unit' and e[1] == 'withdraw_from_mission']
    n_ship = sum(1 for _n, c, _d in UNITS if c in ('Ship', 'Submarine'))
    n_ae = sum(len(ASSIGNED.get(k, []))
               for k in ('A', 'B', 'C1', 'D', 'E'))
    print('withdraw calls   :', len(wd), '= 战前 %d + A~E 重分配 %d'
          % (n_ship, n_ae))
    assert len(wd) == n_ship + n_ae, (len(wd), n_ship, n_ae)
    reasm = [e for e in EVENTS if e[0] == 'unit' and e[1] == 'assign_to_mission']
    print('reassign calls   :', len(reasm))
    assert len(reasm) == n_ae, (len(reasm), n_ae)
    # 顺序：先战前移动，再取消分配
    seq = [e[1] for e in EVENTS
           if e[1] in ('unit_new_position', 'withdraw_from_mission')]
    assert seq.index('unit_new_position') < seq.index('withdraw_from_mission'), seq

    # 单元级武器规则：雷鸣 5 舰 × 4 类目标 + S-400 2 营 × 3 类 × 2 型弹 = 32 条
    uwra = [e for e in EVENTS if e[0] == 'unit' and e[1] == 'wra_qty_salvo']
    print('unit WRA calls   :', len(uwra))
    assert len(uwra) == 32, len(uwra)
    assert all(str(e[2][0]) in ('3221', '2103', '2104') for e in uwra), uwra[:3]
    assert all(e[2][2] == '0' for e in uwra)

    # 任务级武器规则：A/B/C1/D/E 5 个任务 × 4 类目标 = 20 条（必须在分配之后）
    mwra = [e for e in EVENTS if e[0] == 'support' and e[1] == 'wra_qty_salvo']
    print('mission WRA calls:', len(mwra))
    assert len(mwra) == 20, len(mwra)

    # 水面舰艇油门：A~E 六个任务，出航=巡航(Cruise)、阵位=全速(Full)
    # 水面舰艇油门：A~E 六个任务(12 条) + 左阵风5 的舰艇(2 条) = 14
    ship_th = [e for e in EVENTS
               if e[1] in ('support_set_throttle_transit_ship',
                           'support_set_throttle_station_ship')]
    print('ship throttle    :', len(ship_th))
    assert len(ship_th) == 14, len(ship_th)

    # 挂载：应有 22 组（卡27Mx2, 阵风Mx6, 苏34x3, 苏75x2, 苏35x2, 苏24x1,
    #   苏27x2, S70x4, 伊尔96x2, 伊尔22x1, 苏30x4, 苏57x3, 苏75x1, 图160x1,
    #   阵风C#1, 阵风C#2, 阵风C#3#4, 鹰狮x4, 苏35x2, 神经元x4, TB2x2, 前哨x2, 卡29x1）
    print('loadouts set     :', len(LOADOUTS))
    for guid, lid in sorted(LOADOUTS.items()):
        print('   %-40s -> %s' % (a._units[guid].Name, lid))

    # 巡逻任务的执行单元核对
    print('patrol assignments:')
    for n in ('阵风3', '神经元1', '神经元2', '神经元3', '阵风1', '阵风2',
              'TB1', 'TB2', 'TB3', 'S70-1', 'S70-2', '反潜巡逻',
              'A', 'B', 'C1', 'D', 'E'):
        if n in ASSIGNED:
            print('   %-8s <- %s' % (n, [a._units[g].Name for g in ASSIGNED[n]]))
    assert len(ASSIGNED['阵风3']) == 3          # 阵风C#3 + TB2#7#8
    assert len(ASSIGNED['神经元3']) == 2        # 神经元#3#4
    assert len(ASSIGNED['TB1']) == 4
    assert len(ASSIGNED['S70-1']) == 3          # S-70#1 + 苏-30#1#2
    assert len(ASSIGNED['S70-2']) == 3          # S-70#3 + 苏-30#3#4
    assert len(ASSIGNED['阵风2']) == 3          # 阵风C#2 + 苏-34#1#2
    # 新增的三条制空巡逻
    assert len(ASSIGNED['左制空']) == 3, ASSIGNED.get('左制空')
    assert len(ASSIGNED['右制空']) == 7, ASSIGNED.get('右制空')
    assert len(ASSIGNED['北制空']) == 6, ASSIGNED.get('北制空')
    print('左制空 <-', [a._units[g].Name for g in ASSIGNED['左制空']])
    print('右制空 <-', [a._units[g].Name for g in ASSIGNED['右制空']])
    print('北制空 <-', [a._units[g].Name for g in ASSIGNED['北制空']])

    # 苏27-2 已暂时注释掉，这里不再校验

    # 出航油门=加速（Throttle.Full=4）：神经元2、神经元3、阵风2、苏57-2
    fast = [e for e in EVENTS
            if e[1] in ('patrol_set_throttle_transit', 'support_throttle_transit')
            and e[2] and getattr(e[2][0], 'name', '') == 'Flank']
    print('fast-transit missions:', len(fast))
    assert len(fast) == 5, len(fast)   # 神经元2/3、阵风2、苏57-2、中间保船（出航油门=加力）

    # 12 个巡逻任务的任务条令：对地自由开火（mission 级）
    land_free = [e for e in EVENTS
                 if e[0] == 'patrol'
                 and e[1] == 'doctrine_weapon_control_status_land'
                 and e[2] and getattr(e[2][0], 'value', None) == 0]
    print('patrol mission land-free:', len(land_free))
    assert len(land_free) == 11, len(land_free)   # S70-3 已删除

    # 总条令对地/反辐射 WRA：SBU-64 5 + SBU-54 5 + KH-58 1 + UPAB-500B 5 = 16
    gwra = [e for e in EVENTS if e[0] == 'side' and e[1] == 'wra_qty_salvo'
            and e[2] and str(e[2][0]) in ('2596', '1603', '50002', '3712')]
    print('ground WRA calls :', len(gwra))
    assert len(gwra) == 16, len(gwra)

    # 阵风C#2 的挂载已换成 SBU-54 + 重型挂载 AAM Load（不是“流星 Maximum CAP”）
    c2 = [a._units[g].Name for g in LOADOUTS if a._units[g].Name.endswith('#2')
          and '阵风' in a._units[g].Name and 'C型' in a._units[g].Name]
    assert c2, '阵风C#2 没有设置挂载'

    # ⑨ 鸡窝雷达：应真的下发过“开雷达”（switch_radar(True)）
    radar = [e for e in EVENTS
             if e[0] == 'unit' and e[1] == 'switch_radar' and e[2] and e[2][0]]
    print('radar switched on:', len(radar))
    assert radar, '没有给鸡窝雷达下发开雷达指令'

    # 静态检查：所有 self._log(...) 调用都必须是 (级别, 消息) 两个参数
    import ast
    import io as _io
    src = _io.open(os.path.join(ROOT, 'Mission_all_red.py'), encoding='utf-8').read()
    bad_log = [(n.lineno, len(n.args))
               for n in ast.walk(ast.parse(src))
               if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute)
               and n.func.attr == '_log' and len(n.args) != 2]
    assert not bad_log, '这些 _log 调用参数个数不对: %s' % bad_log

    # BOL：只应下发 3 次（第二轮靠“弹药减少”确认，不应重复下发）
    bols = [e for e in EVENTS if e[0] == 'bol']
    print('BOL calls        :', len(bols))
    for b in bols:
        _k, unit, lat, lon, mount, weapon, qty, course = b[:8]
        print('   unit=%-22s target=(%.6f,%.6f) mount=%s weapon=%s qty=%s '
              'course=%d 点(含终点)'
              % (unit.Name, lat, lon, mount, weapon, qty, len(course)))
    assert len(bols) == 3, len(bols)

    # 锆石应从 #2 发出（#1 上没有这种弹，靠“自动换同型单元”兜底）
    pr = [b for b in bols if b[5] == 3361]
    assert pr and 'PR.2235.0护卫舰 #2' in pr[0][1].Name, pr

    # 伊斯坎德尔应打 SS-26（1235）：4 发 + 2 发两个目标点
    ss = [b for b in bols if b[5] == 1235]
    assert len(ss) == 2, ss
    assert sorted(b[6] for b in ss) == [2, 4], [b[6] for b in ss]
    assert sorted(round(b[2], 4) for b in ss) == [43.6577, 48.3130], \
        [b[2] for b in ss]

    # 航迹点裁剪（平台单条指令 300 字符）：用当年沙赫德那条 7 点指令复核
    pts = [(50.911593, 2.081675), (51.102344, 2.854912),
           (50.758936, 2.212539), (51.046481, 3.210333),
           (50.730516, 2.510804), (50.858603, 3.101413),
           (51.224247, 2.971228)]
    assert R.Agent._bol_cmd_len('H5-00001JS5TRO73', 3792, 4142, 10,
                                51.224247, 2.971228, pts) == 409
    fit, dropped = a._fit_bol_course('H5-00001JS5TRO73', 3792, 4142, 10,
                                     51.224247, 2.971228, pts)
    assert len(fit) == 4 and len(dropped) == 3, (fit, dropped)
    assert fit[-1] == pts[-1], '目标点必须保留在末尾'

    # 所有下发成功的指令都必须 ≤300 字符
    assert all(e[2] <= 300 for e in EVENTS if e[0] == 'bol_try'), \
        [e for e in EVENTS if e[0] == 'bol_try']

    # 逐项确认“已发射”（弹药确实减少）
    done = [i for i, st in a._bol_state.items() if st.get('fired')]
    print('BOL confirmed    :', len(done), '/', len(a.BOL_STRIKES))
    assert len(done) == 3, done

    # 舰船航线
    plots = [e for e in EVENTS if e[0] == 'unit' and e[1] == 'plotted_course']
    print('ship plots       :', len(plots))

    # 条令
    side_calls = [e for e in EVENTS if e[0] == 'side']
    print('side doctrine/wra:', len(side_calls))

    # ---- 场景二：平台回“成功”但根本不扣弹（蓝方踩过的坑）----
    print('\n--- 场景二：平台回成功但不扣弹，应自动换策略并在 5 轮后放弃 ---')
    EVENTS.clear()
    FakeServer.AMMO_DECREMENT = False
    a2 = AgentProxy(build_situation()[0])
    a2.initial(build_situation())
    for i in range(16):
        a2.step(i * 30, build_situation())
    n_bol2 = len([e for e in EVENTS if e[0] == 'bol'])
    n_unit_bol2 = len([e for e in EVENTS
                       if e[0] == 'unit' and e[1] == 'attack_BOL'])
    giveup = [i for i, st in a2._bol_state.items() if st.get('fired')]
    print('BOL calls(场景二) :', n_bol2 + n_unit_bol2,
          '(底层 %d + 封装 %d)  放弃项: %d' % (n_bol2, n_unit_bol2, len(giveup)))
    # 5 种策略 × 3 项 = 15 次下发，之后标记放弃，不会无限重试
    assert n_bol2 + n_unit_bol2 == 3 * len(a2.BOL_STRATEGIES), n_bol2 + n_unit_bol2
    assert len(giveup) == 3, giveup
    FakeServer.AMMO_DECREMENT = True

    # ---- 场景三：想定里的单元名没有 #舷号，应走“唯一候选”兜底 ----
    print('\n--- 场景三：地面发射车名没有 #舷号，应走唯一候选兜底 ---')
    EVENTS.clear()
    units3 = dict(build_situation()[0])
    for guid in ('g088', 'g089'):      # 伊斯坎德尔、沙赫德各只有一辆
        units3[guid] = dict(units3[guid])
        units3[guid]['name'] = re.sub(r'\s*#\s*\d+\s*$', '', units3[guid]['name'])
    a3 = AgentProxy(units3)
    a3.initial((units3, {}))
    a3.step(0, (units3, {}))
    a3.step(30, (units3, {}))
    a3.step(60, (units3, {}))
    n_bol3 = len([e for e in EVENTS if e[0] == 'bol'])
    print('BOL calls(场景三) :', n_bol3)
    assert n_bol3 == 3, n_bol3
    assert len([i for i, st in a3._bol_state.items() if st.get('fired')]) == 3

    # ---- 场景四：23900 到终点后应停车，不再补发航线 ----
    print('\n--- 场景四：舰船到终点后停车（不再重走航线）---')
    EVENTS.clear()
    sit4 = build_situation()
    g4 = [k for k, v in sit4[0].items() if '23900' in v['name']][0]
    sit4[0][g4] = dict(sit4[0][g4])
    sit4[0][g4]['Lat'] = 49.638315          # 正好在航线终点
    sit4[0][g4]['Lon'] = -0.997032
    a4 = AgentProxy(sit4[0])
    a4.initial(sit4)
    u4 = a4._units[g4]
    u4._course = []                          # 模拟航路已走完
    ev0 = len(EVENTS)
    a4.step(0, sit4)
    new = EVENTS[ev0:]
    stops = [e for e in new if e[1] == 'set_desired_speed' and e[2][1] == 0]
    replot = [e for e in new if e[1] == 'plotted_course'
              and e[2][0] == u4.Name]
    print('停车指令:', len(stops), ' 重发航线:', len(replot))
    assert stops, '到终点后没有把速度设为 0'
    assert not replot, '到终点后仍在补发航线'
    # 再走一个周期也不应重发
    ev1 = len(EVENTS)
    a4.step(30, sit4)
    assert not [e for e in EVENTS[ev1:] if e[1] == 'plotted_course'
                and e[2][0] == u4.Name], '停车后又被补发航线'

    print('\n全部断言通过')


if __name__ == '__main__':
    main()

