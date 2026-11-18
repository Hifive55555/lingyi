#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第 2 波（学习/演化环）实验臂生成器。

读取第 1 波结果，按「坐标上升 + 组合验证」给出下一轮候选 θ：
  1) 以「得分速率 = red_score / (sim_end/3600)」为主目标（部分对局提前结束）；
  2) 对每个单参数臂估计效应（相对 A0_new 的差值），形成可加模型；
  3) 取效应为正的参数取值做组合（exploit），再取两个「最不确定」的组合作探索（explore）；
  4) 输出 plan_wave2.json（默认 4 臂 × 8 局）。

用法：
  python next_wave.py --data ../data/arm_summary.csv --runs ../data/runs.csv \
      --out ../plan_wave2.json [--episodes 8] [--top 4]
"""
import argparse
import csv
import json
import math
import os
import random

BASE = 'A0_new'
# 每个臂只动了这些键（用于把臂名映射回 θ）
ARM_THETA = {
    'A0_new': {},
    'A1_old_fixed': {'use_d0': 0, 'fire_fixed_km': 111.12, 'fire_range_coef': 1.0},
    'B1_evade_fix50': {'use_d0': 0},
    'B2_fire_fix111': {'fire_fixed_km': 111.12, 'fire_range_coef': 1.0},
    'C1_kturn08': {'k_turn': 0.8},
    'C2_kturn16': {'k_turn': 1.6},
    'C3_kturn20': {'k_turn': 2.0},
    'D1_fire06': {'fire_k': 0.6},
    'D2_fire10': {'fire_k': 1.0},
    'E1_sam03': {'sam_ratio': 0.3},
    'E2_sam10': {'sam_ratio': 1.0},
    'F1_nolayer': {'ship_layered': 0},
    'G1_jink': {'vjink': 1},
}
# 可组合的键（布尔/定值键不进坐标上升）
KNOBS = ('k_turn', 'fire_k', 'sam_ratio')


def load_runs(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('ok') != 'True':
                continue
            try:
                sim = float(r['sim_end']); sc = float(r['red_score'])
            except (KeyError, ValueError):
                continue
            if sim <= 0:
                continue
            r['rate'] = sc / (sim / 3600.0)          # 分/小时
            rows.append(r)
    return rows


def mean_ci(xs):
    n = len(xs)
    if n == 0:
        return 0.0, 0.0, 0
    m = sum(xs) / n
    if n == 1:
        return m, 0.0, 1
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, sd, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default='../data/runs.csv')
    ap.add_argument('--out', default='../plan_wave2.json')
    ap.add_argument('--episodes', type=int, default=8)
    ap.add_argument('--top', type=int, default=4)
    ap.add_argument('--seed', type=int, default=20261118)
    a = ap.parse_args()

    runs = load_runs(a.runs)
    by = {}
    for r in runs:
        by.setdefault(r['arm'], []).append(r['rate'])

    stats = {}
    for arm, xs in by.items():
        m, sd, n = mean_ci(xs)
        stats[arm] = {'mean': m, 'sd': sd, 'n': n,
                      'rate_mean': m, 'rate_sd': sd}
    base = stats.get(BASE, {'rate_mean': 0.0})
    print('%-16s %5s %9s %9s' % ('arm', 'n', 'rate', 'delta_vs_A0'))
    for arm in sorted(stats, key=lambda k: -stats[k]['rate_mean']):
        print('%-16s %5d %9.1f %9.1f' % (arm, stats[arm]['n'],
                                         stats[arm]['rate_mean'],
                                         stats[arm]['rate_mean'] - base['rate_mean']))

    # 每个参数取值 -> 相对 A0 的效应
    eff = {}
    for arm, st in stats.items():
        if arm == BASE:
            continue
        for k, v in ARM_THETA.get(arm, {}).items():
            if k in KNOBS:
                eff.setdefault(k, {})[v] = st['rate_mean'] - base['rate_mean']

    best = {}
    for k, d in eff.items():
        # 取效应最大的取值；若全为负则取最接近 0 的（保持默认）
        v = max(d, key=lambda x: d[x])
        best[k] = (v, d[v])
        print('knob %-10s best=%s  delta=%+.1f  (all: %s)' %
              (k, v, d[v], {kk: round(vv, 1) for kk, vv in d.items()}))

    # exploit：全部取最优
    cands = []
    cands.append({k: v for k, (v, _) in best.items() if _ > 0})
    # exploit2：只取效应最强的两项
    top2 = sorted(best.items(), key=lambda kv: -kv[1][1])[:2]
    cands.append({k: v for k, (v, _) in top2 if _ > 0})
    # explore：随机扰动（固定种子，可复现）
    rnd = random.Random(a.seed)
    for _ in range(2):
        c = {}
        for k, (v, _) in best.items():
            if rnd.random() < 0.6:
                c[k] = v
        cands.append(c)

    arms, seen = [], {json.dumps({}, sort_keys=True)}
    for c in cands:
        if not c:
            continue
        key = json.dumps(c, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        name = 'W2_' + '_'.join('%s%s' % (k, v) for k, v in sorted(c.items())).replace('.', 'p')
        arms.append({'name': name, 'episodes': a.episodes, 'theta': c})
        if len(arms) >= a.top:
            break

    plan = {
        'scenario': '诺曼底2027(人机协同-人人版)_有红有蓝',
        'decision_interval': 30, 'compression': 10001, 'max_steps': 0,
        'budget_h': 1.8, 'est_s_per_episode': 200, 'episode_timeout_s': 600,
        'out': 'D:/LingYi/exp/v2/runs.jsonl',
        'jobs_dir': 'D:/LingYi/exp/jobs',
        'logs': 'D:/LingYi/exp/v2/logs',
        'tap_dir': 'D:/LingYi/exp/v2/tap',
        'agents': json.load(open(os.path.join(os.path.dirname(__file__), 'agents_block.json'),
                                 encoding='utf-8')) if os.path.exists(
            os.path.join(os.path.dirname(__file__), 'agents_block.json')) else None,
        'arms': arms,
    }
    if plan['agents'] is None:
        plan.pop('agents')
        print('WARN: agents_block.json 缺失，需手工补 agents 字段')
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    print('\nwave2 arms:')
    for x in arms:
        print('  ', x['name'], x['theta'])


if __name__ == '__main__':
    main()
