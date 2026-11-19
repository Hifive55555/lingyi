#!/usr/bin/env python
"""图：五个规则模块每步耗时，以及它占实测单步墙钟的比例。

横轴是"200 个同类单元各遍历 60 个目标"时一次调用的总耗时（ms），
条末注明它占满时长局单步墙钟 0.343 s 的比例。用来回答"规则计算是不是瓶颈"。

数据：纯函数微基准（表 tab:perf）+ `experiment/runs.csv` 的满时长局单步均值。
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
OUT = "/home/hifive/School/2026latter/兵棋比赛智能体报告/最新报告/paper/shared/figures"
STEP_MEAN = 343.0            # ms，满时长局单步墙钟
INK, MUTED, GRID = "#171b20", "#6b737d", "#e9edf1"
BAR = "#2b5d8f"

ROWS = [
    ("物理作战域三维监控", 2.2, 4.4, "7.4–10.2 µs/单元"),
    ("空战单元自卫", 2.1, 2.1, "10.4 µs/机"),
    ("空空作战", 1.4, 1.4, "6.8–7.2 µs/机"),
    ("地空导弹营", 1.0, 1.0, "4.8 µs/营"),
    ("登陆船只集群自卫", 0.05, 0.05, "<1 µs/舰"),
]


def main():
    font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_manager.FontProperties(fname=CJK).get_name()],
        "font.size": 9.0, "svg.fonttype": "path", "figure.dpi": 300,
        "axes.edgecolor": "#171b20", "axes.linewidth": 0.6, "axes.unicode_minus": False,
    })
    fig, ax = plt.subplots(figsize=(6.2, 2.45))
    fig.subplots_adjust(left=0.295, right=0.86, top=0.93, bottom=0.215)

    ys = np.arange(len(ROWS))[::-1]
    for y, (name, lo, hi, unit) in zip(ys, ROWS):
        ax.barh(y, lo, height=0.46, color=BAR, alpha=0.95, zorder=3)
        if hi > lo:
            ax.barh(y, hi - lo, left=lo, height=0.46, color=BAR, alpha=0.35, zorder=3)
        share = hi / STEP_MEAN * 100
        txt = "%.1f ms（%.1f%%）" % (hi, share) if share >= 0.1 else "%.2f ms（<0.1%%）" % hi
        ax.annotate(txt, xy=(hi, y), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=7.2, color=INK)
        ax.annotate(unit, xy=(-0.12, y), ha="right", va="center", fontsize=7.0, color=MUTED)

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in ROWS], fontsize=7.6)
    ax.set_xlim(0, 7.0)
    ax.set_ylim(-0.6, len(ROWS) - 0.4)
    ax.set_xlabel("一次调用的总耗时 / ms（200 单元 × 60 目标）", labelpad=3)
    ax.grid(True, axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=2, pad=2, colors=MUTED, labelcolor=INK)

    fig.savefig(os.path.join(OUT, "fig_perf_share.png"), dpi=600, facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(OUT, "fig_perf_share.svg"), facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    for name, lo, hi, _ in ROWS:
        print("%-10s %.2f ms  占 %.1f%%" % (name, hi, hi / STEP_MEAN * 100))


if __name__ == "__main__":
    main()
