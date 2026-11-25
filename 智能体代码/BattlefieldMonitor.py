# -*- coding:utf-8 -*-
r"""
物理作战域三维监控智能体（Battlefield Monitor）
================================================
规则型智能体，**唯一的信息源，也是唯一不直接产生动作的智能体**。
设计依据：设计报告 2.3.1 节。

职责与接口
----------
每步枚举敌方弹药，判断"是否有弹指向本方单位"；命中则向下游返回两个字段：

    弹型（str） + 弹速（km/h）

这两个字段是下游所有距离判据的输入。**刻意不带出弹目距离、不带出完整威胁对象**，
原因见报告：平台没有"我方单位被瞄准"的直接字段，需要按几何关系算；若把完整威胁
对象传给下游，下游就会依赖监控的内部实现，任何改动都会连带影响四条规则。只给两
个标量，下游各自重算、各自检验——这是"互不相交的决策域"成立的前提。

判定几何（报告代码 4）
----------------------
对每个（我方单位, 敌方弹药）对，算最近接近点（CPA）：

    每步调用（逐我方单位）:
      for 弹 in 敌方弹药:
          p = 最近接近点(弹, 本单位)        # 位置 + 速度矢量
          if p.时刻 > 0 and p.距离 < 门限:  # 门限按拦截包线取
              返回(弹.弹型, 弹.弹速)        # 仅两个字段
              break

* ``p.时刻 > 0``：弹正在接近（远离则不算）。
* ``p.距离``：最近接近距离，不是当前距离——所以"现在还在 200 km 外、但必从头顶
  掠过"的弹也会被抓到，这正是三维监控相对于"按当前距离筛"的价值。
* 门限按作用对象类别取：飞机 / 舰船 / 地面单位三路各有拦截包线，见类属性
  ``GATE_*``。

按作用对象归并三路
------------------
报告里监控的输出按作用对象归并为三路（飞机、船、地空导弹营），各路按自己的节奏
调用：

* 飞机一路 → 空战单元自卫（Evade）、空空作战
* 船一路   → 登陆船只集群自卫（Ship）
* 地面一路 → 地空导弹营攻击与自卫（SAM）

本实现不预设下游是谁，只按"目标 guid"回答，谁问就答谁；``route()`` 提供按类别
取目标清单的便捷入口。

坐标与量纲
----------
* 态势里坐标键是 ``lat`` / ``lon``（**不是** latitude/longitude）；
* 情报（THContact）键名首字母大写：``Name`` / ``Type`` / ``Lat`` / ``Lon`` /
  ``CurrentSpeed`` / ``CurrentHeading``；
* ``CurrentSpeed`` 单位是**节**，本模块对外统一换算成 **km/h**（×1.852）——
  报告里 2500 / 1500 km/h 这类阈值都是 km/h。

性能
----
复杂度 O(目标数 × 弹药数)。200 单元、60 枚弹时约 1.2 万次 CPA 计算，纯 Python
实测约 10 ms（含威胁记录的构造，属最坏情形）——相当于 30 秒决策周期的 0.03%，
不会成为瓶颈。速度矢量的三角函数已提到内层循环之外，内侧只剩加减乘。

客户端消息输出
--------------
监控是唯一同时掌握"哪枚弹、指向谁、还有多远、有没有消失"的模块，所以由它向
客户端「智能体消息输出栏」播报（平台只实现了 ``agent_message_text`` 纯文本接口）：

    【袭击】AGM-88E AARGM-ER 攻击 地空导弹连#1（距 83km，1667 km/h）
    【逼近】AGM-88E AARGM-ER 距 地空导弹连#1 仅 7km（1667 km/h）
    【解除】地空导弹连#1 的 AGM-88E AARGM-ER 已不再被探测（可能已耗尽、已命中或失去探测）
    【态势】2 个单元被瞄准：地空导弹连#1←AGM-88E；爱国者地空导弹连#1←Kh-31P

其中【解除】就是"关了雷达之后，那枚弹到底打空了没"的答案：连续
``NOTIFY_CLEAR_CYCLES`` 个周期不再被判为威胁才报，抗住单周期的探测抖动；
措辞里带上"失去探测"，是因为雷达关机时失去接触并不等于弹已耗尽。

每条消息 = 1 条指令，故做了去重（同一 (单元, 弹) 的"袭击"只发一次）、限流
（每周期 ``NOTIFY_MAX_PER_CYCLE`` 条，超出的顺延到下周期，不丢）。
"""

