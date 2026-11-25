# -*- coding: utf-8 -*-
"""
蓝方（人人版）离线自测：用假的 entitys.player / agent_base 驱动
Mission_all_blue_hh.Agent，检查任务、挂载、条令、机动是否按预期下发。

运行： python tools/selftest_blue_hh.py
"""
import ast
import io
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


from _agentpath import ensure as _ensure

_AGENT_DIR = _ensure('Mission_all_blue_hh.py', ROOT)
if _AGENT_DIR and _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)


EVENTS = []
LOADOUTS = {}
ASSIGNED = {}
MISSIONS = {}


class Reply(object):
    def __init__(self, code=0):
        self.code = code
        self.result = b'{}'


class Recorder(object):
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

    def mission_active(self, is_active):
        EVENTS.append(('mission_active', self.Name, is_active, {}))
        return Reply(0)


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
        self.AssignedMission = ''      # 已分配任务的 guid，空表示未分配
        self._course = []

    def get_way_points_info(self):
        return list(self._course)

    def plotted_course(self, course_list):
        self._course = list(course_list)
        EVENTS.append(('unit', 'plotted_course', (self.Name, course_list), {}))
        return Reply(0)

    def clear_plotted_course(self):
        self._course = []
        return Reply(0)

    def set_throttle(self, thr):
        EVENTS.append(('unit', 'set_throttle', (self.Name, thr), {}))
        return Reply(0)

    def set_desired_speed(self, spd):
        EVENTS.append(('unit', 'set_desired_speed', (self.Name, spd), {}))
        return Reply(0)

    def set_depth(self, depth):
        EVENTS.append(('depth', self.Name, depth))
        return Reply(0)


class FakeServer(object):
    def __init__(self):
        self.created = []

    def __getattr__(self, item):
        def fn(*a, **k):
            if item == 'api_create_support_mission':
                m = FakeMission(a[1], 'support')
                MISSIONS[a[1]] = 'support'
                EVENTS.append(('create', a[1], a[2], {}))
                return m
            if item == 'api_create_patrol_mission':
                m = FakeMission(a[1], 'patrol')
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
                cmd_len = B.Agent._bol_cmd_len(unit.ID, mount, weapon, qty,
                                               lat, lon, pts)
                EVENTS.append(('bol_try', unit, cmd_len, len(pts)))
                if cmd_len > 300:
                    return Reply(-1)
                _consume(unit, weapon, qty)
                EVENTS.append(('bol', unit, weapon, qty, course))
                return Reply(0)
            if item == 'api_set_depth':
                EVENTS.append(('depth', a[0].Name, a[1]))
                return Reply(0)
            EVENTS.append(('api', item, a, k))
            return Reply(0)
        return fn


def _consume(unit, weapon, qty):
    """模拟平台扣弹。"""
    for attr in ('Mounts', 'Magazines'):
        for mv in (getattr(unit, attr, {}) or {}).values():
            for rec in ((mv.get('WeaponRecs') or {}).values()
                        if isinstance(mv, dict) else []):
                if rec.get('WeaponDBID') == weapon:
                    rec['CurrentLoad'] = max(0, int(rec.get('CurrentLoad', 0)) - qty)


class FakePlayer(object):
    Name = '蓝方'

    def __init__(self, side_name):
        self.Name = side_name
        self.log = None
        self._game_server = FakeServer()
        self.units_of_name = {}
        self.aircrafts = {}
        self.ships = {}
        self.submarines = {}
        self.facilitys = {}
        self.satellites = {}
        self.weapons = {}
        self.groups = {}
        self._units = {}

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
        if item.startswith('_'):
            raise AttributeError(item)

        def fn(*a, **k):
            EVENTS.append(('side', item, a, k))
            return Reply(0)
        return fn


agent_base = types.ModuleType('entitys.agent_base')
agent_base.RuleAgentBase = type('RuleAgentBase', (FakePlayer,), {})
sys.modules['entitys.agent_base'] = agent_base
player_mod = types.ModuleType('entitys.player')
player_mod.Player = FakePlayer
sys.modules['entitys.player'] = player_mod
import entitys  # noqa: E402
entitys.agent_base = agent_base
entitys.player = player_mod

import Mission_all_blue_hh as B  # noqa: E402

