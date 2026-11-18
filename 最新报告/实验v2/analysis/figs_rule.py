#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""规则级三图：规避触发点（F4）、开火距离 vs 目标速度（F5）、门限按射程档分布（F6）。

图注数据来源（正文图注另写，此处只记口径）：
  输入 `data/events.csv`（`analysis/events.py` 从平台 stderr 日志抽取的规则级事件表）。

  F4 `fig_evade_scatter.png|svg`（2.3.2 空战单元自卫）
    `event = evade_beam` 且 `evade_phase = start` 的行——一次规避会因航路每 30 s 重画而写出多行，
    只有 `start` 那一行的 `dist_km` 是规则的触发距离（`replot` 行的距离已经更小）。
    横轴 `gate_km` = 规则门限（= k_turn·d0），纵轴 `dist_km` = 触发时的弹目距离。
    高亮臂：A0_new / A1_old_fixed / B1_evade_fix50；其余 20 个臂作灰底。
    参考线：y=x（门限本身，虚线）、y=25 km（`EVADE_ALWAYS_KM` 硬兜底，点线）。
    右上角标注：各臂 dist/gate 的中位数、落在 y=x 下方（即 dist < gate）的比例与分母。

  F5 `fig_fire_vs_speed.png|svg`（2.3.3 空空作战）
    `event = fire_aam`，`Va` 从 `detail` 的 `Va=` 解析，`rng_km` 从 `detail` 的 `rng_km=` 解析，
    `dist_km` 取事件列。彩色点 = 五个 v2 臂且弹型为 111.1 km 档（理论曲线按 R=111.1 画，
    换档的弹型封顶是 0.7R 而不是 77.8 km，不能和这三条曲线直接比，故作灰底）。
    理论门限 min(c·d0(Va), 0.7R)，d0 = T(V0-Va)^2 / (2(V0-V_term))，
    参数 T = 240 s、V0 = 4000 km/h、V_term = 500 km/h、R = 111.1 km（R-77-1 对空射程），
    c ∈ {0.6, 0.8, 1.0}；水平虚线 = 射程项封顶 0.7R = 77.8 km。

  F6 `fig_gate_hist.png|svg`（2.3.3 空空作战）
    `event = fire_aam` 的 `gate_km` 直方图，按 `detail` 的 `rng_km` 分 27.8 / 59.3 / 111.1 / 138.9
    四档（其余射程 18.5 / 83.3 km 共 53 次不入四档，见 stdout 计数）。每子图标注样本数与 0.7R。

用法：
  cd 最新报告/实验v2 && ~/.venvs/ai-dev/bin/python analysis/figs_rule.py
输出：
  最新报告/paper/shared/figures/fig_evade_scatter.{png,svg}
  最新报告/paper/shared/figures/fig_fire_vs_speed.{png,svg}
  最新报告/paper/shared/figures/fig_gate_hist.{png,svg}
