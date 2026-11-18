# -*- coding:utf-8 -*-
r"""
监听智能体（人类意图 → 平台动作）
==================================
低空导弹二态按钮的**执行端**：把操作手在按钮页面上的一次点击，转译成平台指令。
设计依据：设计报告 1.3 节「决策协同」——人的指令不经过界面逐条点选，而是由监听
智能体接收、校验、转译；监听智能体不做任何战术判断。

二态语义（用户草图）
--------------------
======================  ==========================  ==========================
                        **打击模式 strike**          **前进模式 move**
======================  ==========================  ==========================
停车 / 机动              清航路 + 保持阵位 + 速度 0   保持阵位取消 + 正北航路
                        + 油门 FullStop             + 油门 Full + 期望 50 km/h
雷达                    开（条令层 + 传感器层双下）  关（同上，先关后走）
交战                    等目标进 0.6·Dmax 由平台开火  不交战（雷达关，无目标可打）
暴露                    高（辐射 + 静止）            低（静默 + 移动）
======================  ==========================  ==========================

上位条令不变：受到攻击时忽略电磁管控 = 否、自由开火、自动规避 = 否。本智能体
**不修改**这些条令字段，只下发单元级动作（开关雷达、停车/机动、航路点、油门）。

本文件做什么 / 不做什么
-----------------------
* 做：每决策周期从命令文件尾部读**新行**，按 ``seq`` 幂等执行，写一行回执
      （含按下墙钟、回执墙钟、往返时延、当时仿真时刻、实际下发的指令清单）。
* 不：不发弹、不选目标、不改条令。发弹仍由平台按「自由开火 + 雷达开」自动执行，
      0.6·Dmax 只作为一个**只读提示**写进回执（见 ``_fire_note``），便于事后
      核对"按下去那一刻到底该不该打"。
* 不：不新开线程。读文件与下发指令都在 ``step`` 线程里做——平台指令由战术智能体
      与监听智能体共用同一个发送通道，另起线程去发有抢占风险（未验证）。
      代价是**往返时延的下限 = 一个决策间隔**（5 推演秒，10 倍速 ≈ 0.5 墙钟秒）。

命令文件 / 回执文件（一次点击一行 JSON）
----------------------------------------
命令（页面服务写，监控智能体读）::

    {"seq":1,"t_wall":1794930000.12,"action":"strike|move","unit":"捷羚地空导弹排#1"}

回执（监听智能体写，页面与 operator_sim 读）::

    {"seq":1,"t_wall_press":1794930000.12,"t_wall_ack":1794930000.71,
     "latency_ms":590.4,"sim_t":1210.0,
     "orders":["捷羚地空导弹排#1 clear_plotted_course()", …],
     "unit":["捷羚地空导弹排#1"],"action":"strike","ok":true,"note":"...",
     "wait_ms":540.0,"apply_ms":50.4}

``latency_ms = wait_ms + apply_ms``：``wait_ms`` 是"点击 → 下一个决策周期"的
排队（下限=一个决策间隔），``apply_ms`` 才是转译与下发本身的开销。实验里要分开
看：前者由推演倍速与决策间隔决定，后者才是这套链路要证明的东西。
``orders`` 是**逐条**平台指令（不是在一次点击里合并后的字符串），所以
``len(orders)`` 就是"这一次按钮等于多少条手工指令"。

默认路径 ``D:/LingYi/exp/button/cmd.jsonl`` / ``.../ack.jsonl``，可用环境变量
``PI_BUTTON_CMD`` / ``PI_BUTTON_LOG`` 覆盖。

接入方法（与主智能体并行挂同一推演方）
--------------------------------------
客户端「智能体调度 → 智能体编辑 → ＋」选本文件，出现 ``Agent`` 后启动。
必须用 ``RuleAgentBase``：只继承 Player 时平台拿不到 ``is_done`` /
``deduction_end``，智能体会被当成"已结束"（monitor-agent README 实测结论）。

与战术智能体的冲突（部署前必读）
--------------------------------
本智能体与 ``SamBattalionDefense`` 会**同时写**同一个单元的雷达/油门/航路。
跑按钮实验时，主智能体的地导自卫规则必须关掉（``SamBattalionDefense.ENABLE =
False``），否则两边互相覆盖，测到的时延与暴露时长都不可信。

可调参数（类属性，改一个词即可回退）
------------------------------------
* ``UNIT_KEYWORDS``       受控单元的关键字（不写死单元名；匹配不上会把候选名打进日志与回执）
* ``INITIAL_MODE``        开局姿态，默认 ``'move'``（草图：初始状态向正北、全速、关雷达）；``''`` = 不动
* ``MOVE_SPEED_KMH``      前进模式期望速度（km/h）
* ``MOVE_DISTANCE_KM``    每次正北航段的长度（km）
* ``REASSERT_CYCLES``     每 N 个周期重发一次当前模式的雷达状态（0 = 关闭自愈）
* ``EMCON_RELEASE``       是否下发 ``EMCON_Obey_doctrine(False)``，让 ``switch_radar`` 不被条令覆盖
* ``FIRE_RATIO``          0.6·Dmax 发弹线（只用于回执里的只读提示）
"""

