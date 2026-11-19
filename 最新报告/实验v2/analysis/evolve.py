#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""④ 参数演化环（平台在环策略搜索）的离线复算与出图。

输入：`data/episode_metrics.csv`（每局一行，含 arm、theta）
输出：
  `data/knob_effects.csv`  各参数取值相对基线 A0 的效应（得分速率，分/小时）
  `data/evolve_trace.csv`  逐个候选 θ 的评估轨迹（含当前最优）
  `fig/fig_evolve.png`     学习曲线（累计评估局数 → 当前最优得分速率）
  `fig/fig_knob.png`       单参数效应条图（含 95% CI）

口径：
  * 目标函数 = 得分速率 `score_final / (sim_end_tap/3600)`；
  * 每个 θ 的估计 = 该臂各局速率的均值，区间用局级 bootstrap；
  * 「坐标上升」：每个参数只按单参数臂估效应，取效应为正的最佳取值；
  * 「组合验证」：把最佳取值拼成一个 θ*，作为下一轮候选（由 `next_wave.py` 生成实验臂）。

用法：
  cd 最新报告/实验v2 && ~/.venvs/ai-dev/bin/python analysis/evolve.py
"""
import csv
import json
import math
import os
import random
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
FIG = os.path.join(ROOT, 'fig')

BASE = 'A0_new'   # 只用 v1 批次做单因子效应：v1 各臂与 v1 基线同版本，避免跨版本差分
ARM_THETA = {
    'V2_A0_new': {},
    'V2_A1_old': {'legacy': 1},
    'V2_B1_evade50': {'use_d0': 0},
    'V2_C1_kturn08': {'k_turn': 0.8},
    'V2_C2_kturn16': {'k_turn': 1.6},
    'V2_E1_sam03': {'sam_ratio': 0.3},
    'V2_E2_sam10': {'sam_ratio': 1.0},
    'V2_F1_nolayer': {'ship_layered': 0},
    'V2_WA_f08': {'wra_nm': 1},
    'V2_WB_f06': {'wra_nm': 1, 'fire_k': 0.6},
    'V2_WC_f10': {'wra_nm': 1, 'fire_k': 1.0},
    'V2_WD_fix111': {'wra_nm': 1, 'fire_fixed_km': 111.12},
    # v1 臂（空战开火未生效），仅在 v2 缺失时兜底
    'A0_new': {}, 'A1_old_fixed': {'legacy': 1}, 'B1_evade_fix50': {'use_d0': 0},
    'C1_kturn08': {'k_turn': 0.8}, 'C2_kturn16': {'k_turn': 1.6},
    'C3_kturn20': {'k_turn': 2.0}, 'E1_sam03': {'sam_ratio': 0.3},
    'E2_sam10': {'sam_ratio': 1.0}, 'F1_nolayer': {'ship_layered': 0},
    'WA_wra1_f08': {'wra_nm': 1}, 'WB_wra1_f06': {'wra_nm': 1, 'fire_k': 0.6},
    'WC_wra1_f10': {'wra_nm': 1, 'fire_k': 1.0},
    'WD_wra1_fix111': {'wra_nm': 1, 'fire_fixed_km': 111.12},
    'G1_jink': {'vjink': 1},
}
KNOBS = ('k_turn', 'fire_k', 'sam_ratio', 'ship_layered', 'wra_nm')


def load():
    rows = []
    with open(os.path.join(DATA, 'episode_metrics.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                sim = float(r['sim_end_tap'])
                sc = float(r['score_final'])
            except (KeyError, ValueError):
                continue
            if sim <= 0:
                continue
            r['rate'] = sc / (sim / 3600.0)
            rows.append(r)
    return rows


def boot_ci(xs, n=4000, seed=20261118):
    if len(xs) < 2:
        return (xs[0] if xs else 0.0, xs[0] if xs else 0.0)
    rnd = random.Random(seed)
    ms = []
    k = len(xs)
    for _ in range(n):
        ms.append(sum(rnd.choice(xs) for _ in range(k)) / k)
    ms.sort()
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def main():
    rows = load()
    by = {}
    for r in rows:
        by.setdefault(r['arm'], []).append(r['rate'])
    if not by:
        print('没有数据')
        return

    # 基线：v1 的 A0_new；v2 的臂只在 v2 块内与 V2_A0_new 比较，不跨版本差分
    base_arm = BASE if BASE in by else max(by, key=lambda a: len(by[a]))

    def _ver(arm):
        for p_ in ('V2_', 'V3_', 'V4_', 'V5_'):
            if arm.startswith(p_):
                return p_.rstrip('_').lower()
        return 'v1'

    base_ver = _ver(base_arm)
    v2_base = 'V2_A0_new' if 'V2_A0_new' in by else None
    v2_mu = st.mean(by[v2_base]) if v2_base else None
    base_mu = st.mean(by[base_arm])
    print('基线臂 %s：n=%d 得分速率=%.1f 分/小时' % (base_arm, len(by[base_arm]), base_mu))

    # 单参数效应
    eff_rows = []
    for arm, xs in by.items():
        if arm == base_arm:
            continue
        th = ARM_THETA.get(arm, {})
        mu = st.mean(xs)
        lo, hi = boot_ci(xs)
        # 同版本基线：v2 臂对齐 V2_A0_new，其余对齐 v1 的 A0_new
        if _ver(arm) == 'v2' and v2_mu is not None:
            base_mu_ref = v2_mu
        elif _ver(arm) == base_ver:
            base_mu_ref = base_mu
        else:
            continue
        for k, v in th.items():
            if k in KNOBS:
                eff_rows.append({'knob': k, 'value': v, 'arm': arm, 'n': len(xs),
                                 'rate_mean': round(mu, 1),
                                 'delta': round(mu - base_mu_ref, 1),
                                 'ci_low': round(lo - base_mu_ref, 1),
                                 'ci_high': round(hi - base_mu_ref, 1)})
    eff_rows.sort(key=lambda r: (r['knob'], r['value']))
    with open(os.path.join(DATA, 'knob_effects.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(eff_rows[0].keys()))
        w.writeheader()
        w.writerows(eff_rows)
    print('\n%-12s %8s %9s %9s   %s' % ('knob', 'value', 'rate', 'delta', '95%CI(delta)'))
    for r in eff_rows:
        print('%-12s %8s %9.1f %+9.1f   [%+.0f, %+.0f]  %s' %
              (r['knob'], r['value'], r['rate_mean'], r['delta'],
               r['ci_low'], r['ci_high'], r['arm']))

    # 演化轨迹：按「先单参数、再组合」的评估顺序，追踪当前最优
    order = [base_arm] + [r['arm'] for r in eff_rows]
    seen, trace, best, cum = set(), [], base_mu, 0
    for arm in order:
        if arm in seen:
            continue
        seen.add(arm)
        cum += len(by[arm])
        mu = st.mean(by[arm])
        best = max(best, mu)
        trace.append({'seq': len(trace) + 1, 'arm': arm, 'n_episodes': len(by[arm]),
                      'cum_episodes': cum, 'rate_mean': round(mu, 1),
                      'best_so_far': round(best, 1),
                      'theta': json.dumps(ARM_THETA.get(arm, {}), ensure_ascii=False)})
    with open(os.path.join(DATA, 'evolve_trace.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(trace[0].keys()))
        w.writeheader()
        w.writerows(trace)
    print('\n演化轨迹（%d 个候选，累计 %d 局）：' % (len(trace), cum))
    for t in trace:
        print('  #%d %-16s n=%2d 速率=%7.1f 最优=%7.1f  θ=%s' %
              (t['seq'], t['arm'], t['n_episodes'], t['rate_mean'],
               t['best_so_far'], t['theta']))

    # 坐标上升推荐的 θ*
    # 每个旋钮只取“同一版本内最优”：有 v2 臂时只看 v2，否则看 v1
    best_by_knob = {}
    for r in eff_rows:
        is_v2 = r['arm'].startswith('V2_')
        cur = best_by_knob.get(r['knob'])
        if cur is None:
            best_by_knob[r['knob']] = (r['value'], r['delta'], r['ci_low'], is_v2)
        elif is_v2 and not cur[3]:
            best_by_knob[r['knob']] = (r['value'], r['delta'], r['ci_low'], is_v2)
        elif is_v2 == cur[3] and r['delta'] > cur[1]:
            best_by_knob[r['knob']] = (r['value'], r['delta'], r['ci_low'], is_v2)
    star = {k: v[0] for k, v in best_by_knob.items() if v[1] > 0}
    print('\n坐标上升推荐 θ* = %s' % json.dumps(star, ensure_ascii=False))
    print('  （仅采纳 delta>0 的取值；括号内为 delta 与 CI 下界）')
    for k, v in best_by_knob.items():
        print('   %-12s -> %-6s delta=%+.1f  CI下界=%+.1f' % (k, v[0], v[1], v[2]))

    # 图
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=300)
        xs = [t['cum_episodes'] for t in trace]
        ys = [t['best_so_far'] for t in trace]
        ax.step(xs, ys, where='post', lw=1.8, color='#2b5d8f')
        ax.scatter(xs, [t['rate_mean'] for t in trace], s=14, color='#a4acb5', zorder=3)
        ax.set_xlabel('累计评估局数')
        ax.set_ylabel('得分速率（分/小时）')
        ax.grid(alpha=.25)
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, 'fig_evolve.png'))
        fig.savefig(os.path.join(FIG, 'fig_evolve.svg'))
        plt.close(fig)

        if eff_rows:
            fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=300)
            labels = ['%s=%s' % (r['knob'], r['value']) for r in eff_rows]
            vals = [r['delta'] for r in eff_rows]
            los = [r['ci_low'] for r in eff_rows]
            his = [r['ci_high'] for r in eff_rows]
            y = range(len(vals))
            ax.barh(list(y), vals, color='#2b5d8f', height=.6)
            ax.errorbar(vals, list(y), xerr=[[v - l for v, l in zip(vals, los)],
                                            [h - v for v, h in zip(vals, his)]],
                        fmt='none', ecolor='#171b20', elinewidth=1, capsize=2)
            ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=7)
            ax.axvline(0, color='#171b20', lw=.8)
            ax.set_xlabel('相对基线 A0 的得分速率差（分/小时）')
            ax.grid(alpha=.25, axis='x')
            fig.tight_layout()
            fig.savefig(os.path.join(FIG, 'fig_knob.png'))
            fig.savefig(os.path.join(FIG, 'fig_knob.svg'))
            plt.close(fig)
        print('\n图已写到 %s' % FIG)
    except Exception as e:
        print('出图失败（可忽略）：%s' % e)


if __name__ == '__main__':
    main()
