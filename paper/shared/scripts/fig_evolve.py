#!/usr/bin/env python
"""图：参数演化的学习曲线——19 个候选里只有一个真的往上走，而它被重复测了两次。

横轴是累计评估局数，纵轴是该候选的得分速率（分/小时）。
灰点大小表示该候选跑了几局；蓝线是"到该候选为止的最优"；
橙色空心点标出同一组参数（ship_layered=0）被重复评估的两次，两次相差 27 分/小时，
这个差就是同一配置重复跑 6 局的抖动幅度。

数据：最新报告/实验v2/data/evolve_trace.csv
"""
import csv
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.lines import Line2D

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
BASE = "/home/hifive/School/2026latter/兵棋比赛智能体报告/最新报告"
CSV = os.path.join(BASE, "实验v2", "data", "evolve_trace.csv")
OUT = os.path.join(BASE, "paper", "shared", "figures")
INK, MUTED, GRID = "#22252b", "#6b7378", "#e4e7ea"
LINE, DOTS, SAME = "#2f6db3", "#8f99a3", "#c98a2b"


def load():
    rows = []
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        rows.append(dict(cum=float(r["cum_episodes"]), rate=float(r["rate_mean"]),
                         best=float(r["best_so_far"]), n=int(r["n_episodes"]),
                         arm=r["arm"], theta=r["theta"]))
    return rows


def main():
    font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_manager.FontProperties(fname=CJK).get_name()],
        "font.size": 9.0, "svg.fonttype": "path", "figure.dpi": 300,
        "axes.edgecolor": "#9aa0a8", "axes.linewidth": 0.6, "axes.unicode_minus": False,
    })
    rows = load()
    x = np.array([r["cum"] for r in rows])
    y = np.array([r["rate"] for r in rows])
    b = np.array([r["best"] for r in rows])
    n = np.array([r["n"] for r in rows])
    base = y[0]

    fig, ax = plt.subplots(figsize=(5.75, 2.95))
    fig.subplots_adjust(left=0.105, right=0.975, top=0.93, bottom=0.20)

    ax.axhline(base, color=MUTED, lw=1.0, ls=(0, (5, 3)), zorder=1)
    ax.annotate("基线 %.1f 分/小时" % base, xy=(x[0], base), xytext=(6, 5),
                textcoords="offset points", fontsize=7.6, color=MUTED)

    same = [r for r in rows if '"ship_layered": 0' in r["theta"]]
    normal = [r for r in rows if r not in same]
    ax.scatter([r["cum"] for r in normal], [r["rate"] for r in normal],
               s=8 + 2.2 * np.array([r["n"] for r in normal]), color=DOTS, alpha=0.85,
               edgecolors="white", linewidths=0.8, zorder=3)
    ax.scatter([r["cum"] for r in same], [r["rate"] for r in same], s=70, facecolors="none",
               edgecolors=SAME, linewidths=1.5, zorder=4)

    ax.step(x, b, where="post", color=LINE, lw=2.0, zorder=5)

    ax.annotate("同一组参数测了两次\n%.1f 与 %.1f，差 %.1f\n＝重复跑 6 局的抖动"
                % (same[0]["rate"], same[1]["rate"], same[1]["rate"] - same[0]["rate"]),
                xy=(same[1]["cum"] + 3, same[1]["rate"] - 10), xytext=(96, 248),
                fontsize=7.4, color=SAME, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=SAME, lw=0.7, shrinkA=3, shrinkB=5))

    ax.set_xlim(0, x[-1] + 24)
    ax.set_ylim(180, 585)
    ax.set_xlabel("累计评估局数", labelpad=3)
    ax.set_ylabel("得分速率 / (分/小时)", labelpad=3)
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=2, pad=2, colors=MUTED, labelcolor=INK)

    handles = [
        Line2D([], [], marker="o", ls="", color=DOTS, ms=6.5, label="一个候选（点越大，局数越多）"),
        Line2D([], [], marker="o", ls="", markerfacecolor="none", markeredgecolor=SAME,
               ms=8, label="同一组参数，重复评估"),
        Line2D([], [], color=LINE, lw=2.0, label="到该候选为止的最优"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.40), ncol=3,
              frameon=False, fontsize=7.4, handletextpad=0.6, columnspacing=1.8)

    fig.savefig(os.path.join(OUT, "fig_evolve.png"), dpi=600, facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(OUT, "fig_evolve.svg"), facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    print("候选 %d 个，累计 %d 局；基线 %.1f，最优 %.1f" % (len(rows), x[-1], base, b[-1]))
    print("高于基线的候选：", [r["arm"] for r in rows if r["rate"] > base])


if __name__ == "__main__":
    main()
