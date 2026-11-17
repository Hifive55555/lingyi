# -*- coding: utf-8 -*-
"""
监控智能体 —— 核心判定（纯函数，不 import 任何平台库，可在 Linux 上离线自测）

职责只有一件事：**给我方每个单元，判断当前有没有敌方弹药正朝它飞，并报出这枚弹的
型号与当前弹速。**

平台没有“我方单位被瞄准”这个字段，只能用几何算：
    1. 敌方弹药 = 情报里 Type == 1（ContactType.Missile）的条目；
    2. 弹与我方单元都化成同一水平面上的点 + 速度矢量；
    3. 求相对运动下的最近接近点 CPA：只要“还在靠近”（t* > 0）就算朝我来。

**本实现不设距离 / 时间 / CPA 门限**：对方弹的射程未知，保险起见“朝我就算”。
需要收紧时，把 ``gate`` 传进来即可（下游自己决定，监控不预设）。

量纲（踩过的坑，务必注意）：
    平台 ``CurrentSpeed`` 的单位是**节（海里/小时）**，不是 km/h。
    本模块入口统一用 km/h，转换在 :func:`use_speed_kmh` 里做；
    对外输出的 ``spd`` 一律是 **km/h**，与报告里 2500 / 1500 km/h 这类阈值同一口径。
"""

import math

KNOT_TO_KMH = 1.852             # 1 节 = 1.852 km/h
NM = 1.852                      # 1 海里 = 1.852 km
MISSILE_TYPE = 1                # ContactType.Missile.value

GROUP_CN = {'air': '空', 'sea': '海', 'land': '陆'}
GROUP_ORDER = ('air', 'sea', 'land')

# 有些版本的平台把在飞弹药记成“空中目标”（Type=0），按名称兜底认一下。
# ⚠ 不能只写 '导弹'：情报里“XX级导弹驱逐舰 / 导弹护卫舰”会把军舰一起匹配进来
#   （实测 2026-11-17：DDG 113 阿利伯克级 Flight IIA 导弹驱逐舰 被判成来袭弹）。
#   所以先按平台名排除，再要求命中具体弹型关键字。
MISSILE_NAME_KEYS = ('missile', 'agm-', 'asm-', 'kh-', 'ss-n', 'aim-', 'r-77',
                     'r-73', 'r-37', 'pl-15', 'pl-21', '雄风', 'lrasm', 'jsow',
                     '锆石', '战斧', 'tomahawk', '风暴阴影', 'scalp', '鱼叉',
                     'harpoon', '标准-', 'sm-6', 'aster', '流星')
# 名字里出现这些，一定不是“在飞的弹”（是平台/舰船/飞机/设施）
PLATFORM_NAME_KEYS = ('舰', '船', '艇', '机', '基地', '机场', '雷达', '营', '连',
                      '站', '旅', '团', '师', 'carrier', 'destroyer', 'frigate')


# ----------------------------------------------------------------- 取值小工具
def num(x, default=0.0):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v


def get(o, key, default=None):
    """从 dict 或对象上取字段（大小写都不敏感）——平台两种给法都有。"""
    if o is None:
        return default
    if isinstance(o, dict):
        for k in (key, key.capitalize(), key.lower(), key.upper()):
            if k in o:
                return o[k]
        return default
    return getattr(o, key, default)


def pos(o):
    """(纬度, 经度)；取不到或为 (0,0) 返回 None。"""
    lat, lon = get(o, 'Lat', get(o, 'lat')), get(o, 'Lon', get(o, 'lon'))
    if lat is None or lon is None:
        return None
    lat, lon = num(lat, None), num(lon, None)
    if lat is None or lon is None:
        return None
    if abs(lat) < 1e-9 and abs(lon) < 1e-9:
        return None
    return (lat, lon)


def km(a, b):
    """两点水平距离（km），小范围等距近似。"""
    dn = (a[0] - b[0]) * 111.32
    de = (a[1] - b[1]) * 111.32 * math.cos(math.radians((a[0] + b[0]) / 2.0))
    return math.hypot(dn, de)


