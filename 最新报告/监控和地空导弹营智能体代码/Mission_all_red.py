# -*- coding:utf-8 -*-
r"""
红方规则智能体 —— 2026 第十届全国兵棋推演大赛 · 联合作战人机协同博弈挑战赛

本文件按用户给的 111.txt + 任务列表.xlsx 逐条实现，功能分七块：

    ① 总条令（set_side_rules）          —— 对空自由开火 / 对海·对地·对潜限制开火，
                                           攻击不忽略计划航线、被攻击不忽略电磁管控、
                                           燃油·武器状态不返航、干扰机与声呐打开
    ② 总条令武器使用规则（set_side_air_wra）—— R-77-1 / R-77M / “流星” / RB107“流星”
                                           四型弹的自动开火距离（50/60/60/60 海里）与
                                           “制导武器-未指定 → 不使用武器”
    ③ 飞机挂载（set_aircraft_loadouts） —— 22 组机型的挂载方案（按机型 + 挂载名
                                           关键字从 model.db 现场查 ID，不写死）
    ④ 舰船条令（set_ship_doctrines）     —— “雷鸣”号护卫舰 #1#2#3#4#5#8#10
                                           对空改为“限制开火（仅限手动）”
    ⑤ 支援任务（SUPPORT_TASKS）          —— 任务列表.xlsx「支援任务」26 条
                                           （苏27-1/苏27-2 额外直接开雷达）
    ⑥ 巡逻任务（PATROL_TASKS）           —— 任务列表.xlsx「巡逻任务」5 条
                                           + 新增「反潜巡逻」（卡-27M#1#2）
    ⑦ 开局动作（BOL_STRIKES / SHIP_MOVES）—— 锆石 ×12 / SS-26“石头” ×4 + ×2
                                           纯方位打击，与 8 组登陆编队 18 节直航
    ⑨ 单独开雷达（set_radar_units）      —— 鸡窝雷达开局开雷达

    BOL 打击是“闭环自愈”的：开局诊断打出每个发射单元真实的弹种/数量/挂架；
    本单元没有这种弹就自动改用真正带着它的同型单元；地面发射车先停车再打；
    下发后**下一周期核对弹药数**，数字下降才算真打出去；平台回“成功”但弹药
    没动，就自动换下一种下发方式（带航迹点 → 不带 → 封装接口 → 只发1发 →
    挂架传0），5 种都失败才放弃，并在日志里附上平台回复原文。
    另外平台**单条指令上限 300 字符**，多航迹点的 BOL 指令会超长被取消，
    代码会按长度裁剪航迹点并说明（见 BOL_MAX_CMD_CHARS）。

------------------------------------------------------------------
一、文件放在哪里、怎么导入
------------------------------------------------------------------
平台运行时把 <安装目录>\intelligent\ai 加入 sys.path，智能体脚本按
    engine.LingYi.entitys.*
导入平台实体库；entitys 目录与 engine\LingYi 同级。因此本文件放在
    <安装目录>\intelligent\ai\engine\LingYi\
下（与 entitys 同级）即可，导入语句与本目录里的蓝方样例保持一致。

客户端导入步骤：进入推演房间 → “智能体”面板 → 选择推演方 **红方** →
“导入/选择脚本” → 选中本文件 → 勾选“规则智能体” → 开始推演。
（战前规划阶段会调用一次 initial()，之后每个决策周期调用一次 step()。）

编辑器里 from engine.LingYi.entitys... 标黄是正常的：工作区没挂该路径，
属 IDE 静态分析提示，不影响平台运行。

运行环境：Python 3.9（entitys 下 gameunit.pyd / deduce_RL.pyd 是 cp39 扩展）。

------------------------------------------------------------------
二、指令条数限制（重要）
------------------------------------------------------------------
平台启动参数 agentOrderCountLimit = 500，且按“任意 10 秒窗口 ≤ 500 条”计。
本智能体开局要下发 450~520 条（条令 + 挂载 + 31 个任务 + 航线），正好卡在
上限上，故内置 _OrderBudget：真·滚动 10 秒窗口节流，超窗口时 sleep 到
窗口滑出再发（不丢包、只是慢一点）。initial() 阶段最多 sleep 十几秒，
远在 10 分钟战前规划窗口内。

------------------------------------------------------------------
三、改哪里
------------------------------------------------------------------
· 单元名对不上：看日志里 “AGENT_BUILD=...” 之后那一行
  “红方单元清单(category) 名称 [dbid]” —— 把真实名字里的关键字
  填进对应 _sel(...) 的第一个参数（允许多个候选关键字）。
· 任务条令：改 SUPPORT_TASKS / PATROL_TASKS 里每条的 doctrine。
· 挂载：改 AIRCRAFT_LOADOUTS，want 是“挂载名必须同时包含的关键字”。
"""

import logging
import math
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

# 战术智能体（独立模块）：物理作战域三维监控 2.3.1 + 登陆船只集群自卫 2.3.4。
# 放在同目录或 engine/LingYi/ 下均可；导入失败不影响主智能体（置 None 即跳过）。
try:
    from engine.LingYi.BattlefieldMonitor import BattlefieldMonitor
    from engine.LingYi.ShipClusterDefense import ShipClusterDefense
except ImportError:                                     # 本地工作区
    try:
        from BattlefieldMonitor import BattlefieldMonitor
        from ShipClusterDefense import ShipClusterDefense
    except Exception:                                   # pragma: no cover
        BattlefieldMonitor = None
        ShipClusterDefense = None


# ======================================================================
# 指令配额：包住平台的 _game_server，按“任意 10 秒 ≤ 460 条”节流
# ======================================================================
class _OrderBudgetExceeded(Exception):
    """本周期已下发指令数触到硬上限（内部信号，不外抛给平台）。"""
    pass


class _OrderBudget(object):
    """
    统计并节流“下发给推演引擎的指令条数”。

    平台限制：任意 10 秒内 ≤ 500 条（agentOrderCountLimit）。
    超出的指令会被“智能体指令条数超出数量限制，已被取消下发”直接丢掉，
    现象就是“设了却没生效”的随机丢包。

    做法：
      ① 每决策周期一个软预算（hard_limit），防单个周期失控；
      ② 真·滚动 10 秒窗口（按真实时钟，跨周期累计）：窗口内将超
         WINDOW_LIMIT 就 sleep 到最早那批滑出窗口再发。
    推演跑得快时，好几个决策周期会挤进同一个 10 秒窗口，光靠①不够，
    所以②是必需的。
    """

    WINDOW_SEC = 10.0
    WINDOW_LIMIT = 460          # 500 留 40 条余量
    MAX_SLEEP = 15.0            # 单次节流最长睡眠
    MAX_SLEEP_PER_CYCLE = 12.0  # 每个决策周期因节流睡掉的总时长上限

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
def _sel(key, *nums):
    """
    构造一个“单元选择器”。

    :param key: str 或 tuple/list，名称关键字（任一命中即可，忽略空格/引号/大小写）
    :param nums: int 或 'a-b'，舷号（单元名里 #n 的 n）；不传表示该型全部单元
    :return: dict, {'keys': (...), 'nums': (...)}

    例：_sel(('苏-75', 'su-75', 'checkmate'), 1, 2)
        _sel('TB2', '1-6', '13-20')
    """
    if isinstance(key, (list, tuple)):
        keys = tuple(str(k) for k in key)
    else:
        keys = (str(key),)
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
    return {'keys': keys, 'nums': tuple(out)}


_PUNCT_RE = re.compile(r'[\s\u3000"“”\'‘’()（）\[\]【】《》<>]')
_NUM_RE = re.compile(r'#\s*(\d+)')


