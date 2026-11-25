# -*- coding:utf-8 -*-
r"""
蓝方规则智能体（人机协同-人人版） —— 2026 全国兵棋推演大赛

按 `蓝方人人总任务.txt` + `蓝方人人任务列表.xlsx` 实现，功能分七块：

    ① 总条令（set_side_rules）        —— 对空自由开火 / 对海·对地·对潜限制开火，
                                         攻击不忽略计划航线、被攻击不忽略电磁管控、
                                         燃油·武器状态不返航、干扰机与声呐打开
    ② 总条令武器使用规则（set_side_air_wra）
                                      —— AIM-120D / AIM-260 / AIM-120C-7 三型弹：
                                         自动开火距离 60/90/50 海里；
                                         制导武器-未指定 → 不使用武器；
                                         对第5代/第四代战斗机 → 齐射 1 枚
    ③ 飞机挂载（set_aircraft_loadouts）—— 19 组（F/A-18F、F-35B/C/A、EA-18G、
                                         E-2D、MQ-25A、B-2A、F-15E、F-2A/B、幻影、
                                         F-16V/B、MQ-1C、RQ-4B、MH-60R）
    ④ 舰船条令（set_ship_doctrines）  —— 邦克山 / 阿利伯克 / 摩耶 对空限制开火
    ⑤ 任务（SUPPORT_TASKS / PATROL_TASKS）
                                      —— 支援 31 条 + 巡逻 3 条（反潜 / 无人机送死 / 打航母）
                                         其中 AAAAAAAA/BBBBBBBBB/CCCCCCCC 为地面单位机动任务，
                                         「北船机动」为摩耶/DDH 的水面机动任务
    ⑥ 战前移动（PREWAR_MOVES）        —— 装甲车/伪装防空车/反舰导弹排/防空营等
                                         开局直接 M 到指定点，再交给任务航路
                                         （REASSIGN_TASKS 负责“取消分配→归位→重新分配”）
    ⑦ 电磁管控（set_emcon_not_inherit）—— 爱国者#1 取消“与上级保持一致”

    说明：原“摩耶/日向级直升驱逐舰全速前往 (52.858177, 3.874748)”与
          “装甲车加速向南逃跑”两段机动已取消（SHIP_RUSH / GROUND_MOVES 置空，
          代码保留在注释里，需要时填回即可）。

------------------------------------------------------------------
一、文件放在哪里、怎么导入
------------------------------------------------------------------
平台运行时把 <安装目录>\intelligent\ai 加入 sys.path，智能体按
    engine.LingYi.entitys.*
导入平台实体库；entitys 目录与 engine\LingYi 同级。本文件放在
    <安装目录>\intelligent\ai\engine\LingYi\
下（与 entitys 同级）即可。

客户端导入：进入推演房间 → “智能体”面板 → 推演方选 **蓝方** →
“导入/选择脚本” → 选中本文件 → 规则智能体 → 开始推演。
（战前规划阶段调用一次 initial()，之后每个决策周期调用一次 step()。）

运行环境：Python 3.9（entitys 下 gameunit.pyd / deduce_RL.pyd 是 cp39 扩展）。

------------------------------------------------------------------
二、任务表怎么改
------------------------------------------------------------------
· 支援任务：SUPPORT_TASKS，每行
    (任务名, 起点, 终点, 执行单元选择器, 'single'/'two' 编队)
  执行单元留空 () 表示“只建任务、不分配单元”（后续手动分配）。
· 战前移动：PREWAR_MOVES，每行 (单元选择器组, (纬度, 经度))；
  要“M 到位再走任务航线”的单元，还要把任务名登记到 REASSIGN_TASKS，
  否则平台会用默认站位覆盖战前移动（开局先回系统原点）。
· 巡逻任务：PATROL_TASKS，每行
    (任务名, 巡逻类型, 四点巡逻区, 执行单元选择器, 单元条令, 备注)
· 单元名对不上：看日志里 “蓝方单元清单(...) 名称 [dbid]”，
  把真实名字的关键字补进对应 _sel(...) 即可（改完必须重开一局）。
  _sel 支持 avoid=('霍克',) 这种排除词，避免“地空导弹连”误命中“霍克地空导弹连”。

------------------------------------------------------------------
三、指令条数限制
------------------------------------------------------------------
平台启动参数 agentOrderCountLimit = 500，按“任意 10 秒窗口 ≤ 500 条”计，
超出会被静默丢弃。本智能体开局约 400 条，内置 _OrderBudget 真·滚动窗口
节流（超窗口就 sleep 到滑出，不丢包）。
"""

import logging
import os
import re
import time

try:  # 平台运行环境
    from engine.LingYi.entitys.global_util import *
    from engine.LingYi.entitys.agent_base import RuleAgentBase
    from engine.LingYi.entitys.player import *
    try:
        from engine.LingYi.entitys.data import query_data
    except Exception:                                   # pragma: no cover
        query_data = None
except ImportError:                                     # 本地工作区（仅便于看代码）
    from entitys.global_util import *
    from entitys.agent_base import RuleAgentBase
    from entitys.player import *
    try:
        from entitys.data import query_data
    except Exception:                                   # pragma: no cover
        query_data = None

# 战术智能体（独立模块）：物理作战域三维监控 2.3.1 + 地空导弹营攻击与自卫 2.3.5。
# 放在同目录或 engine/LingYi/ 下均可；导入失败不影响主智能体（置 None 即跳过）。
try:
    from engine.LingYi.BattlefieldMonitor import BattlefieldMonitor
    from engine.LingYi.SamBattalionDefense import SamBattalionDefense
except ImportError:                                     # 本地工作区
    try:
        from BattlefieldMonitor import BattlefieldMonitor
        from SamBattalionDefense import SamBattalionDefense
    except Exception:                                   # pragma: no cover
        BattlefieldMonitor = None
        SamBattalionDefense = None


# ======================================================================
# 指令配额：包住平台的 _game_server，按“任意 10 秒 ≤ 460 条”节流
# ======================================================================
class _OrderBudgetExceeded(Exception):
    """本周期已下发指令数触到硬上限（内部信号，不外抛给平台）。"""
    pass


class _OrderBudget(object):
    """
    统计并节流“下发给推演引擎的指令条数”。

    平台限制：任意 10 秒内 ≤ 500 条（agentOrderCountLimit），超出的指令会被
    “智能体指令条数超出数量限制，已被取消下发”直接丢掉。
    做法：① 每决策周期软预算；② 真·滚动 10 秒窗口，超窗口就 sleep 到滑出。
    """

    WINDOW_SEC = 10.0
    WINDOW_LIMIT = 460          # 500 留 40 条余量
    MAX_SLEEP = 15.0
    MAX_SLEEP_PER_CYCLE = 12.0

    def __init__(self, real, hard_limit):
        self._real = real
        self.hard_limit = int(hard_limit)
        self.used = 0
        self._stamps = []           # [(下发时刻, 条数)]，跨周期不清零
        self.paced_sleep = 0.0
        self.cycle_sleep = 0.0
        self.cycle_sleep_cap = self.MAX_SLEEP_PER_CYCLE

    def reset(self, hard_limit=None):
        self.used = 0
        self.cycle_sleep = 0.0
        self.cycle_sleep_cap = self.MAX_SLEEP_PER_CYCLE
        if hard_limit is not None:
            self.hard_limit = int(hard_limit)

    def _prune(self, now):
        cut = now - self.WINDOW_SEC
        i = 0
        for t, _c in self._stamps:
            if t >= cut:
                break
            i += 1
        if i:
            del self._stamps[:i]

    def _win_total(self):
        return sum(c for _t, c in self._stamps)

    def _pace(self, cost):
        """窗口内放得下返回 True（必要时先 sleep）；放不下返回 False。"""
        slept = 0.0
        while True:
            now = time.time()
            self._prune(now)
            if self._win_total() + cost <= self.WINDOW_LIMIT:
                return True
            if not self._stamps:
                return True
            wait = self.WINDOW_SEC - (now - self._stamps[0][0]) + 0.02
            if wait <= 0.0:
                return False
            if slept + wait > self.MAX_SLEEP:
                return False
            if self.cycle_sleep + slept + wait > self.cycle_sleep_cap:
                return False
            time.sleep(wait)
            slept += wait
            self.paced_sleep += wait
            self.cycle_sleep += wait

    def __getattr__(self, item):
        real = self.__dict__.get('_real')
        fn = getattr(real, item)
        if not callable(fn) or not (item.startswith('api_')
                                    or item in ('unit_new_position',
                                                'agent_message_output')):
            return fn

        def wrapper(*a, **k):
            cost = 1
            # 建任务时，每个坐标点还会额外产生一条 AddReferencePoint
            if item.startswith('api_create_') and item.endswith('_mission'):
                pts = a[2] if item.endswith('support_mission') else (
                    a[3] if item.endswith('patrol_mission') else None)
                if isinstance(pts, (list, tuple)):
                    cost += sum(1 for p in pts if isinstance(p, (list, tuple)))
            if self.used + cost > self.hard_limit:
                raise _OrderBudgetExceeded('%s 触到本周期硬上限 %d 条'
                                           % (item, self.hard_limit))
            if not self._pace(cost):
                raise _OrderBudgetExceeded('%s 触到 10 秒窗口上限 %d 条'
                                           % (item, self.WINDOW_LIMIT))
            now = time.time()
            self._prune(now)
            self.used += cost
            self._stamps.append((now, cost))
            res = fn(*a, **k)
            # 新建出来的任务对象也要指向计数器，否则任务级条令会绕过计数
            if item.startswith('api_create_') and item.endswith('_mission'):
                try:
                    if res is not None and hasattr(res, '_game_server'):
                        res._game_server = self
                except Exception:
                    pass
            return res
        return wrapper


# ======================================================================
# 单元选择器
# ======================================================================
def _sel(key, *nums, avoid=()):
    """
    构造一个“单元选择器”。

    :param key: str 或 tuple/list，名称关键字（任一命中即可，忽略空格/引号/大小写）
    :param nums: int 或 'a-b'，舷号（单元名里 #n 的 n）；不传表示该型全部单元
    :param avoid: str 或 tuple/list，名称里含这些词就排除
                  （例：“地空导弹连”会命中“霍克地空导弹连”，用 avoid=('霍克',) 排掉）
    :return: dict, {'keys': (...), 'nums': (...), 'avoid': (...)}

    例：_sel(('f/a-18f', 'f18'), 1, 2)
        _sel('mq-1c', '1-4')
        _sel(('地空导弹连',), 1, avoid=('霍克', 'hawk'))
    """
    if isinstance(key, (list, tuple)):
        keys = tuple(str(k) for k in key)
    else:
        keys = (str(key),)
    if isinstance(avoid, (list, tuple)):
        avoid_keys = tuple(str(k) for k in avoid if k)
    else:
        avoid_keys = (str(avoid),) if avoid else ()
    out = []
    for n in nums:
        if isinstance(n, int):
            out.append(n)
            continue
        s = str(n).strip()
        m = re.match(r'^(\d+)\s*[-~]\s*(\d+)$', s)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif s.isdigit():
            out.append(int(s))
    return {'keys': keys, 'nums': tuple(out), 'avoid': avoid_keys}


_PUNCT_RE = re.compile(r'[\s\u3000"“”\'‘’()（）\[\]【】《》<>]')
_NUM_RE = re.compile(r'#\s*(\d+)')


def _norm(text):
    """
    名称归一化：小写、去掉空白与各类引号/括号、统一全半角标点、去掉 - . / ，
    使“F/A-18F型 战斗机 #1”“F-35C 型“闪电II” 战斗机 #1”都能对上同一关键字。
    """
    t = str(text or '').lower()
    t = _PUNCT_RE.sub('', t)
    t = t.replace('：', ':').replace('，', ',').replace('。', '.')
    t = t.replace('—', '-').replace('–', '-').replace('－', '-')
    t = t.replace('-', '').replace('.', '').replace('/', '')
    return t


def _unit_num(name):
    """取单元名里的舷号（#n）；取不到再退回结尾数字。"""
    m = _NUM_RE.search(str(name or ''))
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)\s*$', str(name or ''))
    return int(m.group(1)) if m else None


