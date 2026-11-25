# -*- coding: utf-8 -*-
"""校验：任务表常量 vs 任务列表.xlsx（防手抄坐标出错）"""
import os
import re
import sys
import types

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from _agentpath import ensure as _ensure
_ensure('Mission_all_red.py', ROOT)

# ---- 最简桩：只要能把 Mission_all_red 导入进来读常量 ----
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

XLSX = None
for _name in ('红方人人任务列表.xlsx', '任务列表.xlsx'):
    _p = os.path.join(ROOT, _name)
    if os.path.exists(_p):
        XLSX = _p
        break
if XLSX is None:
    raise SystemExit('找不到红方任务列表 xlsx（红方人人任务列表.xlsx / 任务列表.xlsx）')
wb = openpyxl.load_workbook(XLSX)


def parse_pt(text):
    nums = re.findall(r'-?\d+\.?\d*', str(text))
    return (float(nums[0]), float(nums[1]))


# 按要求暂时注释掉的支援任务（代码里没有是正常的）
SKIP_SUPPORT = {
    '左55-1', '左35-1', '苏27-2', '苏57-1', '苏57-2', '苏57-3',
    '苏30下', '苏30右', '北鹰狮-1', '北鹰狮-2',
}
# 按要求删掉的巡逻任务
SKIP_PATROL = {'S70-3'}
# 后续按要求改过坐标的支援任务（以代码为准）
COORD_OVERRIDES = {
    '北35-1': {'start': (52.560513, 1.544638),
               'end': (52.803664, 4.192573)},
    # 2026-11-25 合并对面（决赛）版本：左阵风5 编入了特拉法尔加/雷鸣/戴高乐/
    # PR.2235.0#2，航线随之改到北海方向；xlsx 还是旧点，以代码为准。
    '左阵风5': {'start': (47.123779, -4.278493),
                'end': (47.132004, -2.568771)},
}


def check_support():
    ws = wb['支援任务']
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        rows.append(row)
    # 允许代码里额外新增（A~E 登陆编队支援任务不在 Excel 里）
    by_name = {c[0]: c for c in R.Agent.SUPPORT_TASKS}
    bad = 0
    for row in rows:
        name = row[0]
        if name in SKIP_SUPPORT:
            continue                    # 已按要求注释掉
        const = by_name.get(name)
        if const is None:
            print('✗ Excel 里的支援任务[%s] 在代码里找不到' % name)
            bad += 1
            continue
        p1, p2 = parse_pt(row[2]), parse_pt(row[3])
        ov = COORD_OVERRIDES.get(name) or {}
        p1 = ov.get('start', p1)
        p2 = ov.get('end', p2)
        cname, c1, c2 = const[0], const[1], const[2]
        for a, b, tag in ((p1, c1, '起点'), (p2, c2, '终点')):
            if abs(a[0] - b[0]) > 1e-6 or abs(a[1] - b[1]) > 1e-6:
                print('✗ 支援[%s] %s 不一致: xlsx=%s 代码=%s' % (name, tag, a, b))
                bad += 1
        if name != cname:
            print('✗ 任务名不一致: xlsx=%s 代码=%s' % (name, cname))
            bad += 1
    extra = [c[0] for c in R.Agent.SUPPORT_TASKS if c[0] not in
             {r[0] for r in rows}]
    print('支援任务：Excel %d 条，代码 %d 条（代码多出 %s），坐标/名称不一致 %d 处'
          % (len(rows), len(R.Agent.SUPPORT_TASKS), extra or '无', bad))
    return bad


def check_patrol():
    """
    逐条比对 Excel 与 PATROL_TASKS（按任务名匹配，允许代码里额外新增任务）。

    比赛期间按用户要求新增了「反潜巡逻」，它不在 Excel 里，属正常。
    """
    ws = wb['巡逻任务']
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        rows.append(row)

    by_name = {c[0]: c for c in R.Agent.PATROL_TASKS}
    # 后续按要求改过名的任务
    renamed = {'保护船只': '中间保船'}
    # 后续按要求改过参考点的任务（以代码为准）
    point_overrides = {
        '阵风2': [(49.887483, 0.867620), (49.262512, 1.319737),
                  (50.236411, 2.339777), (50.420554, 1.609962)],
        'S70-1': [(49.309963, -2.354200), (48.435346, -1.721087),
                  (48.256206, -0.057564), (49.432592, -0.402715)],
        'S70-2': [(49.164396, -0.091327), (48.209604, 0.004134),
                  (48.606595, 2.441496), (49.309869, 1.625361)],
        '保护船只': [(49.569167, -1.297403), (49.491055, -1.363648),
                     (49.418070, -0.672153), (49.562069, -0.738725)],
    }
    bad = 0
    for row in rows:
        name = row[0]
        if name in SKIP_PATROL:
            continue                    # 已按要求删除
        const = by_name.get(renamed.get(name, name))
        if const is None:
            print('✗ Excel 里的巡逻任务[%s] 在代码里找不到' % name)
            bad += 1
            continue
        pts = point_overrides.get(name) or [parse_pt(row[i])
                                            for i in (2, 3, 4, 5)]
        cpts = list(const[2])
        for i, (a, b) in enumerate(zip(pts, cpts)):
            if abs(a[0] - b[0]) > 1e-6 or abs(a[1] - b[1]) > 1e-6:
                print('✗ 巡逻[%s] 第%d点 不一致: xlsx=%s 代码=%s'
                      % (name, i + 1, a, b))
                bad += 1
        # 任务类型（表格里把“防空压制”写成了“防控压制”，一起认；
        #   保护船只 已按要求改成“中间保船/防空作战巡逻”）
        typ = str(row[1])
        want = ('ANTI_LAND' if '反地面' in typ else
                'SEAD' if ('防空压制' in typ or '防控压制' in typ) else
                'SEA_CONTROL' if '海上控制' in typ else
                'ANTI_SUBMARINE' if '反潜' in typ else '?')
        if renamed.get(name) == '中间保船':
            want = 'AIR'
        got = const[1].name
        if want != got:
            print('✗ 巡逻[%s] 类型不一致: xlsx=%s 代码=%s' % (name, typ, got))
            bad += 1

    extra = [c[0] for c in R.Agent.PATROL_TASKS if c[0] not in
             {r[0] for r in rows}]
    print('巡逻任务：Excel %d 条，代码 %d 条（代码新增 %s），'
          '坐标/名称/类型不一致 %d 处'
          % (len(rows), len(R.Agent.PATROL_TASKS), extra or '无', bad))
    return bad


if __name__ == '__main__':
    n = check_support() + check_patrol()
    print('结论:', '全部一致' if n == 0 else '有 %d 处不一致' % n)