import json
import logging
import math
import os
import sys
import time
from collections import OrderedDict

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_ai_dir(start):
    """往上找 ``intelligent\\ai``（里面有 engine/LingYi/entitys/player.py）。

    不写死层级：放在 ``ai\\agent\\button`` 还是 ``ai\\button`` 都能自己找对。
    """
    p = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(p, 'engine', 'LingYi', 'entitys', 'player.py')):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            return os.path.dirname(os.path.dirname(os.path.dirname(start)))
        p = parent


_AI_DIR = _find_ai_dir(_HERE)
if _AI_DIR not in sys.path:
    sys.path.insert(0, _AI_DIR)

from engine.LingYi.entitys.agent_base import RuleAgentBase   # noqa: E402

log = logging.getLogger("按钮监听")
log.setLevel(logging.INFO)

DEFAULT_CMD = 'D:/LingYi/exp/button/cmd.jsonl'
DEFAULT_ACK = 'D:/LingYi/exp/button/ack.jsonl'


# ======================================================================
# 小工具（与监控/地导智能体同一套写法，便于互相对照）
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


def _km(lat1, lon1, lat2, lon2):
    """两点大圆距离（公里）；参数不全返回 None。"""
    if None in (lat1, lon1, lat2, lon2):
        return None
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2.0) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2)
    a = min(1.0, max(0.0, a))
    return 2.0 * 6371.0 * math.asin(math.sqrt(a))


def _shift(lat, lon, bearing_deg, dist_km):
    """从 (lat, lon) 按方位角走 dist_km 的落点。"""
    br = math.radians(bearing_deg)
    d = dist_km / 6371.0
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(d)
                   + math.cos(p1) * math.sin(d) * math.cos(br))
    l2 = l1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(p1),
                         math.cos(d) - math.sin(p1) * math.sin(p2))
    return (math.degrees(p2), (math.degrees(l2) + 540.0) % 360.0 - 180.0)


def _env_flag(name, default):
    """读布尔环境变量（'0'/'false'/'no'/'off' 为假，其余非空为真）。"""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() not in ('0', 'false', 'no', 'off')


def _pct(values, p):
    """线性插值分位数（p 取 0~100）；空列表返回 None。"""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo = int(math.floor(k))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