import logging
import math

__all__ = ["BattlefieldMonitor"]

KNOT_TO_KMH = 1.852
EARTH_R_KM = 6371.0


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
    if None in (lat1, lon1, lat2, lon2):
        return None
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2.0) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2)
    a = min(1.0, max(0.0, a))
    return 2.0 * EARTH_R_KM * math.asin(math.sqrt(a))


def closest_approach(lat_m, lon_m, hdg_m, spd_kmh,
                     lat_t, lon_t, hdg_t=None, spd_t_kmh=0.0):
    """
    最近接近点（Closest Point of Approach）。

    在以目标为原点的局部平面里做匀速直线运动求交，误差在本场景（百公里级、
    数十秒~十几分钟）可忽略，但比"直接用当前距离"正确得多：能抓到"现在还很远、
    但注定从头顶掠过"的弹，也能排除"现在很近、其实正在飞离"的弹。

    :param lat_m/lon_m: 弹当前位置
    :param hdg_m: 弹航向（度，正北 0，顺时针）
    :param spd_kmh: 弹速（km/h）
    :param lat_t/lon_t: 目标当前位置
    :param hdg_t: 目标航向（度），可空
    :param spd_t_kmh: 目标速度（km/h）
    :return: (t_cpa, d_cpa, d_now)
             t_cpa = 距离最近时刻（秒）；>0 表示正在接近
             d_cpa = 最近接近距离（km）
             d_now = 当前距离（km）
             参数不全时返回 None
    """
    if None in (lat_m, lon_m, hdg_m, spd_kmh, lat_t, lon_t):
        return None

    # 局部平面：x 东、y 北，单位 km
    kx = 111.32 * math.cos(math.radians(lat_t))
    ky = 110.57
    rx = (lon_m - lon_t) * kx
    ry = (lat_m - lat_t) * ky

    # 速度矢量（km/s）
    vm = spd_kmh / 3600.0
    hr = math.radians(hdg_m)
    vx = vm * math.sin(hr)
    vy = vm * math.cos(hr)

    # 减去目标自身运动（舰船 18~22 节 ≈ 33~41 km/h，对 900 km/h 的弹是次要项，
    # 但算进来更准，且成本极低）
    if hdg_t is not None and spd_t_kmh:
        vt = spd_t_kmh / 3600.0
        ht = math.radians(hdg_t)
        vx -= vt * math.sin(ht)
        vy -= vt * math.cos(ht)

    return cpa_core(rx, ry, vx, vy)


def cpa_core(rx, ry, vx, vy):
    """
    最近接近点的纯算术核（供批量调用时复用预算好的矢量）。

    :param rx/ry: 弹相对目标的局部坐标（km，x 东 y 北）
    :param vx/vy: 弹相对目标的速度（km/s）
    :return: (t_cpa, d_cpa, d_now)
    """
    d_now = math.hypot(rx, ry)
    v2 = vx * vx + vy * vy
    if v2 <= 1e-12:
        # 弹速为 0（悬停/数据缺失）：只按当前位置判断
        return (0.0, d_now, d_now)
    t = -(rx * vx + ry * vy) / v2
    cx, cy = rx + vx * t, ry + vy * t
    return (t, math.hypot(cx, cy), d_now)


