# -*- coding:utf-8 -*-
r"""
蓝方规则智能体 —— 第十届全国兵棋推演大赛专项赛

本文件按步骤逐步构建，当前已完成：
    第一步：修改总条令（set_rules）
    第二步：创建任务 1 —— 运输机支援（支援任务，C-5M 型运输机 #1/#2）

文件放置位置：
    与 engine/LingYi/entitys 同级，即 D:\LingYi\intelligent\ai\engine\LingYi\ 下。
    平台运行时把 D:\LingYi\intelligent\ai 加入 sys.path，故 import 路径为
    engine.LingYi.entitys.*；编辑器里这三行标黄是因为工作区没挂载该路径，
    属 IDE 静态分析提示，不影响平台运行（已用真实引擎实测导入通过）。

运行环境：Python 3.9（entitys 下 gameunit.pyd / deduce_RL.pyd 为 cp39 扩展，
用 3.13 等其它版本会报 DLL load failed）。
"""

import logging
import math
import re
import time

from engine.LingYi.entitys.global_util import *
from engine.LingYi.entitys.agent_base import RuleAgentBase
from engine.LingYi.entitys.player import *


class _OrderBudgetExceeded(Exception):
    """本周期已下发指令数触到硬上限（内部信号，不会外抛给平台）。"""
    pass


class _OrderBudget(object):
    """
    包住平台的 _game_server，统计"本决策周期"已下发的指令条数。

    为什么需要：
        平台启动参数 agentOrderCountLimit=500，且实测是**按每 10 秒窗口**计
        （日志实证：run 123 在首次丢弃前已被接受 1047 条，但其中最近 10 秒
        只有 525 条）。超出窗口的指令会被平台
        "智能体指令条数超出数量限制，已被取消下发" 直接丢掉 ——
        现象就是"设了却没生效"的随机丢包。

    计数口径：
        代理侧一次 `_game_server.api_*` 调用 = 平台一条 Lua 指令；
        建任务（api_create_*_mission）还会附带"每个坐标点一条 AddReferencePoint"，
        故对这两种调用按 fan-out 加权。

    本类用 __getattr__ 透传所有非 api_ 属性，对外行为与原对象一致。

    🔴 双重闸门（对应"比赛时被截断"的坑）：
        ① 每决策周期预算（reset() 清零，hard_limit）；
        ② **滚动 10 秒窗口**（按**真实时钟**计时，跨周期累计）——
           平台的限制本来就是"任意 10 秒内 ≤ 500 条"。
        为什么必须有 ②：比赛时推演跑得快（网速快），30 秒推演时间可能只花
        2~3 秒真实时间，于是**好几个决策周期会挤进同一个 10 秒窗口**，
        光靠①（每周期 ≤400）仍可能在 10 秒内累计到 800+ 条而被平台截断。
        ② 会在这时自动把剩下的条目推迟到窗口空出来再发（不丢、只是慢一点）。
    """

    # 平台真实规则：任意 10 秒内 ≤ 500 条。这里按真实时钟精确复刻，留 40 条余量。
    WINDOW_SEC = 10.0
    WINDOW_LIMIT = 460
    # 单次节流最长睡眠（防御性上限）：超过就改为"整项顺延到下个周期"，
    #   绝不长期阻塞决策调用（平台等推演服务器的时间是有限的）。
    MAX_SLEEP = 15.0
    # 每个决策周期内**因节流而睡掉的总时长上限**：
    #   单次决策调用不能被拖太久（引擎实测能容忍 13s 左右）。
    #   一个周期最多睡 12s，剩下的条目"整项顺延"到下个周期继续，
    #   既不会超窗口、也不会把决策调用拖死。约 2~3 个周期即可发完开局设置。
    MAX_SLEEP_PER_CYCLE = 12.0

    def __init__(self, real, hard_limit):
        self._real = real
        self.hard_limit = int(hard_limit)
        self.used = 0
        # [(下发时刻, 条数)]：最近 WINDOW_SEC 秒内已下发的记录（**跨周期不清零**）
        self._stamps = []
        self.paced_sleep = 0.0      # 累计因窗口节流睡掉的秒数（诊断用）
        self.cycle_sleep = 0.0      # **本决策周期**已睡掉的秒数
        # 本周期允许因节流睡掉的总时长（initial 里会临时放开到无限）
        self.cycle_sleep_cap = self.MAX_SLEEP_PER_CYCLE

    def reset(self, hard_limit=None):
        """每个决策周期开始时清零（**只清周期计数，绝不清窗口时间戳**）。"""
        self.used = 0
        self.cycle_sleep = 0.0
        self.cycle_sleep_cap = self.MAX_SLEEP_PER_CYCLE
        if hard_limit is not None:
            self.hard_limit = int(hard_limit)

    def _prune(self, now):
        """丢掉已经滑出窗口的记录。"""
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
        """
        真·滚动窗口节流：10 秒窗口内将超过 WINDOW_LIMIT 时，
        **sleep 到最早那批指令滑出窗口**再发。

        🔴 为什么必须 sleep 而不是"顺延到下一个决策周期"：
           平台按 10 秒滚动窗口计数，而两个决策周期可能落在同一窗口里
           （日志实证：initial 458 条 + 紧随其后的第一步决策 375 条，
            两个周期合计 833 条落在同一个 10 秒窗口 -> 全部被取消下发）。
           sleep 到窗口滑出，才能从根上保证"任意 10 秒 ≤ 460"。

        :param cost: int, 本次要发的条数
        :return: bool, True=已让出空间可以发；False=放不下，应顺延到下个周期
        """
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
                return False        # 窗口里全是刚发的，本周期放不下
            if slept + wait > self.MAX_SLEEP:
                return False        # 防御：不长期阻塞，交给"整项顺延"
            if self.cycle_sleep + slept + wait > self.cycle_sleep_cap:
                return False        # 本周期睡得够久了 -> 剩余条目顺延到下周期
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
            # 建任务：每个"坐标点"还会额外产生一条 AddReferencePoint
            if item.startswith('api_create_') and item.endswith('_mission'):
                pts = a[2] if item.endswith('support_mission') else (
                      a[3] if item.endswith('patrol_mission') else None)
                if isinstance(pts, (list, tuple)):
                    cost += sum(1 for p in pts if isinstance(p, (list, tuple)))
            # 闸门①：本决策周期预算（先查，避免白睡）
            if self.used + cost > self.hard_limit:
                raise _OrderBudgetExceeded(
                    '%s 触到本周期硬上限 %d 条' % (item, self.hard_limit))
            # 闸门②：真·滚动 10 秒窗口（sleep 到窗口滑出；放不下则整项顺延）
            if not self._pace(cost):
                raise _OrderBudgetExceeded(
                    '%s 触到 10 秒窗口上限 %d 条，整项顺延到下个周期'
                    % (item, self.WINDOW_LIMIT))
            now = time.time()
            self._prune(now)
            self.used += cost
            self._stamps.append((now, cost))
            res = fn(*a, **k)
            # 新建出来的任务对象要重绑到本代理，否则后续任务级
            # SetMission/SetDoctrine 会绕过计数。
            if item.startswith('api_create_') and item.endswith('_mission'):
                try:
                    if res is not None and hasattr(res, '_game_server'):
                        res._game_server = self
                except Exception:
                    pass
            return res
        return wrapper


