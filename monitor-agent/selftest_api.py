# -*- coding: utf-8 -*-
"""
监控组件 API 契约自测（不需要灵弈平台、不需要 Windows）

    python selftest_api.py

这个文件是**给验收看的**：它假装自己是“下游智能体”（地空导弹营 / 空战单元自卫），
只用 ``lymonitor.monitor.Monitor`` 的公开接口做决策，逐条验证 ``API.md`` 里的行为。

⚠ 场景设计说明：因为判定规则是「**弹在朝我飞就算**」（不设距离/时间/CPA 门限），
一枚沿子午线向北飞的反辐射弹会同时“朝”这条线上它前方的所有单元。为了让每条断言
指向明确，这里把每个场景布置成**径向散开**：弹从中心朝自己的目标飞，对其他方位的
单元就是“正在远离”，不会被误标。这个取舍的后果写在 API.md §5。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lymonitor.monitor import Monitor  # noqa: E402

FAIL = []
N = [0]


def ok(cond, msg):
    N[0] += 1
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


# ------------------------------------------------------------------ 假平台对象
class U(object):
    """假的 Player 单元对象。CurrentSpeed 单位是**节**（和平台一致）。"""

    def __init__(self, name, lat, lon, hdg=0.0, knots=0.0, alt=8000.0, dmg=0.0):
        self.Name = name
        self.Lat = lat
        self.Lon = lon
        self.CurrentHeading = hdg
        self.CurrentSpeed = knots
        self.CurrentAltitude = alt
        self.DamagePercent = dmg


class FakeAgent(object):
    """假的“主智能体”：只有 Player 那几个容器 + Contacts。"""

    def __init__(self):
        self.Name = '红方'
        self.aircrafts = {}
        self.ships = {}
        self.submarines = {}
        self.facilitys = {}
        self.Contacts = {}
        self.messages = []

    def agent_message_text(self, text):
        self.messages.append(text)


def contact(cid, name, lat, lon, hdg, knots, ctype=1, db=2056):
    return {'ID': cid, 'Name': name, 'Type': ctype, 'DBID': db,
            'Lat': lat, 'Lon': lon, 'CurrentHeading': hdg,
            'CurrentSpeed': knots, 'CurrentAltitude': 1000.0}


def sit(cts):
    return ({}, cts)


# ==================================================================
# 场景 A：一架飞机，两枚弹（一近一远）都朝它飞
# ==================================================================
print("─" * 62)
print("场景 A：incoming / incoming_list / threats_for / ensure / status")
print("─" * 62)
a = FakeAgent()
a.aircrafts['air1'] = U('苏-35S #1', 45.00, 1.00, hdg=0.0, knots=486)   # 486 节 ≈ 900 km/h
cts_a = {'c_near': contact('c_near', 'AGM-88E AARGM-ER', 45.00, 0.90, hdg=90.0, knots=1600),
         'c_far': contact('c_far', 'Kh-31P', 45.00, 0.30, hdg=90.0, knots=900),
         'c_plane': contact('c_plane', 'F-35A #1', 45.10, 0.20, hdg=90.0, knots=480,
                            ctype=0, db=1001)}
sit_a = sit(cts_a)

print("1) setup / ready")
m = Monitor(a)
rep = m.setup(sit_a)
ok(m.ready is True, "setup 之后 ready=True")
ok(rep.get('本方单位') == 1, "本方单位 1 个：%s" % (rep,))
ok(rep.get('敌方弹药') == 2, "敌方弹药 2 枚（Type=0 的飞机被排除）：%s" % (rep,))

print("2) has_incoming / incoming")
ok(m.has_incoming('air1') is True, "air1 被指着")
name, spd = m.incoming('air1')
ok(name == 'AGM-88E AARGM-ER', "最紧迫的一枚 = 近的那枚：%s" % name)
ok(abs(spd - 1600 * 1.852) < 1.0,
   "弹速已换算成 km/h：%.0f km/h（情报里写的是 1600 节）" % spd)
ok(m.incoming('nobody') is None, "没被指着时 incoming 返回 None")
ok(m.has_incoming('nobody') is False, "没被指着时 has_incoming 返回 False")

print("3) incoming_list")
lst = m.incoming_list('air1')
ok(len(lst) == 2, "air1 有 2 枚弹朝它飞：%s" % ([n for n, _ in lst],))
ok(lst[0][0] == 'AGM-88E AARGM-ER', "按紧急度排序，近的在前")
ok(lst[0][1] > lst[1][1], "近的那枚弹速也更大（1600 节 > 900 节）")

print("4) threats_for（给要动作的下游）")
rows = m.threats_for('air1')
ok(rows and rows[0]['id'] == 'c_near',
   "第一条带的 id 就是情报 guid（可直接当 attack_* 的 target）：%s"
   % (rows[0]['id'] if rows else None))
for k in ('id', 'n', 'db', 'spd', 'd', 'cpa', 'tgo'):
    ok(k in rows[0], "字段 %s 存在" % k)
ok(rows[0]['cpa'] < 5.0,
   "CPA = %.2f km（基本对头；不是 0 是因为本机也在以 900km/h 北飞）" % rows[0]['cpa'])
ok(abs(rows[0]['spd'] - 2963.2) < 1.0, "当前弹速 %.0f km/h" % rows[0]['spd'])

print("5) 用 threats_for 的 id 反查情报，算规避方位")
cid = rows[0]['id']
c = cts_a[cid]
bearing = (math.degrees(math.atan2((c['Lon'] - a.aircrafts['air1'].Lon) * math.cos(math.radians(45)),
                                   c['Lat'] - a.aircrafts['air1'].Lat)) + 360) % 360
ok(cid == 'c_near' and c is cts_a['c_near'],
   "反查拿到的就是同一份情报对象；来袭方位 %.0f°（正西=270°）" % bearing)

print("6) ensure：同一份态势只算一次")
before = m.status()['cycle']
ok(m.ensure(sit_a) is False, "同一个 situation 对象 -> 不重算")
ok(m.status()['cycle'] == before, "周期数没变：%s" % before)
ok(m.ensure(sit_a, time_elapse=130) is True, "给了新时间 -> 重算")
ok(m.status()['cycle'] == before + 1, "周期数 +1")

print("7) status / missiles / bare_contacts")
st = m.status()
ok(st['own'] == 1 and st['missiles'] == 2, "status: %s" % (st['stats'],))
ok(st['gate'] == 'none', "gate = none（不设门限）")
ok(len(m.missiles()) == 2, "missiles() 返回 2 枚")

# ==================================================================
# 场景 B：空 / 海 / 陆 / 潜各一个，各被一枚弹径向逼近 -> route()
# ==================================================================
print("─" * 62)
print("场景 B：route() 按作用对象分类（报告的一进三出）")
print("─" * 62)
b = FakeAgent()
b.aircrafts['air1'] = U('苏-35S #1', 45.00, 1.00)                    # 中心正东 1°
b.ships['ship1'] = U('雷鸣号 #1', 45.00, -1.00)                      # 正西 1°
b.facilitys['sam1'] = U('地空导弹连#1', 46.00, 0.00, alt=60)          # 正北 1°
b.submarines['sub1'] = U('基洛级 #1', 44.00, 0.00, alt=-100)          # 正南 1°
cts_b = {'c_air': contact('c_air', 'AGM-88E', 45.00, 0.50, hdg=90.0, knots=1600),
         'c_sea': contact('c_sea', 'SS-N-33', 45.00, -0.50, hdg=270.0, knots=490),
         'c_land': contact('c_land', 'AGM-88G', 45.50, 0.00, hdg=0.0, knots=1200),
         'c_sub': contact('c_sub', '鱼叉', 44.50, 0.00, hdg=180.0, knots=460)}
m_b = Monitor(b)
m_b.setup(sit(cts_b))
air = m_b.route('air')
sea = m_b.route('sea')
land = m_b.route('land')
ok(air == [('air1', '苏-35S #1')], "空：%s" % (air,))
ok(sea == [('ship1', '雷鸣号 #1'), ('sub1', '基洛级 #1')], "海（舰+潜）：%s" % (sea,))
ok(land == [('sam1', '地空导弹连#1')], "陆：%s" % (land,))
ok(m_b.route('aircraft') == air and m_b.route('ship') == sea and m_b.route('facility') == land,
   "别名 'aircraft'/'ship'/'facility' 也认")
ok(m_b.route('satellite') == [], "未知类别返回空列表")
ok(len(m_b.rows()) == 4 and all(r['hit'] for r in m_b.rows()),
   "4 个单元全部被各自那枚弹标记，且没有交叉误标")

# ==================================================================
# 场景 C：弹已经飞过去 -> 不算
# ==================================================================
print("─" * 62)
print("场景 C：弹已掠过并继续远离 -> 不判定")
print("─" * 62)
c2 = FakeAgent()
c2.aircrafts['air1'] = U('苏-35S #1', 45.00, 1.00)
m_c = Monitor(c2)
m_c.setup(sit({'c_past': contact('c_past', 'AIM-120C', 45.00, 1.30, hdg=90.0, knots=1600)}))
ok(m_c.has_incoming('air1') is False, "弹在正东并继续向东 -> 不算")
ok([x['n'] for x in m_c.bare_contacts()] == ['AIM-120C'],
   "它出现在 bare_contacts 里（诊断接口能看出“看见了但没朝我飞”）")

# ==================================================================
# 场景 D：下游智能体按监控结论做分支（模仿 SamBattalionDefense）
# ==================================================================
print("─" * 62)
print("场景 D：把监控嵌进主智能体，按结论做分支")
print("─" * 62)
d = FakeAgent()
d.facilitys['sam1'] = U('地空导弹连#1', 45.00, 1.00, alt=60)
d.facilitys['sam2'] = U('地空导弹连#2', 45.00, -1.00, alt=60)
sit_d = sit({'c1': contact('c1', 'AGM-88G', 45.00, 0.50, hdg=90.0, knots=1200)})
m_d = Monitor(d)
m_d.setup(sit_d)


def sam_step(situation, time_elapse):
    """有监控就以监控为唯一判据（不叠加自己的几何兜底）。"""
    m_d.ensure(situation, time_elapse)
    acts = []
    for guid, u in d.facilitys.items():
        if m_d.has_incoming(guid):
            n, s = m_d.incoming(guid)
            acts.append('%s 被 %s(%d km/h) 瞄准 -> 关雷达+脱离' % (u.Name, n, round(s)))
        else:
            acts.append('%s 正常值班' % u.Name)
    return acts


ok(sam_step(sit_d, 200) == ['地空导弹连#1 被 AGM-88G(2222 km/h) 瞄准 -> 关雷达+脱离',
                            '地空导弹连#2 正常值班'],
   "下游分支正确（被瞄准的脱离，没被瞄准的值班）")

# ==================================================================
# 场景 E：需要收紧时传 gate
# ==================================================================
print("─" * 62)
print("场景 E：门限可选（默认不放门限，需要时传 gate）")
print("─" * 62)
m_e = Monitor(a, gate={'max_km': 10.0})
m_e.setup(sit_a)
ok(m_e.has_incoming('air1') is True and len(m_e.incoming_list('air1')) == 1,
   "gate max_km=10：只剩 7.9 km 那枚，55 km 外的被过滤")
m_e2 = Monitor(a, gate={'cpa_km': 1.0})
m_e2.setup(sit_a)
ok(m_e2.has_incoming('air1') is False,
   "gate cpa_km=1：本机在动，CPA=2.3 km > 1，被过滤（说明 CPA 是弹道最近距离，不是当前距离）")
m_e3 = Monitor(a, gate={'cpa_km': 5.0, 'max_km': 90.0, 'tgo_s': 900.0})
m_e3.setup(sit_a)
ok(m_e3.has_incoming('air1') is True, "三项门限一起给也正常（沿用旧实现的口径）")

print("─" * 62)
print("场景 F：IGNORE_NAME_KEYS 可以按名字剔掉平台里的“告警”类情报")
print("─" * 62)
f = FakeAgent()
f.aircrafts['air1'] = U('苏-35S #1', 45.00, 1.00)
sit_f = sit({'c_real': contact('c_real', '防空导弹#40', 45.00, 0.90, hdg=90.0, knots=1600),
             'c_warn': contact('c_warn', '警告来袭#70', 45.00, 0.85, hdg=90.0, knots=1600)})
m_f = Monitor(f)
m_f.setup(sit_f)
ok(len(m_f.missiles()) == 2, "默认两条都算（2 枚）")
m_f2 = Monitor(f)
m_f2.IGNORE_NAME_KEYS = ('警告来袭',)
m_f2.setup(sit_f)
ok(len(m_f2.missiles()) == 1, "设了 IGNORE_NAME_KEYS 后只剩真弹（1 枚）：%s"
   % ([x['n'] for x in m_f2.missiles()],))

print("\n%d 项断言，%d 项失败" % (N[0], len(FAIL)))
for f in FAIL:
    print("  ! " + f)
sys.exit(1 if FAIL else 0)