# ======================================================================
# 监听智能体
# ======================================================================
class PiButtonListener(RuleAgentBase):
    """人类意图层：把一次按钮点击转译成一组平台动作。"""

    # ---------------------------------------------------------------- 频率
    DECISION_SEC = 5               # 决策间隔（推演秒）。5 s 是比赛规则允许的最小值

    # ---------------------------------------------------------------- 受控单元
    # 不写死单元名：按关键字匹配（'捷羚地空导弹排#1' 这类地导单元都命中）
    UNIT_KEYWORDS = ('地空导弹排', '地空导弹连', '地空导弹营', '地空导弹分队',
                     'sam bty', 'sam coy')

    # ---------------------------------------------------------------- 姿态参数
    INITIAL_MODE = os.environ.get('PI_INITIAL_MODE', 'move')   # '' = 开局不干预
    MOVE_SPEED_KMH = 50.0          # 前进模式期望速度（地面单元上限约 55.6）
    MOVE_DISTANCE_KM = 50.0        # 每段正北航路的长度
    MOVE_BEARING_DEG = 0.0         # 前进方向：正北
    REASSERT_CYCLES = 20           # 每 N 周期重发当前模式的雷达状态（0 = 关闭自愈）
    EMCON_RELEASE = _env_flag('PI_EMCON_RELEASE', True)   # 释放条令电磁管控

    # ---------------------------------------------------------------- 只读提示
    FIRE_RATIO = 0.6               # 发弹线 = 0.6 * Dmax（报告 2.3.5 的 3/5 Dmax）
    MIN_SAM_RANGE_KM = 5.0         # 判定"这型弹算对空弹"的最低对空射程
    MIN_AIR_ALT_M = 50.0           # 低于此高度不算空中目标（地面回波）

    # ---------------------------------------------------------------- 通道
    SEEN_KEEP = 5000               # 记住多少个已处理的 seq（幂等表上限）
    MSG_ENABLE = True              # 往客户端"智能体输出"推一行

    # ==================================================================
    def __init__(self, side_name="红方", *args, **kwargs):
        RuleAgentBase.__init__(self, side_name)
        self.side_cn = side_name
        self.agent_type = "PiButtonListener"
        self.agent_decision_time = self.DECISION_SEC
        self.now = 0.0
        self.cycle = 0

        self.cmd_path = os.environ.get('PI_BUTTON_CMD', DEFAULT_CMD)
        self.ack_path = os.environ.get('PI_BUTTON_LOG', DEFAULT_ACK)
        self._offset = None         # 命令文件已读到的字节位置（None = 还没定位）
        self._seen = OrderedDict()  # 已处理的 seq（幂等）

        self._units = []            # [{'name','guid','obj','lat','lon','dmax',...}]
        self._own_names = []        # 本方全部单元名（匹配失败时列候选）
        self._contacts = {}
        self._lat = []              # 往返时延样本（ms）
        self._press_count = {'strike': 0, 'move': 0}
        self._warned = set()

    # ------------------------------------------------------------------
    def _say(self, level, msg):
        """日志：优先走平台 Player 的 ``_log``（Mission_all_red 用的就是它）。"""
        text = '[按钮监听] %s' % msg
        fn = getattr(self, '_log', None)
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
        self._say(level, msg)

    def _announce(self, text):
        """往客户端「智能体消息输出」推一行（纯文本接口）。"""
        if not self.MSG_ENABLE:
            return
        fn = getattr(self, 'agent_message_text', None)
        if not callable(fn):
            return
        try:
            fn(text)
        except Exception as e:
            self._warn_once('announce', '消息栏推送失败: %s' % e)

    # ------------------------------------------------------------------
    # 枚举惰性解析（宿主未必 from global_util import *，自己兜住）
    # ------------------------------------------------------------------
    def _enum(self, name, member, fallback):
        try:
            mod = sys.modules.get(type(self).__module__)
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

    # ==================================================================
    # 一、开局：解析受控单元 + 运行期反查 Dmax
    # ==================================================================
    def setup(self, situation):
        """解析受控单元，逐个反查对空射程 Dmax；返回自检摘要。"""
        try:
            self._units = self._resolve_units(situation)
        except Exception as e:
            self._say('error', '单元解析异常: %s' % e)
            self._units = []
        for b in self._units:
            try:
                b['dmax'], b['range_src'] = self._probe_dmax(b)
            except Exception as e:
                b['dmax'], b['range_src'] = None, '反查异常:%s' % e
        rep = {
            '受控单元': [b['name'] for b in self._units],
            'Dmax': dict((b['name'], None if b['dmax'] is None
                          else round(b['dmax'], 1)) for b in self._units),
            '射程来源': dict((b['name'], b['range_src']) for b in self._units),
            '命令文件': self.cmd_path,
            '回执文件': self.ack_path,
        }
        self._say('info', '初始化完成：%s' % rep)
        if not self._units:
            self._say('warning', '未解析到受控单元（关键字=%s）。本方单元候选：%s'
                      % (self.UNIT_KEYWORDS,
                         '、'.join(self._own_names[:40]) or '（态势为空）'))
        return rep

    def _resolve_units(self, situation):
        """按关键字从态势里挑受控单元；同时记下本方全部单元名备查。"""
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return []
        out, names = [], []
        for guid, u in units.items():
            if not isinstance(u, dict):
                continue
            name = str(u.get('name', '') or '')
            if name:
                names.append(name)
            bare = _norm(name)
            if not any(_norm(k) in bare for k in self.UNIT_KEYWORDS):
                continue
            g = u.get('guid') or guid
            obj = self.get_unit(g)
            if obj is None:
                self._say('warning', '[%s] 态势里有、get_unit 取不到对象，跳过' % name)
                continue
            out.append({
                'name': name, 'guid': g, 'obj': obj,
                'lat': _to_float(u.get('lat', u.get('latitude'))),
                'lon': _to_float(u.get('lon', u.get('longitude'))),
                'dmax': None, 'range_src': '',
                'mode': None,            # None / 'strike' / 'move'
                'radar': None,           # 本智能体最后一次下发的雷达状态
                'radar_cycle': None,     # 最后一次下发雷达时的周期号
                'emcon_released': False,
            })
        out.sort(key=lambda b: b['name'])
        self._own_names = sorted(names)
        return out

    def _probe_dmax(self, b):
        """
        运行期反查 Dmax：扫该单元**真实挂载**的全部武器，逐型查对空射程取最大者。

        不写死武器 ID，也**不按名称兜底**（名称表就是另一种写死）：查不到就返回
        None，回执里标"发弹线未知"，并把真实挂载打进日志，供人工核对。
        挂载的遍历方式与 SamBattalionDefense 一致：model.db 里"设施→挂架→武器"
        的映射不作准，只有单元自己的 Mounts / Magazines / Loadouts 才是真挂载。
        """
        weapons = {}
        for _mount, wid, cnt in self._iter_weapon_recs(b['obj']):
            weapons[wid] = weapons.get(wid, 0) + (cnt or 0)
        best_wid, best = None, None
        for wid in weapons:
            rng = self._weapon_air_range(wid)
            if rng is None or rng < self.MIN_SAM_RANGE_KM:
                continue
            if best is None or rng > best:
                best_wid, best = wid, rng
        if best is None:
            self._say('warning', '%s 未能从挂载反查到对空射程（挂载=%s），'
                                 '回执里发弹线标为未知' % (b['name'], sorted(weapons)))
            return None, '未反查（挂载=%s）' % sorted(weapons)
        return float(best), '挂载反查(武器%s)' % best_wid

    def _iter_weapon_recs(self, unit):
        """遍历单元挂载，yield (挂架DBID, 武器DBID, 当前数量)。"""
        for attr in ('Mounts', 'Magazines', 'Loadouts'):
            cont = getattr(unit, attr, None)
            if not isinstance(cont, dict):
                continue
            for mk, mv in cont.items():
                if not isinstance(mv, dict):
                    continue
                comp = mv.get('Component')
                mount = _to_int(comp.get('DBID')) if isinstance(comp, dict) else None
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
        qd = self._query_data()
        if qd is None:
            return None
        try:
            row = qd.get_weapon_info(int(wid))
            if row:
                return _to_float(row[0])
        except Exception:
            return None
        return None

    def _query_data(self):
        for mod_name in ('engine.LingYi.entitys.data', 'entitys.data'):
            mod = sys.modules.get(mod_name)
            if mod is not None and hasattr(mod, 'query_data'):
                return mod.query_data
        for mod_name in ('engine.LingYi.entitys.data', 'entitys.data'):
            try:
                mod = __import__(mod_name, fromlist=['query_data'])
                if hasattr(mod, 'query_data'):
                    return mod.query_data
            except Exception:
                continue
        self._warn_once('query_data', '取不到平台 query_data，Dmax 无法反查')
        return None

    # ==================================================================
    # 二、生命周期
    # ==================================================================
    def initial(self, situation):
        """战前规划：解析单元、下发初始姿态（草图：向正北、全速、关雷达）。"""
        try:
            self._prime_offset()
            rep = self.setup(situation)
            mode = str(self.INITIAL_MODE or '').strip().lower()
            if mode in ('strike', 'move'):
                for b in self._units:
                    texts, ok = self._apply(b, mode)
                    self._say('info', '初始姿态 %s → %s（%s）'
                              % (mode, b['name'],
                                 ';'.join(texts) if ok else '有失败，见上'))
            elif mode:
                self._say('warning', 'PI_INITIAL_MODE=%r 无效（只支持 move/strike/空）'
                          % mode)
            self._announce('【按钮】监听就绪：%d 个单元（%s），初始=%s，文件=%s'
                           % (len(self._units),
                              '、'.join(rep.get('受控单元') or []) or '无',
                              mode or '不干预', os.path.basename(self.cmd_path)))
        except Exception as e:
            # 平台把 initial 里的异常当致命错误（整局直接结束），这里必须兜住
            self._say('error', 'initial 异常（已忽略）: %s' % e)
        return None

    def step(self, time_elapse, situation):
        """每决策周期调用一次。整个函数体兜住异常——监听出问题不能连累推演。"""
        try:
            self.now = float(time_elapse or 0.0)
            self.cycle += 1
            self._contacts = situation[1] if isinstance(situation, (tuple, list)) \
                and len(situation) > 1 and isinstance(situation[1], dict) else {}
            if not self._units and self.cycle % 20 == 1:
                self.setup(situation)       # 开局没解析到，每分钟重试一次
            self._refresh(situation)
            n = self._poll_commands()
            kept = self._keep_posture()
            if n or kept or self.cycle % 20 == 0:
                self._say('info', '周期%d t=%ds 处理点击%d 看护%d 状态=%s'
                          % (self.cycle, int(self.now), n, len(kept),
                             self._state_text()))
        except Exception as e:
            self._say('error', '周期%d 监听异常: %s' % (self.cycle, e))
        return None

    def deduction_end(self):
        """推演结束：把点击次数与时延分位数打进日志（实验统计的第一手数据）。"""
        try:
            self._say('info', '推演结束：点击 %d 次（打击%d/前进%d），往返时延 P50=%s ms '
                              'P95=%s ms（n=%d）'
                      % (sum(self._press_count.values()),
                         self._press_count['strike'], self._press_count['move'],
                         _fmt(_pct(self._lat, 50)), _fmt(_pct(self._lat, 95)),
                         len(self._lat)))
            self._announce('【按钮】推演结束：点击%d次，时延P50=%sms P95=%sms'
                           % (sum(self._press_count.values()),
                              _fmt(_pct(self._lat, 50)), _fmt(_pct(self._lat, 95))))
        except Exception as e:
            self._say('warning', '结束统计异常: %s' % e)

    def _state_text(self):
        if not self._units:
            return '无受控单元'
        return '，'.join('%s=%s/雷达%s' % (b['name'], b.get('mode') or '-',
                                         _radar_word(b.get('radar')))
                        for b in self._units)

    def _refresh(self, situation):
        """按态势刷新位置（航路点要用最新的点算，别用开局那一份）。"""
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        if not isinstance(units, dict):
            return
        for b in self._units:
            u = units.get(b['guid'])
            if not isinstance(u, dict):
                for _g, cand in units.items():
                    if isinstance(cand, dict) and str(cand.get('name', '')) == b['name']:
                        u = cand
                        break
            if isinstance(u, dict):
                b['lat'] = _to_float(u.get('lat', u.get('latitude')), b['lat'])
                b['lon'] = _to_float(u.get('lon', u.get('longitude')), b['lon'])

    # ==================================================================
    # 三、读命令（只读新行、按 seq 幂等）
    # ==================================================================
    def _prime_offset(self):
        """
        跳过命令文件里**已有的历史行**：本进程只执行启动之后的新点击。

        命令文件的序号是跨局连续递增的（页面服务与 operator_sim 都按文件里的
        最大值续号），所以"开局从头读"会把上一局留下的点击重放一遍。
        """
        if self._offset is not None:
            return
        try:
            self._offset = os.path.getsize(self.cmd_path)
            self._say('info', '命令通道已就绪：%s（已有 %d 字节，从行尾开始读）'
                      % (self.cmd_path, self._offset))
        except OSError:
            self._offset = 0
            self._say('warning', '命令文件还不存在（首次点击时由页面服务创建）：%s'
                      % self.cmd_path)

    def _poll_commands(self):
        """本周期读到的每条新命令各执行一次；返回成功处理的条数。"""
        n = 0
        for rec in self._read_new_lines():
            try:
                if self._handle(rec):
                    n += 1
            except Exception as e:
                self._say('error', '命令处理异常（已忽略，不影响推演）: %s' % e)
        return n

    def _read_new_lines(self):
        """
        从命令文件 ``self._offset`` 处读增量，只返回**完整行**。

        写到一半的行留到下个周期（不推进 offset），因此页面服务与智能体同时
        写/读也不会解析出半截 JSON。文件被截断或轮转（size < offset）时从头读，
        已处理的 seq 仍由幂等表挡住，不会重复执行。
        """
        if self._offset is None:
            self._prime_offset()
        try:
            size = os.path.getsize(self.cmd_path)
        except OSError:
            return []
        if size < self._offset:
            self._say('warning', '命令文件变小（截断/轮转），从头重读：%s' % self.cmd_path)
            self._offset = 0
        if size == self._offset:
            return []
        try:
            with open(self.cmd_path, 'rb') as f:
                f.seek(self._offset)
                blob = f.read()
        except OSError as e:
            self._say('warning', '读命令文件失败: %s' % e)
            return []
        cut = blob.rfind(b'\n')
        if cut < 0:
            return []
        self._offset += cut + 1
        out = []
        for raw in blob[:cut].split(b'\n'):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw.decode('utf-8', 'replace'))
            except ValueError:
                self._say('warning', '命令文件有非法 JSON 行（已跳过）: %r' % raw[:120])
                continue
            if isinstance(rec, dict):
                out.append(rec)
        return out

    def _handle(self, rec):
        """执行一条命令并写一行回执；返回是否真的执行了（重复 seq 返回 False）。"""
        seq = rec.get('seq')
        if seq is None:
            self._say('warning', '命令缺少 seq（跳过，无法幂等）: %r' % (rec,))
            return False
        key = str(seq)
        if key in self._seen:
            return False                    # 幂等：同一个 seq 只执行一次
        self._seen[key] = 1
        if len(self._seen) > self.SEEN_KEEP:
            self._seen.popitem(last=False)

        t_recv = time.time()
        t_press = _to_float(rec.get('t_wall'))
        action = str(rec.get('action', '') or '').strip().lower()
        targets = self._resolve_target(rec.get('unit'))
        orders, ok, note = [], True, ''
        if action not in ('strike', 'move'):
            ok = False
            note = '未知 action=%r（只支持 strike/move）' % (rec.get('action'),)
        elif not targets:
            ok = False
            note = ('未匹配到单元 unit=%r；候选：%s'
                    % (rec.get('unit'),
                       '、'.join(self._own_names[:20]) or '（开局未解析到本方单元）'))
        else:
            for b in targets:
                texts, good = self._apply(b, action)
                orders.extend(texts)
                ok = ok and good
            note = self._fire_note(targets, action)
            if t_press is None:
                note = ('%s；命令未带 t_wall，时延不可算' % note).strip('；')
            self._press_count[action] = self._press_count.get(action, 0) + 1
        t_ack = time.time()

        def _ms(seconds):
            return round(seconds * 1000.0, 1)

        ack = {
            'seq': seq,
            't_wall_press': t_press,
            't_wall_ack': round(t_ack, 3),
            'latency_ms': (_ms(t_ack - t_press) if t_press is not None else None),
            'sim_t': round(self.now, 1),
            'orders': orders,
            # 以下为排障/统计附加字段
            'unit': [b['name'] for b in targets],
            'action': action,
            'ok': ok,
            'note': note,
            # 时延分解：等一个决策周期（排队）+ 转译下发（本身开销）
            'wait_ms': (_ms(t_recv - t_press) if t_press is not None else None),
            'apply_ms': _ms(t_ack - t_recv),
        }
        self._write_ack(ack)
        if ack['latency_ms'] is not None:
            self._lat.append(ack['latency_ms'])
        self._say('info', '点击 seq=%s %s %s → %s（时延 %s ms = 排队 %s + 转译 %s，'
                          't=%ds，%s）'
                  % (seq, action, ack['unit'] or '-', '成功' if ok else '失败',
                     _fmt(ack['latency_ms']), _fmt(ack['wait_ms']),
                     _fmt(ack['apply_ms']), int(self.now), note or '无提示'))
        if ok:
            self._announce('【按钮】seq%s %s → %s模式（%s ms，%d 条指令）'
                           % (seq, '、'.join(ack['unit']), action,
                              _fmt(ack['latency_ms']), len(orders)))
        else:
            self._announce('【按钮】seq%s 执行失败：%s' % (seq, note or '见日志'))
        return True

    def _resolve_target(self, unit):
        """unit 为空/``*`` 时取全部受控单元；否则精确名优先，再退化到名称包含。"""
        name = str(unit if unit is not None else '').strip()
        if not name or name == '*':
            return list(self._units)
        bare = _norm(name)
        exact = [b for b in self._units if _norm(b['name']) == bare]
        if exact:
            return exact
        return [b for b in self._units
                if bare in _norm(b['name']) or _norm(b['name']) in bare]

    def _write_ack(self, ack):
        """追加一行回执。写失败只告警，绝不外抛。"""
        try:
            d = os.path.dirname(os.path.abspath(self.ack_path))
            if d and not os.path.isdir(d):
                os.makedirs(d, exist_ok=True)
            line = json.dumps(ack, ensure_ascii=False, separators=(',', ':'))
            with open(self.ack_path, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
                f.flush()
        except Exception as e:
            self._say('error', '回执写入失败（seq=%s）: %s' % (ack.get('seq'), e))

    # ==================================================================
    # 四、姿态（二态语义的唯一实现处）
    # ==================================================================
    def _apply(self, b, action):
        """切换到一个姿态；返回 (逐条指令记录 list, 是否全部成功)。"""
        b['mode'] = action
        out = []
        if action == 'strike':
            ok = self._posture_strike(b, out)
        else:
            ok = self._posture_move(b, out)
        return ['%s %s' % (b['name'], t) for t in out], ok

    def _posture_strike(self, b, out):
        """
        打击模式：清航路 → 保持阵位 → 速度 0 → 油门停车 → 开雷达。

        顺序不能换的两处：
        ① **先清航路再停车**：前进时下过航路，只停油门不清航路，单元会继续朝
           旧航路点跑（SamBattalionDefense._recover 的实测结论）；
        ② **停车与开雷达同一次下发**：只停不开等于瞎停，只开不停等于边跑边辐射。
        """
        results = [
            self._order(b, out, 'clear_plotted_course'),
            self._order(b, out, 'hold_positon', True),
            self._order(b, out, 'set_desired_speed', 0),
            self._order(b, out, 'set_throttle', self._throttle('FullStop')),
        ]
        results.append(self._radar(b, out, True))
        return all(results)

    def _posture_move(self, b, out):
        """
        前进模式：关雷达 → 松开阵位 → 正北航路 → 油门全速 + 期望 50 km/h。

        雷达必须先关再走：边跑边辐射等于给反辐射弹指路（报告 2.3.5）。
        """
        results = [self._radar(b, out, False),
                   self._order(b, out, 'hold_positon', False)]
        pt = self._north_point(b)
        if pt is None:
            out.append('plotted_course(跳过:无坐标)')
            results.append(False)
        else:
            results.append(self._order(b, out, 'plotted_course', [pt]))
        results.append(self._order(b, out, 'set_throttle', self._throttle('Full')))
        results.append(self._order(b, out, 'set_desired_speed',
                                   float(self.MOVE_SPEED_KMH)))
        return all(results)

    def _north_point(self, b):
        """从当前位置向正北推 MOVE_DISTANCE_KM 得到一个航路点。"""
        lat, lon = b.get('lat'), b.get('lon')
        if lat is None or lon is None:
            return None
        return _shift(lat, lon, self.MOVE_BEARING_DEG, self.MOVE_DISTANCE_KM)

    def _order(self, b, out, attr, *args):
        """下发一条平台指令，成败都记进 out；返回是否成功。绝不外抛。"""
        obj = b['obj']
        fn = getattr(obj, attr, None)
        if not callable(fn):
            self._say('warning', '%s 平台没有接口 %s' % (b['name'], attr))
            out.append('%s(无此接口)' % attr)
            return False
        try:
            fn(*args)
            out.append('%s(%s)' % (attr, ','.join(_arg_text(a) for a in args)))
            return True
        except Exception as e:
            self._say('warning', '%s %s 失败: %s' % (b['name'], attr, e))
            out.append('%s(失败:%s)' % (attr, e))
            return False

    def _radar(self, b, out, on):
        """
        雷达开关：条令层（EMCON）与传感器层各下一次，成功与否记进 out。

        ``EMCON_Obey_doctrine(False)`` 每个单元只下一次：平台可能因任务条令 /
        电磁管控把雷达改回相反状态，而本地缓存仍记着旧值——实测表现就是
        "停了但雷达没开"（SamBattalionDefense 的注释记录了这条）。
        """
        ok = True
        if self.EMCON_RELEASE and not b.get('emcon_released'):
            if self._order(b, out, 'EMCON_Obey_doctrine', False):
                b['emcon_released'] = True
            else:
                ok = False
        for attr in ('doctrine_switch_radar', 'switch_radar'):
            if not self._order(b, out, attr, bool(on)):
                ok = False
        b['radar'] = bool(on)
        b['radar_cycle'] = self.cycle
        return ok

    def _keep_posture(self):
        """
        姿态看护：按当前模式重发一次雷达状态；前进模式航路为空时再规划一段。

        只为抗"平台/条令把雷达悄悄改回去"这一类重置，不改语义。默认每
        ``REASSERT_CYCLES`` 个周期一次，单单元 2~3 条指令，远低于 500 条/10 秒。
        """
        if self.REASSERT_CYCLES <= 0:
            return []
        done = []
        for b in self._units:
            mode = b.get('mode')
            if mode not in ('strike', 'move'):
                continue
            texts = []
            last = b.get('radar_cycle')
            if last is None or self.cycle - last >= self.REASSERT_CYCLES:
                self._radar(b, texts, mode == 'strike')
                texts = ['%s(雷达自愈)' % t for t in texts]
            if mode == 'move':
                self._ensure_course(b, texts)
            if texts:
                done.append('%s:%s' % (b['name'], '+'.join(texts)))
        if done:
            self._say('info', '周期%d 姿态看护：%s' % (self.cycle, '；'.join(done)))
        return done

    def _ensure_course(self, b, out):
        """前进模式下航路已走完就再规划一段正北航路（保持"持续北进"的语义）。"""
        obj = b['obj']
        try:
            if obj.get_way_points_info():
                return
        except Exception:
            return              # 查不到航路状态就按"还有航路"处理，避免每周期重发
        pt = self._north_point(b)
        if pt is None:
            return
        if self._order(b, out, 'plotted_course', [pt]):
            out.append('续航路(正北%.0fkm)' % self.MOVE_DISTANCE_KM)

    # ==================================================================
    # 五、只读提示：0.6·Dmax 发弹线（不发弹）
    # ==================================================================
    def _fire_note(self, targets, action):
        """打击模式下把"最近的敌方空中目标 vs 0.6·Dmax"写进回执，供事后核对。"""
        if action != 'strike':
            return ''
        parts = []
        for b in targets:
            dmax = b.get('dmax')
            if not dmax:
                parts.append('%s 发弹线未知（Dmax 未反查到）' % b['name'])
                continue
            line = self.FIRE_RATIO * dmax
            dist = self._nearest_air_km(b)
            if dist is None:
                parts.append('发弹线%.0fkm（视野内无空中目标）' % line)
            else:
                parts.append('最近空中目标%.0fkm %s发弹线%.0fkm'
                             % (dist, '≤' if dist <= line else '>', line))
        return '；'.join(parts)

    def _nearest_air_km(self, b):
        """视野内最近的敌方空中目标距离（km）；没有返回 None。"""
        contacts = self._contacts
        if not isinstance(contacts, dict):
            return None
        own = set(_norm(n) for n in self._own_names)
        best = None
        for _cid, c in contacts.items():
            if not isinstance(c, dict):
                continue
            if _to_int(c.get('Type')) != 0:          # 0 = 空中
                continue
            alt = _to_float(c.get('CurrentAltitude'), 0.0) or 0.0
            if alt < self.MIN_AIR_ALT_M:
                continue
            if _norm(c.get('Name')) in own:
                continue
            dist = _km(_to_float(c.get('Lat')), _to_float(c.get('Lon')),
                       b.get('lat'), b.get('lon'))
            if dist is None:
                continue
            if best is None or dist < best:
                best = dist
        return best


def _arg_text(value):
    if isinstance(value, bool):
        return 'True' if value else 'False'
    if isinstance(value, (list, tuple)):
        return '[%d点]' % len(value)
    return str(value)


def _radar_word(state):
    if state is None:
        return '?'
    return '开' if state else '关'


def _fmt(value):
    return '-' if value is None else '%.0f' % value


class Agent(PiButtonListener):
    """客户端「智能体编辑」导入用的入口：类名必须是 ``Agent``。"""

    def __init__(self, side_name="红方", *args, **kwargs):
        super(Agent, self).__init__(side_name)
