#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""过程图（F9 事件时序 / F3 步耗-在飞弹量）：

  fig_event_timeline  F9  各类事件按 30 min 分箱的事件数（第 3 章 3.3）
  fig_step_vs_missiles F3 单步墙钟 vs 该步在飞弹药数（第 2 章 2.4）

数据来源：
  F9  `data/events.csv`（逐事件行，全臂 206 局合计），按 sim_t 30 min 分箱计数。
      计的是**日志事件条数**：`evade_beam` 含 start/replot 两相，`threat` 受 monitor()
      节流（tgo<=120 s 或每 20 周期），`sam_fire` 为每战术周期重复记录的发弹令，
      故数值是"强度/频次"而非物理发射枚数。
  F3  `raw/tap/*__红方.jsonl`（一行 = 一个决策步）：x = cts 中 type_code==1（在飞弹药）
      的条数，cts 隔步采集 → 用前值填充；y = 相邻两行 wall 之差（单步墙钟）。
      过滤 wall 差 <=0（重试导致 i/t 归零）或 >5 s（引擎重启/暂停）的异常步。
      x 为整数计数，散点横坐标加 ±0.18 抖动仅防重叠，平滑与拟合用未抖动的原值。

用法： cd 最新报告/实验v2 && ~/.venvs/ai-dev/bin/python analysis/figs_process.py
输出： ../paper/shared/figures/fig_event_timeline.{png,svg}
       ../paper/shared/figures/fig_step_vs_missiles.{png,svg}
