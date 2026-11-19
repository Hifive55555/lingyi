#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""规则级图（v2 新增）：规避触发比值、开火距离、地导发弹比例。

输入 `data/events.csv`，输出到 `fig/`：
  fig_evade_ratio.png  各臂「触发距离 / 门限」分布（箱线 + 抖动点）
  fig_fire_dist.png    各臂开火距离分布（仅 fire_aam 非零的臂）
  fig_sam_ratio.png    FIRE_RATIO → 发弹次数 / 发弹距离（三点连线）

用法： cd 最新报告/实验v2 && ~/.venvs/ai-dev/bin/python analysis/figs_v2.py
"""
import csv
import os
import statistics as st
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
FIG = os.path.join(ROOT, 'fig')

# 臂的展示名（图上用短名）
SHORT = {
    'A0_new': 'A0 新规则', 'A1_old_fixed': 'A1 旧规则', 'B1_evade_fix50': 'B1 固定50/20',
    'C1_kturn08': 'C1 k=0.8', 'C2_kturn16': 'C2 k=1.6', 'C3_kturn20': 'C3 k=2.0',
    'E1_sam03': 'E1 比例0.3', 'E2_sam10': 'E2 比例1.0', 'F1_nolayer': 'F1 不分层',
    'G1_jink': 'G1 垂直扭动', 'WA_wra1_f08': 'WA 关条令·0.8d0', 'WB_wra1_f06': 'WB 关条令·0.6d0',
    'WC_wra1_f10': 'WC 关条令·1.0d0', 'WD_wra1_fix111': 'WD 关条令·固定111',
    'V2_A0_new': 'A0 新规则(v2)', 'V2_A1_old': 'A1 旧规则(v2)', 'V2_WA_f08': 'WA(v2)',
    'V2_WB_f06': 'WB(v2)', 'V2_WC_f10': 'WC(v2)', 'V2_WD_fix111': 'WD(v2)',
    'V2_B1_evade50': 'B1(v2)', 'V2_C1_kturn08': 'C1(v2)', 'V2_C2_kturn16': 'C2(v2)',
    'V2_E1_sam03': 'E1(v2)', 'V2_E2_sam10': 'E2(v2)', 'V2_F1_nolayer': 'F1(v2)',
}


SYTLE_DIR = os.path.join(os.path.dirname(ROOT), 'paper', 'shared', 'scripts')


def _apply_style():
    """统一风格：字号/轴线/网格/配色取自 paper/shared/scripts/figstyle.py。"""
    import sys
    if SYTLE_DIR not in sys.path:
        sys.path.insert(0, SYTLE_DIR)
    import figstyle
    import matplotlib
    figstyle.apply(matplotlib)


def load():
    with open(os.path.join(DATA, 'events.csv'), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def order_arms(arms):
    pref = ['V2_A0_new', 'A0_new', 'V2_A1_old', 'A1_old_fixed', 'V2_B1_evade50', 'B1_evade_fix50',
            'V2_C1_kturn08', 'C1_kturn08', 'V2_C2_kturn16', 'C2_kturn16',
            'V2_WA_f08', 'WA_wra1_f08', 'V2_WB_f06', 'WB_wra1_f06', 'V2_WC_f10', 'WC_wra1_f10',
            'V2_WD_fix111', 'WD_wra1_fix111', 'V2_E1_sam03', 'E1_sam03', 'V2_E2_sam10', 'E2_sam10',
            'V2_F1_nolayer', 'F1_nolayer', 'G1_jink']
    known = [a for a in pref if a in arms]
    return known + sorted(a for a in arms if a not in known)


def main():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
    except Exception as e:
        print('matplotlib 不可用：%s' % e)
        return
    for cand in ('Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'Source Han Sans SC'):
        if any(f.name == cand for f in font_manager.fontManager.ttflist):
            plt.rcParams['font.sans-serif'] = [cand, 'DejaVu Sans']
            break
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    _apply_style()

    rows = load()

    # ---------- 1) 规避触发比值 ----------
    by = collections.defaultdict(list)
    for r in rows:
        if r['event'] == 'evade_beam' and r.get('evade_phase') == 'start':
            v = num(r.get('ratio_gate'))
            if v is not None:
                by[r['arm']].append(v)
    arms = [a for a in order_arms(by) if len(by[a]) >= 30]
    if arms:
        data = [by[a] for a in arms]
        fig, ax = plt.subplots(figsize=(7.6, 3.8), dpi=300)
        bp = ax.boxplot(data, vert=True, widths=.55, showfliers=False,
                        patch_artist=True, medianprops=dict(color='#171b20', lw=1.2))
        for i, p in enumerate(bp['boxes']):
            p.set_facecolor('#2b5d8f' if arms[i].startswith('V2_') or arms[i] == 'A0_new' else '#b9cde3')
            p.set_edgecolor('#6b737d')
        ax.axhline(1.0, color='#b23a2b', lw=1.0, ls='--')
        ax.text(len(arms) + 0.4, 1.02, '判定距离=触发距离', color='#b23a2b', fontsize=6.4,
                va='bottom', ha='right')
        ax.set_xticks(range(1, len(arms) + 1))
        ax.set_xticklabels([SHORT.get(a, a) for a in arms], rotation=35, ha='right', fontsize=6.4)
        ax.set_ylabel('触发距离 / 门限')
        ax.grid(color='#e9edf1', lw=0.5, axis='y')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, 'fig_evade_ratio.png'))
        fig.savefig(os.path.join(FIG, 'fig_evade_ratio.svg'))
        plt.close(fig)
        print('fig_evade_ratio: %d 臂' % len(arms))

    # ---------- 2) 空战开火距离 ----------
    by2 = collections.defaultdict(list)
    for r in rows:
        if r['event'] == 'fire_aam':
            v = num(r.get('dist_km'))
            if v is not None:
                by2[r['arm']].append(v)
    arms2 = [a for a in order_arms(by2) if len(by2[a]) >= 20]
    if arms2:
        fig, ax = plt.subplots(figsize=(6.8, 3.4), dpi=300)
        for i, a in enumerate(arms2):
            xs = by2[a]
            ax.scatter([i] * len(xs), xs, s=4, alpha=.25,
                       color='#2b5d8f' if (a.startswith('V2_') or a == 'A0_new') else '#a4acb5')
            ax.plot([i - .30, i + .30], [st.median(xs)] * 2, color='#b23a2b', lw=1.8, zorder=4)
        # 射程项封顶：0.7R = 77.8 km（R-77-1 射程 111.1 km）
        ax.axhline(0.7 * 111.1, color='#b23a2b', lw=0.9, ls=(0, (5, 3)), zorder=3)
        ax.text(len(arms2) - 0.45, 0.7 * 111.1 + 1.5, '0.7R = 77.8 km', color='#b23a2b',
                fontsize=6.4, ha='right', va='bottom')
        ax.set_xticks(range(len(arms2)))
        ax.set_xticklabels([SHORT.get(a, a) for a in arms2], rotation=25, ha='right', fontsize=6.4)
        ax.set_ylabel('开火距离 / km')
        ax.grid(color='#e9edf1', lw=0.5, axis='y')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, 'fig_fire_dist.png'))
        fig.savefig(os.path.join(FIG, 'fig_fire_dist.svg'))
        plt.close(fig)
        print('fig_fire_dist: %d 臂' % len(arms2))

    # ---------- 3) 地导比例 → 发弹 ----------
    ep = collections.Counter()
    for r in rows:
        if r['event'] == 'episode_start':
            ep[r['arm']] += 1
    fires = collections.Counter()
    dists = collections.defaultdict(list)
    for r in rows:
        if r['event'] == 'sam_fire':
            fires[r['arm']] += 1
            v = num(r.get('dist_km'))
            if v is not None:
                dists[r['arm']].append(v)
    trio = [('E1_sam03', 0.3), ('A0_new', 0.6), ('E2_sam10', 1.0)]
    trio = [(a, x) for a, x in trio if fires[a]]
    if len(trio) >= 2:
        xs = [x for _, x in trio]
        ys = [fires[a] / max(1, ep[a]) for a, _ in trio]
        md = [st.median(dists[a]) for a, _ in trio]
        fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=300)
        ax.plot(xs, ys, 'o-', color='#2b5d8f', lw=1.8, label='发弹次数/局')
        ax.set_xlabel('开火比例  FIRE_RATIO（× Dmax）')
        ax.set_ylabel('发弹次数 / 局', color='#2b5d8f')
        ax.tick_params(axis='y', labelcolor='#2b5d8f')
        ax2 = ax.twinx()
        ax2.plot(xs, md, 's--', color='#b23a2b', lw=1.6, label='发弹距离中位数')
        ax2.set_ylabel('发弹距离中位数 / km', color='#b23a2b')
        ax2.tick_params(axis='y', labelcolor='#b23a2b')
        ax.grid(alpha=.2)
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, 'fig_sam_ratio.png'))
        fig.savefig(os.path.join(FIG, 'fig_sam_ratio.svg'))
        plt.close(fig)
        print('fig_sam_ratio: %d 点' % len(trio))
    print('done')


if __name__ == '__main__':
    main()
