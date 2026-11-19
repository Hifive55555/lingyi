# -*- coding: utf-8 -*-
"""
离线自测：用假的 entitys.player / agent_base 驱动 Mission_tactics_red.Agent，
逐条验证 Monitor / Evade / AirCombat / 边界守卫 / 禁航区 五个行为。

运行： python tools/selftest_tactics_red.py
"""
import math
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

EVENTS = []


class Reply(object):
    def __init__(self, code=0, result=b'{}'):
        self.code = code
        self.result = result


class FakeUnit(object):
    """飞机/舰船/设施的假对象。"""

    def __init__(self, guid, name, lat, lon, alt=8000.0, spd=900.0, hdg=0.0):
        self.ID = guid
        self.Name = name
        self.Lat = lat
        self.Lon = lon
        self.CurrentAltitude = alt
        self.CurrentSpeed = spd
        self.CurrentHeading = hdg
        self.AssignedMission = ''
        self.Mounts = {}
        self._course = []
        self._air = True

    # ---- 飞机状态 ----
    def get_status_type(self):
        if not self._air:
            raise AttributeError('not an aircraft')
        from entitys.global_util import AirValidStatus
        return AirValidStatus.InAir

    # ---- 指令 ----
    def _rec(self, name, *a):
        EVENTS.append((name, self.Name, a))
        return Reply(0)

    def plotted_course(self, pts):
        self._course = list(pts)
        return self._rec('plotted_course', pts)

    def clear_plotted_course(self):
        self._course = []
        return self._rec('clear_plotted_course')

    def set_throttle(self, thr):
        return self._rec('set_throttle', getattr(thr, 'name', thr))

    def set_desired_height(self, h):
        return self._rec('set_desired_height', h)

    def withdraw_from_mission(self):
        self.AssignedMission = ''
        return self._rec('withdraw_from_mission')

    def assign_to_mission(self, name):
        self.AssignedMission = name
        return self._rec('assign_to_mission', name)

    def attack_drop_target_all(self):
        return self._rec('attack_drop_target_all')

    def attack_weapon_allocate_to_target(self, cid, wid, qty, weapon_course=[]):
        return self._rec('attack', cid, wid, qty)

    def get_way_points_info(self):
        return list(self._course)


class FakePlayer(object):
    Name = '红方'

    def __init__(self, side_name='红方'):
        self.Name = side_name
        self.log = None
        self._game_server = None
        self._units = {}
        self.aircrafts = {}
        self.ships = {}
        self.submarines = {}
        self.facilitys = {}
        self.satellites = {}
        self.weapons = {}
        self.groups = {}
        self.missions_obj = {}

    def get_unit(self, guid):
        return self._units.get(guid)

    def agent_message_text(self, text):
        EVENTS.append(('msg', text, ()))
        return Reply(0)


agent_base = types.ModuleType('entitys.agent_base')
agent_base.RuleAgentBase = type('RuleAgentBase', (FakePlayer,), {})
sys.modules['entitys.agent_base'] = agent_base

player_mod = types.ModuleType('entitys.player')
player_mod.Player = FakePlayer
sys.modules['entitys.player'] = player_mod

import entitys  # noqa: E402
entitys.agent_base = agent_base
entitys.player = player_mod

import Mission_tactics_red as T  # noqa: E402


class AgentProxy(T.Agent):
    def __init__(self, units, missions=None):
        T.Agent.__init__(self, '红方', None)
        for u in units:
            self._units[u.ID] = u
        if missions:
            self.missions_obj = missions


class FakeMission(object):
    def __init__(self, name, mid):
        self.Name = name
        self.ID = mid


def _situation(units, contacts=None):
    d = {}
    for u in units:
        cat = 'Aircraft' if u._air else 'Ship'
        d[u.ID] = {'guid': u.ID, 'name': u.Name, 'category': cat, 'dbid': 1,
                   'Lat': u.Lat, 'Lon': u.Lon}
    return (d, contacts or {})


def _missile(lat, lon, spd, hdg, name='AGM-84', dbid=596):
    return {'name': name, 'Type': 1, 'DBID': dbid, 'CurrentSpeed': spd,
            'CurrentHeading': hdg, 'Lat': lat, 'Lon': lon,
            'CurrentAltitude': 30}