# (名称, 类别, DBID) —— 名称与 DBID 取自实盘态势快照
UNITS = [
    ('F/A-18F型 战斗机 #1', 'Aircraft', 965),
    ('F/A-18F型 战斗机 #2', 'Aircraft', 965),
    ('F/A-18F型 战斗机 #3', 'Aircraft', 965),
    ('F/A-18F型 战斗机 #4', 'Aircraft', 965),
    ('F/A-18F型 战斗机 #5', 'Aircraft', 965),
    ('F/A-18F型 战斗机 #6', 'Aircraft', 965),
    ('F-35C 型“闪电II” 战斗机 #1', 'Aircraft', 4874),
    ('F-35C 型“闪电II” 战斗机 #2', 'Aircraft', 4874),
    ('F-35B型“闪电II” 战斗机 #1', 'Aircraft', 5134),
    ('F-35B型“闪电II” 战斗机 #2', 'Aircraft', 5134),
    ('F-35A型 战斗机 #1', 'Aircraft', 4876),
    ('F-35A型 战斗机 #2', 'Aircraft', 4876),
    ('E-2D型“先进鹰眼”舰载预警机 #1', 'Aircraft', 4293),
    ('MQ-25A型 无人加油机 #1', 'Aircraft', 4917),
    ('MQ-25A型 无人加油机 #2', 'Aircraft', 4917),
    ('EA-18G “咆哮者”电子战飞机 #1', 'Aircraft', 4879),
    ('EA-18G “咆哮者”电子战飞机 #2', 'Aircraft', 4879),
    ('B-2A 轰炸机 #1', 'Aircraft', 4881),
    ('B-2A 轰炸机 #2', 'Aircraft', 4881),
    ('F-15E型 战斗机 #1', 'Aircraft', 4973),
    ('F-15E型 战斗机 #2', 'Aircraft', 4973),
    ('F-15E型 战斗机 #3', 'Aircraft', 4291),
    ('F-15E型 战斗机 #4', 'Aircraft', 4291),
    ('幻影-2000-5EI战斗机 #1', 'Aircraft', 175),
    ('幻影-2000-5EI战斗机 #2', 'Aircraft', 175),
    ('幻影-2000-5EI战斗机 #3', 'Aircraft', 175),
    ('幻影-2000-5EI战斗机 #4', 'Aircraft', 175),
    ('F-16V型 BLK 70/72 “战隼”战斗机 #1', 'Aircraft', 4912),
    ('F-16V型 BLK 70/72 “战隼”战斗机 #2', 'Aircraft', 4912),
    ('F-16V型 BLK 70/72 “战隼”战斗机 #3', 'Aircraft', 4912),
    ('F-16V型 BLK 70/72 “战隼”战斗机 #4', 'Aircraft', 4912),
    ('F-16B 战隼20 战斗机 #1', 'Aircraft', 3421),
    ('F-16B 战隼20 战斗机 #2', 'Aircraft', 3421),
    ('F-2A型战斗机  #1', 'Aircraft', 5321),
    ('F-2A型战斗机  #2', 'Aircraft', 5321),
    ('F-2A型战斗机  #3', 'Aircraft', 5321),
    ('F-2B型战斗机 #1', 'Aircraft', 3378),
    ('F-2B型战斗机 #2', 'Aircraft', 3378),
    ('MQ-1C  无人机 #1', 'Aircraft', 4794),
    ('MQ-1C  无人机 #2', 'Aircraft', 4794),
    ('MQ-1C  无人机 #3', 'Aircraft', 4794),
    ('MQ-1C  无人机 #4', 'Aircraft', 4794),
    ('RQ-4B型”全球鹰“无人机 #1', 'Aircraft', 2848),
    ('MH-60R 反潜直升机 #1', 'Aircraft', 5037),
    ('MH-60R 反潜直升机 #2', 'Aircraft', 5037),
    ('SSN 792“佛蒙特”号弗吉尼亚级核动力隐形潜艇', 'Submarine', 553),
    ('CG-52 “邦克山”提康德罗加级号巡洋舰', 'Ship', 2859),
    ('“阿利伯克”级导弹驱逐舰', 'Ship', 2867),
    ('DDG 179 摩耶级驱逐舰', 'Ship', 3211),
    ('DDH 183 IZUMO直升驱逐舰 [22DDH CLASS]', 'Ship', 3619),
    ('CS机场', 'AirBase', 1996),
    ('奥尔良机场', 'AirBase', 430),
    ('C-5M型 运输机#1', 'Aircraft', 1931),
    ('C-5M型 运输机#2', 'Aircraft', 1931),
    ('装甲车#1', 'Facility', 2983),
    ('装甲车#2', 'Facility', 2983),
    ('装甲车#3', 'Facility', 2983),
    ('装甲车#4', 'Facility', 2983),
    ('装甲车#5', 'Facility', 2983),
]


