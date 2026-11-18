# -*- coding:utf-8 -*-
r"""
地空导弹营 / 机动雷达 双模式值班智能体（SAM Battalion + Radar）
================================================================

本模块把原先「没被打就开雷达打、被打就关雷达跑」的二分支循环，改成**人工双模式**
（小窗上的按钮，一个单元一个）：

    地空导弹系统（爱国者 / 地空导弹连 / 霍克）
        机动模式（开局默认）  关雷达 + 全速机动（爱国者、地空导弹连向正北，霍克向正西）
        打击模式              停车 + 开雷达 + 对空自由开火 → 平台自己接战

    可机动雷达
        骗弹模式（开局默认）  停车 + 开雷达（当诱饵，勾反辐射弹）
        机动模式              关雷达 + 全速向正南机动

切换规则（两条任一满足即切回机动模式）：
    ① 操作手在小窗上再按一次该单元的按钮；
    ② 三维监控（``BattlefieldMonitor``）判到有弹指向本单元。

落地细节
    · 平台会拒绝落到水面的航路（``设施不能移动到水面``）。机动航路因此按
      ``MOVE_CANDIDATES`` 从 100km 往近试，第一个被接受的落点为准，
      保证靠海的营也能动起来（会一段一段往前挪）。
    · 铺路爪这类固定雷达按名字跳过（``RADAR_SKIP``），不参与雷达系统。

初始条令（全部地空导弹系统）
    · 对空自由开火（``WeaponControlStatus.Free``）
    · 受攻击时忽略电磁管控 = 否（``IgnoreEMCONUnderAttack.No``）
    · 自动规避 = 否（``AutomaticEvasion.No``）

-------------------------------- 与小窗的约定 --------------------------------
小窗（``灵弈小窗分享(1)/agent/overlay``）是**指令源**，本模块是**执行方**：

* 小窗点按钮 → 覆盖写 ``<状态目录>/sam_intent.json``：:

      {"seq": 12, "cmd": {"<guid>": {"mode": "strike", "ts": 123.4}}}

* 本模块每步读一次，``seq`` 变了就按指令改模式，然后把完整状态写回
  ``<状态目录>/sam_state.json``：:

      {"owner": "agent", "updated": 1763000000.0, "cycle": 7,
       "units": {"<guid>": {"name": "...", "role": "sam"/"radar",
                            "dir": "N"/"W"/"S", "mode": "strike"/"maneuver"/"bait"}}}

  小窗靠这个文件显示每个按钮当前是哪种模式（含被自动切回机动的情况）。

状态目录：``%LOCALAPPDATA%\LingYiOverlay``（可用环境变量 ``LY_SAM_STATE_DIR`` 改）。

接入方法（与原来一致）::

    from engine.LingYi.SamBattalionDefense import SamBattalionDefense
    self.sam_defense = SamBattalionDefense(self, self.monitor)
    # initial(): self.sam_defense.setup(situation)
    # step():    self.sam_defense.step(situation)      # 放在最后，覆盖任务/地面机动给的航路

可调参数（类属性）：
    ``ENABLE=False``                整体关掉；
    ``FIRE_BACKSTOP=False``         不自己补发弹，完全交给平台的自由开火；
    ``PAK_ON_STOP`` / ``MOVE_SPEED`` 停车与全速机动的油门档。

依赖：只依赖平台实体与 ``BattlefieldMonitor``（可选，缺了就用几何自判）。
"""

import json
import logging
import math
import os
import time

__all__ = ["SamBattalionDefense"]

KNOT_TO_KMH = 1.852
NM = 1.852


# ======================================================================
# 小工具
# ======================================================================
def _to_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default=None):
    try:
        if value is None:
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _norm(text):
    """名称归一化：小写、去掉空白与引号括号、去 - . /。"""
    t = str(text or '').lower()
    for ch in (' ', '\u3000', '"', '“', '”', "'", '‘', '’', '(', ')', '（', '）',
               '[', ']', '【', '】', '-', '.', '/', '《', '》'):
        t = t.replace(ch, '')
    return t


def _cget(obj, key, default=None):
    """情报/单元字典取字段，兼容大小写与对象属性三种形态。"""
    if obj is None:
        return default
    for k in (key, key.capitalize(), key.lower(), key.upper()):
        if isinstance(obj, dict):
            if k in obj:
                return obj[k]
        else:
            try:
                if hasattr(obj, k):
                    return getattr(obj, k)
            except Exception:
                pass
    try:
        return obj[key]
    except Exception:
        return default


def _km(lat1, lon1, lat2, lon2):
    """两点大圆距离（公里）。"""
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
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = (math.cos(p1) * math.sin(p2)
         - math.sin(p1) * math.cos(p2) * math.cos(dl))
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def _shift(lat, lon, bearing_deg, dist_km):
    br = math.radians(bearing_deg)
    d = dist_km / 6371.0
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(d)
                   + math.cos(p1) * math.sin(d) * math.cos(br))
    l2 = l1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(p1),
                         math.cos(d) - math.sin(p1) * math.sin(p2))
    return (math.degrees(p2), (math.degrees(l2) + 540.0) % 360.0 - 180.0)


