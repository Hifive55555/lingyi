# -*- coding: utf-8 -*-
"""
监控判定 离线自测（不需要灵弈平台、不需要 Windows）

    python selftest_core.py

覆盖：指向判定 / 侧向掠过 / 远离 / 无航向兜底 / 量纲换算 / 分组 / 排序 /
一弹多目标 / 不设门限（朝我就算） / 可选的收紧门限。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lymonitor import core  # noqa: E402

FAIL = []
N = [0]


def ok(cond, msg):
    N[0] += 1
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def unit(uid, name, g, lat, lon, hdg=0.0, spd=0.0, alt=8000.0):
    """spd 单位 km/h。"""
    return {'id': uid, 'n': name, 'g': g, 'pos': (lat, lon),
            'hdg': hdg, 'spd': spd, 'alt': alt, 'dmg': 0.0}


def missile(mid, name, lat, lon, hdg, spd, db=2001, hdg_ok=True):
    """spd 单位 km/h。"""
    return {'id': mid, 'n': name, 'db': db, 'pos': (lat, lon),
            'hdg': hdg, 'hdg_ok': hdg_ok, 'spd': spd, 'alt': 1000.0}


def run(own, msl, prev=None, now=0.0, gate=None, cap=0):
    return core.analyse(own, msl, prev, now, gate, cap)


print("1) 北向 3000km/h 的弹，正南 45km 处有架北向 900km/h 的飞机 -> 朝我来")
u = unit('u1', '苏-35S #1', 'air', 49.0, 0.0, hdg=0.0, spd=900.0)
m = missile('m1', 'AGM-88B', 48.6, 0.0, hdg=0.0, spd=3000.0)
r = run([u], [m])[0]
ok(r['hit'] and r['n_ms'] == 1, "判定被指向")
ok(abs(r['ms'][0]['spd'] - 3000.0) < 1e-6, "弹速原样带出 = 3000 km/h")
ok(abs(r['ms'][0]['cpa']) < 0.5, "CPA ≈ 0（实际 %.2f km）" % r['ms'][0]['cpa'])
ok(60 < r['ms'][0]['tgo'] < 95, "预计命中 %.0f s 落在 60~95 s" % r['ms'][0]['tgo'])

print("2) 弹朝南飞（远离）-> 不算")
m3 = missile('m3', 'AIM-120C', 48.6, 0.0, hdg=180.0, spd=3000.0)
ok(not run([u], [m3])[0]['hit'], "远离目标不算")

print("3) 不设门限：200km 外朝我来也算（对方射程未知，保险起见）")
m4 = missile('m4', 'AGM-88B', 47.2, 0.0, hdg=0.0, spd=3000.0)      # 南约 200km
r = run([u], [m4])[0]
ok(r['hit'], "200 km 外仍然判定（tgo=%.0fs）" % r['ms'][0]['tgo'])

print("4) 已经飞过去的弹（向东飞，且已在目标东侧）-> 不再靠近，不算")
m5 = missile('m5', 'AIM-120C', 48.9, +0.30, hdg=90.0, spd=3000.0)   # 在目标正东 22km，继续向东
r = run([unit('u2', '苏-27 #3', 'air', 48.9, 0.0)], [m5])[0]
ok(not r['hit'], "已掠过并继续远离 -> 不算")

print("4b) 注意：横穿弹在**到达正横点之前**仍算「朝我」——这是不设门限的必然结果")
m5b = missile('m5b', 'AIM-120C', 48.9, -0.30, hdg=90.0, spd=3000.0)  # 在正西 22km，向东飞
r = run([unit('u2', '苏-27 #3', 'air', 48.85, 0.0)], [m5b])[0]        # 弹从北边 5.6km 掠过
ok(r['hit'] and 5 < r['ms'][0]['cpa'] < 6,
   "还算（CPA %.1f km，其实打不中，但规则上确实在靠近）" % r['ms'][0]['cpa'])

print("5) 可选收紧门限：传 gate 后就按门限过滤")
m6 = missile('m6', 'AGM-88B', 48.6, 0.0, hdg=0.0, spd=3000.0)      # 44km 直冲
own = [unit('u1', '苏-35S #1', 'air', 49.0, 0.0, spd=900.0)]
ok(run(own, [m6])[0]['hit'], "不传 gate：算")
ok(run(own, [m6], gate={'cpa_km': 3.0, 'max_km': 90.0})[0]['hit'], "gate 放宽范围：仍算")
ok(not run(own, [m6], gate={'max_km': 30.0})[0]['hit'], "gate max_km=30：被过滤掉")
# 相对门限：CPA 相对当前距离的比值（应对“朝我就算”→全红的问题）
# 一枚从东南方向斜穿、CPA≈44km、距离≈151km 的弹（CPA/距离≈0.29）
m_far = missile('m_far', '防空导弹#29', 47.7, 0.6, hdg=0.0, spd=2735.0)
ok(run(own, [m_far])[0]['hit'], "不设门限：151km 外朝这边飞也算")
ok(not run(own, [m_far], gate={'cpa_ratio': 0.2})[0]['hit'],
   "gate cpa_ratio=0.2：CPA/距离≈0.29 > 0.2，被过滤（它就是“擦边飞过”的那类）")
ok(run(own, [m6], gate={'cpa_ratio': 0.2})[0]['hit'],
   "gate cpa_ratio=0.2：正对头那枚（CPA≈0）仍然算")

print("6) 弹没有航向：靠距离收缩兜底")
u6 = unit('u6', '雷鸣号 #1', 'sea', 49.0, 0.0)
m7 = missile('m7', 'SS-N-33', 49.3, 0.0, hdg=0.0, spd=900.0, hdg_ok=False)
ok(run([u6], [m7], prev={('u6', 'm7'): (40.0, 0.0)}, now=5.0)[0]['hit'],
   "无航向 + 距离在收缩 -> 兜底判定")
m8 = missile('m8', 'SS-N-33', 49.0, 0.3, hdg=0.0, spd=900.0, hdg_ok=False)
ok(not run([u6], [m8], prev={('u6', 'm8'): (10.0, 0.0)}, now=5.0)[0]['hit'],
   "无航向 + 距离在拉开 -> 不算")
ok(not run([u6], [m7])[0]['hit'], "无航向 + 第一次见到 -> 本周期不算（下周期再判）")

print("7) 量纲：CurrentSpeed 是节，use_speed_kmh 换算成 km/h")
ok(abs(core.use_speed_kmh(1000) - 1852.0) < 1e-6, "1000 节 = 1852 km/h")
ok(abs(core.KNOT_TO_KMH - 1.852) < 1e-9, "KNOT_TO_KMH = 1.852")

print("8) 弹药识别：Type==1，或名字像弹")
ok(core.is_missile({'Type': 1, 'Name': 'X'}), "Type=1 -> 是弹")
ok(not core.is_missile({'Type': 0, 'Name': 'F-35A #1'}), "Type=0 的飞机 -> 不是弹")
ok(core.is_missile({'Type': 0, 'Name': 'AGM-88E AARGM-ER'}),
   "Type=0 但名字是导弹 -> 兜底认出来")
ok(not core.is_missile({'Type': 0, 'Name': 'DDG 113“约翰.芬”阿利伯克级 Flight IIA导弹驱逐舰'}),
   "★ 实测踩过：'导弹驱逐舰' 不能被当成来袭弹（名字里有平台词）")
ok(not core.is_missile({'Type': 0, 'Name': '苏-35S #1'}), "战斗机不算弹")

print("9) 海陆空分组（含：不设门限时，一枚穿场弹会把航路上所有单元都标成「朝我」）")
own = [unit('a1', '苏-35S #1', 'air', 49.0, 0.0), unit('a2', '苏-27 #5', 'air', 49.2, 0.0),
       unit('s1', '雷鸣号 #1', 'sea', 49.0, 0.5), unit('s2', '基洛级 #1', 'sea', 49.0, 0.6, alt=-100),
       unit('l1', '鸡窝雷达', 'land', 49.0, 0.9, alt=160)]
one = missile('mm', 'AGM-88B', 49.05, 0.02, hdg=180.0, spd=3000.0)
rows = run(own, [one])
s = core.summarise(rows)
g = [r['g'] for r in rows]
ok(g.count('air') == 2 and g.count('sea') == 2 and g.count('land') == 1,
   "三组数量 2/2/1，组按 空→海→陆 顺序：%s" % g)
ok(s['all'][1] == 5 and s['all'][0] == s['air'][0] + s['sea'][0] + s['land'][0],
   "summarise 总计对得上：%s" % (s,))
ok(s['all'][0] >= 1, "至少 a1 被标记（实际 %d / 5 个单元）" % s['all'][0])
ok(all(rows[i]['hit'] >= rows[i + 1]['hit'] for i in range(len(rows) - 1)
       if rows[i]['g'] == rows[i + 1]['g']), "组内被攻击的排在前面")

print("10) 一个单元被 3 枚弹指着 -> 按 tgo 升序，可截断")
u10 = unit('u10', '苏-35S #2', 'air', 49.0, 0.0, spd=900.0)
ms = [missile('n1', '近弹', 48.95, 0.0, hdg=0.0, spd=3000.0),
      missile('n2', '远弹', 48.4, 0.0, hdg=0.0, spd=3000.0),
      missile('n3', '中弹', 48.7, 0.0, hdg=0.0, spd=3000.0)]
rows = run([u10], ms)
tg = [round(h['tgo']) for h in rows[0]['ms']]
ok(rows[0]['n_ms'] == 3 and tg == sorted(tg), "3 枚弹按 tgo 升序：%s" % tg)
ok(len(run([u10], ms, cap=2)[0]['ms']) == 2, "max_per_unit=2 截断生效")

print("11) 一枚弹同时指着两个单元 -> 两边都记到")
own11 = [unit('p', '苏-35S #1', 'air', 48.955, 0.0), unit('q', '苏-35S #2', 'air', 48.995, 0.0)]
m11 = missile('x', 'R-77', 48.975, -0.30, hdg=90.0, spd=3000.0)
ok(sum(1 for r in run(own11, [m11]) if r['hit']) == 2, "横穿弹同时威胁两架")

print("\n%d 项断言，%d 项失败" % (N[0], len(FAIL)))
for f in FAIL:
    print("  ! " + f)
sys.exit(1 if FAIL else 0)