def _norm(text):
    """
    名称归一化：小写、去掉空白与各类引号/括号、统一全半角标点、去掉 - . / ，
    使“苏-27SM/SM3型战斗机#1”“苏27SM SM3 型战斗机 #1”都能对上同一关键字。
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
    """红方规则智能体（2026 全国兵棋推演大赛 · 智能体博弈专项赛）"""

    # ------------------------------------------------------------------
    # 每周期指令预算（平台 agentOrderCountLimit=500，按 10 秒窗口计）
    # ------------------------------------------------------------------
    CYCLE_ORDER_BUDGET = 400

    # ------------------------------------------------------------------
    # ① 总条令
    # ------------------------------------------------------------------
    # 交火规则：对空自由开火；对海/对地/对潜限制开火（仅限手动开火）
    RULE_HOLD_SURFACE = True          # 对海：True=限制开火(仅手动)，False=自由开火
    # 2 机编队任务是否勾选“飞机数低于编队规模要求不能起飞”
    TWO_SHIP_USE_FLIGHT_SIZE = True

    # ------------------------------------------------------------------
    # ② 总条令武器使用规则：三型空空导弹
    #    自动开火距离（海里）+ “制导武器-未指定 → 对这种目标不使用武器”
    # ------------------------------------------------------------------
    SIDE_AIR_WRA = (
        # (武器DBID, 名称, 自动开火距离海里)
        ('2056', 'R-77-1型“蝰蛇”空空导弹', '50'),
        ('3126', 'R-77M型“蝰蛇”空空导弹', '60'),
        ('961', '“流星”空空导弹', '60'),
        # RB107“流星”导弹（与“流星”空空导弹是两个型号，按用户要求一并设置）
        ('371', 'RB107“流星”导弹', '60'),
    )
    # 自动开火距离覆盖的 4 类目标
    AIR_WRA_RANGE_TARGETS = (
        WRA_WeaponTargetType.Air_Contact_Unknown_Type,    # 空中感知-未知类型 1999
        WRA_WeaponTargetType.Aircraft_Unspecified,        # 飞机-未指定       2000
        WRA_WeaponTargetType.Aircraft_5th_Generation,     # 飞机-第五代战斗机 2001
        WRA_WeaponTargetType.Aircraft_4th_Generation,     # 飞机-第四代战斗机 2002
    )

    # ------------------------------------------------------------------
    # ③ 飞机挂载
    #    (单元选择器, 挂载名关键字[须全部命中], 说明, 排除关键字)
    #    —— 挂载 ID 运行期按“本机 DBID + 挂载名”从 model.db 现场查，
    #       换想定/换机型也不会失配；表里没有的飞机保持系统默认挂载。
    # ------------------------------------------------------------------
    AIRCRAFT_LOADOUTS = (
        # 戴高乐号航母
        (_sel(('卡-27', 'ka-27'), 1, 2), ['plab-250'],
         'PLAB-250型深水炸弹', ('长期部署',)),
        (_sel(('阵风m', 'rafale m'), 1, 2, 3, 4, 5, 6), ['流星', 'maximumcap'],
         '“流星”空空导弹, Maximum CAP', ()),
        # NK 机场：苏-34#1#2 换 UPAB-500B；#3 仍 UPAB-1500B
        (_sel(('苏-34', 'su-34', '鸭嘴兽'), 1, 2), ['upab-500b'],
         'UPAB-500B (K08BE)', ()),
        (_sel(('苏-34', 'su-34', '鸭嘴兽'), 3), ['upab-1500b'],
         'UPAB-1500B', ()),
        (_sel(('苏-75', 'su-75', 'checkmate'), 1, 2), ['rvv-sd', 'rvv-md', 'internal'],
         'AA-12[RVV-SD], AA-11[RVV-MD], Internal', ()),
        (_sel(('苏-35', 'su-35'), 1, 2), ['r-77m', '外部挂载'],
         'AA-12型[R-77M], 外部挂载', ()),
        # BL 机场
        (_sel(('苏-24mp', 'su-24mp', '击剑手', '电子情报'), 1), ['电子干扰系统', '机载'],
         '电子干扰系统[机载]', ()),
        (_sel(('苏-27', 'su-27'), 1, 2), ['r-77-1', '标准空战巡逻'],
         'AA-12型“蝰蛇”B[R-77-1], 防御电子对抗吊舱, 标准空战巡逻', ()),
        (_sel(('s-70', 's70', '苏霍伊'), 1, 2, 3, 4), ['as-11'],
         'AS-11型“短裙”反辐射导弹', ('内部',)),
        # CT 机场
        (_sel(('伊尔-96', 'il-96'), 1, 2), ['油箱'],
         '油箱', ()),
        (_sel(('伊尔-22', 'il-22'), 1), ['进攻型'],
         '进攻型电子干扰', ()),
        # CT 机场苏-30SM #1~#4：改挂 AS-17 Krypton C [Kh-31P, ARM] 反辐射弹
        (_sel(('苏-30', 'su-30'), 1, 2, 3, 4), ['krypton c', 'kh-31p'],
         'AS-17 Krypton C [Kh-31P, ARM]', ('long-range',)),
        (_sel(('苏-57', 'su-57'), 1, 2, 3), ['r-77m', '外部挂载'],
         'AA-12型[R-77M], 外部挂载', ()),
        # BM 机场
        (_sel(('苏-75', 'su-75', 'checkmate'), 3), ['rvv-sd', 'rvv-md', 'internal'],
         'AA-12[RVV-SD], AA-11[RVV-MD], Internal', ()),
        (_sel(('图-160', 'tu-160', 'blackjack'), 1), ['24kh-555'],
         'AS-15 Kent C [24 Kh-555]', ()),
        # TF 机场
        #   阵风C#1 → 流星 Maximum CAP（不变）
        #   阵风C#2 → **SBU-54 AASM/M … 重型挂载 AAM Load**（本次改动）
        #   阵风C#3#4 → SBU-64 AASM/M … 重型挂载 AAM Load（不变）
        (_sel(('阵风c', 'rafale c'), 1), ['sbu-64', 'aamload'],
         'SBU-64 AASM/M …, 重型挂载 AAM Load', ()),
        (_sel(('阵风c', 'rafale c'), 2), ['sbu-54', 'aamload'],
         'SBU-54 AASM/M …, 重型挂载 AAM Load', ()),
        (_sel(('阵风c', 'rafale c'), 3, 4),
         [['sbu-64', 'aamload'], ['aasm', 'aamload'], ['sbu-64'], ['aasm'],
          ['sbu-54', 'aamload'], ['sbu-54']],
         'SBU-64 AASM/M …, 重型挂载 AAM Load', ()),
        # BT 机场
        (_sel(('鹰狮', 'gripen', 'jas39', 'jas 39'), 1, 2, 3, 4), ['流星', '最大拦截距离'],
         '“流星”空空导弹, 最大拦截距离', ()),
        (_sel(('苏-35', 'su-35'), 5, 6), ['r-77m', '外部挂载'],
         'AA-12型[R-77M], 外部挂载', ()),
        # 野战机场
        (_sel(('神经元', 'neuron'), 1, 2, 3, 4), ['sbu-54'],
         'SBU-54型先进空对地武器[Mk82, GPS+红外成像导引头]', ()),
        (_sel(('tb2', 'bayraktar'), 9, 10), ['mam-l'],
         'MAM-L', ()),
        (_sel(('前哨', 'forpost'), 7, 8), ['r-77-1', '轻型挂载'],
         'AA-12型“蝰蛇”B[R-77-1], 轻型挂载', ()),
        # 23900 型船坞登陆舰
        (_sel(('卡-29', 'ka-29'), 1), ['空中预警'],
         '空中预警(AEW)', ()),
    )

    # ------------------------------------------------------------------
    # ④ “雷鸣”号护卫舰：对空限制开火（仅限手动开火）
    # ------------------------------------------------------------------
    LEIMING_AIR_HOLD = _sel(('雷鸣', 'leiming'), 1, 2, 3, 4, 5, 8, 10)

    # ------------------------------------------------------------------
    # ⑤-1 需要“直接开雷达”的支援任务（除条令 EMCON 外，再把雷达传感器打开）
    #      目前是用户指定的 苏27-1、苏27-2
    # ------------------------------------------------------------------
    SUPPORT_RADAR_TASKS = ('苏27-1', '苏27-2')

    # ------------------------------------------------------------------
    # ⑨ 开局单独开雷达的单元（鸡窝雷达）
    # ------------------------------------------------------------------
    RADAR_ON_UNITS = (_sel(('鸡窝雷达', '鸡窝'),),)

    # ------------------------------------------------------------------
    # ⑤ 支援任务（任务列表.xlsx「支援任务」26 条）
    #    (任务名, 起点, 终点, 执行单元, 'single'=单机 / 'two'=2机编队)
    #    条令：不勾选 1/3 规则；single=不勾选“飞机数低于编队要求不能起飞”，
    #          two=勾选（编队规模 2 机编队，常用于战斗机）
    # ------------------------------------------------------------------
    SUPPORT_TASKS = (
        # —— 按最新要求暂时停用（单元改去「左制空」巡逻）；需要恢复时去掉行首 # 即可
        # ('左55-1', (50.367839, -5.162245), (50.056556, -6.728588),
        #  (_sel(('苏-75', 'su-75', 'checkmate'), 1),), 'single'),
        ('左75-2', (50.120673, -4.996678), (49.724844, -6.551451),
         (_sel(('苏-75', 'su-75', 'checkmate'), 2),), 'single'),
        # ('左35-1', (49.900000, -4.850000), (49.424844, -6.351452),
        #  (_sel(('苏-35', 'su-35'), 1),), 'single'),
        ('左35-2', (49.700000, -4.700001), (49.124844, -6.151453),
         (_sel(('苏-35', 'su-35'), 2),), 'single'),
        ('左阵风1', (47.761895, -6.388525), (48.241469, -7.545601),
         (_sel(('阵风m', 'rafale m'), 1),), 'single'),
        ('左阵风2', (47.411864, -6.466500), (47.531746, -7.959090),
         (_sel(('阵风m', 'rafale m'), 2),), 'single'),
        ('左阵风3', (47.057291, -6.565606), (46.944564, -7.903308),
         (_sel(('阵风m', 'rafale m'), 3),), 'single'),
        ('左阵风4', (46.803174, -6.496490), (46.274431, -7.503355),
         (_sel(('阵风m', 'rafale m'), 4),), 'single'),
        # 左阵风5：除阵风M#5 外，还加入潜艇/护卫舰/航母（见 MAX_THROTTLE_TASKS）
        #   PR.2235.0 护卫舰#2 不在这里 —— 它要留在原地把 12 发锆石 BOL 打完（见 BOL_STRIKES）
        ('左阵风5', (46.687187, -5.711590), (44.982335, -4.715518),
         (_sel(('阵风m', 'rafale m'), 5),
          _sel(('特拉法尔加', 'trafalgar'), 1),
          _sel(('雷鸣', 'leiming'), 1),
          _sel(('戴高乐', 'de gaulle', 'charles'), 1)), 'single'),
        ('左阵风6', (46.934143, -5.338552), (46.366596, -2.652123),
         (_sel(('阵风m', 'rafale m'), 6),), 'single'),
        ('苏27-1', (49.970791, -1.484154), (49.416815, -1.992696),
         (_sel(('苏-27', 'su-27'), 5, 6),), 'two'),
        # ('苏27-2', (50.013269, -0.200909), (49.640898, 0.280470),
        #  (_sel(('苏-27', 'su-27'), 1, 2, 5),), 'two'),
        # ('苏57-1', (50.436629, -1.635106), (49.516627, -2.277045),
        #  (_sel(('苏-57', 'su-57'), 1),), 'single'),
        # ('苏57-2', (50.473891, -0.786968), (49.432592, -0.402715),
        #  (_sel(('苏-57', 'su-57'), 2),), 'single'),
        # ('苏57-3', (50.588309, -0.032595), (49.838270, 0.702697),
        #  (_sel(('苏-57', 'su-57'), 3),), 'single'),
        # ('苏30下', (51.384539, -0.535780), (50.961952, 0.068215),
        #  (_sel(('苏-30', 'su-30'), 1, 2),), 'two'),
        # ('苏30右', (51.715438, 0.003947), (51.682656, 0.860664),
        #  (_sel(('苏-30', 'su-30'), 3, 4),), 'two'),
        ('苏24下', (50.491375, -1.296941), (50.568311, -1.106095),
         (_sel(('苏-24', 'su-24', '击剑手'), 1),), 'single'),
        ('伊尔22', (51.898900, -0.404904), (52.096831, 0.301381),
         (_sel(('伊尔-22', 'il-22'), 1),), 'single'),
        ('轰炸机', (52.117886, -1.755383), (51.920255, -1.687022),
         (_sel(('苏-75', 'su-75', 'checkmate'), 3),
          _sel(('图-160', 'tu-160', 'blackjack'), 1)), 'single'),
        # 北鹰狮-1/-2：暂时停用（鹰狮 #1~#4 改去「北制空」巡逻）；需要恢复时去掉行首 #
        # ('北鹰狮-1', (53.304179, 1.338981), (53.720193, 1.911309),
        #  (_sel(('鹰狮', 'gripen', 'jas39', 'jas 39'), 1, 2),), 'two'),
        # ('北鹰狮-2', (52.658394, 2.197937), (52.713112, 3.731583),
        #  (_sel(('鹰狮', 'gripen', 'jas39', 'jas 39'), 3, 4),), 'two'),
        ('北35-1', (52.560513, 1.544638), (52.803664, 4.192573),
         (_sel(('苏-35', 'su-35'), 5),), 'single'),
        ('北35-2', (52.788025, 1.551222), (53.305207, 3.445392),
         (_sel(('苏-35', 'su-35'), 6),), 'single'),
        # 北阵风-1：阵风C#1 开局不分配任务；前哨 #5#6 已改去「北制空」，这里不再分配
        ('北阵风-1', (51.970252, 1.612684), (52.416187, 3.420873),
         (), 'single'),
        # 北阵风-2：TF 机场阵风C#2 已按本次要求移出（改去执行“阵风2”巡逻任务），
        #            该支援任务保留参考点，执行单元留空
        ('北阵风-2', (51.687659, 2.640069), (52.170698, 4.702347),
         (), 'single'),

        # ---- 登陆编队支援任务（A~E）：接管原“18 节直航”五个初始操作 ----
        #   任务编辑：取消 1/3 规则；速度高度：水面舰艇航速 出航油门=巡航、阵位油门=全速
        ('A', (49.164936, -2.531478), (49.170956, -2.461836),
         (_sel(('蟾蜍', 'toad'), 1), _sel(('雷鸣', 'leiming'), 2)), 'single'),
        ('B', (49.678446, -1.022172), (49.624784, -0.980575),
         (_sel(('蟾蜍', 'toad'), 2), _sel(('雷鸣', 'leiming'), 4)), 'single'),
        ('C1', (50.084713, -0.857245), (49.678446, -1.022172),
         (_sel(('蟾蜍', 'toad'), 3), _sel(('雷鸣', 'leiming'), 3, 5)), 'single'),
        ('C2', (49.691507, -0.129932), (49.609277, -0.085240), (), 'single'),
        ('D', (50.435972, 0.397802), (50.198125, 0.962301),
         (_sel(('蟾蜍', 'toad'), 4, 5), _sel(('雷鸣', 'leiming'), 8)), 'single'),
        ('E', (51.354555, 1.937944), (51.284655, 2.026502),
         (_sel(('蟾蜍', 'toad'), 6, 7), _sel(('雷鸣', 'leiming'), 10),
          _sel(('pr.2235', 'pr2235', '2235.0', '2235'), 1)), 'single'),
    )

    # ------------------------------------------------------------------
    # ⑥ 巡逻任务（红方人人任务列表.xlsx「巡逻任务」13 条，按最新表格重建）
    #    (任务名, 巡逻类型, 巡逻区四点, 执行单元, 单元条令, 备注)
    #    任务编辑项（所有巡逻任务统一）：取消 1/3 规则、
    #        取消“飞机数低于编队要求不起飞”、取消 OPA、取消 WWR
    #    任务条令（所有巡逻任务统一）：燃油状态-返航=否、武器状态-返航=否、
    #        武器状态-预先规划=任务武器耗光允许使用航炮（推荐）
    #    单元条令：按表格“条令设置”列；空着的（神经元/TB/S70/阵风1）不设，继承总条令
    # ------------------------------------------------------------------
    PATROL_TASKS = (
        # 阵风3：对地自由开火（表格明确写了）
        ('阵风3', MissionPatrolType.ANTI_LAND,
         ((51.014970, 2.169616), (51.338653, 3.219732),
          (50.923242, 3.329843), (50.636700, 2.224140)),
         (_sel(('阵风c', 'rafale c'), 3),
          _sel(('tb2', 'bayraktar'), 7, 8)),
         {'land': WeaponControlStatus.Free},
         '阵风C#3 + TB2#7#8，对地自由开火'),

        ('神经元1', MissionPatrolType.ANTI_LAND,
         ((49.253640, -2.244608), (49.153789, -2.234817),
          (49.146183, -1.969473), (49.263517, -1.984840)),
         (_sel(('神经元', 'neuron'), 1),),
         None, '神经元#1，反地面战巡逻'),

        ('神经元2', MissionPatrolType.ANTI_LAND,
         ((49.391321, -1.047379), (49.212755, -1.059674),
          (49.175342, -0.864944), (49.375730, -0.790384)),
         (_sel(('神经元', 'neuron'), 2),),
         None, '神经元#2，反地面战巡逻（出航油门：加速）'),

        ('神经元3', MissionPatrolType.ANTI_LAND,
         ((49.343800, -0.812450), (49.192100, -0.812450),
          (49.192100, -0.538512), (49.343800, -0.538512)),
         (_sel(('神经元', 'neuron'), 3, 4),),
         None, '神经元#3#4，反地面战巡逻（出航油门：加速）'),

        ('阵风1', MissionPatrolType.ANTI_LAND,
         ((49.691700, 0.134748), (49.444400, 0.134748),
          (49.444400, 0.565967), (49.691700, 0.565967)),
         (_sel(('阵风c', 'rafale c'), 4),),
         None, '阵风C#4，反地面战巡逻'),

        ('阵风2', MissionPatrolType.ANTI_LAND,
         ((49.887483, 0.867620), (49.262512, 1.319737),
          (50.236411, 2.339777), (50.420554, 1.609962)),
         (_sel(('阵风c', 'rafale c'), 2),
          _sel(('苏-34', 'su-34', '鸭嘴兽'), 1, 2)),
         None, '阵风C#2 + 苏-34#1#2，反地面战巡逻（出航油门：加力）'),

        ('TB1', MissionPatrolType.ANTI_LAND,
         ((49.475200, -1.510560), (49.303500, -1.510560),
          (49.303500, -1.248580), (49.475200, -1.248580)),
         (_sel(('tb2', 'bayraktar'), 1, 2, 13, 14),),
         None, 'TB2#1#2#13#14，反地面战巡逻'),

        ('TB2', MissionPatrolType.ANTI_LAND,
         ((49.334743, -0.229921), (49.172473, -0.221411),
          (49.171550, 0.079265), (49.355276, 0.052458)),
         (_sel(('tb2', 'bayraktar'), 3, 4, 15, 16),),
         None, 'TB2#3#4#15#16，反地面战巡逻'),

        ('TB3', MissionPatrolType.ANTI_LAND,
         ((49.855800, 1.404140), (49.649600, 1.404140),
          (49.649600, 1.716640), (49.855800, 1.716640)),
         (_sel(('tb2', 'bayraktar'), 5, 6, 17, 18),),
         None, 'TB2#5#6#17#18，反地面战巡逻'),

        # 防空压制巡逻：表格只写了返航条令，没写武器控制 → 继承总条令
        ('S70-1', MissionPatrolType.SEAD,
         ((49.309963, -2.354200), (48.435346, -1.721087),
          (48.256206, -0.057564), (49.432592, -0.402715)),
         (_sel(('s-70', 's70', '苏霍伊'), 1),
          _sel(('苏-30', 'su-30'), 1, 2)),
         None, 'S-70#1（BL）+ 苏-30#1#2（CT），防空压制巡逻'),

        ('S70-2', MissionPatrolType.SEAD,
         ((49.164396, -0.091327), (48.209604, 0.004134),
          (48.606595, 2.441496), (49.309869, 1.625361)),
         (_sel(('s-70', 's70', '苏霍伊'), 3),
          _sel(('苏-30', 'su-30'), 3, 4)),
         None, 'S-70#3（BL）+ 苏-30#3#4（CT），防空压制巡逻'),

        # 中间保船（替代原「保护船只」）：防空作战巡逻，对空自由开火；
        #   速度高度：出航油门=加力，出航/阵位/攻击高度 = 305 米（见 PATROL_HEIGHT_305）
        #   执行单元：前哨无人机 #1~#4 与 #7#8（#5#6 已改去「北制空」）
        ('中间保船', MissionPatrolType.AIR,
         ((49.569167, -1.297403), (49.491055, -1.363648),
          (49.418070, -0.672153), (49.562069, -0.738725)),
         (_sel(('前哨', 'forpost'), 1, 2, 3, 4, 7, 8),),
         {'air': WeaponControlStatus.Free},
         '防空作战巡逻，对空自由开火（前哨无人机 #1~#4、#7#8）'),

        # 反潜作战巡逻：上一版按你要求新增的，这次没有被列入“删去”，
        # 巡逻任务表里也没有这一条 —— 若确认不要，删掉本段即可。
        ('反潜巡逻', MissionPatrolType.ANTI_SUBMARINE,
         ((48.521000, -7.537190), (48.521000, -6.437110),
          (47.730200, -6.437110), (47.730200, -7.537190)),
         (_sel(('卡-27', 'ka-27'), 1, 2),),
         {'air': WeaponControlStatus.Free, 'subsurface': WeaponControlStatus.Free,
          'radar': True},
         '卡-27M#1#2，反潜作战巡逻'),

        # ---- 本批新增的三条“制空”巡逻 ----
        #   任务编辑：关编队数限制、关 1/3、关 OPA、关 WWR（与其他巡逻任务一致）
        #   任务条令：燃油/武器状态-返航=否；加油/补给=不允许（见 PATROL_NO_REFUEL）
        ('左制空', MissionPatrolType.AIR,
         ((49.765336, -2.428524), (48.657470, -3.290493),
          (47.938771, -0.313775), (49.825192, -0.608619)),
         (_sel(('苏-35', 'su-35'), 1),
          _sel(('苏-75', 'su-75', 'checkmate'), 1),
          _sel(('苏-57', 'su-57'), 1)),
         None, '苏-35#1(NK) + 苏-75#1(NK) + 苏-57#1(CT)'),

        ('右制空', MissionPatrolType.AIR,
         ((49.908397, -0.445543), (47.967905, 0.011377),
          (48.712575, 2.896885), (49.838270, 0.702697)),
         (_sel(('苏-27', 'su-27'), 5, 6),
          _sel(('苏-27', 'su-27'), 1, 2),
          _sel(('苏-75', 'su-75', 'checkmate'), 3),
          _sel(('苏-57', 'su-57'), 2, 3)),
         None, '苏-27#5#6 + 苏-27#1#2(BL) + 苏-75#3(BM) + 苏-57#2#3(CT)'),

        ('北制空', MissionPatrolType.AIR,
         ((53.345385, 2.488864), (52.491295, 2.130234),
          (51.915660, 5.827244), (52.574248, 6.018223)),
         (_sel(('鹰狮', 'gripen', 'jas39', 'jas 39'), 1, 2, 3, 4),
          _sel(('前哨', 'forpost'), 5, 6)),
         None, '鹰狮#1~#4(BT) + 前哨#5#6'),
    )

    # ------------------------------------------------------------------
    # ⑥-2 “出航油门 → 加力”的任务（任务编辑-速度高度设置-飞机航速与高度）
    #      油门枚举：Loiter=低速 / Cruise=巡航 / Full=全速 / Flank=加力
    # ------------------------------------------------------------------
    FAST_THROTTLE = Throttle.Flank
    FAST_TRANSIT_PATROL = ('神经元2', '神经元3', '阵风2', '右制空')
    FAST_TRANSIT_SUPPORT = ('苏57-2',)

    # ------------------------------------------------------------------
    # ⑥-3 任务条令需要“对地自由开火”的巡逻任务
    #      （设置在**任务**的条令上：mission.doctrine_weapon_control_status_land(Free)）
    # ------------------------------------------------------------------
    PATROL_LAND_FREE = (
        '神经元1', '神经元2', '神经元3',
        '阵风1', '阵风2', '阵风3',
        'S70-1', 'S70-2',
        'TB1', 'TB2', 'TB3',
    )

    # ------------------------------------------------------------------
    # ⑥-4 「中间保船」：任务条令对空自由开火 + 出航/阵位/攻击高度 = 305 米
    # ------------------------------------------------------------------
    PATROL_AIR_FREE = ('中间保船',)
    PATROL_HEIGHT_305 = ('中间保船',)

    # 三条“制空”巡逻：任务条令 加油/补给 = 不允许
    PATROL_NO_REFUEL = ('左制空', '右制空', '北制空')

    # ------------------------------------------------------------------
    # ⑦ 开局 BOL 纯方位打击
    # ------------------------------------------------------------------
    # 下发方式的备选顺序（前一种失败/没出弹就换下一种，每种每周期只试一次）：
    #   course  : 底层 api_attack_BOL + 导弹航迹点（首选）
    #   plain   : 底层 api_attack_BOL，不带航迹点
    #   unit    : 单元封装 attack_BOL（不带航迹点）
    #   qty1    : 带航迹点但只发 1 发（验证挂架/弹药是否可发）
    #   mount0  : 挂架号传 0（有些版本对舰载/车载发射装置要求不指定挂架）
    BOL_STRATEGIES = ('course', 'plain', 'unit', 'qty1', 'mount0')

    BOL_STRIKES = (
        # ① PR.2235.0 护卫舰#1：12 发 SS-N-33[3M22 锆石]，途经两点后抵达目标
        #   （实盘：12 发锆石装在 #2 上，#1 没有；代码会自动改用带弹的同型舰）
        {'unit': _sel(('pr.2235', 'pr2235', '2235.0', '2235'), 1),
         'wids': ('3361',), 'kws': ('锆石', 'ss-n-33', '3m22'),
         'qty': 12, 'target': (46.107610, -15.697435),
         'course': [(44.651361, -14.190019), (45.090929, -16.203476)],
         'desc': 'PR.2235.0 锆石'},

        # ② 伊斯坎德尔导弹营#2：4 发 SS-26“石头” → (48.312980, 1.022857)
        #   （SSC-7 不具备 BOL 纯方位发射能力，已按要求改为 SS-26）
        {'unit': _sel(('伊斯坎德尔', 'iskander'), 2),
         'wids': ('1235', '567', '1808', '1830', '2900', '2901'),
         'kws': ('ss-26', '石头', '9m723', 'iskander'),
         'qty': 4, 'target': (48.312980, 1.022857), 'course': [],
         'desc': '伊斯坎德尔 SS-26 4发'},

        # ③ 伊斯坎德尔导弹营#2：2 发 SS-26“石头” → (43.657711, -0.215324)
        {'unit': _sel(('伊斯坎德尔', 'iskander'), 2),
         'wids': ('1235', '567', '1808', '1830', '2900', '2901'),
         'kws': ('ss-26', '石头', '9m723', 'iskander'),
         'qty': 2, 'target': (43.657711, -0.215324), 'course': [],
         'desc': '伊斯坎德尔 SS-26 2发'},

        # ④ 沙赫德无人机发射车：平台不允许纯方位发射，**该任务已取消**
    )

    # ------------------------------------------------------------------
    # ⑧ 战前移动 / 航线
    #   平台区分两种机制：
    #     · PREWAR_MOVES  —— 战前规划阶段“挪位置”（unit_new_position，20km 内）
    #     · SHIP_MOVES    —— 规划航线（plotted_course + 期望航速）
    # ------------------------------------------------------------------
    SHIP_SPEED_KNOTS = 18
    # 到点判定：离航线终点这么近就算到达，然后停车（不再补发航线）
    ARRIVE_KM = 2.0

    # 战前移动：(单元选择器组, 目标点)
    PREWAR_MOVES = (
        # 雷鸣#4、蟾蜍#2
        ((_sel(('雷鸣', 'leiming'), 4), _sel(('蟾蜍', 'toad'), 2)),
         (50.239722, -1.176534)),
        # 雷鸣#3#5、蟾蜍#3、23900 型船坞登陆舰#1
        ((_sel(('雷鸣', 'leiming'), 3, 5), _sel(('蟾蜍', 'toad'), 3),
          _sel(('23900',), 1)), (50.226962, -0.757203)),
        # 蟾蜍#4#5、雷鸣#8
        ((_sel(('蟾蜍', 'toad'), 4, 5), _sel(('雷鸣', 'leiming'), 8)),
         (50.459180, 0.102357)),
        # 蟾蜍#1、雷鸣#2
        ((_sel(('蟾蜍', 'toad'), 1), _sel(('雷鸣', 'leiming'), 2)),
         (49.101122, -3.245283)),
        # 蟾蜍#6#7、雷鸣#10（E 任务那三艘）
        ((_sel(('蟾蜍', 'toad'), 6, 7), _sel(('雷鸣', 'leiming'), 10)),
         (51.679603, 1.513794)),
        # PR.2235.0 护卫舰#1：挪到北边后再分配给 E 任务
        ((_sel(('pr.2235', 'pr2235', '2235.0', '2235'), 1),),
         (53.281799, 1.746800)),
    )

    # 航线：(单元选择器组, 航路点列表, 航速节)
    SHIP_MOVES = (
        # 23900 型船坞登陆舰#1：经 C1 起点 → C1 终点 → (49.638315,-0.997032)，22 节
        ((_sel(('23900',), 1),),
         [(50.084713, -0.857245), (49.678446, -1.022172),
          (49.638315, -0.997032)],
         22),
    )
    # 水面舰艇任务的油门：{任务名: (出航油门, 阵位油门)}
    SHIP_THROTTLE_TASKS = {
        'A': (Throttle.Cruise, Throttle.Full),
        'B': (Throttle.Cruise, Throttle.Full),
        'C1': (Throttle.Cruise, Throttle.Full),
        'C2': (Throttle.Cruise, Throttle.Full),
        'D': (Throttle.Cruise, Throttle.Full),
        'E': (Throttle.Cruise, Throttle.Full),
    }
    # 出航/阵位油门都给“最大”（Throttle.Flank）的任务：
    #   左阵风5：潜艇航速与航深、水面舰艇航速 两项都设为最大
    MAX_THROTTLE_TASKS = {
        '左阵风5': (Throttle.Flank, Throttle.Flank),
    }

    # ------------------------------------------------------------------
    # ⑨ 武器使用规则（单位级）：
    #   雷鸣号 #2#3#4#5#8 —— SA-N-21d(3221)：4 类空中目标都不用武器
    #   S-400 营 #1#2    —— 萨姆21A(2103)/萨姆21B(2104)：3 类制导武器都不用武器
    # ------------------------------------------------------------------
    SAM_AIR_TARGETS = (
        WRA_WeaponTargetType.Air_Contact_Unknown_Type,   # 空中感知-未知类型
        WRA_WeaponTargetType.Aircraft_Unspecified,       # 飞机-未指定
        WRA_WeaponTargetType.Aircraft_5th_Generation,    # 飞机-第五代
        WRA_WeaponTargetType.Aircraft_4th_Generation,    # 飞机-第四代
    )
    SAM_GUIDED_TARGETS = (
        WRA_WeaponTargetType.Guided_Weapon_Unspecified,             # 制导武器-未指定
        WRA_WeaponTargetType.Guided_Weapon_Supersonic,              # 制导武器-超音速
        WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,  # 超音速掠海
    )
    UNIT_WRA = (
        # (单元选择器组, 武器DBID, 目标类型元组, 齐射数)
        ((_sel(('雷鸣', 'leiming'), 2, 3, 4, 5, 8),), '3221',
         SAM_AIR_TARGETS, '0'),
        ((_sel(('s-400', 's400'), 1, 2),), '2103',
         SAM_GUIDED_TARGETS, '0'),
        ((_sel(('s-400', 's400'), 1, 2),), '2104',
         SAM_GUIDED_TARGETS, '0'),
    )
    # 任务级武器规则（必须在“分配单元之后”下发，否则任务武器库是空的）：
    #   A/B/C1/D —— SA-N-21d(3221)：4 类空中目标都不用武器
    #   E        —— SA-N-21d(3221)：未知 1 枚 / 未指定 1 枚 / 五5代 2 枚 / 四代 2 枚
    MISSION_WRA_NAMES = ('A', 'B', 'C1', 'D', 'E')
    MISSION_WRA = {
        'A': ('3221', [(t, '0') for t in SAM_AIR_TARGETS]),
        'B': ('3221', [(t, '0') for t in SAM_AIR_TARGETS]),
        'C1': ('3221', [(t, '0') for t in SAM_AIR_TARGETS]),
        'D': ('3221', [(t, '0') for t in SAM_AIR_TARGETS]),
        'E': ('3221', [
            (WRA_WeaponTargetType.Air_Contact_Unknown_Type, '1'),
            (WRA_WeaponTargetType.Aircraft_Unspecified, '1'),
            (WRA_WeaponTargetType.Aircraft_5th_Generation, '2'),
            (WRA_WeaponTargetType.Aircraft_4th_Generation, '2'),
        ]),
    }

    # 分配完之后再做一次“取消分配 → 重新分配”的任务（清掉平台默认站位缓存）
    REASSIGN_TASKS = ('A', 'B', 'C1', 'D', 'E')

    # ==================================================================
    # 构造 / 日志
    # ==================================================================
    def __init__(self, side_name, params=None):
        RuleAgentBase.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
        self._created_missions = []
        self._loadout_cache = {}     # aircraft_dbid -> [(loadout_id, name)]
        self._bol_done = {}          # BOL 去重/重试状态（旧字段，保留兼容）
        self._bol_state = {}         # BOL 逐项状态：{idx: {'round','fired','pre'...}}
        self._move_arrived = set()   # 已到终点并停车的舰船 guid（不再补发航线）
        self._diag_done = False
        # 战术智能体：三维监控（唯一信息源，2.3.1）+ 登陆船只集群自卫（2.3.4）
        #   把其中任意一个置 None 即可单独关掉，互不影响。
        self.monitor = (BattlefieldMonitor(self)
                        if BattlefieldMonitor is not None else None)
        self.ship_defense = (ShipClusterDefense(self, self.monitor)
                             if ShipClusterDefense is not None else None)

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
        :return: list, [{'guid':.., 'name':.., 'category':.., 'dbid':..}]
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
             只命中**唯一**一个单元，就按它处理并打警告；命中多个则列出来
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
            strict, loose = [], []
            for u in pool:
                if u['guid'] in seen:
                    continue
                bare = _norm(u['name'])
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
    # ① 总条令
    # ==================================================================
    def set_side_rules(self):
        """
        修改总条令（推演方级，只下发一次，下级自动继承）。

        对应 111.txt 第一步：
            对空自由开火；对海/对地/对潜限制开火（仅限于手动开火）；
            攻击时忽略计划航线——否；被攻击时忽略电磁管控——否；
            燃油状态-返航——否（到达燃油状态不返回基地）；
            武器状态——任务武器耗光，允许使用航炮（推荐）；
            武器状态-返航——否（到达武器状态不返回基地）；
            电磁管控：干扰机打开、声呐打开。

        :return: int, 下发条数
        """
        n = 0

        # --- 交火规则 ---
        self.doctrine_weapon_control_status_air(WeaponControlStatus.Free); n += 1
        self.doctrine_weapon_control_status_surface(
            WeaponControlStatus.Hold if self.RULE_HOLD_SURFACE
            else WeaponControlStatus.Free); n += 1
        self.doctrine_weapon_control_status_land(WeaponControlStatus.Hold); n += 1
        self.doctrine_weapon_control_status_subsurface(WeaponControlStatus.Hold); n += 1

        # --- 攻击/被攻击时的航线与电磁管控 ---
        self.doctrine_ignore_plotted_course(
            IgnorePlottedCourseWhenAttacking.No); n += 1
        self.doctrine_ignore_emcon_under_attack(IgnoreEMCONUnderAttack.No); n += 1

        # --- 返航规则 ---
        # 燃油状态-返航：否（到达燃油状态不返回基地）
        self.doctrine_fuel_state_rtb(FuelStateRTB.No); n += 1
        # 武器状态-预先规划：任务武器耗光，允许使用航炮（推荐）
        self.doctrine_weapon_state_planned(
            WeaponStatePlanned.WinchesterUseAirGuns); n += 1
        # 武器状态-返航：否（到达武器状态不返回基地）
        self.doctrine_weapon_state_rtb(WeaponStateRTB.No); n += 1

        # --- 电磁管控 ---
        self.doctrine_switch_oecm(True); n += 1      # 干扰机：打开
        self.doctrine_switch_sonar(True); n += 1     # 声呐：打开
        # 雷达：打开（本次新增的总条令要求；推演方级 EMCON 雷达=开）
        self.doctrine_switch_radar(True); n += 1

        self._log('info', '总条令已下发 %d 条（对空自由/对海·对地·对潜限制开火，'
                          '不忽略计划航线，不忽略电磁管控，燃油·武器状态不返航，'
                          '干扰机+声呐+雷达打开）' % n)
        return n

    # ==================================================================
    # ② 总条令：三型空空导弹 WRA
    # ==================================================================
    def set_side_air_wra(self):
        """
        R-77-1 / R-77M / “流星” 的武器使用规则（推演方级，只下发一次）。

        · 自动开火距离：空中感知-未知类型 / 飞机-未指定 / 第五代 / 第四代
          —— 分别 50 / 60 / 60 海里
        · 齐射武器树：制导武器-未指定 → 对这种目标不使用武器（齐射数 0）

        :return: int, 下发条数
        """
        n = 0
        for wid, name, rng in self.SIDE_AIR_WRA:
            # 对“制导武器-未指定”不使用武器
            self.wra_qty_salvo(
                wid, WRA_WeaponTargetType.Guided_Weapon_Unspecified, '0')
            n += 1
            # 4 类空中目标的自动开火距离
            for t in self.AIR_WRA_RANGE_TARGETS:
                self.wra_firing_range(wid, t, rng)
                n += 1
            self._log('info', '总条令 WRA[%s(%s)]：4 类目标自动开火距离 %s 海里，'
                              '制导武器-未指定 不使用武器' % (name, wid, rng))
        self._log('info', '总条令空空导弹 WRA 共下发 %d 条' % n)
        return n

    # ==================================================================
    # ②-2 总条令：对地武器 / 反辐射导弹 WRA
    #   按要求修改三型对地弹的齐射武器数：
    #     SBU-64“铁锤”（2596）、SBU-54“铁锤”AASM/M（1603）
    #       —— 陆地目标-未知类型 / 陆地结构-软-未指定 / 陆地结构-硬化-未指定 /
    #          移动目标-软-未指定 → “对这种目标不使用武器”（齐射 0）
    #          移动目标-硬化-未指定 → SBU-64 = 3 枚；SBU-54 = 2 枚
    #     KH-58UShKE 反辐射导弹（50002）
    #       —— 雷达-未指定 → 2 枚
    # ==================================================================
    SIDE_GROUND_WRA = (
        ('2596', 'SBU-64“铁锤”型先进空对地武器[Mk82,GPS+半主动激光制导]', (
            (WRA_WeaponTargetType.Land_Contact_Unknown_Type, '0'),
            (WRA_WeaponTargetType.Land_Structure_Soft_Unspecified, '0'),
            (WRA_WeaponTargetType.Land_Structure_Hardened_Unspecified, '0'),
            (WRA_WeaponTargetType.Mobile_Target_Soft_Unspecified, '0'),
            (WRA_WeaponTargetType.Mobile_Target_Hardened_Unspecified, '2'),
        )),
        ('1603', 'SBU-54“铁锤”型先进空对地武器 AASM/M [Hammer,Mk82,GPS+IIR]', (
            (WRA_WeaponTargetType.Land_Contact_Unknown_Type, '0'),
            (WRA_WeaponTargetType.Land_Structure_Soft_Unspecified, '0'),
            (WRA_WeaponTargetType.Land_Structure_Hardened_Unspecified, '0'),
            (WRA_WeaponTargetType.Mobile_Target_Soft_Unspecified, '0'),
            (WRA_WeaponTargetType.Mobile_Target_Hardened_Unspecified, '2'),
        )),
        ('50002', 'KH-58UShKE 反辐射导弹', (
            (WRA_WeaponTargetType.Radar_Unspecified, '2'),
        )),
        ('3712', 'UPAB-500B 卫星制导滑翔增程炸弹(K08BE)', (
            (WRA_WeaponTargetType.Land_Contact_Unknown_Type, '0'),
            (WRA_WeaponTargetType.Land_Structure_Soft_Unspecified, '0'),
            (WRA_WeaponTargetType.Land_Structure_Hardened_Unspecified, '0'),
            (WRA_WeaponTargetType.Mobile_Target_Soft_Unspecified, '0'),
            (WRA_WeaponTargetType.Mobile_Target_Hardened_Unspecified, '2'),
        )),
    )

    def set_side_ground_wra(self):
        """
        SBU-64 / SBU-54 / KH-58UShKE 的齐射武器数（推演方级，只下发一次）。

        :return: int, 下发条数
        """
        n = 0
        for wid, name, rules in self.SIDE_GROUND_WRA:
            for ttype, qty in rules:
                self.wra_qty_salvo(wid, ttype, qty)
                n += 1
            self._log('info', '总条令 WRA[%s(%s)]：%s'
                      % (name, wid,
                         '；'.join('%s→%s' % (t.name, q)
                                  for t, q in rules)))
        self._log('info', '总条令对地/反辐射弹 WRA 共下发 %d 条' % n)
        return n

    # ==================================================================
    # ③ 飞机挂载
    # ==================================================================
    def _loadout_rows(self, aircraft_dbid):
        """
        查某机型在 model.db 里可用的挂载方案 [(loadout_id, name), ...]。

        数据表关系：DataAircraftLoadouts(ID=飞机DBID, ComponentID=挂载DBID)，
        DataLoadout(ID, Name)。结果按机型缓存。

        :param aircraft_dbid: int, 飞机 DBID
        :return: list
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
        if db_path:
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute(
                    'select L.ID, L.Name from DataAircraftLoadouts AL '
                    'join DataLoadout L on L.ID = AL.ComponentID '
                    'where AL.ID = ?', (key,))
                rows = [(int(r[0]), str(r[1] or '')) for r in cur.fetchall()]
                rows.sort()          # 按挂载 ID 排序，保证同样的关键字每次挑到同一条
                conn.close()
            except Exception as e:
                self._log('warning', '查询机型 %s 的挂载方案失败: %s' % (key, e))
                rows = []
        self._loadout_cache[key] = rows
        return rows

    def _pick_loadout(self, unit_name, unit, want, avoid=()):
        """
        在本机可用挂载里，按“挂载名必须同时包含 want 中所有关键字”挑一条。

        :param unit_name: str, 单元名（日志用）
        :param unit: Aircraft, 飞机对象
        :param want: list, 关键字（全部命中）；也支持 list[list]（多组备选，依次尝试）
        :param avoid: tuple, 排除关键字
        :return: (loadout_id, name) 或 (None, '')
        """
        rows = self._loadout_rows(getattr(unit, 'DBID', None))
        if not rows:
            return None, ''
        # 统一成“多组备选”的形式
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
                # “转场/预备飞行/维修”不是作战挂载
                if '转场' in n or '预备飞行' in n or '维修' in n:
                    continue
                if best is None or lid < best[0]:
                    best = (lid, lname)
            if best is not None:
                return best

        # 排查辅助：把本机所有挂载名打出来（便于把关键字补进 AIRCRAFT_LOADOUTS）
        self._log('warning', '飞机[%s] 未找到挂载 %s，本机可选挂载：%s'
                  % (unit_name, want, [x[1] for x in rows][:40]))
        return None, ''

    def set_aircraft_loadouts(self, situation):
        """
        按 AIRCRAFT_LOADOUTS 给指定飞机设置挂载（必须在战前规划阶段调用，
        此时挂载立即完成、准备时间为 0）。

        表里没有的飞机保持系统默认挂载，不做任何修改。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 成功的单元名
        """
        done, missing = [], []
        for spec, want, desc, avoid in self.AIRCRAFT_LOADOUTS:
            found = self._resolve_units(situation, (spec,))
            if not found:
                missing.append('%s(%s)' % (desc, spec['keys'][0]))
                continue
            for name, guid in found:
                unit = self.get_unit(guid)
                if unit is None:
                    continue
                lid, lname = self._pick_loadout(name, unit, want, avoid)
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
        “雷鸣”号护卫舰 #1#2#3#4#5#8#10：对空改为限制开火（仅限手动开火）。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 成功的单元名
        """
        found = self._resolve_units(situation, (self.LEIMING_AIR_HOLD,))
        if not found:
            self._log('warning', '未匹配到任何“雷鸣”号护卫舰，对空限制开火未设置')
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
        self._log('info', '“雷鸣”号对空条令设置完成 %d/%d' % (len(done), len(found)))
        return done

    # ==================================================================
    # ④-2 单位级武器使用规则（雷鸣 SA-N-21d / S-400 萨姆21A·21B）
    # ==================================================================
    def set_unit_wra(self, situation):
        """
        按 UNIT_WRA 给指定单元下发“武器使用规则-齐射武器数”。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 下发条数
        """
        n = 0
        for specs, wid, targets, qty in self.UNIT_WRA:
            found = self._resolve_units(situation, specs)
            if not found:
                self._log('warning', '单元 WRA：未匹配到单元 %s'
                          % [s['keys'][0] for s in specs])
            for name, guid in found:
                unit = self.get_unit(guid)
                if unit is None:
                    continue
                ok_here = 0
                for t in targets:
                    try:
                        unit.wra_qty_salvo(wid, t, qty)
                        ok_here += 1
                        n += 1
                    except Exception as e:
                        self._log('error', '单元[%s] WRA(武器%s/%s) 设置失败: %s'
                                  % (name, wid, getattr(t, 'name', t), e))
                self._log('info', '单元[%s] 武器%s：%d/%d 类目标齐射数设为 %s'
                          % (name, wid, ok_here, len(targets), qty))
        self._log('info', '单元级武器使用规则共下发 %d 条' % n)
        return n

    # ==================================================================
    # ⑦-2 任务级武器使用规则（必须在分配单元之后）
    # ==================================================================
    def refresh_ship_assignments(self, situation):
        """
        分配完 A~E 之后再做一遍“取消分配 → 归位 → 重新分配”。

        平台 bug：船被分配到支援任务时，平台会拿**默认站位**（系统初始起点）
        覆盖刚做过的战前移动。这里在重新分配之前，再把战前移动的目标点下发一次，
        保证“分配那一刻”船就在目标位置上，平台的站位计算才是对的。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 重新分配的舰船数
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
                    self._log('info', '舰船[%s] 取消分配→%s→重新分配 任务[%s]'
                              % (uname,
                                 '归位' if dest else '直接', name))
                except Exception as e:
                    self._log('warning', '舰船[%s] 重新分配任务[%s] 失败: %s'
                              % (uname, name, e))
        self._log('info', 'A~E 舰船“取消分配→重新分配”完成 %d 艘' % n)
        return n

    def set_mission_wra(self):
        """
        给 A/B/C1/D/E 等任务下发“武器使用规则-齐射武器数”。

        注意：必须先建任务 + 分配单元，任务的武器库才有内容，否则设置会失败。

        :return: int, 下发条数
        """
        n = 0
        names = set()
        for m in list(getattr(self, '_created_missions', []) or []):
            name = getattr(m, 'Name', None)
            if name not in self.MISSION_WRA:
                continue
            wid, pairs = self.MISSION_WRA[name]
            ok_here = 0
            for t, qty in pairs:
                try:
                    m.wra_qty_salvo(wid, t, qty)
                    ok_here += 1
                    n += 1
                except Exception as e:
                    self._log('error', '任务[%s] WRA(武器%s/%s) 设置失败: %s'
                              % (name, wid, getattr(t, 'name', t), e))
            names.add(name)
            self._log('info', '任务[%s] 武器%s：%d/%d 类目标齐射数已设置（%s）'
                      % (name, wid, ok_here, len(pairs),
                         '/'.join(q for _t, q in pairs)))
        missing = [x for x in self.MISSION_WRA_NAMES if x not in names]
        if missing:
            self._log('warning', '任务级武器规则：没找到这些任务 %s' % missing)
        self._log('info', '任务级武器使用规则共下发 %d 条' % n)
        return n

    # ==================================================================
    # ⑨ 单独开雷达的单元（鸡窝雷达）
    # ==================================================================
    def set_radar_units(self, situation):
        """
        对 RADAR_ON_UNITS 里的单元“开局单独设置：开雷达”。

        做两步，双保险：
          · doctrine_switch_radar(True)  —— 条令里的电磁管控（EMCON）雷达=开
          · switch_radar(True)           —— 直接把雷达传感器打开

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 成功的单元名
        """
        found = self._resolve_units(situation, self.RADAR_ON_UNITS)
        if not found:
            self._log('warning', '未匹配到要单独开雷达的单元（关键字 %s）'
                      % [s['keys'][0] for s in self.RADAR_ON_UNITS])
            return []
        done = []
        for name, guid in found:
            unit = self.get_unit(guid)
            if unit is None:
                continue
            ok_any = False
            try:
                unit.doctrine_switch_radar(True)
                ok_any = True
            except Exception as e:
                self._log('warning', '单元[%s] 条令雷达开启失败: %s' % (name, e))
            try:
                unit.switch_radar(True)
                ok_any = True
            except Exception as e:
                self._log('warning', '单元[%s] 雷达传感器开启失败: %s' % (name, e))
            if ok_any:
                done.append(name)
                self._log('info', '单元[%s] 已单独设置：雷达打开' % name)
        self._log('info', '单元开雷达设置完成 %d/%d' % (len(done), len(found)))
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
            # 任务条令里的武器控制状态（对地/对海/对空/对潜）
            ('wcs_land', 'doctrine_weapon_control_status_land'),
            ('wcs_surface', 'doctrine_weapon_control_status_surface'),
            ('wcs_air', 'doctrine_weapon_control_status_air'),
            ('wcs_subsurface', 'doctrine_weapon_control_status_subsurface'),
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

        :param doctrine: dict, 可含 key:
                         'air'/'surface'/'subsurface'/'land' -> WeaponControlStatus
                         'radar' -> bool
                         'engage_opportunity' -> EngageWithContactTarget
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
                    # 除了条令 EMCON，再把雷达传感器本身直接打开
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
                                rule, doctrine=None, weapon_rule=None, time_lab=None):
        """
        创建支援任务并分配单元。

        :param situation: tuple, (units dict, contacts dict)
        :param name: str, 任务名
        :param points: list, 阵位航线参考点 [(lat, lon), ...]（起点、终点）
        :param units: tuple, 单元选择器
        :param rule: dict, 任务编辑项
        :param doctrine: dict, 单元级条令
        :param weapon_rule: list, [[武器ID, 目标类型, 齐射数, 开火距离], ...]
        :param time_lab: list, [开始, 结束]
        :return: SupportMission 或 None
        """
        mission = self.create_support_mission(name, list(points))
        if mission is None:
            self._log('error', '创建支援任务失败：%s' % name)
            return None
        self._remember_mission(mission)

        # --- 任务编辑项 ---
        mission.set_one_third_rule(rule.get('one_third_rule', False))
        mission.support_flightSize(rule.get('flight_size', EscortFlightSize.SingleAircraft))
        mission.support_useFlightSize(rule.get('use_flight_size', False))
        if 'active_emcon' in rule:
            mission.support_activeEMCON(rule['active_emcon'])
        if 'loop_type' in rule:
            mission.support_loopType(rule['loop_type'])
        if 'one_time_only' in rule:
            mission.support_oneTimeOnly(rule['one_time_only'])
        # 支援任务没有 patrol_checkOPA/WWR，用通用字段 CheckOPA/CheckWWR 下发
        for key, field in (('OPA', 'CheckOPA'), ('WWR', 'CheckWWR')):
            if key in rule:
                try:
                    mission._set('%s=%s' % (field, str(bool(rule[key])).lower()))
                except Exception as e:
                    self._log('warning', '任务[%s] %s 设置失败: %s' % (name, key, e))

        # --- 任务级条令 ---
        self._apply_mission_doctrine(mission, rule)

        # --- 速度高度设置：出航/阵位油门与高度 ---
        #     throttle_and_altitude = [出航油门, 阵位油门, 出航高度, 阵位高度]
        ta = rule.get('throttle_and_altitude')
        if ta:
            for i, fn in enumerate((mission.support_throttle_transit,
                                    mission.support_throttle_station,
                                    mission.support_transitAltitude,
                                    mission.support_stationAltitude)):
                if i < len(ta) and ta[i] is not None:
                    try:
                        fn(ta[i])
                    except Exception as e:
                        self._log('warning', '支援任务[%s] 油门/高度设置失败: %s'
                                  % (name, e))

        # --- 速度高度设置：水面舰艇 出航/阵位油门 ---
        st = rule.get('ship_throttle')
        if st:
            for i, fn in enumerate((mission.support_set_throttle_transit_ship,
                                    mission.support_set_throttle_station_ship)):
                if i < len(st) and st[i] is not None:
                    try:
                        fn(st[i])
                    except Exception as e:
                        self._log('warning', '支援任务[%s] 舰艇油门设置失败: %s'
                                  % (name, e))

        # --- 速度高度设置：潜艇 出航/阵位油门（航速与航深） ---
        sbt = rule.get('sub_throttle')
        if sbt:
            for i, fn in enumerate((mission.support_set_throttle_transit_submarine,
                                    mission.support_set_throttle_station_submarine)):
                if i < len(sbt) and sbt[i] is not None:
                    try:
                        fn(sbt[i])
                    except Exception as e:
                        self._log('warning', '支援任务[%s] 潜艇油门设置失败: %s'
                                  % (name, e))

        # --- 任务级武器规则 ---
        for item in (weapon_rule or []):
            wid, ttype, qty, rng = item[0], item[1], item[2], item[3]
            if qty is not None:
                mission.wra_qty_salvo(wid, ttype, qty)
            if rng is not None:
                mission.wra_firing_range(wid, ttype, rng)

        # --- 分配单元（平台单条指令 ≤300 字符，按 10 个一片）---
        found = self._resolve_units(situation, units)
        if not found:
            self._log('warning', '支援任务[%s] 未匹配到任何执行单元：%s'
                      % (name, [s['keys'][0] for s in units]))
        for i in range(0, len(found), 10):
            guids = [g for _n, g in found[i:i + 10]]
            try:
                self.assign_units_to_mission(unit_list=guids, mission_name=name)
            except Exception as e:
                self._log('error', '支援任务[%s] 分配单元失败: %s' % (name, e))

        # --- 单元级条令 ---
        self._apply_unit_doctrine(doctrine, found, name)

        # --- 起止时间 ---
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
        按 SUPPORT_TASKS 建 26 个支援任务。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        ok = 0
        for name, p1, p2, units, formation in self.SUPPORT_TASKS:
            two = (formation == 'two')
            rule = {
                'one_third_rule': False,
                # 编队规模：单机 / 2 机编队
                'flight_size': (EscortFlightSize.TwoAircraft if two
                                else EscortFlightSize.SingleAircraft),
                # 飞机数低于编队规模要求不能起飞：单机任务不勾选；2 机编队默认勾选
                'use_flight_size': (self.TWO_SHIP_USE_FLIGHT_SIZE if two else False),
                # 支援任务不限制电磁辐射区域 => 雷达持续开机
                'active_emcon': False,
                # 任务条令：燃油/武器状态不返航；武器耗光允许使用航炮
                'fuel_state_rtb': FuelStateRTB.No,
                'weapon_state_rtb': WeaponStateRTB.No,
                'weapon_state_planned': WeaponStatePlanned.WinchesterUseAirGuns,
                'ignore_plotted_course': IgnorePlottedCourseWhenAttacking.No,
            }
            # 任务编辑-速度高度设置-飞机航速与高度-出航油门：加力
            if name in self.FAST_TRANSIT_SUPPORT:
                rule['throttle_and_altitude'] = [self.FAST_THROTTLE, None, None, None]
            # 任务编辑-速度高度设置-水面舰艇航速：出航巡航 / 阵位全速
            if name in self.SHIP_THROTTLE_TASKS:
                rule['ship_throttle'] = self.SHIP_THROTTLE_TASKS[name]
            # 出航/阵位油门都设为“最大”（左阵风5：潜艇与水面舰艇两项）
            if name in self.MAX_THROTTLE_TASKS:
                rule['ship_throttle'] = self.MAX_THROTTLE_TASKS[name]
                rule['sub_throttle'] = self.MAX_THROTTLE_TASKS[name]
            doctrine = {
                # 对空自由开火（与总条令一致；写明便于单任务调整）
                'air': WeaponControlStatus.Free,
                'radar': True,
            }
            # 用户指定：苏27-1、苏27-2 两个支援任务要“开雷达”
            # 除条令 EMCON 外，再把雷达传感器直接打开（双保险）
            if name in self.SUPPORT_RADAR_TASKS:
                doctrine['radar_direct'] = True
            try:
                m = self.add_set_support_mission(
                    situation, name, [p1, p2], units, rule, doctrine=doctrine)
                if m is not None:
                    ok += 1
            except Exception as e:
                self._log('error', '支援任务[%s] 创建异常: %s' % (name, e))
        self._log('info', '支援任务创建完成 %d/%d' % (ok, len(self.SUPPORT_TASKS)))
        return ok

    # ==================================================================
    # ⑥ 巡逻任务
    # ==================================================================
    def add_set_patrol_mission(self, situation, name, mission_type, area, units,
                               rule=None, doctrine=None, weapon_rule=None, time_lab=None):
        """
        创建巡逻任务并分配单元。

        :param situation: tuple, (units dict, contacts dict)
        :param name: str, 任务名
        :param mission_type: MissionPatrolType
        :param area: list, 巡逻区参考点 [(lat, lon), ...]
        :param units: tuple, 单元选择器
        :param rule: dict, 任务编辑项
        :param doctrine: dict, 单元级条令
        :param weapon_rule: list, WRA
        :param time_lab: list, [开始, 结束]
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

        # --- 任务级条令 ---
        self._apply_mission_doctrine(mission, rule)

        # --- 速度高度设置：出航/阵位/攻击 油门与高度 ---
        #     throttle_and_altitude =
        #         [出航油门, 阵位油门, 攻击油门, 出航高度, 阵位高度, 攻击高度]
        ta = rule.get('throttle_and_altitude')
        if ta:
            for i, fn in enumerate((mission.patrol_set_throttle_transit,
                                    mission.patrol_set_throttle_station,
                                    mission.patrol_set_throttle_attack,
                                    mission.patrol_set_transitAltitude,
                                    mission.patrol_set_stationAltitude,
                                    mission.patrol_set_attackAltitude)):
                if i < len(ta) and ta[i] is not None:
                    try:
                        fn(ta[i])
                    except Exception as e:
                        self._log('warning', '巡逻任务[%s] 油门/高度设置失败: %s'
                                  % (name, e))

        # --- 任务级武器规则 ---
        for item in (weapon_rule or []):
            wid, ttype, qty, rng = item[0], item[1], item[2], item[3]
            if qty is not None:
                mission.wra_qty_salvo(wid, ttype, qty)
            if rng is not None:
                mission.wra_firing_range(wid, ttype, rng)

        # --- 分配单元 ---
        found = self._resolve_units(situation, units)
        if not found:
            self._log('warning', '巡逻任务[%s] 未匹配到任何执行单元：%s'
                      % (name, [s['keys'][0] for s in units]))
        for i in range(0, len(found), 10):
            guids = [g for _n, g in found[i:i + 10]]
            try:
                self.assign_units_to_mission(unit_list=guids, mission_name=name)
            except Exception as e:
                self._log('error', '巡逻任务[%s] 分配单元失败: %s' % (name, e))

        # --- 单元级条令 ---
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
        按 PATROL_TASKS 建 13 个巡逻任务。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        ok = 0
        for name, mtype, area, units, doctrine, note in self.PATROL_TASKS:
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
            # 任务编辑-速度高度设置-飞机航速与高度-出航油门：加速
            if name in self.FAST_TRANSIT_PATROL:
                rule['throttle_and_altitude'] = [self.FAST_THROTTLE,
                                                 None, None, None, None, None]
            # 任务条令：对地自由开火（这几个巡逻任务都要）
            if name in self.PATROL_LAND_FREE:
                rule['wcs_land'] = WeaponControlStatus.Free
            # 任务条令：对空自由开火（中间保船）
            if name in self.PATROL_AIR_FREE:
                rule['wcs_air'] = WeaponControlStatus.Free
            # 速度高度：出航油门=加力，出航/阵位/攻击高度 = 305 米（中间保船）
            if name in self.PATROL_HEIGHT_305:
                rule['throttle_and_altitude'] = [self.FAST_THROTTLE, None, None,
                                                 305, 305, 305]
            # 任务条令：加油/补给 = 不允许（三条制空巡逻）
            if name in self.PATROL_NO_REFUEL:
                rule['doctrine_refuel'] = ERefuel.No
            try:
                m = self.add_set_patrol_mission(
                    situation, name, mtype, area, units, rule, doctrine=doctrine)
                if m is not None:
                    ok += 1
                    self._log('info', '巡逻任务[%s] 条令：%s' % (name, note))
            except Exception as e:
                self._log('error', '巡逻任务[%s] 创建异常: %s' % (name, e))
        self._log('info', '巡逻任务创建完成 %d/%d' % (ok, len(self.PATROL_TASKS)))
        return ok

    # ==================================================================
    # ⑦ BOL 纯方位打击
    # ==================================================================
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
        raw = getattr(res, 'result', res)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode('utf-8', 'replace')
            except Exception:
                raw = str(raw)
        s = str(raw)
        for bad in ('指令执行失败', '超出数量限制', '已被取消下发', '找不到武器'):
            if bad in s:
                return False
        return True

    def _collect_weapon_recs(self, unit):
        """
        扫描单元的挂架 / 弹仓，返回 [(挂架DBID, 武器DBID, 当前数量), ...]。

        **必须同时看 Mounts / Magazines / Loadouts**：舰船与地面发射车的弹
        多数在 Magazines 里（战斧、SSC-7、见证者-136 都是），只看 Mounts 会漏。
        WeaponRecs 既可能是 dict（key->rec）也可能是 list。

        :param unit: Unit, 单元对象
        :return: list
        """
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
                    # 有些结构把挂架再嵌一层（仅当本层没有 WeaponRecs 才往下扫）
                    if isinstance(mv, dict) and 'WeaponRecs' not in mv:
                        for sub in mv.values():
                            if isinstance(sub, dict) and 'WeaponRecs' in sub:
                                _emit(sub, _mount_db(sub, mk))
            elif isinstance(cont, (list, tuple)):
                for mv in cont:
                    _emit(mv, _mount_db(mv, None))
        return recs

    def _all_weapons_on_unit(self, unit):
        """
        列出单元上**全部**武器（诊断用）：[{'weapon','mount','count','name'}]。

        当“找不到指定武器”时把这份清单打进日志，直接就能看出真实 DBID 与名称。
        """
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

    def _count_weapons(self, unit, wids):
        """统计单元上指定武器的剩余总数（用于“指令成功但没出弹”的交叉核对）。"""
        total = 0
        for p in self._find_weapons_on_unit(unit, wids):
            total += int(p.get('count') or 0)
        return total

    def _find_weapons_on_unit(self, unit, wids):
        """
        在单元上找指定武器，返回 [{'weapon':int,'mount':int,'count':int,'name':str}]。

        同一型武器装在多个挂架时**按武器合并**（平台按发射系统统筹配弹），
        取第一个可用挂架号代表整个发射系统。

        :param unit: Unit, 单元对象
        :param wids: tuple, 武器 DBID（字符串或整数）
        :return: list
        """
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

        # 兜底：平台 get_weapon_infos()（只读 Mounts，故仅在前面一无所获时用）
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

    @staticmethod
    def _reply_text(res):
        """把平台 Reply 解成一行可读文本（失败原因就藏在 result 里）。"""
        if res is None:
            return 'None（接口未返回）'
        code = getattr(res, 'code', None)
        raw = getattr(res, 'result', res)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode('utf-8', 'replace')
            except Exception:
                raw = str(raw)
        s = str(raw).strip()
        if len(s) > 400:
            s = s[:400] + '...'
        return 'code=%s result=%s' % (code, s)

    def _find_weapons_by_name(self, unit, keywords):
        """
        按武器“名称关键字”在单元上找弹（DBID 对不上时的兜底）。

        :param unit: Unit, 单元对象
        :param keywords: tuple, 名称关键字（归一化后匹配）
        :return: list, 同 _find_weapons_on_unit
        """
        keys = [_norm(k) for k in (keywords or ()) if k]

        def _hit(wid):
            nm = _norm(self._weapon_name(wid))
            return any(k and k in nm for k in keys)

        # 收集本单元出现过的所有武器 DBID
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

    def _bol_attack(self, unit, lat, lon, mount_db, weapon_db, qty, course=None):
        """
        纯方位（BOL）打击，带导弹航迹规划点。

        entitys/unit.py 的 attack_BOL 只有 5 个参数，底层
        GameServer.api_attack_BOL 支持 course（导弹路径规划点），故优先调底层。

        注意：course 末点必须是目标点（平台沿 course 逐点飞，飞到末点就停），
        这里会自动把目标点补到航线末尾。

        :param unit: 发射单元
        :param lat/lon: 目标经纬度
        :param mount_db: 挂架 DBID
        :param weapon_db: 武器 DBID
        :param qty: 发射数量
        :param course: list, [(lat, lon), ...] 中途航迹点
        :return: 平台返回 / None
        """
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

    def _prepare_bol_launcher(self, obj, name):
        """
        地面发射车 BOL 前先“停车 + 保持阵位”。

        平台里地面单元在机动状态不会开火（蓝方实测：发射车一直机动=打不出去），
        所以先清航路、速度归零、油门停车、保持阵位。
        舰船不动（舰船可以边航行边发射）。

        :param obj: Unit, 单元对象
        :param name: str, 单元名
        :return: bool, 是否按地面发射车处理
        """
        is_ground = False
        coll = getattr(self, 'facilitys', None)
        if isinstance(coll, dict) and getattr(obj, 'ID', None) in coll:
            is_ground = True
        if not is_ground:
            for kw in ('营', '连', '发射车', '阵地', '导弹排', '炮'):
                if kw in str(name):
                    is_ground = True
                    break
        if not is_ground:
            return False
        try:
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
            try:
                obj.hold_positon(True)
            except Exception:
                pass
            self._log('info', 'BOL 前按住地面发射车[%s]（清航路+速度0+油门停车+保持阵位）'
                      % name)
        except Exception as e:
            self._log('warning', 'BOL 前按住[%s]失败: %s' % (name, e))
        return True

    @staticmethod
    def _distance_nm(lat1, lon1, lat2, lon2):
        """两点大圆距离（海里），用于核对“目标是否超出武器射程”。"""
        try:
            r = 3440.065
            p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
            dp = p2 - p1
            dl = math.radians(float(lon2) - float(lon1))
            a = (math.sin(dp / 2.0) ** 2
                 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2)
            return 2.0 * r * math.asin(min(1.0, math.sqrt(a)))
        except (TypeError, ValueError):
            return -1.0

    def _dump_bol_inventory(self, situation):
        """
        开局把 3 个 BOL 单元的“真实挂了什么弹”打进日志（排错用）。

        如果日志里出现 “BOL[...] 未找到指定武器”，直接看这几行的
        “该单元现有武器”就能知道平台里的真实 DBID / 数量 / 挂架号。
        """
        for item in self.BOL_STRIKES:
            found = self._resolve_units(situation, (item['unit'],))
            if not found:
                self._log('warning', 'BOL诊断[%s] 未匹配到单元，关键字=%s'
                          % (item['desc'], list(item['unit']['keys'])))
                continue
            for name, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                inv = self._all_weapons_on_unit(obj)
                want = set()
                for w in item['wids']:
                    try:
                        want.add(int(w))
                    except (TypeError, ValueError):
                        pass
                hit = [p for p in inv if p['weapon'] in want]
                self._log('info', 'BOL诊断[%s] 单元[%s] dbid=%s 位置=(%s, %s) '
                                  '目标=(%.6f, %.6f) 武器种类=%d 目标弹=%s'
                          % (item['desc'], name, getattr(obj, 'DBID', '?'),
                             getattr(obj, 'Lat', '?'), getattr(obj, 'Lon', '?'),
                             item['target'][0], item['target'][1], len(inv),
                             ['%s(%s)x%d@挂架%s' % (p['name'], p['weapon'],
                                                    p['count'], p['mount'])
                              for p in hit] or '未找到'))
                if not hit:
                    self._log('warning', 'BOL诊断[%s] 该单元现有全部武器：%s'
                              % (item['desc'],
                                 ['%s(%s)x%d@挂架%s' % (p['name'], p['weapon'],
                                                        p['count'], p['mount'])
                                  for p in inv] or '无（弹仓可能是空的）'))

    # ------------------------------------------------------------------
    # BOL 指令长度控制
    #   官方《智能体开发与应用指南 V1.1》：**单条指令 300 个字符**，超长指令
    #   会被平台直接取消（日志："智能体指令条数超出长度限制，已被取消下发"）。
    #   实测一条 AttackContact(BOL) 指令：
    #       前缀（含 guid/挂架/弹种/数量/目标）约 130 字符，
    #       每个航迹点 "{ longitude=2.08168, latitude=50.91159}" 约 39 字符，
    #       所以 6 个航迹点 + 目标点 = 409 字符 → 必然被平台拒绝。
    #   对策：下发前先算长度，放不下的航迹点按顺序裁掉（**始终保留目标点为末点**），
    #        并在日志里说明裁掉了哪几个点。
    # ------------------------------------------------------------------
    BOL_MAX_CMD_CHARS = 295

    @staticmethod
    def _bol_cmd_len(guid, mount, weapon, qty, lat, lon, points):
        """
        估算一条 BOL 指令（平台 Lua 文本）的字符数。

        格式与平台日志实测一致：
            AttackContact('<guid>','BOL',{mode=1,mount=<m>,weapon=<w>,qty=<q>,
            LATITUDE='<lat>',LONGITUDE='<lon>',COURSE={{ longitude=.., latitude=..},...}})

        :return: int
        """
        head = ("AttackContact('%s','BOL',{mode=1,mount=%s,weapon=%.1f,qty=%s,"
                "LATITUDE='%.5f',LONGITUDE='%.5f',COURSE={"
                % (guid, mount, float(weapon), qty, lat, lon))
        body = ','.join('{ longitude=%.5f, latitude=%.5f}' % (p[1], p[0])
                        for p in points)
        return len(head) + len(body) + 3      # 末尾 "}})"

    def _fit_bol_course(self, guid, mount, weapon, qty, lat, lon, course):
        """
        把导弹航迹点裁到 BOL_MAX_CMD_CHARS 以内（目标点始终保留在末尾）。

        :param course: list, [(lat, lon), ...]，末点必须是目标点
        :return: (list, list), 能下发的航迹点、被裁掉的航迹点
        """
        pts = list(course)
        dropped = []
        while len(pts) > 1 and \
                self._bol_cmd_len(guid, mount, weapon, qty, lat, lon, pts) > self.BOL_MAX_CMD_CHARS:
            # 倒数第二个点：保证末点（目标点）不被裁掉
            dropped.insert(0, pts.pop(-2))
        return pts, dropped

    def _find_bol_alt_unit(self, situation, item, exclude_guid=None):
        """
        本单元上没有这种弹时，在本方其他单元里找“确实带着这种弹”的发射平台。

        本次实测就踩到了：111.txt 写的是 PR.2235.0 护卫舰#1，但想定里 12 发
        锆石装在 **#2** 上（#1 上根本没有 3361）。硬按编号找只会一直“未找到武器”。
        这里同型舰优先（名字命中同一关键字），其次任意携带该弹的非飞机单元。

        :return: (单元名, guid, 单元对象, plans) 或 None
        """
        best = None
        keys = [_norm(k) for k in (item['unit'].get('keys') or ())]
        for u in self._own_units(situation):
            guid = u['guid']
            if guid == exclude_guid:
                continue
            if (u['category'] or '').lower().startswith('aircraft'):
                continue
            obj = self.get_unit(guid)
            if obj is None:
                continue
            plans = self._find_weapons_on_unit(obj, item['wids'])
            if not plans:
                continue
            bare = _norm(u['name'])
            if any(k and k in bare for k in keys):
                return (u['name'], guid, obj, plans)
            if best is None:
                best = (u['name'], guid, obj, plans)
        return best

    def do_bol_strikes(self, situation):
        """
        开局纯方位打击（每周期推进一次，自带“是否真的出弹”的交叉核对）。

        流程（对每一项 BOL）：
            ① 找单元、找弹 —— **本单元没有这种弹时，自动改用真正携带它的同型单元**
               （本次实测：12 发锆石装在 PR.2235.0 护卫舰 **#2** 上，#1 上没有）；
            ② 地面发射车先“停车 + 保持阵位”，**等一个决策周期再开火**
               （实测机动中的伊斯坎德尔营，BOL 回“成功”但一发弹都不出）；
            ③ 航迹点按平台**单条指令 300 字符**上限裁剪（见 BOL_MAX_CMD_CHARS）；
            ④ 按 BOL_STRATEGIES 依次换下发方式（带航迹点 → 不带 → 封装接口 →
               只发 1 发 → 挂架传 0）；
            ⑤ **下一周期核对弹药数**：数字下降才算真打出去；平台回“成功”
               但弹药没动，就当失败换下一种方式（这正是蓝方踩过的坑：
               回“指令执行成功”但弹没出筒）；
            ⑥ 全部方式都失败则打 error 日志并附平台回复原文，便于定位。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本周期确认打出去的次数
        """
        fired = 0
        for idx, item in enumerate(self.BOL_STRIKES):
            st = self._bol_state.setdefault(
                idx, {'round': 0, 'fired': False, 'pre': None, 'wait': 0,
                      'prep_done': False, 'fit_logged': False,
                      'no_unit': 0, 'no_weapon': 0, 'last_reply': ''})
            if st['fired']:
                continue

            found = self._resolve_units(situation, (item['unit'],))
            if not found:
                st['no_unit'] += 1
                if st['no_unit'] in (1, 5, 15, 30):
                    self._log('warning', 'BOL[%s] 未匹配到单元（关键字 %s），第 %d 个决策周期'
                              % (item['desc'], list(item['unit']['keys']),
                                 st['no_unit']))
                continue
            name, guid = found[0]
            obj = self.get_unit(guid)
            if obj is None:
                st['no_unit'] += 1
                if st['no_unit'] in (1, 5, 15):
                    self._log('warning', 'BOL[%s] 取不到单元对象 guid=%s'
                              % (item['desc'], guid))
                continue

            # ---------- ③ 核对上一轮是否真的出弹 ----------
            #   注意：必须核对**真正开火的那个单元**（可能是自动换上的同型单元），
            #   否则会拿“按编号找到、但根本没有这种弹”的单元去比，误判成功。
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
                if st['wait'] < 2:      # 给平台 1 个周期把弹药扣掉
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
                                   '最后一轮平台回复：%s。'
                                   '（可手动在客户端选中该单元试一次“攻击-纯方位”，'
                                   '确认该弹种/该平台版本是否允许 BOL）'
                          % (item['desc'], st['round'], st['last_reply']))
                continue

            # ---------- ① 找弹（本单元没有，就找真正带着这种弹的单元）----------
            plans = self._find_weapons_on_unit(obj, item['wids'])
            if not plans:
                plans = self._find_weapons_by_name(obj, item.get('kws') or ())
            if not plans:
                alt = self._find_bol_alt_unit(situation, item, exclude_guid=guid)
                if alt is not None:
                    alt_name, alt_guid, alt_obj, plans = alt
                    self._log('warning',
                              'BOL[%s] 单元[%s] 上没有指定武器 %s，'
                              '改用确实携带该弹的同型单元[%s]执行'
                              % (item['desc'], name, item['wids'], alt_name))
                    name, guid, obj = alt_name, alt_guid, alt_obj
                else:
                    st['no_weapon'] += 1
                    if st['no_weapon'] in (1, 5, 15, 30):
                        inv = self._all_weapons_on_unit(obj)
                        self._log('warning',
                                  'BOL[%s] 单元[%s] 上找不到指定武器 %s（第 %d 周期），'
                                  '本方也没有其他单元携带该弹。该单元现有全部武器：%s'
                                  % (item['desc'], name, item['wids'],
                                     st['no_weapon'],
                                     ['%s(%s)x%d@挂架%s' % (p['name'], p['weapon'],
                                                            p['count'], p['mount'])
                                      for p in inv] or '无（弹仓可能是空的）'))
                    continue

            # ---------- ② 地面发射车：先停车，**下一周期再开火** ----------
            #   实测：伊斯坎德尔营开局 DesireSpeed=30、Throttle=4（在机动），
            #   这时下发 BOL 平台回“指令执行成功”，但一发弹都不出。
            if not st['prep_done']:
                st['prep_done'] = True
                if self._prepare_bol_launcher(obj, name):
                    self._log('info', 'BOL[%s] 已让地面发射车[%s]停车并保持阵位，'
                                      '下个决策周期再开火（机动中平台不出弹）'
                              % (item['desc'], name))
                    continue

            plan = plans[0]
            strategy = self.BOL_STRATEGIES[st['round']]
            qty = int(item.get('qty') or plan['count'])
            qty = max(1, min(qty, int(plan['count'])))
            if strategy == 'qty1':
                qty = 1
            mount = 0 if strategy == 'mount0' else plan['mount']
            lat, lon = item['target']

            # ---------- ③ 航迹点按“单条指令 300 字符”裁剪 ----------
            course = list(item.get('course') or []) + [(lat, lon)]
            if strategy in ('course', 'qty1', 'mount0'):
                fit, dropped = self._fit_bol_course(
                    guid, mount, plan['weapon'], qty, lat, lon, course)
                if dropped and not st.get('fit_logged'):
                    st['fit_logged'] = True
                    self._log('warning',
                              'BOL[%s] 平台单条指令上限 %d 字符：%d 个航迹点 + 目标点'
                              '共 %d 点放不下，本次只下发前 %d 个航迹点 + 目标点'
                              '（舍去 %s），其余请在对局中手动补点'
                              % (item['desc'], self.BOL_MAX_CMD_CHARS,
                                 len(course) - 1, len(course), len(fit) - 1,
                                 dropped))
                course = fit if len(fit) > 1 else []
            else:
                course = []

            before = self._count_weapons(obj, item['wids'])
            if strategy == 'unit':
                try:
                    res = obj.attack_BOL(lat, lon, mount, plan['weapon'], qty)
                except Exception as e:
                    res = None
                    self._log('error', 'BOL[%s] 调用 attack_BOL 异常: %s'
                              % (item['desc'], e))
            elif strategy == 'plain' or not course:
                res = self._bol_attack(obj, lat, lon, mount, plan['weapon'], qty, None)
            else:
                res = self._bol_attack(obj, lat, lon, mount, plan['weapon'], qty, course)

            st['pre'] = before
            st['fire_guid'] = guid
            st['last_reply'] = self._reply_text(res)
            ok = self._reply_ok(res)
            dist = self._distance_nm(getattr(obj, 'Lat', None),
                                     getattr(obj, 'Lon', None), lat, lon)
            self._log('info', 'BOL[%s] 第%d轮[%s] 单元[%s] %s x%d 挂架=%s '
                              '目标=(%.6f,%.6f) 距离=%.0f海里 航迹点=%d → %s | 平台回复 %s'
                      % (item['desc'], st['round'] + 1, strategy, name, plan['name'],
                         qty, mount, lat, lon, dist,
                         max(0, len(course) - 1) if course else 0,
                         '指令已接受（下周期核对弹药）' if ok else '指令被拒绝',
                         st['last_reply']))
            if not ok:
                st['round'] += 1        # 明确失败：本周期就直接换下一种方式
                st['pre'] = None
        return fired

    # ==================================================================
    # ⑧ 战前移动 / 航线
    # ==================================================================
    def _unit_new_position(self, guid, dest):
        """
        战前移动单个单元（容错版）。

        ⚠ 平台接口的坐标顺序是 **(经度, 纬度)**：
            unit_new_position(unit_guid, lon_lat=(lon, lat))
        本代码里所有坐标都按 (纬度, 经度) 存，所以这里必须交换，
        否则平台会算出一个几千公里外的点，回“移动位置太远”。

        平台接口：Player.unit_new_position(unit_guid, lon_lat=...)，
        内部要先过 self.get_command_check(unit_guid) 这层“指令检查对象”。
        该钩子在 SDK 里默认是 None（由引擎在加载智能体时注入），
        所以这里做两层兜底：钩子可用就用官方方法，否则直接调底层接口。

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

    def prewar_move_units(self, situation):
        """
        战前规划移动：把指定舰船挪到新位置（接口 unit_new_position，20km 内）。

        必须在正式开战前、且在“分配给任务”之前下发。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功移动的单元数
        """
        ok = 0
        for specs, dest in self.PREWAR_MOVES:
            found = self._resolve_units(situation, specs)
            if not found:
                self._log('warning', '战前移动：未匹配到单元 %s'
                          % [s['keys'][0] for s in specs])
            for name, guid in found:
                try:
                    res = self._unit_new_position(guid, dest)
                    ok += 1
                    if self._reply_ok(res):
                        self._log('info', '战前移动[%s] → (%.6f, %.6f) 成功'
                                  % (name, dest[0], dest[1]))
                    else:
                        self._log('warning',
                                  '战前移动[%s] → (%.6f, %.6f) 平台拒绝：%s'
                                  % (name, dest[0], dest[1],
                                     self._reply_text(res)))
                except Exception as e:
                    self._log('error', '战前移动[%s] 失败: %s' % (name, e))
        self._log('info', '战前移动完成 %d 个单元' % ok)
        return ok

    def clear_unit_assignments(self, situation):
        """
        战前移动之后、分配任务之前：对每艘船下发“取消分配单元”（withdraw_from_mission）。

        平台 bug：做过战前移动的船，若还带着默认的任务分配，会被拉回系统默认起点。
        先取消分配、再重新分配到 A~E 等任务，就不会往初始点赶了。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 处理的舰船数
        """
        n = 0
        for u in self._own_units(situation):
            cat = str(u.get('category') or '')
            if cat not in ('Ship', 'Submarine'):
                continue
            obj = self.get_unit(u.get('guid'))
            if obj is None:
                continue
            try:
                obj.withdraw_from_mission()
                n += 1
            except Exception as e:
                self._log('warning', '取消分配[%s] 失败: %s' % (u.get('name'), e))
        self._log('info', '战前“取消分配单元”完成 %d 艘（避免被拉回默认起点）' % n)
        return n

    def move_ships(self, situation):
        """
        规划舰船航线（plotted_course + 期望航速）。

        做法：清空原航路 → 规划航路点 → 油门最大档 → 期望速度（节 → km/h，
        1 节 = 1.852 km/h；油门给最大档是为了保证低航速舰也能顶到目标航速）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功处理的舰船数
        """
        ok = 0
        for specs, points, knots in self.SHIP_MOVES:
            pts = list(points)
            speed_kmh = float(knots) * 1.852
            found = self._resolve_units(situation, specs)
            if not found:
                self._log('warning', '航线规划：未匹配到单元 %s'
                          % [s['keys'][0] for s in specs])
            for name, guid in found:
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    try:
                        obj.clear_plotted_course()
                    except Exception:
                        pass
                    obj.plotted_course(pts)
                    # 油门给到最大档，再由期望速度把航速压在目标值：
                    #   只给油门不给速度 -> 会跑到该档极速；
                    #   只给速度不给油门 -> 低油门档可能顶不到目标航速。
                    try:
                        obj.set_throttle(Throttle.Flank)
                    except Exception:
                        pass
                    try:
                        obj.set_desired_speed(speed_kmh)
                    except Exception:
                        pass
                    ok += 1
                    self._log('info', '舰船[%s] %d节(%.1f km/h) 航线 %d 点 → %s'
                              % (name, knots, speed_kmh, len(pts), pts[-1]))
                except Exception as e:
                    self._log('error', '舰船[%s] 航线规划失败: %s' % (name, e))
        self._log('info', '舰船航线规划完成 %d 艘' % ok)
        return ok

    def _unit_latlon(self, situation, guid):
        """从 situation 里取单元当前 (纬度, 经度)，取不到返回 None。"""
        units = {}
        if isinstance(situation, (list, tuple)) and len(situation) > 0 \
                and isinstance(situation[0], dict):
            units = situation[0]
        u = (units or {}).get(guid)
        if not isinstance(u, dict):
            return None
        for la, lo in (('Lat', 'Lon'), ('lat', 'lon'),
                       ('latitude', 'longitude')):
            if u.get(la) is not None and u.get(lo) is not None:
                try:
                    return (float(u[la]), float(u[lo]))
                except (TypeError, ValueError):
                    return None
        pos = u.get('position') or u.get('Position')
        if isinstance(pos, dict):
            try:
                return (float(pos.get('Lat')), float(pos.get('Lon')))
            except (TypeError, ValueError):
                return None
        return None

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

    def ensure_ship_moves(self, situation):
        """
        舰船航线兜底 + 到点停车。

        规则：
          · 还有航路 —— 什么都不做；
          · 航路为空且已到终点（距终点 < ARRIVE_KM）—— **停车**（清航路 + 速度 0 +
            保持阵位），并记住“已完成”，以后不再补发航线；
          · 航路为空但离终点很远 —— 视为被平台清掉，补发一次航线。
        """
        checked = 0
        for specs, points, knots in self.SHIP_MOVES:
            pts = list(points)
            dest = pts[-1]
            for name, guid in self._resolve_units(situation, specs):
                if guid in self._move_arrived:
                    continue
                obj = self.get_unit(guid)
                if obj is None:
                    continue
                try:
                    has_wp = bool(obj.get_way_points_info())
                except Exception:
                    continue
                if has_wp:
                    continue

                pos = self._unit_latlon(situation, guid)
                dist = self._km_between(pos, dest) if pos else None
                if dist is not None and dist <= self.ARRIVE_KM:
                    # 到终点：停车
                    self._move_arrived.add(guid)
                    try:
                        obj.set_desired_speed(0)
                    except Exception:
                        pass
                    try:
                        obj.set_throttle(Throttle.FullStop)
                    except Exception:
                        pass
                    try:
                        obj.hold_positon(True)
                    except Exception:
                        pass
                    self._log('info', '舰船[%s] 已到达终点 (%.6f, %.6f)（%.1f km），'
                                      '已停车（速度 0）'
                              % (name, dest[0], dest[1], dist))
                    continue

                checked += 1
                try:
                    obj.plotted_course(pts)
                    obj.set_throttle(Throttle.Flank)
                    obj.set_desired_speed(float(knots) * 1.852)
                    self._log('info', '舰船[%s] 航路为空（距终点 %s km），'
                                      '已补发 %d 节航线 → %s'
                              % (name, '?' if dist is None else '%.1f' % dist,
                                 knots, dest))
                except Exception as e:
                    self._log('error', '舰船[%s] 补发航线失败: %s' % (name, e))
        return checked

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
        """
        开局把本方单元清单打进日志（只打一次）。

        用途：若某条任务/挂载“未匹配到单元”，在这里直接搜真实名字，
        把关键字补进对应的 _sel(...)。同时会打出“可挂载但未匹配”的提示。
        """
        if self._diag_done:
            return 0
        self._diag_done = True
        units = self._own_units(situation)
        try:
            by_cat = {}
            for u in units:
                by_cat.setdefault(u['category'] or '?', []).append(
                    '%s[%s]' % (u['name'], u['dbid']))
            self._log('info', '红方单元总数 %d（用于核对名称匹配）' % len(units))
            for cat, names in sorted(by_cat.items()):
                names = sorted(names)
                # 每条日志最多 12 个单元，避免单行过长被日志系统截断
                for i in range(0, len(names), 12):
                    self._log('info', '红方单元清单(%s %d/%d)：%s'
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
        每局推演开始前调用一次（战前规划阶段），做赛前部署：
            总条令 → 空空弹 WRA → 飞机挂载 → “雷鸣”对空条令 →
            26 个支援任务 → 5 个巡逻任务 → 登陆编队航线

        说明：BOL 纯方位打击放在 step() 里做（“开局之后”），因为要等推演
              真正开始才允许开火。

        :param situation: tuple, (units dict, contacts dict)
        :return: None
        """
        self._install_order_budget()

        # 平台在“开局那一刻”加载本文件：改代码必须重开一局才生效，
        # 日志里搜 AGENT_BUILD 可确认当前跑的是哪一版。
        self._log('info', 'AGENT_BUILD=2026-11-09-RED-21 '
                          '（新增 左/右/北 三条制空巡逻；停用 10 条支援任务；'
                          'UPAB-500B WRA + 苏34#1#2 改挂；苏30 改挂 Kh-31P；'
                          '阵风2/S70-1/S70-2/中间保船 换巡逻区；删 S70-3；'
                          'PR.2235.0#1 战前移动入 E 且 E 的 SA-N-21d 改 1/1/2/2）')

        # 本方单元清单（名称匹配排错用）
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
            # ① 总条令
            self.set_side_rules()
            # ② 空空导弹 WRA
            self.set_side_air_wra()
            # ②-2 对地/反辐射弹 WRA（同属“总条令”板块，仍排在挂载之前）
            self.set_side_ground_wra()
            # ③ 飞机挂载（必须战前规划阶段，准备时间为 0）
            self.set_aircraft_loadouts(situation)
            # ④ “雷鸣”号对空限制开火
            self.set_ship_doctrines(situation)
            # ④-2 单位级武器使用规则（雷鸣 SA-N-21d / S-400 萨姆21A·21B）
            self.set_unit_wra(situation)
            # ⑤ 战前移动（必须早于任务分配）
            self.prewar_move_units(situation)
            # ⑤-1 取消分配单元：避免平台把刚挪过的船拉回系统默认起点
            self.clear_unit_assignments(situation)
            # ⑤-2 舰船航线（23900 型船坞登陆舰#1 三点航线、22 节）
            self.move_ships(situation)
            # ⑥ 支援任务（苏27-1/苏27-2 额外直接开雷达）
            self.add_all_support_missions(situation)
            # ⑦ 巡逻任务（含新增的反潜巡逻）
            self.add_all_patrol_missions(situation)
            # ⑦-1 A~E 的船：取消分配 → 重新分配（清掉平台默认站位，避免船回初始起点）
            self.refresh_ship_assignments(situation)
            # ⑦-2 任务级武器规则（必须晚于“分配单元”，否则任务武器库是空的）
            self.set_mission_wra()
            # ⑧ BOL 单元诊断：把 BOL 单元真实携带的弹打出来（不占几条指令）
            self._dump_bol_inventory(situation)
            # ⑨ 鸡窝雷达：开局单独设置，开雷达
            self.set_radar_units(situation)
        finally:
            budget.hard_limit = old_hard
            budget.cycle_sleep_cap = old_cap

        self._log('info', 'initial 完成：本周期下发 %d 条（窗口节流累计睡眠 %.1f 秒）'
                  % (budget.used, budget.paced_sleep))

        # ⑩ 三维监控（唯一信息源）→ 登陆船只集群自卫（解析舰队与舰空导弹射程）
        if getattr(self, 'monitor', None) is not None:
            try:
                self.monitor.setup(situation)
            except Exception as e:
                self._log('error', '三维监控初始化异常: %s' % e)
        if getattr(self, 'ship_defense', None) is not None:
            try:
                self.ship_defense.setup(situation)
            except Exception as e:
                self._log('error', '舰船自卫初始化异常: %s' % e)

    # ==================================================================
    # 入口：每步决策
    # ==================================================================
    def step(self, time_elapse, situation):
        """
        每个决策间隔（self.agent_decision_time，默认 30 秒仿真时间）调用一次。

        本盘的自动动作只有两件：
            ① 开局 BOL 纯方位打击（每周期重试，成功即停）；
            ② 登陆编队航路为空时补发一次直航。
        其余设置都是“下发一次即长期生效”，不重复占用指令配额。

        :param time_elapse: int, 推演已过时间（秒）
        :param situation: tuple, (units dict, contacts dict)
        :return: None
        """
        try:
            if getattr(self, '_order_budget', None) is not None:
                self._order_budget.reset(self.CYCLE_ORDER_BUDGET)
                self._rebind_unit_servers(self._order_budget)
        except Exception as e:
            self._log('error', '指令预算重置异常: %s' % e)

        # ① 开局 BOL 打击（每周期重试，成功即记入去重表）
        try:
            n = self.do_bol_strikes(situation)
            if n:
                self._log('info', '本周期 BOL 打击成功 %d 次（t=%s）'
                          % (n, time_elapse))
        except Exception as e:
            self._log('error', 'BOL 打击异常: %s' % e)

        # ② 登陆编队航路兜底（只在航路为空时补发）
        try:
            self.ensure_ship_moves(situation)
        except Exception as e:
            self._log('error', '登陆编队航线兜底异常: %s' % e)

        # ③ 三维监控：本周期态势只算一次，供下游各路复用（设计报告 2.3.1）
        if getattr(self, 'monitor', None) is not None:
            try:
                self.monitor.ensure(situation)
            except Exception as e:
                self._log('error', '三维监控扫描异常: %s' % e)

        # ④ 登陆船只集群自卫（三类威胁 × ABDE/C 两区，设计报告 2.3.4）
        #    放在最后：先保证航路与 BOL，再处理告警，避免自卫机动打断开局部署。
        if getattr(self, 'ship_defense', None) is not None:
            try:
                self.ship_defense.step(situation)
            except Exception as e:
                self._log('error', '舰船自卫决策异常: %s' % e)

    # ==================================================================
    # 结束
    # ==================================================================
    def deduction_end(self):
        """一局推演结束（可用于保存统计，本智能体不需要）。"""
        try:
            n = sum(1 for st in self._bol_state.values() if st.get('fired'))
            self._log('info', '推演结束：BOL 完成 %d/%d 项'
                      % (n, len(self.BOL_STRIKES)))
        except Exception:
            pass