# ======================================================================
# 监控智能体
# ======================================================================
class BattlefieldMonitor(object):
    """物理作战域三维监控智能体。"""

    ENABLE = True

    # ------------------------------------------------------------------
    # 门限（km）：按作用对象类别取，"按拦截包线取"
    #   飞机：机载武器交战多在 100 km 内，取 100
    #   舰船：舰空导弹包线最大约 65 km（SA-N-21d），留裕度取 150，
    #         保证下游还有时间做分层补射与规避
    #   地面：地空导弹营自身包线 100~215 km，取 180
    # ------------------------------------------------------------------
    GATE_AIRCRAFT = 100.0
    GATE_SHIP = 150.0
    GATE_FACILITY = 180.0
    GATE_DEFAULT = 120.0

    # 只把"最近接近时刻"在此之前、且距离在门限内的弹算作威胁（秒）
    #   20 分钟足够覆盖 500 km 外、900 km/h 的亚音速反舰弹
    MAX_TIME_TO_CPA = 1200.0

    # 敌方弹药识别：情报 Type == 1（ContactType.Missile）
    MISSILE_TYPES = (1,)
    # 有些版本的平台把在飞弹药记成"空中目标"（Type=0），按名称兜底识别
    FALLBACK_NAME_KEYS = (
        '导弹', 'missile', 'agm-', 'asm-', '雄风', 'lrasm', 'jsow',
        'kh-', 'ss-n', '3m22', '锆石', '战斧', 'tomahawk', '卢卡斯', 'lucas',
    )

    # ------------------------------------------------------------------
    # 消息输出（客户端「智能体消息输出栏」）
    #
    # 平台只实现了 agent_message_text（纯文本），且每条消息 = 1 条指令，
    # 受 agentOrderCountLimit 约束。所以这里做三件事：
    #   ① 只在**状态变化**时发（新来袭 / 逼近 / 解除），不做逐周期播报；
    #   ② 同一 (单元, 弹) 的"袭击"只发一次；
    #   ③ 每周期总量封顶 NOTIFY_MAX_PER_CYCLE，超了不丢、下周期补。
    # ------------------------------------------------------------------
    NOTIFY = True
    NOTIFY_MAX_PER_CYCLE = 6        # 每周期最多发几条消息
    NOTIFY_CLOSE_KM = 10.0          # 弹距小于此值发一条"逼近"告警
    NOTIFY_CLEAR_CYCLES = 2         # 连续 N 周期探测不到才算解除（抗抖）
    NOTIFY_SUMMARY_CYCLES = 20      # 每 N 周期发一条态势摘要（有威胁时才发）
    NOTIFY_HEARTBEAT_CYCLES = 20    # 无威胁时每 N 周期发一条"值班"心跳
    NOTIFY_BOOT_CYCLES = 3          # 开局前 N 个周期补发"在线"，防战前规划丢消息

    # 我方单位类别 → 门限
    ROLE_GATE = {
        'aircraft': GATE_AIRCRAFT,
        'ship': GATE_SHIP,
        'submarine': GATE_SHIP,
        'facility': GATE_FACILITY,
    }

    def __init__(self, agent, log=None):
        self.agent = agent
        self._log_fn = log
        self._cycle = 0
        self._last_sit = None
        self._own = []            # [{'guid','name','cat','lat','lon','spd','hdg'}]
        self._threats = {}        # target_guid -> [{'cid','name','speed','t_cpa','d_cpa','d_now'}]
        self._missiles = []       # 本周期枚举到的敌方弹药
        self._ready = False
        self._stats = {'own': 0, 'missiles': 0, 'pairs': 0, 'hits': 0}

        # 消息状态：{(target_guid, cid): {'stage': 'in'|'close', 'miss': n}}
        self._notified = {}
        self._notify_backlog = []     # 每周期限流后没发完的消息
        self._notify_sent = 0         # 累计已发消息条数

    # ------------------------------------------------------------------
    @property
    def ready(self):
        return self._ready

    def _log(self, level, msg):
        fn = self._log_fn
        if not callable(fn):
            fn = getattr(self.agent, '_log', None)
        text = '[三维监控] %s' % msg
        if callable(fn):
            try:
                fn(level, text)
                return
            except Exception:
                pass
        getattr(logging, level if level in ('info', 'warning', 'error') else 'info',
                logging.info)(text)

    # ==================================================================
    # 生命周期
    # ==================================================================
    def setup(self, situation):
        """
        开局登记本方单位清单（不含武器/弹药），并做一次空扫描。

        :return: dict, 自检摘要
        """
        if not self.ENABLE:
            return {}
        try:
            self._own = self._collect_own(situation)
            self._ready = True
            # 先排一条"就绪"，再扫描：就绪与首批袭击走同一次限流发送，
            # 不会因为"多刷一次"突破每周期上限。（否则整局无威胁时消息栏
            # 一直是空的，无法判断是没事件还是没接上。）
            self._notify_text('【就绪】三维监控已启动：监视本方 %d 个单元，'
                              '发现来袭弹即播报' % len(self._own))
            self.step(situation)
        except Exception as e:
            self._log('error', '初始化异常: %s' % e)
            self._ready = False
            return {}
        rep = {'本方单位': len(self._own),
               '敌方弹药': len(self._missiles),
               '命中威胁': sum(len(v) for v in self._threats.values())}
        self._log('info', '初始化完成：%s' % rep)
        return rep

    def _collect_own(self, situation):
        """从态势收集本方全部单元（飞机/舰船/潜艇/地面），作为"被瞄准"的候选。"""
        units = situation[0] if isinstance(situation, (tuple, list)) and situation else {}
        out = []
        if isinstance(units, dict):
            for guid, u in units.items():
                if not isinstance(u, dict):
                    continue
                cat = str(u.get('category', '') or '').lower()
                if cat and cat not in ('aircraft', 'ship', 'submarine',
                                       'facility', 'satellite'):
                    continue
                lat = _to_float(u.get('lat', u.get('latitude')))
                lon = _to_float(u.get('lon', u.get('longitude')))
                if lat is None or lon is None:
                    continue
                out.append({
                    'guid': u.get('guid') or guid,
                    'name': str(u.get('name', '') or ''),
                    'cat': cat,
                    'lat': lat, 'lon': lon,
                    'spd': _to_float(u.get('speed', u.get('CurrentSpeed')), 0.0),
                    'hdg': _to_float(u.get('heading', u.get('CurrentHeading'))),
                })
        return out

    # ------------------------------------------------------------------
    def ensure(self, situation):
        """
        保证本周期已经算过一次。多个下游共用同一份态势时只算一次。

        :return: bool, 本次是否真的重算
        """
        if not self.ENABLE:
            return False
        if situation is self._last_sit:
            return False
        self.step(situation)
        return True

    def step(self, situation):
        """
        每个决策周期调用一次：枚举敌方弹药 → 逐（目标, 弹）算 CPA → 记录威胁。

        :return: dict, {'own','missiles','pairs','hits'}
        """
        if not self.ENABLE:
            return {}
        self._cycle += 1
        self._last_sit = situation
        try:
            self._own = self._collect_own(situation) or self._own
            self._missiles = self._collect_missiles(situation)
            self._threats = {}
            pairs = 0
            for tgt in self._own:
                gate = self.ROLE_GATE.get(tgt['cat'], self.GATE_DEFAULT)
                kx = 111.32 * math.cos(math.radians(tgt['lat']))
                ky = 110.57
                # 目标自身速度矢量（km/s），每目标只算一次
                tv = (tgt['spd'] or 0.0) * KNOT_TO_KMH / 3600.0
                if tgt['hdg'] is not None and tv:
                    hr = math.radians(tgt['hdg'])
                    tvx, tvy = tv * math.sin(hr), tv * math.cos(hr)
                else:
                    tvx = tvy = 0.0
                rows = []
                for m in self._missiles:
                    pairs += 1
                    r = cpa_core((m['lon'] - tgt['lon']) * kx,
                                 (m['lat'] - tgt['lat']) * ky,
                                 m['vx'] - tvx, m['vy'] - tvy)
                    t_cpa, d_cpa, d_now = r
                    if t_cpa <= 0:
                        continue                    # 正在远离
                    if d_cpa > gate:
                        continue                    # 不会进入拦截包线
                    if t_cpa > self.MAX_TIME_TO_CPA:
                        continue                    # 还太远，先不管
                    rows.append({'cid': m['cid'], 'name': m['name'],
                                 'speed': m['speed_kmh'],
                                 't_cpa': t_cpa, 'd_cpa': d_cpa,
                                 'd_now': d_now})
                if rows:
                    # 按"最先到达最近点"排序，最紧迫的排前面
                    rows.sort(key=lambda x: (x['t_cpa'], x['d_cpa']))
                    self._threats[tgt['guid']] = rows
            self._stats = {'own': len(self._own), 'missiles': len(self._missiles),
                           'pairs': pairs,
                           'hits': sum(len(v) for v in self._threats.values())}
            if self._cycle % 20 == 0 and self._stats['missiles']:
                self._log('info', '周期%d 态势扫描：%s' % (self._cycle, self._stats))
            # 状态变化 → 客户端消息输出栏（来袭 / 逼近 / 解除 / 摘要）
            self._notify_changes()
        except Exception as e:
            self._log('error', '扫描异常: %s' % e)
        return dict(self._stats)

    def _collect_missiles(self, situation):
        """枚举敌方弹药。只认"会飞"的来袭弹，不认飞机与水面目标。"""
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
            is_missile = (ctype in self.MISSILE_TYPES) if ctype is not None else False
            if not is_missile:
                low = name.lower()
                is_missile = any(k in low for k in self.FALLBACK_NAME_KEYS)
            if not is_missile:
                continue
            lat = _to_float(_cget(c, 'Lat', None))
            lon = _to_float(_cget(c, 'Lon', None))
            hdg = _to_float(_cget(c, 'CurrentHeading', None))
            spd = _to_float(_cget(c, 'CurrentSpeed', None))
            if lat is None or lon is None:
                continue
            if spd is None or spd <= 0:
                continue                            # 没有速度就判不了指向
            if hdg is None:
                continue
            speed_kmh = spd * KNOT_TO_KMH
            # 速度矢量预先算好（km/s）：外层每目标只算一次三角，内侧只剩加减乘
            vm = speed_kmh / 3600.0
            hr = math.radians(hdg)
            out.append({
                'cid': _cget(c, 'ID', cid) or cid,
                'name': name,
                'lat': lat, 'lon': lon, 'hdg': hdg,
                'speed_kmh': speed_kmh,
                'vx': vm * math.sin(hr),
                'vy': vm * math.cos(hr),
            })
        return out

    # ==================================================================
    # 客户端消息输出（「智能体消息输出栏」）
    #
    # 为什么由监控来发：报告 2.3.1 里监控是唯一信息源，只有它同时掌握
    # "哪枚弹、指向谁、还有多远、有没有消失"。下游（自卫/防空）只做动作，
    # 不发播报，避免同一件事被四个智能体各说一遍。
    # ==================================================================
    def _own_name(self, guid):
        for t in self._own:
            if t['guid'] == guid:
                return t['name']
        return ''

    @staticmethod
    def _short(name, n=22):
        s = str(name or '')
        return s if len(s) <= n else s[:n - 1] + '…'

    @staticmethod
    def _speed_text(kmh):
        try:
            return '%.0f km/h' % float(kmh)
        except (TypeError, ValueError):
            return '?'

    def _notify_text(self, text):
        """把一条消息压入待发队列（同一周期内重复文本只留一条）。"""
        if not self.NOTIFY or not text:
            return
        if text not in self._notify_backlog:
            self._notify_backlog.append(text)
            # 队列上限：若长期发不出去（例如配额始终被占满），只保留最近 30 条，
            # 避免无限增长；顺序上丢最旧的。
            if len(self._notify_backlog) > 30:
                self._notify_backlog.pop(0)
            # 同时落一条日志：万一客户端面板没显示，也能从日志核对
            self._log('info', '客户端消息：%s' % text)

    def _flush_messages(self):
        """按 NOTIFY_MAX_PER_CYCLE 发送；没发完的留到下个周期，不丢。"""
        if not self.NOTIFY or not self._notify_backlog:
            return 0
        fn = getattr(self.agent, 'agent_message_text', None)
        sent = 0
        while self._notify_backlog and sent < self.NOTIFY_MAX_PER_CYCLE:
            text = self._notify_backlog[0]
            if not callable(fn):
                # 宿主没提供消息接口（例如离线测试桩）：只落日志，不报错
                self._log('info', '（无消息接口）%s' % text)
                self._notify_backlog.pop(0)
                continue
            try:
                fn(text)
            except Exception as e:
                # 常见原因：本周期指令配额用尽。消息留在队列里，下周期再发。
                self._log('warning', '消息发送失败（已顺延）: %s' % e)
                break
            # 发送成功才出队，失败则保留
            self._notify_backlog.pop(0)
            sent += 1
            self._notify_sent += 1
        return sent

    def _notify_changes(self):
        """
        对比上一周期的威胁集合，**按"我方单元"聚合**输出四类消息。

        为什么按单元聚合而不是按"弹×单元"逐条发：一枚弹横向飞过时，会同时
        落进好几个单元的拦截包线，逐条发会在一瞬间刷出十几条"某弹攻击舰船N"，
        消息栏反而看不清重点。所以每个单元每周期最多一条，多枚弹时在末尾带
        "等 N 枚"。

        * 【袭击】某单元开始被瞄准（每个单元只发一次；出现新型号时再发一次）
        * 【逼近】该单元最近的弹进入 NOTIFY_CLOSE_KM
        * 【解除】连续 NOTIFY_CLEAR_CYCLES 周期不再被瞄准
                  —— 这正是"关了雷达之后弹到底打空了没"的答案
        * 【态势】每 NOTIFY_SUMMARY_CYCLES 周期汇总一次（仅在确有威胁时）
        """
        if not self.NOTIFY:
            return

        # 每个单元只保留最紧迫的一枚弹（t_cpa 最小），并统计枚数
        cur = {}
        for guid, rows in self._threats.items():
            if not rows:
                continue
            ordered = sorted(rows, key=lambda r: (r['t_cpa'], r['d_now']))
            cur[guid] = (ordered[0], len(ordered),
                         set(r['cid'] for r in ordered))

        # ① 新袭击 + ② 逼近
        for guid, (r, n_missile, cids) in cur.items():
            who = self._own_name(guid) or '我方单位'
            st = self._notified.get(guid)
            if st is None:
                self._notified[guid] = {'stage': 'in', 'miss': 0,
                                        'name': r['name'], 'cids': set(cids)}
                self._notify_text(
                    '【袭击】%s 攻击 %s（距 %.0fkm，%s%s）'
                    % (self._short(r['name']), who, r['d_now'],
                       self._speed_text(r['speed']),
                       '，另 %d 枚' % (n_missile - 1) if n_missile > 1 else ''))
                continue
            st['miss'] = 0
            st['cids'] = set(cids)
            st['name'] = r['name']
            if st['stage'] == 'in' and r['d_now'] <= self.NOTIFY_CLOSE_KM:
                st['stage'] = 'close'
                self._notify_text(
                    '【逼近】%s 距 %s 仅 %.0fkm（%s）'
                    % (self._short(r['name']), who, r['d_now'],
                       self._speed_text(r['speed'])))

        # ③ 解除 / 失联（按单元）
        for guid in list(self._notified.keys()):
            if guid in cur:
                continue
            st = self._notified[guid]
            st['miss'] = st.get('miss', 0) + 1
            if st['miss'] >= self.NOTIFY_CLEAR_CYCLES:
                self._notify_text(
                    '【解除】%s 的 %s 已不再被探测（可能已耗尽、已命中或失去探测）'
                    % (self._own_name(guid) or '我方单位',
                       self._short(st.get('name'))))
                del self._notified[guid]

        # ④ 态势摘要
        if self._threats and self._cycle % self.NOTIFY_SUMMARY_CYCLES == 0:
            parts = []
            for guid, (r, n_missile, _c) in list(cur.items())[:4]:
                parts.append('%s←%s%s'
                             % (self._short(self._own_name(guid), 14),
                                self._short(r['name'], 14),
                                '×%d' % n_missile if n_missile > 1 else ''))
            self._notify_text('【态势】%d 个单元被瞄准：%s'
                              % (len(cur), '；'.join(parts)))

        # ⑤ 值班心跳：没有威胁时也要周期性发一条，证明链路还活着。
        #    否则整局太平（或威胁一直没变化）时消息栏一直空白，
        #    无法区分"没事件"和"消息发不出去"。
        if not cur:
            if self._cycle <= self.NOTIFY_BOOT_CYCLES or \
                    self._cycle % self.NOTIFY_HEARTBEAT_CYCLES == 0:
                self._notify_text('【值班】暂无来袭弹（本方 %d 个单元在监视）'
                                  % len(self._own))

        self._flush_messages()

    # ==================================================================
    # 对外接口（下游只该用这几个）
    # ==================================================================
    def incoming(self, target_guid):
        """
        **报告规定的严格接口**：该目标是否被弹锁定。

        :param target_guid: str, 我方单位 guid
        :return: tuple 或 None, (弹型, 弹速 km/h)；最紧迫的那一枚
        """
        rows = self._threats.get(target_guid)
        if not rows:
            return None
        r = rows[0]
        return (r['name'], r['speed'])

    def incoming_list(self, target_guid):
        """该目标当前所有指向它的弹：[ (弹型, 弹速), ... ]。"""
        return [(r['name'], r['speed'])
                for r in self._threats.get(target_guid, ())]

    def has_incoming(self, target_guid):
        """该目标是否被任何一枚弹锁定。"""
        return bool(self._threats.get(target_guid))

    def threats_for(self, target_guid):
        """
        供下游**动作**用的最小扩展：在"弹型/弹速"之外，额外给出情报 guid。

        报告要求下游只用弹型与弹速做判据、距离自己重算，所以这里**不给距离**
        （``d_now`` 是给日志/诊断看的，规则里不要用）。下游要发弹，必须拿到
        情报 guid，故这一项不得不带。
        """
        return list(self._threats.get(target_guid, ()))

    def route(self, category):
        """
        按作用对象类别取被瞄准的目标清单（报告里的"一进三出"三路）。

        :param category: 'aircraft' / 'ship' / 'facility'
        :return: list, [(guid, 单元名), ...]，仅含当前确实被瞄准的
        """
        cat = str(category or '').lower()
        out = []
        for t in self._own:
            if t['cat'] != cat:
                continue
            if t['guid'] in self._threats:
                out.append((t['guid'], t['name']))
        return out

    def bare_contacts(self, situation=None):
        """未被任何本方单位"锁定判定"命中的敌方弹药（诊断用，看漏了什么）。"""
        hit = set()
        for rows in self._threats.values():
            for r in rows:
                hit.add(r['cid'])
        return [m for m in self._missiles if m['cid'] not in hit]

    def status(self):
        """返回本周期扫描摘要，供主智能体打日志或赛后核对。"""
        return {
            'cycle': self._cycle,
            'own': len(self._own),
            'missiles': len(self._missiles),
            'threatened': dict((g, len(v)) for g, v in self._threats.items()),
            'stats': dict(self._stats),
            'msgs_sent': self._notify_sent,
            'msg_backlog': len(self._notify_backlog),
        }