# ======================================================================
# 智能体
# ======================================================================
class Agent(RuleAgentBase):
    """蓝方规则智能体（人机协同-人人版）"""

    CYCLE_ORDER_BUDGET = 400
    # 2 机编队任务是否勾选“飞机数低于编队规模要求不能起飞”
    TWO_SHIP_USE_FLIGHT_SIZE = True
    # 支援任务的执行单元是否强制“雷达开”（旧蓝方样例是这么做的；
    # 若想让隐身机保持静默，把它改成 False 即可）
    SUPPORT_RADAR = True

    # ------------------------------------------------------------------
    # ① 总条令
    # ------------------------------------------------------------------
    # 交火规则：对空自由开火；对海/对地/对潜限制开火（仅限手动开火）
    RULE_HOLD_SURFACE = True

    # ------------------------------------------------------------------
    # ② 总条令武器使用规则
    #    (武器DBID元组, 名称, 自动开火距离海里)
    # ------------------------------------------------------------------
    SIDE_AIR_WRA = (
        (('51', '3608'), 'AIM-120D型“阿姆拉姆”先进中程空空导弹', '60'),
        (('3567',), 'AIM-260 JATM 联合先进战术导弹', '90'),
        (('718',), 'AIM-120C-7型“阿姆拉姆”先进中程空空导弹', '50'),
    )
    # 自动开火距离覆盖的 4 类空中目标
    AIR_WRA_RANGE_TARGETS = (
        WRA_WeaponTargetType.Air_Contact_Unknown_Type,    # 空中感知-未知类型 1999
        WRA_WeaponTargetType.Aircraft_Unspecified,        # 飞机-未指定       2000
        WRA_WeaponTargetType.Aircraft_5th_Generation,     # 飞机-第五代战斗机 2001
        WRA_WeaponTargetType.Aircraft_4th_Generation,     # 飞机-第四代战斗机 2002
    )
    # 齐射武器数：制导武器-未指定 → 不使用武器；第5代/第四代 → 1 枚
    AIR_WRA_SALVO = (
        (WRA_WeaponTargetType.Guided_Weapon_Unspecified, '0'),
        (WRA_WeaponTargetType.Aircraft_5th_Generation, '1'),
        (WRA_WeaponTargetType.Aircraft_4th_Generation, '1'),
    )

    # ------------------------------------------------------------------
    # ③ 飞机挂载
    #    (单元选择器, 挂载名关键字[须全部命中], 说明)
    #    —— 挂载 ID 运行期按“本机 DBID + 挂载名”从 model.db 现场查；
    #       表里没有的飞机保持系统默认挂载。
    #      （关键字已按 model.db 实库逐条核对过，见 README）
    # ------------------------------------------------------------------
    AIRCRAFT_LOADOUTS = (
        # 福特级航母
        (_sel(('f/a-18f', 'fa-18f', 'f18'), 1, 2, 3),
         ['aim-120a', '先进瞄准', '重型'],
         'AIM-120A 先进中程空空导弹, 先进瞄准前视红外系统, 重型挂载'),
        (_sel(('f/a-18f', 'fa-18f', 'f18'), 4, 5, 6),
         ['agm-154c-1', '短程'],
         'AGM-154C-1 联合防区外武器[内装多级侵彻战斗部], 先进瞄准前视红外吊舱, 短程'),
        (_sel(('e-2d', 'e2d'), 1), ['空中预警'],
         '空中预警(AEW)'),
        (_sel(('f-35c', 'f35c'), 1, 2), ['aim-260', 'internal'],
         'A/A: AIM-260 JATM, Internal Only (Standard CAP)'),
        (_sel(('ea-18g', 'ea18g'), 1, 2), ['agm-88e', 'short'],
         'AGM-88E AARGM-ER, Short-Range'),
        (_sel(('mq-25a', 'mq25a'), 1, 2), ['油箱'],
         '油箱'),
        # 阿斯图机场
        (_sel(('b-2a', 'b2a'), 1, 2), ['lrasm'],
         'AGM-158C LRASM'),
        (_sel(('f-15e', 'f15e'), 1, 2), ['gbu-53', 'maximum'],
         'GBU-53/B SDB-II, Sniper XR Pod, Maximum'),
        # 直升驱逐舰
        (_sel(('f-35b', 'f35b'), 1, 2), ['aim-120c-7', 'internal'],
         'A/A: AIM-120C-7 AMRAAM, Internal Only (Standard CAP)'),
        # CS 机场
        (_sel(('f-2b', 'f2b'), 1, 2), ['asm-3', 'heavy'],
         'ASM-3 Type XX, J/AQQ-2 Pod [FLIR], Heavy'),
        (_sel(('f-15e', 'f15e'), 3, 4), ['aim-120c-7', '狙击手', '重型'],
         '空对空: AIM-120C-7 高级中程空对空导弹, “狙击手”XR瞄准吊舱, 重型挂载'),
        (_sel(('f-35a', 'f35a'), 1, 2), ['aim-260', 'internal'],
         'A/A: AIM-260 JATM, Internal'),
        (_sel(('f-2a', 'f2a'), 1, 2, 3), ['asm-2', '重型'],
         'ASM-2型反舰导弹, J/AQQ-2型探测吊舱, 重型挂载'),
        # 奥尔良机场
        (_sel(('幻影', 'mirage'), 1, 2, 3, 4), ['米卡'],
         '空对空: “米卡”空空导弹'),
        (_sel(('rq-4b', 'rq4b', '全球鹰'), 1), ['侦察'],
         '侦察[机载光电/红外/逆合成孔径雷达]'),
        # 奥尔良机场 F-16V：空对空 AIM-120C-7 + “狙击手”XR 瞄准吊舱 + 重型挂载 402
        (_sel(('f-16v', 'f16v'), 1, 2, 3, 4), ['aim-120c-7', '狙击手', '重型'],
         '空对空: AIM-120C-7 高级中程空对空导弹, “狙击手”XR瞄准吊舱[前视红外], 重型挂载 402'),
        # 卡皮凯机场
        (_sel(('f-16b', 'f16b'), 1, 2), ['aim-7m', '重型'],
         'AIM-7M型“麻雀”空空导弹, AN/ALQ-184 电子干扰吊舱, 重型挂载'),
        (_sel(('mq-1c', 'mq1c'), 1, 2, 3, 4), ['agm-179'],
         'AGM-179 JAGM'),
        # 舰载直升机（邦克山 / 阿利伯克）
        (_sel(('mh-60r', 'mh60r'), 1, 2), ['mk50', '远程'],
         'Mk50型“梭鱼”式鱼雷, 声呐浮标, 远程'),
    )

    # ------------------------------------------------------------------
    # ④ 三艘水面舰：对空限制开火（仅限手动开火）
    # ------------------------------------------------------------------
    SHIP_AIR_HOLD = (
        _sel(('邦克山', 'bunker')),
        _sel(('阿利伯克', 'arleigh')),
        _sel(('摩耶', 'maya')),
    )

    # ------------------------------------------------------------------
    # ⑤ 支援任务（蓝方人人任务列表.xlsx「支援任务」30 条）
    #    (任务名, 起点, 终点, 执行单元, 'single'/'two' 编队)
    #    执行单元为 () 表示只建任务、不分配单元（后续手动分配）
    # ------------------------------------------------------------------
    SUPPORT_TASKS = (
        ('F18-1', (46.957931, -11.657206), (46.710520, -8.387315),
         (_sel(('f/a-18f', 'fa-18f', 'f18'), 1),), 'single'),
        ('F18-2', (47.960824, -12.120344), (48.588744, -8.629481),
         (_sel(('f/a-18f', 'fa-18f', 'f18'), 2, 3),), 'single'),
        ('左35-1', (46.442894, -11.738868), (45.904402, -8.318197),
         (_sel(('f-35c', 'f35c'), 1),), 'single'),
        ('左35-2', (47.591811, -11.878025), (47.936144, -8.383892),
         (_sel(('f-35c', 'f35c'), 2),), 'single'),
        ('F18-456', (48.268485, -12.304778), (49.178437, -9.250657),
         (_sel(('f/a-18f', 'fa-18f', 'f18'), 4, 5, 6),), 'single'),
        ('预警机', (46.932814, -12.377202), (46.740486, -12.121306),
         (_sel(('e-2d', 'e2d'), 1),
          _sel(('mq-25a', 'mq25a'), 1, 2)), 'single'),
        ('电子战1', (49.052079, -12.260208), (49.812009, -10.133023),
         (_sel(('ea-18g', 'ea18g'), 1),), 'single'),
        ('电子战2', (46.686616, -11.196618), (46.532605, -9.523710),
         (_sel(('ea-18g', 'ea18g'), 2),), 'single'),
        ('下15-1', (43.989657, 0.455291), (45.295289, 0.505006),
         (_sel(('f-15e', 'f15e'), 1),), 'single'),
        ('下15-2', (44.728397, 1.246514), (46.015364, 1.180234),
         (_sel(('f-15e', 'f15e'), 2),), 'single'),
        ('轰炸机', (44.843458, 2.037761), (46.052979, 2.064965),
         (_sel(('b-2a', 'b2a'), 1, 2),), 'single'),
        ('幻影1', (47.727615, 1.759148), (47.435836, 1.812716),
         (_sel(('幻影', 'mirage'), 1, 2),), 'two'),
        ('幻影2', (47.777927, 2.411321), (47.577860, 2.723768),
         (_sel(('幻影', 'mirage'), 3, 4),), 'two'),
        ('中16-1', (47.937144, 1.319230), (47.241585, 0.990572),
         (_sel(('f-16v', 'f16v'), 1, 2),), 'single'),
        ('中16-2', (48.247573, 2.762803), (47.846074, 4.152826),
         (_sel(('f-16v', 'f16v'), 3, 4),), 'single'),
        ('中预警机', (48.001774, 2.063845), (47.890807, 2.115018),
         (_sel(('rq-4b', 'rq4b', '全球鹰'), 1),), 'single'),
        ('前16-1', (48.827852, 0.648538), (48.184856, 0.426521),
         (_sel(('f-16b', 'f16b'), 1),), 'single'),
        ('前16-2', (49.266587, 1.878271), (48.695063, 2.831148),
         (_sel(('f-16b', 'f16b'), 2),), 'single'),
        ('北35-1', (53.758908, 5.370089), (53.140057, 3.551135),
         (_sel(('f-35b', 'f35b'), 1), _sel(('f-35a', 'f35a'), 1)), 'single'),
        ('北35-2', (53.169186, 5.909630), (52.290346, 5.339826),
         (_sel(('f-35b', 'f35b'), 2), _sel(('f-35a', 'f35a'), 2)), 'single'),
        ('北15-1', (54.320926, 5.414372), (53.857979, 4.038826),
         (_sel(('f-15e', 'f15e'), 3),), 'single'),
        ('北15-2', (53.558437, 6.784545), (52.755371, 6.328371),
         (_sel(('f-15e', 'f15e'), 4),), 'single'),
        # 北2B / 北2A：分配了执行单元，但**开局不启动**（见 INACTIVE_MISSIONS）
        ('北2B', (55.002778, 7.005483), (54.748357, 6.317195),
         (_sel(('f-2b', 'f2b'), 1, 2),), 'single'),
        ('北2A', (55.816587, 7.116806), (54.816587, 8.006806),
         (_sel(('f-2a', 'f2a'), 1, 2, 3),), 'single'),
        # ---- 地面/水面单位机动任务 ----
        #   执行单元都是“先战前 M 到位、再分配任务”的，并且登记在 REASSIGN_TASKS 里：
        #   initial() 末尾会“取消分配 → 重新 M → 重新分配”，避免平台用默认站位
        #   （系统初始起点）覆盖战前移动（与红方蟾蜍/雷鸣同一套做法）。
        ('AAAAAAAA', (49.305691, -1.208069), (49.348499, -1.186002),
         (_sel(('装甲车', 'armored', 'lav'), 1, 5),
          _sel(('伪装防空车',), 1)), 'single'),
        ('BBBBBBBBB', (49.223866, -0.076773), (49.259276, -0.088111),
         (_sel(('装甲车', 'armored', 'lav'), 2, 4),
          _sel(('伪装防空车',), 2),
          _sel(('反舰导弹排',), 1, 5)), 'single'),
        ('CCCCCCCC', (49.902856, 1.227651), (49.931282, 1.188216),
         (_sel(('装甲车', 'armored', 'lav'), 3),), 'single'),
        # 以下 3 条：只建任务，不分配单元（后续手动分配）
        ('左左左左左左', (46.558828, 0.362615), (43.026544, 0.233935), (), 'single'),
        ('中中中中中中', (47.081605, 3.859811), (44.042966, 6.807560), (), 'single'),
        ('右右右右右右', (49.398257, 7.499765), (48.662679, 13.269188), (), 'single'),

        # ---- 北船机动：摩耶级驱逐舰 + 直升机驱逐舰 ----
        #   任务编辑：取消 1/3 规则；速度高度—水面舰艇航速—出航油门 = 最大
        #   （原“两舰全速去 (52.858177,3.874748) 集结点”的航线与任务已取消）
        ('北船机动', (53.579501, 5.820036), (53.460562, 5.227051),
         (_sel(('摩耶', 'maya')), _sel(('izumo', '出云', '直升驱逐舰', 'ddh'))),
         'single'),

        # 运输机逃跑：C-5M #1#2，关闭“低于编队数不起飞”与 1/3 规则（single 分支默认即如此）
        ('运输机逃跑', (47.349478, -21.463019), (53.818499, -34.760939),
         (_sel(('c-5m', 'c5m'), 1, 2),), 'single'),
    )

    # ------------------------------------------------------------------
    # ⑥ 巡逻任务（蓝方人人任务列表.xlsx「巡逻任务」3 条）
    #    任务编辑项：取消 1/3 规则、取消“飞机数低于编队要求不起飞”、
    #                取消“对巡逻区外目标分析(OPA)”、取消“对武器射程内目标分析(WWR)”
    #    任务条令（三条统一）：对地/对海/对潜自由开火 +
    #                燃油状态-返航=否、武器状态-返航=否、武器耗光允许航炮
    # ------------------------------------------------------------------
    # 三条巡逻任务共用的单元条令
    PATROL_UNIT_DOCTRINE = {
        'land': WeaponControlStatus.Free,
        'surface': WeaponControlStatus.Free,
        'subsurface': WeaponControlStatus.Free,
    }

    PATROL_TASKS = (
        # 反潜巡逻
        ('反潜', MissionPatrolType.ANTI_SUBMARINE,
         ((47.715300, -12.926600), (46.903400, -12.926600),
          (46.903400, -11.365600), (47.715300, -11.365600)),
         (_sel(('mh-60r', 'mh60r'), 1),
          _sel(('mh-60r', 'mh60r'), 2)),
         'MH-60R#1#2，对地/对海/对潜自由开火'),

        # 海上控制巡逻（无人机送死）：**开局不启动，但任务要建好**
        ('无人机送死', MissionPatrolType.SEA_CONTROL,
         ((50.301436, -0.651409), (49.826558, -0.537026),
          (50.088102, 0.711629), (50.475332, 0.369963)),
         (_sel(('mq-1c', 'mq1c'), 1, 2, 3, 4),),
         'MQ-1C#1~4，海上控制巡逻'),

        # 反水面及地面战巡逻（打航母）
        #   佛蒙特号开局直接分配到这里（不再打战斧），深度另行设为 40 米
        ('打航母', MissionPatrolType.ANTI_MLP,
         ((47.452600, -6.604840), (47.452600, -5.587890),
          (46.978400, -5.587890), (46.978400, -6.604840)),
         (_sel(('佛蒙特', 'vermont', 'ssn792', 'ssn 792'),),),
         '反水面及地面战巡逻（佛蒙特号潜艇）'),
    )

    # ------------------------------------------------------------------
    # ⑦-1 开局 BOL 纯方位打击
    #     ⚠ 已按最新要求**取消**（佛蒙特、阿利伯克都不打战斧了），
    #       打击代码保留在 do_bol_strikes() 里，以后要恢复只需把条目填回本表。
    # ------------------------------------------------------------------
    BOL_MAX_CMD_CHARS = 295
    BOL_STRATEGIES = ('course', 'plain', 'unit', 'qty1', 'mount0')

    BOL_STRIKES = ()
    # 注释掉的两条原来的打击计划（需要时原样贴回 BOL_STRIKES 即可）：
    #   佛蒙特  ：UGM-109E（377/810）全部 → (49.717689,-2.193483)，
    #             途经 (49.936685,-0.209524) (49.637561,-0.354083) (50.053257,-0.382165)
    #   阿利伯克：RGM-109I（2941）全部   → (49.717689,-2.193483)，
    #             途经 (49.856532,-1.058552) (49.566030,-1.099090) (49.997354,-1.207326)

    # ------------------------------------------------------------------
    # ⑦-2 开局潜艇深度（不打击，深度按 -40 米，即水下 40 米）
    # ------------------------------------------------------------------
    PREWAR_SUB_DEPTH = (
        (_sel(('佛蒙特', 'vermont', 'ssn792', 'ssn 792')), 40),
    )

    # ------------------------------------------------------------------
    # ⑦ 开局不启动的任务（建好即停用，后续手动启用）
    # ------------------------------------------------------------------
    INACTIVE_MISSIONS = ('F18-456', '北2B', '北2A', '无人机送死')

    # ------------------------------------------------------------------
    # ⑦ 开局机动：**已取消**
    #    原计划：摩耶级驱逐舰 / 日向级直升驱逐舰 全速前往 (52.858177, 3.874748)。
    #    现在两舰改为分配给「北船机动」支援任务（见 SUPPORT_TASKS），不再单独下航线。
    #    需要恢复时，把下面注释里的两行填回 SHIP_RUSH 即可。
    # ------------------------------------------------------------------
    SHIP_RUSH = ()
    # SHIP_RUSH = (
    #     (_sel(('摩耶', 'maya')), (52.858177, 3.874748)),
    #     (_sel(('izumo', '出云', '直升驱逐舰', 'ddh')), (52.858177, 3.874748)),
    # )

    # ------------------------------------------------------------------
    # ⑦-2 地面部队“加速向南逃跑”：**已取消**
    #      装甲车 #1~#5 改为“战前 M 到位 + 分配 AAAAAAAA/BBBBBBBBB/CCCCCCCC 任务”，
    #      见 PREWAR_MOVES / SUPPORT_TASKS。需要恢复时把注释里的三条填回 GROUND_MOVES。
    #      （GROUND_FALLBACK_CYCLES / WATCH_RELEASE 保留：玩家按 U 取消分配时的处理不变）
    # ------------------------------------------------------------------
    GROUND_THROTTLE = Throttle.Flank
    GROUND_FALLBACK_CYCLES = 3
    WATCH_RELEASE = True
    GROUND_MOVES = ()
    # GROUND_MOVES = (
    #     ((_sel(('装甲车', 'armored', 'lav'), 1, 5),), (46.377482, -0.684828)),
    #     ((_sel(('装甲车', 'armored', 'lav'), 2, 4),), (46.392833, 1.114792)),
    #     ((_sel(('装甲车', 'armored', 'lav'), 3),), (46.991967, 3.980198)),
    # )

    # ------------------------------------------------------------------
    # ⑦-3 战前移动（战前部署—移动单元）：[(单元选择器组, (纬度, 经度)), ...]
    #     平台限制：距初始位置 ≤20 km、需符合地形、只在战前规划阶段有效。
    #     其中要进 AAAAAAAA/BBBBBBBBB/CCCCCCCC 的单元同时登记在 REASSIGN_TASKS，
    #     initial() 末尾会“取消分配 → 重新 M → 重新分配”，开局不会被拉回系统原点。
    # ------------------------------------------------------------------
    PREWAR_MOVES = (
        # 装甲车 #1~#5
        ((_sel(('装甲车', 'armored', 'lav'), 1),), (48.977815, -1.309595)),
        ((_sel(('装甲车', 'armored', 'lav'), 2),), (48.958002, 0.120440)),
        ((_sel(('装甲车', 'armored', 'lav'), 3),), (49.576326, 1.655070)),
        ((_sel(('装甲车', 'armored', 'lav'), 4),), (48.968968, -0.038440)),
        ((_sel(('装甲车', 'armored', 'lav'), 5),), (48.829125, -0.856644)),
        # 伪装防空车 #1#2
        ((_sel(('伪装防空车',), 1),), (48.864347, -0.869234)),
        ((_sel(('伪装防空车',), 2),), (48.958002, 0.120440)),
        # 爱国者 #1
        ((_sel(('爱国者', 'patriot', 'pac'), 1),), (48.831155, 1.540032)),
        # 地空导弹连 #1#2
        #   关键字“地空导弹连”会同时命中“霍克地空导弹连”和“爱国者地空导弹连”，
        #   用 avoid 把这三种防空营区分开（否则一个单元会被 M 到别的营的点位）。
        ((_sel(('地空导弹连',), 1,
               avoid=('霍克', 'hawk', '爱国者', 'patriot', 'pac')),),
         (48.822373, -1.267036)),
        ((_sel(('地空导弹连',), 2,
               avoid=('霍克', 'hawk', '爱国者', 'patriot', 'pac')),),
         (48.788107, 0.151154)),
        # 霍克地空导弹连 #1
        ((_sel(('霍克', 'hawk'), 1),), (49.229971, -2.048046)),
        # 捷羚导弹排 #1
        ((_sel(('捷羚', 'tien'), 1),), (49.427542, -2.551515)),
        # 反舰导弹排 #4
        ((_sel(('反舰导弹排',), 4),), (49.229836, -2.033080)),
        # RT 火箭炮 #2
        ((_sel(('rt火箭炮', '火箭炮', 'mlrs'), 2),), (49.181728, -2.233840)),
    )

    # ------------------------------------------------------------------
    # ⑦-4 “取消分配 → 归位 → 重新分配”的任务（清掉平台默认站位缓存）
    # ------------------------------------------------------------------
    REASSIGN_TASKS = ('AAAAAAAA', 'BBBBBBBBB', 'CCCCCCCC')

    # 地面/水面单位的机动任务：不套用“对空自由开火 + 开雷达”这套空中条令
    GROUND_SUPPORT_TASKS = ('AAAAAAAA', 'BBBBBBBBB', 'CCCCCCCC', '北船机动')

    # 水面舰艇任务的油门：{任务名: (出航油门, 阵位油门)}；None = 该项不设置
    SHIP_THROTTLE_TASKS = {
        # 北船机动：任务编辑—速度高度设置—水面舰艇航速—出航油门 = 最大
        #   （Throttle.Flank 是枚举里最快的一档，下发时转成 4 = 最大/加力）
        '北船机动': (Throttle.Flank, None),
    }

    # ------------------------------------------------------------------
    # ⑦-5 要“取消电磁管控设置—与上级保持一致”的单元（目前是爱国者#1）
    #     平台 SDK 只提供了 doctrine_SetEMCON_Inherit()（= 勾选“与上级一致”），
    #     没有反向接口；这里用两步达到同样效果：
    #       ① unit.EMCON_Obey_doctrine(False) —— 单元不再遵循上级电磁管控条令；
    #       ② unit.doctrine_switch_radar(True/False) —— 把条令里的雷达显式设为
    #          主动/被动（显式值即“不再继承上级”，对应 EMCON_SettingsMode 的 1/0）。
    # ------------------------------------------------------------------
    EMCON_FREE_UNITS = (_sel(('爱国者', 'patriot', 'pac'), 1),)
    # 取消继承后给雷达的显式取值：True=主动（开）/ False=被动（静默）
    EMCON_FREE_RADAR = True

    # ==================================================================
    # 构造 / 日志
    # ==================================================================
    def __init__(self, side_name, params=None):
        RuleAgentBase.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
        self._created_missions = []
        self._loadout_cache = {}
        self._bol_state = {}
        self._ground_reissue = {}    # guid -> 已补发次数（每辆车最多 1 次）
        self._mis_prev = {}          # guid -> 上一周期的 AssignedMission（监听按 U）
        self._released = set()       # 玩家已经“取消分配”过的单元（不再补逃跑航路）
        self._cycle_index = 0
        self._diag_done = False
        self._rush_done = False
        # 战术智能体：三维监控（唯一信息源，2.3.1）+ 地空导弹营攻击与自卫（2.3.5）
        #   覆盖 地空导弹连#1#2 与 爱国者地空导弹连#1#2 四个营。
        #   置 None 即可单独关掉，互不影响。
        self.monitor = (BattlefieldMonitor(self)
                        if BattlefieldMonitor is not None else None)
        self.sam_defense = (SamBattalionDefense(self, self.monitor)
                            if SamBattalionDefense is not None else None)

    def _log(self, level, msg):
        """
        安全日志接口。

        平台 player.py 里 self.log = None，直接 self.log.info 会抛
        AttributeError 导致 initial() 第一步就崩，故统一回退到标准库 logging。
        """
        logger = getattr(self, 'log', None)
        func = getattr(logger, level, None) if logger is not None else None
        if callable(func):
            func(msg)
        else:
            getattr(logging, level, logging.info)(
                '%s:%s %s' % (getattr(self, 'Name', '?'),
                              self.__class__.__name__, msg))

    # ==================================================================
    # 单元解析
    # ==================================================================
    def _own_units(self, situation):
        """
        汇总“本方全部单元”的轻量描述，供名称匹配用。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, [{'guid','name','category','dbid'}]
        """
        out, seen = [], set()
        units = {}
        if isinstance(situation, (list, tuple)) and len(situation) > 0 \
                and isinstance(situation[0], dict):
            units = situation[0]

        for guid, u in (units or {}).items():
            if not isinstance(u, dict):
                continue
            g = u.get('guid') or guid
            if g in seen:
                continue
            seen.add(g)
            out.append({'guid': g, 'name': str(u.get('name', '') or ''),
                        'category': str(u.get('category', '') or ''),
                        'dbid': u.get('dbid')})

        for attr in ('aircrafts', 'ships', 'submarines', 'facilitys', 'satellites'):
            coll = getattr(self, attr, None)
            if not isinstance(coll, dict):
                continue
            for g, obj in coll.items():
                if g in seen:
                    continue
                seen.add(g)
                out.append({'guid': g, 'name': str(getattr(obj, 'Name', '') or ''),
                            'category': attr, 'dbid': getattr(obj, 'DBID', None)})
        return out

    def _resolve_units(self, situation, specs):
        """
        按选择器解析出本方单元。

        两级匹配：
          ① 严格：名称含关键字 **且** 舷号 ∈ 期望舷号；
          ② 兜底：舷号对不上（想定里的名字可能没有 #n）时，若该关键字
             只命中唯一一个单元，就按它处理并打警告；命中多个则列出来
             提示改关键字，绝不乱分配。

        :param situation: tuple, (units dict, contacts dict)
        :param specs: list/tuple, _sel() 生成的选择器
        :return: list, [(单元名, guid)]
        """
        pool = self._own_units(situation)
        hit, seen = [], set()
        for spec in specs or ():
            keys = [_norm(k) for k in spec.get('keys', ())]
            nums = spec.get('nums') or ()
            avoid = [_norm(k) for k in (spec.get('avoid') or ())]
            strict, loose = [], []
            for u in pool:
                if u['guid'] in seen:
                    continue
                bare = _norm(u['name'])
                if avoid and any(a and a in bare for a in avoid):
                    continue          # avoid（例：霍克地空导弹连）
                if not any(k and k in bare for k in keys):
                    continue
                if nums and _unit_num(u['name']) not in nums:
                    loose.append(u)
                    continue
                strict.append(u)
            if strict:
                for u in strict:
                    seen.add(u['guid'])
                    hit.append((u['name'], u['guid']))
                continue
            if nums and len(loose) == 1:
                u = loose[0]
                seen.add(u['guid'])
                hit.append((u['name'], u['guid']))
                self._log('warning', '单元[%s] 舷号与 %s 不符，但该型只有这一个单元，'
                                     '按它处理（如不对请改关键字/舷号）'
                          % (u['name'], list(nums)))
            elif nums and len(loose) > 1:
                self._log('warning', '关键字 %s 命中多个单元但舷号 %s 对不上：%s'
                          % (list(spec.get('keys') or ()), list(nums),
                             [u['name'] for u in loose]))
        return hit

    def _find_units_by_exact_name(self, names):
        """按精确名取本方单元对象（优先 units_of_name 索引）。"""
        found, index = [], {}
        uon = getattr(self, 'units_of_name', None)
        if isinstance(uon, dict):
            for nm, obj in uon.items():
                index[_norm(nm)] = (nm, obj)
        for want in names:
            hit = index.get(_norm(want))
            if hit is not None:
                found.append(hit)
        return found

    # ==================================================================
    # 战斧 BOL（纯方位打击）—— 与红方同一套实现
    # ==================================================================
    def _collect_weapon_recs(self, unit):
        """扫描挂架/弹仓，返回 [(挂架DBID, 武器DBID, 当前数量), ...]。"""
        recs = []

        def _to_int(x):
            try:
                return int(x)
            except (TypeError, ValueError):
                return None

        def _mount_db(mv, mk):
            if isinstance(mv, dict):
                comp = mv.get('Component')
                if isinstance(comp, dict) and comp.get('DBID') is not None:
                    return comp.get('DBID')
                if mv.get('DBID') is not None:
                    return mv.get('DBID')
            if mk is not None:
                n = _to_int(mk)
                return n if n is not None else mk
            return None

        def _emit(container, mount_db):
            if not isinstance(container, dict):
                return
            wrs = container.get('WeaponRecs')
            if isinstance(wrs, dict):
                items = list(wrs.values())
            elif isinstance(wrs, (list, tuple)):
                items = list(wrs)
            else:
                return
            for rec in items:
                if not isinstance(rec, dict):
                    continue
                wi = _to_int(rec.get('WeaponDBID'))
                if wi is None:
                    continue
                cnt = _to_int(rec.get('CurrentLoad'))
                if cnt is None:
                    cnt = _to_int(rec.get('DefaultLoad'))
                recs.append((mount_db, wi, cnt or 0))

        for attr in ('Mounts', 'Magazines', 'Loadouts'):
            cont = getattr(unit, attr, None)
            if isinstance(cont, dict):
                for mk, mv in cont.items():
                    _emit(mv, _mount_db(mv, mk))
                    if isinstance(mv, dict) and 'WeaponRecs' not in mv:
                        for sub in mv.values():
                            if isinstance(sub, dict) and 'WeaponRecs' in sub:
                                _emit(sub, _mount_db(sub, mk))
            elif isinstance(cont, (list, tuple)):
                for mv in cont:
                    _emit(mv, _mount_db(mv, None))
        return recs

    def _find_weapons_on_unit(self, unit, wids):
        """在单元上找指定武器，返回 [{'weapon','mount','count','name'}]。"""
        want = set()
        for w in wids:
            try:
                want.add(int(w))
            except (TypeError, ValueError):
                pass
        acc = {}
        for mount_db, wi, cnt in self._collect_weapon_recs(unit):
            if wi not in want or not cnt:
                continue
            key = (mount_db, wi)
            acc[key] = acc.get(key, 0) + cnt

        if not acc:
            fn = getattr(unit, 'get_weapon_infos', None)
            if callable(fn):
                try:
                    for item in (fn() or []):
                        if isinstance(item, (list, tuple)) and len(item) >= 3:
                            try:
                                wi = int(item[1])
                                cnt = int(item[2])
                            except (TypeError, ValueError):
                                continue
                            if wi in want and cnt:
                                acc[(None, wi)] = max(acc.get((None, wi), 0), cnt)
                except Exception:
                    pass

        merged = {}
        for (mnt, wi), cnt in sorted(acc.items(),
                                     key=lambda kv: (str(kv[0][0]), kv[0][1])):
            if cnt <= 0:
                continue
            cur = merged.get(wi)
            if cur is None:
                merged[wi] = {'mount': mnt if mnt is not None else 0, 'count': cnt}
            else:
                cur['count'] += cnt
                if not cur['mount'] and mnt is not None:
                    cur['mount'] = mnt
        return [{'weapon': wi, 'mount': info['mount'], 'count': info['count'],
                 'name': self._weapon_name(wi)}
                for wi, info in sorted(merged.items())]

    def _all_weapons_on_unit(self, unit):
        """列出单元上全部武器（诊断用）：[{'weapon','mount','count','name'}]。"""
        agg = {}
        for mount_db, wi, cnt in self._collect_weapon_recs(unit):
            if not cnt:
                continue
            k = (mount_db, wi)
            agg[k] = agg.get(k, 0) + cnt
        out = []
        for (mnt, wi), cnt in sorted(agg.items(),
                                     key=lambda kv: (-kv[1], str(kv[0]))):
            out.append({'weapon': wi, 'mount': mnt if mnt is not None else 0,
                        'count': cnt, 'name': self._weapon_name(wi)})
        return out

    def _find_weapons_by_name(self, unit, keywords):
        """按武器名称关键字找弹（DBID 对不上时的兜底）。"""
        keys = [_norm(k) for k in (keywords or ()) if k]

        def _hit(wid):
            nm = _norm(self._weapon_name(wid))
            return any(k and k in nm for k in keys)

        wids = set()
        for attr in ('Mounts', 'Magazines', 'Loadouts'):
            cont = getattr(unit, attr, None)
            if not isinstance(cont, dict):
                continue
            for mv in cont.values():
                if not isinstance(mv, dict):
                    continue
                wrs = mv.get('WeaponRecs')
                if isinstance(wrs, dict):
                    for rec in wrs.values():
                        if isinstance(rec, dict) and rec.get('WeaponDBID') is not None:
                            wids.add(rec.get('WeaponDBID'))
        hit = [w for w in wids if _hit(w)]
        if not hit:
            return []
        return self._find_weapons_on_unit(unit, tuple(hit))

    def _weapon_name(self, weapon_id):
        """武器 DBID -> 型号名（model.db）；查不到返回空串。"""
        try:
            return query_data.get_weapon_name(int(weapon_id)) or ''
        except Exception:
            return ''

    def _count_weapons(self, unit, wids):
        """指定武器的剩余总数（用于“指令成功但没出弹”的核对）。"""
        return sum(int(p.get('count') or 0)
                   for p in self._find_weapons_on_unit(unit, wids))

    @staticmethod
    def _reply_ok(res):
        """判断平台返回是否真正执行成功（code == 0 为准）。"""
        if res is None:
            return False
        code = getattr(res, 'code', None)
        if code is not None:
            try:
                return int(code) == 0
            except (TypeError, ValueError):
                return False
        s = str(getattr(res, 'result', res))
        for bad in ('指令执行失败', '超出数量限制', '已被取消下发', '找不到武器'):
            if bad in s:
                return False
        return True

    @staticmethod
    def _reply_text(res):
        """把平台 Reply 解成一行可读文本。"""
        if res is None:
            return 'None（接口未返回）'
        raw = getattr(res, 'result', res)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode('utf-8', 'replace')
            except Exception:
                raw = str(raw)
        s = str(raw).strip()
        if len(s) > 400:
            s = s[:400] + '...'
        return 'code=%s result=%s' % (getattr(res, 'code', None), s)

    @staticmethod
    def _bol_cmd_len(guid, mount, weapon, qty, lat, lon, points):
        """估算一条 BOL 指令的字符数（平台单条指令上限 300）。"""
        head = ("AttackContact('%s','BOL',{mode=1,mount=%s,weapon=%.1f,qty=%s,"
                "LATITUDE='%.5f',LONGITUDE='%.5f',COURSE={"
                % (guid, mount, float(weapon), qty, lat, lon))
        body = ','.join('{ longitude=%.5f, latitude=%.5f}' % (p[1], p[0])
                        for p in points)
        return len(head) + len(body) + 3

    def _fit_bol_course(self, guid, mount, weapon, qty, lat, lon, course):
        """把航迹点裁到 BOL_MAX_CMD_CHARS 以内（目标点始终保留在末尾）。"""
        pts = list(course)
        dropped = []
        while len(pts) > 1 and \
                self._bol_cmd_len(guid, mount, weapon, qty, lat, lon, pts) \
                > self.BOL_MAX_CMD_CHARS:
            dropped.insert(0, pts.pop(-2))
        return pts, dropped

    def _bol_attack(self, unit, lat, lon, mount_db, weapon_db, qty, course=None):
        """纯方位（BOL）打击，带导弹航迹规划点。"""
        course = [(float(p[0]), float(p[1])) for p in (course or [])]
        if course:
            last = course[-1]
            if abs(last[0] - float(lat)) > 1e-9 or abs(last[1] - float(lon)) > 1e-9:
                course.append((float(lat), float(lon)))
        server = getattr(self, '_game_server', None)
        try:
            if server is not None and hasattr(server, 'api_attack_BOL'):
                try:
                    return server.api_attack_BOL(unit, lat, lon, mount_db,
                                                 weapon_db, qty, course=course)
                except TypeError:
                    return server.api_attack_BOL(unit, lat, lon, mount_db,
                                                 weapon_db, qty)
            return unit.attack_BOL(lat, lon, mount_db, weapon_db, qty)
        except Exception as e:
            self._log('error', 'BOL 打击失败 单元[%s] 武器=%s: %s'
                      % (getattr(unit, 'Name', '?'), weapon_db, e))
            return None

    def _set_sub_depth(self, sub, depth):
        """潜艇手动控制深度（先 set_alt_manual(True) 才生效）。"""
        try:
            sub.set_alt_manual(True)
        except Exception as e:
            self._log('warning', '潜艇[%s] set_alt_manual 失败: %s'
                      % (getattr(sub, 'Name', '?'), e))
        server = getattr(self, '_game_server', None)
        try:
            if server is not None and hasattr(server, 'api_set_depth'):
                return server.api_set_depth(sub, depth)
        except Exception as e:
            self._log('error', '潜艇[%s] 设置深度 %s 失败: %s'
                      % (getattr(sub, 'Name', '?'), depth, e))
        return None

    def do_bol_strikes(self, situation):
        """
        开局战斧 BOL（佛蒙特号 / 阿利伯克）。

        流程与红方一致：找单元 → （潜艇先设深度）→ 找弹 → 按长度裁剪航迹点 →
        5 种下发方式轮换 → 下一周期核对弹药数确认真的打出去了。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本周期确认打出去的次数
        """
        fired = 0
        for idx, item in enumerate(self.BOL_STRIKES):
            st = self._bol_state.setdefault(
                idx, {'round': 0, 'fired': False, 'pre': None, 'wait': 0,
                      'depth_done': False, 'fit_logged': False,
                      'no_unit': 0, 'no_weapon': 0, 'last_reply': ''})
            if st['fired']:
                continue

            found = self._resolve_units(situation, (item['unit'],))
            if not found:
                st['no_unit'] += 1
                if st['no_unit'] in (1, 5, 15, 30):
                    self._log('warning', 'BOL[%s] 未匹配到单元（关键字 %s），第 %d 周期'
                              % (item['desc'], list(item['unit']['keys']),
                                 st['no_unit']))
                continue
            name, guid = found[0]
            obj = self.get_unit(guid)
            if obj is None:
                continue

            # 核对上一轮是否真的出弹
            if st['pre'] is not None:
                check_obj = self.get_unit(st.get('fire_guid') or guid) or obj
                cur = self._count_weapons(check_obj, item['wids'])
                if cur < st['pre']:
                    st['fired'] = True
                    fired += 1
                    self._log('info', 'BOL[%s] ✅ 已确认发射：单元[%s] 弹药 %d → %d'
                              % (item['desc'], name, st['pre'], cur))
                    continue
                st['wait'] += 1
                if st['wait'] < 2:
                    continue
                self._log('warning', 'BOL[%s] 上一轮平台回“成功”但弹药 %d → %d 未减少，'
                                     '换下一种下发方式'
                          % (item['desc'], st['pre'], cur))
                st['pre'] = None
                st['wait'] = 0
                st['round'] += 1

            if st['round'] >= len(self.BOL_STRATEGIES):
                st['fired'] = True
                self._log('error', 'BOL[%s] ❌ 已试完 %d 种下发方式仍未出弹，放弃。'
                                   '最后一轮平台回复：%s'
                          % (item['desc'], st['round'], st['last_reply']))
                continue

            # 潜艇深度（只设一次）
            if item.get('depth') is not None and not st['depth_done']:
                st['depth_done'] = True
                self._set_sub_depth(obj, item['depth'])
                self._log('info', 'BOL[%s] 潜艇[%s] 深度已设为 %s 米'
                          % (item['desc'], name, item['depth']))

            plans = self._find_weapons_on_unit(obj, item['wids'])
            if not plans:
                plans = self._find_weapons_by_name(obj, item.get('kws') or ())
            if not plans:
                st['no_weapon'] += 1
                if st['no_weapon'] in (1, 5, 15, 30):
                    inv = self._all_weapons_on_unit(obj)
                    self._log('warning',
                              'BOL[%s] 单元[%s] 上找不到指定武器 %s（第 %d 周期）。'
                              '该单元现有全部武器：%s'
                              % (item['desc'], name, item['wids'], st['no_weapon'],
                                 ['%s(%s)x%d' % (p['name'], p['weapon'], p['count'])
                                  for p in inv] or '无'))
                continue

            strategy = self.BOL_STRATEGIES[st['round']]
            lat, lon = item['target']
            # qty 为 None 表示“该型全部打出去”，此时每个弹种各发一次
            fire_plans = plans[:1] if item.get('qty') else plans
            before = self._count_weapons(obj, item['wids'])
            any_ok = False
            for plan in fire_plans:
                qty = int(item.get('qty') or plan['count'])
                qty = max(1, min(qty, int(plan['count'])))
                if strategy == 'qty1':
                    qty = 1
                mount = 0 if strategy == 'mount0' else plan['mount']
                course = list(item.get('course') or []) + [(lat, lon)]
                if strategy in ('course', 'qty1', 'mount0'):
                    fit, dropped = self._fit_bol_course(
                        guid, mount, plan['weapon'], qty, lat, lon, course)
                    if dropped and not st.get('fit_logged'):
                        st['fit_logged'] = True
                        self._log('warning',
                                  'BOL[%s] 平台单条指令上限 %d 字符：%d 个航迹点 + 目标点'
                                  '共 %d 点放不下，本次只下发前 %d 个航迹点 + 目标点'
                                  '（舍去 %s）'
                                  % (item['desc'], self.BOL_MAX_CMD_CHARS,
                                     len(course) - 1, len(course), len(fit) - 1,
                                     dropped))
                    course = fit if len(fit) > 1 else []
                else:
                    course = []

                if strategy == 'unit':
                    try:
                        res = obj.attack_BOL(lat, lon, mount, plan['weapon'], qty)
                    except Exception as e:
                        res = None
                        self._log('error', 'BOL[%s] 调用 attack_BOL 异常: %s'
                                  % (item['desc'], e))
                elif strategy == 'plain' or not course:
                    res = self._bol_attack(obj, lat, lon, mount,
                                           plan['weapon'], qty, None)
                else:
                    res = self._bol_attack(obj, lat, lon, mount,
                                           plan['weapon'], qty, course)
                ok = self._reply_ok(res)
                any_ok = any_ok or ok
                st['last_reply'] = self._reply_text(res)
                self._log('info', 'BOL[%s] 第%d轮[%s] 单元[%s] %s x%d 挂架=%s '
                                  '目标=(%.6f,%.6f) 航迹点=%d → %s | 平台回复 %s'
                          % (item['desc'], st['round'] + 1, strategy, name,
                             plan['name'], qty, mount, lat, lon,
                             max(0, len(course) - 1) if course else 0,
                             '指令已接受（下周期核对弹药）' if ok else '指令被拒绝',
                             st['last_reply']))

            st['pre'] = before
            st['fire_guid'] = guid
            if not any_ok:
                st['round'] += 1
                st['pre'] = None
        return fired

    # ==================================================================
    # ① 总条令
    # ==================================================================
    def set_side_rules(self):
        """
        修改总条令（推演方级，只下发一次，下级自动继承）。

        对空自由开火；对海/对地/对潜限制开火（仅限于手动开火）；
        攻击时忽略计划航线——否；被攻击时忽略电磁管控——否；
        燃油状态-返航——否；武器状态——任务武器耗光允许使用航炮（推荐）；
        武器状态-返航——否；电磁管控：干扰机打开、声呐打开。

        :return: int, 下发条数
        """
        n = 0
        self.doctrine_weapon_control_status_air(WeaponControlStatus.Free); n += 1
        self.doctrine_weapon_control_status_surface(
            WeaponControlStatus.Hold if self.RULE_HOLD_SURFACE
            else WeaponControlStatus.Free); n += 1
        self.doctrine_weapon_control_status_land(WeaponControlStatus.Hold); n += 1
        self.doctrine_weapon_control_status_subsurface(WeaponControlStatus.Hold); n += 1

        self.doctrine_ignore_plotted_course(
            IgnorePlottedCourseWhenAttacking.No); n += 1
        self.doctrine_ignore_emcon_under_attack(IgnoreEMCONUnderAttack.No); n += 1

        self.doctrine_fuel_state_rtb(FuelStateRTB.No); n += 1
        self.doctrine_weapon_state_planned(
            WeaponStatePlanned.WinchesterUseAirGuns); n += 1
        self.doctrine_weapon_state_rtb(WeaponStateRTB.No); n += 1

        self.doctrine_switch_oecm(True); n += 1      # 干扰机：打开
        self.doctrine_switch_sonar(True); n += 1     # 声呐：打开

        self._log('info', '总条令已下发 %d 条（对空自由/对海·对地·对潜限制开火，'
                          '不忽略计划航线，不忽略电磁管控，燃油·武器状态不返航，'
                          '干扰机+声呐打开）' % n)
        return n

    # ==================================================================
    # ② 总条令：三型空空导弹 WRA
    # ==================================================================
    def set_side_air_wra(self):
        """
        AIM-120D / AIM-260 / AIM-120C-7 的武器使用规则（推演方级，只下发一次）。

        · 自动开火距离：空中感知-未知类型 / 飞机-未指定 / 第五代 / 第四代
          —— 60 / 90 / 50 海里
        · 齐射武器数：制导武器-未指定 → 不使用武器；
                      飞机-第五代/第四代 → 1 枚

        :return: int, 下发条数
        """
        n = 0
        for wids, name, rng in self.SIDE_AIR_WRA:
            for wid in wids:
                for t, qty in self.AIR_WRA_SALVO:
                    self.wra_qty_salvo(wid, t, qty)
                    n += 1
                for t in self.AIR_WRA_RANGE_TARGETS:
                    self.wra_firing_range(wid, t, rng)
                    n += 1
            self._log('info', '总条令 WRA[%s(%s)]：4 类目标自动开火距离 %s 海里，'
                              '制导武器-未指定 不使用武器，5代/4代 各 1 枚'
                      % (name, '/'.join(wids), rng))
        self._log('info', '总条令空空导弹 WRA 共下发 %d 条' % n)
        return n

    # ==================================================================
    # ③ 飞机挂载
    # ==================================================================
    def _loadout_rows(self, aircraft_dbid):
        """
        查某机型在 model.db 里可用的挂载方案 [(loadout_id, name), ...]。

        数据表关系：DataAircraftLoadouts(ID=飞机DBID, ComponentID=挂载DBID)，
        DataLoadout(ID, Name)。结果按机型缓存。
        """
        try:
            key = int(aircraft_dbid)
        except (TypeError, ValueError):
            return []
        if key in self._loadout_cache:
            return self._loadout_cache[key]

        rows = []
        try:
            qd = query_data
            if qd is None:      # 顶层导入失败时再试一次（平台路径可能后挂）
                try:
                    from engine.LingYi.entitys.data import query_data as qd
                except Exception:
                    from entitys.data import query_data as qd
        except Exception:
            qd = None
        if qd is None:
            self._log('error', '无法导入 entitys.data.query_data，挂载方案无法查询')
            self._loadout_cache[key] = []
            return []
        db_path = getattr(qd, 'db_path', None)
        if not db_path or not os.path.exists(db_path):
            self._log('error', 'model.db 路径不可用：%s' % db_path)
            self._loadout_cache[key] = []
            return []
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                'select L.ID, L.Name from DataAircraftLoadouts AL '
                'join DataLoadout L on L.ID = AL.ComponentID '
                'where AL.ID = ?', (key,))
            rows = [(int(r[0]), str(r[1] or '')) for r in cur.fetchall()]
            conn.close()
        except Exception as e:
            self._log('warning', '查询机型 %s 的挂载方案失败: %s' % (key, e))
            rows = []
        self._loadout_cache[key] = rows
        return rows

    def _pick_loadout(self, unit_name, unit, want, avoid=()):
        """
        在本机可用挂载里，按“挂载名必须同时包含 want 中所有关键字”挑一条。

        :param want: list, 关键字（全部命中）；也支持 list[list]（多组备选）
        :return: (loadout_id, name) 或 (None, '')
        """
        rows = self._loadout_rows(getattr(unit, 'DBID', None))
        if not rows:
            return None, ''
        if want and isinstance(want[0], str):
            groups = [list(want)]
        else:
            groups = [list(g) for g in (want or [])]
        avoids = [_norm(a) for a in (avoid or ()) if a]

        for grp in groups:
            wants = [_norm(w) for w in grp]
            best = None
            for lid, lname in rows:
                n = _norm(lname)
                if any(a in n for a in avoids):
                    continue
                if not all(w in n for w in wants):
                    continue
                if '转场' in n or '预备飞行' in n or '维修' in n:
                    continue
                if best is None or lid < best[0]:
                    best = (lid, lname)
            if best is not None:
                return best

        self._log('warning', '飞机[%s] 未找到挂载 %s，本机可选挂载：%s'
                  % (unit_name, want, [x[1] for x in rows][:40]))
        return None, ''

    def set_aircraft_loadouts(self, situation):
        """
        按 AIRCRAFT_LOADOUTS 给指定飞机设置挂载（必须在战前规划阶段调用，
        此时挂载立即完成、准备时间为 0）。表里没有的飞机保持系统默认挂载。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 成功的单元名
        """
        done, missing = [], []
        for spec, want, desc in self.AIRCRAFT_LOADOUTS:
            found = self._resolve_units(situation, (spec,))
            if not found:
                missing.append('%s(%s)' % (desc, spec['keys'][0]))
                continue
            for name, guid in found:
                unit = self.get_unit(guid)
                if unit is None:
                    continue
                lid, lname = self._pick_loadout(name, unit, want)
                if lid is None:
                    continue
                try:
                    self.set_aircraft_loadout_plan_time(unit.ID, lid)
                    done.append(name)
                    self._log('info', '飞机[%s] 挂载 → %s（%s）'
                              % (name, lid, lname))
                except Exception as e:
                    self._log('error', '飞机[%s] 设置挂载 %s 失败: %s'
                              % (name, lid, e))
        if missing:
            self._log('warning', '以下机型的挂载未设置（未匹配到单元）：%s' % missing)
        self._log('info', '飞机挂载设置完成 %d 架（%d 组配置）'
                  % (len(done), len(self.AIRCRAFT_LOADOUTS)))
        return done

    # ==================================================================
    # ④ 舰船条令
    # ==================================================================
    def set_ship_doctrines(self, situation):
        """
        邦克山、阿利伯克、摩耶：对空改为限制开火（仅限手动开火）。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 成功的单元名
        """
        found = self._resolve_units(situation, self.SHIP_AIR_HOLD)
        if not found:
            self._log('warning', '未匹配到邦克山/阿利伯克/摩耶，对空限制开火未设置')
            return []
        done = []
        for name, guid in found:
            unit = self.get_unit(guid)
            if unit is None:
                continue
            try:
                unit.doctrine_weapon_control_status_air(WeaponControlStatus.Hold)
                done.append(name)
                self._log('info', '舰船[%s] 对空改为“限制开火（仅限手动开火）”' % name)
            except Exception as e:
                self._log('error', '舰船[%s] 设置对空限制开火失败: %s' % (name, e))
        self._log('info', '舰船对空条令设置完成 %d/%d' % (len(done), len(found)))
        return done

    # ==================================================================
    # 任务：公共工具
    # ==================================================================
    def _remember_mission(self, mission):
        """记录建出来的任务对象，便于后续把 _game_server 重绑到计数器。"""
        if mission is None:
            return
        try:
            self._created_missions.append(mission)
        except Exception:
            pass

    def _apply_mission_doctrine(self, mission, rule):
        """下发任务级条令（key 存在才下发）。"""
        pairs = (
            ('fuel_state_planned', 'doctrine_fuel_state_planned'),
            ('fuel_state_rtb', 'doctrine_fuel_state_rtb'),
            ('weapon_state_planned', 'doctrine_weapon_state_planned'),
            ('weapon_state_rtb', 'doctrine_weapon_state_rtb'),
            ('doctrine_refuel', 'doctrine_refuel'),
            ('ignore_plotted_course', 'doctrine_ignore_plotted_course'),
            ('ignore_emcon_under_attack', 'doctrine_ignore_emcon_under_attack'),
        )
        for key, fn_name in pairs:
            if key not in rule:
                continue
            fn = getattr(mission, fn_name, None)
            if not callable(fn):
                continue
            try:
                fn(rule[key])
            except Exception as e:
                self._log('warning', '任务[%s] %s 设置失败: %s'
                          % (getattr(mission, 'Name', '?'), key, e))

    def _apply_unit_doctrine(self, doctrine, units, tag):
        """
        给参与任务的单元批量设置条令。

        :param doctrine: dict, 可含 'air'/'surface'/'subsurface'/'land'
                         （WeaponControlStatus）、'radar'（bool）
        :param units: list, [(单元名, guid)]
        :param tag: str, 日志用任务名
        :return: int, 设置成功的单元数
        """
        if not doctrine or not units:
            return 0
        n = 0
        for name, guid in units:
            unit = self.get_unit(guid)
            if unit is None:
                continue
            try:
                if doctrine.get('air') is not None:
                    unit.doctrine_weapon_control_status_air(doctrine['air'])
                if doctrine.get('surface') is not None:
                    unit.doctrine_weapon_control_status_surface(doctrine['surface'])
                if doctrine.get('subsurface') is not None:
                    unit.doctrine_weapon_control_status_subsurface(doctrine['subsurface'])
                if doctrine.get('land') is not None:
                    unit.doctrine_weapon_control_status_land(doctrine['land'])
                if doctrine.get('radar') is not None:
                    unit.doctrine_switch_radar(doctrine['radar'])
                if doctrine.get('radar_direct'):
                    try:
                        unit.switch_radar(True)
                    except Exception as e:
                        self._log('warning', '[%s] 单元[%s] 直接开雷达失败: %s'
                                  % (tag, name, e))
                if doctrine.get('engage_opportunity') is not None:
                    unit.doctrine_engage_opportunity_targets(
                        doctrine['engage_opportunity'])
                n += 1
            except Exception as e:
                self._log('error', '[%s] 单元[%s] 设置条令失败: %s' % (tag, name, e))
        return n

    # ==================================================================
    # ⑤ 支援任务
    # ==================================================================
    def add_set_support_mission(self, situation, name, points, units,
                                rule, doctrine=None, time_lab=None):
        """
        创建支援任务并分配单元。

        :param points: list, 阵位航线参考点 [(lat, lon), ...]（起点、终点）
        :param units: tuple, 单元选择器（可为空 = 不分配单元）
        :return: SupportMission 或 None
        """
        mission = self.create_support_mission(name, list(points))
        if mission is None:
            self._log('error', '创建支援任务失败：%s' % name)
            return None
        self._remember_mission(mission)

        # --- 任务编辑项 ---
        mission.set_one_third_rule(rule.get('one_third_rule', False))
        mission.support_flightSize(
            rule.get('flight_size', EscortFlightSize.SingleAircraft))
        mission.support_useFlightSize(rule.get('use_flight_size', False))
        if 'active_emcon' in rule:
            mission.support_activeEMCON(rule['active_emcon'])
        if 'loop_type' in rule:
            mission.support_loopType(rule['loop_type'])
        if 'one_time_only' in rule:
            mission.support_oneTimeOnly(rule['one_time_only'])
        for key, field in (('OPA', 'CheckOPA'), ('WWR', 'CheckWWR')):
            if key in rule:
                try:
                    mission._set('%s=%s' % (field, str(bool(rule[key])).lower()))
                except Exception as e:
                    self._log('warning', '任务[%s] %s 设置失败: %s' % (name, key, e))
        self._apply_mission_doctrine(mission, rule)

        # --- 速度高度设置：水面舰艇 出航/阵位油门 ---
        #     rule['ship_throttle'] = (出航油门, 阵位油门)，None 表示该项不设置
        st = rule.get('ship_throttle')
        if st:
            for i, fn in enumerate((mission.support_set_throttle_transit_ship,
                                    mission.support_set_throttle_station_ship)):
                if i < len(st) and st[i] is not None:
                    try:
                        fn(st[i])
                        self._log('info', '支援任务[%s] 水面舰艇%s油门 → %s'
                                  % (name, '出航' if i == 0 else '阵位',
                                     getattr(st[i], 'name', st[i])))
                    except Exception as e:
                        self._log('warning', '支援任务[%s] 舰艇油门设置失败: %s'
                                  % (name, e))

        # --- 分配单元（可为空） ---
        found = self._resolve_units(situation, units)
        if units and not found:
            self._log('warning', '支援任务[%s] 未匹配到任何执行单元：%s'
                      % (name, [s['keys'][0] for s in units]))
        for i in range(0, len(found), 10):
            guids = [g for _n, g in found[i:i + 10]]
            try:
                self.assign_units_to_mission(unit_list=guids, mission_name=name)
            except Exception as e:
                self._log('error', '支援任务[%s] 分配单元失败: %s' % (name, e))

        self._apply_unit_doctrine(doctrine, found, name)

        if time_lab:
            if time_lab[0] is not None:
                mission.set_start(time_lab[0])
            if time_lab[1] is not None:
                mission.set_end(time_lab[1])

        self._log('info', '支援任务[%s] 已创建：单元 %d 个 %s，航线 %d 点'
                  % (name, len(found), [n for n, _ in found], len(points)))
        return mission

    def add_all_support_missions(self, situation):
        """
        按 SUPPORT_TASKS 建 32 个支援任务（没写执行单元的只建任务）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        ok = 0
        for name, p1, p2, units, formation in self.SUPPORT_TASKS:
            two = (formation == 'two')
            rule = {
                'one_third_rule': False,
                'flight_size': (EscortFlightSize.TwoAircraft if two
                                else EscortFlightSize.SingleAircraft),
                'use_flight_size': (self.TWO_SHIP_USE_FLIGHT_SIZE if two else False),
                # 支援任务不限制电磁辐射区域 => 雷达持续开机
                'active_emcon': False,
                # 任务条令：燃油/武器状态不返航；武器耗光允许使用航炮
                'fuel_state_rtb': FuelStateRTB.No,
                'weapon_state_rtb': WeaponStateRTB.No,
                'weapon_state_planned': WeaponStatePlanned.WinchesterUseAirGuns,
                'ignore_plotted_course': IgnorePlottedCourseWhenAttacking.No,
            }
            if name in self.GROUND_SUPPORT_TASKS:
                # 地面/水面单位的机动任务：只给航线和油门，不套空中条令
                doctrine = None
            else:
                doctrine = ({'air': WeaponControlStatus.Free,
                             'radar': self.SUPPORT_RADAR} if units else None)
            # 任务编辑—速度高度设置—水面舰艇航速：出航/阵位油门
            if name in self.SHIP_THROTTLE_TASKS:
                rule['ship_throttle'] = self.SHIP_THROTTLE_TASKS[name]
            # 起点=终点时把终点挪 0.01°（约 1km），避免零长度航线
            if abs(p1[0] - p2[0]) < 1e-6 and abs(p1[1] - p2[1]) < 1e-6:
                p2 = (round(p2[0] + 0.01, 6), p2[1])
                self._log('warning', '支援任务[%s] 起终点相同，已把终点北移 0.01° 以免航线长度为零'
                          % name)
            try:
                m = self.add_set_support_mission(
                    situation, name, [p1, p2], units, rule, doctrine=doctrine)
                if m is not None:
                    ok += 1
                    # 开局不启动的任务：建好之后立刻停用（后续手动启用）
                    if name in self.INACTIVE_MISSIONS:
                        m.mission_active(False)
                        self._log('info', '支援任务[%s] 已创建并设为“开局不启用”' % name)
            except Exception as e:
                self._log('error', '支援任务[%s] 创建异常: %s' % (name, e))
        self._log('info', '支援任务创建完成 %d/%d' % (ok, len(self.SUPPORT_TASKS)))
        return ok

    # ==================================================================
    # ⑥ 巡逻任务
    # ==================================================================
    def add_set_patrol_mission(self, situation, name, mission_type, area, units,
                               rule=None, doctrine=None, time_lab=None):
        """
        创建巡逻任务并分配单元。

        :param area: list, 巡逻区参考点 [(lat, lon), ...]
        :return: PatrolMission 或 None
        """
        mission = self.create_patrol_mission(name, mission_type, list(area))
        if mission is None:
            self._log('error', '创建巡逻任务失败：%s' % name)
            return None
        self._remember_mission(mission)
        rule = rule or {}

        if 'one_third_rule' in rule:
            mission.set_one_third_rule(rule['one_third_rule'])
        if 'flight_size' in rule:
            mission.patrol_flight_size(rule['flight_size'])
        if 'use_flight_size' in rule:
            mission.patrol_useFlightSize(rule['use_flight_size'])
        for key, setter in (('OPA', mission.patrol_checkOPA),
                            ('WWR', mission.patrol_checkWWR),
                            ('active_emcon', mission.patrol_activeEMCON),
                            ('station_count', mission.station_count)):
            if key in rule:
                try:
                    setter(rule[key])
                except Exception as e:
                    self._log('warning', '巡逻任务[%s] %s 设置失败: %s' % (name, key, e))

        self._apply_mission_doctrine(mission, rule)

        found = self._resolve_units(situation, units)
        if units and not found:
            self._log('warning', '巡逻任务[%s] 未匹配到任何执行单元：%s'
                      % (name, [s['keys'][0] for s in units]))
        for i in range(0, len(found), 10):
            guids = [g for _n, g in found[i:i + 10]]
            try:
                self.assign_units_to_mission(unit_list=guids, mission_name=name)
            except Exception as e:
                self._log('error', '巡逻任务[%s] 分配单元失败: %s' % (name, e))

        self._apply_unit_doctrine(doctrine, found, name)

        if time_lab:
            if time_lab[0] is not None:
                mission.set_start(time_lab[0])
            if time_lab[1] is not None:
                mission.set_end(time_lab[1])

        self._log('info', '巡逻任务[%s] 已创建：类型 %s，单元 %d 个 %s，巡逻区 %d 点'
                  % (name, mission_type, len(found), [n for n, _ in found], len(area)))
        return mission

    def add_all_patrol_missions(self, situation):
        """
        按 PATROL_TASKS 建 3 个巡逻任务。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        ok = 0
        for name, mtype, area, units, note in self.PATROL_TASKS:
            rule = {
                'one_third_rule': False,                 # 取消 1/3 规则
                'flight_size': EscortFlightSize.SingleAircraft,
                'use_flight_size': False,                # 取消“飞机数低于编队要求不起飞”
                'OPA': False,                            # 取消“对巡逻区外目标分析”
                'WWR': False,                            # 取消“对武器射程内目标分析”
                'active_emcon': False,
                # 任务条令（用户要求）
                'fuel_state_rtb': FuelStateRTB.No,
                'weapon_state_rtb': WeaponStateRTB.No,
                'weapon_state_planned': WeaponStatePlanned.WinchesterUseAirGuns,
                'ignore_plotted_course': IgnorePlottedCourseWhenAttacking.No,
            }
            try:
                m = self.add_set_patrol_mission(
                    situation, name, mtype, area, units, rule,
                    doctrine=self.PATROL_UNIT_DOCTRINE)
                if m is not None:
                    ok += 1
                    self._log('info', '巡逻任务[%s] 条令：对地/对海/对潜自由开火；%s'
                              % (name, note))
                    # 开局不启动的任务：建好之后立刻停用（后续手动启用）
                    if name in self.INACTIVE_MISSIONS:
                        m.mission_active(False)
                        self._log('info', '巡逻任务[%s] 已创建并设为“开局不启用”' % name)
            except Exception as e:
                self._log('error', '巡逻任务[%s] 创建异常: %s' % (name, e))
        self._log('info', '巡逻任务创建完成 %d/%d' % (ok, len(self.PATROL_TASKS)))
        return ok

    # ==================================================================
    # ⑦ 开局机动：全速前往集结点
    # ==================================================================
    def set_sub_depth(self, situation):
        """
        开局设置潜艇深度（战前规划阶段）。

        平台接口：Submarine.set_depth(深度米数，正数 = 水下多少米)，
        例如 40 就是界面上的 -40 米。这里先用 set_depth，失败再退回 api_set_depth。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功设置的潜艇数
        """
        n = 0
        for spec, depth in self.PREWAR_SUB_DEPTH:
            found = self._resolve_units(situation, (spec,))
            if not found:
                self._log('warning', '潜艇深度：未匹配到单元 %s'
                          % list(spec.get('keys') or ()))
            for name, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                res = None
                try:
                    res = obj.set_depth(int(depth))
                except Exception as e:
                    self._log('warning', '潜艇[%s] set_depth 失败(%s)，改用 api_set_depth'
                              % (name, e))
                    res = self._set_sub_depth(obj, depth)
                n += 1
                self._log('info', '潜艇[%s] 深度设为 %s 米（界面 -%s 米），平台回复 %s'
                          % (name, depth, depth, self._reply_text(res)))
        return n

    def rush_ships(self, situation):
        """
        开局“两舰全速前往集结点”——**已取消**（SHIP_RUSH 为空时直接返回）。

        原计划：摩耶级驱逐舰、日向级直升驱逐舰全速前往 (52.858177, 3.874748)；
        现在两舰改为分配给「北船机动」支援任务，不再单独下航线。
        恢复办法：把注释里的两行填回 SHIP_RUSH 即可（本方法无需改动）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功处理的舰船数
        """
        if not self.SHIP_RUSH:
            return 0
        ok = 0
        for spec, dest in self.SHIP_RUSH:
            found = self._resolve_units(situation, (spec,))
            if not found:
                self._log('warning', '全速机动：未匹配到单元 %s' % list(spec['keys']))
            for name, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    try:
                        obj.clear_plotted_course()
                    except Exception:
                        pass
                    obj.plotted_course([dest])
                    try:
                        obj.set_throttle(Throttle.Flank)
                    except Exception:
                        pass
                    ok += 1
                    self._log('info', '舰船[%s] 全速前往 → %s' % (name, dest))
                except Exception as e:
                    self._log('error', '舰船[%s] 全速机动失败: %s' % (name, e))
        self._log('info', '全速机动完成 %d 艘' % ok)
        return ok

    def move_ground_units(self, situation):
        """
        地面部队“加速向南逃跑”——**已取消**（GROUND_MOVES 为空时直接返回）。

        装甲车 #1~#5 现在改为“战前 M 到位 + 分配 AAAAAAAA/BBBBBBBBB/CCCCCCCC 任务”，
        见 PREWAR_MOVES / SUPPORT_TASKS。恢复办法：把注释里的三条填回 GROUND_MOVES。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功处理的车辆数
        """
        if not self.GROUND_MOVES:
            return 0
        ok = 0
        for specs, dest in self.GROUND_MOVES:
            found = self._resolve_units(situation, specs)
            if not found:
                self._log('warning', '地面机动：未匹配到单元 %s'
                          % [list(s['keys']) for s in specs])
            for name, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    try:
                        obj.clear_plotted_course()
                    except Exception:
                        pass
                    obj.plotted_course([dest])
                    try:
                        obj.set_throttle(self.GROUND_THROTTLE)
                    except Exception:
                        pass
                    ok += 1
                    self._log('info', '地面单元[%s] 最大速度前往 → (%.6f, %.6f)'
                              % (name, dest[0], dest[1]))
                except Exception as e:
                    self._log('error', '地面单元[%s] 机动失败: %s' % (name, e))
        self._log('info', '地面部队机动完成 %d 台' % ok)
        return ok

    # ==================================================================
    # ⑦-3 战前移动（战前部署—移动单元）
    # ==================================================================
    def _unit_new_position(self, guid, dest):
        """
        战前移动单个单元（容错版）。

        ⚠ 平台接口的坐标顺序是 **(经度, 纬度)**：
            unit_new_position(unit_guid, lon_lat=(lon, lat))
        本文件所有坐标都按 (纬度, 经度) 存，这里必须交换。

        平台接口：Player.unit_new_position(unit_guid, lon_lat=...)，
        内部要先过 self.get_command_check(unit_guid) 这层“指令检查对象”；
        该钩子在 SDK 里默认 None（由引擎注入），故两层兜底。

        :param guid: str, 单元 guid
        :param dest: tuple, (纬度, 经度)
        :return: 平台回复（失败返回 None）
        """
        lon_lat = (dest[1], dest[0])        # 平台要 (经度, 纬度)
        hook = getattr(self, 'get_command_check', None)
        if callable(hook):
            return self.unit_new_position(guid, lon_lat=lon_lat)
        server = getattr(self, '_game_server', None)
        if server is not None and hasattr(server, 'unit_new_position'):
            return server.unit_new_position(guid, long_lat=lon_lat,
                                            altitude=None, new_depth=None,
                                            new_heading=None)
        raise RuntimeError('没有可用的 unit_new_position 接口'
                           '（get_command_check 与 _game_server 都不可用）')

    @staticmethod
    def _km_between(a, b):
        """两点球面距离（km）。"""
        import math
        r = 6371.0
        la1, lo1 = math.radians(a[0]), math.radians(a[1])
        la2, lo2 = math.radians(b[0]), math.radians(b[1])
        h = (math.sin((la2 - la1) / 2) ** 2
             + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
        return 2 * r * math.asin(math.sqrt(min(1.0, h)))

    def prewar_move_units(self, situation, moves=None):
        """
        战前规划移动：按 PREWAR_MOVES 把单元挪到新位置（unit_new_position，20 km 内）。

        必须在正式开战前、且在“分配给任务”之前下发。日志里会打出
        “目标点距当前位置 X km”，超过 20 km 时平台会回“移动位置太远”，
        直接看这一行就知道是哪个单元、差多少。

        :param situation: tuple, (units dict, contacts dict)
        :param moves: 可选，覆盖用的移动表（refresh 复用同一份逻辑）
        :return: int, 成功移动的单元数
        """
        ok = 0
        for specs, dest in (self.PREWAR_MOVES if moves is None else moves):
            found = self._resolve_units(situation, specs)
            if not found:
                self._log('warning', '战前移动：未匹配到单元 %s'
                          % [list(s.get('keys') or ()) for s in specs])
            for name, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    res = self._unit_new_position(guid, dest)
                    ok += 1
                    cur = None
                    try:
                        cur = (float(getattr(obj, 'Lat')), float(getattr(obj, 'Lon')))
                    except (TypeError, ValueError):
                        cur = None
                    dist = self._km_between(cur, dest) if cur else None
                    if res is None:
                        self._log('info', '战前移动[%s] → (%.6f, %.6f) 已下发'
                                           '（平台无回执；原位置 %s，距离 %s km）'
                                  % (name, dest[0], dest[1],
                                     '%.4f,%.4f' % cur if cur else '?',
                                     '?' if dist is None else '%.1f' % dist))
                    elif self._reply_ok(res):
                        self._log('info', '战前移动[%s] → (%.6f, %.6f) 成功'
                                           '（原位置 %s，距离 %s km）'
                                  % (name, dest[0], dest[1],
                                     '%.4f,%.4f' % cur if cur else '?',
                                     '?' if dist is None else '%.1f' % dist))
                    else:
                        self._log('warning',
                                  '战前移动[%s] → (%.6f, %.6f) 平台拒绝：%s'
                                  '（距原位置 %s km，平台上限 20 km）'
                                  % (name, dest[0], dest[1],
                                     self._reply_text(res),
                                     '?' if dist is None else '%.1f' % dist))
                except Exception as e:
                    self._log('error', '战前移动[%s] 失败: %s' % (name, e))
        self._log('info', '战前移动完成 %d 个单元' % ok)
        return ok

    def clear_unit_assignments(self, situation):
        """
        战前移动之后、建任务之前：把 PREWAR_MOVES 里的单元先“取消分配”。

        平台 bug：做过战前移动的单元若还带着默认任务分配，会被拉回系统默认起点。
        只处理我们要自己安排位置的单元，不碰其他单元。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 处理的单元数
        """
        n = 0
        seen = set()
        for specs, _dest in self.PREWAR_MOVES:
            for name, guid in self._resolve_units(situation, specs):
                if guid in seen:
                    continue
                seen.add(guid)
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    obj.withdraw_from_mission()
                    n += 1
                except Exception as e:
                    self._log('warning', '取消分配[%s] 失败: %s' % (name, e))
        if n:
            self._log('info', '战前“取消分配单元”完成 %d 个（战前移动过的单元，'
                              '避免被拉回默认起点）' % n)
        return n

    def refresh_ground_assignments(self, situation):
        """
        建完任务、分配完单元之后，对 REASSIGN_TASKS 再做一遍
        “取消分配 → 归位（重发战前 M）→ 重新分配”。

        这是“开局直接 M 到指定点、再按任务航线前进、不先回系统原点”的关键一步：
        平台在“分配到支援任务”那一刻会用默认站位覆盖战前移动，
        所以在重新分配之前，把战前移动的目标点再下发一次。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 重新分配的单元数
        """
        # guid -> 战前移动目标点
        pre_dest = {}
        for specs, dest in self.PREWAR_MOVES:
            for _name, guid in self._resolve_units(situation, specs):
                pre_dest[guid] = dest

        n = 0
        for name, p1, p2, units, formation in self.SUPPORT_TASKS:
            if name not in self.REASSIGN_TASKS:
                continue
            found = self._resolve_units(situation, units)
            for uname, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    obj.withdraw_from_mission()
                    dest = pre_dest.get(guid)
                    if dest is not None:
                        # 重新归位（仍在战前规划阶段，允许）
                        self._unit_new_position(guid, dest)
                    obj.assign_to_mission(name)
                    n += 1
                    self._log('info', '单元[%s] 取消分配→%s→重新分配 任务[%s]'
                              % (uname, '归位' if dest else '直接', name))
                except Exception as e:
                    self._log('warning', '单元[%s] 重新分配任务[%s] 失败: %s'
                              % (uname, name, e))
        self._log('info', '“取消分配→重新分配”完成 %d 个单元（%s）'
                  % (n, '/'.join(self.REASSIGN_TASKS)))
        return n

    # ==================================================================
    # ⑦-5 电磁管控：取消“与上级保持一致”
    # ==================================================================
    def set_emcon_not_inherit(self, situation):
        """
        把 EMCON_FREE_UNITS 里单元的电磁管控从“与上级保持一致”改成显式设置。

        平台 SDK 只提供了 doctrine_SetEMCON_Inherit()（= 勾选“与上级一致”），
        没有反向接口，所以用两步等效实现：
          ① unit.EMCON_Obey_doctrine(False)          —— 不再遵循上级电磁管控条令；
          ② unit.doctrine_switch_radar(...)         —— 条令里的雷达显式设为
             主动/被动（EMCON_SettingsMode 的 1/0；显式值即不再继承）。
        雷达实际开关仍由地空导弹营模块按模式控制，这里只决定“继承标记”。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 处理成功的单元名
        """
        found = self._resolve_units(situation, self.EMCON_FREE_UNITS)
        if not found:
            self._log('warning', '电磁管控：未匹配到单元 %s'
                      % [list(s.get('keys') or ()) for s in self.EMCON_FREE_UNITS])
            return []
        done = []
        for name, guid in found:
            obj = self.get_unit(guid)
            if obj is None:
                continue
            ok_any = False
            try:
                obj.EMCON_Obey_doctrine(False)
                ok_any = True
                self._log('info', '单元[%s] 已设为“不遵循上级电磁管控条令”' % name)
            except Exception as e:
                self._log('warning', '单元[%s] EMCON_Obey_doctrine(False) 失败: %s'
                          % (name, e))
            try:
                obj.doctrine_switch_radar(bool(self.EMCON_FREE_RADAR))
                ok_any = True
                self._log('info', '单元[%s] 条令雷达显式设为%s（不再“与上级保持一致”）'
                          % (name, '主动/开' if self.EMCON_FREE_RADAR else '被动/静默'))
            except Exception as e:
                self._log('warning', '单元[%s] 条令雷达设置失败: %s' % (name, e))
            if ok_any:
                done.append(name)
        self._log('info', '电磁管控“取消与上级一致”完成 %d 个单元' % len(done))
        return done

    # ==================================================================
    # 指令配额安装 / 重绑
    # ==================================================================
    def _install_order_budget(self):
        """安装每周期指令计数器（只包一次），并清零本周期用量。"""
        if not isinstance(getattr(self, '_game_server', None), _OrderBudget):
            self._order_budget = _OrderBudget(self._game_server,
                                              self.CYCLE_ORDER_BUDGET)
            self._game_server = self._order_budget
            n = self._rebind_unit_servers(self._order_budget)
            self._log('info', '已安装指令预算：%d 条/周期（平台按 10 秒窗口 ≤500），'
                              '重绑 %d 个对象' % (self.CYCLE_ORDER_BUDGET, n))
        else:
            self._order_budget = self._game_server
        self._order_budget.reset(self.CYCLE_ORDER_BUDGET)
        return self._order_budget

    def _rebind_unit_servers(self, budget):
        """把本方单元/任务对象的 _game_server 也指向计数器，避免绕过计数。"""
        n = 0

        def _bind(obj):
            try:
                obj._game_server = budget
                return 1
            except Exception:
                return 0

        for attr in ('aircrafts', 'ships', 'submarines', 'satellites',
                     'facilitys', 'weapons', 'groups'):
            coll = getattr(self, attr, None)
            if isinstance(coll, dict):
                for obj in list(coll.values()):
                    n += _bind(obj)
        seen = set()
        for obj in list(getattr(self, '_created_missions', []) or []):
            if obj is None or id(obj) in seen:
                continue
            seen.add(id(obj))
            n += _bind(obj)
        return n

    # ==================================================================
    # 诊断
    # ==================================================================
    def _dump_own_units(self, situation):
        """开局把本方单元清单打进日志（只打一次，便于核对名称匹配）。"""
        if self._diag_done:
            return 0
        self._diag_done = True
        units = self._own_units(situation)
        try:
            by_cat = {}
            for u in units:
                by_cat.setdefault(u['category'] or '?', []).append(
                    '%s[%s]' % (u['name'], u['dbid']))
            self._log('info', '蓝方单元总数 %d（用于核对名称匹配）' % len(units))
            for cat, names in sorted(by_cat.items()):
                names = sorted(names)
                for i in range(0, len(names), 12):
                    self._log('info', '蓝方单元清单(%s %d/%d)：%s'
                              % (cat, min(i + 12, len(names)), len(names),
                                 ' | '.join(names[i:i + 12])))
        except Exception as e:
            self._log('warning', '单元清单输出失败: %s' % e)
        return len(units)

    # ==================================================================
    # 入口：战前规划
    # ==================================================================
    def initial(self, situation):
        """
        每局推演开始前调用一次（战前规划阶段），做赛前部署（顺序不可随意调换）：

            总条令 → 空空弹 WRA → 飞机挂载 → 三舰对空条令 →
            战前移动（M 单元）→ 取消分配（这些单元）→
            31 个支援任务（含「北船机动」）→ 3 个巡逻任务 →
            REASSIGN_TASKS 的“取消分配 → 归位 → 重新分配” →
            电磁管控“取消与上级一致”（爱国者#1）→ 潜艇深度

        说明：战前移动必须早于“建任务 + 分配单元”，否则平台会用默认站位
              覆盖移动结果（开局先回系统原点再走航线）。

        :param situation: tuple, (units dict, contacts dict)
        :return: None
        """
        self._install_order_budget()

        # 平台在“开局那一刻”加载本文件：改代码必须重开一局才生效，
        # 日志里搜 AGENT_BUILD 可确认当前跑的是哪一版。
        self._log('info', 'AGENT_BUILD=2026-11-25-BLUE-HH-11 '
                          '（A/B/C 三任务换阵位并配 装甲车/伪装防空车/反舰导弹排；'
                          '取消装甲车向南逃跑与两舰全速机动，改为战前 M + 任务；'
                          '新增「北船机动」（摩耶/DDH，出航油门=最大）；'
                          '爱国者#1 取消电磁管控“与上级一致”；'
                          '地空导弹连/霍克/捷羚/反舰导弹排/RT火箭炮 战前 M）')

        try:
            self._dump_own_units(situation)
        except Exception as e:
            self._log('error', '单元清单输出异常: %s' % e)

        # initial() 阶段是战前规划，允许一次发完：把“每周期上限”和
        # “每周期睡眠上限”临时放开，真正的限流由 10 秒滚动窗口负责。
        budget = self._order_budget
        old_hard, old_cap = budget.hard_limit, budget.cycle_sleep_cap
        budget.hard_limit = 10 ** 9
        budget.cycle_sleep_cap = 10 ** 9
        try:
            self.set_side_rules()
            self.set_side_air_wra()
            self.set_aircraft_loadouts(situation)
            self.set_ship_doctrines(situation)
            # ⑦-3 战前移动（必须早于任务分配）
            self.prewar_move_units(situation)
            # ⑦-3 取消这些单元的默认任务分配（避免被拉回系统原点）
            self.clear_unit_assignments(situation)
            self.add_all_support_missions(situation)
            self.add_all_patrol_missions(situation)
            # ⑦-4 取消分配 → 重新 M → 重新分配（清掉平台默认站位）
            self.refresh_ground_assignments(situation)
            # ⑦-5 电磁管控：取消“与上级保持一致”
            self.set_emcon_not_inherit(situation)
            # 以下两项已按要求取消（SHIP_RUSH / GROUND_MOVES 均为空，调用即为空转）
            self.rush_ships(situation)
            self.move_ground_units(situation)
            # ⑨ 潜艇深度（佛蒙特 0 米；本局不打战斧）
            self.set_sub_depth(situation)
        finally:
            budget.hard_limit = old_hard
            budget.cycle_sleep_cap = old_cap

        self._log('info', 'initial 完成：本周期下发 %d 条（窗口节流累计睡眠 %.1f 秒）'
                  % (budget.used, budget.paced_sleep))

        # ⑥ 三维监控（唯一信息源）→ 地空导弹营（解析四个防空连与真实挂载射程）
        if getattr(self, 'monitor', None) is not None:
            try:
                self.monitor.setup(situation)
            except Exception as e:
                self._log('error', '三维监控初始化异常: %s' % e)
        if getattr(self, 'sam_defense', None) is not None:
            try:
                self.sam_defense.setup(situation)
            except Exception as e:
                self._log('error', '地空导弹营初始化异常: %s' % e)

    # ==================================================================
    # 取消分配监听（玩家按 U）
    # ==================================================================
    def watch_mission_release(self, situation):
        """
        监听“单元从某个任务里被取消分配”的时刻，并做两件事：
          ① 清空它残留的任务航路（不然它会一直朝原支援任务的阵位跑）；
          ② 速度设 0、油门 FullStop（海马斯这类地面发射车停稳了才能发射）。

        触发条件：上一周期该单元 AssignedMission 非空，本周期变成空。
        退出条件：之后不管它 —— 你手动分配任务或画航线，智能体都不再干预。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本次处理的单元数
        """
        if not self.WATCH_RELEASE:
            return 0
        n = 0
        for u in self._own_units(situation):
            guid = u.get('guid')
            if not guid:
                continue
            obj = self.get_unit(guid)
            if obj is None:
                continue
            mis = str(getattr(obj, 'AssignedMission', '') or '').strip()
            prev = self._mis_prev.get(guid)
            self._mis_prev[guid] = mis
            if prev is None or not prev or mis:
                continue            # 首次记录 / 本来就没任务 / 仍在任务里
            # === 刚被取消分配 ===
            try:
                obj.clear_plotted_course()
            except Exception:
                pass
            try:
                obj.set_desired_speed(0)
            except Exception:
                pass
            try:
                obj.set_throttle(Throttle.FullStop)
            except Exception:
                pass
            n += 1
            self._released.add(guid)
            self._log('info', '单元[%s] 已取消任务分配：清空残留航路并停车'
                              '（可以手动分配弹药/任务了）' % u.get('name'))
        return n

    # ==================================================================
    # 入口：每步决策
    # ==================================================================
    def step(self, time_elapse, situation):
        """
        每个决策间隔（默认 30 秒仿真时间）调用一次。

        本智能体的开局设置都在 initial() 里一次下发完毕、长期生效，
        step() 只做两件兜底：① 重绑指令计数；② 两舰航路为空时补发一次。

        :param time_elapse: int, 推演已过时间（秒）
        :param situation: tuple, (units dict, contacts dict)
        :return: None
        """
        self._cycle_index = getattr(self, '_cycle_index', 0) + 1
        try:
            if getattr(self, '_order_budget', None) is not None:
                self._order_budget.reset(self.CYCLE_ORDER_BUDGET)
                self._rebind_unit_servers(self._order_budget)
        except Exception as e:
            self._log('error', '指令预算重置异常: %s' % e)

        # ① 战斧 BOL（本局已取消，BOL_STRIKES 为空时不做任何事）
        try:
            n = self.do_bol_strikes(situation)
            if n:
                self._log('info', '本周期 BOL 打击成功 %d 次（t=%s）'
                          % (n, time_elapse))
        except Exception as e:
            self._log('error', 'BOL 打击异常: %s' % e)

        # ② 监听“取消分配单元（U）”：把残留的任务航路清掉并停车
        try:
            self.watch_mission_release(situation)
        except Exception as e:
            self._log('error', '取消分配监听异常: %s' % e)

        # ② 兜底：航路被平台清掉（寻路失败等）时补发一次全速机动
        #    **已停用**：SHIP_RUSH 为空，本段自动空转。两舰已改走「北船机动」任务，
        #    任务的出航/阵位航线由平台自己维护，这里不再补发。
        #    恢复办法：把条目填回 SHIP_RUSH，本段即自动恢复工作。
        try:
            for spec, dest in self.SHIP_RUSH:
                for name, guid in self._resolve_units(situation, (spec,)):
                    obj = self.get_unit(guid)
                    if obj is None:
                        continue
                    try:
                        if obj.get_way_points_info():
                            continue
                        obj.plotted_course([dest])
                        obj.set_throttle(Throttle.Flank)
                        self._log('info', '舰船[%s] 航路为空，已补发全速 → %s'
                                  % (name, dest))
                    except Exception as e:
                        self._log('error', '舰船[%s] 补发航线失败: %s' % (name, e))
        except Exception as e:
            self._log('error', '全速机动兜底异常: %s' % e)

        # ③ 地面部队“逃跑”兜底 —— **已停用**（GROUND_MOVES 为空，本段自动空转）
        #
        #  原设计：开局把装甲车送到逃跑点；一旦玩家按 U（取消分配单元）后自己
        #         把车分配给别的任务，智能体就不再插手，否则会覆盖玩家的航路。
        #  现在：装甲车改为“战前 M + 分配 AAAAAAAA/BBBBBBBBB/CCCCCCCC 任务”，
        #        航路交给任务，不再补发逃跑航路。恢复办法：把三条填回 GROUND_MOVES。
        #
        #  这段代码保留，规则如下（三条同时满足才补发）：
        #    1) 距开局不超过 GROUND_FALLBACK_CYCLES 个决策周期；
        #    2) 这辆车此前最多只补发过 1 次；
        #    3) 它当前没有航路、也没有被分配到任何任务（AssignedMission 为空）。
        try:
            cycle = getattr(self, '_cycle_index', 0)
            for specs, dest in self.GROUND_MOVES:
                for name, guid in self._resolve_units(situation, specs):
                    obj = self.get_unit(guid)
                    if obj is None:
                        continue
                    done = self._ground_reissue.get(guid, 0)
                    if done >= 1:
                        continue
                    if guid in self._released:      # 玩家按过 U：绝不补逃跑航路
                        continue
                    if cycle > self.GROUND_FALLBACK_CYCLES:
                        continue
                    # 被玩家分配了任务 -> 一律不动它
                    if str(getattr(obj, 'AssignedMission', '') or '').strip():
                        continue
                    try:
                        if obj.get_way_points_info():
                            continue
                        obj.plotted_course([dest])
                        obj.set_throttle(self.GROUND_THROTTLE)
                        self._ground_reissue[guid] = done + 1
                        self._log('info', '地面单元[%s] 开局航路丢失，补发一次最大速度 → %s'
                                          '（之后不再干预）' % (name, dest))
                    except Exception as e:
                        self._log('error', '地面单元[%s] 补发航线失败: %s' % (name, e))
        except Exception as e:
            self._log('error', '地面机动兜底异常: %s' % e)

        # ④ 三维监控：本周期态势只算一次，供下游各路复用（设计报告 2.3.1）
        if getattr(self, 'monitor', None) is not None:
            try:
                self.monitor.ensure(situation)
            except Exception as e:
                self._log('error', '三维监控扫描异常: %s' % e)

        # ⑤ 地空导弹营攻击与自卫（二分支循环，设计报告 2.3.5）
        #    放在最后：先让任务与地面机动接管航路，再由本智能体决定开/关雷达与发弹。
        if getattr(self, 'sam_defense', None) is not None:
            try:
                self.sam_defense.step(situation)
            except Exception as e:
                self._log('error', '地空导弹营决策异常: %s' % e)

    # ==================================================================
    # 结束
    # ==================================================================
    def deduction_end(self):
        """一局推演结束（可用于保存统计，本智能体不需要）。"""
        try:
            self._log('info', '推演结束：已创建任务 %d 个'
                      % len(self._created_missions))
        except Exception:
            pass