"""
import collections
import csv
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
TAP = os.path.join(ROOT, 'raw', 'tap')
FIG = os.path.join(ROOT, 'fig')          # 写到实验目录，避免覆盖论文插图

BIN_S = 30 * 60          # 30 min 分箱
SIM_END = 180 * 60       # 满时长 180 min
NBIN = SIM_END // BIN_S  # 6 个箱：0-30, …, 150-180

# 事件类型 → (图例名, 颜色)
EVENTS = [
    ('evade_beam', '规避机动', '#2b5d8f'),
    ('fire_aam', '空战开火', '#b23a2b'),
    ('sam_fire', '地导发弹', '#b0883a'),
    ('threat', '威胁告警', '#33907f'),
]

# 阶段底色：0-30 首波 / 30-60 高潮 / 60-180 登陆与防空
PHASES = [
    (0, 30, '首波', '#f8e9e5'),
    (30, 60, '高潮', '#f9f0e0'),
    (60, 180, '登陆与防空', '#e7eef7'),
]

STEP_GAMES = 25          # F3 抽样局数（20–30）
STEP_MAX_PTS = 400       # F3 每局最多点数
STEP_SEED = 20271
STALE_S = 5.0            # wall 差 > 5 s 视为引擎重启/暂停
FULL_MEAN_S = 0.34       # 满时长局单步墙钟均值（全部有效步实测 0.348 s）


def _apply_style():
    """统一风格：字号/轴线/网格/配色取自 paper/shared/scripts/figstyle.py。"""
    import os
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    fs = os.path.join(os.path.dirname(os.path.dirname(here)), 'paper', 'shared', 'scripts')
    if fs not in sys.path:
        sys.path.insert(0, fs)
    import figstyle
    import matplotlib
    figstyle.apply(matplotlib)


def setup_matplotlib():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for cand in ('Noto Sans CJK SC', 'Source Han Sans SC', 'WenQuanYi Zen Hei'):
        if any(f.name == cand for f in font_manager.fontManager.ttflist):
            plt.rcParams['font.sans-serif'] = [cand, 'DejaVu Sans']
            break
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    _apply_style()
    return plt


def save(fig, name):
    fig.savefig(os.path.join(FIG, name + '.png'), dpi=300)
    fig.savefig(os.path.join(FIG, name + '.svg'), dpi=300)
    print('写入 %s.{png,svg}' % name)


def style_axes(ax):
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.grid(alpha=.22, lw=.6)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- F9
def load_events():
    with open(os.path.join(DATA, 'events.csv'), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def bin_events(rows):
    """→ (每类每箱计数, 每类首末时刻, 每箱仍存活的局数(在险), 总局数)。"""
    counts = {ev: np.zeros(NBIN, int) for ev, _, _ in EVENTS}
    span = {}
    ep_end = collections.defaultdict(float)
    for r in rows:
        key = (r['arm'], r['episode_idx'])
        t = float(r['sim_t'])
        if t > ep_end[key]:
            ep_end[key] = t
        ev = r['event']
        if ev in counts:
            counts[ev][min(int(t // BIN_S), NBIN - 1)] += 1
            lo, hi = span.get(ev, (t, t))
            span[ev] = (min(lo, t), max(hi, t))
    at_risk = [sum(1 for v in ep_end.values() if v >= b * BIN_S) for b in range(NBIN)]
    return counts, span, at_risk, len(ep_end)


def fig_event_timeline(plt, rows):
    counts, span, at_risk, n_ep = bin_events(rows)
    edges = np.arange(0, SIM_END + 1, BIN_S) / 60.0
    centers = (edges[:-1] + edges[1:]) / 2

    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=300)
    ymax = max(c.max() for c in counts.values())
    for lo, hi, label, color in PHASES:
        ax.axvspan(lo, hi, color=color, alpha=.55, lw=0, zorder=0)
        ax.text((lo + hi) / 2, ymax * 1.045, label, ha='center', va='bottom',
                fontsize=8.5, color='#6b737d', zorder=5)

    for ev, label, color in EVENTS:
        ax.plot(centers, counts[ev], 'o-', color=color, lw=1.7, ms=4.2,
                label='%s（%d）' % (label, counts[ev].sum()), zorder=3)

    ax.set_xlim(0, 180)
    ax.set_xticks(edges)
    ax.set_ylim(0, ymax * 1.18)
    ax.set_yticks(range(0, int(ymax * 1.18) + 1, 3000))
    ax.set_xlabel('仿真时间 / min（每 30 min 一格）')
    ax.set_ylabel('每 30 min 事件数（%d 局合计）' % n_ep)
    ax.legend(loc='lower center', bbox_to_anchor=(.5, 1.0), ncol=4, frameon=False,
              fontsize=8, handlelength=1.6, columnspacing=1.4, handletextpad=.4)
    style_axes(ax)
    fig.tight_layout()
    save(fig, 'fig_event_timeline')
    plt.close(fig)

    # ---- 供正文引用的分箱表（markdown，打印到 stdout）
    head = '| 时段 / min | ' + ' | '.join(lbl for _, lbl, _ in EVENTS) + ' | 合计 | 在险局数 |'
    print('\n## F9 分箱表（events.csv，%d 局全臂合计）\n' % n_ep)
    print(head)
    print('| --- |' + ' ---: |' * (len(EVENTS) + 2))
    for b in range(NBIN):
        vals = [counts[ev][b] for ev, _, _ in EVENTS]
        print('| %d–%d | %s | %d | %d |' % (
            b * 30, (b + 1) * 30, ' | '.join(str(v) for v in vals), sum(vals), at_risk[b]))
    tot = [counts[ev].sum() for ev, _, _ in EVENTS]
    print('| 合计 | %s | %d | %d |' % (
        ' | '.join(str(v) for v in tot), sum(tot), n_ep))
    print('\n首末事件时刻（仿真 min）：')
    for ev, label, _ in EVENTS:
        lo, hi = span[ev]
        print('  %-6s 首 %6.1f  末 %6.1f' % (label, lo / 60, hi / 60))
    print('  evade_beam 分解：start %d / replot %d' % (
        sum(1 for r in rows if r['event'] == 'evade_beam' and r['evade_phase'] == 'start'),
        sum(1 for r in rows if r['event'] == 'evade_beam' and r['evade_phase'] == 'replot')))


# ---------------------------------------------------------------- F3
def game_points(path):
    """一局 tap → ([(在飞弹药数, 单步墙钟 s), …], 被跳过的异常步数)。"""
    pts = []
    prev_wall = None
    inflight = 0
    skipped = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            cts = d.get('cts')
            if cts is not None:                       # 隔步采集 → 稀疏值覆盖，其余沿用前值
                inflight = sum(1 for c in cts if c[1] == 1)
            wall = d.get('wall')
            if wall is not None and prev_wall is not None:
                dt = wall - prev_wall
                if 0 < dt <= STALE_S:
                    pts.append((inflight, dt))
                else:
                    skipped += 1
            if wall is not None:
                prev_wall = wall
    return pts, skipped


def pick_games(paths, k):
    """按文件名排序等距取样，覆盖各臂与各批次。"""
    idx = np.unique(np.linspace(0, len(paths) - 1, k).round().astype(int))
    return [paths[i] for i in idx]


def lowess(xs, ys, grid, frac=.3):
    """局部线性回归（tricube 权），返回 grid 上的平滑值与有效样本数。"""
    n = len(xs)
    k = max(int(np.ceil(frac * n)), 8)
    order = np.argsort(xs, kind='mergesort')
    xs_s, ys_s = xs[order], ys[order]
    out, ns = [], []
    for g in grid:
        d = np.abs(xs_s - g)
        idx = np.argpartition(d, k - 1)[:k]
        h = d[idx].max() or 1.0
        w = (1 - np.clip(d[idx] / h, 0, 1) ** 3) ** 3
        X = xs_s[idx]
        Ym = ys_s[idx]
        sw = w.sum()
        if sw <= 0:
            out.append(np.nan)
            ns.append(0)
            continue
        xm = (w * X).sum() / sw
        ym = (w * Ym).sum() / sw
        sxx = (w * (X - xm) ** 2).sum()
        sxy = (w * (X - xm) * (Ym - ym)).sum()
        slope = sxy / sxx if sxx > 1e-12 else 0.0
        out.append(ym + slope * (g - xm))
        ns.append(len(idx))
    return np.array(out), np.array(ns)


def rankdata(v):
    order = np.argsort(v, kind='mergesort')
    r = np.empty(len(v), float)
    r[order] = np.arange(len(v), dtype=float)
    # 处理并列：取平均秩（x 为小整数，必须做）
    _, inv, cnt = np.unique(v, return_inverse=True, return_counts=True)
    if (cnt > 1).any():
        sums = np.zeros(len(cnt))
        np.add.at(sums, inv, r)
        r = (sums / cnt)[inv]
    return r


def fig_step_vs_missiles(plt):
    paths = sorted(glob.glob(os.path.join(TAP, '*__红方.jsonl')))
    kept = pick_games(paths, STEP_GAMES)
    rng = np.random.default_rng(STEP_SEED)

    xs, ys, per_game = [], [], []
    skipped = 0
    for path in kept:
        pts, sk = game_points(path)
        per_game.append(len(pts))
        skipped += sk
        if len(pts) > STEP_MAX_PTS:
            sel = rng.choice(len(pts), STEP_MAX_PTS, replace=False)
            pts = [pts[i] for i in sorted(sel)]
        xs.extend(pt[0] for pt in pts)
        ys.extend(pt[1] for pt in pts)
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)

    # 全 203 局的有效步，用于核 0.34 s 满时长步均与全样本相关系数
    full = [pt for path in paths for pt in game_points(path)[0]]
    full_x = np.asarray([pt[0] for pt in full], float)
    full_y = np.asarray([pt[1] for pt in full], float)
    mean_all = full_y.mean()
    r_full = float(np.corrcoef(full_x, full_y)[0, 1])
    slope_full = float(np.polyfit(full_x, full_y, 1)[0])

    r = float(np.corrcoef(xs, ys)[0, 1])
    rho = float(np.corrcoef(rankdata(xs), rankdata(ys))[0, 1])
    slope, icpt = np.polyfit(xs, ys, 1)

    fig, ax = plt.subplots(figsize=(6.6, 3.5), dpi=300)
    ylim = (0.0, max(0.60, np.percentile(ys, 99.5) * 1.25))
    clipped = int((ys > ylim[1]).sum())
    jit = np.random.default_rng(STEP_SEED + 1).uniform(-.18, .18, len(xs))
    ax.scatter(xs + jit, ys, s=3.2, alpha=.10, color='#2b5d8f', edgecolors='none', zorder=2)

    grid = np.arange(0, xs.max() + .05, .25)
    sm, ns = lowess(xs, ys, grid)
    ok = ns >= 30
    ax.plot(grid[ok], sm[ok], color='#2b5d8f', lw=2.0, zorder=4)
    ax.annotate('局部线性平滑', (grid[ok][-1], sm[ok][-1]),
                xytext=(-4, 8), textcoords='offset points',
                ha='right', va='bottom', fontsize=8, color='#2b5d8f')

    ax.axhline(FULL_MEAN_S, color='#b23a2b', lw=1.2, ls='--', zorder=3)
    ax.annotate('满时长步均 %.2f s' % FULL_MEAN_S, (xs.max() + .45, FULL_MEAN_S),
                xytext=(0, 5), textcoords='offset points',
                ha='right', va='bottom', fontsize=8, color='#b23a2b')

    ax.set_xlim(-.7, xs.max() + .7)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(0, int(xs.max()) + 1, 2))
    ax.set_xlabel('该步在飞弹药数（cts 中 type=1 的条数，隔步采集前值填充）')
    ax.set_ylabel('该步墙钟 / s（相邻两行 wall 差）')
    style_axes(ax)
    ax.text(.985, .04,
            '%d 局抽样 · n=%d 步（跳过 %d 条 >5 s 异常步、纵轴外 %d 点）\n'
            'Pearson r=%.3f · Spearman ρ=%.3f\n拟合 y = %.4f·x + %.3f s' % (
                len(kept), len(xs), skipped, clipped, r, rho, slope, icpt),
            transform=ax.transAxes, ha='right', va='bottom', fontsize=7.2,
            color='#6b737d', linespacing=1.5,
            bbox=dict(boxstyle='round,pad=0.35', fc='white', ec='#d8dde3', lw=.6, alpha=.92))
    fig.tight_layout()
    save(fig, 'fig_step_vs_missiles')
    plt.close(fig)

    print('\n## F3\n')
    print('抽样局数 %d / %d（每局点数 中位 %d，上限 %d），散点 n=%d'
          % (len(kept), len(paths), int(np.median(per_game)), STEP_MAX_PTS, len(xs)))
    print('在飞弹药数：均值 %.2f  中位 %d  P95 %d  最大 %d'
          % (xs.mean(), np.median(xs), np.percentile(xs, 95), xs.max()))
    print('单步墙钟：均值 %.3f  中位 %.3f  P95 %.3f  最大 %.3f s'
          % (ys.mean(), np.median(ys), np.percentile(ys, 95), ys.max()))
    print('Pearson r=%.3f  Spearman ρ=%.3f  OLS 斜率 %.4f s/弹  截距 %.3f s'
          % (r, rho, slope, icpt))
    print('全 203 局（n=%d）：步均 %.4f s；Pearson r=%.3f；OLS 斜率 %.4f s/弹'
          % (len(full_y), mean_all, r_full, slope_full))
    print('注：图注统计量按抽样散点（n=%d）计算；纵轴外 %d 点未绘出。'
          % (len(xs), clipped))


def main():
    plt = setup_matplotlib()
    os.makedirs(FIG, exist_ok=True)
    fig_event_timeline(plt, load_events())
    fig_step_vs_missiles(plt)


if __name__ == '__main__':
    main()