def use_speed_kmh(raw):
    """把平台给的 ``CurrentSpeed``（节）换成 km/h。"""
    return num(raw) * KNOT_TO_KMH


def is_missile(contact):
    """这条情报是不是在飞的弹。先认 Type==1，再按名字兜底。"""
    try:
        if int(get(contact, 'Type', -1)) == MISSILE_TYPE:
            return True
    except (TypeError, ValueError):
        pass
    name = str(get(contact, 'Name', '') or '').lower()
    if not name:
        return False
    if any(k in name for k in PLATFORM_NAME_KEYS):
        return False
    return any(k in name for k in MISSILE_NAME_KEYS)


# ----------------------------------------------------------------- 判定核心
def cpa(me_pos, me_hdg, me_spd, tgt_pos, tgt_hdg, tgt_spd):
    """
    最近接近点。

    :return: (cpa_km, tgo_s, closing)
             cpa_km : 未来最近距离（km）
             tgo_s  : 从现在到最近接近点的时间（s）
             closing: 是否还在靠近（相对距离仍在缩小）
    """
    lat = math.radians(me_pos[0])
    rx = (tgt_pos[1] - me_pos[1]) * 111.32 * math.cos(lat)      # 东
    ry = (tgt_pos[0] - me_pos[0]) * 111.32                      # 北
    tvx = tgt_spd * math.sin(math.radians(tgt_hdg))
    tvy = tgt_spd * math.cos(math.radians(tgt_hdg))
    mvx = me_spd * math.sin(math.radians(me_hdg))
    mvy = me_spd * math.cos(math.radians(me_hdg))
    vx, vy = tvx - mvx, tvy - mvy
    vv = vx * vx + vy * vy
    if vv < 1e-9:
        return math.hypot(rx, ry), 0.0, False
    t = -(rx * vx + ry * vy) / vv                               # 小时
    closing = t > 0
    if t < 0:
        t = 0.0
    cx, cy = rx + vx * t, ry + vy * t
    return math.hypot(cx, cy), t * 3600.0, closing