# ======================================================================
# 与小窗共用的状态文件
# ======================================================================
STATE_DIR_ENV = 'LY_SAM_STATE_DIR'
STATE_NAME = 'sam_state.json'
INTENT_NAME = 'sam_intent.json'


def state_dir():
    """小窗与智能体共用的小目录（同一个 Windows 用户下路径一致）。"""
    d = os.environ.get(STATE_DIR_ENV)
    if not d:
        base = (os.environ.get('LOCALAPPDATA')
                or os.environ.get('TEMP')
                or os.path.expanduser('~'))
        d = os.path.join(base, 'LingYiOverlay')
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


def state_path():
    return os.path.join(state_dir(), STATE_NAME)


def intent_path():
    return os.path.join(state_dir(), INTENT_NAME)


def _read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path, data):
    """先写临时文件再替换，避免小窗读到半截 JSON。"""
    tmp = path + '.tmp'
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, path)
        return True
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False


# ======================================================================
# 智能体
# ======================================================================
class SamBattalionDefense(object):
    """地空导弹营 + 可机动雷达 的双模式值班控制。"""

    ENABLE = True

    # ------------------------------------------------------------------
    # 单元识别（名称关键字；想加单元直接往元组里塞词）
    # ------------------------------------------------------------------
    SAM_KEYWORDS = ('爱国者', '地空导弹连', '地空导弹营', '地空导弹排',
                    '地空导弹分队', '霍克', 'patriot', 'hawk', 'sam bty', 'sam coy')
    PATRIOT_KEYWORDS = ('爱国者', 'patriot', 'pac')
    HAWK_KEYWORDS = ('霍克', 'hawk', 'mim-23')
    # 可机动雷达：名字里带这些词、且不是地面固定站
    RADAR_KEYWORDS = ('雷达', 'tpq', 'tps', 'mpq', 'radar')
    RADAR_SKIP = ('固定', 'fixed', '铺路爪', 'fps-115', 'fps115')
    # 想强制排除/纳入某些单元时写名字（子串匹配，归一化后比较）
    RADAR_WHITELIST = ()
    RADAR_BLACKLIST = ()

    # ------------------------------------------------------------------
    # 初始机动方向（度：0=正北，90=正东，180=正南，270=正西）
    # ------------------------------------------------------------------
    DIR_PATRIOT = 0.0
    DIR_SAM = 0.0
    DIR_HAWK = 270.0
    DIR_RADAR = 180.0
    MOVE_KM = 100.0                 # 首选机动距离（落水时自动换短的，见 MOVE_CANDIDATES）
    MOVE_CANDIDATES = (100.0, 80.0, 60.0, 45.0, 30.0, 20.0, 12.0, 6.0)
    MOVE_RETRY_CYCLES = 10          # 一个落点都画不出来时，隔几个周期再试
    MOVE_REISSUE_CYCLES = 10        # 航路跑完之后隔几个周期再补一条

    # ------------------------------------------------------------------
    # 模式
    # ------------------------------------------------------------------
    MODE_STRIKE = 'strike'
    MODE_MANEUVER = 'maneuver'
    MODE_BAIT = 'bait'

    # ------------------------------------------------------------------
    # 条令 / 油门
    # ------------------------------------------------------------------
    WCS_FREE_AIR = True             # 对空自由开火
    IGNORE_EMCON_UNDER_ATTACK = False   # 受攻击时忽略电磁管控：否（False = 不忽略）
    AUTO_EVADE = False              # 自动规避：否
    THROTTLE_MOVE = 'Flank'         # 全速机动
    THROTTLE_STOP = 'FullStop'      # 停车
    RADAR_REASSERT_CYCLES = 10      # 每 N 周期重发一次雷达/油门姿态（自愈）

    # ------------------------------------------------------------------
    # 开火后备（自由开火已由平台接管，这里只是兜底：进 0.6 Dmax 补一条分配）
    # ------------------------------------------------------------------
    FIRE_BACKSTOP = True
    FIRE_RATIO = 0.6
    SALVO_ROUNDS = 2
    REENGAGE_CYCLES = 3
    MIN_ENGAGE_KM = 5.0
    MIN_SAM_RANGE_KM = 5.0
    FALLBACK_RANGE = (
        ('萨德', 150.0), ('thaad', 150.0),
        ('爱国者', 120.0), ('patriot', 120.0), ('pac', 120.0),
        ('天马', 40.0), ('km-sam', 40.0),
        ('霍克', 22.0), ('hawk', 22.0), ('mim-23', 22.0),
    )
    FALLBACK_DMAX_KM = 40.0
    CLOSING_HALF_ANGLE_DEG = 60.0   # 未接监控时判“朝我飞来”的夹角半宽

    # ==================================================================
    def __init__(self, agent, monitor=None, log=None):
        """
        :param agent: 宿主智能体（RuleAgentBase 实例）
        :param monitor: BattlefieldMonitor 实例，提供 has_incoming(guid)
        :param log: callable(level, msg)
        """
        self.agent = agent
        self.monitor = monitor
        self._log_fn = log
        self._cycle = 0

        self._units = []        # [{guid,name,role,dir,obj,dmax,best_wid,ammo,lat,lon}]
        self._mode = {}         # guid -> 'strike' / 'maneuver' / 'bait'
        self._radar_state = {}  # guid -> bool（本地缓存，force 时不用）
        self._emcon_released = set()
        self._doctrine_done = set()
        self._stopped = set()
        self._last_move = {}    # guid -> cycle（上次下机动航路的周期）
        self._move_km = {}      # guid -> 上次被平台接受的机动距离
        self._move_fail = {}    # guid -> 画不出航路的次数（限流告警用）
        self._move_block = {}   # guid -> 上次画航路失败时的周期（失败后先缓几个周期）
        self._applied = {}      # guid -> 上次下发生效的 mode
        self._engage_at = {}    # (guid, cid) -> cycle
        self._contacts = {}
        self._intent_seq = None
        self._last_report = {}
        self._warned = set()
        self._state_written = 0.0
        self._ready = False

    # ------------------------------------------------------------------
    @property
    def ready(self):
        return bool(self._units)

    def _log(self, level, msg):
        fn = self._log_fn
        if not callable(fn):
            fn = getattr(self.agent, '_log', None)
        text = '[地空导弹营] %s' % msg
        if callable(fn):
            try:
                fn(level, text)
                return
            except Exception:
                pass
        getattr(logging, level if level in ('info', 'warning', 'error') else 'info',
                logging.info)(text)

    def _warn_once(self, key, msg, level='warning'):
        if key in self._warned:
            return
        self._warned.add(key)
        self._log(level, msg)

    # ------------------------------------------------------------------
    # 枚举惰性解析（宿主已 from global_util import *）
    # ------------------------------------------------------------------
    def _enum(self, name, member, fallback):
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
        fallback = {'Flank': 5, 'Full': 4, 'Cruise': 3,
                    'Loiter': 2, 'FullStop': 1}.get(member, 3)
        return self._enum('Throttle', member, fallback)

    def _wcs_free(self):
        return self._enum('WeaponControlStatus', 'Free', 0)

    # ==================================================================
    # 一、开局解析 + 初始姿态
    # ==================================================================
    def setup(self, situation):
        """解析受控单元，下发初始条令与初始模式：
        地空导弹 = 机动模式（关雷达 + 全速朝各自方向）；雷达 = 骗弹模式（停车 + 开雷达）。"""
        if not self.ENABLE:
            return {}
        try:
            self._units = self._resolve_units(situation)
        except Exception as e:
            self._log('error', '初始化异常: %s' % e)
            return {}
        self._ready = bool(self._units)
        # 上一次留下的指令文件里的 seq 视为“旧的”，之后只认更大的 seq
        self._intent_seq = _to_int(_read_json(intent_path()).get('seq')) or 0

        # 实验臂：用环境变量指定开局模式（模拟“操作手在开局就把它们切过去”）
        #   PI_SAM_INITIAL = strike         → 地导开局就是打击模式（雷达开、停车、自由开火）
        #   PI_SAM_INITIAL = radar_maneuver → 可机动雷达开局就是机动模式（不诱弹）
        #   不设或为空 = 按正文默认（地导机动、雷达骗弹）
        _init = (os.environ.get('PI_SAM_INITIAL') or '').strip().lower()
        for u in self._units:
            if u['role'] == 'radar':
                _m = self.MODE_MANEUVER if _init == 'radar_maneuver' else self.MODE_BAIT
            else:
                _m = self.MODE_STRIKE if _init == 'strike' else self.MODE_MANEUVER
            self._mode[u['guid']] = _m
            try:
                if u['role'] == 'sam':
                    self._set_doctrines(u)
                self._posture(u, force=True)
                self._log('info', '%s 初始模式：%s'
                          % (u['name'], self._mode_cn(self._mode[u['guid']])))
            except Exception as e:
                self._log('warning', '%s 初始姿态失败: %s' % (u['name'], e))

        rep = {
            '单元数': len(self._units),
            '地空导弹': [u['name'] for u in self._units if u['role'] == 'sam'],
            '雷达': [u['name'] for u in self._units if u['role'] == 'radar'],
            'Dmax': dict((u['name'], round(u['dmax'], 1))
                         for u in self._units if u['role'] == 'sam'),
            '监控': '已接入' if self.monitor is not None else '未接入（自判）',
            '状态文件': state_path(),
        }
        self._log('info', '初始化完成：%s' % rep)
        if not self._units:
            self._log('warning', '未识别到地空导弹/雷达单元（关键字=%s）'
                                 % (self.SAM_KEYWORDS,))
        self._write_state(force=True)
        return rep

    def _resolve_units(self, situation):
        """从态势里挑出地空导弹系统与可机动雷达。"""
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return []
        out = []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            name = str(u.get('name', '') or '')
            if not name:
                continue
            bare = _norm(name)
            role = None
            if any(_norm(k) in bare for k in self.SAM_KEYWORDS):
                role = 'sam'
            elif self._is_radar(name, u):
                role = 'radar'
            if role is None:
                continue
            g = u.get('guid') or guid
            obj = self.agent.get_unit(g)
            if obj is None:
                continue
            item = {
                'name': name, 'guid': g, 'obj': obj, 'role': role,
                'dir': self._dir_of(name, role),
                'lat': _to_float(u.get('lat', u.get('latitude'))),
                'lon': _to_float(u.get('lon', u.get('longitude'))),
                'dmax': 0.0, 'best_wid': None, 'ammo': 0, 'range_src': '',
            }
            if role == 'sam':
                self._probe_weapons(item, u)
            out.append(item)
        out.sort(key=lambda x: (x['role'] != 'sam', x['name']))
        return out

    def _is_radar(self, name, unit_dict):
        bare = _norm(name)
        if any(_norm(k) in bare for k in self.RADAR_SKIP):
            return False
        if self.RADAR_WHITELIST and not any(_norm(k) in bare for k in self.RADAR_WHITELIST):
            return False
        if self.RADAR_BLACKLIST and any(_norm(k) in bare for k in self.RADAR_BLACKLIST):
            return False
        return any(_norm(k) in bare for k in self.RADAR_KEYWORDS)

    def _dir_of(self, name, role):
        """初始机动方向：雷达正南；霍克正西；其余地空导弹正北。"""
        bare = _norm(name)
        if role == 'radar':
            return self.DIR_RADAR
        if any(_norm(k) in bare for k in self.HAWK_KEYWORDS):
            return self.DIR_HAWK
        if any(_norm(k) in bare for k in self.PATRIOT_KEYWORDS):
            return self.DIR_PATRIOT
        return self.DIR_SAM

    def _probe_weapons(self, item, unit_dict):
        """扫出该营全部挂载，逐型查对空射程，取最大者作为 Dmax。"""
        obj = item['obj']
        weapons = {}
        for _m, wid, cnt in self._iter_weapon_recs(obj):
            weapons[wid] = weapons.get(wid, 0) + (cnt or 0)

        best_wid, best_range, best_src = None, None, ''
        for wid in weapons:
            rng = self._weapon_air_range(wid)
            if rng is None or rng < self.MIN_SAM_RANGE_KM:
                continue
            if best_range is None or rng > best_range:
                best_wid, best_range, best_src = wid, rng, '挂载反查'
        if best_wid is None:
            best_range = self._fallback_range(item['name'])
            best_src = '按名称兜底'
            if weapons:
                best_wid = max(weapons.items(), key=lambda kv: kv[1])[0]
            self._log('warning', '[%s] 未能从挂载反查到对空射程（挂载=%s），'
                                 'Dmax 按名称取 %.0f km'
                      % (item['name'], sorted(weapons), best_range))
        item.update({
            'weapons': weapons,
            'best_wid': best_wid,
            'dmax': float(best_range or self.FALLBACK_DMAX_KM),
            'range_src': best_src,
            'ammo': (weapons.get(best_wid, 0) if best_wid else 0),
        })

    def _fallback_range(self, name):
        bare = _norm(name)
        for kw, rng in self.FALLBACK_RANGE:
            if _norm(kw) in bare:
                return rng
        return self.FALLBACK_DMAX_KM

    def _iter_weapon_recs(self, unit):
        """遍历单元挂载（挂架/弹仓/挂载），yield (挂架DBID, 武器DBID, 当前数量)。"""
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

    def _weapon_air_range(self, wid):
        try:
            qd = self._query_data()
            if qd is None:
                return None
            row = qd.get_weapon_info(int(wid))
            if row:
                return _to_float(row[0])
        except Exception:
            pass
        return None

    def _query_data(self):
        try:
            import sys
            for mod_name in ('engine.LingYi.entitys.data', 'entitys.data'):
                mod = sys.modules.get(mod_name)
                if mod is not None and hasattr(mod, 'query_data'):
                    return mod.query_data
            from engine.LingYi.entitys.data import query_data
            return query_data
        except Exception:
            try:
                from entitys.data import query_data
                return query_data
            except Exception:
                return None

    # ==================================================================
    # 二、每周期决策
    # ==================================================================
    def step(self, situation):
        """读小窗指令 → 自动判威胁 → 下发姿态 → 打击模式补发弹。"""
        if not self.ENABLE:
            return {}
        self._cycle += 1
        try:
            if not self._units:
                self.setup(situation)
            if not self._units:
                return {}
            self._contacts = (situation[1] if isinstance(situation, (tuple, list))
                              and len(situation) > 1 and isinstance(situation[1], dict)
                              else {})
            if self.monitor is not None and getattr(self.monitor, 'ready', False):
                self.monitor.ensure(situation)

            self._refresh(situation)
            self._apply_intents()
            acts = []
            for u in self._units:
                try:
                    a = self._tick(u, situation)
                    if a:
                        acts.append(a)
                except Exception as e:
                    self._log('warning', '%s 决策异常: %s' % (u['name'], e))

            if acts or self._cycle % 20 == 0:
                self._log('info', '周期%d：%s' % (self._cycle, acts or '无动作'))
            self._last_report = {'cycle': self._cycle, 'actions': acts}
            self._write_state()
            return self._last_report
        except Exception as e:
            self._log('error', '周期%d 决策异常: %s' % (self._cycle, e))
            return {}

    def _tick(self, u, situation):
        g = u['guid']
        mode = self._mode.get(g, self.MODE_MANEUVER)
        acts = []

        # ① 打击/骗弹模式下被弹盯上 → 立刻切回机动模式
        if mode in (self.MODE_STRIKE, self.MODE_BAIT) and self._threatened(u):
            self._set_mode(u, self.MODE_MANEUVER, why='被瞄准')
            self._write_state(force=True)
            acts.append('%s 被瞄准→切回机动模式' % u['name'])

        # ② 模式变了就立刻把姿态下发到位
        if self._applied.get(g) != self._mode.get(g):
            self._posture(u, force=True)
            acts.append('%s → %s' % (u['name'], self._mode_cn(self._mode.get(g))))
        else:
            # ③ 稳态：定期自愈重发（平台可能被任务/条令改回去）
            if self._cycle % self.RADAR_REASSERT_CYCLES == 0:
                self._posture(u, force=True)
            elif self._mode.get(g) == self.MODE_MANEUVER and self._need_move(u):
                self._move(u)

        # ④ 打击模式：自由开火之外再补一条精确分配（可关）
        if self.FIRE_BACKSTOP and u['role'] == 'sam' \
                and self._mode.get(g) == self.MODE_STRIKE:
            tgt, dist = self._pick_target(u, situation)
            if tgt is not None and dist is not None \
                    and dist <= self.FIRE_RATIO * u['dmax'] \
                    and self._fire(u, tgt, dist):
                acts.append('%s 补射 %s（%.0fkm）' % (u['name'], tgt['name'][:18], dist))
        return '；'.join(acts) if acts else None

    # ------------------------------------------------------------------
    def _refresh(self, situation):
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return
        for u in self._units:
            d = units.get(u['guid'])
            if not isinstance(d, dict):
                for _g, cand in units.items():
                    if isinstance(cand, dict) and \
                            str(cand.get('name', '')) == u['name']:
                        d = cand
                        break
            if isinstance(d, dict):
                u['lat'] = _to_float(d.get('lat', d.get('latitude')), u['lat'])
                u['lon'] = _to_float(d.get('lon', d.get('longitude')), u['lon'])
            if u.get('best_wid') is not None:
                total = 0
                for _m, wid, cnt in self._iter_weapon_recs(u['obj']):
                    if wid == u['best_wid']:
                        total += (cnt or 0)
                u['ammo'] = total

    # ------------------------------------------------------------------
    # 三、小窗指令
    # ------------------------------------------------------------------
    def _apply_intents(self):
        """读小窗写的指令文件；seq 变了就按 guid 改模式。"""
        data = _read_json(intent_path())
        seq = _to_int(data.get('seq'))
        if seq is None or seq <= (self._intent_seq or 0):
            return
        self._intent_seq = seq
        cmds = data.get('cmd') or {}
        if not isinstance(cmds, dict):
            return
        by_guid = dict((u['guid'], u) for u in self._units)
        for guid, c in cmds.items():
            u = by_guid.get(guid)
            if u is None or not isinstance(c, dict):
                continue
            mode = str(c.get('mode') or '')
            allowed = ((self.MODE_STRIKE, self.MODE_MANEUVER) if u['role'] == 'sam'
                       else (self.MODE_BAIT, self.MODE_MANEUVER))
            if mode in allowed:
                self._set_mode(u, mode, why='小窗')
                self._log('info', '%s 操作手切换 → %s' % (u['name'], self._mode_cn(mode)))

    def _set_mode(self, u, mode, why=''):
        g = u['guid']
        old = self._mode.get(g)
        if old == mode:
            return old
        self._mode[g] = mode
        self._log('info', '%s %s → %s（%s）'
                  % (u['name'], self._mode_cn(old), self._mode_cn(mode), why or '切换'))
        return old

    @staticmethod
    def _mode_cn(mode):
        return {SamBattalionDefense.MODE_STRIKE: '打击模式',
                SamBattalionDefense.MODE_BAIT: '骗弹模式',
                SamBattalionDefense.MODE_MANEUVER: '机动模式'}.get(mode, str(mode))

    # ------------------------------------------------------------------
    # 四、姿态下发
    # ------------------------------------------------------------------
    def _posture(self, u, force=False):
        """按当前模式把这个单元的姿态下发到位。"""
        mode = self._mode.get(u['guid'], self.MODE_MANEUVER)
        if mode == self.MODE_STRIKE:
            self._posture_strike(u, force)
        elif mode == self.MODE_BAIT:
            self._posture_stop(u, radar=True, force=force)
        else:
            self._posture_maneuver(u, force)
        self._applied[u['guid']] = mode

    def _posture_maneuver(self, u, force=False):
        """机动模式：关雷达 + 松阵位 + 全速朝初始方向跑。"""
        obj = u['obj']
        self._set_radar(u, False, force=force)
        if force:
            try:
                obj.hold_positon(False)
            except Exception:
                pass
        self._stopped.discard(u['guid'])
        self._move(u, force=force)

    def _posture_strike(self, u, force=False):
        """打击模式：停车 + 保持阵位 + 开雷达 + 对空自由开火。"""
        self._set_doctrines(u)
        self._posture_stop(u, radar=True, force=force)

    def _posture_stop(self, u, radar=True, force=False):
        """停车待命（地面发射车必须停稳才打得准）。"""
        obj = u['obj']
        try:
            obj.clear_plotted_course()
        except Exception:
            pass
        try:
            obj.set_throttle(self._throttle(self.THROTTLE_STOP))
        except Exception as e:
            self._log('warning', '%s 停车失败: %s' % (u['name'], e))
        try:
            obj.set_desired_speed(0)
        except Exception:
            pass
        try:
            obj.hold_positon(True)
        except Exception:
            pass
        self._stopped.add(u['guid'])
        self._set_radar(u, radar, force=force)

    def _move(self, u, force=False):
        """给机动模式补一条朝初始方向的全速航路。

        🔴 平台会拒绝“落到水面”的航路（日志：``设施不能移动到水面``），
           靠海的营按 100km 正北画会直接画到海里、原地不动。所以这里从远到近
           换落点，第一个被平台接受的为准（单位会一段一段往前挪，到一段再画下一段）。
        """
        g = u['guid']
        obj = u['obj']
        if not force:
            try:
                if obj.get_way_points_info():
                    return              # 还有航路，让它先跑完
            except Exception:
                pass
            if self._cycle - self._last_move.get(g, -10 ** 9) < 1:
                return                  # 本周期刚下过，别重复刷指令
            if self._cycle - self._move_block.get(g, -10 ** 9) < self.MOVE_RETRY_CYCLES:
                return                  # 上次一个落点都没画成，先缓一缓
        lat, lon = u.get('lat'), u.get('lon')
        if lat is None or lon is None:
            return
        try:
            tried = []
            good = self._move_km.get(g)
            cands = ([good] if good else []) + [k for k in self.MOVE_CANDIDATES if k != good]
            chosen, why, used_brg = None, '', u['dir']
            for km in cands:
                dest = _shift(lat, lon, u['dir'], float(km))
                ok, why = self._send(obj.plotted_course, [dest])
                tried.append(km)
                if ok:
                    chosen = km
                    break
                if not any(k in (why or '') for k in ('水面', '水域', 'water')):
                    break               # 不是落水的问题，换短也没用
            if chosen is None:          # 正前方全是水（海岸上的雷达/营）：左右斜着走一点
                for off in (45.0, -45.0):
                    for km in (40.0, 20.0):
                        dest = _shift(lat, lon, (u['dir'] + off) % 360.0, float(km))
                        ok, why = self._send(obj.plotted_course, [dest])
                        if ok:
                            chosen, used_brg = km, (u['dir'] + off) % 360.0
                            break
                    if chosen is not None:
                        break
            self._last_move[g] = self._cycle
            if chosen is None:
                self._move_block[g] = self._cycle
                self._move_note(u, why, tried)
                return
            self._move_km[g] = chosen
            self._send(obj.set_throttle, self._throttle(self.THROTTLE_MOVE))
            try:
                obj.hold_positon(False)
            except Exception:
                pass
            self._stopped.discard(g)
            if used_brg == u['dir']:
                dir_txt = self._dir_cn(used_brg)
            else:
                dir_txt = '正前方是水，偏 %+.0f°' % ((used_brg - u['dir'] + 180.0) % 360.0 - 180.0)
            self._log('info', '%s 进入机动：航向 %.0f°（%s），全速%s，%.0fkm'
                      % (u['name'], used_brg, dir_txt,
                         '' if len(tried) <= 1 else '（前 %d 个落点落水已换短）' % (len(tried) - 1),
                         chosen))
        except Exception as e:
            self._log('warning', '%s 机动航路失败: %s' % (u['name'], e))

    def _move_note(self, u, why, tried):
        """画不出航路时的告警（限流，别每周期刷屏）。"""
        g = u['guid']
        n = self._move_fail.get(g, 0) + 1
        self._move_fail[g] = n
        if n in (1, 5, 20, 60):
            self._log('warning', '%s 画不出机动航路（方向 %.0f°，试过 %s km；平台回：%s），第 %d 次'
                      % (u['name'], u['dir'], '/'.join('%.0f' % k for k in tried),
                         (why or '')[:60], n))

    def _need_move(self, u):
        """机动模式下航路跑完了就补一条。"""
        try:
            return not u['obj'].get_way_points_info()
        except Exception:
            return False

    @staticmethod
    def _dir_cn(brg):
        names = {(0, 45): '正北', (45, 135): '正东', (135, 225): '正南',
                 (225, 315): '正西', (315, 360): '正北'}
        b = brg % 360.0
        for (lo, hi), name in names.items():
            if lo <= b < hi:
                return name
        return '%.0f°' % b

    # ------------------------------------------------------------------
    # 五、条令 / 雷达
    # ------------------------------------------------------------------
    def _set_doctrines(self, u):
        """对空自由开火 + 受攻击不忽略电磁管控 + 自动规避否（每单元下发一次）。"""
        g = u['guid']
        if g in self._doctrine_done:
            return
        obj = u['obj']
        ok = True
        try:
            obj.doctrine_weapon_control_status_air(self._wcs_free())
        except Exception as e:
            ok = False
            self._log('warning', '%s 设对空自由开火失败: %s' % (u['name'], e))
        try:
            obj.doctrine_ignore_emcon_under_attack(
                self._enum('IgnoreEMCONUnderAttack',
                           'Ignore_EMCON_While_Under_Attack'
                           if self.IGNORE_EMCON_UNDER_ATTACK else 'No',
                           1 if self.IGNORE_EMCON_UNDER_ATTACK else 0))
        except Exception as e:
            ok = False
            self._log('warning', '%s 设“受攻击忽略电磁管控”失败: %s' % (u['name'], e))
        try:
            obj.doctrine_automatic_evasion(
                self._enum('AutomaticEvasion',
                           'Yes' if self.AUTO_EVADE else 'No',
                           1 if self.AUTO_EVADE else 0))
        except Exception as e:
            ok = False
            self._log('warning', '%s 设“自动规避”失败: %s' % (u['name'], e))
        if ok:
            self._doctrine_done.add(g)
            self._log('info', '%s 条令：对空自由开火 / 受攻击不忽略电磁管控 / 自动规避否'
                      % u['name'])

    def _set_radar(self, u, on, force=False):
        """雷达开关；force=True 不看缓存强制下发（切换姿态时必须强发）。"""
        if not force and self._radar_state.get(u['guid']) is on:
            return
        obj = u['obj']
        try:
            if u['guid'] not in self._emcon_released:
                try:
                    obj.EMCON_Obey_doctrine(False)
                    self._emcon_released.add(u['guid'])
                except Exception:
                    pass
            res = obj.switch_radar(bool(on))
            if self._reply_ok(res) or res is None:
                self._radar_state[u['guid']] = bool(on)
                self._log('info', '%s 雷达%s%s'
                          % (u['name'], '开' if on else '关',
                             '（重发）' if force else ''))
        except Exception as e:
            self._log('warning', '%s 雷达开关失败: %s' % (u['name'], e))

    # ------------------------------------------------------------------
    # 六、威胁判定
    # ------------------------------------------------------------------
    def _threatened(self, u):
        """是否有弹指向本单元（有监控用监控，没有就几何自判）。"""
        if self.monitor is not None and getattr(self.monitor, 'ready', False):
            try:
                return bool(self.monitor.has_incoming(u['guid']))
            except Exception:
                return False

        gate = 1.5 * (u.get('dmax') or self.FALLBACK_DMAX_KM)
        lat, lon = u.get('lat'), u.get('lon')
        if lat is None or lon is None:
            return False
        for _cid, c in (self._contacts or {}).items():
            if _to_int(_cget(c, 'Type')) != 1:
                continue
            clat = _to_float(_cget(c, 'Lat'))
            clon = _to_float(_cget(c, 'Lon'))
            d = _km(clat, clon, lat, lon)
            if d is None or d > gate:
                continue
            hdg = _to_float(_cget(c, 'CurrentHeading'))
            if hdg is None:
                return True
            brg = _bearing(clat, clon, lat, lon)
            diff = abs((hdg - brg + 180.0) % 360.0 - 180.0)
            if diff <= self.CLOSING_HALF_ANGLE_DEG:
                return True
        return False

    # ------------------------------------------------------------------
    # 七、目标选择与补射
    # ------------------------------------------------------------------
    def _pick_target(self, u, situation):
        contacts = situation[1] if isinstance(situation, (tuple, list)) \
            and len(situation) > 1 else {}
        if not isinstance(contacts, dict):
            return None, None
        own_ids, own_names = self._own_index(situation)
        best, best_d = None, None
        for cid, c in contacts.items():
            if not self._is_enemy_air(c, own_ids, own_names):
                continue
            lat = _to_float(_cget(c, 'Lat'))
            lon = _to_float(_cget(c, 'Lon'))
            if lat is None or lon is None:
                continue
            d = _km(lat, lon, u.get('lat'), u.get('lon'))
            if d is None or d < self.MIN_ENGAGE_KM:
                continue
            if best_d is None or d < best_d:
                best_d = d
                best = {'cid': _cget(c, 'ID', cid) or cid,
                        'name': str(_cget(c, 'Name', '') or ''), 'dist': d}
        return best, best_d

    def _own_index(self, situation):
        ids, names = set(), set()
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if isinstance(units, dict):
            for g, u in units.items():
                if not isinstance(u, dict):
                    continue
                ids.add(u.get('guid') or g)
                nm = str(u.get('name', '') or '')
                if nm:
                    names.add(_norm(nm))
        return ids, names

    def _is_enemy_air(self, c, own_ids, own_names):
        ctype = _to_int(_cget(c, 'Type'))
        if ctype is not None and ctype != 0:
            return False
        actual = _cget(c, 'ActualUnitID')
        if actual and actual in own_ids:
            return False
        nm = str(_cget(c, 'Name', '') or '')
        if nm and _norm(nm) in own_names:
            return False
        alt = _to_float(_cget(c, 'CurrentAltitude'), 0.0) or 0.0
        if alt < 50.0:
            return False
        return True

    def _fire(self, u, target, dist):
        key = (u['guid'], target['cid'])
        last = self._engage_at.get(key)
        if last is not None and self._cycle - last < self.REENGAGE_CYCLES:
            return False
        obj = u['obj']
        wid = u.get('best_wid')
        ok = False
        try:
            if wid is not None:
                ok = self._reply_ok(obj.attack_weapon_allocate_to_target(
                    target['cid'], int(wid), int(self.SALVO_ROUNDS)))
            if not ok:
                ok = self._reply_ok(obj.attack_auto(target['cid']))
        except Exception as e:
            self._log('error', '%s 发弹异常: %s' % (u['name'], e))
            return False
        if ok:
            self._engage_at[key] = self._cycle
            self._log('info', '%s 拦截[%s] 距离%.0fkm 弹数%d 弹种%s'
                      % (u['name'], target['name'], dist,
                         self.SALVO_ROUNDS, wid))
        else:
            self._warn_once('%s|firefail' % u['guid'],
                            '%s 发弹被拒（可能弹药耗尽或目标已失效）' % u['name'])
        return ok

    def _send(self, fn, *args):
        """下一条指令并对回执判成败；网络原因（回执里带“网络/超时”）重试一次。"""
        why = ''
        for i in range(2):
            try:
                res = fn(*args)
            except Exception as e:
                return False, '异常 %s' % e
            if self._reply_ok(res):
                return True, self._reply_text(res)
            why = self._reply_text(res)
            if '网络' not in why and '超时' not in why:
                break
            time.sleep(0.05)
        return False, why

    @staticmethod
    def _reply_text(res):
        raw = getattr(res, 'result', res)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode('utf-8', 'replace')
            except Exception:
                raw = str(raw)
        return str(raw or '')

    @staticmethod
    def _reply_ok(res):
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

    # ------------------------------------------------------------------
    # 八、状态发布（给小窗显示）
    # ------------------------------------------------------------------
    def _write_state(self, force=False):
        now = time.time()
        if not force and now - self._state_written < 2.0:
            return
        self._state_written = now
        units = {}
        for u in self._units:
            units[u['guid']] = {
                'name': u['name'],
                'role': u['role'],
                'dir': self._dir_letter(u['dir']),
                'mode': self._mode.get(u['guid'], self.MODE_MANEUVER),
                'cycle': self._cycle,
            }
        _write_json(state_path(), {
            'owner': 'agent',
            'updated': round(now, 3),
            'cycle': self._cycle,
            'units': units,
        })

    @staticmethod
    def _dir_letter(brg):
        b = brg % 360.0
        if b < 45 or b >= 315:
            return 'N'
        if b < 135:
            return 'E'
        if b < 225:
            return 'S'
        return 'W'

    # ------------------------------------------------------------------
    def status(self):
        return {
            'cycle': self._cycle,
            'state_file': state_path(),
            'units': [{'name': u['name'], 'guid': u['guid'], 'role': u['role'],
                       'mode': self._mode.get(u['guid']),
                       'dir': self._dir_letter(u['dir']),
                       'dmax': round(u.get('dmax') or 0.0, 1),
                       'range_src': u.get('range_src'),
                       'best_wid': u.get('best_wid'),
                       'ammo': u.get('ammo'),
                       'radar': self._radar_state.get(u['guid'])}
                      for u in self._units],
            'last': self._last_report,
        }
