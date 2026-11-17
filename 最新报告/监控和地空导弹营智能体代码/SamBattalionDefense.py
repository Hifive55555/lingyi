# -*- coding:utf-8 -*-
r"""
地空导弹营攻击与自卫智能体（SAM Battalion）
==============================================
规则型智能体，独立模块。设计依据：设计报告 2.3.5 节。

规则本体（报告代码 8）
----------------------
每步调用::

    if 物理作战域三维监控(本营) 返回来袭弹:
        关闭雷达()      # 减小被反辐射武器锁定的概率
        加速脱离()      # 抬高本营的生存概率
    else:
        开雷达()        # 恢复探测
        自由开火()      # 条令设为对空自由开火
        停车()          # 停车待命（地面发射车必须停稳才能打）
        if 目标距离 <= 0.6 * D_max:
            发弹()

**二分支循环**：被打就关雷达跑，没被打就开雷达、放手、停车、等目标进 0.6 Dmax 再打。
这个比例在报告里叫 3/5 Dmax，几何含义是"内圈发弹线、外圈最大拦截边界"，两圈之间
是能量裕度。报告 2.3.5 用能量模型算过：综合拦截概率在 0.3 Dmax 最高（0.981），到
1.0 Dmax 降为 0，现行 3/5 Dmax 为 0.915。

两条**强绑定**（报告的写法本身就是一条动作，不能拆开执行）
----------------------------------------------------------
* **停车 ⇔ 开雷达**：停车是为了稳定发射，开雷达是为了探测；只停不开等于瞎停。
  所以值班姿态里两者成对下发——状态切换的当周期强制补一次开雷达，稳态每
  ``RADAR_REASSERT_CYCLES`` 个周期再强制重发一次（防平台/任务把雷达重置）。
* **逃跑 ⇔ 关雷达**：边跑边辐射等于给反辐射弹指路。进入规避的那一周期必定先
  下发关雷达，再松阵位、规划斜后方航路、加力；规避期间也定期重发"关雷达"。

本地雷达状态是缓存，平台侧可能被任务条令/EMCON 重置，所以这两处都走
``force=True`` 强制下发，不看缓存——实测的"停了但雷达没开"就是这么来的。

本实现的范围（按用户指定）
--------------------------
* 受控单元：``地空导弹连 #1``、``地空导弹连 #2``、``爱国者地空导弹连 #1``、
  ``爱国者地空导弹连 #2``（关键字 ``地空导弹连`` 即可覆盖四个）。
* 武器：**该单元挂载的全部武器**。不写死弹种——运行期扫 Mounts / Magazines /
  Loadouts 拿到真实挂载，逐型查 ``AirRangeMax``，取最大者作为 Dmax；开火时用
  对空射程最远的那一型（可用 ``attack_weapon_allocate_to_target`` 精确指定）。
  查不到射程时按目标名兜底（爱国者 120 km、其余 40 km），并在日志里标出来。

为什么必须运行期反查：model.db 里"设施→挂架→武器"的对应关系并不作准（实测
爱国者 PAC-2 的挂架 962 在库里映射到 998「AGM-69A 斯哈姆核弹」），只有态势里
单元自己的 Mounts/WeaponRecs 才是真挂载。

依赖
----
"是否有弹指向本营"由 ``BattlefieldMonitor`` 判定（报告 2.3.1 的唯一信息源）；
没接监控时退化为"按来袭弹当前距离筛选"，便于离线测试。

接入方法
--------
::

    from engine.LingYi.SamBattalionDefense import SamBattalionDefense

    def __init__(self, side_name, params=None):
        ...
        self.sam_defense = SamBattalionDefense(self)          # 或传 monitor

    def initial(self, situation):
        ...
        self.sam_defense.setup(situation)

    def step(self, time_elapse, situation):
        ...
        self.sam_defense.step(situation)

可调参数（类属性，改一个词即可回退）：

* ``ENABLE = False``          整体关掉；
* ``PARK_ON_IDLE = False``    不要求停车（只开雷达与自由开火）；
* ``FIRE_RATIO = 0.6``        发弹线（占 Dmax 的比例）；
* ``SALVO_ROUNDS = 2``        每次拦截分配几发。
"""

import logging
import math

__all__ = ["SamBattalionDefense"]