def analyse(own, missiles, prev=None, now=0.0, gate=None, max_per_unit=0):
    """
    逐我方单元判定“是否被弹朝我飞”，返回可直接喂给小窗 / 下游的行。

    :param own     : [{'id','n','g','pos','hdg','spd','alt','dmg'}, ...]
                     g 取 'air' / 'sea' / 'land'；spd 单位 km/h
    :param missiles: [{'id','n','db','pos','hdg','hdg_ok','spd','alt'}, ...]
                     敌方弹药情报，spd 单位 km/h
    :param prev    : {(unit_id, missile_id): (距离km, 时间s)}，上一周期留下的；
                     仅在“弹没有航向”时用于兜底（用距离是否收缩代替航向）。
    :param now     : 当前推演时间（s），与 prev 里的时间同一坐标系。
    :param gate    : None = 不设门限（默认，“朝我就算”）；
                     也可自行收紧任意一项：
                       {'cpa_km':3, 'max_km':90, 'tgo_s':900}   绝对门限
                       {'cpa_ratio':0.2}  相对门限：CPA ≤ 当前距离 × 0.2
                     （实测 138 个单元的大想定里，不设门限会让 91/91 架飞机全被标红，
                      所以要“看谁真被瞄”时建议加 cpa_ratio 或 cpa_km）
    :param max_per_unit: >0 时每单元最多保留几枚（只影响展示，按 tgo 升序截断）。
    :return        : [{'id','n','g','lat','lon','alt','spd','dmg','hit','n_ms','ms':[...]}]
                     ms 每项 {'id','n','db','spd','d','cpa','tgo'}，按紧急程度排序
    """
    gate = gate or {}
    g_cpa = num(gate.get('cpa_km'), 0.0)
    g_max = num(gate.get('max_km'), 0.0)
    g_tgo = num(gate.get('tgo_s'), 0.0)
    g_ratio = num(gate.get('cpa_ratio'), 0.0)
    prev = prev or {}
    out = []
    for u in own:
        u_pos = u.get('pos')
        if u_pos is None:
            continue
        u_hdg = num(u.get('hdg'))
        u_spd = num(u.get('spd'))
        hits = []
        for m in missiles:
            m_pos = m.get('pos')
            if m_pos is None:
                continue
            d = km(u_pos, m_pos)
            if g_max > 0 and d > g_max:
                continue
            m_hdg = num(m.get('hdg'))
            m_spd = num(m.get('spd'))
            cp, tgo, closing = cpa(u_pos, u_hdg, u_spd, m_pos, m_hdg, m_spd)
            if not m.get('hdg_ok', True):
                # 情报里没有 CurrentHeading：算不出 CPA，改用“距离是否在收缩”
                p = prev.get((u['id'], m['id']))
                if p is None:
                    continue                     # 第一次见到这枚弹，下一周期再判
                pd, pt = p
                dt = now - pt
                if dt <= 0:
                    # 同一个推演时刻被算了两次（或时间回退）：无速度可言，
                    # 沿用上一周期的“在靠近”判断，但**不给 tgo**，避免算出垃圾值
                    closing = d < pd - 1e-6
                    cp, tgo = (0.0 if closing else d), None
                else:
                    closing = d < pd - 1e-6
                    cp = 0.0 if closing else d
                    rate = (pd - d) / dt
                    tgo = (d / rate) if rate > 1e-6 else None
                if not closing:
                    continue
            if not closing:
                continue
            if g_cpa > 0 and cp > g_cpa:
                continue
            if g_ratio > 0 and cp > d * g_ratio:
                continue
            if g_tgo > 0 and tgo is not None and tgo > g_tgo:
                continue
            hits.append({'id': m['id'],
                         'n': m.get('n') or '',
                         'db': m.get('db'),
                         'spd': round(m_spd, 1),
                         'd': round(d, 2),
                         'cpa': round(cp, 2),
                         'tgo': None if tgo is None else round(tgo, 1)})
        # 越“快命中”越靠前；算不出时间的排最后
        hits.sort(key=lambda h: (h['tgo'] is None, h['tgo'] or 0.0, h['d']))
        if max_per_unit > 0:
            hits = hits[:max_per_unit]
        out.append({'id': u['id'], 'n': u.get('n') or u['id'], 'g': u.get('g', 'air'),
                    'lat': round(u_pos[0], 4), 'lon': round(u_pos[1], 4),
                    'alt': round(num(u.get('alt')), 0), 'spd': round(u_spd, 0),
                    'dmg': round(num(u.get('dmg')), 0),
                    'hit': bool(hits), 'n_ms': len(hits), 'ms': hits})
    # 组内：被攻击的在前，越紧急越靠前
    out.sort(key=lambda r: (GROUP_ORDER.index(r['g']) if r['g'] in GROUP_ORDER else 9,
                            not r['hit'],
                            (r['ms'][0]['tgo'] if r['ms'] and r['ms'][0]['tgo'] is not None else 1e9)))
    return out


def summarise(rows):
    """给标题栏用的小计：{'air': (被攻击数, 总数), ..., 'all': (x, y)}。"""
    s = {}
    for g in GROUP_ORDER:
        rs = [r for r in rows if r['g'] == g]
        s[g] = (sum(1 for r in rs if r['hit']), len(rs))
    s['all'] = (sum(1 for r in rows if r['hit']), len(rows))
    return s


def prev_of(own, missiles, now):
    """生成下一周期用的 prev：{(unit_id, missile_id): (距离, now)}。"""
    out = {}
    for u in own:
        if u.get('pos') is None:
            continue
        for m in missiles:
            if m.get('pos') is None:
                continue
            out[(u['id'], m['id'])] = (km(u['pos'], m['pos']), now)
    return out
