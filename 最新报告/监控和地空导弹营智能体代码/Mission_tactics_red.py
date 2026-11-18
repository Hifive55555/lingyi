# -*- coding: utf-8 -*-
"""
================================================================================
红方 · 战术规则智能体（Monitor / AirCombat / Evade 三个模块）
================================================================================

这份文件是《本队智能体说明文档》里三个「核心智能体」的可执行实现，只做三件事：

  ① 物理作战域三维监控（Monitor）  —— 纯计算，不下任何指令：
       每步枚举敌方弹药（情报 Type=1），用「相对速度 → 最近接近点 CPA」
       判断它是否指向我方某个单元，命中就向下游交付 (弹型, 弹速, 距离, 剩余时间)。

  ② 空战单元自卫（Evade）        —— 只有飞机用：
       按弹速分档掉头（> 2500 km/h 时 50 km、1500~2500 时 20 km），
       近距离且弹速仍占优时做「正横机动 + 降高 305 m」，
       弹速掉到 500 km/h 以下就恢复任务。
       规避时临时接管控制权（withdraw_from_mission），规避结束再回原任务。

  ③ 空空作战（AirCombat）        —— 只有带弹的飞机用：
       由双方速度解临界距离 d0，距离 ≤ 0.8·d0、高度比在 90%~120% 之间才开火。

另外两条贯穿性的「护栏」（写在文件里，但属于控制权/边界逻辑）：

  · 边界守卫：飞机不能离任务区太远——出界 SOFT_NM 只记录，出界 HARD_NM
    就放弃追击目标并往回飞（任务区可以是手填的「中心+半径」，也可以回落到
    「起飞点 + 默认半径」）。
  · 禁航区：候选航路点若落在 NO_FLY_ZONES 多边形里，会自动往外挪，
    保证不会飞进去（蓝方那条「进禁航区每 20 秒扣 10 分」的规则就靠这个兜住）。

--------------------------------------------------------------------------------
一、怎么用
--------------------------------------------------------------------------------
1. 把本文件放到  <灵弈安装目录>\\intelligent\\ai\\engine\\LingYi\\  下
   （与 Mission_all_red.py 同一目录，同级有 entitys 文件夹）。
2. 在客户端「智能体编辑」里添加智能体，选本文件（类名固定为 Agent）。
3. Python 必须是 3.9（平台是 cp39 的 .pyd）。
4. 它可以与 Mission_all_red.py 同时加载（一个管战前配置，一个管战术动作），
   也可以单独加载——单独加载时它不会改任何战前条令/任务/挂载。

--------------------------------------------------------------------------------
二、想调参数就改这里
--------------------------------------------------------------------------------
· 任务区大小：MISSION_AREAS（任务名 -> (中心纬度, 中心经度, 半径km)）。
  你在客户端把任务区拖大拖小之后，把这里的半径改一下即可；
  没写进表里的任务会自动退回「起飞点 + DEFAULT_AREA_KM」。
· 出界容差：SOFT_NM / HARD_NM（海里）。
· 规避门限：EVADE_* 一组常量。
· 开火系数：FIRE_COEF（默认 0.8，跟文档一致）。
· 禁航区：NO_FLY_ZONES（为空表示不管）。

--------------------------------------------------------------------------------
三、日志怎么看
--------------------------------------------------------------------------------
日志里搜 "TAC" 就能看到本智能体的输出：
  TAC 锁定/威胁   —— 谁被什么弹盯上了、距离多少
  TAC 规避        —— 谁开始规避、往哪飞、为什么结束
  TAC 开火        —— 谁打谁、用什么弹、距离与 d0
  TAC 出界        —— 谁出了任务区、被拽回来
  TAC 禁航区      —— 哪个航路点被挪开了
每 20 个周期会打一行汇总，避免刷屏。
================================================================================
"""

import logging
import math
import os
import sys

try:                                                    # 平台内
    from engine.LingYi.entitys.global_util import (
        WeaponControlStatus, FuelStateRTB, WeaponStateRTB,
        WeaponStatePlanned, IgnorePlottedCourseWhenAttacking,
        IgnoreEMCONUnderAttack, EscortFlightSize, Throttle, AirValidStatus,
        ContactType,
    )
    from engine.LingYi.entitys.agent_base import RuleAgentBase
    from engine.LingYi.entitys.player import *          # noqa: F401,F403
except ImportError:                                     # 本地工作区（仅便于看代码）
    from entitys.global_util import (
        WeaponControlStatus, FuelStateRTB, WeaponStateRTB,
        WeaponStatePlanned, IgnorePlottedCourseWhenAttacking,
        IgnoreEMCONUnderAttack, EscortFlightSize, Throttle, AirValidStatus,
        ContactType,
    )
    from entitys.agent_base import RuleAgentBase
    from entitys.player import *                        # noqa: F401,F403


# ==============================================================================
# 几何小工具（全部用 纬度/经度 顺序，与 plotted_course 一致）
# ==============================================================================
NM = 1.852                      # 1 海里 = 1.852 km


def _get(o, key, default=None):
    """从 dict 或对象上取字段（大小写都不敏感）。"""
    if isinstance(o, dict):
        for k in (key, key.lower(), key.upper()):
            if k in o:
                return o[k]
        return default
    return getattr(o, key, default)


def _num(x, default=0.0):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v


def _pos(o):
    """(纬度, 经度)；取不到或为 (0,0) 返回 None。"""
    lat, lon = _get(o, 'Lat'), _get(o, 'Lon')
    if lat is None or lon is None:
        return None
    lat, lon = _num(lat, None), _num(lon, None)
    if lat is None or lon is None:
        return None
    if abs(lat) < 1e-9 and abs(lon) < 1e-9:
        return None
    return (lat, lon)


def _km(a, b):
    """两点距离（km），小范围用等距近似，够用且快。"""
    dn = (a[0] - b[0]) * 111.32
    de = (a[1] - b[1]) * 111.32 * math.cos(math.radians((a[0] + b[0]) / 2.0))
    return math.hypot(dn, de)


def _bearing(a, b):
    """a -> b 的方位角（度，正北 0，顺时针）。"""
    dn = (b[0] - a[0]) * 111.32
    de = (b[1] - a[1]) * 111.32 * math.cos(math.radians((a[0] + b[0]) / 2.0))
    return (math.degrees(math.atan2(de, dn)) + 360.0) % 360.0


def _point_at(a, brg, km):
    """从 a 出发，沿方位 brg 走 km 公里后的点。"""
    dn = km * math.cos(math.radians(brg)) / 111.32
    de = km * math.sin(math.radians(brg)) / (
        111.32 * max(0.1, math.cos(math.radians(a[0]))))
    return (a[0] + dn, a[1] + de)