def build_situation():
    units = {}
    for i, (name, cat, dbid) in enumerate(UNITS):
        guid = 'b%03d' % i
        units[guid] = {'guid': guid, 'name': name, 'category': cat, 'dbid': dbid}
    return (units, {})


class AgentProxy(B.Agent):
    def __init__(self, units):
        B.Agent.__init__(self, '蓝方', None)
        for guid, d in units.items():
            self._units[guid] = FakeUnit(guid, d['name'], d['category'], d['dbid'])
        # 佛蒙特：UGM-109E 两种 DBID 各 6 发；阿利伯克：RGM-109I 8 发
        for u in self._units.values():
            if '佛蒙特' in u.Name:
                u.Mounts = {'m1': {'Component': {'DBID': 9001}, 'WeaponRecs': {
                    'w1': {'WeaponDBID': 377, 'CurrentLoad': 6},
                    'w2': {'WeaponDBID': 810, 'CurrentLoad': 6}}}}
            elif '阿利伯克' in u.Name:
                u.Mounts = {'m2': {'Component': {'DBID': 9002}, 'WeaponRecs': {
                    'w1': {'WeaponDBID': 2941, 'CurrentLoad': 8}}}}


def main():
    sit = build_situation()
    a = AgentProxy(sit[0])
    a.initial(sit)
    a.step(0, sit)
    a.step(30, sit)
    a.step(60, sit)

    n_sup = len([n for n, k in MISSIONS.items() if k == 'support'])
    n_pat = len([n for n, k in MISSIONS.items() if k == 'patrol'])
    print('support missions :', n_sup)
    print('patrol missions  :', n_pat)
    # 2026-11-25 合并对面（决赛）版本：新增「北船机动」→ 32 条
    assert n_sup == 32, n_sup          # 30 + 运输机逃跑 + 北船机动
    assert n_pat == 3, n_pat

    # 运输机逃跑：C-5M #1#2
    assert len(ASSIGNED.get('运输机逃跑', [])) == 2, ASSIGNED.get('运输机逃跑')

    # 对面（决赛）版本：AAAAAAAA/BBBBBBBBB/CCCCCCCC 不再是“只建任务”，
    #   改为装甲车 / 伪装防空车 / 反舰导弹排“战前 M 到位 → 再分配”（见 PREWAR_MOVES）
    for n, kw in (('AAAAAAAA', ('装甲车', 'Armored', 'LAV')),
                  ('BBBBBBBBB', ('装甲车', 'Armored', 'LAV', '反舰导弹排', '伪装防空车')),
                  ('CCCCCCCC', ('装甲车', 'Armored', 'LAV'))):
        units = [a._units[g].Name for g in ASSIGNED.get(n, [])]
        print('%s units :' % n, units)
        assert units, '%s 没有分配到单元' % n
        assert any(k in u for u in units for k in kw), units

    # 只剩这 3 条按要求不分配单元
    NO_UNIT = ('左左左左左左', '中中中中中中', '右右右右右右')
    empty = [n for n in MISSIONS if n not in NO_UNIT and not ASSIGNED.get(n)]
    assert not empty, '这些任务没有分配到单元: %s' % empty
    for n in NO_UNIT:
        assert n in MISSIONS, n
        assert not ASSIGNED.get(n), n

    # 北2B ← F-2B#1#2（2 架）；北2A ← F-2A#1#2#3（3 架）
    assert len(ASSIGNED.get('北2B', [])) == 2, ASSIGNED.get('北2B')
    assert len(ASSIGNED.get('北2A', [])) == 3, ASSIGNED.get('北2A')

    # 开局不启动的 4 个任务
    inactive = {e[1] for e in EVENTS
                if e[0] == 'mission_active' and e[2] is False}
    print('inactive missions:', sorted(inactive))
    assert inactive == {'F18-456', '北2B', '北2A', '无人机送死'}, inactive

    # 三条巡逻任务都下发“对地/对海/对潜自由开火”（2+4+1=7 个单元）
    for fn in ('doctrine_weapon_control_status_land',
               'doctrine_weapon_control_status_surface',
               'doctrine_weapon_control_status_subsurface'):
        n = len([e for e in EVENTS if e[0] == 'unit' and e[1] == fn])
        print('%-46s %d' % (fn, n))
        assert n == 7, (fn, n)

    print('patrol assignments:')
    for n in ('反潜', '无人机送死', '打航母'):
        print('   %-6s <- %s' % (n, [a._units[g].Name for g in ASSIGNED.get(n, [])]))
    assert len(ASSIGNED['反潜']) == 2
    assert len(ASSIGNED['无人机送死']) == 4
    assert len(ASSIGNED['打航母']) == 1, '佛蒙特号应已分配到打航母'

    # 战斧 BOL：已按要求取消（BOL_STRIKES 为空）
    bols = [e for e in EVENTS if e[0] == 'bol']
    print('BOL calls        :', len(bols))
    assert len(bols) == 0, len(bols)
    assert not a.BOL_STRIKES, a.BOL_STRIKES
    # 潜艇深度仍设为 0 米
    depths = [e for e in EVENTS if e[0] == 'depth']
    print('sub depth        :', depths)
    assert depths and depths[0][2] == 40, depths   # 界面 -40 米 = 水下 40 米

    print('loadouts set     :', len(LOADOUTS))
    for guid, lid in sorted(LOADOUTS.items()):
        print('   %-42s -> %s' % (a._units[guid].Name, lid))
    assert len(LOADOUTS) == 45, len(LOADOUTS)

    # 三舰对空限制开火
    holds = [e for e in EVENTS if e[0] == 'unit'
             and e[1] == 'doctrine_weapon_control_status_air'
             and e[2] and getattr(e[2][0], 'value', None) == 2]
    print('ship air-hold    :', len(holds))
    assert len(holds) == 3, holds

    # 对面（决赛）版本：删掉了 SHIP_RUSH / GROUND_MOVES 两段“开局自己下航线”，
    #   改成 ①「北船机动」任务（摩耶 + 直升机驱逐舰，见 SHIP_THROTTLE_TASKS）
    #        ② PREWAR_MOVES：装甲车/伪装防空车/防空营等“战前 M 到位”，
    #           再由 AAAAAAAA/BBBBBBBBB/CCCCCCCC 三条任务接管（REASSIGN_TASKS 归位后重分配）
    rush = [e for e in EVENTS if e[0] == 'unit' and e[1] == 'plotted_course']
    print('plotted_course   :', len(rush))
    assert not rush, rush          # 不再有开局自下航线

    moves = [e for e in EVENTS if e[1] == 'unit_new_position']
    print('prewar moves     :', len(moves))
    # PREWAR_MOVES 里 14 项；假想定只有装甲车/伪装防空车/爱国者/地空导弹连在册，
    # 霍克/捷羚/反舰导弹排/火箭炮匹配不到 → 实际下发 10 次
    assert len(moves) == 10, len(moves)

    def _dest(e):
        k = e[3] or {}
        return k.get('lon_lat') or k.get('long_lat')

    dests = [tuple(_dest(e)) for e in moves if _dest(e)]
    # 平台接口收 (经度, 纬度)
    assert (48.977815, -1.309595)[::-1] in dests, dests[:5]      # 装甲车#1
    assert (48.958002, 0.120440)[::-1] in dests, dests[:5]       # 装甲车#2
    assert (49.576326, 1.655070)[::-1] in dests, dests[:5]       # 装甲车#3
    assert (48.829125, -0.856644)[::-1] in dests, dests[:5]      # 装甲车#5

    # WRA：3 组武器（51/3608/3567/718）×（3 齐射 + 4 距离）
    wra = [e for e in EVENTS if e[0] == 'side'
           and e[1] in ('wra_qty_salvo', 'wra_firing_range')]
    print('side WRA calls   :', len(wra))
    assert len(wra) == 28, len(wra)

    # 静态检查：_log 参数个数
    src = io.open(os.path.join(_AGENT_DIR or ROOT, 'Mission_all_blue_hh.py'), encoding='utf-8').read()
    bad_log = [(n.lineno, len(n.args)) for n in ast.walk(ast.parse(src))
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == '_log' and len(n.args) != 2]
    assert not bad_log, bad_log

    # ---- 场景五：玩家按 U 后，智能体不再把装甲车抢回逃跑航路 ----
    print('\n--- 场景五：按 U 之后不再被抢回逃跑点 ---')
    EVENTS.clear()
    sit5 = build_situation()
    a5 = AgentProxy(sit5[0])
    a5.initial(sit5)
    EVENTS.clear()                        # 只统计“initial 之后”的下发
    g5 = [k for k, v in sit5[0].items() if v['name'] == '装甲车#3'][0]
    u5 = a5._units[g5]
    u5._course = []                       # 玩家按 U：航路被清掉
    u5.AssignedMission = 'M-玩家任务'      # 随后分配给别的任务
    for i in range(a5.GROUND_FALLBACK_CYCLES + 3):
        a5.step(i * 30, sit5)
    back = [e for e in EVENTS
            if e[1] == 'plotted_course' and e[2][0] == u5.Name]
    print('按U后被抢回次数:', len(back))
    assert not back, '玩家按 U 后智能体又把航路改回逃跑点了'

    # 再验证：即使没分配任务，过了开局窗口也不再补发
    EVENTS.clear()
    sit6 = build_situation()
    a6 = AgentProxy(sit6[0])
    a6.initial(sit6)
    EVENTS.clear()
    g6 = [k for k, v in sit6[0].items() if v['name'] == '装甲车#1'][0]
    u6 = a6._units[g6]
    for i in range(a6.GROUND_FALLBACK_CYCLES + 3):
        a6.step(i * 30, sit6)
    u6._course = []
    ev = len(EVENTS)
    a6.step(9999, sit6)
    again = [e for e in EVENTS[ev:]
             if e[1] == 'plotted_course' and e[2][0] == u6.Name]
    print('过窗口后补发次数:', len(again))
    assert not again, '过了开局窗口仍在补发逃跑航路'

    # ---- 场景六：按 U 之后要清掉残留航路 + 停车（海马斯那类）----
    print('\n--- 场景六：按 U 后清航路并停车 ---')
    EVENTS.clear()
    sit7 = build_situation()
    a7 = AgentProxy(sit7[0])
    a7.initial(sit7)
    EVENTS.clear()
    g7 = [k for k, v in sit7[0].items() if v['name'] == '装甲车#2'][0]
    u7 = a7._units[g7]
    u7.AssignedMission = 'M-右右右右右右'        # 先被分配到任务
    a7.step(0, sit7)                              # 记录状态
    u7.AssignedMission = ''                       # 玩家按 U
    u7._course = [(46.0, 0.5), (46.5, 1.0)]       # 残留的任务航路
    ev = len(EVENTS)
    a7.step(30, sit7)
    new = EVENTS[ev:]
    stopped = [e for e in new
               if e[1] == 'set_desired_speed' and e[2][0] == u7.Name and e[2][1] == 0]
    fullstop = [e for e in new if e[1] == 'set_throttle'
                and e[2][0] == u7.Name
                and getattr(e[2][1], 'name', '') == 'FullStop']
    replot = [e for e in new if e[1] == 'plotted_course' and e[2][0] == u7.Name]
    print('停车:', len(stopped), ' FullStop:', len(fullstop), ' 重画航线:', len(replot))
    assert stopped and fullstop, '按 U 后没有停车'
    assert not replot, '按 U 后又被补了逃跑航路'
    # 只处理一次：再过一周期不重复下发
    ev2 = len(EVENTS)
    a7.step(60, sit7)
    assert not [e for e in EVENTS[ev2:]
                if e[1] == 'set_desired_speed' and e[2][0] == u7.Name], '停车指令重复下发'

    print('\n全部断言通过')


if __name__ == '__main__':
    main()
