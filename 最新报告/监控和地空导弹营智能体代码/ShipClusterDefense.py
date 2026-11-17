# -*- coding:utf-8 -*-
r"""
登陆船只集群自卫智能体（Ship Cluster Defense）
================================================
规则型智能体，独立于主智能体之外的一个模块，主智能体每周期调用一次 ``step()``。

设计依据：设计报告 2.3.4 节「登陆船只集群自卫（Ship）」
------------------------------------------------------------------
本节的判定核心不是「弹型」，而是「**弹型 × 区域**」的笛卡尔积——同一个弹型在不
同区域的处置完全不同。三类威胁、两种杀伤方式（硬杀伤的舰空导弹、软杀伤的雷达
开关与航向机动）、外加跨平台召唤飞机：

    类别         ABDE 区处置                       C 区处置
    ─────────────────────────────────────────────────────────────────────
    ① 卢卡斯     雷鸣号在**弹距 < 3 km** 时自卫     雷鸣号**不打**；改由 23900
      无人机                                     船坞登陆舰的激光自由开火
    ② 海马斯 /  雷鸣号以最大射程 Dmax 开火        一号舰 Dmax 先拦，二号舰等
      反舰导弹排                                 弹突防到 **1/2 Dmax** 再补拦
    ③ 158C /    关雷达 + 双舰切向背身跑 + 加力；  同左
      154C       有弹则开雷达打，无弹则时开时关；
                 同时召唤苏-57 至船的上空，驱离为
                 导弹提供持续照射的敌机

三个判据的用途各不相同（报告 2.3.4.1 / 2.3.4.2）：

* **3 km** 判「骗弹还是真弹」。船在运动，弹的预定航线与船位偏差大，大于 3 km
  多半是欺骗弹，用舰空导弹去打不经济。
* **Dmax 与 1/2 Dmax** 判「谁先打」。两舰都在最大射程开火，会对同一枚弹同时
  打两发——报告表 19 的受控实验给出代价：分层方案拦截率 0.751，低于「双舰均
  在半射程开火」的 0.849，但平均拦截距离 43.3 km 比前者远 44%。**这是用约 10
  个百分点的拦截率换 13 km 的安全裕度**，不是「分层一定更优」。
* **第三类不用距离判据**。158C 要命中目标需要对方武器持续照射，负责照射的飞机
  雷达搜索范围有限，一旦被迫改变方向，照射链就断了。所以这一条把「防御」转化
  为「夺取局部制空权」——召唤苏-57 比多打几发弹更有效。

实现要点
--------
1. **区域不写死经纬度**，按舰船当前所属任务名判定（C1/C2 → C 区，其余 → ABDE
   区），任务名读不到时退化为「到 C 区中心 < ZONE_C_RADIUS_KM」的几何判定。
2. **Dmax 不写死**，运行期从舰船实际携带的对空导弹里查 ``AirRangeMax``
   （SA-N-21d / 3221 = 65 km），查不到才退回 FALLBACK_DMAX_KM。
3. **弹量先行**：开火前统计该型弹出膛数，为 0 就不进「有弹则开雷达打」分支，
   直接走软杀伤——报告第三类的两个分支就是这么分的。
4. **不重复开火**：同 (舰, 弹) 组合按 REENGAGE_CYCLES 节流，且优先用
   ``attack_weapon_allocate_to_target`` 指定弹种与齐射数（默认 2 发），
   避免 ``attack_auto`` 把弹舱一次性打空（表 19 的 B2 方案就是这样，弹耗/拦截
   高达 2.76，四方案最差）。
5. **切向背身之后要能回来**：敢改航路，就必须能在威胁解除后恢复。机动前用
   ``get_way_points_info()`` 快照原航路，威胁解除后回填，否则一圈跑完就再也
   回不到登陆编队。

与监控智能体的关系（报告 2.3.1）
--------------------------------
"有没有弹指向本方"这件事不由本模块判定，而是问 ``BattlefieldMonitor``——它是
报告里的唯一信息源，只回答「弹型 + 弹速」。本模块拿到这两个字段与情报 guid 后，
**自己重算弹目距离**（报告要求下游各算各的，避免依赖监控内部实现），再按
3 km / Dmax / 1/2 Dmax 这些判据处置。

没接监控时（``monitor=None``）本模块会退化为自己扫情报，方便离线测试；但正式
推演建议接上监控，否则"弹是否指向我"没有几何判定，只是按名称 + 当前距离筛，
会漏掉"现在很远、注定从头顶掠过"的弹。

接入方法（三步）
----------------
与本文件放在同一目录，或放在 ``engine/LingYi/`` 下（与 entitys 同级）::

    from engine.LingYi.BattlefieldMonitor import BattlefieldMonitor
    from engine.LingYi.ShipClusterDefense import ShipClusterDefense

    def __init__(self, side_name, params=None):
        ...
        self.monitor = BattlefieldMonitor(self)               # ① 监控（唯一信息源）
        self.ship_defense = ShipClusterDefense(self, self.monitor)   # ② 构造

    def initial(self, situation):
        ...
        self.monitor.setup(situation)
        self.ship_defense.setup(situation)                     # ③ 开局解析舰队与能力

    def step(self, time_elapse, situation):
        ...
        self.monitor.ensure(situation)                         # 本周期态势只算一次
        self.ship_defense.step(situation)                      # 每周期决策

也可以不用 import，把本文件的类整体粘进主智能体文件末尾（本文件只依赖 math/re/
logging，不 import entitys，枚举通过宿主模块惰性取，粘进去即可用）。

可调参数都在类属性里，改一个词即可回退，例如：

* ``ENABLE = False``            整体关掉；
* ``LAYERED = False``           C 区第二类改成与 ABDE 一致（都在 Dmax 开火）；
* ``LUCAS_C_FIRE = True``       C 区卢卡斯也允许雷鸣号打；
* ``EVADE_ENABLED = False``     第三类只关雷达、不跑（不动航路，最保守）。
"""

import logging
import math
import re

__all__ = ["ShipClusterDefense"]


# ======================================================================
# 小工具
# ======================================================================
_PUNCT_RE = re.compile(r'[\s\u3000"“”\'‘’()（）\[\]【】《》<>]')


