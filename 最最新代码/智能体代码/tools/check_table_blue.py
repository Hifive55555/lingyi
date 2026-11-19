# -*- coding: utf-8 -*-
"""校验：蓝方（人人版）任务表 vs 蓝方人人任务列表.xlsx（防手抄坐标出错）"""
import os
import re
import sys
import types

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from _agentpath import ensure as _ensure
_ensure('Mission_all_blue_hh.py', ROOT)

# ---- 最简桩：只要能把 Mission_all_blue_hh 导入进来读常量 ----
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

import Mission_all_blue_hh as B  # noqa: E402

XLSX = os.path.join(ROOT, '蓝方人人任务列表.xlsx')
wb = openpyxl.load_workbook(XLSX)


def parse_pt(text):
    nums = re.findall(r'-?\d+\.?\d*', str(text))
    return (float(nums[0]), float(nums[1]))


# 后续按用户要求改过的坐标（Excel 里还是旧的）
OVERRIDES = {
    '北2A': {'start': (55.816587, 7.116806)},
}


def check_support():
    ws = wb['支援任务']
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        rows.append(row)
    bad = 0
    by_name = {c[0]: c for c in B.Agent.SUPPORT_TASKS}
    for row in rows:
        name = row[0]
        const = by_name.get(name)
        if const is None:
            print('✗ Excel 里的支援任务[%s] 在代码里找不到' % name)
            bad += 1
            continue
        p1, p2 = parse_pt(row[2]), parse_pt(row[3])
        # 后续按用户要求改过的坐标，以 OVERRIDES 为准
        ov = OVERRIDES.get(name) or {}
        if 'start' in ov:
            p1 = ov['start']
        if 'end' in ov:
            p2 = ov['end']
        for a, b, tag in ((p1, const[1], '起点'), (p2, const[2], '终点')):
            # 起终点相同的任务，代码会把终点北移 0.01°，这里放行
            if abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6:
                continue
            if abs(a[0] - b[0]) > 0.0101 or abs(a[1] - b[1]) > 1e-6:
                print('✗ 支援[%s] %s 不一致: xlsx=%s 代码=%s' % (name, tag, a, b))
                bad += 1
    extra = [c[0] for c in B.Agent.SUPPORT_TASKS if c[0] not in
             {r[0] for r in rows}]
    print('支援任务：Excel %d 条，代码 %d 条（代码多出 %s），不一致 %d 处'
          % (len(rows), len(B.Agent.SUPPORT_TASKS), extra or '无', bad))
    return bad


def check_patrol():
    ws = wb['巡逻任务']
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        rows.append(row)
    bad = 0
    by_name = {c[0]: c for c in B.Agent.PATROL_TASKS}
    for row in rows:
        name = row[0]
        const = by_name.get(name)
        if const is None:
            print('✗ Excel 里的巡逻任务[%s] 在代码里找不到' % name)
            bad += 1
            continue
        pts = [parse_pt(row[i]) for i in (2, 3, 4, 5)]
        for i, (a, b) in enumerate(zip(pts, const[2])):
            if abs(a[0] - b[0]) > 1e-6 or abs(a[1] - b[1]) > 1e-6:
                print('✗ 巡逻[%s] 第%d点 不一致: xlsx=%s 代码=%s'
                      % (name, i + 1, a, b))
                bad += 1
        typ = str(row[1])
        want = ('ANTI_SUBMARINE' if '反潜' in typ else
                'SEA_CONTROL' if '海上控制' in typ else
                'ANTI_MLP' if '反水面及地面' in typ else '?')
        got = const[1].name
        if want != got:
            print('✗ 巡逻[%s] 类型不一致: xlsx=%s 代码=%s' % (name, typ, got))
            bad += 1
    print('巡逻任务：Excel %d 条，代码 %d 条，不一致 %d 处'
          % (len(rows), len(B.Agent.PATROL_TASKS), bad))
    return bad


if __name__ == '__main__':
    n = check_support() + check_patrol()
    print('结论:', '全部一致' if n == 0 else '有 %d 处不一致' % n)