def _enemy_air(lat, lon, spd, hdg, alt=8000, name='敌机#1'):
    return {'name': name, 'Type': 0, 'DBID': 1000, 'CurrentSpeed': spd,
            'CurrentHeading': hdg, 'Lat': lat, 'Lon': lon,
            'CurrentAltitude': alt}


def _events(kind, name=None):
    return [e for e in EVENTS if e[0] == kind and (name is None or e[1] == name)]


def _km(a, b):
    dn = (a[0] - b[0]) * 111.32
    de = (a[1] - b[1]) * 111.32 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dn, de)


def main():
    ev = '右制空'
    areas = T.Agent.MISSION_AREAS
    lat0, lon0, rad = areas[ev]
    mis = FakeMission(ev, 'M-1')

    # ---------------------------------------------------------------- 1. 监控
    print('--- 1. Monitor：敌弹指向本机 ---')
    AC = FakeUnit('a1', '苏-35S #1', lat0, lon0, alt=8000, spd=900, hdg=0)
    AC.AssignedMission = 'M-1'
    AC.Mounts = {'m1': {'Component': {'DBID': 9001}, 'WeaponRecs': {
        'w1': {'WeaponDBID': 2056, 'CurrentLoad': 6, 'AirRangeMax': 60}}}}
    # 弹在本机正南 60 km、朝北 3000 km/h
    m_lat = lat0 - 60.0 / 111.32
    contacts = {'c1': _missile(m_lat, lon0, 3000.0, 0.0)}
    a = AgentProxy([AC], {ev: mis})
    a._now = 0.0
    th = a.monitor(_situation([AC], contacts))
    assert 'a1' in th, th
    t = th['a1']
    print('   命中：弹速%.0f 距离%.1fkm CPA%.1fkm tgo=%.0fs'
          % (t['mspeed'], t['dist'], t['cpa'], t['tgo']))
    assert t['mspeed'] == 3000.0
    assert abs(t['dist'] - 60.0) < 1.5, t['dist']
    assert t['cpa'] < 1.0, t['cpa']
    # 相对接近速度 = 3000 - 900 = 2100 km/h → 60km / 2100 ≈ 103 s
    assert 90 < t['tgo'] < 115, t['tgo']

    # ---------------------------------------------------------------- 2. 规避
    print('--- 2. Evade：正横机动（弹速 3000，d0 门限）---')
    EVENTS.clear()
    # 弹进到 45 km（≤ 门限）才会真的动
    close = {'c1': _missile(lat0 - 45.0 / 111.32, lon0, 3000.0, 0.0)}
    a.step(0, _situation([AC], close))
    assert _events('withdraw_from_mission', AC.Name), EVENTS
    assert _events('plotted_course', AC.Name), EVENTS
    assert _events('set_throttle', AC.Name), EVENTS
    dest = _events('plotted_course', AC.Name)[-1][2][0][0]
    away = _km((AC.Lat, AC.Lon), dest)
    brg = T._bearing((AC.Lat, AC.Lon), dest)
    off = abs((brg - 0.0 + 540.0) % 360.0 - 180.0)   # 与弹航向(正北 0°)的夹角
    print('   规避点距本机 %.1f km，航向 %.0f°（与弹航向夹角 %.0f°）'
          % (away, brg, off))
    assert 40 < away < 50, away
    assert 80 < off < 100, off          # 正横：应当接近 90°
    assert AC.AssignedMission == '', '规避时应已退出任务'

    # ------------------------------------------------- 3. 弹速降到 500 以下 → 回任务
    print('--- 3. Evade 结束：弹速 400 < 500 → 回原任务 ---')
    EVENTS.clear()
    slow = {'c1': _missile(m_lat, lon0, 400.0, 0.0)}
    a.step(30, _situation([AC], slow))
    back = _events('assign_to_mission', AC.Name)
    print('   回任务指令：', back)
    assert back and back[-1][2][0] == ev, back
    assert AC.AssignedMission == ev

    # ---------------------------------------------------------------- 4. 空战
    print('--- 4. AirCombat：30km 同高度 → 开火 ---')
    EVENTS.clear()
    AC2 = FakeUnit('a2', '苏-35S #2', lat0, lon0, alt=8000, spd=900, hdg=90)
    AC2.AssignedMission = 'M-1'
    AC2.Mounts = {'m1': {'Component': {'DBID': 9001}, 'WeaponRecs': {
        'w1': {'WeaponDBID': 2056, 'CurrentLoad': 6, 'AirRangeMax': 60}}}}
    # 敌机在本机正东 30 km，同高度，速度 900
    e_lat, e_lon = lat0, lon0 + 30.0 / (111.32 * math.cos(math.radians(lat0)))
    air_contacts = {'e1': _enemy_air(e_lat, e_lon, 900.0, 270.0)}
    b = AgentProxy([AC2], {ev: mis})
    b.step(0, _situation([AC2], air_contacts))
    shots = _events('attack', AC2.Name)
    print('   开火指令：', shots)
    assert shots, EVENTS
    _k, _n, args = shots[-1]
    assert args[1] == 2056 and args[2] >= 1, args
    # d0 自检：V0=4000, Va=900 → 91.6 km，0.8d0=73.3 km
    d0 = b.d0_km(4000.0, 900.0)
    print('   d0=%.1fkm  0.8d0=%.1fkm（距离 30km 在包线内）' % (d0, 0.8 * d0))
    assert 88 < d0 < 95, d0

    # ------------------------------------------------------- 5. 高度比越界不开火
    print('--- 5. AirCombat：高度比 0.5（过低）→ 不开火 ---')
    EVENTS.clear()
    low_contacts = {'e1': _enemy_air(e_lat, e_lon, 900.0, 270.0, alt=4000)}
    b.step(30, _situation([AC2], low_contacts))
    assert not _events('attack', AC2.Name), _events('attack', AC2.Name)

    # ------------------------------------------------------------ 6. 边界守卫
    print('--- 6. 边界守卫：飞出任务区 2.6° → 放弃目标 + 回飞 ---')
    EVENTS.clear()
    AC3 = FakeUnit('a3', '苏-35S #3', lat0 + 2.6, lon0, alt=8000, spd=900, hdg=0)
    AC3.AssignedMission = 'M-1'
    c = AgentProxy([AC3], {ev: mis})
    c.step(0, _situation([AC3], {}))
    assert _events('attack_drop_target_all', AC3.Name), EVENTS
    pts = _events('plotted_course', AC3.Name)
    assert pts, EVENTS
    inside = pts[-1][2][0][0]
    print('   回飞点：%.3f,%.3f  距中心 %.1fkm（半径 %.1f）'
          % (inside[0], inside[1], _km(inside, (lat0, lon0)), rad))
    assert _km(inside, (lat0, lon0)) < rad, '回飞点仍在区外'

    # --------------------------------------------------------------- 7. 禁航区
    print('--- 7. 禁航区：候选点在多边形内 → 自动外移 ---')
    d = AgentProxy([AC], {ev: mis})
    poly = [(lat0 - 0.5, lon0 - 0.5), (lat0 + 0.5, lon0 - 0.5),
            (lat0 + 0.5, lon0 + 0.5), (lat0 - 0.5, lon0 + 0.5)]
    d.NO_FLY_ZONES = (('测试禁航区', poly),)
    frm = (lat0 - 2.0, lon0)          # 区外
    to = (lat0, lon0)                 # 区内
    safe = d._safe_point(frm, to)
    print('   安全点：%.3f,%.3f  在禁航区内？%s'
          % (safe[0], safe[1], T._point_in_poly(safe, poly)))
    assert not T._point_in_poly(safe, poly), safe

    # ---------------------------------------- 8. 规避中“任务区”不能被基地顶替
    print('--- 8. 规避中仍按原任务区判边界（不能回落成基地）---')
    EVENTS.clear()
    AC4 = FakeUnit('a4', '苏-35S #4', lat0 + 0.3, lon0, alt=8000, spd=900,
                   hdg=0)
    AC4.AssignedMission = 'M-1'
    AC4.Mounts = {'m1': {'Component': {'DBID': 9001}, 'WeaponRecs': {
        'w1': {'WeaponDBID': 2056, 'CurrentLoad': 6, 'AirRangeMax': 60}}}}
    e = AgentProxy([AC4], {ev: mis})
    # 人为把“家”设到很远的基地，模拟飞机已经离开基地进入任务区
    e._home['a4'] = (lat0 - 3.0, lon0)
    close4 = {'c4': _missile(lat0 + 0.3 - 40.0 / 111.32, lon0, 3000.0, 0.0)}
    e.step(0, _situation([AC4], close4))
    assert _events('withdraw_from_mission', AC4.Name), EVENTS
    # 退任务后仍应识别为在「右制空」里 → 边界守卫不应该判它出界
    out = e._outside_km('a4', AC4, (lat0 + 0.3, lon0))
    n_bound = e.boundary_guard(_situation([AC4], close4))
    print('   退任务后距任务区边界：%.1f km，边界守卫纠正 %d 架（都应为 0）'
          % (out, n_bound))
    assert out == 0.0, out
    assert n_bound == 0, n_bound

    # ------------------------------------------------- 9. 消息栏（操作手看的）
    print('--- 9. 消息栏：被锁定/规避/开火要有提示 ---')
    msgs = [e2[1] for e2 in EVENTS if e2[0] == 'msg']
    for m in msgs:
        print('   MSG:', m)
    assert any('被锁定' in m for m in msgs), msgs
    assert any('规避' in m for m in msgs), msgs
    EVENTS.clear()
    b.step(60, _situation([AC2], air_contacts))
    assert any(e2[0] == 'msg' and '开火' in e2[1] for e2 in EVENTS), EVENTS

    # ------------------------------------------- 10. 机炮不能被当成空战弹
    print('--- 10. 只有机炮(1796)的飞机 → 无空战弹 ---')
    AC5 = FakeUnit('a5', '苏-27SM #1', lat0, lon0, alt=8000, spd=900, hdg=90)
    AC5.AssignedMission = 'M-1'
    AC5.Mounts = {'m1': {'Component': {'DBID': 9001}, 'WeaponRecs': {
        'g1': {'WeaponDBID': 1796, 'CurrentLoad': 150, 'AirRangeMax': 1.0}}}}
    f = AgentProxy([AC5], {ev: mis})
    print('   选中的空战弹：', f._best_aam(AC5))
    assert f._best_aam(AC5) is None

    # --------------------------------- 11. 短程弹不能按 d0 跑到 40 km 外开火
    print('--- 11. R-73(10nm) 对 40km 处目标 → 不开火；12km → 开火 ---')
    AC5.Mounts = {'m1': {'Component': {'DBID': 9001}, 'WeaponRecs': {
        'g1': {'WeaponDBID': 1896, 'CurrentLoad': 4, 'AirRangeMax': 10.0}}}}
    print('   选中：', f._best_aam(AC5))
    e_lon40 = lon0 + 40.0 / (111.32 * math.cos(math.radians(lat0)))
    e_lon12 = lon0 + 12.0 / (111.32 * math.cos(math.radians(lat0)))
    EVENTS.clear()
    f.step(120, _situation([AC5], {'e40': _enemy_air(lat0, e_lon40, 900.0, 270.0)}))
    assert not _events('attack', AC5.Name), '40km 不该开火'
    f.step(150, _situation([AC5], {'e12': _enemy_air(lat0, e_lon12, 900.0, 270.0)}))
    shots = _events('attack', AC5.Name)
    print('   12km 开火：', shots)
    assert shots, EVENTS

    # ------------------ 12. 慢速弹（d0 会算很小）仍要按“剩余时间”触发规避
    print('--- 12. 弹只剩 1143km/h、距离 13.5km → 仍要规避 ---')
    EVENTS.clear()
    AC6 = FakeUnit('a6', '苏-27SM #6', lat0, lon0, alt=8000, spd=900, hdg=0)
    AC6.AssignedMission = 'M-1'
    g = AgentProxy([AC6], {ev: mis})
    # 先让它见过这枚弹的“高速状态”，再降速
    fast = {'m1': _missile(lat0 - 60.0 / 111.32, lon0, 2058.0, 0.0)}
    g.monitor(_situation([AC6], fast))
    slow = {'m1': _missile(lat0 - 13.5 / 111.32, lon0, 1143.0, 0.0)}
    g.step(30, _situation([AC6], slow))
    turns = _events('plotted_course', AC6.Name)
    print('   规避指令：', turns[-1][2] if turns else None)
    assert turns, EVENTS

    print('\n全部断言通过')

if __name__ == '__main__':
    main()
