#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 runs.csv / episode_metrics.csv 生成论文用的「实验臂矩阵」Typst 表体。

用法：
  cd 最新报告/实验v2 && ~/.venvs/ai-dev/bin/python analysis/gen_arms_table.py > /tmp/arms.typ

输出是一段可直接粘进 `sections/09-method.typ` 的 `table(...)` 内部行
（每行形如：  [`A0_new`], [`{}`], [20], [11], [469 (114)], [目标],）。
"""
import csv
import os
import random
import statistics as st
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')

# 臂 -> (θ 的 Typst 写法, 该臂要回答的问题)
ARMS = [
    ('V2_A0_new', '{}', '现行新规则（$k=1.2$、$c=0.8$、比例 0.6、分层开）'),
    ('V2_A1_old', r'use_d0=0,\ fire_fixed=111.12', '旧规则组合臂（固定 50/20 km + 固定 111 km）'),
    ('V2_B1_evade50', 'use_d0=0', '只退回固定分档掉头'),
    ('V2_C1_kturn08', 'k_turn=0.8', '掉头门限偏内'),
    ('V2_C2_kturn16', 'k_turn=1.6', '掉头门限偏外'),
    ('V2_WA_f08', 'wra_nm=1', '关掉平台自动开火，规则独自决定开火'),
    ('V2_WB_f06', 'wra_nm=1,\ fire_k=0.6', '关条令 + 更近开火'),
    ('V2_WC_f10', 'wra_nm=1,\ fire_k=1.0', '关条令 + 贴包线开火'),
    ('V2_WD_fix111', 'wra_nm=1,\ fire_fixed=111.12', '关条令 + 固定 111 km 开火'),
    ('V2_E1_sam03', 'sam_ratio=0.3', '地导发弹比例 0.3（蓝方实例）'),
    ('V2_E2_sam10', 'sam_ratio=1.0', '地导发弹比例 1.0（蓝方实例）'),
    ('V2_F1_nolayer', 'ship_layered=0', '舰船不分层补射'),
    ('BLANK_notac', '（不挂战术智能体）', '空白对照：只跑战前配置'),
]


def boot(xs, n=2000, seed=61118):
    if len(xs) < 3:
        return (st.mean(xs) if xs else 0, st.mean(xs) if xs else 0)
    rnd = random.Random(seed)
    k = len(xs)
    ms = sorted(sum(rnd.choice(xs) for _ in range(k)) / k for _ in range(n))
    return ms[int(.025 * n)], ms[int(.975 * n)]


def main():
    rows = list(csv.DictReader(open(os.path.join(DATA, 'episode_metrics.csv'), encoding='utf-8')))
    by = collections.defaultdict(list)
    for r in rows:
        by[r['arm']].append(r)

    print('% 自动生成：analysis/gen_arms_table.py（数据：data/episode_metrics.csv）')
    for arm, theta, why in ARMS:
        v = by.get(arm)
        if not v:
            print('%% %s: 无数据，跳过' % arm)
            continue
        n = len(v)
        full = sum(1 for x in v if x['full_length'] == '1')
        rates = []
        for x in v:
            s = float(x['sim_end_tap'])
            if s > 0:
                rates.append(float(x['score_final']) / (s / 3600))
        mu = st.mean(rates) if rates else 0
        sd = st.pstdev(rates) if len(rates) > 1 else 0
        lo, hi = boot(rates)
        print('      [`%s`], [$%s$], [%d], [%d], [%.0f ($plus.minus$%.0f)], [%s],'
              % (arm, theta, n, full, mu, sd, why))
    print('\n%% 合计 %d 局' % len(rows))


if __name__ == '__main__':
    main()