"""
import csv
import os
import re
import sys

import numpy as np

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # 最新报告/实验v2
EVENTS = os.path.join(ROOT, 'data', 'events.csv')
OUT = os.path.join(os.path.dirname(ROOT), 'paper', 'shared', 'figures')

# d0 与门限的常数（与 Mission_tactics_red 的实现一致，推导见 2.3.1 节）
V0_KH = 4000.0
V_TERM_KH = 500.0
T_DECAY_S = 240.0
FIRE_RANGE_COEF = 0.7
R_MAIN_KM = 111.1                                 # 主力弹 R-77-1 对空射程
EVADE_FLOOR_KM = 25.0                             # EVADE_ALWAYS_KM 硬兜底

# F4：三个高亮臂（臂名, 图例, 颜色, marker, 空心）。A1 与 B1 的门限都是固定 20 km，
# 两列点完全落在 x=20 上，B1 用空心 marker 才不会把下面的 A1 完全盖住。
EVADE_ARMS = [
    ('A0_new', 'A0_new（新规则）', '#1f77b4', 'o', False),
    ('A1_old_fixed', 'A1_old_fixed（旧规则）', '#d62728', 's', False),
    ('B1_evade_fix50', 'B1_evade_fix50（固定 50/20 km）', '#2ca02c', '^', True),
]
# F5：五个高亮臂（臂名, 图例, 颜色, marker）
FIRE_ARMS = [
    ('V2_A0_new', 'A0_new（0.8d0）', '#1f77b4', 'o'),
    ('V2_WA_f08', 'WA（关条令，0.8d0）', '#2ca02c', 's'),
    ('V2_WB_f06', 'WB（关条令，0.6d0）', '#9467bd', '^'),
    ('V2_WC_f10', 'WC（关条令，1.0d0）', '#ff7f0e', 'D'),
    ('V2_WD_fix111', 'WD（关条令，固定 111 km）', '#8c564b', 'v'),
]
BANDS = [27.8, 59.3, 111.1, 138.9]


def setup_font():
    """返回 True 表示图内可用中文标签。

    只接受注册了 regular(400) 字重的族：本机 matplotlib 只把 Noto Sans CJK 的可变字体
    注册成 100（Thin），9 pt 下笔画过细，故退到同设计的 Source Han Sans SC（Noto Sans CJK
    即其重命名版，字宽与字形一致）。
    """
    from matplotlib import font_manager as fm

    weights = {}
    for f in fm.fontManager.ttflist:
        weights.setdefault(f.name, set()).add(f.weight)
    for name in ('Noto Sans CJK SC', 'Source Han Sans SC', 'WenQuanYi Micro Hei'):
        if 400 in weights.get(name, set()):
            plt.rcParams['font.sans-serif'] = [name, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['svg.fonttype'] = 'path'
            print(f'font: {name} (regular)')
            return True
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    print('WARNING: 未找到 Noto Sans CJK SC，图内改用英文标签', file=sys.stderr)
    return False


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def kv(detail):
    return dict(re.findall(r'([A-Za-z_]+)=(-?\d+(?:\.\d+)?)', detail or ''))


def d0_km(va):
    """线性减速（V0 -> V_term，历时 T）下能追上的临界距离，km。"""
    return T_DECAY_S * (V0_KH - np.asarray(va, dtype=float)) ** 2 / (2.0 * (V0_KH - V_TERM_KH)) / 3600.0


def gate_theory(va, c, rng=R_MAIN_KM):
    return np.minimum(c * d0_km(va), FIRE_RANGE_COEF * rng)


def load():
    """单遍流式读 events.csv：返回规避触发点与开火事件。"""
    evade = []     # (arm, gate_km, dist_km)
    fire = []      # (arm, Va, rng_km, dist_km, gate_km)
    with open(EVENTS, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row['event']
            if name == 'evade_beam':
                if row['evade_phase'] != 'start':
                    continue
                gate = fnum(row['gate_km'])
                dist = fnum(row['dist_km'])
                if gate is None or dist is None or gate <= 0:
                    continue
                evade.append((row['arm'], gate, dist))
            elif name == 'fire_aam':
                detail = kv(row['detail'])
                va = fnum(detail.get('Va'))
                rng = fnum(detail.get('rng_km'))
                dist = fnum(row['dist_km'])
                gate = fnum(row['gate_km'])
                if None in (va, rng, dist, gate):
                    continue
                fire.append((row['arm'], va, rng, dist, gate))
    return evade, fire


def say(zh, en):
    return zh if ZH else en


def fig_evade_scatter(evade):
    hi = {arm: ([], []) for arm, _, _, _, _ in EVADE_ARMS}
    bg_gate, bg_dist = [], []
    for arm, gate, dist in evade:
        if arm in hi:
            hi[arm][0].append(gate)
            hi[arm][1].append(dist)
        else:
            bg_gate.append(gate)
            bg_dist.append(dist)

    fig, ax = plt.subplots(figsize=(7.0, 4.9))
    ax.scatter(bg_gate, bg_dist, s=3.0, c='#c9c9c9', alpha=0.35, linewidths=0,
               zorder=1, label=say(f'其余 {len(set(a for a, _, _ in evade)) - len(hi)} 个臂（背景）',
                                   'other arms (background)'))
    stats = []
    for arm, label, color, marker, hollow in EVADE_ARMS:
        g = np.asarray(hi[arm][0])
        d = np.asarray(hi[arm][1])
        if hollow:
            ax.scatter(g, d, s=16.0, marker=marker, facecolors='none', edgecolors=color,
                       alpha=0.65, linewidths=0.55, zorder=2, label=label)
        else:
            ax.scatter(g, d, s=10.0, marker=marker, c=color, alpha=0.5, linewidths=0,
                       zorder=2, label=label)
        stats.append((arm, len(g), float(np.median(d / g)), int((d < g).sum())))

    x_line = np.array([0.0, 135.0])
    ax.plot(x_line, x_line, ls='--', c='k', lw=1.0, zorder=3,
            label=say('y = x（门限本身）', 'y = x (gate)'))
    ax.axhline(EVADE_FLOOR_KM, ls=':', c='#d62728', lw=1.6, zorder=3,
               label=say(f'y = {EVADE_FLOOR_KM:.0f} km（硬兜底）', f'y = {EVADE_FLOOR_KM:.0f} km (hard floor)'))

    ax.set_xlim(0, 132)
    ax.set_ylim(0, 96)
    ax.set_xlabel(say('门限 gate_km（= k_turn·d0）/ km', 'gate_km (= k_turn·d0) / km'), fontsize=9)
    ax.set_ylabel(say('实际触发距离 dist_km / km', 'trigger distance dist_km / km'), fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.22, lw=0.5, zorder=0)
    ax.legend(fontsize=8, loc='upper left', framealpha=0.92, borderpad=0.5, labelspacing=0.35)

    # 右上角统计块（x>60 的上方是该区唯一有散点处，故压半透明白框保证可读；分母即 n 列）
    ax.add_patch(Rectangle((0.495, 0.715), 0.5, 0.28, transform=ax.transAxes,
                           facecolor='white', alpha=0.93, edgecolor='#9a9a9a', lw=0.6, zorder=4))
    col = (0.512, 0.700, 0.845, 0.992)
    rows = [say('臂', 'arm'), say('n（分母）', 'n (denominator)'), say('dist/gate 中位', 'median dist/gate'),
            say('落在 y=x 下方', 'below y = x')]
    ys = (0.958, 0.891, 0.824, 0.757)
    for x, txt in zip(col, rows):
        ax.text(x, ys[0], txt, transform=ax.transAxes, fontsize=7.4, color='#333333',
                ha='left' if x == col[0] else 'right', va='center', zorder=5)
    for (arm, n, med, below), y in zip(stats, ys[1:]):
        ax.text(col[0], y, arm, transform=ax.transAxes, fontsize=7.4, ha='left', va='center', zorder=5)
        ax.text(col[1], y, f'{n}', transform=ax.transAxes, fontsize=7.4, ha='right', va='center', zorder=5)
        ax.text(col[2], y, f'{med:.2f}', transform=ax.transAxes, fontsize=7.4, ha='right', va='center', zorder=5)
        ax.text(col[3], y, f'{below / n:.1%}', transform=ax.transAxes,
                fontsize=7.4, ha='right', va='center', zorder=5)

    fig.tight_layout()
    save(fig, 'fig_evade_scatter')
    print('[F4] evade_beam/start 触发点（dist<gate 记为「落在 y=x 下方」）')
    for arm, n, med, below in stats:
        print(f'  {arm:16s} n={n:5d}  dist/gate 中位={med:.3f}  下方={below:5d}/{n}（{below / n:.1%}）')
    print(f'  背景臂 {len(set(a for a, _, _ in evade)) - len(stats)} 个：{len(bg_gate)} 点')
    return stats


def fig_fire_vs_speed(fire):
    hi = {arm: ([], []) for arm, _, _, _ in FIRE_ARMS}
    bg_va, bg_dist = [], []
    for arm, va, rng, dist, gate in fire:
        if arm in hi and abs(rng - R_MAIN_KM) < 1e-6:
            hi[arm][0].append(va)
            hi[arm][1].append(dist)
        else:
            bg_va.append(va)
            bg_dist.append(dist)

    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    bg_handle = ax.scatter(bg_va, bg_dist, s=5.0, c='#c9c9c9', alpha=0.30, linewidths=0, zorder=1,
                           label=say('背景：其他臂与其他射程档', 'background: other arms / range bands'))

    va = np.linspace(80.0, 1000.0, 921)
    curves = [
        (0.6, dict(ls=(0, (6.0, 2.2)), c='#222222', lw=1.6, zorder=4),
         say('理论门限 0.6·d0（取 0.7R）', 'theory min(0.6·d0, 0.7R)')),
        (0.8, dict(ls=(0, (5.0, 1.6, 1.0, 1.6)), c='#222222', lw=1.6, zorder=4),
         say('理论门限 0.8·d0（取 0.7R）', 'theory min(0.8·d0, 0.7R)')),
        # c=1.0 在本场 Va 范围（≤920 km/h）内一直大于 0.7R，曲线与封顶线完全重合，
        # 画粗灰线 + 封顶红虚线压在上面，两者在虚线的缝隙里叠成一条。
        (1.0, dict(ls='-', c='#9c9c9c', lw=3.4, alpha=0.8, zorder=2),
         say('理论门限 1.0·d0（≡ 0.7R，与封顶线重合）', 'theory min(1.0·d0, 0.7R): ≡ 0.7R')),
    ]
    theory_handles = [ax.plot(va, gate_theory(va, c), label=label, **style)[0] for c, style, label in curves]
    theory_handles.append(ax.axhline(
        FIRE_RANGE_COEF * R_MAIN_KM, ls=(0, (5.0, 4.0)), c='#d62728', lw=1.7, zorder=5,
        label=say('射程项封顶 0.7R = 77.8 km', 'range cap 0.7R = 77.8 km')))

    arm_handles = [bg_handle]
    arm_labels = [bg_handle.get_label()]
    for arm, label, color, marker in FIRE_ARMS:
        arm_handles.append(ax.scatter(hi[arm][0], hi[arm][1], s=26.0, marker=marker, c=color, alpha=0.55,
                                      linewidths=0.3, edgecolors='white', zorder=3, label=label))
        arm_labels.append(label)

    ax.set_xlim(100, 1000)
    ax.set_ylim(0, 120)
    ax.set_xticks(range(100, 1001, 100))
    ax.set_xlabel(say('目标速度 Va（detail 的 Va=）/ km/h', 'target speed Va / km/h'), fontsize=9)
    ax.set_ylabel(say('开火距离 dist_km / km', 'firing distance dist_km / km'), fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.22, lw=0.5, zorder=0)
    # 图例放到坐标区下方，分臂、理论两组：5 臂 + 3 曲线 + 封顶线共 10 项，区内没有这么大一块空白，
    # 压在数据上会遮点。
    arms_leg = ax.legend(arm_handles, arm_labels, fontsize=7.6, loc='upper center',
                         bbox_to_anchor=(0.5, -0.10), ncol=3, frameon=False,
                         labelspacing=0.35, columnspacing=1.6, handletextpad=0.6)
    ax.add_artist(arms_leg)
    ax.legend(theory_handles, [h.get_label() for h in theory_handles], fontsize=7.6,
              loc='upper center', bbox_to_anchor=(0.5, -0.215), ncol=2, frameon=False,
              labelspacing=0.35, columnspacing=1.6, handletextpad=0.6)

    fig.tight_layout()
    save(fig, 'fig_fire_vs_speed')

    print('[F5] fire_aam（彩色点 = 111.1 km 弹型档；门限与三条理论曲线的吻合度按该档算）')
    for arm, label, _, _ in FIRE_ARMS:
        v = np.asarray(hi[arm][0])
        d = np.asarray(hi[arm][1])
        n_all = sum(1 for a, _, _, _, _ in fire if a == arm)
        if len(v) == 0:
            print(f'  {arm:14s} n(111.1档)=0')
            continue
        gates = np.array([g for a, _, r, _, g in fire if a == arm and abs(r - R_MAIN_KM) < 1e-6])
        fit = {c: float(np.mean(np.abs(gates - gate_theory(v, c)) <= 0.2)) for c, _, _ in curves}
        best = max(fit, key=fit.get)
        tag = f'最贴合 c={best}' if fit[best] >= 0.5 else '三条曲线都不吻合（固定门限 111.1 km）'
        print(f'  {arm:14s} n(111.1档)={len(v):4d}（全部射程档 {n_all:4d}）  Va P50={np.median(v):.0f} km/h  '
              f'dist P50={np.median(d):.1f} km  dist/gate 中位={np.median(d / gates):.2f}  '
              f'门限吻合: ' + ' '.join(f'c={c}:{f * 100:.0f}%' for c, f in sorted(fit.items())) + f'  → {tag}')
    print(f'  背景点 {len(bg_va)} 个（其他臂 + 其他射程档）')


def fig_gate_hist(fire):
    by_band = {b: [] for b in BANDS}
    other = {}
    for arm, va, rng, dist, gate in fire:
        if rng in by_band:
            by_band[rng].append(gate)
        else:
            other[rng] = other.get(rng, 0) + 1

    bins = np.arange(0.0, 120.0, 2.5)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.9), sharex=True)
    for ax, band in zip(axes.ravel(), BANDS):
        vals = np.asarray(by_band[band])
        cap = FIRE_RANGE_COEF * band
        counts, _, _ = ax.hist(vals, bins=bins, color='#4c78a8', alpha=0.85,
                               edgecolor='white', linewidth=0.4)
        ax.axvline(cap, ls='--', c='#d62728', lw=1.3, zorder=4)
        ax.set_ylim(0, max(counts.max(), 1) * 1.18)
        ax.set_title(say(f'射程档 rng_km = {band:.1f} km\nn = {len(vals)}，理论封顶 0.7R = {cap:.1f} km',
                         f'rng_km = {band:.1f} km\nn = {len(vals)}, 0.7R = {cap:.1f} km'), fontsize=8.5)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.22, lw=0.5, axis='y')
    for ax in axes[1]:
        ax.set_xlabel(say('开火门限 gate_km / km', 'firing gate gate_km / km'), fontsize=9)
    for ax in axes[:, 0]:
        ax.set_ylabel(say('开火次数', 'fire events'), fontsize=9)
    axes[0][0].set_xlim(0, 118)
    fig.tight_layout()
    cap_handle = Line2D([], [], ls='--', c='#d62728', lw=1.3)
    fig.legend([cap_handle], [say('红色虚线 = 该射程档的理论封顶 0.7R', 'red dashed = theory cap 0.7R')],
               loc='lower center', bbox_to_anchor=(0.5, -0.015), frameon=False, fontsize=8)
    save(fig, 'fig_gate_hist')

    print('[F6] fire_aam 按 detail 的 rng_km 分档')
    for band in BANDS:
        vals = np.asarray(by_band[band])
        print(f'  rng={band:6.1f} km  n={len(vals):5d}  0.7R={FIRE_RANGE_COEF * band:5.1f} km  '
              f'gate 众数={np.median(vals):6.1f} km（P50），最大={vals.max():.1f} km')
    print(f'  不入四档的射程：{sorted(other.items())}，共 {sum(other.values())} 次')


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for suffix in ('.png', '.svg'):
        fig.savefig(os.path.join(OUT, name + suffix), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  -> {os.path.join(OUT, name)}.png|svg')


def main():
    global ZH
    ZH = setup_font()
    print(f'font/cjk={ZH}; events={EVENTS}')
    evade, fire = load()
    fig_evade_scatter(evade)
    fig_fire_vs_speed(fire)
    fig_gate_hist(fire)


ZH = False

if __name__ == '__main__':
    main()