def _norm(text):
    """名称归一化：小写、去掉空白与各类引号括号、统一全半角，便于关键字匹配。"""
    t = str(text or '').lower()
    t = _PUNCT_RE.sub('', t)
    t = t.replace('：', ':').replace('，', ',').replace('。', '.')
    t = t.replace('—', '-').replace('–', '-').replace('－', '-')
    return t


def _to_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _km(lat1, lon1, lat2, lon2):
    """两点大圆距离（公里）。取球面余弦公式，误差在本场景（数十~数百公里）可忽略。"""
    lat1, lon1, lat2, lon2 = (_to_float(lat1), _to_float(lon1),
                              _to_float(lat2), _to_float(lon2))
    if None in (lat1, lon1, lat2, lon2):
        return None
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2.0) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2)
    a = min(1.0, max(0.0, a))
    return 2.0 * 6371.0 * math.asin(math.sqrt(a))


def _bearing(lat1, lon1, lat2, lon2):
    """起点指向终点的方位角（度，正北为 0，顺时针）。"""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = (math.cos(p1) * math.sin(p2)
         - math.sin(p1) * math.cos(p2) * math.cos(dl))
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def _shift(lat, lon, bearing_deg, dist_km):
    """从 (lat, lon) 沿 bearing_deg 走 dist_km 后的坐标。"""
    br = math.radians(bearing_deg)
    d = dist_km / 6371.0
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(d)
                   + math.cos(p1) * math.sin(d) * math.cos(br))
    l2 = l1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(p1),
                         math.cos(d) - math.sin(p1) * math.sin(p2))
    return (math.degrees(p2), (math.degrees(l2) + 540.0) % 360.0 - 180.0)


def _cget(contact, key, default=None):
    """
    从情报对象里取字段。

    平台把情报转成字典时**键名首字母大写**（'Name'/'Type'/'Lat'/'Lon'），
    但不同版本、不同序列化路径偶尔给的是小写或对象属性，故三级兼容。
    """
    if contact is None:
        return default
    for k in (key, key.capitalize(), key.lower(), key.upper()):
        if isinstance(contact, dict):
            if k in contact:
                return contact[k]
        else:
            try:
                if hasattr(contact, k):
                    return getattr(contact, k)
            except Exception:
                pass
    try:
        return contact[key]
    except Exception:
        return default