class Agent(RuleAgentBase):
    """蓝方规则智能体"""

    # 潜艇浅水发射深度（米）。艇体顶部深度超过约 45m 时，浅水发射会失败，
    # 故取 40m；如平台报"潜艇深度不满足导弹发射条件"，可下调到 20~30 再试。
    SUB_SHALLOW_DEPTH = 40
    # 初始 BOL 打击时潜艇的深度（按要求：20 米）
    SUB_BOL_DEPTH = 20

    # ==================================================================
    # 每周期指令预算（对应平台启动参数 agentOrderCountLimit=500，每 10 秒窗口）
    #
    #   🔴 为什么要有这个：平台只保证"任意 10 秒内 ≤500 条"，超出的会被
    #      "智能体指令条数超出数量限制，已被取消下发"丢掉（随机丢包）。
    #      以前 initial() 一口气发 870 条，队尾的设置经常被吞（表现为
    #      "任务建好了、但速度/潜深/WRA 没生效"）。
    #
    #   做法：initial() 只发"必须在战前规划阶段完成"的少量指令，
    #        其余进 _setup_queue，step() 里每周期按预算发一批。
    #        实测单个阶段最贵 165 条（任务一~九），故取 400 为硬上限 ——
    #        任何 10 秒窗口内最多 400 条（< 500）。另有一道"滚动 10 秒窗口"
    #        闸门（见 _OrderBudget）兜住"推演跑得快、多个周期挤进同一窗口"的情况。
    #        870 条约 3 个周期发完（约 90 秒推演时间，仍在战前规划窗口内）。
    # ==================================================================
    CYCLE_ORDER_BUDGET = 400

    # ==================================================================
    # 第三步：飞机挂载方案（机型 DBID 与挂载方案 ID 均取自 model.db 实测）
    #   单元名取自平台态势日志；挂载 ID 已校验"确实属于该机型"。
    # ==================================================================
    # {单元名: (挂载方案ID, 说明)}
    AIRCRAFT_LOADOUTS = {
        # 企业号航母：F/A-18F #1~#4
        #   AGM-154C-1 联合防区外武器[内装多级侵彻战斗部]，先进瞄准前视红外吊舱，短程
        'F/A-18F型 战斗机 #1': (19385, 'AGM-154C-1 JSOW[多级侵彻], 先进瞄准前视红外吊舱, 短程'),
        'F/A-18F型 战斗机 #2': (19385, 'AGM-154C-1 JSOW[多级侵彻], 先进瞄准前视红外吊舱, 短程'),
        'F/A-18F型 战斗机 #3': (19385, 'AGM-154C-1 JSOW[多级侵彻], 先进瞄准前视红外吊舱, 短程'),
        'F/A-18F型 战斗机 #4': (19385, 'AGM-154C-1 JSOW[多级侵彻], 先进瞄准前视红外吊舱, 短程'),
        # 企业号航母：F/A-18F #5~#6 —— ADM-160C 改进型小型空射诱饵干扰弹
        'F/A-18F型 战斗机 #5': (19852, 'ADM-160C改进型小型空射诱饵干扰弹'),
        'F/A-18F型 战斗机 #6': (19852, 'ADM-160C改进型小型空射诱饵干扰弹'),
        # 企业号航母：F-35C #1~#2 —— A/A: AIM-260 JATM, AIM-9X Sidewinder, External
        'F-35C 型“闪电II” 战斗机 #1': (26473, 'A/A: AIM-260 JATM, AIM-9X Sidewinder, External'),
        'F-35C 型“闪电II” 战斗机 #2': (26473, 'A/A: AIM-260 JATM, AIM-9X Sidewinder, External'),
        # 阿斯图机场：B-2A #1~#2 —— AGM-158C LRASM
        'B-2A 轰炸机 #1': (150006, 'AGM-158C LRASM'),
        'B-2A 轰炸机 #2': (150006, 'AGM-158C LRASM'),
        # 奥尔良机场：F-16V #1~#4
        #   AGM-154C 联合防区外武器[内装多级侵彻战斗部]，
        #   “狙击手”XR瞄准吊舱 & “蓝盾”夜间低空导航吊舱[前视红外]，近程
        'F-16V型 BLK 70/72 “战隼”战斗机 #1': (9481, 'AGM-154C JSOW[多级侵彻], 狙击手XR&蓝盾夜间吊舱, 近程'),
        'F-16V型 BLK 70/72 “战隼”战斗机 #2': (9481, 'AGM-154C JSOW[多级侵彻], 狙击手XR&蓝盾夜间吊舱, 近程'),
        'F-16V型 BLK 70/72 “战隼”战斗机 #3': (9481, 'AGM-154C JSOW[多级侵彻], 狙击手XR&蓝盾夜间吊舱, 近程'),
        'F-16V型 BLK 70/72 “战隼”战斗机 #4': (9481, 'AGM-154C JSOW[多级侵彻], 狙击手XR&蓝盾夜间吊舱, 近程'),
        # 直升机驱逐舰：F-35B #1~#2 —— A/A: AIM-120C-7 AMRAAM, AIM-9X, Light External
        'F-35B型“闪电II” 战斗机 #1': (28480, 'A/A: AIM-120C-7 AMRAAM, AIM-9X Sidewinder, Light External'),
        'F-35B型“闪电II” 战斗机 #2': (28480, 'A/A: AIM-120C-7 AMRAAM, AIM-9X Sidewinder, Light External'),
        # 其余飞机不在此表内 -> 保持系统默认挂载，不做任何修改
    }

    # ==================================================================
    # 第三步：五艘水面舰的统一条令
    # ==================================================================
    SHIP_DOCTRINE_UNITS = [
        'CVN 80 “企业号”福特级航空母舰',
        '“阿利伯克”级导弹驱逐舰',
        'CG-52 “邦克山”提康德罗加级号巡洋舰',
        'DDG 179 摩耶级驱逐舰',
        'DDH 183 IZUMO直升驱逐舰 [22DDH CLASS]',
    ]

    # ==================================================================
    # 第四步：任务一~任务九 的公共默认项
    #   1/3 规则关闭、不勾选"飞机数低于编队规模要求不能起飞"
    #   并且统一**不勾选**：
    #     · 对巡逻区外的探测目标进行分析 (OPA)
    #     · 对武器射程内探测目标进行分析 (WWR)
    #   （巡逻任务的额外返航条令见下方 PATROL_RULE_BASE）
    # ==================================================================
    SUPPORT_RULE_BASE = {
        'one_third_rule': False,
        'flight_size': EscortFlightSize.SingleAircraft,
        'use_flight_size': False,
        # 支援任务不限制电磁辐射区域 => 雷达持续开机
        'active_emcon': False,
        # 不分析巡逻区外探测目标 / 不分析武器射程内目标
        'OPA': False,
        'WWR': False,
    }
    # F-35C 的 AIM-260：对下列目标一律"不使用武器"
    AIM260_DBID = '3567'
    AIM260_NO_USE_TARGETS = (
        WRA_WeaponTargetType.Air_Contact_Unknown_Type,        # 空中感知-未知类型
        WRA_WeaponTargetType.Guided_Weapon_Unspecified,       # 制导武器-未指定
        WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,
        WRA_WeaponTargetType.Guided_Weapon_Subsonic_Sea_Skimming,
        WRA_WeaponTargetType.Guided_Weapon_Supersonic,
        WRA_WeaponTargetType.Guided_Weapon_Subsonic,
        WRA_WeaponTargetType.Guided_Weapon_Ballistic,         # 制导武器-弹道导弹
    )
    AIM260_AUTO_FIRE_RANGE_NM = '80'   # 对所有飞机的自动开火距离 80 海里

    # ==================================================================
    # 修改一：巡逻任务（任务一~四）追加的返航条令
    #   燃油状态-返航：否（到达燃油状态不返回基地）
    #   武器状态-返航：否（飞机到达武器状态不返回基地）
    #   武器状态-预先规划：任务武器耗光，允许使用机炮（推荐）
    #
    #   说明：平台枚举中"允许使用机炮"只存在于 WeaponStatePlanned
    #   （= WinchesterUseAirGuns 2002），WeaponStateRTB 只有
    #   No / YesLastUnit / YesFirstUnit / YesLeaveGroup 四个值，
    #   没有机炮选项。因此"允许使用机炮"落在"预先规划"这一项上。
    # ==================================================================
    PATROL_RULE_BASE = {
        'one_third_rule': False,
        'flight_size': EscortFlightSize.SingleAircraft,
        'use_flight_size': False,
        # 不分析巡逻区外探测目标 / 不分析武器射程内目标
        'OPA': False,
        'WWR': False,
        # --- 修改一：返航条令 ---
        'fuel_state_rtb': FuelStateRTB.No,                    # 燃油状态-返航：否
        'weapon_state_rtb': WeaponStateRTB.No,                # 武器状态-返航：否
        'weapon_state_planned': WeaponStatePlanned.WinchesterUseAirGuns,  # 耗光允许机炮
    }

    # ==================================================================
    # 修改二：所有任务 —— 三种空空导弹对 7 类目标"不使用武器"
    # ==================================================================
    AIM_NO_USE_WEAPONS = (
        '945',    # AIM-9X型“响尾蛇”空空导弹
        '2780',   # AIM-9X-2型“响尾蛇”空空导弹
        '3664',   # AIM-9X-2“响尾蛇”Blk III空对空导弹
        '51',     # AIM-120D型“阿姆拉姆”先进中程空空导弹 P3I.4
        '3608',   # AIM-120D型“阿姆拉姆”先进中程空空导弹 P3I.4
        '3567',   # AIM-260 JATM 联合先进战术导弹
    )

    # ==================================================================
    # 总条令补充：三型中距弹的武器使用规则（WRA）
    #   每型都是：对"空中感知-未知类型"不使用武器；对所有制导武器不使用武器；
    #             对所有飞机齐射 1 枚；对飞机的自动开火距离分别为 45/60/80 海里
    # ==================================================================
    MID_RANGE_WRA = (
        # (武器DBID, 名称, 自动开火距离海里)
        ('718', 'AIM-120C-7型“阿姆拉姆”先进中程空空导弹 P3I.3', '45'),
        # AIM-120D：要求"打所有飞机只发射一枚弹"（两种 DBID 都覆盖）
        ('51', 'AIM-120D型“阿姆拉姆”先进中程空空导弹 P3I.4', '45'),
        ('3608', 'AIM-120D型“阿姆拉姆”先进中程空空导弹 P3I.4', '45'),
        ('1199', 'AAM-4B型中程空空导弹 [99型]', '60'),
        ('3567', 'AIM-260 JATM 联合先进战术导弹', '80'),
    )
    # "对所有飞机都是一枚弹" —— 针对飞机类目标把齐射数设为 1
    AIRCRAFT_TARGET_TYPES = (
        WRA_WeaponTargetType.Aircraft_Unspecified,
        WRA_WeaponTargetType.Aircraft_5th_Generation,
        WRA_WeaponTargetType.Aircraft_4th_Generation,
        WRA_WeaponTargetType.Aircraft_3rd_Generation,
        WRA_WeaponTargetType.Aircraft_Less_Capable,
        WRA_WeaponTargetType.Aircraft_High_Perf_Bombers,
        WRA_WeaponTargetType.Aircraft_Medium_Perf_Bombers,
        WRA_WeaponTargetType.Aircraft_Low_Perf_Bombers,
        WRA_WeaponTargetType.Aircraft_High_Perf_Recon_EW,
        WRA_WeaponTargetType.Aircraft_Medium_Perf_Recon_EW,
        WRA_WeaponTargetType.Aircraft_Low_Perf_Recon_EW,
        WRA_WeaponTargetType.Aircraft_AEW,
    )
    # "对所有制导武器不使用武器" —— 制导武器类目标
    GUIDED_WEAPON_TARGET_TYPES = (
        WRA_WeaponTargetType.Guided_Weapon_Unspecified,
        WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,
        WRA_WeaponTargetType.Guided_Weapon_Subsonic_Sea_Skimming,
        WRA_WeaponTargetType.Guided_Weapon_Supersonic,
        WRA_WeaponTargetType.Guided_Weapon_Subsonic,
        WRA_WeaponTargetType.Guided_Weapon_Ballistic,
    )

    # ==================================================================
    # 对海打击任务（A~E 区）
    #   执行单元 = 地面发射车；目标 = 红方登陆舰/护卫舰（按**船名**锁定情报 guid）
    #   目标写法支持三种：
    #     '蟾蜍'      -> 所有名字含"蟾蜍"的情报
    #     '蟾蜍#1'    -> 名字含"蟾蜍"且含"#1"的情报（船号）
    #     '“蟾蜍”I级坦克登陆舰 [Pr.775] #73' -> 精确名
    # ==================================================================
    STRIKE_MISSIONS = [
        # 任务名按选手要求：A船 / B船 / ...
        # 执行单元：选手指定（打光弹后再由选手手动转入 A/B/C/D 支援任务撤离）
        # A船：RT-2000 火箭炮#1#2 + 反舰导弹排#4
        {'name': 'A船',
         'units': ['RT-2000 火箭炮#1', 'RT-2000 火箭炮#2', '反舰导弹排#4'],
         'targets': []},
        {'name': 'B船',
         'units': [],
         'targets': []},
        # C船：海马斯#1#2 + 反舰导弹排#1#5
        {'name': 'C船',
         'units': ['海马斯火箭炮#1', '海马斯火箭炮#2',
                   '反舰导弹排#1', '反舰导弹排#5'],
         'targets': []},
        # D船：海马斯#3 + 反舰导弹排#2 + LUCAS 无人机发射车#1
        {'name': 'D船',
         'units': ['海马斯火箭炮#3', '反舰导弹排#2',
                   'LUCAS 无人机发射车#1'],
         'targets': []},
        # E船：海马斯#4 + 反舰导弹排#3
        {'name': 'E船',
         'units': ['海马斯火箭炮#4', '反舰导弹排#3'],
         'targets': []},
    ]

    # LUCAS 无人机发射车（用户要求：打船每船 18 发）
    #   未由用户指派到具体区域，暂加入 D 区；如需改区，调整 STRIKE_MISSIONS 即可。
    # LUCAS 无人机发射车（已改为选手手动转入 A/B/C/D 任务，故不再自动并入）

    # 北部海域打击目标（任务十六/十七 的飞机用）：按船型锁定
    NORTH_SHIP_TARGETS = ['蟾蜍', '雷鸣']

    def add_set_strike_mission(self, situation, name, point_list, unit_names,
                               targets=None, doctrine=None, mission_type=None):
        """
        创建**打击任务**并分配单元、按船名把情报加入目标列表。

        与支援任务的关键区别：打击任务**有目标列表**（target_list）。
        支援/巡逻任务没有目标列表，只靠"对海自由开火"不会主动去索敌开火
        —— 这正是"飞机到达阵位也不打船"的原因。

        :param situation: tuple, (units dict, contacts dict)
        :param name: str, 任务名
        :param point_list: list, 航线参考点（可拖动修改航线）
        :param unit_names: list, 执行单元名称
        :param targets: list, 目标写法（'蟾蜍' / '蟾蜍#1' / 精确名）
        :param doctrine: dict, 单元级条令
        :param mission_type: MissionStrikeType, 默认对海
        :return: StrikeMission 或 None
        """
        if mission_type is None:
            mission_type = MissionStrikeType.SHIP
        mission = self.create_strike_mission(name, mission_type)
        if mission is None:
            self._log('error', '创建打击任务失败：%s' % name)
            return None
        self._remember_mission(mission)
        # 分配单元
        hit_names, hit_guids = self._find_unit_guids_by_ovlp(situation, unit_names)
        missing = [n for n in unit_names if n not in hit_names]
        if missing:
            self._log('warning', '打击任务[%s]未匹配到的单元：%s' % (name, missing))
        for i in range(0, len(hit_guids), 10):
            self.assign_units_to_mission(mission_name=name, unit_list=hit_guids[i:i + 10])
        # 锁定并加入目标
        all_g, miss_t = [], []
        for t in (targets or []):
            hits, _ = self._resolve_contacts_by_spec(situation, t)
            if hits:
                all_g.extend(g for g, _ in hits)
            else:
                miss_t.append(t)
        seen, tgt = set(), []
        for g in all_g:
            if g not in seen:
                seen.add(g)
                tgt.append(g)
        if tgt:
            mission.strike_add_target(tgt)
        if miss_t:
            self._log('warning', '打击任务[%s]未锁定的目标：%s（须已探测到）' % (name, miss_t))
        # 单元级条令
        self._apply_unit_doctrine(doctrine, hit_names, name)
        self._log('info', '打击任务[%s] 已创建：执行单元 %d 个，目标 %d 个，航线点 %d 个'
                  % (name, len(hit_guids), len(tgt), len(point_list or [])))
        return mission

    # ==================================================================
    # 发射车"停下来才能打" + "打完往南跑"
    #   问题：地面发射车若处在移动状态，平台不会开火（一直机动=打不出去）。
    #   对策：
    #     ① 开局把这些发射车**按住不动**（清航路 + 速度0 + 停车 + 保持阵位），
    #        这样才开始正常接战；
    #     ② 当某车的（反舰）弹全部打光后，自动给它一条**向南**的航路并加速撤离。
    # ==================================================================
    LAUNCHER_UNIT_KEYS = ('海马斯火箭炮', '反舰导弹排',
                          'LUCAS 无人机发射车', 'RT-2000 火箭炮')
    # 发射车撤离：**没有距离限制**，位置太靠前，打完就得一直往后跑。
    # 航路给得很长（向南 10 段 x 1.0 度 = 10 度纬度 ≈ 600 海里），
    # 并且撤离期间**每个决策周期重发一次**，从结构上保证"永远有路可跑"。
    RETREAT_SOUTH_LAT_DELTA = 1.0
    RETREAT_SOUTH_STEPS = 10
    RETREAT_SPEED_KMH = 32
    # 反舰武器 DBID（平台实际装载的），用于判断"弹是否打光"
    LAUNCHER_WEAPON_IDS = ('6798', '6799', '6800', '7723',   # 海马斯
                           '3624',                            # 反舰导弹排
                           '150001',                          # LUCAS
                           '7275', '7276', '7277')            # RT-2000

    # ==================================================================
    # 霍克地空导弹连：关闭原有航线设置，保持原有阵位、关闭雷达
    # ==================================================================
    HAWK_UNIT_KEYS = ('霍克',)

    def initial_hawks(self, situation):
        """
        霍克地空导弹连#1~#4：**关闭原有航线设置**，按原有阵位不动，关闭雷达。

        做法：清空航路 + 速度归零 + 停车 + 保持阵位，并关掉雷达。
        注意这里**不改变它们的位置**（保持原有阵位）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 处理成功的单元数
        """
        ok = 0
        for name, obj in self._get_units_by_keys(situation, self.HAWK_UNIT_KEYS):
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
                try:
                    obj.doctrine_switch_radar(False)
                except Exception:
                    pass
                # 不再由防空联动去开雷达：把状态标成"已处理"
                obj._ly_hawk_fixed = True
                ok += 1
                self._log('info', '霍克[%s] 已关闭航线+保持阵位+关雷达' % name)
            except Exception as e:
                self._log('error', '霍克[%s] 设置失败: %s' % (name, e))
        self._log('info', '霍克设置完成 %d 个' % ok)
        return ok

    def initial_launchers(self, situation):
        """
        开局把所有地面发射车按住不动，让它们能正常接战。

        地面单元处于机动状态时平台不会开火，这是"目标加进列表却打不出去"的主因。
        这里清空航路、速度归零、油门停车并保持阵位。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 处理成功的单元数
        """
        ok = 0
        launchers = self._get_launcher_units(situation)
        for name, obj in launchers:
            try:
                # 先清航路，再停车，最后保持阵位
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
                # 攻击时不要忽略计划航线（否则又会边跑边打/根本不停）
                try:
                    obj.doctrine_ignore_plotted_course(
                        IgnorePlottedCourseWhenAttacking.No)
                except Exception:
                    pass
                obj._ly_hold_done = True
                # 基线 = "自由开火"：因为按住不动正是"自由开火"该有的动作。
                # 这样开局(限制开火)不会触发撤离，只有选手真的改过条令才响应。
                obj._ly_wcs_free = True
                ok += 1
                self._log('info', '发射车[%s] 已按住不动（清航路+速度0+保持阵位）' % name)
            except Exception as e:
                self._log('error', '发射车[%s] 停止失败: %s' % (name, e))
        self._log('info', '发射车静止化完成 %d 个' % ok)
        return ok

    def _get_launcher_units(self, situation):
        """收集所有地面发射车单元对象。"""
        units = situation[0] if isinstance(situation[0], dict) else {}
        out = []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            name = str(u.get('name', ''))
            if not any(k in name for k in self.LAUNCHER_UNIT_KEYS):
                continue
            obj = self.get_unit(u.get('guid', guid))
            if obj is not None:
                out.append((name, obj))
        return out

    def _launcher_ammo_left(self, unit):
        """
        统计该发射车剩余的（反舰）弹药总数。

        :param unit: Unit, 单元对象
        :return: (int, dict), 剩余总数、{武器ID: 数量}
        """
        detail = {}
        for key in ('Mounts', 'Magazines', 'Loadouts'):
            c = getattr(unit, key, None)
            if not isinstance(c, dict):
                continue
            for _, item in c.items():
                if not isinstance(item, dict):
                    continue
                for _, w in (item.get('WeaponRecs') or {}).items():
                    if not isinstance(w, dict):
                        continue
                    wid = w.get('WeaponDBID')
                    if wid is None:
                        continue
                    wid = str(int(wid))
                    cnt = w.get('CurrentLoad', w.get('DefaultLoad', 0)) or 0
                    detail[wid] = max(detail.get(wid, 0), int(cnt))
        total = sum(c for w, c in detail.items() if w in self.LAUNCHER_WEAPON_IDS)
        return total, detail

    def launcher_retreat_south(self, situation):
        """
        逐周期检查：发射车把（反舰）弹**全部打光**后，自动给一条**向南**航路并加速撤离。

        这是"打完就跑"（shoot and scoot）的自动化：开火前保持静止以正常接战，
        弹全部耗尽后才撤离，既避免被反炮兵又不影响射击。

        关键安全设计（避免"开局就逃跑"）：
          只有在**开局确实带过弹**、且现在**已归零**时才触发撤离。
          若一直读不到弹（态势里挂载字段缺失等），视为"未知"，
          绝不撤离 —— 否则会被误判成已打光而开局就跑。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本周期新触发撤离的单元数
        """
        fired = 0
        for name, obj in self._get_launcher_units(situation):
            if getattr(obj, '_ly_retreat_done', False):
                continue
            total, detail = self._launcher_ammo_left(obj)
            peak = getattr(obj, '_ly_ammo_peak', None)
            if peak is None:
                # 第一周期：记录弹药基线；基线为 0 表示没读到弹 -> 标记"未知"
                obj._ly_ammo_peak = total
                obj._ly_ammo_known = total > 0
                continue
            if total > peak:
                obj._ly_ammo_peak = total
                obj._ly_ammo_known = True
            if not getattr(obj, '_ly_ammo_known', False):
                # 从未确认带过弹 -> 不撤离
                continue
            if total > 0:
                continue
            # 弹已全部打光 -> 往南撤离
            try:
                lat = float(getattr(obj, 'Lat', 0.0) or 0.0)
                lon = float(getattr(obj, 'Lon', 0.0) or 0.0)
                south = [(lat - self.RETREAT_SOUTH_LAT_DELTA, lon),
                         (lat - self.RETREAT_SOUTH_LAT_DELTA * 2.0, lon)]
                try:
                    obj.hold_positon(False)
                except Exception:
                    pass
                obj.plotted_course(south)
                try:
                    obj.set_desired_speed(self.RETREAT_SPEED_KMH)
                except Exception:
                    pass
                try:
                    obj.set_throttle(Throttle.Full)
                except Exception:
                    pass
                obj._ly_retreat_done = True
                fired += 1
                self._log('info', '发射车[%s] 弹药已全部打光(基线%d->现0) 开始向南撤离 %s 速度%d'
                          % (name, peak, south, self.RETREAT_SPEED_KMH))
            except Exception as e:
                self._log('error', '发射车[%s] 撤离指令失败: %s' % (name, e))
        return fired

    # 打击任务对水面目标使用的武器数目（按发射单元类型指定）
    #   key   = 单元名关键字
    #   value = (齐射数, 该型单元平台实际装载的武器DBID)
    #   ⚠️ 选手要求：**所有发射车统一每船 4 发**（改了这一处就够，
    #      LAUNCHER_SALVO_BY_UNIT 会自动跟随，避免两张表打架）。
    #   注：这里的武器ID是**平台实际装载的ID**（在 model.db 中多无元数据），
    #       只有用它们下发 WRA 才不会报"找不到武器"。
    STRIKE_WRA_BY_UNIT = {
        # 海马斯实际只带 M30A2 超射程精确制导武器（3136）
        '海马斯火箭炮':   ('4',  ('3136',)),
        # 反舰导弹排实际带 雄风二型反舰导弹（1934，四联装）
        '反舰导弹排':     ('4',  ('1934',)),
        'LUCAS 无人机发射车': ('4', ('150001',)),
        'RT-2000 火箭炮': ('4', ('7275', '7276', '7277')),
    }

    # 用于"按船型全选"和诊断的目标名关键字
    TARGET_KEYWORDS = ('蟾蜍', '雷鸣', '登陆舰', '护卫舰')

    # ==================================================================
    # 北打船（16/17）：WRA 按**船型**区分，打登陆舰、不打驱逐舰
    #
    #   背景：飞机"舍近求远"去打驱逐舰。WRA 的目标类型是按**舰种+吨位**
    #   分类的（见 WRA_WeaponTargetType），因此可以精确控制：
    #     Ship_Amphibious_*        -> 两栖/登陆舰（蟾蜍）  -> 满齐射
    #     Ship_Surface_Combatant_* -> 水面战斗舰（驱逐舰）-> 不使用武器(0)
    #
    #   注意：必须把通用的
    #     Surface_Contact_Unknown_Type(2999) / Ship_Unspecified(3000)
    #   也设为 0，否则 AI 会把驱逐舰归入"未指定"而照打不误。
    #   只有把通用项关掉、只放行两栖项，才能真正做到"只打登陆舰"。
    # ==================================================================
    # 两栖/登陆舰（含蟾蜍 Pr.775 约 4000 吨 -> 3203；其余吨位一并放行）
    STRIKE_AMPHIB_TYPES = (
        WRA_WeaponTargetType.Ship_Amphibious_0_500_tons,
        WRA_WeaponTargetType.Ship_Amphibious_501_1500_tons,
        WRA_WeaponTargetType.Ship_Amphibious_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_25001_45000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_45001_95000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_95000_tons,
    )
    # 水面战斗舰（驱逐舰/护卫舰）
    STRIKE_COMBATANT_TYPES = (
        WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons,
    )

    def _north_ship_wra(self, unit):
        """
        为北打船的飞机生成"只打两栖舰、不打水面战斗舰"的 WRA 规则。

        只作用于该单元**实际携带**的反舰武器，避免给不存在的武器下发
        （那会报"找不到武器"并连累整批指令）。

        :param unit: Unit, 单元对象
        :return: list, [[weaponID, target_type, qty, range], ...]
        """
        wids, _diag = self._unit_anti_ship_weapons(unit)
        rules = []
        for wid in sorted(set(int(w) for w in wids)):
            # 通用水面项关闭（否则驱逐舰会被归入"未指定"照打）
            for t in (WRA_WeaponTargetType.Surface_Contact_Unknown_Type,
                      WRA_WeaponTargetType.Ship_Unspecified):
                rules.append([wid, t, '0', 'Max'])
            # 水面战斗舰（驱逐舰/护卫舰）关闭
            for t in self.STRIKE_COMBATANT_TYPES:
                rules.append([wid, t, '0', 'Max'])
            # 两栖/登陆舰放行（满齐射）
            for t in self.STRIKE_AMPHIB_TYPES:
                rules.append([wid, t, 'Max', 'Max'])
        return rules

    # ==================================================================
    # 任务通用条令（平台任务条令不继承推演方总条令，必须逐任务下发）
    # ==================================================================
    @staticmethod
    def _mission_common_doctrine():
        """返回 19 个任务统一要下发的任务级条令字典。"""
        return {
            'weapon_state_rtb': WeaponStateRTB.No,                  # 武器状态-返航：否
            'fuel_state_rtb': FuelStateRTB.No,                      # 燃油状态-返航：否
            'weapon_state_planned': WeaponStatePlanned.WinchesterUseAirGuns,  # 耗光用航炮
            'doctrine_refuel': ERefuel.No,                          # 加油/补给：不允许
            'ignore_emcon_under_attack': IgnoreEMCONUnderAttack.No,  # 受攻击忽略电磁管控：否
            'ignore_plotted_course': IgnorePlottedCourseWhenAttacking.No,  # 攻击忽略计划航线：否
        }

    # 水面目标类型：精简为 12 类"覆盖面最广"的，避免指令量过大被平台丢弃。
    #   未知类型(2999) + 船-未指定(3000) 这两条最关键：
    #     接触点未识别时查 2999，已识别是舰船但不知型号时查 3000。
    #   再补上航母/水面战斗舰/两栖舰/辅助舰/商船的"未分级"档位。
    #   如需全量 34 类（覆盖每个吨位细分），把 USE_ALL_SURFACE_TARGETS 改成 True。
    SURFACE_TARGET_TYPES_CORE = (
        WRA_WeaponTargetType.Surface_Contact_Unknown_Type,        # 2999 未知类型 ★
        WRA_WeaponTargetType.Ship_Unspecified,                    # 3000 船-未指定 ★
        WRA_WeaponTargetType.Ship_Carrier_0_25000_tons,           # 3001 航母
        WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons,   # 3101 战斗舰（雷鸣级在此档）
        WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons,  # 3103
        WRA_WeaponTargetType.Ship_Amphibious_1501_5000_tons,      # 3203 两栖舰（蟾蜍级在此档）★
        WRA_WeaponTargetType.Ship_Amphibious_5001_10000_tons,     # 3204
        WRA_WeaponTargetType.Ship_Amphibious_10001_25000_tons,    # 3205
        WRA_WeaponTargetType.Ship_Amphibious_25001_45000_tons,    # 3206
        WRA_WeaponTargetType.Ship_Auxiliary_1501_5000_tons,       # 3303
        WRA_WeaponTargetType.Ship_Merchant_Civilian_1501_5000_tons,  # 3403
        WRA_WeaponTargetType.Submarine_Surfaced,                  # 3501 潜艇上浮
    )
    USE_ALL_SURFACE_TARGETS = False   # True = 用全量 34 类（指令量约 3 倍）

    # ==================================================================
    # 反舰饱和打击：所有"水面舰艇"类目标类型
    #   说明：WRA 的目标类型分两层 ——
    #     • 未知类型：接触点还没识别出舰种时用 Surface_Contact_Unknown_Type(2999)
    #     • 未指定  ：已识别是舰船但不知型号时用 Ship_Unspecified(3000)
    #     • 具体类型：识别出吨位/舰种后按 3101~3408 细分
    #   三层必须全设，否则"只设了具体舰种、接触点却还是未知"就会落回继承值而不打。
    # ==================================================================
    SURFACE_TARGET_TYPES = (
        WRA_WeaponTargetType.Surface_Contact_Unknown_Type,      # 2999 未知类型（最关键）
        WRA_WeaponTargetType.Ship_Unspecified,                  # 3000 船-未指定
        # 水面战斗舰 0~500 / … / 95000+
        WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons,
        WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons,
        # 两栖舰（蟾蜍级坦克登陆舰属此类，是加分目标）
        WRA_WeaponTargetType.Ship_Amphibious_0_500_tons,
        WRA_WeaponTargetType.Ship_Amphibious_501_1500_tons,
        WRA_WeaponTargetType.Ship_Amphibious_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_25001_45000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_45001_95000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_95000_tons,
        # 辅助舰
        WRA_WeaponTargetType.Ship_Auxiliary_0_500_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_501_1500_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_25001_45000_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_45001_95000_tons,
        WRA_WeaponTargetType.Ship_Auxiliary_95000_tons,
        # 商船/民用（红方登陆船团里可能混有）
        WRA_WeaponTargetType.Ship_Merchant_Civilian_0_500_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_501_1500_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_25001_45000_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_45001_95000_tons,
        WRA_WeaponTargetType.Ship_Merchant_Civilian_95000_tons,
    )
    # 优先打击的加分目标（蟾蜍级坦克登陆舰 = 两栖舰）
    PRIORITY_AMPHIB_TYPES = (
        WRA_WeaponTargetType.Ship_Amphibious_1501_5000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_5001_10000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_10001_25000_tons,
        WRA_WeaponTargetType.Ship_Amphibious_25001_45000_tons,
    )
    # 地面发射车（海马斯 / 雄风反舰导弹连 / 反舰导弹排 等）
    # 它们的反舰弹射程一般 ≤150 海里，把自动开火距离卡在射程内即可只打临近船团
    GROUND_LAUNCHER_MAX_FIRE_NM = '150'

    # ------------------------------------------------------------------
    # 额外/强制纳入"反舰饱和打击"的武器 DBID（可留空）
    #   正常情况靠自动识别（查 DataWeaponTargets 的 CodeID=2001 水面舰艇）就够了；
    #   若发现某型弹没被识别到，把它的 DBID 填进来即可强制纳入。
    # ------------------------------------------------------------------
    EXTRA_ANTI_SHIP_WEAPONS = (
        # 例：'1133',   # 雄风三型反舰导弹
        # 例：'722',    # ASM-3 型反舰导弹
    )
    # 需要强制纳入反舰饱和打击的单元名（同样可留空）
    EXTRA_ANTI_SHIP_UNITS = (
        # 例：'海马斯火箭炮 #1',
    )

    def __init__(self, side_name, params):
        RuleAgentBase.__init__(self, side_name)
        logging.info('%s:%s play game' % (side_name, self.__class__.__name__))
        # 战斧打击机场是否已执行（开局立刻执行一次）
        self._tomahawk_fired = False

    # ==================================================================
    # 日志（重要：不要直接用 self.log！）
    # ==================================================================
    def _log(self, level, msg):
        """
        安全日志接口。

        平台 entitys/player.py 中 self.log = None，且全工程再无赋值处，
        因此 self.log.info(...) 必定抛 AttributeError: 'NoneType' object has
        no attribute 'info'，会导致 initial() 第一步就崩、智能体"导入后不执行"。
        此处统一回退到标准库 logging，与官方样例 agent 的写法保持一致。

        :param level: str, 'info' / 'warning' / 'error'
        :param msg: str, 日志内容
        :return: None
        """
        logger = getattr(self, 'log', None)
        func = getattr(logger, level, None) if logger is not None else None
        if callable(func):
            func(msg)
        else:
            getattr(logging, level, logging.info)('%s:%s %s'
                                                  % (self.Name, self.__class__.__name__, msg))

    # ==================================================================
    # 指令配额（关键！）
    #   平台启动参数里带 agentOrderCountLimit = 500，即每个决策周期下发给
    #   推演引擎的指令条数上限，超出的会被丢弃。
    #   initial() 里若不加控制地下发数千条 WRA，绝大多数会被丢掉，
    #   表现就是"设了自由开火却完全不开火"。
    # ==================================================================
    def _cmd_budget(self):
        """本周期可用于 WRA 的指令条数（留出份额给任务创建/分配单元等）。"""
        limit = getattr(self, '_order_count_limit', 0) or 500
        return max(40, int(limit * 0.5))      # 只用 50%，避免挤掉其他指令

    # ==================================================================
    # 第一步：修改总条令
    # ==================================================================
    def set_rules(self, rule):
        """
        设置总条令。

        入参 rule 为字典，key 与下方各项一一对应，可在 initial() 前按需覆写，
        以支持后续"根据态势动态调整条令"。

        :param rule: dict, 条令项字典
        :return: None
        """
        # ------------------------------------------------------------------
        # 一、交战规则：限制开火（仅限手动开火）
        # ------------------------------------------------------------------
        # 对空武器状态：限制开火（仅限于手动开火）
        self.doctrine_weapon_control_status_air(rule['weapon_control_status_air'])
        # 对海（水面）武器状态：限制开火（仅限于手动开火）
        self.doctrine_weapon_control_status_surface(rule['weapon_control_status_surface'])
        # 对潜（水下）武器状态：限制开火（仅限于手动开火）
        self.doctrine_weapon_control_status_subsurface(rule['weapon_control_status_subsurface'])
        # 对地武器状态：限制开火（仅限于手动开火）
        self.doctrine_weapon_control_status_land(rule['weapon_control_status_land'])
        # 攻击时忽略计划航线：否
        self.doctrine_ignore_plotted_course(rule['ignore_plotted_course'])

        # ------------------------------------------------------------------
        # 二、电磁管控
        # ------------------------------------------------------------------
        # 被攻击时忽略电磁管控：否
        self.doctrine_ignore_emcon_under_attack(rule['ignore_emcon_under_attack'])
        # 干扰机（电子干扰传感器）：打开
        self.doctrine_switch_oecm(rule['switch_oecm'])
        # 声呐：打开
        self.doctrine_switch_sonar(rule['switch_sonar'])

        # ------------------------------------------------------------------
        # 三、返航规则：燃油 / 武器耗尽后不自动返航
        # ------------------------------------------------------------------
        # 燃油状态-返航：否（到达燃油状态不返回基地）
        self.doctrine_fuel_state_rtb(rule['fuel_state_rtb'])
        # 武器状态-预先规划：任务武器耗光，允许使用航炮（推荐）
        self.doctrine_weapon_state_planned(rule['weapon_state_planned'])
        # 武器状态-返航：否（到达武器状态不返回基地）
        self.doctrine_weapon_state_rtb(rule['weapon_state_rtb'])
        # 加油/补给：全局不允许（平台实体接口名为 doctrine_refuel）
        if 'doctrine_refuel' in rule:
            self.doctrine_refuel(rule['doctrine_refuel'])

    def _dump_weapon_mounts(self, situation, keywords=('邦克山',)):
        """
        一次性诊断：把指定单元的**真实挂载结构**完整打进日志。

        目的：BOL 下发时 mount/weapon 必须与平台内部完全一致，
              否则平台会回"指令执行成功"但弹其实没出筒。
              这里把三套接口的输出都打出来做对照：
                1) unit.Mounts 原始结构（挂架 key -> Component.DBID/Name -> WeaponRecs）
                2) unit.weapon2mount()（引擎官方：武器 -> 挂架列表）
                3) unit.get_weapon_infos()（引擎官方：只读 Mounts）
        """
        try:
            units = situation[0] if isinstance(situation[0], dict) else {}
            for guid, u in units.items():
                if not isinstance(u, dict):
                    continue
                nm = str(u.get('name', ''))
                if not any(k in nm for k in keywords):
                    continue
                obj = self.get_unit(u.get('guid', guid))
                if obj is None:
                    continue
                self._log('info', '=== 挂载诊断[%s] ===' % nm)
                # 1) 原始 Mounts / Magazines / Loadouts
                for attr in ('Mounts', 'Magazines', 'Loadouts'):
                    cont = getattr(obj, attr, None)
                    if not isinstance(cont, dict):
                        self._log('info', '  %s: 非字典(%s)' % (attr, type(cont).__name__))
                        continue
                    self._log('info', '  %s: %d 个挂架' % (attr, len(cont)))
                    for mk, mv in cont.items():
                        if not isinstance(mv, dict):
                            continue
                        comp = mv.get('Component') or {}
                        wrs = mv.get('WeaponRecs') or {}
                        ws = []
                        if isinstance(wrs, dict):
                            for _rk, wv in wrs.items():
                                if isinstance(wv, dict):
                                    ws.append('%s(x%s)' % (wv.get('WeaponDBID'),
                                                           wv.get('CurrentLoad')))
                        self._log('info', '    [%s] key=%s DBID=%s Name=%s 武器=%s'
                                  % (attr, mk, comp.get('DBID'), comp.get('Name'), ws))
                # 2) 官方接口
                for fn_name in ('weapon2mount', 'get_weapon_infos', 'get_weapon_info'):
                    fn = getattr(obj, fn_name, None)
                    if not callable(fn):
                        continue
                    try:
                        self._log('info', '  %s() -> %s' % (fn_name, fn()))
                    except Exception as e:
                        self._log('warning', '  %s() 失败: %s' % (fn_name, e))
                self._log('info', '=== 挂载诊断结束[%s] ===' % nm)
        except Exception as e:
            self._log('error', '挂载诊断异常: %s' % e)


    # ==================================================================
    # 总条令：防空导弹的武器使用规则（**side 级，只下发一次**）
    #
    #   按要求只改这 4 型弹，其余项目平台会自动跟随，不需要逐项下发。
    #   格式：(武器DBID, 名称, 需要"不使用武器"的目标类型, {目标类型: 自动开火距离(海里)})
    #
    #   目标类型对照：
    #     空中感知-未知类型            = Air_Contact_Unknown_Type          1999
    #     飞机-未指定                  = Aircraft_Unspecified              2000
    #     飞机-第5代战斗机             = Aircraft_5th_Generation           2001
    #     飞机-第四代战斗机            = Aircraft_4th_Generation           2002
    #     制导武器-未指定              = Guided_Weapon_Unspecified         2200
    #     制导武器-超音速掠海          = Guided_Weapon_Supersonic_Sea_Skimming 2201
    #     制导武器-超音速              = Guided_Weapon_Supersonic         2203
    #     制导武器-弹道导弹            = Guided_Weapon_Ballistic          2211
    # ==================================================================
    SIDE_SAM_WRA = (
        # ③ 天弓1防空导弹(891)
        (('891',), '天弓1防空导弹',
         (WRA_WeaponTargetType.Air_Contact_Unknown_Type,
          WRA_WeaponTargetType.Guided_Weapon_Unspecified),
         {WRA_WeaponTargetType.Aircraft_Unspecified: '20'}),
        # ④ 天弓2防空导弹(890)
        (('890',), '天弓2防空导弹',
         (WRA_WeaponTargetType.Air_Contact_Unknown_Type,
          WRA_WeaponTargetType.Guided_Weapon_Unspecified,
          WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,
          WRA_WeaponTargetType.Guided_Weapon_Supersonic),
         {WRA_WeaponTargetType.Aircraft_Unspecified: '45',
          WRA_WeaponTargetType.Aircraft_5th_Generation: '45',
          WRA_WeaponTargetType.Aircraft_4th_Generation: '45'}),
        # ⑤ MIM-104E 爱国者-2（同名的几个 DBID 一并覆盖）
        (('642', '3610', '50004'), 'MIM-104E型“爱国者-2”防空导弹',
         (WRA_WeaponTargetType.Air_Contact_Unknown_Type,
          WRA_WeaponTargetType.Guided_Weapon_Unspecified,
          WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,
          WRA_WeaponTargetType.Guided_Weapon_Supersonic,
          WRA_WeaponTargetType.Guided_Weapon_Ballistic),
         {WRA_WeaponTargetType.Aircraft_Unspecified: '40',
          WRA_WeaponTargetType.Aircraft_5th_Generation: '40',
          WRA_WeaponTargetType.Aircraft_4th_Generation: '40'}),
        # ⑥ MIM-104F 爱国者-3（同名的几个 DBID 一并覆盖）
        (('1150', '3207', '50003'), 'MIM-104F型“爱国者-3”防空导弹',
         (WRA_WeaponTargetType.Air_Contact_Unknown_Type,
          WRA_WeaponTargetType.Guided_Weapon_Unspecified,
          WRA_WeaponTargetType.Guided_Weapon_Supersonic_Sea_Skimming,
          WRA_WeaponTargetType.Guided_Weapon_Supersonic,
          WRA_WeaponTargetType.Guided_Weapon_Ballistic),
         {WRA_WeaponTargetType.Aircraft_Unspecified: '30',
          WRA_WeaponTargetType.Aircraft_5th_Generation: '30',
          WRA_WeaponTargetType.Aircraft_4th_Generation: '30'}),
    )

    def set_side_sam_wra(self):
        """
        总条令（side 级）里 4 型防空导弹的武器使用规则。

        **只在 initial() 里调用一次**（WRA 是永久生效的，不需要重发）。

        :return: int, 下发条数
        """
        n = 0
        for wids, label, no_use, ranges in self.SIDE_SAM_WRA:
            for wid in wids:
                # "对这种目标不使用武器" = 齐射数 0
                for t in no_use:
                    self.wra_qty_salvo(wid, t, '0')
                    n += 1
                # 自动开火距离（海里）
                for t, rng in ranges.items():
                    self.wra_firing_range(wid, t, rng)
                    n += 1
            self._log('info', '总条令防空弹 WRA 已设[%s]：%d 型武器，'
                              '不使用武器 %d 项，开火距离 %d 项'
                      % (label, len(wids), len(no_use), len(ranges)))
        self._log('info', '总条令防空弹 WRA 共下发 %d 条' % n)
        return n

    def set_side_air_wra(self):
        """
        总条令（side 级）中距空空弹 WRA。

        选手要求：只改总条令、只改 3 型弹对 2 类飞机目标，各设 1 枚。
          AIM-120C-7 (718) / AIM-120D (51, 3608) / AIM-260 JATM (3567)
          飞机-第5代战斗机 (2001) / 飞机-第四代战斗机 (2002)

        关键：调用的是 **self.wra_qty_salvo**（Agent 继承自 Player，即 side 级），
        不是逐单元/逐任务下发。设完后下级自动继承，指令量仅 8 条。
        """
        wids = ('718', '51', '3608', '3567')
        targets = (
            WRA_WeaponTargetType.Aircraft_5th_Generation,   # 2001 第五代
            WRA_WeaponTargetType.Aircraft_4th_Generation,   # 2002 第四代
        )
        n = 0
        for wid in wids:
            for t in targets:
                self.wra_qty_salvo(wid, t, '1')
                n += 1
        self._log('info', '总条令中距弹 WRA 已设：%d 型弹 × 2 类飞机目标 = %d 条'
                  % (len(wids), n))
        return n

    # ==================================================================
    # 创建支援任务的通用封装
    # ==================================================================
    def _find_unit_guids_by_ovlp(self, situation, unit_names):
        """
        按单元名称匹配单元 guid（内部工具函数）。

        采用三级匹配，从严到宽，避免"名称相似就误命中"导致把不属于本任务的
        单元也分配进任务：
            1) 完全相同；
            2) 去掉全/半角空格后相同；
            3) 去掉空格后互为子串（仅当第 1、2 级一个都没命中时才启用）。
        每个待匹配名称最多命中一个单元。

        :param situation: tuple, (units dict, contacts dict)
        :param unit_names: list, 待匹配的单元名称列表
        :return: (list, list), 命中的单元名列表、对应的 guid 列表
        """
        def _bare(text):
            return str(text).replace(' ', '').replace('\u3000', '')

        units = situation[0] if isinstance(situation[0], dict) else {}
        candidates = []
        for guid, unit in units.items():
            if not isinstance(unit, dict):
                continue
            name = str(unit.get('name', ''))
            if name:
                candidates.append((guid, name, _bare(name)))

        hit_names = []
        hit_guids = []
        matched_wanted = set()

        for level in (1, 2, 3):
            # 模糊匹配（第 3 级）仅在第 1、2 级完全落空时启用
            if level == 3 and hit_guids:
                break
            for wanted in unit_names:
                # 名称列表本身可能重复，同一名称只匹配一次
                if wanted in matched_wanted:
                    continue
                bare_wanted = _bare(wanted)
                for guid, name, bare_name in candidates:
                    if level == 1:
                        thr = (name == wanted)
                    elif level == 2:
                        thr = (bare_name == bare_wanted)
                    else:
                        thr = (bare_wanted in bare_name) or (bare_name in bare_wanted)
                    if thr:
                        hit_names.append(wanted)
                        hit_guids.append(guid)
                        matched_wanted.add(wanted)
                        break
        return hit_names, hit_guids

    def add_set_support_mission(self, situation, name, point_list, mission_rule, unit_names,
                                weapon_state_rtb=None, weapon_state_planned=None,
                                weapon_rule=None, doctrine=None, time_lab=None):
        """
        创建支援任务并分配单元（封装函数）。

        :param situation: tuple, (units dict, contacts dict)
        :param name: str, 任务名
        :param point_list: list, 阵位航线参考点 [(lat, lon), ...]，纬度在前经度在后
        :param mission_rule: dict, 任务条令字典，见下方支持的 key
        :param unit_names: list, 任务所需单元名称列表
        :param weapon_state_rtb: WeaponStateRTB, 可选，武器状态-返航
        :param weapon_state_planned: WeaponStatePlanned, 可选，武器状态-预先规划
        :param weapon_rule: list, 可选，WRA 规则 [[weaponID, target_type, qty, range], ...]
        :param doctrine: dict, 可选，单元级条令 {'air'/'surface'/'subsurface'/'land': 状态, 'radar': bool}
        :param time_lab: list, [开始时间, 结束时间]，None 表示不设置
        :return: SupportMission, 创建的任务对象；创建失败返回 None
        """
        # ---------------- 创建支援任务、设置阵位航线 ----------------
        mission = self.create_support_mission(name, point_list)
        if mission is None:
            self._log('error', '创建支援任务失败：%s' % name)
            return None
        self._remember_mission(mission)

        # ---------------- 1/3 规则 ----------------
        mission.set_one_third_rule(mission_rule['one_third_rule'])
        # ---------------- 编队规模 ----------------
        mission.support_flightSize(mission_rule['flight_size'])
        # ---------------- 飞机数低于编队规模要求不能起飞 ----------------
        mission.support_useFlightSize(mission_rule['use_flight_size'])

        # ---------------- 其余按需设置（key 存在才下发） ----------------
        if 'one_time_only' in mission_rule:
            # 任务是否仅限一次
            mission.support_oneTimeOnly(mission_rule['one_time_only'])
        if 'active_emcon' in mission_rule:
            # 是否仅在阵位上打开电磁辐射
            mission.support_activeEMCON(mission_rule['active_emcon'])
        if 'tanker_one_time' in mission_rule:
            # 一个加油周期后，加油队列为空时，加油机返回起降机场
            mission.support_tanker_one_time(mission_rule['tanker_one_time'])
        if 'loop_type' in mission_rule:
            # 导航类型：True 仅一次；False 连续循环
            mission.support_loopType(mission_rule['loop_type'])
        # ---------------- 目标分析开关 ----------------
        # 支援任务(SupportMission)没有 patrol_checkOPA/WWR，用底层 _set 下发
        # 通用任务字段：CheckOPA / CheckWWR（均为 False 表示"不勾选"）。
        for _k, _field in (('OPA', 'CheckOPA'), ('WWR', 'CheckWWR')):
            if _k in mission_rule:
                # 先试专用 setter，再退回底层 _set
                _fn = getattr(mission, 'support_check' + _k, None) or \
                      getattr(mission, 'patrol_check' + _k, None)
                if callable(_fn):
                    _fn(mission_rule[_k])
                else:
                    mission._set("%s=%s" % (_field,
                                            str(bool(mission_rule[_k])).lower()))
        if 'include_in_ato' in mission_rule:
            # 是否包含在空中任务指令中。
            # 只有 StrikeMission 有 set_includeInATO；支援/巡逻任务用底层
            # _set("IncludeInATO=...") 下发（该字段对任务通用，见 strikemission.py）。
            val = str(bool(mission_rule['include_in_ato'])).lower()
            fn = getattr(mission, 'set_includeInATO', None)
            if callable(fn):
                fn(mission_rule['include_in_ato'])
            else:
                mission._set("IncludeInATO=%s" % val)

        if 'doctrine_refuel' in mission_rule:
            # 加油/补给
            mission.doctrine_refuel(mission_rule['doctrine_refuel'])
        if 'refuel_select' in mission_rule:
            # 对所选单位进行加油/补给（注意：实体接口名为 doctrine_refuel_select，
            # 参考历史文件中的 use_refuel_unrep 在 entitys 中并不存在，属笔误）
            mission.doctrine_refuel_select(mission_rule['refuel_select'])
        if 'fuel_state_planned' in mission_rule:
            # 燃油状态-预先规划
            mission.doctrine_fuel_state_planned(mission_rule['fuel_state_planned'])
        if 'fuel_state_rtb' in mission_rule:
            # 燃油状态-返航
            mission.doctrine_fuel_state_rtb(mission_rule['fuel_state_rtb'])
        if weapon_state_planned is not None:
            # 武器状态-预先规划
            mission.doctrine_weapon_state_planned(weapon_state_planned)
        if weapon_state_rtb is not None:
            # 武器状态-返航
            mission.doctrine_weapon_state_rtb(weapon_state_rtb)

        # ---------------- 出航/阵位油门与高度 ----------------
        throttle_altitude = mission_rule.get('throttle_and_altitude')
        if throttle_altitude:
            # [出航油门, 阵位油门, 出航高度, 阵位高度]
            if throttle_altitude[0] is not None:
                mission.support_throttle_transit(throttle_altitude[0])
            if throttle_altitude[1] is not None:
                mission.support_throttle_station(throttle_altitude[1])
            if throttle_altitude[2] is not None:
                mission.support_transitAltitude(throttle_altitude[2])
            if throttle_altitude[3] is not None:
                mission.support_stationAltitude(throttle_altitude[3])

        # ---------------- 水面舰艇 / 地面机动单元 出航/阵位 油门 ----------------
        # 🔴 地面机动单元（爱国者连、海马斯、反舰导弹排、装甲车…）与水面舰艇
        #    共用这一套"舰船油门"通道（见 entitys/supportmission.py 的
        #    support_set_throttle_transit_ship / support_set_throttle_station_ship）。
        #    **不设时平台按默认低速跑**：实测地面单元只有 18.5 km/h
        #    （= 10 节 = 最大 30 节的三分之一），根本来不及跑到阵位。
        ship_ta = mission_rule.get('ship_throttle')
        if ship_ta:
            # [出航油门, 阵位油门]
            if ship_ta[0] is not None:
                mission.support_set_throttle_transit_ship(ship_ta[0])
            if ship_ta[1] is not None:
                mission.support_set_throttle_station_ship(ship_ta[1])

        # ---------------- 潜艇 出航/阵位 油门与潜深 ----------------
        # 潜艇的油门/潜深是独立通道（support_set_throttle_*_submarine）。
        sub_ta = mission_rule.get('submarine_throttle_depth')
        if sub_ta:
            # [出航油门, 阵位油门, 出航潜深, 阵位潜深]
            if sub_ta[0] is not None:
                mission.support_set_throttle_transit_submarine(sub_ta[0])
            if sub_ta[1] is not None:
                mission.support_set_throttle_station_submarine(sub_ta[1])
            if sub_ta[2] is not None:
                mission.support_set_depth_transit_submarine(sub_ta[2])
            if sub_ta[3] is not None:
                mission.support_set_depth_station_submarine(sub_ta[3])

        # ---------------- 自动规避 ----------------
        if 'auto_evasion' in mission_rule:
            mission.doctrine_automatic_evasion(mission_rule['auto_evasion'])
        # 接战临机出现目标
        if 'engage_opportunity' in mission_rule:
            mission.doctrine_engage_opportunity_targets(
                mission_rule['engage_opportunity'])

        # ---------------- 武器使用规则（WRA）----------------
        # weapon_rule 可能是 list（任务级共用）或 callable（逐单元定制，
        # 由下面的 _apply_unit_doctrine 处理），callable 时此处跳过。
        for item in (weapon_rule if isinstance(weapon_rule, (list, tuple)) else []):
            wid, ttype, qty, rng = item[0], item[1], item[2], item[3]
            if qty is not None:
                mission.wra_qty_salvo(wid, ttype, qty)
            if rng is not None:
                mission.wra_firing_range(wid, ttype, rng)

        # ---------------- 分配单元 ----------------
        # 平台单次下发指令长度不超过 300 字符，单元多时需分片下发，此处按 10 个一片
        hit_names, hit_guids = self._find_unit_guids_by_ovlp(situation, unit_names)
        missing = [n for n in unit_names if n not in hit_names]
        if missing:
            self._log('warning', '支援任务[%s]未匹配到的单元：%s' % (name, missing))
        for i in range(0, len(hit_guids), 10):
            self.assign_units_to_mission(mission_name=name, unit_list=hit_guids[i:i + 10])
        self._log('info', '支援任务[%s]命中单元 %d 个 名称=%s guid=%s'
                  % (name, len(hit_guids), hit_names, hit_guids))

        # ---------------- 单元级条令 + 单元级 WRA ----------------
        self._apply_unit_doctrine(doctrine, hit_names, name, unit_weapon_rule=weapon_rule)

        # ---------------- 任务起止时间 ----------------
        if time_lab:
            if time_lab[0] is not None:
                mission.set_start(time_lab[0])
            if time_lab[1] is not None:
                mission.set_end(time_lab[1])
        return mission

    # ==================================================================
    # 巡逻任务通用封装（第四步：任务一~任务四）
    # ==================================================================
    def add_set_patrol_mission(self, situation, name, mission_type, area, unit_names,
                               rule=None, weapon_rule=None, doctrine=None, time_lab=None):
        """
        创建巡逻任务并分配单元。

        :param situation: tuple, (units dict, contacts dict)
        :param name: str, 任务名
        :param mission_type: MissionPatrolType, 巡逻任务类型（AIR/ANTI_SHIP/...）
        :param area: list, 巡逻区参考点 [(lat, lon), ...]
        :param unit_names: list, 任务所需单元名称
        :param rule: dict, 任务编辑项（按 key 存在与否下发）
        :param weapon_rule: list, WRA 规则 [[weaponID, target_type, qty, range], ...]
        :param doctrine: tuple/None, 单元级条令 (对空, 对海, 对潜) 传 bool 或 None 跳过
        :param time_lab: list, [开始, 结束]
        :return: PatrolMission, 失败返回 None
        """
        mission = self.create_patrol_mission(name, mission_type, area)
        if mission is None:
            self._log('error', '创建巡逻任务失败：%s' % name)
            return None
        self._remember_mission(mission)
        rule = rule or {}

        # 1/3 规则
        if 'one_third_rule' in rule:
            mission.set_one_third_rule(rule['one_third_rule'])
        # 编队规模 / 飞机数低于编队规模不能起飞
        if 'flight_size' in rule:
            mission.patrol_flight_size(rule['flight_size'])
        if 'use_flight_size' in rule:
            mission.patrol_useFlightSize(rule['use_flight_size'])
        # 其余按需
        for key, setter in (('OPA', mission.patrol_checkOPA),
                            ('WWR', mission.patrol_checkWWR),
                            ('active_emcon', mission.patrol_activeEMCON),
                            ('station_count', mission.station_count)):
            if key in rule:
                setter(rule[key])
        if 'ignore_plotted_course' in rule:
            mission.doctrine_ignore_plotted_course(rule['ignore_plotted_course'])
        if 'doctrine_refuel' in rule:
            mission.doctrine_refuel(rule['doctrine_refuel'])
        if 'fuel_state_planned' in rule:
            mission.doctrine_fuel_state_planned(rule['fuel_state_planned'])
        if 'fuel_state_rtb' in rule:
            mission.doctrine_fuel_state_rtb(rule['fuel_state_rtb'])
        if 'weapon_state_planned' in rule:
            mission.doctrine_weapon_state_planned(rule['weapon_state_planned'])
        if 'weapon_state_rtb' in rule:
            mission.doctrine_weapon_state_rtb(rule['weapon_state_rtb'])

        # 出航/阵位/攻击 油门与高度
        ta = rule.get('throttle_and_altitude')
        if ta:
            # [出航油门, 阵位油门, 攻击油门, 出航高度, 阵位高度, 攻击高度]
            for i, fn in enumerate((mission.patrol_set_throttle_transit,
                                    mission.patrol_set_throttle_station,
                                    mission.patrol_set_throttle_attack,
                                    mission.patrol_set_transitAltitude,
                                    mission.patrol_set_stationAltitude,
                                    mission.patrol_set_attackAltitude)):
                if i < len(ta) and ta[i] is not None:
                    fn(ta[i])

        # ---------------- 水面舰艇 出航/阵位/攻击 油门 ----------------
        # 巡逻任务的"飞机油门"与"水面舰艇油门"是两套独立设置
        # （patrol_set_throttle_* 是飞机；set_*ThrottleShip 才是水面舰艇）。
        # 故水面舰巡逻任务必须走 ship_throttle 这个 key。
        st = rule.get('ship_throttle')
        if st:
            # [出航油门, 阵位油门, 攻击油门]
            for i, fn in enumerate((mission.set_transitThrottleShip,
                                    mission.set_stationThrottleShip,
                                    mission.set_attackThrottleShip)):
                if i < len(st) and st[i] is not None:
                    fn(st[i])

        # ---------------- 潜艇 出航/阵位/攻击 油门与潜深 ----------------
        # 与"飞机油门""水面舰艇油门"一样，潜艇是**第三套独立通道**
        # （patrolmission.py 的 set_*ThrottleSubmarine / set_*DepthSubmarine）。
        # 潜深传**负值**（海拔高度，-180 表示水下 180 米）。
        sd = rule.get('submarine_throttle_depth')
        if sd:
            # [出航油门, 阵位油门, 攻击油门, 出航潜深, 阵位潜深, 攻击潜深]
            for i, fn in enumerate((mission.set_transitThrottleSubmarine,
                                    mission.set_stationThrottleSubmarine,
                                    mission.set_attackThrottleSubmarine,
                                    mission.set_transitDepthSubmarine,
                                    mission.set_stationDepthSubmarine,
                                    mission.set_attackDepthSubmarine)):
                if i < len(sd) and sd[i] is not None:
                    fn(sd[i])

        # 武器使用规则
        for item in (weapon_rule or []):
            wid, ttype, qty, rng = item[0], item[1], item[2], item[3]
            if qty is not None:
                mission.wra_qty_salvo(wid, ttype, qty)
            if rng is not None:
                mission.wra_firing_range(wid, ttype, rng)

        # 分配单元
        hit_names, hit_guids = self._find_unit_guids_by_ovlp(situation, unit_names)
        missing = [n for n in unit_names if n not in hit_names]
        if missing:
            self._log('warning', '巡逻任务[%s]未匹配到的单元：%s' % (name, missing))
        for i in range(0, len(hit_guids), 10):
            self.assign_units_to_mission(mission_name=name, unit_list=hit_guids[i:i + 10])

        # 单元级条令（对空/对海/对潜自由开火 + 雷达开 + 单元级 WRA）
        self._apply_unit_doctrine(doctrine, hit_names, name, unit_weapon_rule=weapon_rule)

        if time_lab:
            if time_lab[0] is not None:
                mission.set_start(time_lab[0])
            if time_lab[1] is not None:
                mission.set_end(time_lab[1])
        self._log('info', '巡逻任务[%s] 已创建，分配单元 %d 个：%s'
                  % (name, len(hit_guids), hit_names))
        return mission

    def _apply_unit_doctrine(self, doctrine, unit_names, tag, unit_weapon_rule=None):
        """
        给参与任务的单元批量设置条令（自由开火 / 雷达开关 / 单元级 WRA）。

        :param doctrine: dict 或 None, 可含 key:
                         'air' / 'surface' / 'subsurface' / 'land' -> WeaponControlStatus
                         'radar' -> bool
        :param unit_names: list, 单元名
        :param tag: str, 日志用任务名
        :param unit_weapon_rule: list 或 callable 或 None
                                 · list: 所有单元共用同一套 WRA
                                   [[weaponID, target_type, qty, range], ...]
                                 · callable: 逐单元计算，签名 f(unit) -> 同上 list
                                   （用于"只打某类船"这种按单元携带武器而定制的规则）
        :return: None
        """
        if (not doctrine and not unit_weapon_rule) or not unit_names:
            return
        found = self._find_units_by_exact_name(unit_names)
        for name, unit in found:
            try:
                # 逐单元计算 WRA（callable 形式）
                rules = unit_weapon_rule
                if callable(rules):
                    try:
                        rules = rules(unit)
                    except Exception as e:
                        self._log('error', '[%s] 单元[%s]生成 WRA 失败: %s' % (tag, name, e))
                        rules = None
                doctrine = doctrine or {}
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
                if doctrine.get('engage_opportunity') is not None:
                    unit.doctrine_engage_opportunity_targets(
                        doctrine['engage_opportunity'])
                # 单元级武器使用规则（Unit 继承 DoctrineOperator，支持 WRA）
                for item in (rules or []):
                    wid, ttype, qty, rng = item[0], item[1], item[2], item[3]
                    if qty is not None:
                        unit.wra_qty_salvo(wid, ttype, qty)
                    if rng is not None:
                        unit.wra_firing_range(wid, ttype, rng)
            except Exception as e:
                self._log('error', '[%s] 单元[%s]设置条令失败: %s' % (tag, name, e))
        self._log('info', '[%s] 单元条令已设置 %d 个：%s' % (tag, len(found), [n for n, _ in found]))

    # ==================================================================
    # 第二步：战斧打击机场（BOL 纯方位打击 + 导弹航迹规划）
    # ==================================================================
    def _get_units_by_keywords(self, situation, keywords):
        """
        按名称关键字（子串）找出本方单元对象，宽松匹配（忽略全/半角空格与大小写）。

        同时查两处，避免漏掉只出现在其中一处、或名字与想定不一致的单元：
          1) self.units_of_name / self.ships / self.submarines 等本方单元集合；
          2) situation[0] 里按 name 关键字命中的单元。

        :param situation: tuple, (units dict, contacts dict)
        :param keywords: list, 名称关键字列表，任意命中即算
        :return: list, [(单元名, 单元对象)]
        """
        def _bare(t):
            return str(t).replace(' ', '').replace('\u3000', '').lower()

        bare_keys = [_bare(k) for k in keywords]
        hits = []
        seen = set()

        def _add(obj):
            if obj is None:
                return
            guid = getattr(obj, 'ID', None) or id(obj)
            if guid in seen:
                return
            name = str(getattr(obj, 'Name', '') or '')
            if name and any(k in _bare(name) for k in bare_keys):
                seen.add(guid)
                hits.append((name, obj))

        # 1) 本方单元集合
        index = getattr(self, 'units_of_name', None)
        if isinstance(index, dict):
            for _, obj in index.items():
                _add(obj)
        for attr in ('ships', 'submarines', 'aircrafts', 'satellites', 'facilitys', 'weapons'):
            coll = getattr(self, attr, None)
            if isinstance(coll, dict):
                for obj in coll.values():
                    _add(obj)

        # 2) 态势里的单元（用态势中的 guid 取对象）
        units = situation[0] if isinstance(situation[0], dict) else {}
        for guid, unit in units.items():
            if not isinstance(unit, dict):
                continue
            if any(k in _bare(unit.get('name', '')) for k in bare_keys):
                _add(self.get_unit(unit.get('guid', guid)))
        return hits

    def _find_units_by_exact_name(self, names):
        """
        按精确名称取本方单元对象，优先用 units_of_name 索引。

        :param names: list, 精确单元名列表
        :return: list, [(单元名, 单元对象)]
        """
        def _bare(t):
            return str(t).replace(' ', '').replace('\u3000', '').lower()

        found = []
        index = {}
        units_of_name = getattr(self, 'units_of_name', None)
        if isinstance(units_of_name, dict):
            for nm, obj in units_of_name.items():
                index[_bare(nm)] = (nm, obj)
        for want in names:
            hit = index.get(_bare(want))
            if hit is not None:
                found.append(hit)
        if len(found) < len(names):
            # 退路：从本方各单元集合里逐类找
            pool = []
            for attr in ('ships', 'submarines', 'aircrafts', 'facilitys', 'groups'):
                coll = getattr(self, attr, None)
                if isinstance(coll, dict):
                    pool.extend(coll.values())
            for want in names:
                if any(_bare(want) == _bare(n) for n, _ in found):
                    continue
                for obj in pool:
                    if _bare(getattr(obj, 'Name', '')) == _bare(want):
                        found.append((getattr(obj, 'Name', want), obj))
                        break
        return found

    def _weapon_name(self, weapon_id):
        """
        通过武器 DBID 取型号名称（读 entitys/data/model.db）。

        :param weapon_id: int, 武器 DBID
        :return: str, 武器名称；查不到返回 ''
        """
        try:
            from engine.LingYi.entitys.data import query_data
            return query_data.get_weapon_name(int(weapon_id)) or ''
        except Exception as e:
            self._log('warning', '查询武器名称失败 weapon_id=%s : %s' % (weapon_id, e))
            return ''

    def _unit_weapon_list(self, unit):
        """
        取单元当前可用的武器清单，返回 [(名称, 武器DBID, 数量)]，按武器DBID合并取最大。

        必须同时看三处，缺一处就会漏弹（实战已踩）：
          1) Mounts   —— 已装到挂架上的弹；
          2) Magazines—— 弹药库/垂发库里的弹。战斧主要在这里，而
                         Ship.get_weapon_infos() 只读 Mounts，所以单靠它看不到战斧；
          3) Loadouts —— 挂载方案（飞机用），记录可能没有 CurrentLoad。

        另外仍会调平台的 get_weapon_infos()/get_weapon_info() 作为兜底口径。

        :param unit: Unit, 单元对象
        :return: list, [(name, weapon_id, count)]
        """
        acc = {}   # weapon_id -> [name, count]

        def _add(wid, cnt, name=''):
            try:
                wid = int(wid)
                cnt = int(cnt or 0)
            except (TypeError, ValueError):
                return
            if cnt <= 0:
                return
            if wid in acc:
                acc[wid][1] = max(acc[wid][1], cnt)
                if not acc[wid][0] and name:
                    acc[wid][0] = name
            else:
                acc[wid] = [str(name or ''), cnt]

        # ---- 1) 直接扫 Mounts / Magazines / Loadouts ----
        for key in ('Mounts', 'Magazines', 'Loadouts'):
            container = getattr(unit, key, None)
            if not isinstance(container, dict):
                continue
            for _, item in container.items():
                if not isinstance(item, dict):
                    continue
                recs = item.get('WeaponRecs')
                if not isinstance(recs, dict):
                    continue
                for _, w in recs.items():
                    if not isinstance(w, dict):
                        continue
                    wid = w.get('WeaponDBID')
                    if wid is None:
                        continue
                    cnt = w.get('CurrentLoad')
                    if cnt is None:
                        cnt = w.get('DefaultLoad', 0)
                    _add(wid, cnt, w.get('Name', ''))

        # ---- 2) 平台接口兜底 ----
        fn = getattr(unit, 'get_weapon_infos', None)
        if callable(fn):
            try:
                for item in (fn() or []):
                    if isinstance(item, (list, tuple)) and len(item) >= 3:
                        _add(item[1], item[2], item[0])
            except Exception as e:
                self._log('warning', 'get_weapon_infos 失败: %s' % e)
        fn = getattr(unit, 'get_weapon_info', None)
        if callable(fn):
            try:
                d = fn() or {}
                if isinstance(d, dict):
                    for w, c in d.items():
                        _add(w, c, self._weapon_name(w))
            except Exception as e:
                self._log('warning', 'get_weapon_info 失败: %s' % e)

        out = []
        for wid, (nm, cnt) in acc.items():
            out.append((nm or self._weapon_name(wid), wid, cnt))
        return out

    def _find_tomahawk_on_unit(self, unit, name_keywords=None):
        """
        找出单元上所有可发射的"战斧"导弹，返回可用发射方案。

        实现要点（踩过的坑）：
          1. 武器枚举必须同时扫 Mounts / Magazines / Loadouts（见 _unit_weapon_list）。
             战斧主要在 Magazines 里，而 Ship.get_weapon_infos() 只读 Mounts，
             单靠平台接口会看不到战斧 → 整批漏发。
          2. 武器名优先用记录里自带的 Name 字段，查不到才回退 model.db。
          3. 挂架 DBID 从承载该武器的容器里取；找不到就传 0（平台允许不指定挂架）。

        :param unit: Unit, 单元对象
        :param name_keywords: list, 型号关键字过滤（默认 ['战斧']）
        :return: list, [{'mount': 挂架DBID, 'weapon': 武器DBID, 'count': 可用数量,
                         'name': 名称, 'src': 来源}]
        """
        if name_keywords is None:
            name_keywords = ['战斧']

        def _hit(text):
            t = str(text or '').lower()
            return any(k.lower() in t for k in name_keywords)

        # ---- 1. 权威武器清单（Mounts + Magazines + Loadouts + 平台接口）----
        weapons = self._unit_weapon_list(unit)

        # ---- 2. 建立"武器DBID -> [承载它的挂架/发射装置DBID...]"映射 ----
        mounts_of = {}
        for src in ('Mounts', 'Magazines', 'Loadouts'):
            container = getattr(unit, src, None)
            if not isinstance(container, dict):
                continue
            for _, mount_info in container.items():
                if not isinstance(mount_info, dict):
                    continue
                mount_dbid = 0
                comp = mount_info.get('Component')
                if isinstance(comp, dict):
                    mount_dbid = comp.get('DBID', 0) or 0
                recs = mount_info.get('WeaponRecs')
                if not isinstance(recs, dict):
                    continue
                for _, w in recs.items():
                    if not isinstance(w, dict):
                        continue
                    wid = w.get('WeaponDBID')
                    if wid is None:
                        continue
                    wid = int(wid)
                    lst = mounts_of.setdefault(wid, [])
                    if mount_dbid not in lst:
                        lst.append(mount_dbid)

        # ---- 3. 组方案：同一型号跨多个挂架时，按挂架拆分数量分别发射 ----
        # （不能合成一次调用：BOL 的落点由发射平台位置解算，提前量必须按各自的
        #   挂架分别算，否则只有最后确定的那个挂架/落点生效）
        plans = []
        for wname, wid, cnt in weapons:
            if cnt <= 0:
                continue
            if not _hit(wname):
                wname = self._weapon_name(wid)   # 记录没带名字时用 model.db 兜底
                if not _hit(wname):
                    continue
            mounts = mounts_of.get(wid) or [0]
            n = len(mounts)
            base, extra = divmod(int(cnt), n)
            for i, mount_dbid in enumerate(mounts):
                qty = base + (1 if i < extra else 0)
                if qty <= 0:
                    continue
                plans.append({'mount': mount_dbid, 'weapon': int(wid),
                              'count': qty, 'name': wname,
                              'src': 'get_weapon_infos'})
        return plans

    @staticmethod
    def _reply_ok(res):
        """
        判断平台返回是否**真正执行成功**。

        判定口径（见 global_util.Reply）：
            · 有 code 属性时：**只看 code == 0**（平台自己就是按这个打印
              "指令执行成功/失败"的），这是唯一可靠的依据。
            · 没有 code（如测试桩返回纯字符串）时：退回文本判断，但要
              更精确 —— 只在**明确的失败句式**下判失败。

        🔴 踩过的坑：
          1) 最早写 `'指令执行失败' not in str(res)`：Reply 的 str() 是
             `"code: -1"`，result 是 bytes 不显示 → 失败被判成成功；
          2) 后来加了"result 含'失败'两字就判失败" → **误伤**：平台
             BOL 成功的返回里也会出现"失败"字样（如"0 发失败"），
             导致明明 `指令执行成功` 却被判失败并反复重试 ——
             界面上就是战斧被反复"重定向到新目标"刷屏。
        """
        if res is None:
            return False
        code = getattr(res, 'code', None)
        if code is not None:
            # 平台用 code 区分成功/失败：0 = 未报异常，-1 = 错误
            try:
                return int(code) == 0
            except (TypeError, ValueError):
                return False
        # ---- 没有 code 属性：退回文本判断（仅测试桩会走到这里）----
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

    def _bol_attack(self, unit, lat, lon, mount_db, weapon_db, qty, course=None):
        """
        纯方位（BOL）打击，支持导弹航迹规划点。

        注意：entitys/unit.py 的 Unit.attack_BOL 只暴露 5 个参数，
        但底层 GameServer.api_attack_BOL 的真实签名是
            (unit_obj, lat, lon, mount_num, weapon_id, qty_num, course=[])
        以及协议 RequestAttackBearing 中的 `repeated Waypoint course = 9; //导弹路径规划点`。
        因此这里通过 _game_server 直接调用，以带上级规划的航路点。

        :param unit: Unit, 发射单元对象
        :param lat: float, 目标纬度
        :param lon: float, 目标经度
        :param mount_db: int, 挂架 DBID
        :param weapon_db: int, 武器 DBID
        :param qty: int, 发射数量
        :param course: list, 导弹航迹规划点 [(lat, lon), ...]（**中途点**，
                       本函数会自动把目标点补到航线末尾）
        :return: 平台返回结果，失败返回 None
        """
        course = list(course or [])
        # 🔴 关键：航线必须以**目标点**为终点。
        #    平台是"沿 course 逐点飞行"的：如果 course 的末点不是目标点，
        #    导弹飞到末点就停了，不会再"折"向目标点 ——
        #    之前的现象就是"导弹直接打向了途经点，没再往终点折"。
        #    10-09 成功那次也是这个结构：COURSE 末点 == LATITUDE/LONGITUDE。
        if course:
            try:
                _last = course[-1]
                if (abs(float(_last[0]) - float(lat)) > 1e-9 or
                        abs(float(_last[1]) - float(lon)) > 1e-9):
                    course = course + [(float(lat), float(lon))]
            except (TypeError, ValueError, IndexError):
                course = course + [(float(lat), float(lon))]
        server = getattr(self, '_game_server', None)
        try:
            # 优先底层接口：额外支持 course（导弹路径规划点）
            if server is not None and hasattr(server, 'api_attack_BOL'):
                try:
                    return server.api_attack_BOL(unit, lat, lon, mount_db, weapon_db,
                                                 qty, course=course)
                except TypeError:
                    # 该版本底层接口没有 course 形参，退回位置参数
                    return server.api_attack_BOL(unit, lat, lon, mount_db, weapon_db, qty)
            # 退路：用单元自身的封装接口（不带航路点）
            return unit.attack_BOL(lat, lon, mount_db, weapon_db, qty)
        except Exception as e:
            self._log('error', 'BOL 打击失败 单元[%s] 武器=%s : %s'
                      % (getattr(unit, 'Name', '?'), weapon_db, e))
            return None

    def _set_sub_depth(self, sub, depth):
        """
        设置潜艇深度（浅水发射）。

        entitys/unit.py 同样没有 set_depth 封装，底层为
            GameServer.api_set_depth(unit_obj, depth)
        需先 set_alt_manual(True) 打开手动控制，深度才会生效。

        :param sub: Unit, 潜艇对象
        :param depth: float, 目标深度（米，正数）
        :return: None
        """
        # 去重：深度设一次即可（平台会保持该深度）。
        # 之前每个决策周期都重发，日志实证 3 分钟内 12 条 SetUnit，
        # 属于无谓占用指令配额。
        nm_ = getattr(sub, 'Name', '?')
        seen = self._wra_seen()
        dk = 'SUBDEPTH|%s' % nm_
        if seen.get(dk) == str(depth):
            return
        seen[dk] = str(depth)
        try:
            sub.set_alt_manual(True)  # 必须手动控制，才能设置深度
        except Exception as e:
            self._log('warning', '潜艇[%s] set_alt_manual 失败: %s' % (getattr(sub, 'Name', '?'), e))
        server = getattr(self, '_game_server', None)
        try:
            if server is not None and hasattr(server, 'api_set_depth'):
                server.api_set_depth(sub, depth)
            else:
                sub.set_desired_height(-float(depth))  # 退路：负值表示水下深度
            self._log('info', '潜艇[%s] 深度已设为 %sm（浅水）' % (getattr(sub, 'Name', '?'), depth))
        except Exception as e:
            self._log('error', '设置潜艇[%s]深度失败: %s' % (getattr(sub, 'Name', '?'), e))

    # ------------------------------------------------------------------
    # 任务 2 参战单元配置（如需调整参战兵力，只改这里）
    # 以下名称取自平台实际态势日志（THSituationFull），非猜测：
    #   DDG:  “阿利伯克”级导弹驱逐舰
    #   CG:   CG-52 “邦克山”提康德罗加级号巡洋舰
    # ------------------------------------------------------------------
    TOMAHAWK_SURFACE_EXACT = [
        '“阿利伯克”级导弹驱逐舰',
        'CG-52 “邦克山”提康德罗加级号巡洋舰',
    ]
    TOMAHAWK_SURFACE_KEYS = ['阿利伯克', '阿里伯克', '伯克', '邦克山', 'CG-52']
    # 潜艇
    TOMAHAWK_SUB_EXACT = ['SSN-792 浮蒙特号攻击核潜艇 #1']
    TOMAHAWK_SUB_KEYS = ['SSN-792', '浮蒙特', '蒙特']

    def _resolve_strike_units(self, situation, exact_names, keywords):
        """
        解析参战单元：精确名与关键字两路结果取并集（按单元ID去重）。

        :param situation: tuple, (units dict, contacts dict)
        :param exact_names: list, 精确单元名候选
        :param keywords: list, 名称关键字候选
        :return: list, [(单元名, 单元对象)]
        """
        merged = []
        seen = set()
        for src in (self._find_units_by_exact_name(exact_names),
                    self._get_units_by_keywords(situation, keywords)):
            for name, obj in src:
                key = getattr(obj, 'ID', None) or id(obj)
                if key in seen:
                    continue
                seen.add(key)
                merged.append((name, obj))
        if merged:
            self._log('info', '参战单元解析结果：%s' % [n for n, _ in merged])
        return merged

    def tomahawk_strike_nk_airfield(self, situation):
        """
        战斧打击 NK 机场 —— **已按要求停用（改为完全手动）**。

        用户要求：不再设置导弹航迹规划点，也不设置"自由开火"，
        战斧打不打、怎么打，全部由选手在对局中手动决定。
        因此这里不再调用 attack_BOL，也不再潜艇调深。

        保留本方法只是为了兼容 step() 的调用点，实际不做任何动作。
        若以后要恢复自动打击，参考原实现：
          · 水面舰/潜艇分别用 surface_course / sub_course 两组航迹点；
          · 通过 _bol_attack(unit, lat, lon, mount, weapon, qty, course) 下发；
          · 潜艇先 _set_sub_depth(sub, self.SUB_SHALLOW_DEPTH) 调浅。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 固定返回 0（未发起任何打击）
        """
        self._log('info', '战斧打击机场已停用（改为手动控制：不设航迹、不设自由开火）')
        return 0

    # ==================================================================
    # 第三步：飞机挂载 + 舰船条令
    # ==================================================================
    def set_aircraft_loadouts(self, situation):
        """
        按 AIRCRAFT_LOADOUTS 表给指定飞机设置挂载方案。

        在 initial()（战前规划阶段）调用，则立即完成挂载、准备时间为 0：
            self.set_aircraft_loadout_plan_time(unit_id, loadoutID)
        表里没有的飞机不做任何修改，保持系统默认挂载。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 已成功下发挂载的单元名列表
        """
        if not self.AIRCRAFT_LOADOUTS:
            return []
        exact = list(self.AIRCRAFT_LOADOUTS.keys())
        found = self._find_units_by_exact_name(exact)
        hit_names = [n for n, _ in found]

        missing = [n for n in exact if n not in hit_names]
        if missing:
            self._log('warning', '未匹配到的飞机（挂载未设置）：%s' % missing)

        done = []
        for name, unit in found:
            loadout_id, desc = self.AIRCRAFT_LOADOUTS[name]
            try:
                self.set_aircraft_loadout_plan_time(unit.ID, loadout_id)
                done.append(name)
                self._log('info', '飞机[%s] 挂载已设为 %s (%s)'
                          % (name, loadout_id, desc))
            except Exception as e:
                self._log('error', '飞机[%s] 设置挂载 %s 失败: %s'
                          % (name, loadout_id, e))
        self._log('info', '飞机挂载设置完成 %d/%d' % (len(done), len(exact)))
        return done

    def set_ship_doctrines(self, situation):
        """
        按 SHIP_DOCTRINE_UNITS 给指定水面舰统一设置条令：
            对空自由开火、对海自由开火、
            接战临机出现目标=是（可与任何目标交战）、
            电磁管控雷达=打开。

        :param situation: tuple, (units dict, contacts dict)
        :return: list, 已成功设置条令的单元名列表
        """
        found = self._find_units_by_exact_name(self.SHIP_DOCTRINE_UNITS)
        hit_names = [n for n, _ in found]
        missing = [n for n in self.SHIP_DOCTRINE_UNITS if n not in hit_names]
        if missing:
            self._log('warning', '未匹配到的水面舰（条令未设置）：%s' % missing)

        done = []
        for name, unit in found:
            try:
                # 对空：自由开火
                unit.doctrine_weapon_control_status_air(WeaponControlStatus.Free)
                # 对海：自由开火
                unit.doctrine_weapon_control_status_surface(WeaponControlStatus.Free)
                # 接战临机出现目标：是（可与任何目标交战）
                unit.doctrine_engage_opportunity_targets(
                    EngageWithContactTarget.Yes_AnyTarget)
                # 电磁管控：雷达打开
                unit.doctrine_switch_radar(True)
                done.append(name)
                self._log('info', '舰船[%s] 条令已设置（对空/对海自由开火、'
                                  '接战临机目标=是、雷达开）' % name)
            except Exception as e:
                self._log('error', '舰船[%s] 设置条令失败: %s' % (name, e))
        self._log('info', '舰船条令设置完成 %d/%d' % (len(done), len(self.SHIP_DOCTRINE_UNITS)))
        return done

    # ==================================================================
    # 第四步：任务一 ~ 任务九（均开局立刻启用）
    # ==================================================================
    def _aim260_wra(self):
        """
        F-35C 的 AIM-260 武器使用规则：
          * 对空中感知-未知类型、各类制导武器 —— 不使用武器
          * 对所有飞机的自动开火距离 —— 80 海里
        :return: list, [[weaponID, target_type, qty, range], ...]
        """
        rules = [[self.AIM260_DBID, t, '0', None] for t in self.AIM260_NO_USE_TARGETS]
        # 自动开火距离：对"飞机-未指定"（即所有飞机）设 80 海里
        rules.append([self.AIM260_DBID, WRA_WeaponTargetType.Aircraft_Unspecified,
                      None, self.AIM260_AUTO_FIRE_RANGE_NM])
        return rules


    def add_mission_1_asw(self, situation):
        """
        1_反潜 —— 反潜作战巡逻任务。

        巡逻区（4 个坐标点）：
            (47.597901, -12.514962)  (47.625094, -11.412875)
            (47.012400, -11.395400)  (47.012400, -12.521700)

        任务条令：
          · 关闭"飞机数低于编队不允许起飞"(use_flight_size=False)
          · 关闭 1/3 规则
          · 不勾选"对巡逻区外目标分析"(OPA=False)
          · 不勾选"对武器射程内目标分析"(WWR=False)
          · 对潜自由开火
          · 燃油状态-返航：不返航
          · 武器状态-返航：不返航
          · 打开雷达
        """
        rule = self._patrol_rule_ext(
            one_third_rule=False,
            use_flight_size=False,
            OPA=False,
            WWR=False,
            fuel_state_rtb=FuelStateRTB.No,
            weapon_state_rtb=WeaponStateRTB.No,
        )
        return self.add_set_patrol_mission(
            situation, "1_反潜", MissionPatrolType.ANTI_SUBMARINE,
            [(47.597901, -12.514962), (47.625094, -11.412875),
             (47.012400, -11.395400), (47.012400, -12.521700)],
            ['MH-60R 反潜直升机 #1', 'MH-60R 反潜直升机 #2'],
            rule=rule,
            doctrine={'subsurface': WeaponControlStatus.Free, 'radar': True})

    def add_mission_2_antiradar(self, situation):
        """任务二（1818181818181818）：对海巡逻，F/A-18F #1#2，对海自由开火+雷达开"""
        return self.add_set_patrol_mission(
            situation, "1818181818181818", MissionPatrolType.ANTI_SHIP,
            [(48.737864, -13.167777), (49.001195, -11.625072),
             (48.156980, -12.045704)],
            ['F/A-18F型 战斗机 #1', 'F/A-18F型 战斗机 #2'],
            rule=dict(self.PATROL_RULE_BASE),
            doctrine={'surface': WeaponControlStatus.Free, 'radar': True})

    def add_mission_3_decoy_north(self, situation):
        """任务三：西部海域北侧诱饵弹（对空巡逻，F/A-18F #5，对空自由开火+雷达开）"""
        return self.add_set_patrol_mission(
            situation, "西北诱饵", MissionPatrolType.AIR,
            [(47.541600, -10.880300), (47.541600, -9.684890),
             (47.161200, -10.880300)],
            ['F/A-18F型 战斗机 #5'],
            rule=dict(self.PATROL_RULE_BASE),
            doctrine={'air': WeaponControlStatus.Free, 'radar': True})

    def add_mission_4_decoy_south(self, situation):
        """任务四：西部海域南侧诱饵弹（对空巡逻，F/A-18F #6，对空自由开火+雷达开）"""
        return self.add_set_patrol_mission(
            situation, "西南诱饵", MissionPatrolType.AIR,
            [(45.968319, -9.713547), (46.402935, -10.535515),
             (46.498097, -9.348763)],
            ['F/A-18F型 战斗机 #6'],
            rule=dict(self.PATROL_RULE_BASE),
            doctrine={'air': WeaponControlStatus.Free, 'radar': True})

    def add_mission_5_f35_north(self, situation):
        """任务五：西侧海域北F35（支援，F-35C #1，对空自由开火+雷达开+AIM-260 WRA）"""
        rule = dict(self.SUPPORT_RULE_BASE)
        return self.add_set_support_mission(
            situation, "西北F35",
            [(48.393831, -12.691730), (48.686476, -11.308483)],
            rule, ['F-35C 型“闪电II” 战斗机 #1'],
            weapon_rule=self._aim260_wra(),
            doctrine={'air': WeaponControlStatus.Free, 'radar': True})

    def add_mission_6_f35_south(self, situation):
        """任务六：西侧海域南F35（支援，F-35C #2，对空自由开火+雷达开+AIM-260 WRA）"""
        rule = dict(self.SUPPORT_RULE_BASE)
        return self.add_set_support_mission(
            situation, "西南F35",
            [(45.314312, -11.097853), (44.905688, -9.745750)],
            rule, ['F-35C 型“闪电II” 战斗机 #2'],
            weapon_rule=self._aim260_wra(),
            doctrine={'air': WeaponControlStatus.Free, 'radar': True})

    def add_mission_7_e2d(self, situation):
        """任务七：E2D探测任务（支援，E-2D #1 + MQ-25A #1/#2，雷达开，出航/阵位高度 15000m）"""
        rule = dict(self.SUPPORT_RULE_BASE)
        # [出航油门, 阵位油门, 出航高度, 阵位高度] —— 只改高度，油门按默认
        rule['throttle_and_altitude'] = [None, None, 15000, 15000]
        return self.add_set_support_mission(
            situation, "7_E2D探测任务",
            [(46.931883, -13.581819), (46.465679, -13.086716)],
            rule, ['E-2D型“先进鹰眼”舰载预警机 #1',
                   'MQ-25A型 无人加油机 #1', 'MQ-25A型 无人加油机 #2'],
            doctrine={'radar': True})

    def add_mission_8_ew_north(self, situation):
        """任务八：西侧海域北电子战飞机（支援，EA-18G #1 + 企业号 F/A-18F #3#4，雷达开）"""
        return self.add_set_support_mission(
            situation, "西北电子战",
            [(48.049541, -13.608961), (48.212714, -13.086280)],
            dict(self.SUPPORT_RULE_BASE),
            ['EA-18G “咆哮者”电子战飞机 #1',
             'F/A-18F型 战斗机 #3', 'F/A-18F型 战斗机 #4'],
            doctrine={'radar': True})

    def add_mission_9_ew_south(self, situation):
        """任务九：西侧海域南电子战飞机（支援，EA-18G #2，雷达开）"""
        return self.add_set_support_mission(
            situation, "西南电子战",
            [(45.901111, -13.019168), (45.794874, -12.357930)],
            dict(self.SUPPORT_RULE_BASE), ['EA-18G “咆哮者”电子战飞机 #2'],
            doctrine={'radar': True})

    def add_all_step4_missions(self, situation):
        """
        创建新建的反潜/电子战/诱饵等任务（开局立刻启用）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        creators = (self.add_mission_1_asw, self.add_mission_2_antiradar,
                    self.add_mission_3_decoy_north, self.add_mission_4_decoy_south,
                    self.add_mission_5_f35_north, self.add_mission_6_f35_south,
                    self.add_mission_7_e2d, self.add_mission_8_ew_north,
                    self.add_mission_9_ew_south)
        ok = 0
        for fn in creators:
            try:
                if fn(situation) is not None:
                    ok += 1
            except Exception as e:
                self._log('error', '%s 执行异常: %s' % (fn.__name__, e))
        self._log('info', '第四步任务创建完成 %d/%d' % (ok, len(creators)))
        return ok

    def apply_aim_no_use_wra(self, situation):
        """
        修改二：对**所有**携带 AIM-9X / AIM-120D / AIM-260 的飞机，把这三种弹对以下
        7 类目标统一设置为"对这种目标不使用武器"：
            空中感知-未知类型、制导武器-未指定、
            制导武器-超音速掠海、制导武器-亚音速掠海、
            制导武器-超音速、制导武器-亚音速、制导武器-弹道导弹

        在单元上设置（Unit 继承 DoctrineOperator，支持 WRA），
        因此无论该机参与的是巡逻任务还是支援任务都会生效。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功设置的单元数
        """
        targets = self.AIM260_NO_USE_TARGETS

        # 只对"飞机"设置（不含舰船/潜艇/地面单元）：
        #   1) 第三步设置了挂载的飞机；
        #   2) 当前想定里 category == 'Aircraft' 的单元；
        #   3) 本地飞机集合 aircrafts 里的单元。
        names = set(self.AIRCRAFT_LOADOUTS.keys())
        units = situation[0] if isinstance(situation[0], dict) else {}
        for _, u in units.items():
            if isinstance(u, dict) and str(u.get('category', '')) == 'Aircraft':
                nm = u.get('name')
                if nm:
                    names.add(nm)
        aircrafts = getattr(self, 'aircrafts', None)
        if isinstance(aircrafts, dict):
            for obj in aircrafts.values():
                nm = getattr(obj, 'Name', None)
                if nm:
                    names.add(nm)

        found = self._find_units_by_exact_name(sorted(names))
        if not found:
            self._log('warning', '修改二：未解析到任何飞机，AIM 不使用武器未设置')
            return 0
        done = 0
        for uname, unit in found:
            carried = self._unit_carried_weapons(unit)
            try:
                # 关键：只对**该单元实际携带**的武器下发 WRA。
                # 给不存在的武器下发会报"找不到武器"，且一条失败会连累整批。
                aim_wids = [w for w in self.AIM_NO_USE_WEAPONS
                            if int(w) in carried]
                mid_wids = [w for w, _n, _r in self.MID_RANGE_WRA
                            if int(w) in carried]
                if not aim_wids and not mid_wids:
                    continue
                # 1) AIM-9X / AIM-120D / AIM-260 对 7 类目标不使用武器
                #    🔴 必须去重！本函数每周期都被调用，一架飞机每次就是几十条指令，
                #       不去重会瞬间吃光 500 条配额，后面的 154 / 发射车 规则
                #       全部被"超出数量限制"丢弃
                #       （日志实证：武器 3567 出现 67 次、718 出现 62 次）。
                for wid in aim_wids:
                    for t in targets:
                        self._wra_once(unit, wid, t, '0', 'AIM_NOUSE')
                # 2) 三型中距弹：对未知空中/所有制导武器不使用；对所有飞机齐射1枚 + 开火距离
                for wid in mid_wids:
                    rng_nm = dict((w, r) for w, _n, r in self.MID_RANGE_WRA)[wid]
                    self._wra_once(unit, wid,
                                   WRA_WeaponTargetType.Air_Contact_Unknown_Type,
                                   '0', 'AIM_MID')
                    for gt in self.GUIDED_WEAPON_TARGET_TYPES:
                        self._wra_once(unit, wid, gt, '0', 'AIM_MID')
                    for at in self.AIRCRAFT_TARGET_TYPES:
                        self._wra_once(unit, wid, at, '1', 'AIM_MID')
                        self._wra_range_once(unit, wid, at, rng_nm, 'AIM_MID')
                done += 1
            except Exception as e:
                self._log('error', '单元[%s]设置 WRA 失败: %s' % (uname, e))
        self._log('info', 'AIM/中距弹 WRA 设置完成 %d 个单元' % done)
        return done

    # ==================================================================
    # 任务十 ~ 任务十九（单元名取自平台态势日志）
    # ==================================================================
    def _patrol_rule_ext(self, **over):
        """巡逻任务 rule：基础项 + 本次统一追加项，可再覆盖。"""
        r = dict(self.PATROL_RULE_BASE)
        r.update(self._mission_common_doctrine())
        r.update(over)
        return r

    def _support_rule_ext(self, **over):
        """支援任务 rule：基础项 + 本次统一追加项，可再覆盖。"""
        r = dict(self.SUPPORT_RULE_BASE)
        r.update(self._mission_common_doctrine())
        r.update(over)
        return r

    def _doctrine_ext(self, engage_any=False, **over):
        """
        任务单元条令：对空自由开火 + 雷达开（可覆盖）。

        :param engage_any: bool, True 时额外设"接战临机出现目标=是（可与任何目标交战）"
        :param over: 其他条令覆盖项
        """
        d = {'air': WeaponControlStatus.Free, 'radar': True}
        if engage_any:
            d['engage_opportunity'] = EngageWithContactTarget.Yes_AnyTarget
        d.update(over)
        return d

    def add_mission_10_ship_A(self, situation):
        """
        任务十（1515151515151515）：A区打船巡逻 —— 开局**不**启用。

        执行单元：F-15E #1#2 + 阿斯图机场的 B-2A 轰炸机 #1#2
        条令：对空自由开火 + 对海自由开火 + 雷达开
        """
        m = self.add_set_patrol_mission(
            situation, "1515151515151515", MissionPatrolType.ANTI_SHIP,
            [(45.314300, -0.448020), (45.314300, 0.221596),
             (44.977900, 0.221596), (44.977900, -0.448020)],
            ['F-15E型 战斗机 #1', 'F-15E型 战斗机 #2',
             'B-2A 轰炸机 #1', 'B-2A 轰炸机 #2'],
            rule=self._patrol_rule_ext(),
            doctrine=self._doctrine_ext(air=WeaponControlStatus.Free,
                                        surface=WeaponControlStatus.Free,
                                        radar=True))
        if m is not None:
            try:
                m.mission_active(False)      # 开局不启用
                self._log('info', '10_A区打船 已创建并设为"开局不启用"')
            except Exception as e:
                self._log('error', '任务十 设为不启用失败: %s' % e)
        return m

    def add_mission_11_ship_C(self, situation):
        """任务十一：C区船只打击（对海巡逻，MQ-9B #1~6 + MQ-1C #1~8）"""
        units = ['MQ-9B型  无人机 #%d' % i for i in range(1, 7)] + \
                ['MQ-1C  无人机 #%d' % i for i in range(1, 9)]
        return self.add_set_patrol_mission(
            situation, "无人机送死", MissionPatrolType.ANTI_SHIP,
            [(49.943145, -0.556572), (49.979383, -0.012980),
             (49.623551, 0.075979), (49.576093, -0.446543)],
            units,
            rule=self._patrol_rule_ext(),
            doctrine=self._doctrine_ext(surface=WeaponControlStatus.Free))



    def add_mission_12_north35_1(self, situation):
        """任务十四：北35-1（支援，F-35B #1 + F-15J #1）"""
        return self.add_set_support_mission(
            situation, "北35-1",
            [(53.891493, 4.884105), (53.674450, 4.410329)],
            self._support_rule_ext(),
            ['F-35B型“闪电II” 战斗机 #1', 'F-15J型“鹰”战斗机  #1'],
            doctrine=self._doctrine_ext())

    def add_mission_13_north35_2(self, situation):
        """任务十五：北35-2（支援，F-35B #2 + F-15J #2）"""
        return self.add_set_support_mission(
            situation, "北35-2",
            [(53.272960, 6.275026), (52.860884, 5.637663)],
            self._support_rule_ext(),
            ['F-35B型“闪电II” 战斗机 #2', 'F-15J型“鹰”战斗机  #2'],
            doctrine=self._doctrine_ext())




    def add_mission_14_north35_3(self, situation):
        """任务十九：北35-3（支援，F-35A #1）"""
        return self.add_set_support_mission(
            situation, "北35-3",
            [(55.019999, 4.515092), (54.682323, 4.201212)],
            self._support_rule_ext(),
            ['F-35A型“闪电II” 战斗机 #1'],
            doctrine=self._doctrine_ext())

    def add_mission_15_carrier_guard(self, situation):
        """
        25_航母护航 —— 保护航母的对空/对海巡逻任务。

        巡逻区（4 个参考点，围成航母附近的一个矩形）：
            (47.208800, -14.824400)  (47.208800, -14.510800)
            (47.106700, -14.824400)  (47.106700, -14.510800)

        执行单元：“阿利伯克”级导弹驱逐舰、CG-52“邦克山”巡洋舰

        任务条令（按要求逐项设置）：
          · 对空自由开火、对海自由开火
          · 开雷达
          · 接战临机出现目标 = 是（可与任何目标交战）
          · 关闭 1/3 规则
          · 不勾选"对巡逻区外的探测目标进行分析"(OPA)
          · 不勾选"对武器射程内探测目标进行分析"(WWR)
          · 水面舰艇航速：出航油门最大、阵位油门最大、攻击油门最大

        注意：水面舰艇的油门口是独立的 `set_*ThrottleShip`，
        不能用飞机的 `patrol_set_throttle_*`，否则设了也不生效。
        """
        rule = self._patrol_rule_ext(
            one_third_rule=False,
            OPA=False,
            WWR=False,
            # 水面舰艇：出航/阵位/攻击 全部最大油门
            ship_throttle=(Throttle.Flank, Throttle.Flank, Throttle.Flank),
        )
        return self.add_set_patrol_mission(
            situation, "航母", MissionPatrolType.ANTI_SHIP,
            [(47.208800, -14.824400), (47.208800, -14.510800),
             (47.106700, -14.824400), (47.106700, -14.510800)],
            # 按要求：邦克山已改派去"战斧"对陆打击任务，航母护航只留阿利伯克
            ['“阿利伯克”级导弹驱逐舰'],
            rule=rule,
            doctrine=self._doctrine_ext(engage_any=True,
                                        air=WeaponControlStatus.Free,
                                        surface=WeaponControlStatus.Free,
                                        radar=True))

    # ==================================================================
    # 新增任务组（A~D / 左中右 / 北船 / 北加油 / 中1中2 / 潜艇跑 / 装甲车队）
    # ==================================================================
    # 水面发射车支援任务（开局不启动），auto_evasion=False
    CAR_SHIP_MISSIONS = (
        # (任务名, 参考点, 执行单元, 是否开局启动) —— 任务名按选手原话，不自行改名
        # A~D 四个"撤离用"支援任务：**开局启动、但不预置执行单元**
        #   （选手会在打光弹后手动把发射车转入对应任务）
        ('A', [(47.608973, -0.867896), (47.139439, -0.825667)], [], True),
        ('B', [(47.635726, 0.597333), (47.114162, 0.606425)], [], True),
        # C 支援任务：原本放奥尔良机场的 幻影-2000-5EI #1~#4 与 RQ-4B 全球鹰#1，
        #   ⚠️ 按要求：这 5 架已改由"米卡"对空巡逻任务使用，**从 C 任务里舍弃**，
        #   C 只保留原本在空中的 RQ-180 隐身无人侦察机。
        #   （仍是 **C 支援任务**，不是"C船"打击任务。）
        ('C', [(48.348536, 3.297530), (47.880057, 3.808931)],
         ['RQ-180型隐身无人侦察机'], True),
        ('D', [(49.616902, 4.642746), (49.341559, 5.205965)], [], True),
        # 防空支援任务（开局启动，对空自由开火，初始关雷达）
        #   按要求：地空导弹连#2 **不再开局猛冲**到旧参考点，直接分配给"右"任务；
        #   其余（对空自由开火 + 初始关雷达）不变。
        ('左', [(48.725172, -1.307133), (48.710053, -1.006182)],
         ['地空导弹连#1'], True),
        ('中', [(48.884762, -0.068431), (48.881383, 0.209246)],
         ['爱国者地空导弹连#1'], True),
        ('右', [(48.904978, 1.667522), (48.935677, 1.351050)],
         ['地空导弹连#2'], True),
    )

    # ==================================================================
    # A~D 撤退任务的"最大速度"保障（选手要求：打完船手动转进 A~D 后要跑到 50+ km/h）
    #
    #   🔴 为什么不能只靠任务油门：
    #      平台的任务油门只有 **飞机 / 水面舰艇 / 潜艇** 三套通道
    #      （proto：setMissionPatrolAircraftThrottle / ShipThrottle /
    #        SubmarineConfig；根本没有"地面单元"这一路）。
    #      而这些撤退单元是**地面机动单元**（海马斯/反舰导弹排/霍克/LUCAS），
    #      所以 transitThrottleShip=4 对它们无效，一直吃默认低速 ——
    #      实测 18.5 km/h（= 10 节 = 其最大 30 节的三分之一）。
    #
    #   做法：发现单元被（选手手动）分配进 A~D 时，对**单元本身**下一次：
    #         set_throttle(Flank) + set_desired_speed(55.6)
    #        即"油门最大 + 期望速度 30 节"。
    #        ⚠️ 只提速，**不规划任何航线** —— 撤退航线由 A~D 任务自己给。
    #        同一 (单元, 任务) 只下一次，避免每周期重复占配额。
    #
    #   🔴 判据用"类别"而不是写死名单：
    #      一开始按选手给的名单写死，结果实测就漏了「反舰导弹排#4」——
    #      它被转进 A 却没在名单里，于是速度还是 18.5。名单太脆。
    #      A~D 本来就是给前沿地面单元撤退用的，所以改为：
    #      **A~D 里所有"非飞机"单元一律提速**。
    #      （飞机有任务油门通道，本来就生效，不动它。）
    # ==================================================================
    ESCAPE_MISSION_NAMES = ('A', 'B', 'C', 'D')
    # 左/中/右 是"打打停停"的防空任务：
    #   分配进去 -> 最大速度机动；被**移出** -> 停车（选手随后手动让它自由开火），
    #   打完再分配进去 -> 再次最大速度 …… 如此往复。
    SAM_MISSION_NAMES = ('左', '中', '右')
    # 左/中/右 是否也做单元级提速：
    #   True  = 分配进去最大速度跑、移出后按住停车（当前行为）
    #   False = 完全不管它们，恢复"分配即 18.5 / 取消即停车"的原始行为
    #           （选手说这三组被打概率小、不需要加速；改这一个词即可回退，
    #            完全不影响已验收的 A~D）
    SAM_SPEED_BOOST = True
    # 30 节 = 55.6 km/h（地面单元实测的最大速度；"低速"档 18.5 km/h 正是它的 1/3）
    # 注：model.db 的 DataFacility.MaxSpeed 对 LUCAS(50001) 等条目写的是 0，
    #     但该字段对地面单元并不作准 —— 实测 LUCAS 能跑，且 18.5 = 55.6/3，
    #     说明它的最大速度同样是 30 节。故不按该字段区分。
    # 30 节（地面单元最大速度）。
    #   🔴 必须留一点余量：平台把 km/h 换算成节时按 1.852 算，
    #      写 55.6 会变成 30.02 节，回算 55.597 km > 上限 55.560 km，
    #      平台直接拒收（日志实证："已超出可设置范围：0.000000 - 55.560000公里"）。
    #      取 55.5 -> 29.968 节 -> 55.50 km，稳在范围内。
    # 必须留一点余量：... 
    # "50 多 km/h"（选手要求的目标档）。
    #   🔴 各单元速度上限并不一样，必须取**最低的那个**才不会发失败：
    #      地空导弹连 / 爱国者 等 ：上限 55.56 km/h（30 节）
    #      海马斯火箭炮#4        ：上限 **51.856 km/h（28 节）**
    #        日志实证：manualSpeed=55.5 -> "已超出可设置范围：0.000000 - 51.856000公里"
    #      取 50.5 km/h（27.3 节）：在所有单元的范围内，且满足"50 多"的要求。
    #      另外油门档 FLANK 本身就会让单元跑到它自己的最大速度，
    #      显式速度只是"托底"，失败也不影响整体（见提速循环里的分开 try）。
    ESCAPE_SPEED_KMH = 50.5
    # 开局猛冲单元"到达目标点"的判定半径（公里）：到位后自动停车
    #   （否则"手动油门=最大 + 航线已结束"会让它自己乱走）
    RUSH_ARRIVE_KM = 5.0
    # 每几个决策周期**重发一次**提速指令（自我修复：防止平台在分配任务等时机
    # 把速度重置回默认低速 18.5）。5 个周期 ≈ 2.5 分钟，占用极小。
    ESCAPE_REASSERT_CYCLES = 5

    def _units_of_mission_raw(self, mission):
        """
        从平台取"某任务已分配的单元 guid"，**对返回格式做最大兼容**。

        🔴 为什么不用 entitys 的 mission.get_units_assigned()：
           它写死了 `mission_json["mission"]["unitlist"]` 这个字段名，
           实测在真机上解析不出来（返回空列表，导致提速一直不触发）。
           这里改为：拿到 Reply.result 的原始文本后，**直接正则抓 guid 形式的串**，
           不管平台把它放在哪个字段里都能拿到。
           （多抓到的任务 guid 之类会被 get_unit() 过滤掉，无害。）

        :param mission: Mission 对象
        :return: list, 单元 guid
        """
        try:
            reply = self._game_server.api_get_units_assigned(mission)
        except Exception as e:
            self._log('warning', '读取任务单元失败: %s' % e)
            return []
        if reply is None or getattr(reply, 'code', None) != 0:
            return []
        raw = getattr(reply, 'result', None)
        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode('utf-8', 'replace')
            except Exception:
                raw = str(raw)
        txt = str(raw or '')
        # 单元的 guid 形如 'J9-00001JTUIVL8E'
        return re.findall(r'[A-Za-z0-9]{2}-[A-Za-z0-9]{9,}', txt)

    def _boost_units(self, guids, tag):
        """
        对指定 guid 的单元下"最大速度"：取消阵位 + 油门最大 + 期望速度 55.6。
        **只改速度，不动航线**。

        :param guids: list, 单元 guid
        :param tag: str, 日志用标签
        :return: int, 成功数
        """
        n = 0
        for g in guids:
            obj = self.get_unit(g)
            if obj is None:
                continue
            nm = getattr(obj, 'Name', g)
            try:
                obj.hold_positon(False)      # 取消"保持阵位"，否则原地不动
                obj.set_throttle(Throttle.Flank)
                obj.set_desired_speed(self.ESCAPE_SPEED_KMH)
                n += 1
                # 标记已提速 —— **必须先把状态字典建出来**，
                # 否则（首次调用时字典还不存在）状态没记上，
                # 下一周期会把它当成"第一次进入"再提速一次。
                st = getattr(self, '_ly_speed_state', None)
                if not isinstance(st, dict):
                    st = {}
                    self._ly_speed_state = st
                st[g] = 'run'
                # 记下"进过 左/中/右"（移出时要靠它补一次"按住停车"）
                if tag in self.SAM_MISSION_NAMES:
                    ss = getattr(self, '_ly_sam_seen', None)
                    if not isinstance(ss, set):
                        ss = set()
                        self._ly_sam_seen = ss
                    ss.add(g)
                self._log('info', '[%s] 提速[%s]：油门最大 + 期望速度 %.1f km/h'
                                  '（30 节），未改动其航线'
                          % (tag, nm, self.ESCAPE_SPEED_KMH))
            except Exception as e:
                self._log('error', '[%s] 提速[%s] 失败: %s' % (tag, nm, e))
        return n

    def rush_units_park(self, situation):
        """
        开局猛冲（RUSH_UNITS）的单元**到达目标点后自动停车**。

        🔴 为什么需要（选手实测 + 日志实证）：
           猛冲是"给一条到目标点的航线 + 手动油门=FLANK"。冲到终点后
           **航线结束、而 FLANK 还在** —— 一台"油门最大又没航线"的地面车
           就会自己乱走（选手现象："到目标点的航线没有了，所以乱跑"）。
           所以到位后补一次 FullStop + 保持阵位，把它按住。

        安全边界：
          · 只处理 RUSH_UNITS 名单里的单元，**到达才停、只停一次**；
          · 已经被 A~D / 左中右 接手（提速状态=run）的**绝不动**
            —— 不能干扰已经验收通过的那套提速；
          · 不动航线、不下别的东西。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本次停车数
        """
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return 0
        parked = getattr(self, '_ly_rush_parked', None)
        if not isinstance(parked, set):
            parked = set()
            self._ly_rush_parked = parked
        speed_state = getattr(self, '_ly_speed_state', None)
        if not isinstance(speed_state, dict):
            speed_state = {}
            self._ly_speed_state = speed_state   # 必须挂到 self 上，下面要写回状态
        n = 0
        for entry in self.RUSH_UNITS:
            name, tgt = entry[0], entry[1]
            for uname, obj in self._find_units_by_exact_name([name]):
                g = getattr(obj, 'ID', None)
                if g is None or g in parked:
                    continue
                # 🔴 不再因为"它被算在某个任务里"就跳过！
                #    平台的任务成员列表**会滞后**：选手把海马斯#4 从 D 移到
                #    E船 之后，平台的 D 列表里还挂着它（日志实证：
                #    "认到的单元={'D': [..., '海马斯火箭炮#4']}"），
                #    于是提速逻辑一直在拉它、而这里又被跳过 -> 它永远不停 ✗。
                #    猛冲到位的语义很明确：**到了自己的目标点就该停车待命**。
                u = units.get(g)
                if not isinstance(u, dict):
                    continue
                # 🔴 态势里坐标的键名是 **lat / lon**（见 entitys/facility.py
                #    get_summary_info）。写成 latitude/longitude 会永远读不到，
                #    这个"到位停车"就永远不会触发。这里两种都兼容。
                try:
                    lat = float(u.get('lat', u.get('latitude')))
                    lon = float(u.get('lon', u.get('longitude')))
                except (TypeError, ValueError):
                    continue
                # 等距近似：够用（判断"到没到"只需几公里精度）
                dlat = (lat - float(tgt[0])) * 111.0
                dlon = ((lon - float(tgt[1])) * 111.0
                        * math.cos(math.radians(lat)))
                dist = math.sqrt(dlat * dlat + dlon * dlon)
                if dist > self.RUSH_ARRIVE_KM:
                    continue
                try:
                    obj.set_throttle(Throttle.FullStop)
                    obj.hold_positon(True)
                    parked.add(g)
                    # 把提速状态记成 stop：这样**以后真把它分配进 A~D 时，
                    # 会重新触发一次提速**（否则状态停留在 run，不会再提速）。
                    if isinstance(speed_state, dict):
                        speed_state[g] = 'stop'
                    n += 1
                    self._log('info', '猛冲单元[%s] 已到目标点（距 %.1f km），'
                                      '停车待命（避免"油门最大又没航线"自己乱走）'
                              % (uname, dist))
                except Exception as e:
                    self._log('error', '猛冲单元[%s] 停车失败: %s' % (uname, e))
        return n

    def enforce_escape_speed(self, situation):
        """
        A~D / 左中右 任务的"速度"联动（选手改不了油门，必须由智能体下发）。

        规则（选手明确要求）：
          · 单元被分配进 **A~D**（撤离任务）-> 最大速度跑（Flank + 55.6 km/h），
            之后**一直跑**（选手不会再把它们移出来）；
          · 单元被分配进 **左/中/右**（防空任务）-> 同样最大速度机动；
          · **左/中/右 的单元被移出后 -> 停车**（FullStop + 保持阵位）——
            它们是"打打停停"：移出=停车待机（选手随后手动让它自由开火），
            再分配进去=加速转移，然后再移出=停车 …… 如此往复。
          · 飞机不动（它们有任务油门通道，本来就生效）。
          · 🔴 **只改油门/速度，绝不规划或清除航线** ——
            否则就变成"用航线假装加速"，跑到阵位后照样掉速。

        按**状态迁移**下发：只有"停->跑"或"跑->停"的边沿才发指令，
        稳定状态不重复占配额。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本次新下发的指令单元数
        """
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return 0
        missions = self._all_mission_objects() or {}

        def _is_aircraft(guid):
            u = units.get(guid)
            return (isinstance(u, dict)
                    and str(u.get('category', '')) == 'Aircraft')

        # ---- 1) 收集"此刻在 A~D / 左中右 里"的单元 ----
        names = tuple(self.ESCAPE_MISSION_NAMES) + (
            tuple(self.SAM_MISSION_NAMES) if self.SAM_SPEED_BOOST else ())
        id2name = {}
        for mn in names:
            m = missions.get(mn)
            if m is not None:
                gid = str(getattr(m, 'ID', ''))
                if gid:
                    id2name[gid] = mn
        # ---- 来源1：平台"任务已分配单元"查询（权威）----
        plat = {}
        for mn in names:
            m = missions.get(mn)
            if m is None:
                continue
            for g in self._units_of_mission_raw(m):
                if _is_aircraft(g):
                    continue
                plat[g] = mn
        # ---- 来源2：态势里的 unit["mission"] 字段（可能滞后）----
        sit = {}
        for guid, u in units.items():
            if not isinstance(u, dict) or _is_aircraft(guid):
                continue
            mg = str(u.get('mission', '') or '')
            mn = id2name.get(mg) or (mg if mg in names else None)
            if mn:
                sit[guid] = mn
        # 🔴 判定策略：**两个来源取并集**。
        #   上一版曾想把"左/中/右"收紧成只认平台查询（担心移出后不生效），
        #   但实战确认：**移出后平台确实会停车，只是要等一段时间**
        #   （速度指令有惯性），并不是判定不准。
        #   既然现有判定已经跑通（A~D / 左中右 都到 50+ km/h），
        #   就保持并集、不做收紧，避免把已验证的成功改坏。
        in_mission = dict(plat)
        for g, mn in sit.items():
            in_mission.setdefault(g, mn)
        # 诊断：成员变化时打印一次两个来源的判定（便于核对"移出/重分配"）
        #   🔴 注意用 sum(1 for ...)：len(生成器) 会抛 TypeError，
        #      而它抛在提速循环**之前**，会把整个看护函数打断，
        #      导致"任务成员一变就提不了速"（日志里表现为
        #      "A~D 撤退提速看护异常: object of type 'generator' has no len()"）。
        sig = {mn: sorted(g for g, x in in_mission.items() if x == mn) for mn in names}
        if sig != getattr(self, '_ly_speed_sig', None):
            self._ly_speed_sig = sig
            # 连"认到的到底是哪几台"一起打出来，便于核对误判
            _who = {}
            for mn in names:
                _ns = []
                for g in sig.get(mn, []):
                    o2 = self.get_unit(g)
                    _ns.append(getattr(o2, 'Name', g) if o2 is not None else g)
                if _ns:
                    _who[mn] = _ns[:4]
            self._log('info', '速度联动判定: 平台=%s ｜ 态势=%s ｜ 认到的单元=%s'
                      % ({mn: sum(1 for g, x in plat.items() if x == mn)
                          for mn in names},
                         {mn: sum(1 for g, x in sit.items() if x == mn)
                          for mn in names},
                         _who))

        tracked = getattr(self, '_ly_speed_tracked', None)
        if not isinstance(tracked, set):
            tracked = set()
            self._ly_speed_tracked = tracked
        # 进过 左/中/右 的单元（它们被移出时我才补"按住"；A~D 不管）
        sam_seen = getattr(self, '_ly_sam_seen', None)
        if not isinstance(sam_seen, set):
            sam_seen = set()
            self._ly_sam_seen = sam_seen
        state = getattr(self, '_ly_speed_state', None)
        if not isinstance(state, dict):
            state = {}
            self._ly_speed_state = state
        # 每 ESCAPE_REASSERT_CYCLES 个周期**重发一次**提速：
        #   防止平台在"分配任务"等时机把速度重置回 18.5（自我修复）。
        at = getattr(self, '_ly_speed_at', None)
        if not isinstance(at, dict):
            at = {}
            self._ly_speed_at = at
        cyc = int(getattr(self, '_ly_esc_cycle', 0)) + 1
        self._ly_esc_cycle = cyc
        tracked |= set(in_mission.keys())

        n = 0
        # ---- 2) 在 A~D / 左中右 里的 -> 全速 ----
        for g, mn in in_mission.items():
            first = (state.get(g) != 'run')
            # 🔴 定期重发**只给 A~D**（它们要一直跑，已验收，不动）。
            #    左/中/右 **绝不重发**：选手取消任务分配后，平台正在把它减速停稳，
            #    如果我还每 5 周期重发一次"最大油门"，它就一直停不下来
            #    （实测要将近 5 分钟才停）。左/中/右 只在"进入任务"那一次提速。
            allow_reassert = (mn in self.ESCAPE_MISSION_NAMES)
            stale = (allow_reassert
                     and cyc - int(at.get(g, -99999))
                     >= self.ESCAPE_REASSERT_CYCLES)
            if not (first or stale):
                continue
            # 🔴 "自己一直跑"的根治：
            #    平台的"任务已分配单元"列表**会滞后**（选手取消分配后，它还会
            #    把这台列在里面一段时间），于是我会一直重发提速，把它拉着一路跑。
            #    判据：**已经停住的车（速度≈0）说明选手已经取消了分配 -> 绝不再提速**，
            #    并把状态记为 stop（下次真分配进来时会重新提速）。
            #    只拦"重发"，不拦"首次进入"，所以 A~D 首次分配的提速完全不受影响。
            if stale and not first:
                _sp = None
                _u = units.get(g)
                if isinstance(_u, dict):
                    _sp = _u.get('speed')
                try:
                    _sp = None if _sp is None else float(_sp)
                except (TypeError, ValueError):
                    _sp = None
                if _sp is not None and _sp <= 1.0:
                    state[g] = 'stop'
                    continue
            obj = self.get_unit(g)
            if obj is None:
                continue
            nm = getattr(obj, 'Name', g)
            try:
                obj.hold_positon(False)        # 取消"保持阵位"，否则原地不动
                obj.set_throttle(Throttle.Flank)
                state[g] = 'run'
                at[g] = cyc
                if mn in self.SAM_MISSION_NAMES:
                    sam_seen.add(g)            # 记住它进过 左/中/右
                n += 1
                # 显式速度**单独 try**：有的单元上限更低（如海马斯#4 = 28 节），
                # 被平台拒收时不能把"已提速"这件事整体作废
                # （否则状态没记上、日志也没有，下一周期还会重发一遍）。
                _spd_note = ''
                try:
                    obj.set_desired_speed(self.ESCAPE_SPEED_KMH)
                except Exception as e2:
                    _spd_note = '（该单元速度上限更低，仅用油门档；%s）' % e2
                self._log('info', '[%s] 提速[%s]：油门最大 + 期望速度 %.1f km/h'
                                  '（约 %.0f km/h），未改动其航线%s%s'
                          % (mn, nm, self.ESCAPE_SPEED_KMH,
                             self.ESCAPE_SPEED_KMH,
                             '' if first else '（定期重发）', _spd_note))
            except Exception as e:
                self._log('error', '[%s] 提速[%s] 失败: %s' % (mn, nm, e))
        # ---- 3) 离开被跟踪任务的单元 ----
        #   A~D：选手不会移出，保持原样（只记状态）。
        #   左/中/右：**补一次"停车"** ——
        #     🔴 实战发现：平台在移出任务时确实会停车，但**过一会儿它会自己溜走**
        #        （因为我提速时取消了它的"保持阵位"，它会顺着原航线漂出去）。
        #        这里补两条：油门归零 + 保持阵位，把它**按住**。
        #        同时把状态记成 'stop'，这样选手**再分配进去时会重新提速**
        #        （"打打停停"：移出->按住->自由开火；再分配->加速转移）。
        for g in list(tracked):
            if g in in_mission:
                continue
            tracked.discard(g)
            if state.get(g) == 'stop':
                continue
            state[g] = 'stop'
            if g not in sam_seen:            # 只处理 左/中/右 的单元
                continue
            sam_seen.discard(g)
            obj = self.get_unit(g)
            if obj is None:
                continue
            nm = getattr(obj, 'Name', g)
            try:
                obj.set_throttle(Throttle.FullStop)
                obj.hold_positon(True)       # 保持阵位 = 原地按住
                n += 1
                self._log('info', '左/中/右 移出[%s]：已按住'
                                  '（油门归零 + 保持阵位），不会再自己溜走' % nm)
            except Exception as e:
                self._log('error', '按住[%s] 失败: %s' % (nm, e))
        return n

    def add_car_ship_missions(self, situation):
        """
        创建 A~D 发射车支援任务（开局不启动）与 左/中/右 防空支援任务（开局启动）。

        任务条令：关闭 1/3 规则；关闭自动规避；
        防空任务额外设"对空自由开火"。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建数
        """
        ok = 0
        for name, pts, units, active in self.CAR_SHIP_MISSIONS:
            try:
                is_aa = '地空导弹连' in ''.join(units) or '爱国者' in ''.join(units)
                # 出航/阵位油门一律拉到最大（Flank）：
                #   · 地面机动单元（爱国者连/海马斯/反舰导弹排/装甲车）最大 30 节
                #     ≈ 55.6 km/h；不设时平台按默认低速跑，只有约 10 节
                #     （18.5 km/h），跑不到阵位 —— 走 ship_throttle 通道；
                #   · 飞机（C 任务的 RQ-180）走 throttle_and_altitude 通道。
                rule = self._support_rule_ext(
                    one_third_rule=False,
                    auto_evasion=AutomaticEvasion.No,
                    ship_throttle=(Throttle.Flank, Throttle.Flank),
                    throttle_and_altitude=(Throttle.Flank, Throttle.Flank,
                                           None, None))
                doct = {}
                if is_aa:
                    # 防空任务：对空自由开火；**初始关闭雷达**（按要求）
                    doct = {'air': WeaponControlStatus.Free, 'radar': False}
                m = self.add_set_support_mission(
                    situation, name, pts, rule, units, doctrine=doct or None)
                if m is not None:
                    if not active:
                        m.mission_active(False)
                    # 左/中/右：单元是**我们自己刚分配进去的**，直接提速 ——
                    # 不依赖"从平台读任务单元"那一步，保证一定生效。
                    if self.SAM_SPEED_BOOST and name in self.SAM_MISSION_NAMES:
                        _, _gids = self._find_unit_guids_by_ovlp(situation, units)
                        self._boost_units(_gids, name)
                    ok += 1
            except Exception as e:
                self._log('error', '[%s] 创建异常: %s' % (name, e))
        self._log('info', '发射车/防空支援任务创建完成 %d/%d'
                  % (ok, len(self.CAR_SHIP_MISSIONS)))
        return ok

    # 北船1 / 北船2：**海域控制巡逻**（按选手要求新建）
    #   执行单元取自 CS 机场；初始"未启用"，激活时间 2027-05-21 04:25:00
    NORTH_SHIP_PATROLS = (
        ('北船1',
         [(54.092100, 5.451090), (53.726600, 6.153020),
          (54.092100, 6.153020)],
         ['F-2B型战斗机 #1', 'F-2A型战斗机  #1', 'F-2A型战斗机  #2']),
        ('北船2',
         [(53.389300, 6.639420), (53.389300, 7.490870),
          (52.945700, 6.639420)],
         ['F-2B型战斗机 #2', 'F-2A型战斗机  #3', 'F-2A型战斗机  #4']),
    )
    # 北船1/北船2 的激活时间（参考"潜艇跑"的写法：字符串 'MM/DD/YYYY HH:MM:SS'）
    NORTH_PATROL_START = '05/21/2027 04:25:00'

    def add_north_ship_patrols(self, situation):
        """
        创建 北船1 / 北船2 海域控制巡逻任务。

        要求：
          · 任务类型 = 海域控制巡逻（SEA_CONTROL）
          · 关闭"飞机数低于编队规模不能起飞"
          · 不勾选 1/3 规则、不勾选对巡逻区外探测目标分析、不勾选对武器射程内目标分析
          · 任务条令：对空自由开火
          · 初始状态"未启用"，激活时间 2027-05-21 04:25:00
          · 单元**开局就分配**（与"潜艇跑"一致）

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建数
        """
        ok = 0
        for name, pts, units in self.NORTH_SHIP_PATROLS:
            try:
                rule = self._patrol_rule_ext(
                    one_third_rule=False,
                    use_flight_size=False,
                    OPA=False,
                    WWR=False,
                    fuel_state_rtb=FuelStateRTB.No,
                    weapon_state_rtb=WeaponStateRTB.No,
                    ignore_plotted_course=IgnorePlottedCourseWhenAttacking.No)
                m = self.add_set_patrol_mission(
                    situation, name, MissionPatrolType.SEA_CONTROL,
                    pts, units,
                    rule=rule,
                    doctrine={'air': WeaponControlStatus.Free, 'radar': True},
                    time_lab=[self.NORTH_PATROL_START, None])
                if m is not None:
                    # 初始"未启用"
                    try:
                        m.mission_active(False)
                    except Exception as e:
                        self._log('error', '[%s] 设为未启用失败: %s' % (name, e))
                    ok += 1
                    self._log('info', '[%s] 已创建（海域控制巡逻），初始未启用，'
                                      '激活时间 %s' % (name, self.NORTH_PATROL_START))
            except Exception as e:
                self._log('error', '[%s] 创建异常: %s' % (name, e))
        self._log('info', '北船1/北船2 创建完成 %d/%d' % (ok, len(self.NORTH_SHIP_PATROLS)))
        return ok

    # 中1 / 中2：海域控制巡逻（16161616161616 / 61616161616161）
    #   ⚠️ 这一段曾被误删，导致 add_mid_patrols 报
    #      "AttributeError: 'Agent' object has no attribute 'MID_PATROLS'"，
    #      务必保留。
    MID_PATROLS = (
        ('16161616161616',
         [(47.764300, 1.516620), (47.764300, 1.984690),
          (47.481200, 1.984690), (47.481200, 1.516620)],
         ['F-16V型 BLK 70/72 “战隼”战斗机 #1',
          'F-16V型 BLK 70/72 “战隼”战斗机 #2',
          'F-16B 战隼20 战斗机 #1']),
        ('61616161616161',
         [(48.324300, 3.817310), (48.324300, 4.232590),
          (48.111000, 4.232590), (48.111000, 3.817310)],
         ['F-16V型 BLK 70/72 “战隼”战斗机 #3',
          'F-16V型 BLK 70/72 “战隼”战斗机 #4',
          'F-16B 战隼20 战斗机 #2']),
    )

    def add_mid_patrols(self, situation):
        """
        创建 中1 / 中2 对空巡逻任务。

        条令：关闭低于编队不能起飞、关闭 1/3、关闭 OPA/WWR；
        飞机出航油门=加速；对空/对海自由开火；
        关闭"攻击时忽略计划航线"；燃油/武器状态-返航=不返航。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建数
        """
        ok = 0
        for name, pts, units in self.MID_PATROLS:
            try:
                rule = self._patrol_rule_ext(
                    one_third_rule=False,
                    use_flight_size=False,
                    OPA=False,
                    WWR=False,
                    fuel_state_rtb=FuelStateRTB.No,
                    weapon_state_rtb=WeaponStateRTB.No,
                    ignore_plotted_course=IgnorePlottedCourseWhenAttacking.No)
                m = self.add_set_patrol_mission(
                    situation, name, MissionPatrolType.SEA_CONTROL, pts, units,
                    rule=rule,
                    doctrine={'air': WeaponControlStatus.Free,
                              'surface': WeaponControlStatus.Free,
                              'radar': True})
                if m is not None:
                    ok += 1
            except Exception as e:
                self._log('error', '[%s] 创建异常: %s' % (name, e))
        self._log('info', '中1/中2 巡逻任务创建完成 %d/%d' % (ok, len(self.MID_PATROLS)))
        return ok

    def add_mission_submarine_run(self, situation):
        """
        潜艇跑：支援任务（SSN 792 佛蒙特），激活时间 2027-05-21 04:02。

        条令：关闭 1/3；潜艇出航/阵位油门=加速；
        出航潜深 -30 米、阵位潜深 -150 米；关闭雷达。

        :param situation: tuple, (units dict, contacts dict)
        :return: Mission 或 None
        """
        rule = self._support_rule_ext(
            one_third_rule=False,
            # [出航油门, 阵位油门, 出航潜深, 阵位潜深]
            submarine_throttle_depth=(Throttle.Full, Throttle.Full, -30.0, -150.0))
        # 激活时间 2027-05-21 04:02:00
        # 注意：平台的 set_start 收的是**字符串** 'MM/DD/YYYY HH:MM:SS'
        # （源码：str_set = "starttime='%s'" % start_time），
        # 之前传毫秒整数是错的，UI 上会显示成 9999-12-31。
        start_str = '05/21/2027 04:02:00'
        m = self.add_set_support_mission(
            situation, "潜艇跑",
            [(48.859100, -6.431250), (48.970600, -6.166930)],
            rule, ['SSN-792 浮蒙特号攻击核潜艇 #1'],
            doctrine={'radar': False},
            time_lab=[start_str, None])
        # 注意：任务本身"初始未启用"，但单元**开局就分配进去**
        # （选手要求：开局就把它分配到潜艇跑任务里）
        # 按要求：初始状态"未启用"
        if m is not None:
            try:
                m.mission_active(False)
                self._log('info', '潜艇跑 已设为"初始未启用"，激活时间 %s' % start_str)
            except Exception as e:
                self._log('error', '潜艇跑 设为未启用失败: %s' % e)
        return m

    # ==================================================================
    # 米卡（对空巡逻 AAW） / 航母杀手（反水面及地面战巡逻 SUR_MIXED）
    #
    #   两个任务都按要求"开局立刻启用"，并且：
    #     · 不额外下发任何 WRA（单元级也不发），尽量少占用指令配额；
    #     · 米卡 的 5 架单元从原来的 "C" 支援任务里划走（C 只留 RQ-180）。
    #
    #   ⚠️ 平台限制：**巡逻任务没有"仅限一次"开关**。
    #      proto 里 PatrolMissionConfig 只有 patrolZones/onStationCount/activeEMCON；
    #      只有支援任务(setMissionSupportLoopType 的 "1"=仅一次)和
    #      打击任务(strikeOneTimeOnly)才有一次性设置。故这两个任务只能建成常驻巡逻。
    # ==================================================================
    MIKA_NAME = '米卡'
    # 四个参考点（纬度, 经度）
    MIKA_AREA = [(47.559100, 3.272760), (47.559100, 4.084360),
                 (47.065600, 4.084360), (47.065600, 3.272760)]
    # 奥尔良机场：幻影-2000-5EI #1~#4 + RQ-4B 全球鹰 #1（这 5 架从 C 任务划出）
    MIKA_UNITS = ['幻影-2000-5EI战斗机 #1', '幻影-2000-5EI战斗机 #2',
                  '幻影-2000-5EI战斗机 #3', '幻影-2000-5EI战斗机 #4',
                  'RQ-4B型”全球鹰“无人机 #1']

    CARRIER_KILLER_NAME = '航母杀手'
    # 三个参考点（纬度, 经度）
    CARRIER_KILLER_AREA = [(47.320200, -6.620270), (47.320200, -5.354710),
                           (46.834800, -5.354710)]
    # 执行单元：SSN 792“佛蒙特”号弗吉尼亚级核动力隐形潜艇
    #   单元名不写死，改用关键字在态势里解析真实名称 —— 该艇名里既有全角引号
    #   又有"佛蒙特"（旧代码曾误写成"浮蒙特"，导致整条任务命中 0 个单元）。
    CARRIER_KILLER_UNIT_KEYS = ('佛蒙特', 'SSN 792')
    # 潜艇 出航/阵位/攻击 潜深（米，负值）
    CARRIER_KILLER_DEPTH = -180.0

    def _names_matching_keywords(self, situation, keywords):
        """
        在态势里按关键字取出单元的**真实名称**（避免手写名称不匹配）。

        :param situation: tuple, (units dict, contacts dict)
        :param keywords: tuple, 名称关键字
        :return: list, 命中的真实单元名（去重、保持态势顺序）
        """
        units = situation[0] if isinstance(situation[0], dict) else {}
        out = []
        for _, u in units.items():
            if not isinstance(u, dict):
                continue
            nm = str(u.get('name', ''))
            if nm and any(k in nm for k in keywords) and nm not in out:
                out.append(nm)
        return out

    def add_mission_mika(self, situation):
        """
        米卡：对空巡逻任务（AAW），开局立刻启用。

        任务编辑：关闭"飞机数低于编队规模不能起飞"/1/3 规则/
                  对巡逻区外目标分析/对武器射程内探测目标分析。
        （这四项正是 PATROL_RULE_BASE 的默认值，故直接用 _patrol_rule_ext()。）

        按要求：不设单元级条令、不发任何 WRA，尽量少占用指令配额。

        :param situation: tuple, (units dict, contacts dict)
        :return: PatrolMission 或 None
        """
        m = self.add_set_patrol_mission(
            situation, self.MIKA_NAME, MissionPatrolType.AIR, self.MIKA_AREA,
            self.MIKA_UNITS,
            rule=self._patrol_rule_ext(),
        )
        if m is not None:
            try:
                m.mission_active(True)      # 开局立刻启用
            except Exception as e:
                self._log('error', '米卡 设为启用失败: %s' % e)
        return m

    def add_mission_carrier_killer(self, situation):
        """
        航母杀手：反水面及地面战巡逻任务（SUR_MIXED = MissionPatrolType.ANTI_MLP），
        开局立刻启用。

        任务编辑：关闭"飞机数低于编队规模不能起飞"/1/3 规则/
                  对巡逻区外目标分析/对武器射程内探测目标分析；
                  潜艇 出航/阵位/攻击 油门 = 最大（Flank）；
                  潜艇 出航/阵位/攻击 潜深 = -180 米。
        条令：对海自由开火。
        按要求：不发任何 WRA。

        :param situation: tuple, (units dict, contacts dict)
        :return: PatrolMission 或 None
        """
        # 用关键字解析真实单元名（该艇名含全角引号，写死容易不匹配）
        units = self._names_matching_keywords(situation, self.CARRIER_KILLER_UNIT_KEYS)
        if not units:
            self._log('warning', '%s 未找到潜艇单元（关键字=%s），任务跳过'
                      % (self.CARRIER_KILLER_NAME, self.CARRIER_KILLER_UNIT_KEYS))
            return None
        rule = self._patrol_rule_ext(
            # [出航油门, 阵位油门, 攻击油门, 出航潜深, 阵位潜深, 攻击潜深]
            submarine_throttle_depth=(Throttle.Flank, Throttle.Flank, Throttle.Flank,
                                      self.CARRIER_KILLER_DEPTH,
                                      self.CARRIER_KILLER_DEPTH,
                                      self.CARRIER_KILLER_DEPTH))
        m = self.add_set_patrol_mission(
            situation, self.CARRIER_KILLER_NAME, MissionPatrolType.ANTI_MLP,
            self.CARRIER_KILLER_AREA, units,
            rule=rule,
            doctrine={'surface': WeaponControlStatus.Free},
        )
        if m is not None:
            try:
                m.mission_active(True)      # 开局立刻启用
            except Exception as e:
                self._log('error', '%s 设为启用失败: %s'
                          % (self.CARRIER_KILLER_NAME, e))
        return m

    @staticmethod
    def _utc_ms(y, mo, d, h=0, mi=0, sec=0):
        """把 UTC 日期时间转成"1970 起的毫秒"（平台 START/END 用这个格式）。"""
        import calendar
        import datetime
        dt = datetime.datetime(y, mo, d, h, mi, sec,
                               tzinfo=datetime.timezone.utc)
        return int(calendar.timegm(dt.utctimetuple())) * 1000

    # 装甲车队：**直接奔终点、最高速度**（已按要求去掉必须经过的途经点）
    ARMOR_SPEED_KMH = 40      # 期望速度（实际油门用最大 Flank，见下）
    ARMOR_CONVOYS = (
        (['装甲车#1', '伪装防空车#1', '装甲车#5'],
         [], (49.313146, -1.173154)),
        (['装甲车#4', '伪装防空车#2', '装甲车#2'],
         [], (49.249247, -0.055300)),
        (['装甲车#3'], [], (49.906043, 1.229555)),
    )

    def set_armor_convoy_courses(self, situation):
        """
        给装甲车/伪装防空车直接规划航线（中途点 -> 终点），
        **油门设为最大（加速）**，并关闭自动规避。

        这些是地面车辆：用 plotted_course 直接下航路，再把油门开到最大、
        关掉自动规避（免得它们自己乱绕）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功处理的单元数
        """
        ok = 0
        for names, mid, dest in self.ARMOR_CONVOYS:
            course = list(mid) + [dest]
            for nm in names:
                try:
                    found = self._find_units_by_exact_name([nm])
                    if not found:
                        self._log('warning', '装甲车队[%s] 未匹配到单元' % nm)
                        continue
                    for uname, obj in found:
                        obj.plotted_course(course)
                        # 油门最大（加速）
                        try:
                            obj.set_throttle(Throttle.Flank)
                        except Exception:
                            pass
                        try:
                            obj.set_desired_speed(self.ARMOR_SPEED_KMH)
                        except Exception:
                            pass
                        # 关闭自动规避
                        try:
                            obj.doctrine_automatic_evasion(AutomaticEvasion.No)
                        except Exception:
                            pass
                        ok += 1
                        self._log('info', '装甲车[%s] 航线已规划+油门最大 -> %s'
                                  % (uname, course))
                except Exception as e:
                    self._log('error', '装甲车[%s] 航线规划失败: %s' % (nm, e))
        self._log('info', '装甲车队航线规划完成 %d 辆' % ok)
        return ok

    # 开局"猛冲"单元表：(**精确单元名**, 目标点, 是否关雷达)
    #
    #   🔴 必须用**精确名**匹配，不能用关键字！
    #      曾经用关键字 '地空导弹连#2'，结果同时命中了
    #      **霍克地空导弹连#2**（名字里含该子串），把它也一起猛冲了 ——
    #      而霍克地空导弹连#2 应该是"原地不动、关雷达"的。
    #
    #   ⚠️ 按要求：**地空导弹连#2 已从本表移除** —— 它不再开局前往旧的参考点，
    #      改为直接分配进"右"防空支援任务（见 CAR_SHIP_MISSIONS 的 '右'，
    #      对空自由开火 + 初始关雷达的效果保持不变）。
    RUSH_UNITS = (
        # 海马斯火箭炮#4：目标点按要求改为 (50.960142, 2.364601)
        #   （原目标点 (50.940821, 2.392699) 作废）
        ('海马斯火箭炮#4', (50.960142, 2.364601), False),
        ('反舰导弹排#5', (49.034269, 0.250846), False),
        # DDG 179 摩耶级驱逐舰：最大航速前往，不关雷达
        # （精确匹配会忽略空格，写成 'DDG 179摩耶级驱逐舰' 也能命中）
        ('DDG 179 摩耶级驱逐舰', (53.142707, 4.088746), False),
    )

    def initial_rush_units(self, situation):
        """
        开局让指定单元**以最大速度**机动到指定点（可选关雷达）。

        ⚠️ 用**精确名**匹配：关键字匹配会误伤同名前缀的单元
        （如 '地空导弹连#2' 会命中 '霍克地空导弹连#2'）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功处理的单元数
        """
        ok = 0
        for name, target, radar_off in self.RUSH_UNITS:
            found = self._find_units_by_exact_name([name])
            if not found:
                self._log('warning', '猛冲[%s] 未匹配到单元（跳过）' % name)
                continue
            for uname, obj in found:
                if radar_off:
                    try:
                        obj.switch_radar(False)
                        self._log('info', '猛冲[%s] 雷达已关闭' % uname)
                    except Exception as e:
                        self._log('error', '猛冲[%s] 关雷达失败: %s' % (uname, e))
                try:
                    obj.plotted_course([target])
                    try:
                        obj.set_throttle(Throttle.Flank)
                    except Exception:
                        pass
                    try:
                        obj.doctrine_automatic_evasion(AutomaticEvasion.No)
                    except Exception:
                        pass
                    ok += 1
                    self._log('info', '猛冲[%s] 已规划航线 + 油门最大 -> %s'
                              % (uname, (target,)))
                except Exception as e:
                    self._log('error', '猛冲[%s] 机动失败: %s' % (uname, e))
        self._log('info', '开局猛冲单元处理完成 %d 个' % ok)
        return ok

    # ==================================================================
    # 扫地#1（反地面战巡逻） / 扫地#2（对陆打击）
    # ==================================================================
    # 扫地#1：反地面战巡逻任务（开局启动，**暂不加入执行单元**）
    SWEEP1_NAME = '扫地#1'
    SWEEP1_AREA = [(50.438400, -6.957500), (50.438400, -6.157030),
                   (50.160800, -6.157030), (50.160800, -6.957500)]
    # 扫地#2：对陆打击任务（开局启动，**暂不加入执行单元**）
    #   ⚠️ 按要求：**该任务没有参考点**，直接创建即可（不要设警戒区）。
    SWEEP2_NAME = '扫地#2'

    def add_sweep_missions(self, situation):
        """
        新建两个对地任务（开局启动，均**不加入执行单元**，由选手后续手动转入）：

          扫地#1：**反地面战巡逻任务**（MissionPatrolType.ANTI_LAND）
                  关闭 低于编队规模不起飞 / 1/3 规则 / 巡逻区外分析 / 武器射程内分析
                  任务条令：对地自由开火
          扫地#2：**对陆打击任务**（MissionStrikeType.LAND）
                  关闭 低于编队规模不起飞 / 包括在空中任务指令中
                  任务条令：对地自由开火

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        ok = 0

        # ---------------- 扫地#1：反地面战巡逻 ----------------
        try:
            m1 = self.add_set_patrol_mission(
                situation, self.SWEEP1_NAME, MissionPatrolType.ANTI_LAND,
                self.SWEEP1_AREA,
                [],                       # 暂不加入执行单元
                rule=self._patrol_rule_ext(
                    one_third_rule=False,       # 关闭 1/3 规则
                    use_flight_size=False,      # 关闭 低于编队规模不起飞
                    OPA=False,                  # 关闭 对巡逻区外探测目标分析
                    WWR=False,                  # 关闭 对武器射程内探测目标分析
                    # 任务条令：对地自由开火
                    land=WeaponControlStatus.Free,
                ),
            )
            if m1 is not None:
                ok += 1
        except Exception as e:
            self._log('error', '创建任务[%s]失败: %s' % (self.SWEEP1_NAME, e))

        # ---------------- 扫地#2：对陆打击 ----------------
        try:
            m2 = self.create_strike_mission(self.SWEEP2_NAME,
                                            MissionStrikeType.LAND)
            if m2 is not None:
                self._remember_mission(m2)
                # 关闭"飞机数低于编组规模数不能起飞"
                for fn, val in (('strike_setStrikeUseFlightSize', False),
                                # 关闭"包含在空中任务指令中"
                                ('set_includeInATO', False)):
                    setter = getattr(m2, fn, None)
                    if callable(setter):
                        try:
                            setter(val)
                        except Exception as e:
                            self._log('warning', '任务[%s] %s(%s) 失败: %s'
                                      % (self.SWEEP2_NAME, fn, val, e))
                    else:
                        self._log('warning', '任务[%s] 无接口 %s（跳过）'
                                  % (self.SWEEP2_NAME, fn))
                # 任务条令：对地自由开火
                try:
                    m2.doctrine_weapon_control_status_land(
                        WeaponControlStatus.Free)
                except Exception as e:
                    self._log('warning', '任务[%s] 对地自由开火设置失败: %s'
                              % (self.SWEEP2_NAME, e))
                # ⚠️ 扫地#2 **不设参考点**（按选手更正：该任务直接创建即可）
                self._log('info', '打击任务[%s] 已创建（对陆，未分配单元，无参考点）'
                          % self.SWEEP2_NAME)
                ok += 1
            else:
                self._log('error', '创建打击任务失败：%s' % self.SWEEP2_NAME)
        except Exception as e:
            self._log('error', '创建任务[%s]失败: %s' % (self.SWEEP2_NAME, e))

        self._log('info', '扫地任务创建完成 %d/2' % ok)
        return ok

    # ==================================================================
    # 初始 BOL 纯防卫打击（战斧 / 卢卡斯无人机）
    #   目标点固定；武器按型号指定；数量取该单元该型武器的可用量。
    # ==================================================================
    BOL_STRIKES = (
        # (单元名关键字, 目标点, 武器DBID, 说明, 发射数量)
        #   目标点写法：
        #     (lat, lon)                     -> 全部弹都打这一个点
        #     [((lat,lon), 数量), ...]        -> 每个点按指定数量发（可精确分配）
        #     (lat, lon, 数量)                -> 同上，单点带数量
        #   发射数量为 None 时用该单元该型武器的可用量。
        #
        # ⚠️ 平台里潜艇的单元名是
        #    「SSN 792“佛蒙特”号弗吉尼亚级核动力隐形潜艇」（没有连字符！）
        #    之前写 'SSN-792' 永远匹配不到，日志一直是
        #    "BOL[SSN-792] 未匹配到单元，跳过"。
        #   🔴 武器清单必须**列全潜射战斧各型号**：原先只写 ('377',)，
        #      于是只按 UGM-109E 的 12 发打，艇上其它型号（UGM-109C/D/H/I 等，
        #      合计 16 发）一发没动。_find_weapons_on_unit 只会挑"艇上真有的"，
        #      所以列全不会误触发。
        ('佛蒙特', (47.504157, -6.164696),
         ('377', '810', '1165', '1180', '2942', '2943',
          '378', '379', '380', '382', '808', '809', '811', '812'),
         '潜艇 战斧（各型号）', None),
        # 邦克山：**两个坐标点**，都**必须途经** (50.338666, -8.318062)
        #   然后继续飞向各自的目标点（航线的末点由 _bol_attack 自动补成目标点）。
        #   ⚠️ 为什么必须给航路点（course）：战斧是巡航导弹，有航线才会沿航线飞；
        #      不给航路点时平台把它当"就地激活"，界面上就会不断刷
        #      "已重定向到新目标"。
        #   🔴 平台实际装载（挂架 3017 的挂载诊断，日志实证）：
        #     weapon 586  = RGM-109E 型“战斧”巡航导弹 Blk IV   **只有 4 发**
        #     weapon 1131 = RGM-109C 型“战斧”巡航导弹 Blk III  **只有 4 发**
        #     所以 qty 用 None（= 把该型弹全部打出去），不要写死 8。
        #   拆成两条是为了让两型弹各打各自的点（每条单独指定武器）。
        ('邦克山', [{'pt': (51.478738, -1.355596), 'qty': None,
                     'course': [(50.338666, -8.318062)]}],
         ('586',), '巡洋舰 RGM-109E 战斧', None),
        ('邦克山', [{'pt': (51.986462, -1.088081), 'qty': None,
                     'course': [(50.338666, -8.318062)]}],
         ('1131',), '巡洋舰 RGM-109C Blk III 战斧', None),
        # 阿利伯克（40 发一次打完，按目标点 28 / 12 分配）：
        #   平台实际装载：RGM-109E(586) 共 24 发 + RGM-109I MMT(2941) 共 16 发 = 40 发
        #
        #   ① 打 (51.478738,-1.355596)：**28 发**
        #        = 586 全部 24 发 + 2941 中的 4 发
        #        途经 (50.338666,-8.318062)
        #   ② 打 (50.572223,-3.642392)：**12 发**
        #        = 2941 中剩下的 12 发
        #        途经 (48.414187,-8.320517)
        #
        #   🔴 为什么要写成"同型弹分两条"：
        #      上一版把 2941 一次性给了一个点（16 发），现在要把 2941 拆成 4+12。
        #      因为 _find_weapons_on_unit 已按**武器**合并（不再按挂架拆），
        #      每条只发**一次**指令、qty 明确，平台才会按数量一次分配完 ——
        #      这正是之前"分挂架发两次、后一条被丢掉"的教训。
        #      三条指令互不重复（武器/目标点任一不同即视为不同），不会被去重。
        ('阿利伯克', [{'pt': (51.478738, -1.355596),
                       'course': [(50.338666, -8.318062)]}],
         ('586',), '驱逐舰 RGM-109E 战斧 24发->点1', 24),
        ('阿利伯克', [{'pt': (51.478738, -1.355596),
                       'course': [(50.338666, -8.318062)]}],
         ('2941',), '驱逐舰 RGM-109I MMT 4发->点1', 4),
        ('阿利伯克', [{'pt': (50.572223, -3.642392),
                       'course': [(48.414187, -8.320517)]}],
         ('2941',), '驱逐舰 RGM-109I MMT 12发->点2', 12, False, '2804'),
        # LUCAS 无人机发射车#3 按要求打满 18 发
        ('LUCAS 无人机发射车#3', (49.157179, -2.783497), ('150001', '50001'),
         'LUCAS 卢卡斯无人机', 18),
        # LUCAS 无人机发射车#1 开局纯方位打击，18 发全射
        #   （目标点按要求改为 (51.438343, 1.870959)，其余不变）
        ('LUCAS 无人机发射车#1', (51.438343, 1.870959), ('150001', '50001'),
         'LUCAS 卢卡斯无人机#1', 18),
        # 地地导弹排#2：先经过 (48.029704,-1.732429)，再折向终点 (50.572223,-3.642392)
        #   （航线的末点由 _bol_attack 自动补成目标点），8 发全射
        ('地地导弹排#2', [{'pt': (50.572223, -3.642392), 'qty': 8,
                           'course': [(48.029704, -1.732429)]}],
         ('3228',), '地地导弹排#2', None),
        # 地地导弹排#1：**暂时去掉途经点**，直接对 (50.940457,0.925167) 纯方位打击，
        #   8 发全射。
        #   （原因：带途经点时导弹"越过去了"没打中终点，先做直打对照实验。
        #     若直打能命中，说明问题出在航路点与终点的配合上。）
        ('地地导弹排#1', (50.940457, 0.925167),
         ('3228',), '地地导弹排#1', 8),
    )

    @staticmethod
    def _normalize_bol_targets(targets):
        """
        把 BOL 目标点写法统一成 [{'pt':(lat,lon), 'qty':数量或None,
        'course':[(lat,lon),...] 或 []}, ...]。

        支持的写法：
            (lat, lon)                          -> 单点、默认数量、无航迹点
            (lat, lon, 数量)                    -> 单点、指定数量
            [(lat, lon), (lat2, lon2)]          -> 多点、默认数量
            [((lat, lon), 数量), ...]           -> 多点、每点指定数量
            [{'pt':(lat,lon), 'qty':n,
              'course':[(la,lo),...]}, ...]     -> 完整写法（含导弹航迹规划点）

        :param targets: 见上
        :return: list, [{'pt':(lat,lon), 'qty':int或None, 'course':list}, ...]
        """
        out = []
        if isinstance(targets, dict):
            targets = [targets]

        def _one(item):
            # 字典写法
            if isinstance(item, dict):
                pt = item.get('pt')
                if not pt:
                    return None
                crs = []
                for c in (item.get('course') or []):
                    if isinstance(c, (list, tuple)) and len(c) >= 2:
                        crs.append((float(c[0]), float(c[1])))
                q = item.get('qty')
                return {'pt': (float(pt[0]), float(pt[1])),
                        'qty': int(q) if q else None,
                        'course': crs}
            if isinstance(item, (list, tuple)):
                # ((lat,lon), qty)
                if item and isinstance(item[0], (list, tuple)):
                    pt = item[0]
                    q = item[1] if len(item) > 1 else None
                    return {'pt': (float(pt[0]), float(pt[1])),
                            'qty': int(q) if q else None, 'course': []}
                # (lat, lon, qty?, course?)
                if len(item) >= 2:
                    q = item[2] if len(item) > 2 else None
                    crs = []
                    if len(item) > 3 and isinstance(item[3], (list, tuple)):
                        for c in item[3]:
                            if isinstance(c, (list, tuple)) and len(c) >= 2:
                                crs.append((float(c[0]), float(c[1])))
                    return {'pt': (float(item[0]), float(item[1])),
                            'qty': int(q) if q else None, 'course': crs}
            return None

        if isinstance(targets, (list, tuple)) and targets and \
                isinstance(targets[0], (list, tuple, dict)):
            for item in targets:
                r = _one(item)
                if r:
                    out.append(r)
        else:
            r = _one(targets)
            if r:
                out.append(r)
        return out

    @staticmethod
    def _bins_for_groups(plans, n):
        """
        把若干"挂架×武器"组按**整组**尽量平均地分到 n 个桶里。

        用于 BOL 的 A 方案：不把数量拆成小批，而是整组分配给各目标点，
        使各点的总弹数尽量接近（大组优先，放到当前总数较小的桶里）。

        :param plans: list, [{'mount':..,'weapon':..,'count':..}, ...]
        :param n: int, 桶数（目标点数）
        :return: list, 长度为 n，每个元素是该桶分到的 plan 列表
        """
        n = max(1, int(n))
        bins = [[] for _ in range(n)]
        totals = [0] * n
        for p in sorted(plans, key=lambda x: -int(x.get('count') or 0)):
            i = totals.index(min(totals))
            bins[i].append(p)
            totals[i] += int(p.get('count') or 0)
        return bins

    def initial_bol_strikes(self, situation):
        """
        初始执行 BOL 纯防卫打击。

        潜艇先调整到 +20 米再发射（浅水才允许发射）。

        说明：这里**不设置导弹航迹规划点**（course 留空），只做纯方位打击。
        目标点可以是单个 (lat, lon)，也可以是列表（如邦克山打两个点，
        每个点各发一轮）。
        发射数量：BOL_STRIKES 里给了具体数字就用它（如 LUCAS=18），
        否则用该单元该型武器的可用量。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功发起的 BOL 次数
        """
        fired = 0
        # 成功清单：{'单元名|武器|lat|lon': True}
        done = getattr(self, '_ly_bol_done_keys', None)
        if not isinstance(done, dict):
            done = {}
            self._ly_bol_done_keys = done
        # 潜艇"已交还深度控制权"标记：{'单元名': True}
        #   BOL 期间必须浅水（否则浅水发射失败），故用 set_alt_manual(True) 把
        #   潜艇按在 SUB_BOL_DEPTH；BOL 全部结束后必须 set_alt_manual(False)
        #   交还控制权，**任务里的潜深/油门才会生效**。
        #   🔴 曾经漏掉交还这一步，结果潜艇永远停在 -20 米手动控制，
        #      任务里的 -180 米潜深与最大油门始终不生效。
        released = getattr(self, '_ly_sub_depth_released', None)
        if not isinstance(released, dict):
            released = {}
            self._ly_sub_depth_released = released
        # 本周期各单元是否还有"未完成的 BOL"（决定能不能交还深度控制权）
        pend = {}
        subs_seen = {}
        # 潜艇：本局是否**成功**打出过 BOL（**必须跨周期保留**！
        #   写成局部变量的话，下一周期 sub_ok 为空 -> 会被当成"还没打出去"，
        #   于是一直按住浅水直到兜底上限，永远不交还深度控制权。）
        sub_ok = getattr(self, '_ly_sub_bol_ok', None)
        if not isinstance(sub_ok, dict):
            sub_ok = {}
            self._ly_sub_bol_ok = sub_ok
        # 潜艇上一周期深度（**必须跨周期保留**，否则"是否稳定"永远判不出来）
        prev_alt = getattr(self, '_ly_sub_prev_alt', None)
        if not isinstance(prev_alt, dict):
            prev_alt = {}
            self._ly_sub_prev_alt = prev_alt
        hold = getattr(self, '_ly_sub_bol_hold', None)   # 潜艇被按住浅水的周期数
        if not isinstance(hold, dict):
            hold = {}
            self._ly_sub_bol_hold = hold
        # 潜艇"打出 BOL 之后"已在浅水待机的周期数
        fire_hold = getattr(self, '_ly_sub_fire_hold', None)
        if not isinstance(fire_hold, dict):
            fire_hold = {}
            self._ly_sub_fire_hold = fire_hold
        for _entry in self.BOL_STRIKES:
            # 兼容 5 元组 / 6 元组 / 7 元组
            #   第 6 位 = distribute（整组分配开关）
            #   第 7 位 = mount_hint（强制使用的挂架 DBID；用于让"同型弹打不同目标"
            #             的两条指令落在**不同挂架**上，避免平台把后一条当重复丢掉）
            key, targets, wids, desc, want_qty = _entry[:5]
            distribute = bool(_entry[5]) if len(_entry) > 5 else False
            mount_hint = _entry[6] if len(_entry) > 6 else None
            # 目标点归一化成 [((lat,lon), 数量或None), ...]
            pts = self._normalize_bol_targets(targets)
            try:
                found = self._find_units_by_keywords_any(situation, [key])
                if not found:
                    self._log('warning', 'BOL[%s] 未匹配到单元，跳过' % key)
                    continue
                for name, obj in found:
                    # 潜艇：BOL 期间先按到浅水深度（>约 45m 浅水发射会失败）；
                    #        已交还控制权的就不再干预，任务里的潜深自己生效。
                    is_sub = ('SSN' in name or '潜艇' in name)
                    if is_sub:
                        subs_seen[name] = obj
                        # 已交还控制权 -> 不再干预（否则会每周期白刷日志）
                        if not released.get(name):
                            self._set_sub_depth(obj, self.SUB_BOL_DEPTH)
                            # 🔴 必须等它**真的上浮到位、而且稳下来**再打 BOL：
                            #    ① 剧本里潜艇开局就 -132.7 米，上浮指令发出去后
                            #       立刻打，弹出不来（平台回"指令执行成功"但没发射）；
                            #    ② 实测"还在上浮途中就打"只出去 7/12 发 ——
                            #       所以还要求两周期之间深度基本不变（稳住）再打。
                            _alt = getattr(obj, 'CurrentAltitude', None)
                            try:
                                _alt = None if _alt is None else float(_alt)
                            except (TypeError, ValueError):
                                _alt = None
                            _prev = prev_alt.get(name)
                            prev_alt[name] = _alt
                            _deep = (_alt is not None
                                     and _alt < -self.SUB_BOL_READY_DEPTH)
                            _moving = (_alt is not None and _prev is not None
                                       and abs(_alt - _prev) > self.SUB_BOL_STABLE_M)
                            if _deep or _moving:
                                pend[name] = pend.get(name, 0) + 1
                                _why = ('还没上浮到 -%d 米以内' % self.SUB_BOL_READY_DEPTH
                                        if _deep else '还在上浮/下潜中，未稳定')
                                self._log('info',
                                          '潜艇[%s] 当前 %.1f 米（%s），'
                                          '本周期先不打 BOL（下周期再试）'
                                          % (name,
                                             _alt if _alt is not None else 0.0, _why))
                                continue
                    # 潜艇给足重试次数（其它单元仍是 BOL_MAX_TRIES=1）
                    max_tries = (self.SUB_BOL_MAX_TRIES if is_sub
                                 else self.BOL_MAX_TRIES)
                    plans = self._find_weapons_on_unit(obj, wids)
                    # 挂架覆盖：让本条的指令固定用指定挂架下发
                    if mount_hint is not None and plans:
                        _mh = int(mount_hint)
                        plans = [dict(p, mount=_mh) for p in plans]
                    if not plans:
                        # 只警告一次，避免每周期刷屏（日志里曾每 3 秒刷一次）
                        nk = 'NOWEAPON|%s|%s' % (name, wids)
                        if not done.get(nk):
                            done[nk] = True
                            self._log('warning',
                                      'BOL[%s] 该单元未发现指定武器 %s（不再重复提示）'
                                      % (name, wids))
                        continue
                    # ---- A 方案：整组（挂架×武器）分配 ----
                    #   不把数量拆成小批，而是把探测到的每个"挂架×武器"组
                    #   按**整组**尽量平均地分给各个目标点，每组按自己的
                    #   全部存量发射。这样平台一次就能分配完，不会出现
                    #   "打了 3 发、剩下的没出去"。
                    if distribute and len(pts) > 1 and plans:
                        bins = self._bins_for_groups(plans, len(pts))
                        for spec_t, p_list in zip(pts, bins):
                            (lat, lon) = spec_t['pt']
                            course = spec_t.get('course') or []
                            for p in p_list:
                                k = '%s|%s|%s|%.6f|%.6f' % (name, p['mount'],
                                                            p['weapon'], lat, lon)
                                if done.get(k):
                                    continue
                                tries = done.get('TRIES|' + k, 0)
                                if tries >= max_tries:
                                    done[k] = True
                                    continue
                                done['TRIES|' + k] = tries + 1
                                qty = p['count']
                                res = self._bol_attack(obj, lat, lon, p['mount'],
                                                       p['weapon'], qty, course)
                                okc = self._reply_ok(res)
                                if okc:
                                    done[k] = True
                                    fired += 1
                                    sub_ok[name] = True
                                elif tries + 1 >= max_tries:
                                    done[k] = True
                                else:
                                    # 本周期没打成，下周期还要重试 -> 视为"未完成"
                                    pend[name] = pend.get(name, 0) + 1
                                self._log('info', 'BOL[%s] %s 发射 %s x%d 挂架=%s -> '
                                                  '(%.6f, %.6f) 航线=%d点 %s'
                                          % (name, desc, p['name'], qty, p['mount'],
                                             lat, lon, len(course) + (1 if course else 0),
                                             '成功' if okc else '失败'))
                        continue
                    for spec_t in pts:
                        (lat, lon) = spec_t['pt']
                        per_qty = spec_t['qty']
                        course = spec_t.get('course') or []
                        # 目标点自带数量时：把该数量**按武器型号平均拆分**
                        #   （如 8 发、2 种战斧 -> 每种 4 发），
                        #   这样 RGM-109C 与 RGM-109E 都会打出去。
                        #   🔴 之前写成 plans[:1]（只取第一种），
                        #      导致"每次纯方位只打出去 109E"。
                        if per_qty:
                            _share = max(1, per_qty // max(1, len(plans)))
                            use_plans = [(p, _share) for p in plans]
                        else:
                            use_plans = [(p, None) for p in plans]
                        for p, _pq in use_plans:
                          # 去重键：单元|**挂架**|武器|目标点 都相同才算"已打过"。
                          # 🔴 必须带挂架号：同型武器可能装在多个**不同 DBID**的
                          #    挂架上（如阿利伯克的 Mk41 有 2803/2804 两个），
                          #    不带挂架号就会把后一个挂架的去重掉，只发一次。
                          k = '%s|%s|%s|%.6f|%.6f' % (name, p['mount'],
                                                       p['weapon'], lat, lon)
                          if done.get(k):
                              continue
                          # 🔴 尝试次数上限：BOL 打出去之后，后续重试只会得到
                          #    "无可用武器"之类的失败。若失败就无限重试，会变成
                          #    **每 1~2 秒重复攻击一次**（界面上刷满"有一个要重定向的
                          #    备选目标"），把指令配额吃光，导致海马斯等 WRA 全被丢弃。
                          tries = done.get('TRIES|' + k, 0)
                          if tries >= max_tries:
                              done[k] = True          # 放弃，不再打扰
                              continue
                          done['TRIES|' + k] = tries + 1
                          # 目标点自带数量（已按型号拆分） > 武器级数量 > 可用量
                          qty = _pq or want_qty or p['count']
                          res = self._bol_attack(obj, lat, lon, p['mount'],
                                                 p['weapon'], qty, course)
                          okc = self._reply_ok(res)
                          if okc:
                              done[k] = True
                              fired += 1
                              sub_ok[name] = True
                          elif tries + 1 >= max_tries:
                              # 最后一次也没成功 -> 标记完成，停止重试
                              done[k] = True
                              self._log('warning',
                                        'BOL[%s] %s 尝试 %d 次仍失败，放弃重试'
                                        % (name, desc, tries + 1))
                          else:
                              self._log('warning',
                                        'BOL[%s] %s %s x%d -> (%.6f,%.6f) 本次未成功'
                                        '（第 %d/%d 次，下周期再试）'
                                        % (name, desc, p['name'], qty, lat, lon,
                                           tries + 1, max_tries))
                              # 本周期没打成，下周期还要重试 -> 视为"未完成"
                              pend[name] = pend.get(name, 0) + 1
                          self._log('info', 'BOL[%s] %s 发射 %s x%d 挂架=%s -> '
                                            '(%.6f, %.6f) 航迹点=%d %s'
                                    % (name, desc, p['name'], qty, p['mount'],
                                       lat, lon, len(course),
                                       '成功' if okc else '失败'))
            except Exception as e:
                self._log('error', 'BOL[%s] 执行异常: %s' % (key, e))
        # ---------------- 潜艇：BOL **打出去之后**才交还深度控制权 ----------------
        #   🔴 顺序要求：潜艇必须先在 -20 米把 BOL 打出去，之后才能让
        #      "航母杀手"任务的 -180 米潜深接管 —— 否则一下潜就再也打不出 BOL 了。
        #   交还条件（满足其一）：
        #     · BOL 已成功，**并且在浅水多待满 SUB_BOL_HOLD_AFTER_FIRE_CYCLES 个周期**
        #       （实测立刻下潜时 16 发只出去 7 发 —— 平台需要时间把筒里的弹放完，
        #        所以打出后继续在 -20 米待机约 3 倍时长，再交还控制权）；
        #     · 已按住浅水 SUB_BOL_HOLD_MAX_CYCLES 个周期（兜底，避免永远不放行）。
        #   仍在重试、或一次都没成功时，继续按住浅水。
        for name, obj in subs_seen.items():
            if released.get(name):
                continue
            n = hold.get(name, 0) + 1
            hold[name] = n
            if sub_ok.get(name):
                # 打出去了：还要在浅水待机几个周期，让弹全部出筒
                fh = fire_hold.get(name, 0) + 1
                fire_hold[name] = fh
                if fh < self.SUB_BOL_HOLD_AFTER_FIRE_CYCLES:
                    self._log('info', '潜艇[%s] BOL 已打出，继续在浅水 %d 米待机 '
                                      '%d/%d 个周期（把弹放完再下潜）'
                              % (name, self.SUB_BOL_DEPTH, fh,
                                 self.SUB_BOL_HOLD_AFTER_FIRE_CYCLES))
                    continue
            elif pend.get(name) and n < self.SUB_BOL_HOLD_MAX_CYCLES:
                self._log('info', '潜艇[%s] BOL 还没打出去（第 %d 周期），'
                                  '继续保持在浅水 %d 米'
                          % (name, n, self.SUB_BOL_DEPTH))
                continue
            elif n < self.SUB_BOL_HOLD_MAX_CYCLES:
                self._log('info', '潜艇[%s] BOL 尚未成功（第 %d 周期），'
                                  '暂不交还深度控制权（最多等 %d 个周期）'
                          % (name, n, self.SUB_BOL_HOLD_MAX_CYCLES))
                continue
            try:
                obj.set_alt_manual(False)
                released[name] = True
                if sub_ok.get(name):
                    self._log('info', '潜艇[%s] BOL 已完成、浅水待机结束，交还深度控制权'
                                      '（任务里的潜深/油门从此生效）' % name)
                else:
                    self._log('warning', '潜艇[%s] BOL 等满 %d 个周期仍未成功，'
                                         '强制交还深度控制权（任务潜深生效）'
                              % (name, self.SUB_BOL_HOLD_MAX_CYCLES))
            except Exception as e:
                self._log('warning', '潜艇[%s] 交还深度控制权失败: %s' % (name, e))

        self._log('info', '本轮 BOL 成功 %d 次，累计已完成 %d 项' % (fired, len(done)))
        return fired

    def _find_units_by_keywords_any(self, situation, keywords):
        """按关键字（任一命中）找本方单元对象。"""
        return self._get_units_by_keywords(situation, keywords)

    def _find_weapons_on_unit(self, unit, wids):
        """
        在单元上找到指定武器（Mounts / Magazines / Loadouts / Weapons），
        返回可发射清单 [{'weapon':int, 'mount':int, 'count':int, 'name':str}]。

        🔴 为什么要按"挂架"分别列出（而不是合并成一条）：
           同一型武器可能装在**多个挂架**上（前 Mk41 / 后 Mk41 / 装甲箱…）。
           若把所有挂架合并成一条、数量只取最大值，就会严重低估载弹量 ——
           实测邦克山 3 个挂架各带 8/6/4 枚战斧，合并后只报 8 枚，
           于是"以为打完了，其实还剩十几枚"。

        挂架 DBID 的取法（按优先级）：
           1) 挂架字典里的 Component.DBID
           2) 挂架字典里的 DBID
           3) Mounts 字典的 key（保证不同挂架不会被合并）

        :param unit: Unit, 单元对象
        :param wids: tuple, 允许的武器 DBID（字符串或整数）
        :return: list, 见上
        """
        want = set()
        for w in wids:
            try:
                want.add(int(w))
            except (TypeError, ValueError):
                pass

        acc = {}          # (mount_db, weapon_db) -> 数量

        def _to_int(x):
            try:
                return int(x)
            except (TypeError, ValueError):
                return None

        def _mount_db(mv, mk):
            """推导挂架 DBID。"""
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

        def _record(rec, mount_db):
            """记录一条 WeaponRec（形如 {'WeaponDBID':.., 'CurrentLoad':..}）。"""
            if not isinstance(rec, dict):
                return
            wi = _to_int(rec.get('WeaponDBID'))
            if wi is None or wi not in want:
                return
            cnt = _to_int(rec.get('CurrentLoad'))
            if cnt is None:
                cnt = _to_int(rec.get('DefaultLoad'))
            if cnt is None:
                cnt = 0
            key = (mount_db, wi)
            # 🔴 必须是**求和**，不能取 max！
            #    同型武器可能装在**多个挂架**上，而这些挂架常常共用同一个
            #    挂架 DBID（日志实证：邦克山有两个 Mk41，DBID 都是 3017，
            #    各带 586(x4) 与 1131(x4)）。
            #    取 max 会把它算成 4（应为 8），于是"该打 8 发只打了 4 发"，
            #    用户看到的就是"109C 数量不对 / 没打出去"。
            acc[key] = acc.get(key, 0) + cnt

        def _scan_weaponrecs(container, mount_db):
            """
            在一个"挂架/弹仓"字典里找 WeaponRecs。
            WeaponRecs 可能是 dict（key->rec）或 list（rec 列表）。
            """
            if not isinstance(container, dict):
                return
            wrs = container.get('WeaponRecs')
            if isinstance(wrs, dict):
                for rec in wrs.values():
                    _record(rec, mount_db)
            elif isinstance(wrs, (list, tuple)):
                for rec in wrs:
                    _record(rec, mount_db)

        # ---- 1) Mounts / Magazines / Loadouts：逐个挂架扫描 ----
        for attr in ('Mounts', 'Magazines', 'Loadouts'):
            cont = getattr(unit, attr, None)
            if isinstance(cont, dict):
                for mk, mv in cont.items():
                    _scan_weaponrecs(mv, _mount_db(mv, mk))
                    # 有些结构把挂架再嵌一层（如 {"Mounts": {...}}）。
                    # ⚠️ 仅当本层没有 WeaponRecs 时才往下扫，否则会同一条
                    #    记录被计两次（求和后会翻倍）。
                    if isinstance(mv, dict) and 'WeaponRecs' not in mv:
                        for sub in mv.values():
                            if isinstance(sub, dict) and 'WeaponRecs' in sub:
                                _scan_weaponrecs(sub, _mount_db(sub, mk))
            elif isinstance(cont, (list, tuple)):
                for mv in cont:
                    _scan_weaponrecs(mv, _mount_db(mv, None))

        # ---- 2) 兜底：直接挂在 unit 上的 Weapons ----
        for attr in ('Weapons', 'WeaponRecs'):
            cont = getattr(unit, attr, None)
            if isinstance(cont, dict):
                for rec in cont.values():
                    _record(rec, None)
            elif isinstance(cont, (list, tuple)):
                for rec in cont:
                    _record(rec, None)

        # ---- 3) 最后兜底：平台的 get_weapon_infos() ----
        if not acc:
            fn = getattr(unit, 'get_weapon_infos', None)
            if callable(fn):
                try:
                    infos = fn() or []
                except Exception:
                    infos = []
                for item in infos:
                    if isinstance(item, (list, tuple)) and len(item) >= 3:
                        wi = _to_int(item[1])
                        cnt = _to_int(item[2])
                        if wi is not None and wi in want and cnt:
                            key = (None, wi)
                            if cnt > acc.get(key, -1):
                                acc[key] = cnt

        # ---- 4) 按**武器**合并（关键：平台按"发射系统"统筹，不按单个挂架）----
        #   日志实证：
        #     · 邦克山两个 Mk41（DBID 都是 3017，各 4 发）-> 一次
        #       `mount=3017, qty=8` 打出 8 发；说明平台会在整个发射系统里凑数。
        #     · 阿利伯克两个 Mk41（DBID 2803 / 2804，各 586×12、2941×8）->
        #       分两次 `mount=2803 x12` + `mount=2804 x12` 下发时，**只出去 12 发**，
        #       后一条被平台当成重复（都回"指令执行成功"，但弹没出筒）。
        #   因此这里按武器求和，取**第一个挂架 DBID** 代表整个发射系统，
        #   一次把总数打出去。
        merged = {}
        for (mnt, wi), cnt in sorted(acc.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
            if cnt <= 0:
                continue
            cur = merged.get(wi)
            if cur is None:
                merged[wi] = {'mount': mnt if mnt is not None else 0, 'count': cnt}
            else:
                cur['count'] += cnt
                # 若原本没有挂架号（None），补上后遇到的可用挂架号
                if not cur['mount'] and mnt is not None:
                    cur['mount'] = mnt

        out = []
        for wi, info in sorted(merged.items()):
            out.append({'weapon': wi,
                        'mount': info['mount'],
                        'count': info['count'],
                        'name': self._weapon_name(wi)})
        return out

    def add_all_step5_missions(self, situation):
        """
        创建 10~15 号任务（A区打船 / C区 / 北35 / 航母护航）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        creators = (self.add_mission_10_ship_A, self.add_mission_11_ship_C,
                    self.add_mission_12_north35_1, self.add_mission_13_north35_2,
                    self.add_mission_14_north35_3)
        ok = 0
        for fn in creators:
            try:
                if fn(situation) is not None:
                    ok += 1
            except Exception as e:
                self._log('error', '%s 执行异常: %s' % (fn.__name__, e))
        self._log('info', '第五步任务创建完成 %d/%d' % (ok, len(creators)))
        return ok

    def _remember_mission(self, mission):
        """
        记录已创建的任务，供"统一补任务条令"使用。

        不能只依赖 self.missions_obj —— 该字典由平台内部维护，若平台未回填，
        逐任务下发条令就会整批落空（这正是"只改总条令没用"的另一个原因）。

        :param mission: Mission, 任务对象
        :return: None
        """
        m = getattr(self, '_created_missions', None)
        if not isinstance(m, dict):
            m = {}
            self._created_missions = m
        name = getattr(mission, 'Name', None) or getattr(mission, 'name', None)
        if name:
            m[name] = mission

    def _all_mission_objects(self):
        """
        汇总所有已知任务对象：平台 missions_obj + 自己记录的任务。

        :return: dict, {任务名: 任务对象}
        """
        out = {}
        mo = getattr(self, 'missions_obj', None)
        if isinstance(mo, dict):
            out.update(mo)
        mine = getattr(self, '_created_missions', None)
        if isinstance(mine, dict):
            out.update(mine)
        return out

    # 已经在"创建任务时"下发过那 6 项通用条令的任务类型。
    #   _patrol_rule_ext() / _support_rule_ext() 里已经 r.update(_mission_common_doctrine())，
    #   所以巡逻/支援任务**不需要**在这里再补一遍（那是重复，白白吃掉指令配额）。
    #   这里只补**没有**走那两条路的任务（主要是 打击任务 A船~E船 / 扫地#2 等）。
    _RULE_COVERED_CLASSES = ('PatrolMission', 'SupportMission')

    @classmethod
    def _mission_is_rule_covered(cls, mission):
        """
        判断该任务在**创建时**是否已经拿到那 6 项通用条令。

        判定方式：遍历类的 MRO，看有没有 PatrolMission / SupportMission。
        （只用 type(x).__name__ 不可靠 —— 子类或包装类的名字会变。）
        """
        try:
            return any(c.__name__ in cls._RULE_COVERED_CLASSES
                       for c in type(mission).__mro__)
        except Exception:
            return False

    def apply_unified_mission_doctrine(self):
        """
        把"任务通用条令"补到**尚未覆盖的**任务上（跳过巡逻/支援任务）。

        平台的任务条令不继承推演方总条令（已知行为），因此必须逐任务下发：
            武器状态-返航：否；燃油状态-返航：否；武器状态-预先规划：耗光用航炮；
            加油/补给：不允许；受攻击时忽略电磁管控：否；攻击时忽略计划航线：否。

        🔴 2026-10-14 修正：巡逻/支援任务在**创建时**已经通过
        `_patrol_rule_ext()` / `_support_rule_ext()` 拿到这 6 项，
        这里再补一遍属于**纯重复** —— 白白消耗指令配额
        （实测初始突发 ~500 条、正好贴住 500 上限，把 BOL 挤掉）。
        现在只给"没走那两条路"的任务补，**打击任务依旧会拿到这 6 项**。

        :return: int, 本次实际处理的任务数
        """
        missions = self._all_mission_objects()
        if not missions:
            self._log('warning', '未找到任何任务对象，通用条令未下发')
            return 0
        doc = self._mission_common_doctrine()
        ok = 0
        skipped = 0
        for mname, mission in missions.items():
            # 跳过"创建时已下发过"的任务类型（巡逻/支援）
            if self._mission_is_rule_covered(mission):
                skipped += 1
                continue
            try:
                mission.doctrine_weapon_state_rtb(doc['weapon_state_rtb'])
                mission.doctrine_fuel_state_rtb(doc['fuel_state_rtb'])
                mission.doctrine_weapon_state_planned(doc['weapon_state_planned'])
                mission.doctrine_refuel(doc['doctrine_refuel'])
                mission.doctrine_ignore_emcon_under_attack(doc['ignore_emcon_under_attack'])
                mission.doctrine_ignore_plotted_course(doc['ignore_plotted_course'])
                ok += 1
            except Exception as e:
                self._log('error', '任务[%s]设置通用条令失败: %s' % (mname, e))
        self._log('info', '任务通用条令已补 %d 个（巡逻/支援 %d 个已在创建时下发，跳过）'
                  % (ok, skipped))
        return ok

    # ==================================================================
    # 发射车 WRA（**必须显式设数字，不能是"与上一级一致/继承"**）
    #   选手实测（截图）：若设成继承，UI 显示"与上一级一致"，
    #   下面的吨位档位**不会**跟着变，所以必须给单元**显式**设成 4。
    #     海马斯火箭炮#1~#4  -> 武器 3136 (M30A2 超射程精确制导武器)
    #     反舰导弹排#1~#5    -> 武器 1934 (雄风二型反舰导弹)
    # ==================================================================
    LAUNCHER_WRA_TARGET_TYPES = (
        WRA_WeaponTargetType.Ship_Unspecified,                    # 3000 船-未指定
    )

    # ==================================================================
    # BOL 纯方位打击的最大尝试次数。
    #   = 1 表示**只激活一次**：发出去就不再重发。
    #   选手要求："这个战斧的BOL纯方位打击，只需要激活一次就OK，
    #             否则会浪费太多的WRA个数"。
    #   之前 =2，且 _reply_ok 误判失败，导致战斧每 1~2 秒被反复
    #   "重定向到新目标"刷屏（截图实证）。
    BOL_MAX_TRIES = 1

    # ------------------------------------------------------------------
    # 潜艇专用：BOL 必须**先在浅水打出去**，之后才能让任务里的潜深接管
    #   背景：潜艇 BOL 需要 -20 米（浅水发射），而"航母杀手"任务要它去 -180 米；
    #         若先下潜就再也打不出 BOL 了（上浮 160 米按 1 m/s 要 160 秒）。
    #   因此：
    #     · 潜艇的重试次数给足（其它单元仍是 1 次，避免"重定向"刷屏）；
    #     · 只要 BOL 还没打出去，就**不交还**深度控制权（一直按住浅水）；
    #     · 但设一个上限周期兜底，避免武器真没了还把潜艇永远按在浅水。
    # ------------------------------------------------------------------
    SUB_BOL_MAX_TRIES = 5          # 潜艇 BOL 每项的尝试次数上限
    SUB_BOL_HOLD_MAX_CYCLES = 10   # 最多按住浅水多少个决策周期（10×30s=5 分钟）
    # 🔴 发射前置条件：潜艇深度必须浅于该值（即 -40 米以内）才允许打 BOL。
    #    剧本里佛蒙特号**开局就在 -132.7 米**，只发一条"上浮到 20 米"的指令后
    #    60 毫秒就打 BOL，弹是出不来的 —— 平台会回"指令执行成功"，
    #    但实际没发射，而代码把它当成成功就交还深度控制权、直接下潜了。
    #    故取与 SUB_SHALLOW_DEPTH 相同的 40 米（文档：超过约 45 米浅水发射会失败）。
    #    必须按"当前实际深度"判断，等它真的浮上来再打。
    SUB_BOL_READY_DEPTH = 40
    # 🔴 打出 BOL 之后**还要在浅水待机几个决策周期**再下潜。
    #    实测：打完立刻下潜时 16 发只出去 7 发 —— 平台需要时间把筒里的弹放完。
    #    选手要求"在 -20 米多待一会儿（约 3 倍于现在的时间）"，故取 3 个周期
    #    （3×30s = 90 秒推演时间）。
    SUB_BOL_HOLD_AFTER_FIRE_CYCLES = 3
    # 深度"稳定"判据：与上一周期相比变化不超过该值（米）才算稳住。
    #   实测"还在上浮途中就打"只出去 7/12 发，所以要等它稳住再打。
    SUB_BOL_STABLE_M = 5.0

    # 发射车对每个船的齐射数（选手要求：**都是 4 发**）
    LAUNCHER_SALVO_BY_UNIT = {
        '默认': '4',
    }

    # 战斧各型号 DBID（潜艇 UGM-109E / 驱逐舰 RGM-109E,I / 巡洋舰 RGM-109E,C）
    TOMAHAWK_WIDS = ('377', '586', '2941', '230')

    # ==================================================================
    # ⑥ 战斧：对所有目标"使用全部武器"
    #   （目标是固定坐标的 BOL 打击，但按要求 WRA 设为 99=使用全部武器）
    # ==================================================================

    # ==================================================================
    # ②③④⑤ 指定任务：对某类目标"不使用武器"（齐射数 0）
    # ==================================================================
    MISSION_NO_USE_WRA = {
        '1818181818181818': [
            ('AGM-154C-1', ('826', '1301', '3042'),
             WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons)],
        '16161616161616': [
            ('AGM-154C', ('826', '1301', '3042'),
             WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons)],
        '61616161616161': [
            ('AGM-154C', ('826', '1301', '3042'),
             WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons)],
        '1515151515151515': [
            ('AGM-158C', ('2378', '3642', '3654'),
             WRA_WeaponTargetType.Ship_Amphibious_10001_25000_tons)],
    }

    def _mission_unit_names(self, mname):
        """
        查出某任务的执行单元名（供"指定任务武器规则"用）。

        依次查：自己记录的表 -> 各任务配置表（打击/支援/巡逻）。
        找不到返回空列表（调用方会跳过单元级规则，只留任务级）。

        :param mname: str, 任务名
        :return: list, 单元名列表
        """
        # 1) 任务创建时记录下来的
        m = getattr(self, '_mission_units', None)
        if isinstance(m, dict) and m.get(mname):
            return list(m[mname])
        # 2) 打击任务
        for spec in getattr(self, 'STRIKE_MISSIONS', []):
            if spec.get('name') == mname:
                return list(spec.get('units', []))
        # 3) 支援（A~D / 左中右）
        for name, _pts, units, _act in getattr(self, 'CAR_SHIP_MISSIONS', ()):
            if name == mname:
                return list(units)
        # 4) 北船 / 北船2
        for name, _pts, units in getattr(self, 'NORTH_SHIP_PATROLS', ()):
            if name == mname:
                return list(units)
        # 5) 中1 / 中2（1616…/6161…）
        for name, _pts, units in getattr(self, 'MID_PATROLS', ()):
            if name == mname:
                return list(units)
        return []

    def apply_mission_no_use_wra(self, situation):
        """
        对指定任务下发"对这种目标不使用武器"（齐射数=0）。

        UI 里飞机显示「与上一级一致」，说明**任务级优先**，
        故先设任务级、再补单元级（两层都设死）。
        单元级只对该任务实际携带该型武器的飞机下发。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 下发条数
        """
        ok = 0
        for mname, entries in self.MISSION_NO_USE_WRA.items():
            mission = self._all_mission_objects().get(mname)
            if mission is None:
                self._log('warning', '指定任务[%s] 不存在，跳过其武器规则' % mname)
                continue
            hit_guids = []
            try:
                fn = getattr(mission, 'get_units_assigned', None)
                if callable(fn):
                    hit_guids = list(fn() or [])
            except Exception:
                hit_guids = []
            units = situation[0] if isinstance(situation[0], dict) else {}
            objs = []
            if hit_guids:
                for guid, u in units.items():
                    if not isinstance(u, dict):
                        continue
                    if guid not in hit_guids:
                        continue
                    obj = self.get_unit(u.get('guid', guid))
                    if obj is not None:
                        objs.append((str(u.get('name', '')), obj))
            else:
                # 🔴 关键修复：get_units_assigned() 返回空时，
                #    绝不能退化成"遍历全场所有单元" —— 那会把 AGM-154 的
                #    "不使用武器"规则下发到 奥尔良机场/企业号航母 等无关单元上
                #    （日志实证：任务[61616161616161][奥尔良机场] ... 不使用武器），
                #    既浪费有限的指令配额，又把配额挤爆导致真正的规则被丢。
                #    改为：从各任务配置表里查出该任务的执行单元名，精确匹配。
                want_names = self._mission_unit_names(mname)
                for nm in want_names:
                    for uname, obj in self._find_units_by_exact_name([nm]):
                        objs.append((uname, obj))
                if not objs:
                    self._log('warning', '任务[%s] 取不到执行单元，'
                                         '单元级武器规则跳过（任务级已设）' % mname)
            for label, wids, ttype in entries:
                for wid in wids:                       # 任务级
                    try:
                        mission.wra_qty_salvo(wid, ttype, '0')
                        ok += 1
                        self._log('info', '任务[%s] %s(武器%s) 对目标类型%s 不使用武器（任务级）'
                                  % (mname, label, wid, getattr(ttype, 'value', ttype)))
                    except Exception as e:
                        self._log('error', '任务[%s] 武器%s 任务级规则失败: %s' % (mname, wid, e))
                for name, obj in objs:                 # 单元级
                    try:
                        plans = self._find_weapons_on_unit(obj, wids)
                        if not plans:
                            continue
                        for wid in sorted({p['weapon'] for p in plans}):
                            obj.wra_qty_salvo(wid, ttype, '0')
                            ok += 1
                            self._log('info', '任务[%s][%s] %s(武器%d) 对目标类型%d 不使用武器'
                                      % (mname, name, label, wid,
                                         getattr(ttype, 'value', ttype)))
                    except Exception as e:
                        self._log('error', '任务[%s][%s] 单元级规则失败: %s' % (mname, name, e))
        self._log('info', '指定任务武器规则完成 %d 条' % ok)
        return ok

    # ==================================================================
    # AGM-154 (JSOW) 与 AGM-158C (LRASM) 的武器使用规则
    # ==================================================================
    # AGM-154 各型号（F-16 / F/A-18F 携带）
    AGM154_WIDS = ('826', '1301', '3042')
    # AGM-158C LRASM（B-2A 轰炸机携带）
    LRASM_WIDS = ('2378', '3642', '3654')
    # 船吨位分类（用于"只打 5000 吨以下"）
    SHIP_TONNAGE_GROUPS = (
        (WRA_WeaponTargetType.Ship_Carrier_0_25000_tons,
         WRA_WeaponTargetType.Ship_Carrier_25001_45000_tons,
         WRA_WeaponTargetType.Ship_Carrier_45001_95000_tons,
         WRA_WeaponTargetType.Ship_Carrier_95000_tons),
        (WRA_WeaponTargetType.Ship_Surface_Combatant_0_500_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_501_1500_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_5001_10000_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_10001_25000_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_25001_45000_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_45001_95000_tons,
         WRA_WeaponTargetType.Ship_Surface_Combatant_95000_tons),
        (WRA_WeaponTargetType.Ship_Amphibious_0_500_tons,
         WRA_WeaponTargetType.Ship_Amphibious_501_1500_tons,
         WRA_WeaponTargetType.Ship_Amphibious_1501_5000_tons,
         WRA_WeaponTargetType.Ship_Amphibious_5001_10000_tons,
         WRA_WeaponTargetType.Ship_Amphibious_10001_25000_tons,
         WRA_WeaponTargetType.Ship_Amphibious_25001_45000_tons,
         WRA_WeaponTargetType.Ship_Amphibious_45001_95000_tons,
         WRA_WeaponTargetType.Ship_Amphibious_95000_tons),
        (WRA_WeaponTargetType.Ship_Auxiliary_0_500_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_501_1500_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_1501_5000_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_5001_10000_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_10001_25000_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_25001_45000_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_45001_95000_tons,
         WRA_WeaponTargetType.Ship_Auxiliary_95000_tons),
        (WRA_WeaponTargetType.Ship_Merchant_Civilian_0_500_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_501_1500_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_1501_5000_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_5001_10000_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_10001_25000_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_25001_45000_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_45001_95000_tons,
         WRA_WeaponTargetType.Ship_Merchant_Civilian_95000_tons),
    )
    # <= 5000 吨的档位（每组前 3 档）
    SHIP_UNDER_5000_TYPES = tuple(t for g in SHIP_TONNAGE_GROUPS for t in g[:3])
    # > 5000 吨的档位（每组第 4 档起）
    SHIP_OVER_5000_TYPES = tuple(t for g in SHIP_TONNAGE_GROUPS for t in g[3:])



    # ==================================================================
    # ③④ 反舰导弹排（雄风二型 1934）：对"船-水面战舰 1501-5000吨"不使用武器
    #     （排水量较少的加强护卫舰和护卫舰）
    #     单位级下发；"船-未指定"的 4 发由 apply_launcher_wra 负责，其余自动继承。
    # ==================================================================
    ANTI_SHIP_PLT_NO_USE = {
        # 雄风二型 + 平台实际装载的其它反舰弹，一并禁用该吨位档
        '武器': ('1934', '3624'),
        '目标类型': WRA_WeaponTargetType.Ship_Surface_Combatant_1501_5000_tons,
    }

    # ==================================================================
    # WRA 去重缓存
    #   🔴 为什么需要：step() 每个决策周期都会补发 WRA。若不做去重，
    #      同一批设置会被无限重复下发，累积占满 agentOrderCountLimit=500
    #      的配额，导致后面的指令被丢弃（"时好时坏"）。
    #      平台上的 WRA 设置是**持久化**的，设一次即可；这里只记录
    #      "已成功下发的 (单元, 武器, 目标类型) -> 值"，值变了才重发。
    # ==================================================================
    def _wra_seen(self):
        d = getattr(self, '_ly_wra_sent', None)
        if not isinstance(d, dict):
            d = {}
            self._ly_wra_sent = d
        return d

    def _wra_once(self, obj, wid, ttype, value, key_prefix):
        """
        只在"该设置尚未成功下发过"时才下发，避免每周期重复。

        :param obj: 单元/任务对象
        :param wid: 武器 DBID（或任务级用）
        :param ttype: 目标类型
        :param value: 设置值（'4' / '0' / 'Max' ...）
        :param key_prefix: 缓存键前缀（区分单元级/任务级/不同规则）
        :return: True 表示本次真的下发了；False 表示已设过、跳过
        """
        seen = self._wra_seen()
        # 🔴 缓存键**必须用单元名**，不能用 id(obj)！
        #    id() 是 Python 的内存地址，平台重建/换实例后会变，
        #    导致缓存永不命中 —— 实测 AIM 空空弹因此被重复下发几百次，
        #    把 500 条配额吃光，海马斯的 WeaponQty=4 反而被丢弃
        #    （所以 UI 一直显示"与上一级一致"）。
        gid = getattr(obj, 'Name', None) or getattr(obj, 'ID', None) or id(obj)
        tv = getattr(ttype, 'value', ttype)
        k = '%s|%s|%s|%s' % (key_prefix, gid, wid, tv)
        if seen.get(k) == str(value):
            return False
        obj.wra_qty_salvo(wid, ttype, str(value))
        seen[k] = str(value)
        return True

    def _wra_range_once(self, obj, wid, ttype, value, key_prefix):
        """同上，针对"自动开火距离"。（键同样用单元名，不能用 id()）"""
        seen = self._wra_seen()
        gid = getattr(obj, 'Name', None) or getattr(obj, 'ID', None) or id(obj)
        tv = getattr(ttype, 'value', ttype)
        k = '%s|RANGE|%s|%s|%s' % (key_prefix, gid, wid, tv)
        if seen.get(k) == str(value):
            return False
        obj.wra_firing_range(wid, ttype, str(value))
        seen[k] = str(value)
        return True

    def apply_anti_ship_plt_no_use(self, situation):
        """
        给反舰导弹排#1~#5 的雄风二型(1934) 设"对 船-水面战舰 1501-5000吨 不使用武器"。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 下发条数
        """
        wids = self.ANTI_SHIP_PLT_NO_USE['武器']
        ttype = self.ANTI_SHIP_PLT_NO_USE['目标类型']
        ok = 0
        for name, obj in self._get_launcher_units(situation):
            if '反舰导弹排' not in name:
                continue
            try:
                plans = self._find_weapons_on_unit(obj, wids)
                if not plans:
                    continue
                for wid in sorted({p['weapon'] for p in plans}):
                    if self._wra_once(obj, wid, ttype, '0', 'PLT_NOUSE'):
                        ok += 1
                    self._log('info', '反舰导弹排[%s] 雄风二型(武器%d) 对目标类型%d 不使用武器'
                              % (name, wid, getattr(ttype, 'value', ttype)))
            except Exception as e:
                self._log('error', '反舰导弹排[%s] 不使用武器设置失败: %s' % (name, e))
        self._log('info', '反舰导弹排"不使用武器"规则完成 %d 条' % ok)
        return ok

    def apply_launcher_wra(self, situation):
        """
        给地面发射车下发反舰 WRA（齐射数 = LAUNCHER_SALVO_BY_UNIT['默认'] = 4）。

        关键设计：
          1. **只给"该型发射车实际携带的已知反舰弹"下发**。
             以前用 _unit_anti_ship_weapons()，它把"库里查不到"的武器一律当反舰，
             结果把海马斯的 2947/2949（火箭弹）等也纳入，指令量暴涨、
             把 agentOrderCountLimit=500 的配额吃光，导致"海马斯有时改了有时没改"。
          2. 目标类型只用 LAUNCHER_WRA_TARGET_TYPES（船-未指定，其余自动跟随）。

        :param situation: tuple, (units dict, contacts dict)
        :return: (int, list), 处理单元数、每单元武器清单
        """
        qty = self.LAUNCHER_SALVO_BY_UNIT['默认']
        types = self.LAUNCHER_WRA_TARGET_TYPES
        ok, report = 0, []
        for name, obj in self._get_launcher_units(situation):
            try:
                # ---- 该型发射车"应当携带"的武器（来自配置表）----
                want = None
                for key, (_q, ws) in self.STRIKE_WRA_BY_UNIT.items():
                    if key in name:
                        want = [int(w) for w in ws]
                        break
                if not want:
                    continue
                # ---- 只保留该单元**实际携带**的 ----
                carried = set()
                for w in want:
                    if self._find_weapons_on_unit(obj, (str(w),)):
                        carried.add(w)
                if not carried:
                    continue
                sent = 0
                for wid in sorted(carried):
                    for t in types:
                        # 去重：同样的设置只发一次
                        if self._wra_once(obj, wid, t, qty, 'LAUNCHER'):
                            sent += 1
                        self._wra_range_once(obj, wid, t, 'Max', 'LAUNCHER')
                ok += 1
                report.append((name, sorted(carried)))
                if sent:
                    self._log('info', '发射车[%s] 反舰 WRA 已设：武器=%s 齐射数=%s '
                                      '目标类型=%d 种'
                              % (name, sorted(carried), qty, len(types)))
                else:
                    self._log('info', '发射车[%s] 本周期 WRA 无需重发（已设过，跳过）' % name)
            except Exception as e:
                self._log('error', '发射车[%s] 反舰 WRA 设置失败: %s' % (name, e))
        self._log('info', '发射车反舰 WRA 完成 %d 个单元' % ok)
        return ok, report

    def apply_anti_ship_saturation(self, situation):
        """
        （旧版：对全部携带反舰弹的单元无差别下发，指令量过大，已停用）
        现由 apply_launcher_wra 取代 —— 只处理地面发射车。
        """
        return self.apply_launcher_wra(situation)

    def _apply_anti_ship_saturation_legacy(self, situation):
        """
        对**所有携带反舰武器的单元**（飞机 / 舰船 / 地面发射车）下发反舰饱和打击 WRA。

        背景：单纯把"对海"设为自由开火不会开火 —— 平台是两级闸门，
        WCS 只决定"允许开火"，真正扣扳机的是 WRA 的**齐射武器数**；
        齐射数为 0 / 未设置时，自由开火也不会发射。

        本方法做四件事：
          1. 自动识别每个单元携带的**反舰武器**（查 DataWeaponTargets，CodeID=2001 水面舰艇）；
          2. 对全部水面舰艇目标类型（未知类型 + 未指定 + 具体吨位）设 `齐射数 = Max`（饱和打击）；
          3. 自动开火距离设 `Max`（射程内必打；射程外本来也打不到）；
          4. 对**加分目标（两栖舰/登陆舰，如蟾蜍级）**额外优先分配。

        注意：WRA 只能规定"对某类目标打几发"，**不能规定打击顺序**。
        平台会自行选择最近的有效目标；"先打蟾蜍再打雷鸣"无法用 WRA 表达，
        只能靠优先目标列表 / 手动分配武器实现。

        :param situation: tuple, (units dict, contacts dict)
        :return: (int, list), 设置成功的单元数、每单元识别到的反舰武器清单
        """
        units = situation[0] if isinstance(situation[0], dict) else {}

        # ---- 按"地面发射车优先"排序：地面单元排在前面，保证配额优先给它们 ----
        ordered = []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            obj = self.get_unit(u.get('guid', guid))
            if obj is None:
                continue
            cat = str(u.get('category', ''))
            # Facility(地面) > Ship/Submarine > 其他
            prio = 0 if cat == 'Facility' else (1 if cat in ('Ship', 'Submarine') else 2)
            ordered.append((prio, u.get('name', ''), obj))
        ordered.sort(key=lambda x: x[0])

        # ---- 依据指令配额决定目标类型数量 ----
        # 每条 WRA 项都要下发两次（齐射数 + 开火距离），故每个武器消耗 2*N 条指令。
        budget = self._cmd_budget()
        base = self.SURFACE_TARGET_TYPES if self.USE_ALL_SURFACE_TARGETS \
            else self.SURFACE_TARGET_TYPES_CORE
        n_types = len(base)
        # 先估算总消耗，若超预算则只保留最关键的几个目标类型
        tiered = [base]
        tiered.append(base[:6])
        tiered.append((base[0], base[1], base[5]))   # 未知类型/未指定/两栖1501-5000
        tiered.append((base[0], base[1]))            # 最关键两条

        report = []
        done = 0
        spent = 0
        chosen = tiered[-1]
        # 预估总武器数，选一个能放下的档位
        est_weapons = 0
        for _, _nm, obj in ordered:
            w, _d = self._unit_anti_ship_weapons(obj)
            est_weapons += len(set(w) | {int(x) for x in self.EXTRA_ANTI_SHIP_WEAPONS
                                         if str(x).isdigit()})
        for t in tiered:
            if est_weapons * len(t) * 2 <= budget or len(t) == len(tiered[-1]):
                chosen = t
                break
        self._log('info', '反舰WRA预算: 指令上限=%s 可用=%d 预估武器数=%d 目标类型=%d 种'
                  % (getattr(self, '_order_count_limit', '未知'), budget,
                     est_weapons, len(chosen)))

        for prio, name, obj in ordered:
            # 该单元携带的反舰武器（自动识别 + 配置里强制纳入的）
            asm, diag = self._unit_anti_ship_weapons(obj)
            carried = self._unit_carried_weapons(obj)
            # 关键：手工指定/无法判定的武器，只有在单元**确实携带**时才下发，
            # 否则平台会报"找不到武器"并连累整批指令。
            asm = set(asm) | {int(w) for w in self.EXTRA_ANTI_SHIP_WEAPONS
                              if str(w).isdigit()}
            asm = sorted(w for w in asm if (w in carried) or (not carried))
            if not asm:
                # 诊断：说明为什么这个单元被跳过
                if diag:
                    self._log('info', '反舰WRA跳过[%s] 武器判定=%s' % (name, diag))
                continue
            # 该单元需要的指令数（每个武器：目标类型数 x 2）
            need = len(asm) * len(chosen) * 2
            if spent + need > budget:
                self._log('warning', '反舰WRA配额不足，跳过[%s]（已用 %d/%d，还需 %d）'
                          % (name, spent, budget, need))
                continue
            try:
                for wid in asm:
                    for t in chosen:
                        obj.wra_qty_salvo(wid, t, 'Max')
                        obj.wra_firing_range(wid, t, 'Max')
                spent += need
                done += 1
                report.append((name, sorted(asm)))
                self._log('info', '反舰饱和打击已设置: [%s] 反舰武器=%s 目标类型=%d 指令=%d 判定=%s'
                          % (name, sorted(asm), len(chosen), need, diag))
            except Exception as e:
                self._log('error', '单元[%s]设置反舰 WRA 失败: %s' % (name, e))
        self._log('info', '反舰饱和打击共设置 %d 个单元，消耗指令 %d/%d'
                  % (done, spent, budget))
        return done, report

    def _unit_carried_weapons(self, unit):
        """
        返回该单元**实际携带**的武器 DBID 集合（用于 WRA 前校验）。

        为什么需要它：平台对不存在的武器下发 WRA 会整批报错
        `找不到武器`，而且**一条失败会连累整批指令**。
        日志实测：早期版本给所有飞机都下发 AIM-9X/AIM-120D/AIM-260 的 WRA，
        结果 17280 条 SetDoctrineWRA 全部失败。

        数据来源（都只反映"真实携带"）：
          • Mounts / Loadouts / Magazines 里的 WeaponDBID
          • 平台接口 get_weapon_infos() / get_weapon_info()

        :param unit: Unit, 单元对象
        :return: set, 实际携带的武器 DBID
        """
        out = set()

        def _walk(obj, depth=0):
            if depth > 6:
                return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'WeaponDBID' and isinstance(v, (int, str)):
                        try:
                            out.add(int(v))
                        except (TypeError, ValueError):
                            pass
                    else:
                        _walk(v, depth + 1)
            elif isinstance(obj, (list, tuple)):
                for v in obj:
                    _walk(v, depth + 1)

        for key in ('Mounts', 'Loadouts', 'Magazines', 'Weapons'):
            c = getattr(unit, key, None)
            if c:
                _walk(c)
        fn = getattr(unit, 'get_weapon_infos', None)
        if callable(fn):
            try:
                for item in (fn() or []):
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        out.add(int(item[1]))
            except Exception:
                pass
        fn = getattr(unit, 'get_weapon_info', None)
        if callable(fn):
            try:
                d = fn() or {}
                if isinstance(d, dict):
                    for w in d:
                        out.add(int(w))
            except Exception:
                pass
        return out

    def _unit_anti_ship_weapons(self, unit):
        """
        找出单元可用于反舰饱和打击的武器 DBID 列表。

        判定规则（重要：**不能只认"能查到反舰目标码"的武器**）：
          1. 递归收集该单元所有出现过的 WeaponDBID：
             Mounts / Magazines / Loadouts / 以及 mounts[].WeaponRecs[].Weapons[] 嵌套结构；
          2. 逐个查 model.db：
             • 目标码含 2001（水面舰艇）           -> 反舰，纳入
             • **查不到该武器（目标码为空）**       -> 纳入（无法判定不等于不能用）
               地面发射车（海马斯/雄风反舰导弹连）的弹在库里查不到，
               早期版本因此把它们整批漏掉 —— 这是"设了自由开火毫无反应"的根因。
             • 能查到但目标码明确不含 2001（如 AIM-120/对地巡航弹） -> 排除
          3. 额外纳入 EXTRA_ANTI_SHIP_WEAPONS 里手工指定的武器。

        :param unit: Unit, 单元对象
        :return: (list, dict), 纳入的武器列表、诊断信息 {武器ID: 说明}
        """
        try:
            from engine.LingYi.entitys.data import query_data
        except Exception as e:
            self._log('warning', '无法导入 query_data，反舰武器识别跳过: %s' % e)
            query_data = None

        # ---- 1. 递归收集所有 WeaponDBID 与挂架容器名 ----
        wids = {}
        containers_seen = set()

        def _walk(obj, depth=0):
            if depth > 6:
                return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'WeaponDBID' and isinstance(v, (int, str)):
                        try:
                            wids[int(v)] = True
                        except (TypeError, ValueError):
                            pass
                    else:
                        _walk(v, depth + 1)
            elif isinstance(obj, (list, tuple)):
                for v in obj:
                    _walk(v, depth + 1)

        for key in ('Mounts', 'Magazines', 'Loadouts', 'Weapons'):
            container = getattr(unit, key, None)
            if container:
                containers_seen.add(key)
                _walk(container)

        # 平台接口兜底（Ship.get_weapon_infos / Unit.get_weapon_info）
        fn = getattr(unit, 'get_weapon_infos', None)
        if callable(fn):
            try:
                for item in (fn() or []):
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        wids[int(item[1])] = True
                containers_seen.add('get_weapon_infos')
            except Exception:
                pass
        fn = getattr(unit, 'get_weapon_info', None)
        if callable(fn):
            try:
                d = fn() or {}
                if isinstance(d, dict):
                    for w in d:
                        wids[int(w)] = True
                    containers_seen.add('get_weapon_info')
            except Exception:
                pass

        # ---- 2. 逐个判定 ----
        out = []
        diag = {}
        for wid in sorted(wids):
            targets = None
            if query_data is not None:
                try:
                    targets = query_data.get_weapon_targets(wid)
                except Exception:
                    targets = None
            if targets:                       # 能查到目标码
                if 2001 in targets:           # 水面舰艇
                    out.append(wid)
                    diag[wid] = '反舰(目标码含2001)'
                else:
                    diag[wid] = '排除(目标码不含2001: %s)' % sorted(targets)[:6]
            else:                             # 查不到该武器 -> 无法判定，纳入
                out.append(wid)
                diag[wid] = '纳入(库中查不到该武器，无法判定)'

        # ---- 3. 手工指定的额外武器 ----
        for w in self.EXTRA_ANTI_SHIP_WEAPONS:
            try:
                wi = int(w)
            except (TypeError, ValueError):
                continue
            if wi not in out:
                out.append(wi)
                diag[wi] = '手工纳入(EXTRA_ANTI_SHIP_WEAPONS)'

        if not containers_seen:
            diag['_note'] = '该单元没有任何挂架/弹药库字段(可能是地面单元)'
        return sorted(set(out)), diag

    # ==================================================================
    # 对海打击任务（A~E 区）：按船名锁定情报 guid 并建任务
    # ==================================================================
    def _resolve_contacts_by_spec(self, situation, spec):
        """
        按目标写法在**情报**里锁定 contact guid。

        支持三种写法：
          '蟾蜍'      -> 名字含"蟾蜍"的全部情报
          '蟾蜍#1'    -> 名字含"蟾蜍"且含"#1"的情报
          精确名       -> 完全一致

        注意：打击任务的目标列表只认 **contact guid**（情报ID），不认坐标；
        坐标只能用于"在情报里就近匹配"，前提是该目标已被我方探测到。

        :param situation: tuple, (units dict, contacts dict)
        :param spec: str, 目标写法
        :return: (list, list), 命中的 (contact_guid, contact_name) 列表、未命中的 spec
        """
        contacts = situation[1] if isinstance(situation[1], dict) else {}
        spec = str(spec).strip()
        # 拆出"船型关键字"和"船号"
        hull = None
        m = re.search(r'#\s*(\d+)', spec)
        base = spec
        if m:
            hull = m.group(1)
            base = spec[:m.start()]
        base_bare = base.replace('“', '').replace('”', '').replace('"', '').strip()

        hits = []
        for cid, c in contacts.items():
            if not isinstance(c, dict):
                continue
            nm = str(c.get('Name', ''))
            if not nm:
                continue
            nm_bare = nm.replace('“', '').replace('”', '').replace('"', '')
            if hull is None:
                if base_bare and base_bare in nm_bare:
                    hits.append((cid, nm))
            else:
                # 要求船型与船号同时命中；船号按 '#数字' 形式在名字里找
                if base_bare in nm_bare and re.search(r'#\s*%s\b' % re.escape(hull), nm_bare):
                    hits.append((cid, nm))
        return hits, spec

    def _dump_target_contacts(self, situation):
        """把当前情报里所有疑似目标（登陆舰/护卫舰等）打进日志，便于核对船名。"""
        contacts = situation[1] if isinstance(situation[1], dict) else {}
        rows = []
        for cid, c in contacts.items():
            if not isinstance(c, dict):
                continue
            nm = str(c.get('Name', ''))
            if nm and any(k in nm for k in self.TARGET_KEYWORDS):
                rows.append((nm, cid))
        if rows:
            self._log('info', '当前可打击的情报目标（%d 条）：%s'
                      % (len(rows), sorted(rows)))
        else:
            self._log('warning', '当前情报里没有找到任何目标（关键字=%s）；'
                                 '可能尚未探测到，需等后续决策周期再锁定'
                      % (self.TARGET_KEYWORDS,))
        return rows

    def add_strike_missions(self, situation):
        """
        创建 A~E 五个对海打击任务：分配地面发射车 + 按船名锁定目标并加入目标列表。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 成功创建的任务数
        """
        self._dump_target_contacts(situation)
        ok = 0
        # 按要求：A船~E船**不预置执行单元**（选手自行手动转入）
        missions = [dict(m) for m in self.STRIKE_MISSIONS]
        for spec in missions:
            name = spec['name']
            try:
                # 按 spec 指定任务类型（默认对海；'LAND' = 对陆打击）
                _mt = MissionStrikeType.SHIP
                if str(spec.get('mission_type', '')).upper() == 'LAND':
                    _mt = MissionStrikeType.LAND
                mission = self.create_strike_mission(name, _mt)
                if mission is None:
                    self._log('error', '创建打击任务失败：%s' % name)
                    continue
                self._remember_mission(mission)

                # ---- 分配执行单元 ----
                _, guids = self._find_unit_guids_by_ovlp(situation, spec['units'])
                if not guids:
                    self._log('warning', '打击任务[%s]未匹配到任何执行单元：%s'
                              % (name, spec['units']))
                for i in range(0, len(guids), 10):
                    self.assign_units_to_mission(mission_name=name,
                                                 unit_list=guids[i:i + 10])

                # ---- 武器使用规则：按发射单元类型指定对船齐射数 ----
                # 对陆打击任务（战斧，目标是机场）不需要对海 WRA，跳过
                per_wid = {}      # 武器ID -> 齐射数
                if str(spec.get('mission_type', '')).upper() == 'LAND':
                    self._log('info', '打击任务[%s] 为对陆打击，跳过对海 WRA' % name)
                else:
                    for uname in spec['units']:
                        for key, (qty, ws) in self.STRIKE_WRA_BY_UNIT.items():
                            if key in uname:
                                for w in ws:
                                    per_wid[str(w)] = qty
                if per_wid:
                    for wid in sorted(per_wid):
                        for t in self.LAUNCHER_WRA_TARGET_TYPES:
                            mission.wra_qty_salvo(wid, t, per_wid[wid])
                    self._log('info', '打击任务[%s] WRA 已设：%s（目标类型 %d 种）'
                              % (name, {w: per_wid[w] for w in sorted(per_wid)},
                                 len(self.LAUNCHER_WRA_TARGET_TYPES)))
                else:
                    self._log('warning', '打击任务[%s] 未匹配到武器配置，WRA 未设置' % name)

                # ---- 锁定目标（contact guid）----
                all_g, missing = [], []
                for t in spec.get('targets', []):
                    hits, _ = self._resolve_contacts_by_spec(situation, t)
                    if hits:
                        all_g.extend(g for g, _ in hits)
                    else:
                        missing.append(t)
                # 去重保序
                seen, tgt = set(), []
                for g in all_g:
                    if g not in seen:
                        seen.add(g)
                        tgt.append(g)
                if tgt:
                    mission.strike_add_target(tgt)
                if missing:
                    self._log('warning', '打击任务[%s]未锁定的目标：%s'
                              '（须已探测到；船名需与我方情报一致）' % (name, missing))
                if not spec.get('targets'):
                    self._log('info', '打击任务[%s]未指定目标，仅建立任务（按区域索敌）' % name)

                ok += 1
                self._log('info', '打击任务[%s] 已创建：执行单元 %d 个，目标 %d 个'
                          % (name, len(guids), len(tgt)))
            except Exception as e:
                self._log('error', '打击任务[%s] 创建异常：%s' % (name, e))
        self._log('info', '对海打击任务创建完成 %d/%d' % (ok, len(self.STRIKE_MISSIONS)))
        return ok

    # 读 WCS 时按单元类型取不同的键
    WCS_KEYS_SURFACE = ('WCS_Surface', 'WCS_surface', 'wcs_surface')
    WCS_KEYS_AIR = ('WCS_Air', 'WCS_air', 'wcs_air')

    def _read_wcs(self, situation, name, keys):
        """
        读取某单元当前的武器控制状态(WCS) —— 即"该单元自己的对空/对海条令"。

        ⚠️ **只从态势数据里读，绝不调用平台接口。**
        实测教训：`api_get_Doctrine` / `api_get_doctrineWRA` 每周期对多个单元
        轮询会把平台指令队列打爆 —— 日志实证 13:29:47 开始轮询，13:31:14 起
        出现 653 次"网络状态不佳，指令已被取消下发"，随后 656 次
        "智能体暂未收到态势"，智能体与客户端**彻底失联**，
        导致停车/开雷达/撤离等所有动作全部作废。

        本函数**不假设嵌套结构**：在整个单元 dict 里递归找 WCS 字段，
        因为智能体收到的态势结构未必与平台落盘 JSON 一致
        （平台落盘里确实有 "Doctrine": {"WCS_Surface": 0, ...}）。

        字段缺失时返回 None，调用方一律当作"未知"，绝不当成"手动"。

        取值：Free=0 / Tight=1 / Hold=2。

        :param situation: tuple, (units dict, contacts dict)
        :param name: str, 单元名
        :param keys: tuple, 候选字段名（WCS_Surface / WCS_Air 等）
        :return: (int or None, str), WCS值、命中字段名
        """
        units = situation[0] if isinstance(situation[0], dict) else {}
        for _guid, u in units.items():
            if not isinstance(u, dict) or str(u.get('name', '')) != name:
                continue
            hit = [None]

            def _scan(o, depth=0):
                if depth > 4 or hit[0] is not None:
                    return
                if isinstance(o, dict):
                    for k, v in o.items():
                        if isinstance(k, str) and any(
                                k.lower() == kk.lower() for kk in keys):
                            if v is not None:
                                try:
                                    hit[0] = (int(v), k)
                                    return
                                except (TypeError, ValueError):
                                    pass
                        _scan(v, depth + 1)
                elif isinstance(o, (list, tuple)):
                    for v in o:
                        _scan(v, depth + 1)
            _scan(u)
            if hit[0] is not None:
                return hit[0]
            return None, ''
        return None, ''

    def _dump_unit_keys_once(self, situation):
        """
        一次性诊断：把**相关单元在态势里的真实字段名**打进日志。

        上一次"条令轮询 成功=0/N"说明我猜的键路径不对。为了不再盲猜，
        这里把海马斯/防空单元的字段清单（含 Doctrine 内容）打出来，
        据此就能精确定位 WCS 字段的真实位置。只打一次。
        """
        if getattr(self, '_ly_keys_dumped', False):
            return
        self._ly_keys_dumped = True
        try:
            units = situation[0] if isinstance(situation[0], dict) else {}
            shown = 0
            for _guid, u in units.items():
                if not isinstance(u, dict):
                    continue
                nm = str(u.get('name', ''))
                if not any(k in nm for k in ('海马斯', '爱国者', '霍克', '反舰导弹排',
                                             'LUCAS', '地空导弹连')):
                    continue
                doc = u.get('Doctrine') or u.get('doctrine')
                docinfo = dict(doc) if isinstance(doc, dict) else repr(doc)[:120]
                self._log('info', '态势字段诊断[%s] 顶层键=%s Doctrine=%s'
                          % (nm, sorted(u.keys()), docinfo))
                shown += 1
                if shown >= 4:
                    break
            if shown == 0:
                self._log('warning', '态势字段诊断：未找到发射车/防空单元')
        except Exception as e:
            self._log('error', '态势字段诊断异常: %s' % e)

    def _parse_wcs_from_obj(self, obj, keys):
        """
        从 dict / str / bytes 里解析 WCS 值。

        支持三种形态：
          · dict: {"WCS_Surface": 2}
          · 文本: "WCS_Surface=2" / "WCS_Surface: 2" / "WCS_Surface 2"
          · 字节: protobuf 原始序列（含 "WCS_Surface" 字样时按文本兜底搜）

        :param obj: 待解析对象
        :param keys: tuple, 候选字段名
        :return: (int or None, str), 值与命中的字段名
        """
        if isinstance(obj, dict):
            for k in keys:
                if k in obj and obj[k] is not None:
                    try:
                        return int(obj[k]), k
                    except (TypeError, ValueError):
                        return None, ''
            return None, ''
        if isinstance(obj, (bytes, bytearray)):
            try:
                obj = bytes(obj).decode('utf-8', 'ignore')
            except Exception:
                return None, ''
        if not isinstance(obj, str):
            return None, ''
        for k in keys:
            m = re.search(r'%s[\'"]?\s*[:=]?\s*[\'"]?(-?\d+)' % re.escape(k), obj)
            if m:
                try:
                    return int(m.group(1)), k
                except (TypeError, ValueError):
                    pass
        return None, ''

    def _wcs_is_free(self, wcs):
        """WCS 是否为"自由开火"(0)。读不到(None)时返回 None 表示未知。"""
        if wcs is None:
            return None
        return wcs == WeaponControlStatus.Free.value

    # 每多少个决策周期打一次"条令轮询"汇总日志
    POLL_LOG_EVERY = 4

    def _poll_summary(self, results):
        """
        把本轮"读条令"的结果汇总打一行日志（每 N 周期一次，避免刷屏）。

        这一行是判定**通道B（条令轮询）是否可用**的直接依据：
          · 若"成功"数量 > 0  → 读得到，按键联动可生效；
          · 若"成功"= 0        → 平台封装取不到数据，只能靠弹药判据兜底。

        :param results: list, [(单元名, WCS值, 来源)]
        :return: None
        """
        n = getattr(self, '_ly_poll_seq', 0) + 1
        self._ly_poll_seq = n
        if n % self.POLL_LOG_EVERY != 0:
            return
        ok = [(nm, v, s) for nm, v, s in results if v is not None]
        bad = [nm for nm, v, _s in results if v is None]
        self._log('info', '条令轮询#%d 成功=%d/%d 明细=%s 读不到=%s'
                  % (n, len(ok), len(results), ok, bad if bad else '无'))

    def launcher_doctrine_toggle(self, situation):
        """
        发射车"超链接按钮"式控制（响应选手手动改条令）：

          · 条令 = **自由开火**     -> 停车 + 保持阵位（准备接战）
          · 条令 = **仅限手动开火** -> 启动油门往南撤离

        这样选手在对局中把条令从"自由开火"改回"仅限手动开火"就相当于
        "按下逃跑按钮"；靠条令而不是靠检测弹药，从而不依赖弹药读数是否准确。

        首周期行为由 initial_launchers() 设定：
          · 开局总条令是"限制开火"(非 Free)，若首周期就响应会被误判成
            "选手按了逃跑按钮"而开局就跑；
          · initial_launchers() 已把基线写成"自由开火"（按住不动正是自由开火
            该有的动作），因此开局不会撤离，只有选手**真的改过**条令才响应。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本周期发生状态切换的单元数
        """
        switched = 0
        polled = []
        for name, obj in self._get_launcher_units(situation):
            # 已在撤离中 -> 不再轮询条令，只续发航路（保证一直在跑）
            if getattr(obj, '_ly_retreat_done', False):
                self._retreat_unit_south(name, obj, repeat=True)
                continue
            wcs, src = self._read_wcs(situation, name, self.WCS_KEYS_SURFACE)
            polled.append((name, wcs, src))

            # ---- 通道1：弹药全部打光 -> 立即后撤（与条令无关，最可靠）----
            total, _detail = self._launcher_ammo_left(obj)
            peak = getattr(obj, '_ly_ammo_peak', None)
            if peak is None:
                obj._ly_ammo_peak = total
                obj._ly_ammo_known = total > 0
            elif total > peak:
                obj._ly_ammo_peak = total
                obj._ly_ammo_known = True
            if bool(getattr(obj, '_ly_ammo_known', False)) and total == 0:
                if self._retreat_unit_south(name, obj):
                    switched += 1
                continue

            # ---- 通道2：该单元"对海条令"从自由开火变为手动 -> 后撤 ----
            # 只在**确实读到过值**时才判断：读不到(None)一律视为"未知"，不动作。
            free = self._wcs_is_free(wcs)
            if free is None:
                continue
            prev = getattr(obj, '_ly_wcs_free', None)
            obj._ly_wcs_free = free
            if prev is None:
                continue                     # 首个已知值 -> 只建基线
            if prev == free:
                continue                     # 未变化
            if not free:
                if self._retreat_unit_south(name, obj):
                    switched += 1
                continue
            # 变回自由开火 -> 停车待战
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
                obj._ly_retreat_done = False
                switched += 1
                self._log('info', '发射车[%s] 条令=自由开火 -> 停车待战' % name)
            except Exception as e:
                self._log('error', '发射车[%s] 停车失败: %s' % (name, e))
        self._poll_summary(polled)
        return switched

    def _retreat_unit_south(self, name, obj, repeat=False):
        """
        让一个单元向南撤离（清阵位 + 向南航路 + 加速）。

        航路刻意给得**很长**（向南 4 段、约 12 个纬度），而且撤离期间
        **每个决策周期都重发一次**，这样单元不会在终点停车
        —— 避免"跑到一半停下被打"。

        :param name: str, 单元名
        :param obj: Unit, 单元对象
        :param repeat: bool, True 表示撤离后的续发（不再重复打日志）
        :return: bool, 是否下发成功
        """
        try:
            lat = float(getattr(obj, 'Lat', 0.0) or 0.0)
            lon = float(getattr(obj, 'Lon', 0.0) or 0.0)
            d = self.RETREAT_SOUTH_LAT_DELTA
            south = [(lat - d * i, lon) for i in range(1, self.RETREAT_SOUTH_STEPS + 1)]
            try:
                obj.hold_positon(False)
            except Exception:
                pass
            obj.plotted_course(south)
            try:
                obj.set_desired_speed(self.RETREAT_SPEED_KMH)
            except Exception:
                pass
            try:
                obj.set_throttle(Throttle.Full)
            except Exception:
                pass
            if not repeat:
                obj._ly_retreat_done = True
                self._log('info', '发射车[%s] 开始向南撤离 %s 速度%d'
                          % (name, south, self.RETREAT_SPEED_KMH))
            return True
        except Exception as e:
            self._log('error', '发射车[%s] 撤离失败: %s' % (name, e))
            return False

    # ==================================================================
    # 防空单元（爱国者 / 霍克 / 地空导弹连）："对空条令"联动
    #   对空自由开火 -> 停车 + 开雷达 + 对空自由开火
    #   对空手动开火 -> 关雷达 + 约5海里闭环机动（不落地、不停车）
    #   注意：判断的是**该单元自己的对空条令**，不是推演方总条令。
    # ==================================================================
    SAM_UNIT_KEYS = ('爱国者', '霍克', '地空导弹连')
    # 防空单元**不能脱离阵位**（只要在动就打不中它们），所以：
    #   · 绕圈半径约 2.5 海里（不能太大，否则等于脱离阵位）；
    #   · **闭环**航路，绕完自动进入下一圈 → 永远不会"没路跑"而停下。
    # 约 2.5 海里 ≈ 0.0417 度纬度；取 0.04/0.06（经度在 48°N 约 2.3 海里）
    PATRIOT_PATROL_LAT_DELTA = 0.04
    PATRIOT_PATROL_LON_DELTA = 0.06
    PATRIOT_SPEED_KMH = 32

    def _sam_loop_course(self, lat, lon):
        """
        生成一个**闭环**机动航线（约 5 海里见方），首点即末点。

        闭环的意义：单元绕圈回到起点后继续下一圈，不会像开放航路那样
        在终点停住 —— 这正是"半道停车"的根因。

        :param lat: float, 基点纬度
        :param lon: float, 基点经度
        :return: list, 闭环航路点
        """
        a, b = self.PATRIOT_PATROL_LAT_DELTA, self.PATRIOT_PATROL_LON_DELTA
        return [(lat + a, lon + b),      # 东北
                (lat + a, lon - b),      # 西北
                (lat - a, lon - b),      # 西南
                (lat - a, lon + b),      # 东南
                (lat + a, lon + b)]      # 回到起点 -> 闭环

    def _get_units_by_keys(self, situation, keys):
        """按名称关键字收集单元对象。"""
        units = situation[0] if isinstance(situation[0], dict) else {}
        out = []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            name = str(u.get('name', ''))
            if not any(k in name for k in keys):
                continue
            obj = self.get_unit(u.get('guid', guid))
            if obj is not None:
                out.append((name, obj))
        return out

    def patriot_doctrine_toggle(self, situation):
        """
        爱国者防空连的"雷达/机动"联动：

          · 条令 = 自由开火     -> 停车 + 打开雷达 + 对空自由开火
          · 条令 = 仅限手动开火 -> 关闭雷达 + 加速在**附近**来回机动

        与发射车不同：爱国者不是往南跑，而是在一小段路里往返机动
        （打一阵换个位置，避免被反辐射武器锁定）。

        这是**持续跟随**的状态：选手在对局中可以来回切换很多遍，
        每切换一次就执行一次对应动作（自由开火 <-> 仅限手动开火）。

        开局行为由 initial_patriots() 设定：开局即为"关雷达 + 附近机动"，
        并把内部状态标成"手动"(_ly_wcs_free=False)，因此开局不会有多余动作、
        雷达也不会被打开。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 本周期发生状态切换的单元数
        """
        switched = 0
        polled = []
        for name, obj in self._get_units_by_keys(situation, self.SAM_UNIT_KEYS):
            # 霍克已单独处理（关航线+保持阵位+关雷达），不参与联动
            if getattr(obj, '_ly_hawk_fixed', False):
                continue
            wcs, src = self._read_wcs(situation, name, self.WCS_KEYS_AIR)
            polled.append((name, wcs, src))
            free = self._wcs_is_free(wcs)
            # 手动状态：每周期续发闭环机动航路，保证一直在跑、不在终点停车
            if getattr(obj, '_ly_sam_moving', False):
                if free is not True:
                    try:
                        blat, blon = getattr(obj, '_ly_patrol_base',
                                             (float(getattr(obj,'Lat',0) or 0),
                                              float(getattr(obj,'Lon',0) or 0)))
                        obj.plotted_course(self._sam_loop_course(blat, blon))
                        obj.set_desired_speed(self.PATRIOT_SPEED_KMH)
                        obj.set_throttle(Throttle.Full)
                    except Exception:
                        pass
                    continue
                obj._ly_sam_moving = False
            if free is None:
                continue
            prev = getattr(obj, '_ly_wcs_free', None)
            obj._ly_wcs_free = free
            if prev is None:
                continue                     # 首个已知值 -> 只建基线
            if prev == free:
                continue                     # 未变化
            try:
                lat = float(getattr(obj, 'Lat', 0.0) or 0.0)
                lon = float(getattr(obj, 'Lon', 0.0) or 0.0)
                if free:
                    # 自由开火 -> 停车 + 开雷达 + 对空自由开火
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
                    try:
                        obj.doctrine_switch_radar(True)
                    except Exception:
                        pass
                    try:
                        obj.doctrine_weapon_control_status_air(
                            WeaponControlStatus.Free)
                    except Exception:
                        pass
                    self._log('info', '爱国者[%s] 条令=自由开火 -> 停车+开雷达+自由开火' % name)
                else:
                    # 仅限手动开火 -> 关雷达 + 附近来回机动
                    # 记住机动基点，避免每周期漂移
                    if getattr(obj, '_ly_patrol_base', None) is None:
                        obj._ly_patrol_base = (lat, lon)
                    blat, blon = obj._ly_patrol_base
                    loop = self._sam_loop_course(blat, blon)
                    try:
                        obj.doctrine_switch_radar(False)
                    except Exception:
                        pass
                    try:
                        obj.hold_positon(False)
                    except Exception:
                        pass
                    obj.plotted_course(loop)
                    try:
                        obj.set_desired_speed(self.PATRIOT_SPEED_KMH)
                    except Exception:
                        pass
                    try:
                        obj.set_throttle(Throttle.Full)
                    except Exception:
                        pass
                    obj._ly_sam_moving = True
                    self._log('info', '防空[%s] 条令=手动 -> 关雷达+闭环机动' % name)
                switched += 1
            except Exception as e:
                self._log('error', '防空[%s] 条令联动失败: %s' % (name, e))
        self._poll_summary(polled)
        return switched

    def initial_patriots(self, situation):
        """
        爱国者**开局即进入"静默机动"状态**：
          关闭雷达 + 在附近一小段路里加速来回跑。

        这是选手要求的开局姿态：不要一上来就开雷达站着（会被反辐射武器盯上），
        而是关雷达机动；等选手把条令改成"自由开火"，再停车+开雷达+自由开火。

        同时把内部状态标成"手动"(_ly_wcs_free=False)，这样：
          · 开局不会有多余的切换动作；
          · 只有选手**真的改过**条令才会触发（而且可来回切换多次）。

        :param situation: tuple, (units dict, contacts dict)
        :return: int, 处理成功的单元数
        """
        ok = 0
        for name, obj in self._get_units_by_keys(situation, self.SAM_UNIT_KEYS):
            try:
                lat = float(getattr(obj, 'Lat', 0.0) or 0.0)
                lon = float(getattr(obj, 'Lon', 0.0) or 0.0)
                obj._ly_patrol_base = (lat, lon)
                # 关雷达（静默）
                try:
                    obj.doctrine_switch_radar(False)
                except Exception:
                    pass
                # 附近往返机动
                loop = self._sam_loop_course(lat, lon)
                try:
                    obj.hold_positon(False)
                except Exception:
                    pass
                obj.plotted_course(loop)
                try:
                    obj.set_desired_speed(self.PATRIOT_SPEED_KMH)
                except Exception:
                    pass
                try:
                    obj.set_throttle(Throttle.Full)
                except Exception:
                    pass
                # 基线 = 手动（与开局姿态一致）
                obj._ly_wcs_free = False
                obj._ly_sam_moving = True
                ok += 1
                self._log('info', '防空[%s] 开局=关雷达+闭环机动（待选手改自由开火）' % name)
            except Exception as e:
                self._log('error', '爱国者[%s] 开局静默机动失败: %s' % (name, e))
        self._log('info', '爱国者开局静默机动完成 %d 个' % ok)
        return ok

    # ==================================================================
    # 局内初始化
    # ==================================================================
    def initial(self, situation):
        """
        每局推演开始前调用一次，用于赛前规划：条令设置、挂载设置、任务创建等。

        :param situation: tuple, (units dict, contacts dict)
        :return: None
        """
        # ---------------- 启动自检：关键常量/方法是否齐备 ----------------
        # 目的：我此前多次用脚本批量改代码时**误删了相邻的配置块**
        #       （如 MID_PATROLS、LAUNCHER_SALVO_BY_UNIT），
        #       导致任务静默创建失败、WRA 不生效，而现象看起来与改动无关。
        #       这里在开局做一次显式检查，缺什么直接打 ERROR 日志，便于立刻发现。
        try:
            missing = []
            want_attrs = (
                'STRIKE_MISSIONS', 'CAR_SHIP_MISSIONS', 'MID_PATROLS',
                'NORTH_SHIP_PATROLS', 'LAUNCHER_SALVO_BY_UNIT',
                'LAUNCHER_WRA_TARGET_TYPES', 'STRIKE_WRA_BY_UNIT',
                'LAUNCHER_UNIT_KEYS', 'BOL_STRIKES', 'MISSION_NO_USE_WRA',
                'ANTI_SHIP_PLT_NO_USE', 'ARMOR_CONVOYS', 'SURFACE_TARGET_TYPES_CORE',
            )
            want_methods = (
                'apply_launcher_wra', 'apply_anti_ship_plt_no_use',
                'apply_mission_no_use_wra', 'initial_bol_strikes',
                'add_strike_missions', 'add_mid_patrols', 'add_car_ship_missions',
                'add_north_ship_patrols', 'set_side_sam_wra',
                'initial_rush_units', 'add_sweep_missions',
                'set_armor_convoy_courses', 'set_aircraft_loadouts',
                'add_mission_mika', 'add_mission_carrier_killer',
                'add_mission_1_transport', '_build_setup_queue', '_drain_setup',
                'enforce_escape_speed',
            )
            for a_ in want_attrs:
                if not hasattr(self, a_):
                    missing.append('常量 ' + a_)
            for a_ in want_methods:
                if not callable(getattr(self, a_, None)):
                    missing.append('方法 ' + a_)
            if missing:
                self._log('error', '启动自检失败！以下关键项缺失（很可能被误删）：%s'
                          % '、'.join(missing))
            else:
                self._log('info', '启动自检通过：%d 个常量 + %d 个方法齐备'
                          % (len(want_attrs), len(want_methods)))
        except Exception as e:
            self._log('error', '启动自检异常: %s' % e)

        # ---------------- 先装上"每周期指令预算"计数器 ----------------
        #   必须在任何下单之前装，否则前面发的指令不计入本周期的账。
        self._install_order_budget()

        # ---------------- 构建标识（用来确认平台跑的是不是最新代码）----------------
        #   🔴 平台是在**开局那一刻**把本文件加载进进程的：
        #      改了代码**必须重新开一局**才生效；同一局中途改代码不会起作用。
        #      在日志里搜 AGENT_BUILD 即可确认当前跑的是哪一版。
        self._log('info', 'AGENT_BUILD=2026-10-14-1600 '
                          '（猛冲到位必停车 + 速度档 50.5 适配低上限单元 + '
                          '开局设置 initial 内发完 + 10秒窗口节流 + 任务对象重绑 + '
                          'A~D/左中右 提速 + 潜艇浅水待机）')

        # ---------------- 修改总条令 ----------------
        # 对空/对海/对潜/对地：限制开火（Hold = 仅限手动开火）
        # 攻击时不忽略计划航线、被攻击时不忽略电磁管控
        # 干扰机与声呐打开
        # 燃油状态-返航、武器状态-返航：否（不因燃油/武器状态自动返航）
        # 武器状态-预先规划：任务武器耗光，允许使用航炮
        rule = {
            # 交战规则：限制开火（仅限手动开火）
            'weapon_control_status_air': WeaponControlStatus.Hold,
            'weapon_control_status_surface': WeaponControlStatus.Hold,
            'weapon_control_status_subsurface': WeaponControlStatus.Hold,
            'weapon_control_status_land': WeaponControlStatus.Hold,
            'ignore_plotted_course': IgnorePlottedCourseWhenAttacking.No,

            # 电磁管控
            'ignore_emcon_under_attack': IgnoreEMCONUnderAttack.No,
            'switch_oecm': True,     # 干扰机：打开
            'switch_sonar': True,    # 声呐：打开

            # 燃油 / 武器返航规则
            'fuel_state_rtb': FuelStateRTB.No,
            'weapon_state_planned': WeaponStatePlanned.WinchesterUseAirGuns,
            'weapon_state_rtb': WeaponStateRTB.No,

            # 加油/补给：不允许（全局）
            'doctrine_refuel': ERefuel.No,
        }
        self.set_rules(rule)          # 12 条

        # ================== 第三步：飞机挂载 ==================
        # 🔴 必须在战前规划阶段设置，此时才会立即完成挂载（准备时间 0）；
        #    这一项**不能**延后到 step()，否则飞机会有准备时间。
        self.set_aircraft_loadouts(situation)   # 16 条

        # ==================================================================
        # 开局设置队列：**在 initial() 里一次发完**
        #
        #   🔴 实战教训（本盘日志铁证）：
        #      战前规划阶段平台**可能很久才调用一次 step()** ——
        #      实测 initial 于 14:46:10 结束（队列还剩 12 项），
        #      下一次决策直到 14:48:47 才来（隔了 2 分 37 秒），
        #      于是 D/左/中/右 等任务要等开局后才建好 ✗。
        #      "分周期慢慢发"这条路在规划阶段根本走不通。
        #
        #   做法：initial() 里把整个队列发完；
        #         发送速率由 _OrderBudget 的**真·滚动 10 秒窗口节流**保证
        #         （窗口内将超 460 条就 sleep 到窗口滑出），
        #         所以平台看到的永远是"任意 10 秒 ≤460 条"，
        #         一条都不会被取消；900 余条约 20 秒发完，远在规划窗口内。
        #         step() 里仍保留 drain 作为兜底（万一 initial 被打断）。
        # ==================================================================
        self._setup_queue = self._build_setup_queue(situation)
        try:
            # 本周期不设"每周期条数上限"和"每周期睡眠上限"：
            #   真正的限流由窗口节流负责（sleep 到窗口滑出，≤460/10s）。
            self._order_budget.hard_limit = 10 ** 9
            self._order_budget.cycle_sleep_cap = 10 ** 9
            self._drain_setup(limit=10 ** 9)
        finally:
            self._order_budget.hard_limit = self.CYCLE_ORDER_BUDGET
            self._order_budget.cycle_sleep_cap = \
                self._order_budget.MAX_SLEEP_PER_CYCLE

        # ==================================================================
        # 以下所有任务创建/条令/WRA 都已移入 _build_setup_queue()，
        # 由 _drain_setup() 在每个周期按指令预算分批下发（避免 500 条丢包）。
        # ==================================================================

        # ========== 一次性诊断：打出态势里的真实字段名（只读，不占指令）==========
        try:
            self._dump_unit_keys_once(situation)
        except Exception as e:
            self._log('error', '态势字段诊断异常: %s' % e)

        # ================== 挂载诊断（一次性，便于核对 mount/weapon）==========
        try:
            self._dump_weapon_mounts(situation, ('邦克山', '阿利伯克'))
        except Exception as e:
            self._log('error', '挂载诊断异常: %s' % e)

        self._log('info', 'initial game 完成（本周期下发 %d 条，队列剩余 %d 项）'
                  % (self._order_budget.used, len(self._setup_queue)))

    # ==================================================================
    # 每周期指令预算：安装 / 组队 / 分批下发
    # ==================================================================
    def _install_order_budget(self):
        """
        安装每周期指令计数器（只包一次），并清零本周期用量。

        🔴 关键：**单元对象也各持一份 `_game_server` 引用**（框架在解析态势时
           赋的），如果只换 `self._game_server`，那么
           "逐单元条令 / 逐单元 WRA / 雷达开关机" 这些指令会绕过计数
           （实测漏计 40%+，预算就形同虚设）。所以这里把所有本方单元对象
           （飞机/舰船/潜艇/卫星/地面/武器/编组）的引用一并换掉。

        :return: _OrderBudget
        """
        if not isinstance(getattr(self, '_game_server', None), _OrderBudget):
            self._order_budget = _OrderBudget(self._game_server,
                                              self.CYCLE_ORDER_BUDGET)
            self._game_server = self._order_budget
            n = self._rebind_unit_servers(self._order_budget)
            self._log('info', '已安装每周期指令预算：硬上限 %d 条/周期，'
                              '重绑 %d 个单元对象' % (self.CYCLE_ORDER_BUDGET, n))
        else:
            self._order_budget = self._game_server
        self._order_budget.reset(self.CYCLE_ORDER_BUDGET)
        return self._order_budget

    def _rebind_unit_servers(self, budget):
        """
        把本方**单元对象**和**任务对象**的 _game_server 都指向计数器，
        保证指令不绕过计数。

        🔴 任务对象也必须重绑（老师指出）：`missions_obj` / `_created_missions`
           里的任务对象各自持有 `_game_server`，任务级 `SetMission` /
           `SetDoctrine` / 任务 WRA 都是走它们自己那份引用的 ——
           只重绑单元的话，这些指令会绕过计数（预算形同虚设）。

        :param budget: _OrderBudget
        :return: int, 重绑成功的对象数
        """
        n = 0

        def _bind(obj):
            try:
                obj._game_server = budget
                return 1
            except Exception:
                return 0

        # ---- 1) 单元对象 ----
        for attr in ('aircrafts', 'ships', 'submarines', 'satellites',
                     'facilitys', 'weapons', 'groups'):
            coll = getattr(self, attr, None)
            if isinstance(coll, dict):
                for obj in list(coll.values()):
                    n += _bind(obj)
        # ---- 2) 任务对象（含护航任务子对象）----
        seen = set()
        for attr in ('missions_obj', '_created_missions', 'missions',
                     '_mission_objects', '_escort_missions'):
            coll = getattr(self, attr, None)
            objs = []
            if isinstance(coll, dict):
                objs = list(coll.values())
            elif isinstance(coll, (list, tuple, set)):
                objs = list(coll)
            for obj in objs:
                if obj is None or id(obj) in seen:
                    continue
                seen.add(id(obj))
                n += _bind(obj)
                # 任务对象上挂的护航/子任务对象
                for sub_attr in ('escort', 'escort_mission', 'mission',
                                 'sub_missions'):
                    for sub in ([getattr(obj, sub_attr, None)]
                                if not isinstance(getattr(obj, sub_attr, None),
                                                  (list, tuple, set))
                                else list(getattr(obj, sub_attr))):
                        if sub is not None and id(sub) not in seen:
                            seen.add(id(sub))
                            n += _bind(sub)
        return n

    def _build_setup_queue(self, situation):
        """
        构造"开局设置"队列：[(标签, 预估条数, 方法, 参数), ...]。

        顺序约束（**不能乱**）：
          · "任务统一补条令 / 任务武器规则 / 发射车 WRA" 必须排在
            **所有任务都建完之后**（它们要遍历任务对象）；
          · 总条令与飞机挂载已在 initial() 里直接下发，不在此队列。

        预估条数来自离线实测（真实 113 单位编成），用于"整项放不下就顺延下周期"，
        避免任务建到一半被截断。

        :param situation: tuple, (units dict, contacts dict)
        :return: list
        """
        s = situation
        return [
            # ---- 侧级条令 / WRA（最先，便宜且关键）----
            ('总条令-中距弹WRA',     8, self.set_side_air_wra,        ()),
            ('总条令-防空弹WRA',    58, self.set_side_sam_wra,        ()),
            ('五艘水面舰条令',      20, self.set_ship_doctrines,      (s,)),
            # ---- 任务创建 ----
            ('任务1-运输机支援',    10, self.add_mission_1_transport, (s,)),
            ('任务一~九',          165, self.add_all_step4_missions,  (s,)),
            ('任务十~十九',        135, self.add_all_step5_missions,  (s,)),
            ('15_航母护航',         23, self.add_mission_15_carrier_guard, (s,)),
            ('扫地#1/#2',           20, self.add_sweep_missions,      (s,)),
            ('A~D/左中右支援任务', 125, self.add_car_ship_missions,   (s,)),
            ('北船1/北船2',         46, self.add_north_ship_patrols,  (s,)),
            ('中1/中2',             50, self.add_mid_patrols,         (s,)),
            ('潜艇跑',              17, self.add_mission_submarine_run, (s,)),
            ('米卡',                17, self.add_mission_mika,        (s,)),
            ('航母杀手',            23, self.add_mission_carrier_killer, (s,)),
            # ---- 单元机动（晚一点无妨）----
            ('开局猛冲单元',         9, self.initial_rush_units,      (s,)),
            ('装甲车队航线',        28, self.set_armor_convoy_courses, (s,)),
            # ---- 打击任务（必须在"统一补条令"之前）----
            ('A船~E船打击任务',     20, self.add_strike_missions,     (s,)),
            # ---- 任务级条令与武器规则（必须在所有任务建完之后）----
            ('任务统一补条令',      40, self.apply_unified_mission_doctrine, ()),
            ('任务武器规则②③④⑤',   20, self.apply_mission_no_use_wra, (s,)),
            ('反舰导弹排不使用武器', 5, self.apply_anti_ship_plt_no_use, (s,)),
            ('发射车反舰WRA',       20, self.apply_launcher_wra,      (s,)),
        ]

    def _drain_setup(self, reserve=0, limit=None):
        """
        按本周期指令预算，尽量多发"开局设置"队列；放不下的整项留到下个周期。

        · 只采用"整项发完"的粒度：预估条数放不下就 break（绝不半途截断任务创建）；
        · 万一预估偏低真的触到硬上限（_OrderBudgetExceeded），
          抛掉该项并报错，避免下一周期重复建任务；
        · step() 每周期都会调用它，直到队列清空。

        :param reserve: int, 给本周期"其它指令"（如 step() 里的 BOL 打击）预留的条数
        :param limit: int 或 None, 本周期的条数上限；
                      None = 用 CYCLE_ORDER_BUDGET（step() 的正常节奏）；
                      initial() 会传一个很大的值，让整个队列一次发完
                      （速率由 _OrderBudget 的 10 秒滚动窗口节流保证）。
        :return: int, 本周期完成的项数
        """
        q = getattr(self, '_setup_queue', None)
        budget = getattr(self, '_order_budget', None)
        if not q or budget is None:
            return 0
        # 注意：本函数**不重置**计数器 —— initial() 里前面已发的 28 条要计入
        # 同一个周期；每个 step() 由调用方先 reset()。
        base = self.CYCLE_ORDER_BUDGET if limit is None else int(limit)
        limit = max(0, base - int(reserve))
        done = 0
        while self._setup_queue:
            label, est, fn, args = self._setup_queue[0]
            if budget.used + est > limit:
                self._log('info', '本周期已下发 %d 条（预算 %d，预留 %d），'
                                  '下一项[%s]约需 %d 条，顺延到下个周期（队列剩余 %d 项）'
                          % (budget.used, self.CYCLE_ORDER_BUDGET, reserve,
                             label, est, len(self._setup_queue)))
                return done
            try:
                fn(*args)
            except _OrderBudgetExceeded:
                self._setup_queue.pop(0)
                self._log('error', '[%s] 预估偏低、触到本周期硬上限 %d 条，'
                                   '已跳过该项以免重复下发（可能有遗漏）'
                          % (label, self.CYCLE_ORDER_BUDGET))
                return done
            except Exception as e:
                self._log('error', '%s 执行异常: %s' % (label, e))
            self._setup_queue.pop(0)
            done += 1
            self._log('info', '开局设置[%s] 已下发（本周期累计 %d 条，队列剩余 %d 项）'
                      % (label, budget.used, len(self._setup_queue)))
        else:
            self._log('info', '开局设置队列已全部下发完毕（本周期 %d 条）'
                      % budget.used)
        return done

    def add_mission_1_transport(self, situation):
        """
        任务1：运输机支援（C-5M 型运输机 #1/#2 摆渡到阵位航线）。

        说明：原先这段代码直接写在 initial() 里，现抽成方法以便放进
        "开局设置队列"分批下发。

        :param situation: tuple, (units dict, contacts dict)
        :return: SupportMission 或 None
        """
        mission_1_name = "运输机支援"  # 任务名
        # 阵位航线参考点（纬度，经度），按顺序排列
        mission_1_airline = [(44.632810, -13.589059), (43.797489, -9.629276)]
        mission_1_rule = {
            'one_third_rule': False,          # 1/3 规则：不勾选
            'flight_size': EscortFlightSize.SingleAircraft,  # 编队规模：单机
            'use_flight_size': False,         # 飞机数低于编队规模要求不能起飞：不勾选
            # 其余项（油门、高度、加油、仅限一次等）未指定，采用平台默认值，
            # 如需下发在封装函数支持后追加对应 key，例如：
            # 'throttle_and_altitude': [Throttle.Cruise, Throttle.Loiter, None, None],
        }
        # 单元名取自平台实际态势日志（THSituationFull），注意是"C-5M型 运输机"
        mission_1_unit = ['C-5M型 运输机#1', 'C-5M型 运输机#2']
        mission_1_time = [None, None]  # 任务启动、结束时间，None 表示不设置
        # 武器状态-返航：否（到达武器状态不返回基地）
        # 武器状态-预先规划：任务武器耗光，允许使用航炮（推荐）
        return self.add_set_support_mission(
            situation, mission_1_name, mission_1_airline, mission_1_rule,
            mission_1_unit, weapon_state_rtb=WeaponStateRTB.No,
            weapon_state_planned=WeaponStatePlanned.WinchesterUseAirGuns,
            time_lab=mission_1_time)

    # ==================================================================
    # 每步决策
    # ==================================================================
    def step(self, time_elapse, situation):
        """
        每个决策间隔自动调用一次（self.agent_decision_time，默认 30 秒仿真时间）。

        :param time_elapse: int, 推演已过时间（秒）
        :param situation: tuple, (units dict, contacts dict)
        :return: None
        """
        # ================== 继续下发"开局设置"队列（每个周期有独立配额）=======
        #   initial() 因为 agentOrderCountLimit=500 不能一次发完（870 条），
        #   剩余项在这里每周期按预算继续发，直到队列清空。
        #   注意：新周期 = 新配额，先把计数器清零。
        try:
            if getattr(self, '_order_budget', None) is not None:
                self._order_budget.reset(self.CYCLE_ORDER_BUDGET)
                # 🔴 每步重绑：态势每步可能重建单元/任务对象（各自持真实
                #    server 引用），不重绑它们就会绕过计数（老师指出）。
                self._rebind_unit_servers(self._order_budget)
            # 给本周期后面的 BOL 打击预留 60 条，避免队列把配额吃干净
            self._drain_setup(reserve=60)
        except Exception as e:
            self._log('error', '开局设置队列下发异常: %s' % e)

        # ================== A~D 撤退任务：最大速度保障 ==================
        #   队列发完之后才启用（它每周期要问 4 个任务，占少量配额）。
        #   选手手动把单元转进 A~D 后，这里会在下一个周期把速度提到最大。
        if not getattr(self, '_setup_queue', None):
            try:
                self.enforce_escape_speed(situation)
            except Exception as e:
                self._log('error', 'A~D 撤退提速看护异常: %s' % e)
            # 猛冲单元到位后停车（与提速互斥：已被 A~D/左中右 接手的不碰）
            try:
                self.rush_units_park(situation)
            except Exception as e:
                self._log('error', '猛冲单元停车看护异常: %s' % e)

        # ================== 战斧打击：已改为完全手动 ==================
        # 按要求不再自动设置航迹、也不自动开火；选手在对局中手动决定。
        # 因此这里不再调用 tomahawk_strike_nk_airfield()。

        # 🔴 AIM / 发射车 / 154 的 WRA 都已在 initial() 里下发过一次，
        #    平台上是**永久生效**的，step() 里**不再重发**。
        #    step() 只负责 BOL（本身有去重与次数上限）。

        # 注：阿利伯克打机场改为 **BOL + 坐标 + 必经航路点**（见 BOL_STRIKES）。
        #     原来用"指定目标 contact"的方式不可行：开局情报里没有机场，
        #     锁定不了 contact（日志实证：当前情报里没有找到任何目标）。
        # ================== 初始 BOL 纯防卫打击（带重试）==================
        # 🔴 为什么每周期都尝试：
        #   平台限制 agentOrderCountLimit=500 条/周期。initial() 阶段要下发
        #   数百条 WRA + 建任务 + 分配单元，配额会被占满，导致 BOL 指令被
        #   "智能体指令条数超出数量限制，已被取消下发"（日志已多次实证）。
        #   故改为：**每个决策周期都尝试**，已成功的记入 _ly_bol_done_keys
        #   不再重发；被丢弃的下一周期自动重试，直到全部成功。
        #   这样即使某周期配额不足，也一定会在后续周期补发，不会"丢包"。
        try:
            self.initial_bol_strikes(situation)
        except Exception as e:
            self._log('error', '初始 BOL 打击异常: %s' % e)

        # ================== 条令联动：已按要求停用 ==================
        # 按要求：爱国者、地空导弹连#1#2、以及所有霍克**执行原有航线**，
        # 由 左/中/右 三个支援任务 + 霍克原地关雷达来管，不再由条令联动去
        # 停车/开雷达/附近机动 —— 那会把任务设定的航线反复改掉。
        # 发射车（海马斯/反舰导弹排/LUCAS）也改为只按 A~D 支援任务的航线走，
        # 不再自动向南撤离。
        # 如需恢复，把下面两行注释打开即可。
        # self.launcher_doctrine_toggle(situation)
        # self.patriot_doctrine_toggle(situation)
