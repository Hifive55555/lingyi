#!/usr/bin/env python
"""图：规避触发点与判定距离的关系（平台事件级，一个点 = 一次规避）。

一个点 = 一次规避的起始事件。横轴是规则当次算出的判定距离，纵轴是实际动手时的弹目距离。
落在 y = x 虚线下方，表示动手时导弹已经进到判定距离以内；贴在 y = 25 km 点线上，
表示这次规避是硬兜底触发的，而不是判定距离触发的。

数据源：`实验v2/data/events.csv`（`event = evade_beam`、`evade_phase = start` 的 `dist_km`、
`gate_km`、`ratio_gate`）。
输出：paper/shared/figures/fig_evade_scatter.{png,svg}
"""
import csv
import os
import statistics as st

import matplotlib as mpl
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
FIG = os.path.join(PAPER, "figures")
DATA = os.path.join(os.path.dirname(os.path.dirname(PAPER)), "实验v2", "data", "events.csv")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
INK = "#22252b"
MUTED = "#5f676d"
GRID = "#e4e7ea"
BLUE = "#3d6fb0"
RED = "#a0433a"
GREEN = "#3f8a5f"
GREY = "#c8ccd2"

ARMS = [("A0_new", "A0：按 $1.2\\,d_0$ 实时算", BLUE, 9, "o", 0.55),
        ("A1_old_fixed", "A1：固定 20 / 50 km 分档", RED, 11, "s", 0.75),
        ("B1_evade_fix50", "B1：固定 50 / 20 km 分档", GREEN, 26, "^", 0.80)]


def load():
    pts, bg = {}, []
    with open(DATA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["event"] != "evade_beam" or r["evade_phase"] != "start":
                continue
            if not r["dist_km"] or not r["gate_km"]:
                continue
            x, y = float(r["gate_km"]), float(r["dist_km"])
            if r["arm"] in dict((a, 1) for a, *_ in ARMS):
                pts.setdefault(r["arm"], []).append((x, y, float(r["ratio_gate"]) if r["ratio_gate"] else None))
            else:
                bg.append((x, y))
    return pts, bg


def main():
    if os.path.exists(CJK):
        font_manager.fontManager.addfont(CJK)
        fam = font_manager.FontProperties(fname=CJK).get_name()
    else:
        fam = "Noto Sans CJK SC"
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [fam, "Noto Sans CJK SC"],
        "font.size": 8, "axes.unicode_minus": False, "svg.fonttype": "path",
        "figure.dpi": 300, "axes.edgecolor": "#9aa0a8", "axes.linewidth": 0.6,
    })

    pts, bg = load()
    fig, ax = plt.subplots(figsize=(5.2, 3.55))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.975, bottom=0.135)

    nbg = len({r for r in bg})
    if bg:
        bx, by = zip(*bg)
        ax.scatter(bx, by, s=1.6, c=GREY, alpha=0.45, lw=0, zorder=1,
                   label="其余配置（背景）")

    xmax = 125
    ax.plot([0, xmax], [0, xmax], ls=(0, (5, 4)), c=INK, lw=0.9, zorder=4,
            label="y = x（恰好等于判定距离）")
    ax.axhline(25, ls=(0, (1.6, 1.6)), c=RED, lw=1.1, zorder=3,
               label="y = 25 km（硬兜底）")

    handles = []
    for arm, lab, color, ms, mk, alpha in ARMS:
        d = pts.get(arm, [])
        if not d:
            continue
        x = [p[0] for p in d]
        y = [p[1] for p in d]
        h = ax.scatter(x, y, s=ms, marker=mk, c=color, alpha=alpha, lw=0,
                       zorder=5, label=f"{lab}（{len([q for q in d if q[2] is not None])} 次）")
        handles.append((arm, lab.split("：")[0], len(d), color, h))

    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 88)
    ax.set_xticks(range(0, 121, 20))
    ax.set_yticks(range(0, 81, 20))
    ax.set_xlabel("判定距离 $d_{\\mathrm{turn}}$（= $k_{\\mathrm{turn}}\\,d_0$）/ km", labelpad=2)
    ax.set_ylabel("实际触发时的弹目距离 / km", labelpad=2)
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)

    # 右上角小表：n、比值中位、落在 y=x 下方的比例
    rows = []
    for arm, lab, color, *_ in ARMS:
        rg = [p[2] for p in pts.get(arm, []) if p[2] is not None]
        if not rg:
            continue
        rows.append((lab.split("：")[0], len(rg), st.median(rg),
                     sum(r < 1 for r in rg) / len(rg) * 100))
    ax.add_patch(mpl.patches.FancyBboxPatch(
        (0.530, 0.545), 0.470, 0.440, transform=ax.transAxes,
        boxstyle="round,pad=0.012", fc="white", ec="#d5d9de", lw=0.6,
        alpha=0.99, zorder=6, mutation_aspect=1.0))
    tx = [0.548, 0.726, 0.862, 0.982]
    ty = 0.955
    ax.text(tx[0], ty, "配置", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", zorder=7)
    ax.text(tx[1], ty, "n", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", ha="center", zorder=7)
    ax.text(tx[2], ty, "比值中位", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", ha="right", zorder=7)
    ax.text(tx[3], ty, "y=x 下方", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", ha="right", zorder=7)
    for i, (lab, n, med, pct) in enumerate(rows):
        yy = ty - 0.075 * (i + 1) - 0.012
        ax.text(tx[0], yy, lab, transform=ax.transAxes, fontsize=7.2, color=MUTED, va="top", zorder=7)
        ax.text(tx[1], yy, f"{n}", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", ha="center", zorder=7)
        ax.text(tx[2], yy, f"{med:.2f}", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", ha="right", zorder=7)
        ax.text(tx[3], yy, f"{pct:.1f}%", transform=ax.transAxes, fontsize=7.2, color=INK, va="top", ha="right", zorder=7)

    ax.legend(loc="upper left", fontsize=7.0, frameon=True, framealpha=0.95,
              edgecolor="#d5d9de", handletextpad=0.5, labelspacing=0.35,
              borderpad=0.5, scatterpoints=1)

    out_png = os.path.join(FIG, "fig_evade_scatter.png")
    out_svg = os.path.join(FIG, "fig_evade_scatter.svg")
    fig.savefig(out_png, dpi=600, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out_svg, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    print("→", out_png)


if __name__ == "__main__":
    main()