# ======================================================================
# 智能体
# ======================================================================
class ShipClusterDefense(object):
    """登陆船只集群自卫智能体。"""

    # ------------------------------------------------------------------
    # 总开关
    # ------------------------------------------------------------------
    ENABLE = True
    # C 区第二类威胁是否分层补射（False = 与 ABDE 一致，都在 Dmax 开火）
    LAYERED = True
    # C 区卢卡斯是否也允许雷鸣号拦截（False = 按报告，只由 23900 处理）
    LUCAS_C_FIRE = False
    # 第三类是否允许改航路机动（False = 只关雷达、不动航路）
    EVADE_ENABLED = True

    # ------------------------------------------------------------------
    # 舰队识别：名称关键字（任一命中即算本方舰船）
    #   现役想定：蟾蜍级登陆舰 #1~#7、雷鸣号护卫舰 #1#2#3#4#5#8#10、
    #             23900 型船坞登陆舰 #1、PR.2235.0 护卫舰 #1 → 共 16 艘。
    #   换想定只改这一行；若某型舰名改了，把新关键字补进来即可。
    # ------------------------------------------------------------------
    FLEET_KEYWORDS = ('蟾蜍', 'toad', '雷鸣', 'leiming', '23900',
                      'ivan rogov', '伊万', '2235', 'pr.2235')

    # ------------------------------------------------------------------
    # 区域判定
    # ------------------------------------------------------------------
    # 归入 C 区的登陆编队任务名（C1/C2 是中央登陆轴）
    ZONE_C_MISSIONS = ('C1', 'C2', 'C')
    # 任务名读不到时的几何退化判定：C 区中心与半径
    ZONE_C_CENTER = (49.87, -0.55)
    ZONE_C_RADIUS_KM = 60.0

    # ------------------------------------------------------------------
    # 威胁判据（报告 2.3.4.1 表 18）
    # ------------------------------------------------------------------
    # 只处理对这个距离以内的集群构成威胁的来袭弹（超出不理会，省指令）
    ENGAGE_RADIUS_KM = 140.0
    # 第一类：弹距小于该值才视为真弹（船在动，远界多是欺骗弹）
    LUCAS_CLOSE_KM = 3.0
    # C 区由 23900 激光处理的就近距离
    LUCAS_LASER_KM = 5.0
    # 第三类（反舰导弹）机动规避的转弯角与航程
    EVADE_ANGLE_DEG = 135.0          # 135°=斜后方，兼顾「切向」与「背身」
    EVADE_DISTANCE_KM = 25.0

    # ------------------------------------------------------------------
    # 开火控制
    # ------------------------------------------------------------------
    SALVO_ROUNDS = 2                 # 每次拦截分配的弹数（表 19 的 2.22 发/次）
    REENGAGE_CYCLES = 3              # 同一 (舰, 弹) 的最短重发间隔（周期）
    FALLBACK_DMAX_KM = 65.0          # 查不到弹种射程时的兜底（SA-N-21d = 65 km）
    MIN_SAM_AIR_RANGE_KM = 10.0      # 判定「这艘船有舰空导弹」的最低对空射程

    # ------------------------------------------------------------------
    # 状态机
    # ------------------------------------------------------------------
    RELEASE_CYCLES = 3               # 连续多少周期无该类威胁才退出规避
    RADAR_BLINK_CYCLES = 4           # 无弹时雷达「时开时关」的开/关周期数

    # ------------------------------------------------------------------
    # 召唤苏-57
    # ------------------------------------------------------------------
    SUMMON_ENABLE = True
    SUMMON_KEYWORDS = ('苏-57', '苏57', 'su-57', 'su57')
    SUMMON_MISSION_NAME = '登陆编队护航'
    SUMMON_COOLDOWN = 10             # 两次召唤之间的最小间隔（周期）
    SUMMON_MAX_TIMES = 3             # 一局最多召唤几次（防止反复抽调）

    # ------------------------------------------------------------------
    # 威胁关键字 → 类别
    #   顺序有意义：先判卢卡斯（无人机），再判空射反舰弹，最后判陆基反舰弹。
    # ------------------------------------------------------------------
    THREAT_KEYWORDS = (
        ('lucas', ('卢卡斯', 'lucas')),
        ('asm_air', ('agm-158', 'lrasm', 'agm-154', 'jsow',
                     '158c', '154c', '158 c', '154 c')),
        ('asm_ground', ('雄风', 'hsiung', 'hf-2', 'hf2', 'hf-3',
                        'm30a2', 'm30a1', 'gmler', '制导火箭',
                        '反舰导弹排', '海马斯')),
    )

    # 舰船角色（按能力探测；名字只用于给 23900 兜底）
    ROLE_SAM = 'sam'
    ROLE_LASER = 'laser'
    ROLE_LANDING = 'landing'

    # ==================================================================
    # 构造
    # ==================================================================
    def __init__(self, agent, monitor=None, log=None):
        """
        :param agent: RuleAgentBase 实例（宿主智能体，提供 get_unit /
                      create_support_mission / assign_units_to_mission 等接口）
        :param monitor: BattlefieldMonitor 实例。给了就用它做「是否有弹指向本方」
                        的判定（设计报告 2.3.1 的唯一信息源）；不给则本模块自己
                        扫情报，便于单独运行与离线测试。
        :param log: callable(level, msg)；不给则用 agent._log，再退化为 logging
        """
        self.agent = agent
        self.monitor = monitor
        self._log_fn = log
        self._cycle = 0

        # 舰队与能力（setup 里填充）
        self._ships = []            # [{'name','guid','obj','role','dmax','sam_wid',
                                #   'ammo','mission'}]
        self._ship_by_guid = {}
        self._fighter_guids = []
        self._sub_ready = False

        # 运行状态
        self._engage_at = {}        # (ship_guid, threat_guid) -> cycle
        self._evading = {}          # ship_guid -> {'course': [...], 'since': cycle}
        self._radar_state = {}      # ship_guid -> bool（我们下发的雷达状态）
        self._radar_blink = {}      # ship_guid -> cycle
        self._emcon_released = set()   # 已解除电磁管控的舰
        self._wcs_free_done = set()    # 已设为对空自由开火的舰
        self._quiet = {}            # ship_guid -> 连续无第三类威胁的周期数
        self._summon_at = -10 ** 6
        self._summon_times = 0
        self._summon_mission = None
        self._last_report = {}

    # ------------------------------------------------------------------
    # 日志
    # ------------------------------------------------------------------
    def _log(self, level, msg):
        fn = self._log_fn
        if not callable(fn):
            fn = getattr(self.agent, '_log', None)
        text = '[舰船自卫] %s' % msg
        if callable(fn):
            try:
                fn(level, text)
                return
            except Exception:
                pass
        getattr(logging, level if level in ('info', 'warning', 'error') else 'info',
                logging.info)(text)

    # ------------------------------------------------------------------
    # 枚举惰性解析：宿主已 from global_util import *，直接借它的模块取，
    # 这样本文件不必 import entitys，粘进主文件也能跑。
    # ------------------------------------------------------------------
    def _enum(self, name, member, fallback):
        """
        取平台枚举成员，三级兜底：

        ① 宿主模块（宿主做了 ``from global_util import *``，枚举就在它的命名空间里）；
        ② 直接 import global_util（宿主被 exec 加载、模块没登记进 sys.modules 时）；
        ③ 整数常量兜底（只在离线单测里会走到）。
        """
        try:
            import sys
            mod = sys.modules.get(type(self.agent).__module__)
            enum_cls = getattr(mod, name, None) if mod is not None else None
            if enum_cls is not None:
                return getattr(enum_cls, member, fallback)
        except Exception:
            pass
        for mod_name in ('engine.LingYi.entitys.global_util', 'entitys.global_util'):
            try:
                mod = __import__(mod_name, fromlist=['*'])
                enum_cls = getattr(mod, name, None)
                if enum_cls is not None:
                    return getattr(enum_cls, member, fallback)
            except Exception:
                continue
        return fallback

    def _throttle(self, member):
        # Throttle.Flank=5 / Full=4 / Cruise=3 / Loiter=2 / FullStop=1
        fallback = {'Flank': 5, 'Full': 4, 'Cruise': 3,
                    'Loiter': 2, 'FullStop': 1}.get(member, 3)
        return self._enum('Throttle', member, fallback)

    def _wcs_free(self):
        # WeaponControlStatus.Free = 0
        return self._enum('WeaponControlStatus', 'Free', 0)

    # ==================================================================
    # 一、开局解析
    # ==================================================================
    def setup(self, situation):
        """
        解析本方登陆舰队、判定每艘舰的角色与能力。

        :param situation: tuple, (units dict, contacts dict)
        :return: dict, 自检结果（可直接打进日志）
        """
        if not self.ENABLE:
            return {}
        try:
            self._ships = self._resolve_fleet(situation)
            self._ship_by_guid = dict((s['guid'], s) for s in self._ships)
            self._fighter_guids = self._resolve_fighters()
            self._sub_ready = True
        except Exception as e:
            self._log('error', '初始化异常: %s' % e)
            self._sub_ready = False
            return {}

        roles = {}
        for s in self._ships:
            roles[s['role']] = roles.get(s['role'], 0) + 1
        rep = {
            '舰船数': len(self._ships),
            '角色分布': roles,
            '苏57数': len(self._fighter_guids),
            'Dmax': dict((s['name'], round(s['dmax'], 1)) for s in self._ships
                         if s['role'] == self.ROLE_SAM),
            '监控': ('已接入（唯一信息源）' if self.monitor is not None
                     else '未接入（自扫情报）'),
        }
        self._log('info', '初始化完成：%s' % rep)
        if not self._ships:
            self._log('warning', '未解析到登陆舰队（蟾蜍/雷鸣/23900/2235），'
                                 '本智能体不动作')
        return rep

    def _resolve_fleet(self, situation):
        """
        从态势里取出本方登陆舰队，并探测每艘舰的能力。

        舰船按「**能力**」而不是名字定角色，理由：换想定时舰名会变，而
        「有没有对空导弹」不会变；23900 的激光按名字兜底。
        """
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return []

        fleet_kw = self.FLEET_KEYWORDS
        out = []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            cat = str(u.get('category', '') or '')
            if cat and cat.lower() not in ('ship', 'surface'):
                continue
            name = str(u.get('name', '') or '')
            bare = _norm(name)
            if not any(_norm(k) in bare for k in fleet_kw):
                continue
            g = u.get('guid') or guid
            obj = self.agent.get_unit(g)
            if obj is None:
                continue
            info = self._probe_ship(name, g, obj, u)
            out.append(info)

        # C 区优先排序：C 区舰排在前面，便于「一号舰/二号舰」的编号
        out.sort(key=lambda x: (0 if self._zone_of_unit(x) == 'C' else 1,
                                x['name']))
        return out

    def _probe_ship(self, name, guid, obj, unit_dict):
        """探测单舰：对空导弹型号/射程/余弹、是否有激光、所属任务。"""
        sam = self._best_air_weapon(obj)
        laser = self._has_laser(obj)
        role = self.ROLE_LANDING
        if sam:
            role = self.ROLE_SAM
        elif laser or _norm('23900') in _norm(name) or '伊万' in name:
            # 没有对空导弹但具备激光/近防平台的船坞登陆舰
            role = self.ROLE_LASER

        return {
            'name': name,
            'guid': guid,
            'obj': obj,
            'role': role,
            'dmax': (sam or {}).get('range', self.FALLBACK_DMAX_KM),
            'sam_wid': (sam or {}).get('wid'),
            'sam_mount': (sam or {}).get('mount'),
            'ammo': (sam or {}).get('count', 0),
            'laser': laser,
            'mission': str(unit_dict.get('mission', '') or ''),
            'lat': _to_float(unit_dict.get('lat', unit_dict.get('latitude'))),
            'lon': _to_float(unit_dict.get('lon', unit_dict.get('longitude'))),
        }

    def _iter_weapon_recs(self, unit):
        """遍历单元上的（挂架DBID, 武器DBID, 当前数量）。三处都要看：挂架/弹仓/挂载。"""
        for attr in ('Mounts', 'Magazines', 'Loadouts'):
            cont = getattr(unit, attr, None)
            if not isinstance(cont, dict):
                continue
            for mk, mv in cont.items():
                if not isinstance(mv, dict):
                    continue
                mount = None
                comp = mv.get('Component')
                if isinstance(comp, dict) and comp.get('DBID') is not None:
                    mount = _to_int(comp.get('DBID'))
                if mount is None:
                    mount = _to_int(mv.get('DBID')) or _to_int(mk)
                wrs = mv.get('WeaponRecs')
                if isinstance(wrs, dict):
                    items = list(wrs.values())
                elif isinstance(wrs, (list, tuple)):
                    items = list(wrs)
                else:
                    items = []
                for w in items:
                    if not isinstance(w, dict):
                        continue
                    wid = _to_int(w.get('WeaponDBID'))
                    if wid is None:
                        continue
                    cnt = _to_int(w.get('CurrentLoad'))
                    if cnt is None:
                        cnt = _to_int(w.get('DefaultLoad')) or 0
                    yield mount, wid, cnt

    def _best_air_weapon(self, unit):
        """
        找出该舰**实际携带**的对空导弹里射程最远的一型。

        :return: dict 或 None, {'wid','mount','range','count'}
        """
        best = None
        seen = {}
        for mount, wid, cnt in self._iter_weapon_recs(unit):
            seen[wid] = seen.get(wid, 0) + (cnt or 0)
            info = self._weapon_range(wid)
            if info is None:
                continue
            rng = info[0]
            if rng is None or rng < self.MIN_SAM_AIR_RANGE_KM:
                continue
            if best is None or rng > best['range']:
                best = {'wid': wid, 'mount': mount, 'range': float(rng),
                        'count': seen[wid]}
        if best is not None:
            # 余弹按同型弹总数算（同型弹可能分装多个挂架）
            best['count'] = seen.get(best['wid'], 0)
        return best

    def _weapon_range(self, wid):
        """查武器对空最大射程（km）。查不到返回 None。"""
        try:
            qd = self._query_data()
            if qd is not None:
                row = qd.get_weapon_info(int(wid))
                if row:
                    # (AirRangeMax, AirPoK, LandRangeMax, ...)
                    rng = _to_float(row[0])
                    name = row[13] if len(row) > 13 else ''
                    return (rng, name)
        except Exception:
            pass
        return None

    def _query_data(self):
        """取 entitys.data.query_data（宿主可能已经导入过）。"""
        try:
            import sys
            for mod_name in ('engine.LingYi.entitys.data', 'entitys.data'):
                if mod_name in sys.modules:
                    mod = sys.modules[mod_name]
                    if hasattr(mod, 'query_data'):
                        return mod.query_data
            from engine.LingYi.entitys.data import query_data
            return query_data
        except Exception:
            try:
                from entitys.data import query_data
                return query_data
            except Exception:
                return None

    def _has_laser(self, unit):
        """是否有激光类武器（按武器名判定；平台无此能力时返回 False）。"""
        try:
            qd = self._query_data()
            if qd is None:
                return False
            for _m, wid, _c in self._iter_weapon_recs(unit):
                try:
                    nm = qd.get_weapon_name(int(wid)) or ''
                except Exception:
                    nm = ''
                if '激光' in nm and '制导' not in nm:
                    return True
        except Exception:
            pass
        return False

    def _resolve_fighters(self):
        """解析可召唤的苏-57（本方飞机）。"""
        out = []
        try:
            aircrafts = getattr(self.agent, 'aircrafts', None)
            if not isinstance(aircrafts, dict):
                return out
            for g, obj in aircrafts.items():
                nm = _norm(getattr(obj, 'Name', '') or '')
                if any(_norm(k) in nm for k in self.SUMMON_KEYWORDS):
                    out.append(g)
        except Exception:
            pass
        return out

    def _zone_of_unit(self, ship):
        """按所属任务名判区，读不到任务名时退化为几何判定。"""
        mission = str(ship.get('mission') or '')
        if mission:
            for m in self.ZONE_C_MISSIONS:
                if mission == m or mission.startswith(m):
                    return 'C'
            return 'ABDE'
        lat, lon = ship.get('lat'), ship.get('lon')
        clat, clon = self.ZONE_C_CENTER
        d = _km(lat, lon, clat, clon)
        if d is not None and d <= self.ZONE_C_RADIUS_KM:
            return 'C'
        return 'ABDE'

    # ==================================================================
    # 二、每周期决策
    # ==================================================================
    def step(self, situation):
        """
        每周期调用一次：识别威胁 → 按「弹型 × 区域」分派处置。

        :param situation: tuple, (units dict, contacts dict)
        :return: dict, 本周期的决策摘要（便于主智能体打日志）
        """
        if not self.ENABLE:
            return {}
        self._cycle += 1
        try:
            if not self._sub_ready:
                self.setup(situation)
            if not self._ships:
                return {}

            self._refresh_positions(situation)
            threats = self._scan_threats(situation)
            acts = self._dispatch(threats)
            self._housekeep(threats)

            if acts or self._cycle % 20 == 0:
                self._log('info', '周期%d：威胁%d（%s），动作%s'
                          % (self._cycle, len(threats),
                             self._brief_threats(threats), acts))
            self._last_report = {'cycle': self._cycle,
                                 'threats': len(threats),
                                 'actions': acts}
            return self._last_report
        except Exception as e:
            self._log('error', '周期%d 决策异常: %s' % (self._cycle, e))
            return {}

    def _refresh_positions(self, situation):
        """刷新各舰当前位置、所属任务与余弹（态势字典是权威来源）。"""
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return
        for s in self._ships:
            u = units.get(s['guid'])
            if not isinstance(u, dict):
                # 态势 key 偶尔不是 guid，退化为按名字找
                u = None
                for _g, cand in units.items():
                    if isinstance(cand, dict) and \
                            str(cand.get('name', '')) == s['name']:
                        u = cand
                        break
            if isinstance(u, dict):
                s['lat'] = _to_float(u.get('lat', u.get('latitude')), s['lat'])
                s['lon'] = _to_float(u.get('lon', u.get('longitude')), s['lon'])
                m = str(u.get('mission', '') or '')
                if m:
                    s['mission'] = m
            # 余弹随时在变，每周期更新（打光后就该走软杀伤分支）
            if s['role'] == self.ROLE_SAM and s['sam_wid'] is not None:
                total = 0
                for _m, wid, cnt in self._iter_weapon_recs(s['obj']):
                    if wid == s['sam_wid']:
                        total += (cnt or 0)
                s['ammo'] = total

    def _scan_threats(self, situation):
        """
        挑出对集群有威胁的来袭弹。

        **有监控智能体时走监控**（报告 2.3.1：监控是唯一信息源，只回答"是否有弹
        指向本方 + 弹型 + 弹速"），本模块只负责**重算距离**——报告明确要求下游
        各算各的，不依赖监控的内部实现。没接监控时退化为自己扫情报。

        :return: list, [{'guid','name','cls','lat','lon','speed','near','dist'}]
                 near = 最近的那艘舰；dist = 到该舰的距离（km）
        """
        if self.monitor is not None and getattr(self.monitor, 'ready', False):
            try:
                self.monitor.ensure(situation)
                return self._scan_from_monitor(situation)
            except Exception as e:
                self._log('warning', '监控结果不可用，退回自扫情报: %s' % e)
        return self._scan_from_contacts(situation)

    def _scan_from_monitor(self, situation):
        """
        消费监控输出：对每艘舰问"有没有弹指向你"，再把弹目距离自己重算一遍。

        监控给的是 (弹型, 弹速) + 情报 guid；坐标仍从情报里取，距离用本舰位置
        重算——这样监控换实现也不会影响本模块的判据。
        """
        contacts = situation[1] if isinstance(situation, (tuple, list)) \
            and len(situation) > 1 else {}
        if not isinstance(contacts, dict):
            return []
        by_id = {}
        for cid, c in contacts.items():
            by_id[_cget(c, 'ID', cid) or cid] = c

        merged = {}
        for s in self._ships:
            if s.get('lat') is None or s.get('lon') is None:
                continue
            for row in self.monitor.threats_for(s['guid']):
                c = by_id.get(row.get('cid'))
                if c is None:
                    continue
                lat = _to_float(_cget(c, 'Lat', None))
                lon = _to_float(_cget(c, 'Lon', None))
                if lat is None or lon is None:
                    continue
                cls = self._classify(row.get('name') or
                                     str(_cget(c, 'Name', '') or ''))
                if cls is None:
                    continue
                dist = _km(lat, lon, s['lat'], s['lon'])
                if dist is None or dist > self.ENGAGE_RADIUS_KM:
                    continue
                cur = merged.get(row.get('cid'))
                # 同一枚弹可能同时"指向"几艘舰，按最近的那艘记账
                if cur is None or dist < cur['dist']:
                    merged[row.get('cid')] = {
                        'guid': row.get('cid'),
                        'name': row.get('name') or str(_cget(c, 'Name', '') or ''),
                        'cls': cls,
                        'lat': lat, 'lon': lon,
                        'speed': _to_float(_cget(c, 'CurrentSpeed', None)),
                        'near': s,
                        'dist': dist,
                    }
        out = list(merged.values())
        out.sort(key=lambda t: t['dist'])
        return out

    def _scan_from_contacts(self, situation):
        """
        没有监控时的退化路径：自己扫情报，按名称关键字认威胁、按当前距离筛。

        :return: list, 同 ``_scan_threats``
        """
        contacts = situation[1] if isinstance(situation, (tuple, list)) \
            and len(situation) > 1 else {}
        if not isinstance(contacts, dict):
            return []

        out = []
        for cid, c in contacts.items():
            name = str(_cget(c, 'Name', '') or '')
            if not name:
                continue
            ctype = _to_int(_cget(c, 'Type', None))
            # 只认「导弹」与「空中目标」；水面/地面/潜艇不在此智能体范围
            if ctype is not None and ctype not in (0, 1):
                continue
            cls = self._classify(name)
            if cls is None:
                continue
            lat = _to_float(_cget(c, 'Lat', None))
            lon = _to_float(_cget(c, 'Lon', None))
            if lat is None or lon is None:
                continue

            near, best = None, None
            for s in self._ships:
                if s.get('lat') is None or s.get('lon') is None:
                    continue
                d = _km(lat, lon, s['lat'], s['lon'])
                if d is None:
                    continue
                if best is None or d < best:
                    best, near = d, s
            if near is None or best is None:
                continue
            if best > self.ENGAGE_RADIUS_KM:
                continue

            out.append({
                'guid': _cget(c, 'ID', cid) or cid,
                'name': name,
                'cls': cls,
                'lat': lat, 'lon': lon,
                'speed': _to_float(_cget(c, 'CurrentSpeed', None)),
                'near': near,
                'dist': best,
            })
        out.sort(key=lambda t: t['dist'])
        return out

    def _classify(self, name):
        """按名称关键字判定威胁类别；识别不了的按空射反舰弹（第三类）处理。"""
        bare = _norm(name)
        for cls, kws in self.THREAT_KEYWORDS:
            for k in kws:
                if _norm(k) in bare:
                    return cls
        # 防空导弹/巡航弹等落到这里：不主动介入，避免误把对方防空弹当反舰弹
        return None

    # ------------------------------------------------------------------
    # 分派
    # ------------------------------------------------------------------
    def _dispatch(self, threats):
        acts = []
        for t in threats:
            zone = self._zone_of_unit(t['near'])
            t['zone'] = zone
            try:
                if t['cls'] == 'lucas':
                    acts.append(self._handle_lucas(t, zone))
                elif t['cls'] == 'asm_ground':
                    acts.append(self._handle_asm_ground(t, zone))
                else:
                    acts.append(self._handle_asm_air(t))
            except Exception as e:
                self._log('error', '威胁[%s]处置异常: %s' % (t['name'], e))
        return [a for a in acts if a]

    # ---------------- 第一类：卢卡斯无人机 ----------------
    def _handle_lucas(self, t, zone):
        """
        ABDE 区：雷鸣号在弹距 < 3 km 时自卫（判真弹，不打欺骗弹）。
        C 区   ：雷鸣号写死不打，由 23900 的激光自由开火。
        """
        if zone == 'C':
            lpd = self._pick(lambda s: s['role'] == self.ROLE_LASER, t)
            if lpd is None:
                # 23900 若带了舰空导弹，会被能力探测判成 sam；这里按名字兜底，
                # 否则「C 区卢卡斯没人管」——雷鸣号仍然不许打。
                lpd = self._pick(lambda s: self._is_lpd(s['name']), t)
            if lpd is None:
                if self._warn_once('no_lpd'):
                    self._log('warning', 'C 区发现卢卡斯，但没有可用的 23900 '
                                         '（既无激光也未识别到舰名），本轮不处理')
                return None
            if not self.LUCAS_C_FIRE:
                # 让 23900 自己的近防/激光自由开火（一次设定，之后靠平台自动）
                self._set_wcs_free(lpd)
            if t['dist'] <= self.LUCAS_LASER_KM or self.LUCAS_C_FIRE:
                return self._fire(lpd, t, qty=1) and ('C区卢卡斯→%s' % lpd['name'])
            return None

        if t['dist'] > self.LUCAS_CLOSE_KM:
            # 远界不理会：船在动，弹的预定航线与船位偏差大，多半是欺骗弹
            return None
        sam = self._pick(lambda s: s['role'] == self.ROLE_SAM, t)
        if sam is None:
            return None
        ok = self._fire(sam, t, qty=1)
        return ('ABDE区卢卡斯近距自卫→%s' % sam['name']) if ok else None

    @staticmethod
    def _is_lpd(name):
        """是不是那艘 23900 船坞登陆舰（名字兜底，用于能力探测误判时）。"""
        bare = _norm(name)
        return ('23900' in bare) or ('伊万' in bare) or ('ivanrogov' in bare)

    def _warn_once(self, key):
        """同一条告警只打一次，避免每周期刷屏。"""
        done = getattr(self, '_warned', None)
        if done is None:
            done = set()
            self._warned = done
        if key in done:
            return False
        done.add(key)
        return True

    # ---------------- 第二类：海马斯 / 反舰导弹排 ----------------
    def _handle_asm_ground(self, t, zone):
        """
        ABDE 区：雷鸣号以 Dmax 开火。
        C 区   ：一号舰 Dmax 先拦，二号舰等弹突防到 1/2 Dmax 再补拦。
        """
        sams = self._sorted_sams(t)
        if not sams:
            return None

        if zone != 'C' or not self.LAYERED:
            ship = sams[0]
            if t['dist'] <= ship['dmax']:
                ok = self._fire(ship, t, qty=self.SALVO_ROUNDS)
                return ('%s区陆基反舰弹→%s(Dmax%.0f)'
                        % (zone, ship['name'], ship['dmax'])) if ok else None
            return None

        # C 区分层：一号舰远界先拦
        first = sams[0]
        if t['dist'] <= first['dmax']:
            ok = self._fire(first, t, qty=self.SALVO_ROUNDS)
            if ok:
                return 'C区分层→%s(Dmax%.0f 先拦)' % (first['name'], first['dmax'])

        # 二号舰等突防到半射程再补，避免两舰同打一枚弹
        if len(sams) >= 2:
            second = sams[1]
            if t['dist'] <= second['dmax'] * 0.5:
                ok = self._fire(second, t, qty=self.SALVO_ROUNDS)
                if ok:
                    return ('C区分层→%s(%.0fkm 半射程补拦)'
                            % (second['name'], second['dmax'] * 0.5))
        return None

    # ---------------- 第三类：158C / 154C 空射反舰弹 ----------------
    def _handle_asm_air(self, t):
        """
        关雷达 + 双舰切向背身跑 + 加力；有弹则开雷达打，无弹则时开时关；
        同时召唤苏-57 至船的上空，驱离为其提供持续照射的敌机。

        顺序有讲究：**先决定这一轮要不要开雷达打，再决定雷达该开还是关**，
        否则同一周期里会出现「关了又开」的两条指令，白占配额。
        """
        ship = t['near']
        acts = []
        has_ammo = (ship['role'] == self.ROLE_SAM and ship['ammo'] > 0
                    and ship.get('sam_wid') is not None)

        # ① 软杀伤：关雷达 + 切向背身 + 加力
        if not has_ammo:
            self._radar_set(ship, False)
        if self.EVADE_ENABLED:
            self._start_evade(ship, t)

        # ② 硬杀伤：只有「有弹」的舰才开雷达打（报告第三类的分支）
        if has_ammo:
            self._radar_set(ship, True)
            if t['dist'] <= ship['dmax']:
                if self._fire(ship, t, qty=self.SALVO_ROUNDS):
                    acts.append('%s 有弹→开雷达拦截(%.0fkm)'
                                % (ship['name'], t['dist']))
            else:
                acts.append('%s 有弹但超出射程(%.0f>%.0fkm)'
                            % (ship['name'], t['dist'], ship['dmax']))
        elif ship['role'] == self.ROLE_SAM:
            # 无弹：时开时关迷惑（周期性地开一个周期以刷新航迹）
            if (self._cycle - self._radar_blink.get(ship['guid'], 0)) \
                    >= self.RADAR_BLINK_CYCLES:
                self._radar_blink[ship['guid']] = self._cycle
                self._radar_set(ship, True)
                acts.append('%s 无弹→雷达闪亮' % ship['name'])

        # ③ 夺取局部制空权：召唤苏-57 打照射机
        if self._summon():
            acts.append('召唤苏-57至编队上空')

        if not acts:
            acts.append('%s 规避中(%.0fkm)' % (ship['name'], t['dist']))
        return '；'.join(acts)

    # ------------------------------------------------------------------
    # 通用动作
    # ------------------------------------------------------------------
    def _sorted_sams(self, t):
        """按到该弹的距离排序的、有弹的防空舰。"""
        sams = [s for s in self._ships
                if s['role'] == self.ROLE_SAM and s.get('lat') is not None]
        for s in sams:
            s['_d'] = _km(t['lat'], t['lon'], s['lat'], s['lon']) or 1e9
        sams.sort(key=lambda s: s['_d'])
        return sams

    def _pick(self, pred, t):
        """按条件挑距离该弹最近的舰。"""
        cands = [s for s in self._ships if pred(s) and s.get('lat') is not None]
        if not cands:
            # 位置未知时退化为第一个符合条件的
            cands = [s for s in self._ships if pred(s)]
            return cands[0] if cands else None
        return min(cands, key=lambda s: _km(t['lat'], t['lon'], s['lat'], s['lon'])
                   or 1e9)

    def _fire(self, ship, threat, qty=None):
        """
        对来袭弹分配拦截。

        优先 ``attack_weapon_allocate_to_target``（可指定弹种与齐射数），
        退化 ``attack_manual``，再退化 ``attack_auto``；同一 (舰, 弹) 节流。

        :return: bool, 本次是否真的下发了指令
        """
        key = (ship['guid'], threat['guid'])
        last = self._engage_at.get(key)
        if last is not None and self._cycle - last < self.REENGAGE_CYCLES:
            return False
        qty = self.SALVO_ROUNDS if qty is None else qty
        obj = ship['obj']
        wid = ship.get('sam_wid')
        mount = ship.get('sam_mount') or 0

        ok = False
        try:
            if wid:
                res = obj.attack_weapon_allocate_to_target(
                    threat['guid'], int(wid), int(qty))
                ok = self._reply_ok(res)
            if not ok:
                res = obj.attack_manual(threat['guid'], int(mount), int(wid or 0),
                                        int(qty))
                ok = self._reply_ok(res)
            if not ok:
                res = obj.attack_auto(threat['guid'])
                ok = self._reply_ok(res)
        except Exception as e:
            self._log('error', '%s 开火指令异常: %s' % (ship['name'], e))
            return False

        if ok:
            self._engage_at[key] = self._cycle
            self._log('info', '%s 拦截[%s] 距离%.0fkm 弹数%d'
                      % (ship['name'], threat['name'], threat['dist'], qty))
        else:
            self._log('warning', '%s 拦截[%s] 指令被拒（可能无弹或超出射程）'
                      % (ship['name'], threat['name']))
        return ok

    @staticmethod
    def _reply_ok(res):
        """平台回执判定：**只看 code == 0**，不要用「失败」两字判断。"""
        if res is None:
            return False
        code = getattr(res, 'code', None)
        if code is not None:
            try:
                return int(code) == 0
            except (TypeError, ValueError):
                return False
        raw = getattr(res, 'result', res)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode('utf-8', 'replace')
            except Exception:
                raw = str(raw)
        s = str(raw)
        return not any(b in s for b in ('指令执行失败', '超出数量限制',
                                        '已被取消下发', '找不到武器'))

    def _radar_set(self, ship, on):
        """
        设置雷达开关（同一状态不重复下发）。

        平台要求：手动开关雷达前必须把「是否遵循电磁管控条令」置 False，
        否则开关不生效。故每舰第一次下发前先解除一次管控。
        """
        cur = self._radar_state.get(ship['guid'])
        if cur is on:
            return
        obj = ship['obj']
        try:
            if ship['guid'] not in self._emcon_released:
                try:
                    obj.EMCON_Obey_doctrine(False)
                    self._emcon_released.add(ship['guid'])
                except Exception:
                    pass
            res = obj.switch_radar(bool(on))
            if self._reply_ok(res) or res is None:
                self._radar_state[ship['guid']] = bool(on)
                self._log('info', '%s 雷达%s' % (ship['name'], '开' if on else '关'))
        except Exception as e:
            self._log('warning', '%s 雷达开关失败: %s' % (ship['name'], e))

    def _set_wcs_free(self, ship):
        """让该舰对空自由开火（23900 的近防/激光自行交战）。一次设定即可。"""
        if ship['guid'] in self._wcs_free_done:
            return
        try:
            ship['obj'].doctrine_weapon_control_status_air(self._wcs_free())
            self._wcs_free_done.add(ship['guid'])
            self._log('info', '%s 对空改为自由开火（C区近防自交战）' % ship['name'])
        except Exception as e:
            self._log('warning', '%s 设对空自由开火失败: %s' % (ship['name'], e))

    # ------------------------------------------------------------------
    # 机动规避与恢复
    # ------------------------------------------------------------------
    def _start_evade(self, ship, threat):
        """切向背身跑：记下原航路 → 规划斜后方航路 → 加力。"""
        if ship['guid'] in self._evading:
            return
        snapshot = self._snapshot_course(ship)
        lat, lon = ship.get('lat'), ship.get('lon')
        brg = _bearing(lat, lon, threat['lat'], threat['lon'])
        # 斜后方：既脱离来袭方向，又不完全背对（保留侧向机动余地）
        esc = (brg + self.EVADE_ANGLE_DEG) % 360.0
        pt = _shift(lat, lon, esc, self.EVADE_DISTANCE_KM)
        try:
            ship['obj'].plotted_course([pt])
            ship['obj'].set_throttle(self._throttle('Flank'))
            self._evading[ship['guid']] = {'course': snapshot,
                                           'since': self._cycle}
            self._log('info', '%s 切向背身规避：航向%.0f°，原航路%d点已快照'
                      % (ship['name'], esc, len(snapshot)))
        except Exception as e:
            self._log('warning', '%s 规避机动失败: %s' % (ship['name'], e))

    def _snapshot_course(self, ship):
        """快照当前航路（供威胁解除后回填）。坐标键是 longitude/latitude。"""
        out = []
        try:
            for p in (ship['obj'].get_way_points_info() or []):
                lat = _to_float(p.get('latitude'))
                lon = _to_float(p.get('longitude'))
                if lat is not None and lon is not None:
                    out.append((lat, lon))
        except Exception:
            pass
        return out

    def _stop_evade(self, ship):
        """威胁解除：回填原航路、恢复巡航、开雷达。"""
        st = self._evading.pop(ship['guid'], None)
        if st is None:
            return
        try:
            if st['course']:
                ship['obj'].plotted_course(list(st['course']))
                self._log('info', '%s 归建：回填原航路%d点'
                          % (ship['name'], len(st['course'])))
            else:
                self._log('info', '%s 归建：原航路为空，交由任务重新下发'
                          % ship['name'])
            ship['obj'].set_throttle(self._throttle('Cruise'))
            self._radar_set(ship, True)
        except Exception as e:
            self._log('warning', '%s 归建失败: %s' % (ship['name'], e))

    # ------------------------------------------------------------------
    # 召唤苏-57
    # ------------------------------------------------------------------
    def _summon(self):
        """
        调用苏-57 至登陆编队上空，驱离为反舰导弹提供持续照射的敌机。

        首次调用建一个支援任务「登陆编队护航」并把苏-57 编进去；之后按
        SUMMON_COOLDOWN 节流重下航线（编队会移动）。建任务失败则直接改航路。
        """
        if not self.SUMMON_ENABLE or not self._fighter_guids:
            return False
        if self._summon_times >= self.SUMMON_MAX_TIMES:
            return False
        if self._cycle - self._summon_at < self.SUMMON_COOLDOWN:
            return False

        center = self._fleet_center()
        if center is None:
            return False
        self._summon_at = self._cycle
        self._summon_times += 1

        # ① 优选：建一个以编队为中心的护航任务
        try:
            if self._summon_mission is None:
                m = self.agent.get_mission_by_name(self.SUMMON_MISSION_NAME)
                if m is None:
                    lat, lon = center
                    pts = [(lat + 0.25, lon - 0.25), (lat - 0.25, lon + 0.25)]
                    m = self.agent.create_support_mission(
                        self.SUMMON_MISSION_NAME, pts)
                    if m is not None:
                        try:
                            m.mission_active(True)
                        except Exception:
                            pass
                self._summon_mission = m
            if self._summon_mission is not None:
                for i in range(0, len(self._fighter_guids), 10):
                    self.agent.assign_units_to_mission(
                        unit_list=self._fighter_guids[i:i + 10],
                        mission_name=self.SUMMON_MISSION_NAME)
                self._log('info', '已召唤苏-57（%d 机）至编队上空执行护航'
                          % len(self._fighter_guids))
                return True
        except Exception as e:
            self._log('warning', '护航任务创建/分配失败，改用直飞: %s' % e)

        # ② 兜底：直接给苏-57 下一条到编队上空的航线
        try:
            lat, lon = center
            for g in self._fighter_guids:
                obj = self.agent.get_unit(g)
                if obj is not None:
                    obj.plotted_course([(lat, lon)])
            self._log('info', '已直接调度苏-57 飞往编队上空')
            return True
        except Exception as e:
            self._log('error', '召唤苏-57 失败: %s' % e)
            return False

    def _fleet_center(self):
        pts = [(s['lat'], s['lon']) for s in self._ships
               if s.get('lat') is not None and s.get('lon') is not None]
        if not pts:
            return None
        return (sum(p[0] for p in pts) / len(pts),
                sum(p[1] for p in pts) / len(pts))

    # ------------------------------------------------------------------
    # 收尾：威胁解除后归建、恢复雷达
    # ------------------------------------------------------------------
    def _housekeep(self, threats):
        air_near = set(t['near']['guid'] for t in threats
                       if t['cls'] not in ('lucas', 'asm_ground'))
        for ship in self._ships:
            if ship['guid'] in self._evading:
                if ship['guid'] in air_near:
                    self._quiet[ship['guid']] = 0
                else:
                    n = self._quiet.get(ship['guid'], 0) + 1
                    self._quiet[ship['guid']] = n
                    if n >= self.RELEASE_CYCLES:
                        self._stop_evade(ship)
                        self._quiet[ship['guid']] = 0
            # 没有第三类威胁、又不在规避的舰，雷达保持开启
            elif not air_near and self._radar_state.get(ship['guid']) is False:
                self._radar_set(ship, True)

    # ------------------------------------------------------------------
    # 诊断
    # ------------------------------------------------------------------
    def _brief_threats(self, threats):
        if not threats:
            return '无'
        by_cls = {}
        for t in threats:
            by_cls[t['cls']] = by_cls.get(t['cls'], 0) + 1
        first = threats[0]
        return '%s；最近 %s %.0fkm/%s' % (
            by_cls, first['name'][:24], first['dist'],
            first.get('zone', '?'))

    def status(self):
        """返回当前舰队状态，供主智能体打印或赛中核对。"""
        return {
            'cycle': self._cycle,
            'ships': [{'name': s['name'], 'role': s['role'],
                       'dmax': round(s['dmax'], 1), 'ammo': s['ammo'],
                       'zone': self._zone_of_unit(s),
                       'mission': s['mission'],
                       'evading': s['guid'] in self._evading}
                      for s in self._ships],
            'summon_times': self._summon_times,
            'last': self._last_report,
        }


def _to_int(value, default=None):
    try:
        if value is None:
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default
