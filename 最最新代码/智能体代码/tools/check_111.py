# -*- coding: utf-8 -*-
"""
校验：111.txt 里的坐标是否都被代码原样收录（BOL 目标/航迹点、登陆点）。

比赛过程中按用户要求做过的变更也在这里体现：
  · 沙赫德无人机发射车的 BOL **已取消**（该弹不支持纯方位发射）
    → 它的 6 个航迹点 + 目标点不再使用，属正常；
  · 新增的 SS-26 第二目标点 (43.657711,-0.215324) 来自后续需求，
    不在 111.txt 里，属正常。
"""
import os
import re
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

agent_base = types.ModuleType('entitys.agent_base')
agent_base.RuleAgentBase = type('RuleAgentBase', (object,), {
    '__init__': lambda self, side_name: setattr(self, 'Name', side_name)})
sys.modules['entitys.agent_base'] = agent_base
player_mod = types.ModuleType('entitys.player')
player_mod.Player = object
sys.modules['entitys.player'] = player_mod
import entitys  # noqa: E402
entitys.agent_base = agent_base
entitys.player = player_mod

import Mission_all_red as R  # noqa: E402

# 已按要求取消的沙赫德 BOL 航路（6 个航迹点 + 目标点）
CANCELLED = {
    (50.911593, 2.081675), (51.102344, 2.854912), (50.758936, 2.212539),
    (51.046481, 3.210333), (50.730516, 2.510804), (50.858603, 3.101413),
    (51.224247, 2.971228),
    # 原“18 节直航”的 5 个登陆点：其中 4 个已取消（改由支援任务 A~E 接管）
    (49.175220, -2.486464), (49.627703, -0.990658),
    (50.163598, 0.901632), (51.291194, 2.005753),
    # 23900 原来的单点直航目标，已改为三点航线（见 ADDED_LATER）
    (49.588100, -0.185594),
    # 「中间保船」原来的巡逻区四点（已按要求换成新四点）
    (49.620200, -0.298774), (49.523700, -0.014330),
    (49.620200, -0.014330),
}
# 后续需求新增、111.txt 里没有的坐标
ADDED_LATER = {
    (43.657711, -0.215324),
    # 23900 型船坞登陆舰#1 的三点航线
    (50.084713, -0.857245), (49.678446, -1.022172), (49.638315, -0.997032),
}

# 111.txt 里滚进来的**蓝方**坐标（战斧 BOL 目标/航迹点），红方代码当然用不到
NOT_RED = {
    (49.717689, -2.193483), (49.779592, -2.529662), (49.936685, -0.209524),
    (49.637561, -0.354083), (50.053257, -0.382165),
    (49.755181, -2.546504), (49.856532, -1.058552), (49.566030, -1.099090),
    (49.997354, -1.207326),
}

TXT = None
for _name in ('红方人人总任务.txt', '111.txt'):
    _p = os.path.join(ROOT, _name)
    if os.path.exists(_p):
        TXT = _p
        break
if TXT is None:
    raise SystemExit('找不到红方总任务 txt（红方人人总任务.txt / 111.txt）')
txt = open(TXT, encoding='utf-8').read()
want = set((round(float(a), 6), round(float(b), 6))
           for a, b in re.findall(r'（\s*(-?\d+\.\d+)\s*[，,]\s*(-?\d+\.\d+)\s*）', txt))

# ① 111.txt 里“必须原样落到代码”的坐标：BOL 目标/航迹 + 登陆点
strict = []
for i, b in enumerate(R.Agent.BOL_STRIKES):
    strict.append(('BOL%d-目标' % i, tuple(round(x, 6) for x in b['target'])))
    for j, p in enumerate(b.get('course') or []):
        strict.append(('BOL%d-航迹%d' % (i, j + 1),
                       (round(p[0], 6), round(p[1], 6))))
for i, (specs, points, knots) in enumerate(R.Agent.SHIP_MOVES):
    for j, p in enumerate(points):
        strict.append(('航线%d-第%d点' % (i + 1, j + 1),
                       (round(p[0], 6), round(p[1], 6))))

# ② 代码里用到的全部坐标（任务表另有 check_table 校验，这里只用于“111 有没有漏用”）
used = set(p for _t, p in strict)
for name, p1, p2, units, formation in R.Agent.SUPPORT_TASKS:
    used.add((round(p1[0], 6), round(p1[1], 6)))
    used.add((round(p2[0], 6), round(p2[1], 6)))
for name, mtype, area, units, doctrine, note in R.Agent.PATROL_TASKS:
    for p in area:
        used.add((round(p[0], 6), round(p[1], 6)))
# 战前移动目标点也算“代码用到了”
for specs, dest in getattr(R.Agent, 'PREWAR_MOVES', ()):
    used.add((round(dest[0], 6), round(dest[1], 6)))

missing = [(tag, p) for tag, p in strict
           if p not in want and p not in ADDED_LATER]
unused = (want - used) - CANCELLED - NOT_RED

print('111.txt 中的坐标点:', len(want))
print('BOL/登陆点里必须原样收录的:', len(strict))
print('111.txt 里已取消（沙赫德 BOL / 旧登陆点）:', len(want & CANCELLED))
print('111.txt 有、代码没用到（且未取消）:', sorted(unused))
print('BOL/登陆点有、111.txt 没有（且非后续新增）:', missing)
print('结论:', '一致' if not missing and not unused else '需检查')