KNOT_TO_KMH = 1.852


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
# 智能体
# ======================================================================
class SamBattalionDefense(object):
    """地空导弹营攻击与自卫智能体。"""

    ENABLE = True

    # ------------------------------------------------------------------
    # 受控单元：四个防空连（关键字 '地空导弹连' 同时覆盖
    #   「地空导弹连#1/#2」与「爱国者地空导弹连#1/#2」）
    # ------------------------------------------------------------------
    SAM_KEYWORDS = ('地空导弹连', '地空导弹营', '地空导弹排', '地空导弹分队',
                    'sam bty', 'sam coy')

    # ------------------------------------------------------------------
    # 开火判据（报告 2.3.5：3/5 Dmax）
    # ------------------------------------------------------------------
    FIRE_RATIO = 0.6                 # 目标距离 <= 0.6 * Dmax 才发弹
    SALVO_ROUNDS = 2                 # 每次拦截分配几发
    REENGAGE_CYCLES = 3              # 同一 (营, 目标) 的最短重发间隔（周期）
    MIN_ENGAGE_KM = 5.0              # 太近也不打（已进入近防/来不及）
    MIN_SAM_RANGE_KM = 5.0           # 判定"这型弹算对空弹"的最低对空射程

    # 射程查不到时按目标名兜底（km）
    FALLBACK_RANGE = (
        ('萨德', 150.0), ('thaad', 150.0),
        ('爱国者', 120.0), ('patriot', 120.0), ('pac', 120.0),
        ('天马', 40.0), ('km-sam', 40.0),
        ('霍克', 22.0), ('hawk', 22.0), ('mim-23', 22.0),
    )
    FALLBACK_DMAX_KM = 40.0

    # ------------------------------------------------------------------
    # 自卫机动
    # ------------------------------------------------------------------
    EVADE_KM = 15.0                  # 脱离时规划的航程
    EVADE_ANGLE_DEG = 135.0          # 斜后方（背身脱离）
    EVADE_SPEED_KMH = 50.0           # 期望速度（地面单元上限约 55.6，留余量）
    RELEASE_CYCLES = 2               # 连续多少周期无来袭弹才恢复战斗状态（60s）
    CLOSING_HALF_ANGLE_DEG = 60.0    # 未接监控时判"朝我飞来"的夹角半宽
    EVADE_MAX_CYCLES = 20            # 连续规避上限（20×30s=10min）；<=0 关闭兜底
    PARK_ON_IDLE = True              # 未被打时是否要求停车待命
    # 未被打时是否强制开雷达（报告 2.3.5 的"开雷达"）。
    #   蓝方原设计是"开局关雷达"以躲避反辐射武器；若想保留那个行为，
    #   把这里改成 False —— 此时雷达状态交回任务/条令，本智能体只在被打时关。
    RADAR_ON_IDLE = True
    RADAR_REASSERT_CYCLES = 10       # 每 N 周期重发一次"开雷达"（自愈）
    RETURN_TO_POST = False           # 威胁解除后是否回原阵位（默认原地停车）

    # ==================================================================
    def __init__(self, agent, monitor=None, log=None):
        """
        :param agent: RuleBased 实例（宿主智能体）
        :param monitor: BattlefieldMonitor 实例（提供"是否有弹指向本营"）
        :param log: callable(level, msg)
        """
        self.agent = agent
        self.monitor = monitor
        self._log_fn = log
        self._cycle = 0

        self._battalions = []       # [{'name','guid','obj','weapons','best_wid',
                                    #   'dmax','range_src','lat','lon'}]
        self._state = {}            # guid -> 'idle' / 'evade'
        self._quiet = {}            # guid -> 连续无来袭弹的周期数
        self._engage_at = {}        # (guid, target_id) -> cycle
        self._radar_state = {}      # guid -> bool
        self._emcon_released = set()
        self._free_fire_done = set()
        self._parked = set()
        self._evading = {}          # guid -> {'post': (lat,lon), 'since': cycle}
        self._summon_ok = False
        self._contacts = {}         # 本周期情报快照（供取证/兜底判定）
        self._last_report = {}
        self._warned = set()

    # ------------------------------------------------------------------
    @property
    def ready(self):
        return bool(self._battalions)

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
    # 一、开局解析
    # ==================================================================
    def setup(self, situation):
        """解析四个防空连，逐营读出真实挂载与对空射程。"""
        if not self.ENABLE:
            return {}
        try:
            self._battalions = self._resolve_battalions(situation)
        except Exception as e:
            self._log('error', '初始化异常: %s' % e)
            return {}

        rep = {
            '防空营数': len(self._battalions),
            'Dmax': dict((b['name'], round(b['dmax'], 1)) for b in self._battalions),
            '射程来源': dict((b['name'], b['range_src']) for b in self._battalions),
            '监控': '已接入' if self.monitor is not None else '未接入（自判）',
        }
        self._log('info', '初始化完成：%s' % rep)
        if not self._battalions:
            self._log('warning', '未解析到地空导弹连（关键字=%s）'
                                 % (self.SAM_KEYWORDS,))
        return rep

    def _resolve_battalions(self, situation):
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return []
        out = []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            name = str(u.get('name', '') or '')
            bare = _norm(name)
            if not any(_norm(k) in bare for k in self.SAM_KEYWORDS):
                continue
            g = u.get('guid') or guid
            obj = self.agent.get_unit(g)
            if obj is None:
                continue
            out.append(self._probe_battalion(name, g, obj, u))
        out.sort(key=lambda b: b['name'])
        return out

    def _probe_battalion(self, name, guid, obj, unit_dict):
        """
        探测单营：扫出**全部挂载武器**，逐型查对空射程，取最大者作为 Dmax。

        注意：不写死弹种。平台库里"设施→挂架→武器"的映射不作准，只有单元
        自己的 Mounts / Magazines / Loadouts 才是真挂载。
        """
        weapons = {}                    # wid -> 当前数量
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
            best_range, best_src = self._fallback_range(name), '按名称兜底'
            # 兜底时仍优先用挂载里"数量最多"的那型弹开火
            if weapons:
                best_wid = max(weapons.items(), key=lambda kv: kv[1])[0]
            self._log('warning', '[%s] 未能从挂载反查到对空射程（挂载=%s），'
                                 'Dmax 按名称取 %.0f km'
                      % (name, sorted(weapons), best_range))

        return {
            'name': name, 'guid': guid, 'obj': obj,
            'weapons': weapons,             # 该营挂载的全部武器
            'best_wid': best_wid,           # 用于开火的那型弹
            'dmax': float(best_range),
            'range_src': best_src,
            'ammo': (weapons.get(best_wid, 0) if best_wid else 0),
            'lat': _to_float(unit_dict.get('lat', unit_dict.get('latitude'))),
            'lon': _to_float(unit_dict.get('lon', unit_dict.get('longitude'))),
        }

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
        """查某型弹的对空最大射程（km）；查不到返回 None。"""
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
        """
        二分支循环：被瞄准 → 关雷达+脱离；否则 → 开雷达+自由开火+停车+择机发弹。

        :return: dict, 本周期的决策摘要
        """
        if not self.ENABLE:
            return {}
        self._cycle += 1
        try:
            if not self._battalions:
                self.setup(situation)
            if not self._battalions:
                return {}
            self._contacts = situation[1] if isinstance(situation, (tuple, list)) \
                and len(situation) > 1 and isinstance(situation[1], dict) else {}
            if self.monitor is not None and getattr(self.monitor, 'ready', False):
                self.monitor.ensure(situation)

            self._refresh(situation)
            acts = []
            for b in self._battalions:
                # 兜底：规避太久就强制恢复值班（防止判据卡住导致整局逃跑）
                if self._evade_expired(b):
                    acts.append(self._recover_expired(b))
                elif self._threatened(b):
                    acts.append(self._defend(b))
                else:
                    acts.append(self._attack(b, situation))
            acts = [a for a in acts if a]

            if acts or self._cycle % 20 == 0:
                self._log('info', '周期%d：%s' % (self._cycle, acts or '无动作'))
            self._last_report = {'cycle': self._cycle, 'actions': acts}
            return self._last_report
        except Exception as e:
            self._log('error', '周期%d 决策异常: %s' % (self._cycle, e))
            return {}

    def _refresh(self, situation):
        """刷新各营位置与余弹（态势是权威来源）。"""
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return
        for b in self._battalions:
            u = units.get(b['guid'])
            if not isinstance(u, dict):
                for _g, cand in units.items():
                    if isinstance(cand, dict) and \
                            str(cand.get('name', '')) == b['name']:
                        u = cand
                        break
            if isinstance(u, dict):
                b['lat'] = _to_float(u.get('lat', u.get('latitude')), b['lat'])
                b['lon'] = _to_float(u.get('lon', u.get('longitude')), b['lon'])
            if b['best_wid'] is not None:
                total = 0
                for _m, wid, cnt in self._iter_weapon_recs(b['obj']):
                    if wid == b['best_wid']:
                        total += (cnt or 0)
                b['ammo'] = total

    # ------------------------------------------------------------------
    # 判据
    # ------------------------------------------------------------------
    def _threatened(self, b):
        """
        是否有弹**指向本营**。

        🔴 有监控时以监控为**唯一**判据（报告 2.3.1），不要再叠加"附近有弹"
           的兜底：否则只要战场上还有别处的弹在飞（哪怕打的是别人），本营就
           会一直被判定为"被打"，进入规避后**永远不恢复**——实测表现就是
           "地空导弹连一直在逃跑"。这是本函数第一版的真实缺陷。

        没有监控时才退化为几何自判：来袭弹在 1.5*Dmax 内，**且航向指向本营**
        （与"弹→本营"方位的夹角不超过 CLOSING_HALF_ANGLE_DEG）。

        :return: bool
        """
        if self.monitor is not None and getattr(self.monitor, 'ready', False):
            try:
                return bool(self.monitor.has_incoming(b['guid']))
            except Exception:
                return False

        # —— 以下仅在未接入监控时使用 ——
        gate = 1.5 * (b.get('dmax') or self.FALLBACK_DMAX_KM)
        blat, blon = b.get('lat'), b.get('lon')
        if blat is None or blon is None:
            return False
        for _cid, c in (self._contacts or {}).items():
            if _to_int(_cget(c, 'Type')) != 1:
                continue
            lat = _to_float(_cget(c, 'Lat'))
            lon = _to_float(_cget(c, 'Lon'))
            d = _km(lat, lon, blat, blon)
            if d is None or d > gate:
                continue
            hdg = _to_float(_cget(c, 'CurrentHeading'))
            if hdg is None:
                return True                 # 没航向，只能按距离算
            brg = _bearing(lat, lon, blat, blon)
            diff = abs((hdg - brg + 180.0) % 360.0 - 180.0)
            if diff <= self.CLOSING_HALF_ANGLE_DEG:
                return True
        return False

    # ------------------------------------------------------------------
    # 分支一：被打 → 关雷达 + 加速脱离
    # ------------------------------------------------------------------
    def _evade_expired(self, b):
        """
        规避是否已经太久（兜底闸门）。

        正常路径是靠"连续 RELEASE_CYCLES 周期无威胁"退出规避；但若判据因任何
        原因卡在"一直被瞄准"，单元就会整局逃跑、再也不开雷达。这里加一道硬
        上限：连续规避超过 EVADE_MAX_CYCLES 个周期，强制恢复一次值班
        （开雷达 + 停车）。若威胁是真的，下个周期会立刻重新规避——等于一次
        雷达闪亮，代价很小；若威胁是假的，它就此归位。``<= 0`` 表示关闭该闸门。
        """
        if self.EVADE_MAX_CYCLES <= 0:
            return False
        st = self._evading.get(b['guid'])
        if not st:
            return False
        return (self._cycle - st.get('since', self._cycle)) >= self.EVADE_MAX_CYCLES

    def _recover_expired(self, b):
        """规避超时：强制恢复值班并告警（便于赛后定位判据问题）。"""
        st = self._evading.get(b['guid']) or {}
        self._log('warning', '%s 已连续规避 %d 周期，强制恢复值班'
                            '（若威胁仍在，下周期会重新规避）'
                  % (b['name'], self._cycle - st.get('since', self._cycle)))
        self._recover(b)
        self._quiet[b['guid']] = 0
        return '%s 规避超时→强制恢复' % b['name']

    def _defend(self, b):
        """
        被打：**关雷达 + 松阵位 + 加力脱离**（三者绑定，见 _start_evade）。

        🔴 绑定关系：报告 2.3.5 的"被打"分支就是"关雷达 + 加速脱离"一条动作。
           雷达必须一关就走、一走就关——边跑边辐射等于给反辐射弹指路。
        """
        self._quiet[b['guid']] = 0
        if b['guid'] not in self._evading:
            self._start_evade(b)
            self._state[b['guid']] = 'evade'
            return '%s 被瞄准→关雷达+加速脱离' % b['name']

        # 已经在规避：定期重发"关雷达"，防止被平台/任务重置成开机
        if self._cycle % self.RADAR_REASSERT_CYCLES == 0:
            self._radar_set(b, False, force=True)
        # 每 10 个周期打一条提醒，便于分辨"确实一直被瞄准"还是"判据卡住了"
        st = self._evading.get(b['guid']) or {}
        n = self._cycle - st.get('since', self._cycle)
        if n and n % 10 == 0:
            self._log('warning', '%s 已连续规避 %d 周期（%s 仍判为被瞄准）'
                      % (b['name'], n,
                         '监控' if self.monitor is not None else '几何自判'))
        return None

    def _start_evade(self, b):
        """记录原阵位 → 关雷达 → 松阵位 → 斜后方航路 → 加力脱离（一次做全）。"""
        obj = b['obj']
        post = (b.get('lat'), b.get('lon'))
        try:
            # ① 关雷达：与"脱离"绑定，必须先关
            self._radar_set(b, False, force=True)
            # ② 松开保持阵位
            try:
                obj.hold_positon(False)
            except Exception:
                pass
            # ③ 规划斜后方航路
            lat, lon = b.get('lat'), b.get('lon')
            heading = self._threat_bearing(b) if lat is not None else None
            if lat is not None and heading is not None:
                esc = (heading + 180.0 + self.EVADE_ANGLE_DEG) % 360.0
                pt = _shift(lat, lon, esc, self.EVADE_KM)
                obj.plotted_course([pt])
            # ④ 加力
            obj.set_throttle(self._throttle('Flank'))
            try:
                obj.set_desired_speed(self.EVADE_SPEED_KMH)
            except Exception:
                pass
            self._evading[b['guid']] = {'post': post, 'since': self._cycle}
            self._parked.discard(b['guid'])
            self._log('info', '%s 脱离中（原阵位 %s，雷达已关）' % (b['name'], post))
        except Exception as e:
            self._log('warning', '%s 脱离机动失败: %s' % (b['name'], e))

    def _threat_bearing(self, b):
        """
        来袭弹的大致方位（度）。规避方向要背对它。

        ① 有监控：用监控给的最紧迫那枚弹的情报 id 反查坐标；
        ② 无监控：从情报里挑"最近且朝我飞来"的那枚。
        """
        blat, blon = b.get('lat'), b.get('lon')
        if blat is None or blon is None:
            return None

        if self.monitor is not None and getattr(self.monitor, 'ready', False):
            try:
                rows = self.monitor.threats_for(b['guid'])
                if rows:
                    contact = self._contact_by_id(rows[0].get('cid'))
                    if contact is not None:
                        lat = _to_float(_cget(contact, 'Lat'))
                        lon = _to_float(_cget(contact, 'Lon'))
                        if lat is not None and lon is not None:
                            return _bearing(lat, lon, blat, blon)
            except Exception:
                pass

        # 无监控（或监控没给到坐标）：自己从情报里挑最近的来袭弹
        best, best_d = None, None
        for _i, c in (self._contacts or {}).items():
            if _to_int(_cget(c, 'Type')) != 1:
                continue
            lat = _to_float(_cget(c, 'Lat'))
            lon = _to_float(_cget(c, 'Lon'))
            d = _km(lat, lon, blat, blon)
            if d is None:
                continue
            if best_d is None or d < best_d:
                best_d, best = d, (lat, lon)
        if best is None:
            return None
        return _bearing(best[0], best[1], blat, blon)

    def _contact_by_id(self, cid):
        if cid is None:
            return None
        for _i, c in (self._contacts or {}).items():
            if (_cget(c, 'ID', _i) or _i) == cid:
                return c
        return None

    # ------------------------------------------------------------------
    # 分支二：未被打 → 开雷达 + 自由开火 + 停车 + 择机发弹
    # ------------------------------------------------------------------
    def _attack(self, b, situation):
        acts = []
        # ① 恢复战斗状态（从回避转回）
        if b['guid'] in self._evading:
            n = self._quiet.get(b['guid'], 0) + 1
            self._quiet[b['guid']] = n
            if n < self.RELEASE_CYCLES:
                return None
            self._recover(b)
            acts.append('%s 威胁解除→停车+开雷达' % b['name'])

        # ② 维持"停车 + 开雷达 + 自由开火"的值班姿态（三者绑定）
        self._maintain_combat(b)

        # ③ 目标距离 <= 0.6 Dmax 才发弹
        target, dist = self._pick_target(b, situation)
        if target is None:
            return '；'.join(acts) if acts else None
        line = self.FIRE_RATIO * b['dmax']
        if dist > line:
            if self._cycle % 10 == 0:       # 待机状态限流，避免每周期刷屏
                return '；'.join(acts + ['%s 目标%.0fkm>%.0fkm 待机'
                                         % (b['name'], dist, line)])
            return '；'.join(acts) if acts else None
        if self._fire(b, target, dist):
            acts.append('%s 发弹→%s(%.0fkm/发弹线%.0fkm)'
                        % (b['name'], target['name'][:20], dist, line))
        return '；'.join(acts) if acts else None

    def _recover(self, b):
        """
        退出规避：**先清掉规避航路** → 原地停车 → 开雷达，恢复防空值班。

        🔴 必须清航路：规避时下过一条 15 km 的航路，若不清掉，
           "油门已停 + 航路还在" 会让单元继续朝规避点跑；而且 ``_park()``
           见还有航路就跳过，于是永远停不下来。
        """
        st = self._evading.pop(b['guid'], None)
        self._state[b['guid']] = 'idle'
        obj = b['obj']
        try:
            if self.RETURN_TO_POST and st and st.get('post') and \
                    None not in st['post']:
                obj.plotted_course([st['post']])
                self._log('info', '%s 返回原阵位 %s' % (b['name'], st['post']))
            else:
                try:
                    obj.clear_plotted_course()
                except Exception:
                    pass
            obj.set_throttle(self._throttle('FullStop'))
            try:
                obj.set_desired_speed(0)
            except Exception:
                pass
            try:
                obj.hold_positon(True)
            except Exception:
                pass
            self._parked.add(b['guid'])     # 已停车，_park 不必再发
            self._log('info', '%s 威胁解除→停车+开雷达，恢复防空值班' % b['name'])
        except Exception as e:
            self._log('warning', '%s 恢复失败: %s' % (b['name'], e))
        self._state[b['guid']] = 'combat'
        # 停车与开雷达绑定：切换的这一刻强制下发，不依赖缓存
        self._radar_set(b, True, force=True)

    def _maintain_combat(self, b):
        """
        维持"停车 + 开雷达 + 自由开火"的值班姿态（三者绑定）。

        🔴 为什么必须绑定：报告 2.3.5 把"停车"和"开雷达"写在同一个分支——
           停车是为了稳定发射，开雷达是为了探测；只停不开等于瞎停，
           只开不停等于边跑边辐射。实测出现过"停了但雷达没开"，根因是雷达
           状态用本地缓存去重，平台那边被任务/条令重置后我们以为还开着。
           所以：停车走到位的同一周期一定补一次开雷达；稳态下每
           RADAR_REASSERT_CYCLES 个周期强制重发一次。
        """
        self._set_free_fire(b)
        if self.PARK_ON_IDLE:
            self._park(b)
        if self.RADAR_ON_IDLE:
            force = (self._cycle % self.RADAR_REASSERT_CYCLES == 0)
            self._radar_set(b, True, force=force)

    def _park(self, b, force=False):
        """
        停车待命（地面发射车必须停稳才能开火）。

        ⚠️ 默认只在**已经到位**（无剩余航路）时才停车：蓝方的防空连开局可能正被
        支援任务带着转移阵位，这时停车会把部署卡在半路。有航路就让它先走完。
        ``force=True`` 用于"刚从规避状态恢复"，此时航路应已被清掉。
        """
        if b['guid'] in self._parked:
            return
        obj = b['obj']
        try:
            if not force:
                try:
                    if obj.get_way_points_info():
                        return                  # 还在转移阵位，先不停
                except Exception:
                    pass
            obj.set_throttle(self._throttle('FullStop'))
            try:
                obj.set_desired_speed(0)
            except Exception:
                pass
            try:
                obj.hold_positon(True)
            except Exception:
                pass
            self._parked.add(b['guid'])
        except Exception as e:
            self._log('warning', '%s 停车失败: %s' % (b['name'], e))

    def _set_free_fire(self, b):
        if b['guid'] in self._free_fire_done:
            return
        try:
            b['obj'].doctrine_weapon_control_status_air(self._wcs_free())
            self._free_fire_done.add(b['guid'])
            self._log('info', '%s 对空改为自由开火' % b['name'])
        except Exception as e:
            self._log('warning', '%s 设自由开火失败: %s' % (b['name'], e))

    def _radar_set(self, b, on, force=False):
        """
        雷达开关。``force=True`` 时不看本地缓存、强制下发。

        平时靠缓存去重省指令；但"停车/逃跑"这类**姿态切换**必须强制下发——
        平台可能因任务条令、EMCON 重置等原因把雷达改回相反状态，而本地缓存
        仍然记着旧值，于是出现"停了但雷达没开"。
        """
        if not force and self._radar_state.get(b['guid']) is on:
            return
        obj = b['obj']
        try:
            if b['guid'] not in self._emcon_released:
                try:
                    obj.EMCON_Obey_doctrine(False)
                    self._emcon_released.add(b['guid'])
                except Exception:
                    pass
            res = obj.switch_radar(bool(on))
            if self._reply_ok(res) or res is None:
                self._radar_state[b['guid']] = bool(on)
                self._log('info', '%s 雷达%s%s'
                          % (b['name'], '开' if on else '关',
                             '（重发）' if force else ''))
        except Exception as e:
            self._log('warning', '%s 雷达开关失败: %s' % (b['name'], e))

    # ------------------------------------------------------------------
    # 目标选择与发弹
    # ------------------------------------------------------------------
    def _pick_target(self, b, situation):
        """
        选最近的敌方空中目标。

        :return: (目标dict 或 None, 距离km)。目标dict 含 {'cid','name','dist'}
        """
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
            d = _km(lat, lon, b.get('lat'), b.get('lon'))
            if d is None:
                continue
            if d < self.MIN_ENGAGE_KM:
                continue
            if best_d is None or d < best_d:
                best_d = d
                best = {'cid': _cget(c, 'ID', cid) or cid,
                        'name': str(_cget(c, 'Name', '') or ''), 'dist': d}
        return best, best_d

    def _own_index(self, situation):
        """本方单元 id 与名称集合，用于排除友军情报。"""
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
        """是否敌方空中目标（Type=0 空中；排除本方单元）。"""
        ctype = _to_int(_cget(c, 'Type'))
        if ctype is not None and ctype != 0:
            return False
        actual = _cget(c, 'ActualUnitID')
        if actual and actual in own_ids:
            return False
        nm = str(_cget(c, 'Name', '') or '')
        if nm and _norm(nm) in own_names:
            return False
        # 高度太低的多半是地面回波，防空营不浪费弹
        alt = _to_float(_cget(c, 'CurrentAltitude'), 0.0) or 0.0
        if alt < 50.0:
            return False
        return True

    def _fire(self, b, target, dist):
        """按挂载里对空射程最远的那型弹发弹；同 (营, 目标) 节流。"""
        key = (b['guid'], target['cid'])
        last = self._engage_at.get(key)
        if last is not None and self._cycle - last < self.REENGAGE_CYCLES:
            return False

        obj = b['obj']
        wid = b.get('best_wid')
        ok = False
        try:
            if wid is not None:
                ok = self._reply_ok(obj.attack_weapon_allocate_to_target(
                    target['cid'], int(wid), int(self.SALVO_ROUNDS)))
            if not ok:
                ok = self._reply_ok(obj.attack_auto(target['cid']))
        except Exception as e:
            self._log('error', '%s 发弹异常: %s' % (b['name'], e))
            return False

        if ok:
            self._engage_at[key] = self._cycle
            self._log('info', '%s 拦截[%s] 距离%.0fkm 弹数%d 弹种%s'
                      % (b['name'], target['name'], dist,
                         self.SALVO_ROUNDS, wid))
        else:
            self._warn_once('%s|firefail' % b['guid'],
                            '%s 发弹被拒（可能弹药耗尽或目标已失效）' % b['name'])
        return ok

    @staticmethod
    def _reply_ok(res):
        """平台回执判定：只看 code == 0。"""
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
    # 诊断
    # ------------------------------------------------------------------
    def status(self):
        """返回各营状态，供主智能体打印或赛后核对。"""
        return {
            'cycle': self._cycle,
            'battalions': [{'name': b['name'],
                            'dmax': round(b['dmax'], 1),
                            'range_src': b['range_src'],
                            'best_wid': b['best_wid'],
                            'ammo': b['ammo'],
                            'state': self._state.get(b['guid'], 'idle'),
                            'radar': self._radar_state.get(b['guid']),
                            'parked': b['guid'] in self._parked}
                           for b in self._battalions],
            'last': self._last_report,
        }