def _point_in_poly(p, poly):
    """射线法判断点是否在多边形内。poly: [(lat, lon), ...]"""
    y, x = p[0], p[1]
    inside = False
    n = len(poly)
    for i in range(n):
        y1, x1 = poly[i]
        y2, x2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xx = x1 + (y - y1) * (x2 - x1) / (y2 - y1 + 1e-12)
            if x < xx:
                inside = not inside
    return inside


# ==============================================================================
# 智能体
# ==============================================================================
class Agent(RuleAgentBase):
    # ------------------------------------------------------------------
    # 一、可调参数
    # ------------------------------------------------------------------
    # 每个决策周期最多下发多少条指令（平台总上限 500/10s，这里再自限一层）
    ORDER_CAP_PER_CYCLE = 120

    # 本次实验的标签：改这里，日志第一行会原样打出来，方便回看“这一局是什么设置”
    RUN_TAG = '默认设置'

    # 分模块开关：验证时一次只开一个，出问题好定位
    ENABLE_MONITOR = True       # 只算不动手（消息栏/日志）
    ENABLE_EVADE = True         # 自卫掉头
    ENABLE_AIR_COMBAT = True    # 空空开火
    ENABLE_BOUNDARY = True      # 出界召回

    # ---- 威胁判定（Monitor）----
    THREAT_CPA_KM = 3.0         # 最近接近点 < 3 km 视为“指向我方”
    THREAT_MAX_KM = 90.0        # 超过这个距离的弹不关心
    THREAT_TGO_S = 900.0        # 预计命中时间超过 15 分钟的弹不关心

    # ---- 规避（Evade）----
    SPD_HI = 2500.0             # km/h
    SPD_LO = 1500.0             # km/h
    EVADE_TURN_HI_KM = 50.0     # 高速弹：进 50 km 掉头
    EVADE_TURN_LO_KM = 20.0     # 中速弹：进 20 km 掉头
    EVADE_JINK_KM = 20.0        # 垂直机动时，距本机多远取横向点
    EVADE_JINK_ALT_M = 305.0    # 垂直机动降高
    EVADE_DONE_SPD = 500.0      # 弹速低于此值，恢复任务
    EVADE_MAX_SEC = 120.0       # 一次规避最长持续
    # 兜底触发：d0 用“当前弹速”会算很小（弹已经减速时），必须再加两条硬条件
    EVADE_ALWAYS_KM = 25.0      # 进到 25 km 内：无条件规避
    EVADE_ALWAYS_TGO = 60.0     # 预计 60 秒内命中：无条件规避
    # 规避方式：
    #   'beam' = 正横机动（默认）。几何上最省能量：转向与弹的速度矢量垂直，
    #            迫使弹持续修正，脱靶量最大；而且一定看得见（90° 转向）。
    #   'away' = 纯掉头（文档 2.3.2 的写法）：弹从正后方追来时“掉头”=继续往前飞，
    #            画面上看不出在规避，效果也最差。
    EVADE_MODE = 'beam'
    EVADE_BEAM_KM = 45.0        # 正横目标点距离（本机前方多远）
    VERTICAL_JINK = False       # 文档结论：纯运动学下垂直机动是负收益，默认关
    JINK_SWITCH_CYCLES = 1      # 每几个周期换一次左右
    REPLOT_SEC = 30.0           # 规避航路最快多久重画一次（避免每周期重置转向）
    # 掉头距离优先用 d_turn = 1.2·d0（文档 4.1.1 结论：五档存活率全 100%，
    # 固定 50/20 km 分档在 2000~2500 km/h 时裕度只有 0.47~0.74，会掉头太晚）
    EVADE_USE_D0 = True
    USE_DROPTARGET = False      # False：规避/召回时不发 DropTarget（该 Lua 脚本异常会带崩引擎）
    EVADE_D0_COEF = 1.2

    # ---- 空空作战（AirCombat）----
    D0_T_SEC = 240.0            # 导弹从初速衰减到 Vterm 的时间常数
    D0_VTERM = 500.0            # 能量耗尽速度
    FIRE_COEF = 0.8             # 距离 ≤ 0.8·d0 开火
    FIRE_FIXED_KM = None        # 实验臂开关：设成定值则用"固定开火距离"（复现 60/90 海里
                                # 常数基线），忽略 d0；None = 按 FIRE_COEF·d0（正文规则）
    HEIGHT_R_MIN = 0.9          # 目标高度 / 本机高度 的下限
    HEIGHT_R_MAX = 1.2          # 上限
    FIRE_MIN_KM = 5.0           # 太近了不打（避免已错过的目标）
    # 真正的射程门限：不能只看 d0，还要看这型弹自己打得到多远
    FIRE_RANGE_COEF = 0.7       # 只在武器最大射程的 70% 以内开火
    TARGET_MAX_KM = 160.0       # 超过这个距离不考虑
    FIRE_RETRY_SEC = 30.0       # 同一目标两次分配武器的间隔
    V0_DEFAULT = 4000.0         # 我方弹初速的兜底值（km/h），会被实测值覆盖
    # 也可以直接写死某型弹的初速：{武器DBID: km/h}
    V0_TABLE = {}

    # ---- 边界 / 禁航区 ----
    SOFT_NM = 20.0              # 出界多少只记录
    HARD_NM = 50.0              # 出界多少就拽回来
    DEFAULT_AREA_KM = 70.0      # 任务没写进 MISSION_AREAS 时的默认半径
    NO_FLY_MARGIN_KM = 5.0      # 出禁航区时多退这么远
    # 禁航区多边形：[(名字, [(lat, lon), ...]), ...]，为空表示不检查
    NO_FLY_ZONES = ()

    # ---- 任务区表：任务名 -> (中心纬度, 中心经度, 半径km) ----
    # 依据当前红方任务表算出来的初值；你在客户端拖大拖小任务区后改半径即可。
    MISSION_AREAS = {
        # 支援（航线形心）
        '左75-2': (49.922759, -5.774064, 106.2),
        '左35-2': (49.412422, -5.425727, 107.8),
        '左阵风1': (48.001682, -6.967063, 97.0),
        '左阵风2': (47.471805, -7.212795, 102.9),
        '左阵风3': (47.000928, -7.234457, 97.5),
        '左阵风4': (46.538803, -6.999923, 94.8),
        '左阵风5': (45.834761, -5.213554, 148.8),
        '左阵风6': (46.650369, -3.995337, 153.7),
        '苏27-1': (49.693803, -1.738425, 82.2),
        '苏24下': (50.529843, -1.201518, 54.3),
        '伊尔22': (51.997866, -0.051761, 72.9),
        '轰炸机': (52.019070, -1.721202, 57.5),
        '北35-1': (52.682088, 2.868606, 136.7),
        '北35-2': (53.046616, 2.498307, 115.9),
        '北阵风-1': (52.193219, 2.516779, 112.8),
        '北阵风-2': (51.929178, 3.671208, 122.0),
        # 巡逻（巡逻区形心）
        '阵风3': (50.978391, 2.735833, 70.9),
        '神经元1': (49.204282, -2.108434, 30.5),
        '神经元2': (49.288787, -0.940595, 33.1),
        '神经元3': (49.267950, -0.675481, 31.6),
        '阵风1': (49.568050, 0.350357, 39.3),
        '阵风2': (49.951740, 1.534274, 96.8),
        'TB1': (49.389350, -1.379570, 32.0),
        'TB2': (49.258510, -0.079902, 33.6),
        'TB3': (49.752700, 1.560390, 34.6),
        'S70-1': (48.858527, -1.133892, 122.3),
        'S70-2': (48.822616, 0.994916, 127.4),
        '中间保船': (49.510090, -1.017982, 45.5),
        '反潜巡逻': (48.125600, -6.987150, 78.7),
        '左制空': (49.046692, -1.660353, 176.9),
        '右制空': (49.106787, 0.791354, 178.7),
        '北制空': (52.581647, 4.116141, 156.8),
    }

    # ---- 客户端消息栏（操作手看的）----
    MSG_ENABLE = True           # 往客户端“智能体输出”消息栏推提示
    MSG_MAX_PER_CYCLE = 3       # 每周期最多几条，避免刷屏
    MSG_DEDUP_SEC = 30.0        # 同一句话多久内不重复
    MSG_REPORT_FULL = True      # 每周期额外推一条“谁在被攻击”的汇总

    # ------------------------------------------------------------------
    # 二、构造 / 日志
    # ------------------------------------------------------------------
    def __init__(self, side_name, params=None):
        RuleAgentBase.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
        self._st = {}            # guid -> 单元状态机
        self._home = {}          # guid -> 起飞/初始位置
        self._v0_est = {}        # 武器DBID -> 实测初速（km/h）
        self._m_v0 = {}          # 情报ID（某枚弹）-> 这枚弹观测到的最高速度
        self._wt_cache = {}      # 武器DBID -> 武器类型（2001 导弹 / 2004 机炮 …）
        self._our_wids = set()   # 我方在用的空战弹 DBID（判定某枚弹是不是我们打的）
        self._dead = set()       # 平台报“找不到单元”的 guid（已毁/已卸载），不再下发
        self._rng_cache = {}     # 武器DBID -> 对空射程 km
        self._msgs = []          # 本周期待推送的消息
        self._last_msg = {}      # 消息去重：text -> 时间
        self._combat_diag = {}   # 空战诊断计数
        self._area_warned = set()  # 已经提示过“任务不在区表里”的任务名
        self._cycle = 0
        self._used = 0           # 本周期已下发指令数
        self._threats = {}       # guid -> 威胁 dict
        self._missiles = []      # 本周期敌方弹药列表
        self._air = {}           # guid -> 空中目标情报
        self._diag_done = False
        self._now = 0.0

    def _log(self, level, msg):
        """安全日志（平台里 self.log 可能是 None，统一回退到 logging）。"""
        logger = getattr(self, 'log', None)
        fn = getattr(logger, level, None) if logger is not None else None
        if callable(fn):
            fn(msg)
        else:
            getattr(logging, level, logging.info)(
                '%s:%s[TAC] %s' % (getattr(self, 'Name', '?'),
                                   self.__class__.__name__, msg))

    def _cmd(self, guid, fn, *args, **kwargs):
        """
        下发一条指令（计数 + 异常兜底 + 死单元跳过）。返回 (ok, 回复文字)。

        :param guid: str, 目标单元 guid（平台回“找不到单元”就把该 guid 拉黑）
        """
        if guid in self._dead:
            return False, '单元已失效（跳过）'
        if self._used >= self.ORDER_CAP_PER_CYCLE:
            return False, '本周期指令额度已用完'
        self._used += 1
        try:
            res = fn(*args, **kwargs)
        except Exception as e:
            return False, '异常 %s' % e
        ok = self._reply_ok(res)
        txt = self._reply_text(res)
        if not ok and ('找不到单元' in txt or '未找到单元' in txt or
                       '不存在' in txt):
            self._dead.add(guid)
            self._log('warning', '单元 %s 已失效（%s），后续不再下发' % (guid, txt))
        return ok, txt

    # ---------------------- 客户端消息栏 ----------------------
    def _notify(self, text):
        """往客户端“智能体输出”消息栏推一条（带去重与条数限制）。"""
        if not self.MSG_ENABLE or not text:
            return
        last = self._last_msg.get(text)
        if last is not None and self._now - last < self.MSG_DEDUP_SEC:
            return
        if len(self._msgs) >= self.MSG_MAX_PER_CYCLE:
            return
        self._last_msg[text] = self._now
        self._msgs.append(text)

    def _flush_msgs(self):
        """把本周期攒的消息真正发给客户端。"""
        if not self._msgs:
            return 0
        n = 0
        fn = getattr(self, 'agent_message_text', None)
        for text in self._msgs:
            if not callable(fn):
                break
            try:
                fn(text)
                n += 1
            except Exception as e:
                self._log('warning', '消息推送失败: %s' % e)
                break
        self._msgs = []
        return n

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
        return True

    @staticmethod
    def _reply_text(res):
        if res is None:
            return 'None'
        raw = getattr(res, 'result', res)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = bytes(raw).decode('utf-8', 'ignore')
            except Exception:
                raw = str(raw)
        return str(raw or '')[:160]

    @staticmethod
    def _alive(obj):
        """单元是否还在：DamagePercent ≥ 100 视为已被击毁。

        引擎对已击毁单元执行 DropTarget 会抛未捕获异常（"Unexpected error in
        RPC handling"）并带崩推演，所以下发前必须先判。
        """
        if obj is None:
            return False
        try:
            return _num(_get(obj, 'DamagePercent', 0)) < 100.0
        except Exception:
            return True

    # ------------------------------------------------------------------
    # 三、数据采集
    # ------------------------------------------------------------------
    def _own_units(self, situation):
        out = []
        units = {}
        if isinstance(situation, (list, tuple)) and len(situation) > 0 \
                and isinstance(situation[0], dict):
            units = situation[0]
        for guid, u in (units or {}).items():
            if not isinstance(u, dict):
                continue
            out.append((u.get('guid') or guid,
                        str(u.get('name', '') or ''),
                        str(u.get('category', '') or ''),
                        u))
        return out

    def _contacts(self, situation):
        if isinstance(situation, (list, tuple)) and len(situation) > 1 \
                and isinstance(situation[1], dict):
            return situation[1]
        return {}

    @staticmethod
    def _airborne(obj):
        """
        是否在空。

        只有飞机（Aircraft）才有 get_status_type；舰船/地面设施一律返回 False，
        避免把海拔 160 米的雷达站当成“飞机”。
        """
        fn = getattr(obj, 'get_status_type', None)
        if not callable(fn):
            return False
        try:
            return fn() in (AirValidStatus.InAir, AirValidStatus.InAirRTB)
        except Exception:
            return False

    def _collect(self, situation):
        """刷新：我方弹型、敌方弹药、敌方空中目标。"""
        self._missiles = []
        self._air = {}
        # 我方在用的空战弹（用于判断“这枚弹是不是我们打出去的”，进而标定初速）
        our = set()
        for _g, _n, _c, _r in self._own_units(situation):
            _o = self.get_unit(_g)
            if _o is None:
                continue
            for _m in (getattr(_o, 'Mounts', {}) or {}).values():
                _recs = _m.get('WeaponRecs') if isinstance(_m, dict) else None
                if not isinstance(_recs, dict):
                    continue
                for _rec in _recs.values():
                    if isinstance(_rec, dict) and \
                            _num(_rec.get('AirRangeMax', 0)) > 0:
                        try:
                            our.add(int(_rec.get('WeaponDBID')))
                        except (TypeError, ValueError):
                            pass
        self._our_wids = our
        for cid, c in self._contacts(situation).items():
            if not isinstance(c, dict):
                continue
            p = _pos(c)
            if p is None:
                continue
            cty = _get(c, 'Type')
            try:
                cty = int(cty) if cty is not None else -1
            except (TypeError, ValueError):
                cty = -1
            item = {
                'id': cid,
                'name': str(_get(c, 'Name', '') or ''),
                'dbid': _get(c, 'DBID'),
                'pos': p,
                'speed': _num(_get(c, 'CurrentSpeed', 0)),
                'hdg': _num(_get(c, 'CurrentHeading', 0)),
                'alt': _num(_get(c, 'CurrentAltitude', 0)),
            }
            if cty == int(ContactType.Missile.value):
                self._missiles.append(item)
                # 记住这枚弹观测到的最高速（作为 d0 的 V0，避免“弹已减速→d0 变得很小”）
                prev = self._m_v0.get(cid, 0.0)
                if item['speed'] > prev:
                    self._m_v0[cid] = item['speed']
                # 我方打出去的弹：第一次看到就把速度记成该型弹的初速估计
                try:
                    w = int(item['dbid'])
                except (TypeError, ValueError):
                    w = None
                if w is not None and w in self._our_wids and item['speed'] > 0:
                    prev = self._v0_est.get(w, 0.0)
                    if item['speed'] > prev:
                        self._v0_est[w] = item['speed']
                        if prev <= 0.0:
                            self._log('info', '标定弹速：武器%s 初速≈%.0f km/h'
                                      % (w, item['speed']))
            elif cty == int(ContactType.Air.value):
                self._air[cid] = item

    @staticmethod
    def _cpa(me_pos, me_hdg, me_spd, tgt):
        """
        计算目标弹药对本方的最近接近点。

        :return: (cpa_km, t_go_s, 是否在接近)
        """
        lat = math.radians(me_pos[0])
        # 相对位置（我方为原点，东/北，km）
        rx = (tgt['pos'][1] - me_pos[1]) * 111.32 * math.cos(lat)
        ry = (tgt['pos'][0] - me_pos[0]) * 111.32
        # 相对速度（km/h）
        tvx = tgt['speed'] * math.sin(math.radians(tgt['hdg']))
        tvy = tgt['speed'] * math.cos(math.radians(tgt['hdg']))
        mvx = me_spd * math.sin(math.radians(me_hdg))
        mvy = me_spd * math.cos(math.radians(me_hdg))
        vx, vy = tvx - mvx, tvy - mvy
        vv = vx * vx + vy * vy
        if vv < 1e-9:
            return math.hypot(rx, ry), 0.0, False
        t = -(rx * vx + ry * vy) / vv          # 小时
        closing = t > 0
        if t < 0:
            t = 0.0
        cx, cy = rx + vx * t, ry + vy * t
        return math.hypot(cx, cy), t * 3600.0, closing

    # ------------------------------------------------------------------
    # 四、模块 1：物理作战域三维监控（只算，不动手）
    # ------------------------------------------------------------------
    def monitor(self, situation):
        """
        枚举敌方弹药，判断“是否指向我方某个单元”，命中就记一条威胁。

        :return: dict, {我方guid: 威胁}
        """
        self._collect(situation)
        threats = {}
        if not self._missiles:
            self._threats = threats
            return threats
        for guid, name, cat, raw in self._own_units(situation):
            obj = self.get_unit(guid)
            if obj is None:
                continue
            p = _pos(obj) or _pos(raw)
            if p is None:
                continue
            hdg = _num(_get(obj, 'CurrentHeading', _get(raw, 'CurrentHeading', 0)))
            spd = _num(_get(obj, 'CurrentSpeed', _get(raw, 'CurrentSpeed', 0)))
            best = None
            for m in self._missiles:
                if _km(p, m['pos']) > self.THREAT_MAX_KM:
                    continue
                cpa, tgo, closing = self._cpa(p, hdg, spd, m)
                if not closing or cpa > self.THREAT_CPA_KM:
                    continue
                if tgo > self.THREAT_TGO_S:
                    continue
                if best is None or tgo < best['tgo']:
                    best = {'mid': m['id'], 'mname': m['name'], 'mdbid': m['dbid'],
                            'mspeed': m['speed'], 'mpos': m['pos'],
                            'mhdg': m['hdg'],
                            'mv0': self._m_v0.get(m['id'], m['speed']),
                            'dist': _km(p, m['pos']), 'cpa': cpa, 'tgo': tgo}
            if best:
                best['name'] = name
                threats[guid] = best
        self._threats = threats
        for guid, t in threats.items():
            if t['tgo'] <= 120.0 or self._cycle % 20 == 0:
                self._log('info', '威胁[%s] ← %s 弹速%.0fkm/h 距离%.1fkm CPA%.1fkm '
                                  '预计%.0fs命中'
                          % (t['name'], t['mname'] or t['mdbid'], t['mspeed'],
                             t['dist'], t['cpa'], t['tgo']))
        # 操作手看的一行汇总：谁在被攻击
        if threats and self.MSG_REPORT_FULL:
            parts = []
            for _g, t in sorted(threats.items(), key=lambda kv: kv[1]['tgo']):
                parts.append('%s(%.0fs)' % (t['name'], t['tgo']))
            self._notify('【被锁定】%d 架：%s'
                         % (len(parts), '、'.join(parts[:6])))
        return threats

    # ------------------------------------------------------------------
    # 五、任务区 / 边界
    # ------------------------------------------------------------------
    def _mission_of(self, obj):
        """单元当前任务名（平台给的是任务 guid，尽力换成名字）。"""
        mis = str(getattr(obj, 'AssignedMission', '') or '').strip()
        if not mis:
            return ''
        for name, m in (getattr(self, 'missions_obj', None) or {}).items():
            if mis in (name, getattr(m, 'ID', None)):
                return name
        return mis

    def _area_of(self, guid, obj):
        """
        (中心, 半径km)；查不到就返回 (None, None) 表示“这个任务不做出界判定”。

        顺序：状态机里记下的“原任务” → 当前任务 → 调参表 MISSION_AREAS。
        ⚠ 两个坑都在这里：
          1) 规避时会退任务，AssignedMission 变空；若回落成“起飞点”，飞机就会被
             判成“出界 200 km”并拽回基地（上一版就是这么把飞机送回去的）。
          2) 任务不在 MISSION_AREAS 里时，**不要**回落到“起飞点 + 70 km”——
             飞机在别的空域执行任务，会被误判成出界（TB2#17、前哨#3#4 就是这样）。
        """
        st = self._st.get(guid) or {}
        name = st.get('mis') or self._mission_of(obj)
        if name and name in self.MISSION_AREAS:
            lat, lon, r = self.MISSION_AREAS[name]
            return (lat, lon), r
        if st.get('area'):
            return st['area']
        if name:
            self._warn_unknown_area(name)
        return None, None

    def _warn_unknown_area(self, name):
        """任务不在任务区表里：提示一次，然后跳过边界检查（不误召回）。"""
        if name in self._area_warned:
            return
        self._area_warned.add(name)
        self._log('warning',
                  '任务[%s] 不在 MISSION_AREAS 表里，本任务不做“出界召回”'
                  '（要管的话把它加进 MISSION_AREAS：中心纬度, 中心经度, 半径km）'
                  % name)

    def _outside_km(self, guid, obj, pos):
        """出界多少公里（在区内返回 0）。"""
        center, r = self._area_of(guid, obj)
        if center is None:
            return 0.0
        return max(0.0, _km(center, pos) - r)

    def _safe_point(self, frm, to):
        """把候选点从禁航区里拉出来（沿 to→frm 方向回退）。"""
        for _zname, poly in self.NO_FLY_ZONES:
            if not poly or not _point_in_poly(to, poly):
                continue
            for i in range(1, 21):
                cand = (to[0] + (frm[0] - to[0]) * i / 20.0,
                        to[1] + (frm[1] - to[1]) * i / 20.0)
                if not _point_in_poly(cand, poly):
                    brg = _bearing(to, cand)
                    self._log('info', '禁航区[%s]：目标点在内，已外移 %.0fkm'
                              % (_zname, _km(to, cand)))
                    return _point_at(cand, brg, self.NO_FLY_MARGIN_KM)
            return tuple(frm)
        return to

    # ------------------------------------------------------------------
    # 六、模块 2：空战单元自卫
    # ------------------------------------------------------------------
    def _break_point(self, pos, missile_pos, dist_km):
        """掉头点：沿着“弹→我”的延长线往外飞。"""
        away = _bearing(missile_pos, pos)
        return _point_at(pos, away, max(dist_km, self.EVADE_JINK_KM))

    def _turn_point(self, pos, th, gate):
        """
        算规避目标点。

        'beam'：转到与来袭弹速度矢量**垂直**的方向，取“远离弹航线”的那一侧。
        'away'：沿“弹→我”延长线往外飞。
        """
        if self.EVADE_MODE != 'beam':
            dest = self._break_point(pos, th['mpos'], gate + 20.0)
            return self._safe_point(pos, dest)
        mh = _num(th.get('mhdg', 0))                    # 弹的航向
        bl = _bearing(th['mpos'], pos)                  # 弹→我 的方位
        delta = (bl - mh + 540.0) % 360.0 - 180.0       # 我在弹航线的哪一侧
        turn_to = (mh + 90.0) if delta >= 0 else (mh - 90.0)
        dest = _point_at(pos, turn_to % 360.0, self.EVADE_BEAM_KM)
        return self._safe_point(pos, dest)

    def evade(self, situation):
        """
        对每架在空飞机执行“分档掉头 / 垂直机动 / 恢复”。

        :return: int, 本周期处理的自卫动作数
        """
        n = 0
        for guid, name, cat, raw in self._own_units(situation):
            obj = self.get_unit(guid)
            if obj is None or not self._airborne(obj):
                continue
            if cat and str(cat) != 'Aircraft':
                continue
            st = self._st.setdefault(guid, {'state': 'mission', 'mis': '',
                                            't0': 0.0, 'jink': 1, 'jink_t': -1e9,
                                            'last_fire': -1e9, 'tgt': ''})
            p = _pos(obj) or _pos(raw)
            if p is None:
                continue
            th = self._threats.get(guid)
            # ---- 没有威胁：若在规避中则恢复 ----
            if th is None:
                if st['state'] != 'mission':
                    self._end_evade(guid, obj, st, '威胁消失')
                continue
            # ---- 已在规避中：先判结束条件 ----
            if st['state'] == 'evade':
                if th['mspeed'] < self.EVADE_DONE_SPD:
                    self._end_evade(guid, obj, st, '弹速降到 %.0f' % th['mspeed'])
                    continue
                if self._now - st['t0'] > self.EVADE_MAX_SEC:
                    self._end_evade(guid, obj, st,
                                    '规避超时 %.0fs' % self.EVADE_MAX_SEC)
                    continue
            # ---- 先算要不要动手（没到门限就别打断任务）----
            my_spd = _num(_get(obj, 'CurrentSpeed', 0))
            if self.EVADE_USE_D0:
                # 用这枚弹“观测到的最高速”当 V0（不是当前速度），否则弹一减速 d0 就塌了
                gate = self.EVADE_D0_COEF * self.d0_km(
                    max(th.get('mv0', th['mspeed']), 600.0), max(my_spd, 300.0))
            elif th['mspeed'] > self.SPD_HI:
                gate = self.EVADE_TURN_HI_KM
            else:
                gate = self.EVADE_TURN_LO_KM      # 中低速弹统一按近距处理
            need_jink = (self.VERTICAL_JINK
                         and th['dist'] < self.EVADE_JINK_KM
                         and th['mspeed'] > my_spd * 1.5)
            # 三条并列：包线门限 / 绝对距离 / 绝对剩余时间——任一满足就动
            need_turn = (th['dist'] <= gate
                         or th['dist'] <= self.EVADE_ALWAYS_KM
                         or th['tgo'] <= self.EVADE_ALWAYS_TGO)
            if not (need_turn or need_jink):
                # 还在包线外：保持任务托管，不抢控制权
                if st['state'] == 'evade' and \
                        self._now - st['t0'] > self.EVADE_MAX_SEC:
                    self._end_evade(guid, obj, st, '规避超时')
                continue
            # ---- 真正要动手了：先接管控制权 ----
            if st['state'] != 'evade':
                st['state'] = 'evade'
                st['t0'] = self._now
                st['mis'] = self._mission_of(obj)
                st['area'] = self._area_of(guid, obj)
                st['turn_t'] = -1e9
                if st['mis']:
                    ok, txt = self._cmd(guid, obj.withdraw_from_mission)
                    self._log('info', '规避[%s] 接管控制（退任务 %s）%s'
                              % (name, st['mis'], 'ok' if ok else txt))
                    if not ok:
                        # 单元已不在场景里：立刻拉黑，绝不能再下发 DropTarget
                        self._dead.add(guid)
                        st['state'] = 'mission'
                        continue
                self._notify('【规避】%s 开始规避（弹速%.0f 距离%.0fkm 门限%.0fkm）'
                             % (name, th['mspeed'], th['dist'], gate))
            # 垂直机动（默认关）：近距离且弹速仍明显大于我机
            if need_jink:
                if self._now - st['jink_t'] >= self.JINK_SWITCH_CYCLES * 30.0:
                    st['jink'] = -st['jink']
                    st['jink_t'] = self._now
                brg = _bearing(th['mpos'], p) + 90.0 * st['jink']
                dest = _point_at(p, (brg + 360.0) % 360.0, self.EVADE_JINK_KM)
                dest = self._safe_point(p, dest)
                self._cmd(guid, obj.plotted_course, [dest])
                self._cmd(guid, obj.set_desired_height, self.EVADE_JINK_ALT_M)
                self._cmd(guid, obj.set_throttle, Throttle.Flank)
                self._log('info', '规避[%s] 垂直扭动 → 航向%.0f° 降高%.0fm'
                          % (name, brg % 360.0, self.EVADE_JINK_ALT_M))
                n += 1
                continue
            if need_turn:
                # 航路别每周期重画（会一直重置转向），REPLOT_SEC 或偏离够远才重发
                dest = self._turn_point(p, th, gate)
                old = st.get('turn_pt')
                need_plot = (self._now - st.get('turn_t', -1e9)
                             >= self.REPLOT_SEC) or (old is None) or \
                            (_km(old, dest) > 5.0)
                if need_plot and guid not in self._dead:
                    # DropTarget 对个别单元（已退任务 / 舰载机 / 刚被击毁）会让引擎抛未捕获
                    # 异常（"Unexpected error in RPC handling"）并直接带崩推演；撤离控制权
                    # 已由 withdraw_from_mission 完成，这里默认不再下发。
                    if self.USE_DROPTARGET:
                        self._cmd(guid, obj.attack_drop_target_all)
                    self._cmd(guid, obj.plotted_course, [dest])
                    self._cmd(guid, obj.set_throttle, Throttle.Flank)
                    st['turn_t'] = self._now
                    st['turn_pt'] = dest
                    self._log('info',
                              '规避[%s] %s（弹速%.0f 距离%.1f 门限%.0f）→ 航向%.0f° %.3f,%.3f'
                              % (name, '正横机动' if self.EVADE_MODE == 'beam'
                                 else '掉头', th['mspeed'], th['dist'], gate,
                                 _bearing(p, dest), dest[0], dest[1]))
                    self._notify('【规避】%s %s，转向 %.0f°'
                                 % (name, '正横机动' if self.EVADE_MODE == 'beam'
                                    else '掉头', _bearing(p, dest)))
                    n += 1
        return n

    def _end_evade(self, guid, obj, st, why):
        name = getattr(obj, 'Name', guid)
        st['state'] = 'mission'
        st['turn_pt'] = None
        mis = st.get('mis') or ''
        # 任务名留着给 _area_of 用（重新分配后 _mission_of 会再读到）
        if mis:
            ok, txt = self._cmd(guid, obj.assign_to_mission, mis)
            self._log('info', '规避结束[%s]（%s）→ 回任务 %s %s'
                      % (name, why, mis, 'ok' if ok else txt))
            self._notify('【恢复】%s 规避结束（%s）→ 回任务 %s'
                         % (name, why, mis))
        else:
            center, _r = self._area_of(guid, obj)
            if center:
                self._cmd(guid, obj.plotted_course, [center])
                self._log('info', '规避结束[%s]（%s）→ 回任务区中心' % (name, why))
                self._notify('【恢复】%s 规避结束（%s）→ 回任务区'
                             % (name, why))
            else:
                self._log('info', '规避结束[%s]（%s）' % (name, why))

    # ------------------------------------------------------------------
    # 七、模块 3：空空作战
    # ------------------------------------------------------------------
    def _best_aam(self, obj):
        """从挂载里挑空战弹：(武器DBID, 数量, 最大射程km)。选射程最远的那型。

        2026-11-18 修：原来只认 WeaponRecs 为 dict，且用 sqlite 查 model.db 判类型；
        平台实测 `无空战弹` 恒为满额（每架飞机都判成没有空空弹），空战规则因此从未触发。
        现在改为：Mounts/Magazines/Loadouts 三个容器都扫，WeaponRecs 允许 dict/list，
        射程优先取挂载记录里的 AirRangeMax，其次走平台 query_data，最后回退 sqlite；
        机炮/诱饵按射程下限 10 km 剔除，不再依赖 Type 字段。
        """
        best = None
        seen = []
        for attr in ('Mounts', 'Magazines', 'Loadouts'):
            cont = getattr(obj, attr, None)
            if not isinstance(cont, dict):
                continue
            for _mk, mv in cont.items():
                if not isinstance(mv, dict):
                    continue
                wrs = mv.get('WeaponRecs')
                if isinstance(wrs, dict):
                    items = list(wrs.values())
                elif isinstance(wrs, (list, tuple)):
                    items = list(wrs)
                else:
                    items = []
                for rec in items:
                    if not isinstance(rec, dict):
                        continue
                    try:
                        wid = int(rec.get('WeaponDBID'))
                        load = int(rec.get('CurrentLoad', 0) or 0)
                    except (TypeError, ValueError):
                        continue
                    if load <= 0:
                        continue
                    rng_nm = _num(rec.get('AirRangeMax', 0))
                    rng_km = rng_nm * NM if rng_nm > 0 else self._db_air_range_km(wid)
                    if rng_km < 10.0:          # 机炮 / 诱饵 / 对空射程未知
                        continue
                    seen.append((wid, load, round(rng_km, 1)))
                    if best is None or rng_km > best[2]:
                        best = (wid, load, rng_km)
        if self._cycle % 60 == 0:
            self._log('info', '空战弹诊断[%s]：%s' %
                      (getattr(obj, 'Name', '?'), seen[:4] if seen else '无'))
        return best

    def _weapon_type(self, wid):
        """查武器类型：2001 导弹 / 2004 机炮 / 2006-2007 诱饵。"""
        wid = int(wid)
        if wid in self._wt_cache:
            return self._wt_cache[wid]
        ty = 0
        path = self._db_path()
        if path:
            try:
                import sqlite3
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute('select Type from DataWeapon where ID = ?', (wid,))
                row = cur.fetchone()
                conn.close()
                if row and row[0]:
                    ty = int(row[0])
            except Exception as e:
                self._log('warning', '查武器%s类型失败: %s' % (wid, e))
        self._wt_cache[wid] = ty
        return ty

    def _db_air_range_km(self, wid):
        """从 model.db 的 DataWeapon.AirRangeMax（海里）查某型弹的对空射程。"""
        wid = int(wid)
        if wid in self._rng_cache:
            return self._rng_cache[wid]
        rng = 0.0
        # ① 平台接口优先（与 SamBattalionDefense 同一口径，返回 km）
        try:
            from engine.LingYi.entitys.data import query_data as _qd
            _row = _qd.get_weapon_info(int(wid))
            if _row and _row[0]:
                self._rng_cache[wid] = float(_row[0])
                return float(_row[0])
        except Exception:
            pass
        # ② sqlite 回退
        path = self._db_path()
        if path:
            try:
                import sqlite3
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute('select AirRangeMax from DataWeapon where ID = ?',
                            (wid,))
                row = cur.fetchone()
                conn.close()
                if row and row[0]:
                    rng = float(row[0]) * NM
            except Exception as e:
                self._log('warning', '查武器%s射程失败: %s' % (wid, e))
        self._rng_cache[wid] = rng
        return rng

    def _db_path(self):
        """model.db 路径：优先 query_data，其次按文件位置推断。"""
        if getattr(self, '_dbp', None):
            return self._dbp
        path = None
        try:
            from entitys.data import query_data as qd
            path = getattr(qd, 'db_path', None)
        except Exception:
            try:
                from engine.LingYi.entitys.data import query_data as qd
                path = getattr(qd, 'db_path', None)
            except Exception:
                path = None
        if not path:
            here = os.path.dirname(os.path.abspath(__file__))
            for cand in (os.path.join(here, 'entitys', 'data', 'model.db'),
                         os.path.join(here, '..', 'entitys', 'data', 'model.db')):
                if os.path.exists(cand):
                    path = cand
                    break
        self._dbp = path
        return path

    def _v0_of(self, wid):
        """我方某型弹的初速（km/h）：实测值 > 手填表 > 兜底。"""
        wid = int(wid)
        if wid in self._v0_est:
            return self._v0_est[wid]
        if wid in self.V0_TABLE:
            return float(self.V0_TABLE[wid])
        return float(self.V0_DEFAULT)

    def d0_km(self, v0, va):
        """
        临界距离（km）：d0 = T·(V0-Va)² / (2·(V0-Vterm))，速度 km/h、T 秒。

        Va ≥ Vterm 时用闭式解；Va < Vterm 时取 F(T)（见文档 2.1.2）。
        """
        th = self.D0_T_SEC / 3600.0            # 秒 -> 小时
        vt = self.D0_VTERM
        v0 = max(v0, vt + 1.0)
        if va >= vt:
            return th * (v0 - va) ** 2 / (2.0 * (v0 - vt))
        return th * (v0 + vt) / 2.0 - th * va

    def air_combat(self, situation):
        """
        对每架在空、带弹、不在规避状态的飞机：选目标 → 算 d0 → 满足条件就开火。

        :return: int, 本周期开火次数
        """
        fired = 0
        why = {'无敌机情报': 0, '无敌机': 0, '无空战弹': 0, '高度比': 0,
               '距离': 0, '规避中': 0, '冷却': 0, '被拒': 0}
        if not self._air:
            # 没有敌方航空情报：这一点必须能看见，否则“开火0”无从诊断
            if self._cycle % 20 == 0:
                self._log('info', '空战诊断：本周期没有任何敌方航空情报'
                                  '（敌方飞机是否被探测到？）')
            return 0
        for guid, name, cat, raw in self._own_units(situation):
            if cat and str(cat) != 'Aircraft':
                continue
            obj = self.get_unit(guid)
            if obj is None or not self._airborne(obj):
                continue
            st = self._st.get(guid) or {}
            if st.get('state') == 'evade':
                why['规避中'] += 1
                continue                        # 先保命
            pos = _pos(obj) or _pos(raw)
            if pos is None:
                continue
            alt = _num(_get(obj, 'CurrentAltitude', 0))
            ammo = self._best_aam(obj)
            if not ammo:
                why['无空战弹'] += 1
                continue
            wid, _load, rng_km = ammo
            v0 = self._v0_of(wid)
            # 选目标：最近的敌机，且已进入考虑范围
            tgt = None
            for cid, c in self._air.items():
                d = _km(pos, c['pos'])
                if d > min(self.TARGET_MAX_KM, rng_km * 1.5):
                    continue
                if tgt is None or d < tgt[1]:
                    tgt = (cid, d, c)
            if tgt is None:
                why['无敌机'] += 1
                continue
            cid, dist, c = tgt
            # 高度比
            if alt <= 1.0:
                why['高度比'] += 1
                continue
            ratio = c['alt'] / alt if alt > 0 else 1.0
            if ratio < self.HEIGHT_R_MIN or ratio > self.HEIGHT_R_MAX:
                why['高度比'] += 1
                continue
            d0 = self.d0_km(v0, max(c['speed'], 1.0))
            # 双重门限：既要在能量包线内（0.8·d0），也要在这型弹真能打到的距离内
            _g0 = (self.FIRE_FIXED_KM if self.FIRE_FIXED_KM else self.FIRE_COEF * d0)
            gate = min(_g0, self.FIRE_RANGE_COEF * rng_km)
            if dist > gate or dist < self.FIRE_MIN_KM:
                why['距离'] += 1
                continue
            # 同一目标别每步都重复分配
            if st.get('tgt') == cid and self._now - st.get('last_fire', -1e9) < \
                    self.FIRE_RETRY_SEC:
                why['冷却'] += 1
                continue
            qty = 1 if dist > gate * 0.6 else 2
            qty = min(qty, _load)
            ok, txt = self._cmd(guid, obj.attack_weapon_allocate_to_target,
                                cid, wid, qty)
            st['tgt'] = cid
            st['last_fire'] = self._now
            self._st[guid] = st
            if ok:
                fired += 1
                self._log('info', '开火[%s] → %s  武器%s×%d  距离%.1fkm ≤ 门限%.1fkm '
                                  '(0.8d0=%.1f 射程%.1f V0=%.0f Va=%.0f 高度比%.2f)'
                          % (name, c['name'] or cid, wid, qty, dist, gate,
                             0.8 * d0, rng_km, v0, c['speed'], ratio))
                self._notify('【开火】%s → %s（%.0fkm，%s×%d）'
                             % (name, c['name'] or '敌机', dist, wid, qty))
            else:
                why['被拒'] += 1
                self._log('warning', '开火[%s] 被拒：%s' % (name, txt))
        if self._cycle % 20 == 0:
            self._log('info', '空战诊断：敌机情报%d 架；未开火原因 %s'
                      % (len(self._air),
                         ' '.join('%s=%d' % (k, v) for k, v in why.items()
                                  if v)))
        return fired

    # ------------------------------------------------------------------
    # 八、边界守卫（出界就拽回来）
    # ------------------------------------------------------------------
    def boundary_guard(self, situation):
        """
        飞机离任务区太远时：放弃追击 + 往回飞；同时记录软界告警。

        :return: int, 本周期纠正的架数
        """
        n = 0
        hard = self.HARD_NM * NM
        for guid, name, cat, raw in self._own_units(situation):
            if guid in self._dead:
                continue
            if cat and str(cat) != 'Aircraft':
                continue
            obj = self.get_unit(guid)
            if obj is None or not self._airborne(obj):
                continue
            pos = _pos(obj) or _pos(raw)
            if pos is None:
                continue
            out_km = self._outside_km(guid, obj, pos)
            if out_km <= 0:
                continue
            if out_km < self.SOFT_NM * NM:
                continue                        # 软界内：只放行
            center, r = self._area_of(guid, obj)
            if center is None:
                continue
            if out_km < hard:
                # 软界外、硬界内：只记录（每 10 个周期一次，避免刷屏）
                if self._cycle % 10 == 0:
                    self._log('info', '出界[%s] 距任务区 %.0fkm（软界 %.0fnm，硬界 %.0fnm）'
                              % (name, out_km, self.SOFT_NM, self.HARD_NM))
                continue
            # 硬界外：丢目标 + 往回飞到“区内 20km”处
            st = self._st.setdefault(guid, {'state': 'mission', 'mis': '',
                                            't0': 0.0, 'jink': 1,
                                            'jink_t': -1e9, 'last_fire': -1e9,
                                            'tgt': '', 'turn_t': -1e9,
                                            'turn_pt': None})
            # 同一架不要每周期都重发（否则指令刷屏、航路反复重置）
            if self._now - st.get('bound_t', -1e9) < self.REPLOT_SEC:
                continue
            st['bound_t'] = self._now
            brg = _bearing(pos, center)
            dest = _point_at(center, (brg + 180.0) % 360.0, max(r - 20.0, 0.0))
            dest = self._safe_point(pos, dest)
            if guid in self._dead or not self._alive(obj):
                continue
            if self.USE_DROPTARGET:
                self._cmd(guid, obj.attack_drop_target_all)
            self._cmd(guid, obj.plotted_course, [dest])
            self._log('warning', '出界[%s] 距任务区 %.0fkm > 硬界 %.0fnm，已放弃目标并回飞'
                      % (name, out_km, self.HARD_NM))
            self._notify('【出界】%s 距任务区 %.0fkm，已召回'
                         % (name, out_km))
            n += 1
        return n

    # ------------------------------------------------------------------
    # 九、入口
    # ------------------------------------------------------------------
    def _capability_report(self, situation, tag):
        """
        开局自检：每架飞机到底带没带空战弹、射程从哪来。

        这一段专门用来回答“为什么开火 0”——如果这里就是 0 架可开火，
        那问题在挂载/射程，不在开火条件。
        """
        n_air = n_aam = 0
        lines = []
        for guid, name, cat, raw in self._own_units(situation):
            if cat and str(cat) != 'Aircraft':
                continue
            obj = self.get_unit(guid)
            if obj is None:
                continue
            n_air += 1
            ammo = self._best_aam(obj)
            if not ammo:
                if len(lines) < 8:
                    lines.append('%s: 无对空弹' % name)
                continue
            n_aam += 1
            wid, load, rng = ammo
            if len(lines) < 8:
                lines.append('%s: %s×%d 射程%.0fkm' % (name, wid, load, rng))
        self._log('info', '能力自检（%s）：在空/可用飞机 %d 架，其中带对空弹 %d 架'
                  % (tag, n_air, n_aam))
        for ln in lines:
            self._log('info', '   · %s' % ln)
        if self.MSG_ENABLE and n_air:
            self._notify('【自检】飞机%d 架，带对空弹%d 架' % (n_air, n_aam))

    def initial(self, situation):
        """
        战前规划：只记录每个单元的初始位置（作为“家”），不改任何配置。

        :param situation: tuple, (units dict, contacts dict)
        """
        self._log('info', 'AGENT_BUILD=2026-11-16-TAC-RED-02 '
                          '（Monitor / AirCombat / Evade + 边界守卫 + 消息栏）')
        self._log('info', '本次实验设置 RUN_TAG = %s' % self.RUN_TAG)
        try:
            for guid, name, cat, raw in self._own_units(situation):
                obj = self.get_unit(guid)
                p = (_pos(obj) if obj is not None else None) or _pos(raw)
                if p:
                    self._home[guid] = p
            self._log('info', '记录初始位置 %d 个单元' % len(self._home))
        except Exception as e:
            self._log('error', 'initial 记录初始位置异常: %s' % e)

    def step(self, time_elapse, situation):
        """
        每个决策周期（默认 30 秒仿真时间）调用一次。

        顺序：监控 → 自卫 → 空战 → 边界守卫。

        :param time_elapse: int, 推演已过时间（秒）
        :param situation: tuple, (units dict, contacts dict)
        """
        self._cycle += 1
        self._used = 0
        self._now = float(time_elapse or 0)
        try:
            # 开局第 1 个周期 + 第 20 周期各做一次“能力自检”
            # （第 1 周期可能还没换上我们设的挂载，第 20 周期是换好之后的真实状态）
            if self._cycle in (1, 20):
                self._capability_report(
                    situation, '开局' if self._cycle == 1 else '换挂载后')
            threats = self.monitor(situation) if self.ENABLE_MONITOR else {}
            n_evade = self.evade(situation) if self.ENABLE_EVADE else 0
            n_fire = self.air_combat(situation) if self.ENABLE_AIR_COMBAT else 0
            n_bound = self.boundary_guard(situation) if self.ENABLE_BOUNDARY else 0
            if self._cycle % 20 == 0 or n_evade or n_fire or n_bound:
                self._log('info', 'TAC 汇总：周期%d 威胁%d 自卫%d 开火%d 出界纠正%d '
                                  '指令%d'
                          % (self._cycle, len(threats), n_evade, n_fire,
                             n_bound, self._used))
        except Exception as e:
            self._log('error', 'step 异常: %s' % e)
        finally:
            # 消息栏最后统一推送（任何分支出错都不影响）
            try:
                self._flush_msgs()
            except Exception as e:
                self._log('warning', '消息推送异常: %s' % e)

    def deduction_end(self):
        """推演结束（本智能体只打一行统计）。"""
        try:
            self._log('info', '推演结束：周期 %d，实测弹速 %d 型'
                      % (self._cycle, len(self._v0_est)))
        except Exception:
            pass
