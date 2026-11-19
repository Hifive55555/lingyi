#!/usr/bin/env python
"""图：判定距离在各个射程档上落在哪里。

每个射程档一行。圆点是一个出现过的判定距离取值，圆点越大表示这个值出现得越多；
红色竖线是该档射程的七成，也就是判定距离的上限。最大的那个圆点（众数）压在红线上，
就说明这一档的开火大多停在"射程七成"这个数上。

数据：最新报告/实验v2/data/events.csv 的 fire_aam（gate_km、detail 的 rng_km）。
"""
import collections
import csv
import os
import re

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.lines import Line2D

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
BASE = "/home/hifive/School/2026latter/兵棋比赛智能体报告/最新报告"
EVENTS = os.path.join(BASE, "实验v2", "data", "events.csv")
OUT = os.path.join(BASE, "paper", "shared", "figures")
TIERS = [27.8, 59.3, 111.1, 138.9]
INK, MUTED, GRID = "#22252b", "#6b7378", "#e4e7ea"
DOT, CAPC = "#31506e", "#a0433a"


def load():
    pr = re.compile(r"rng_km=([\d.]+)")
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(EVENTS, encoding="utf-8")):
        if r["event"] != "fire_aam" or not r["detail"] or not r["gate_km"]:
            continue
        m = pr.search(r["detail"])
        if not m:
            continue
        t = round(float(m.group(1)), 1)
        if t in TIERS:
            by[t].append(round(float(r["gate_km"]), 1))
    return by


def main():
    font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_manager.FontProperties(fname=CJK).get_name()],
        "font.size": 9.0, "svg.fonttype": "path", "figure.dpi": 300,
        "axes.edgecolor": "#9aa0a8", "axes.linewidth": 0.6, "axes.unicode_minus": False,
    })
    by = load()
    fig, ax = plt.subplots(figsize=(6.4, 2.55))
    fig.subplots_adjust(left=0.165, right=0.895, top=0.88, bottom=0.235)

    ys = list(range(len(TIERS)))[::-1]
    for i, y in enumerate(ys):
        if i % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="#f5f7f9", lw=0, zorder=0)

    rng = np.random.default_rng(0)
    for y, t in zip(ys, TIERS):
        v = np.array(by[t])
        cap = 0.7 * t
        cnt = collections.Counter(np.round(v, 1))
        mode = cnt.most_common(1)[0]
        ax.scatter(v, y + rng.uniform(-0.20, 0.20, len(v)), s=4.0, color=DOT, alpha=0.20,
                   linewidths=0, zorder=2)
        ax.plot([cap, cap], [y - 0.34, y + 0.34], color=CAPC, lw=2.0, zorder=3,
                solid_capstyle="butt")
        ax.scatter([mode[0]], [y], s=52, color=INK, zorder=5, edgecolors="white",
                   linewidths=0.9)
        ax.annotate("众数 %.1f（%d 次）" % (mode[0], mode[1]), xy=(mode[0], y),
                    xytext=(0, 12), textcoords="offset points", ha="center",
                    fontsize=7.4, color=INK)
        ax.annotate("n=%d" % len(v), xy=(129, y), ha="left", va="center",
                    fontsize=7.4, color=MUTED)

    ax.set_yticks(ys)
    ax.set_yticklabels(["射程 %.1f\n上限 %.1f" % (t, 0.7 * t) for t in TIERS], fontsize=7.6)
    ax.set_xlim(0, 128)
    ax.set_ylim(-0.5, len(TIERS) - 0.5)
    ax.set_xticks([0, 25, 50, 75, 100, 125])
    ax.set_xlabel("开火时的判定距离 / km", labelpad=3)
    ax.grid(True, axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=2, pad=2, colors=MUTED, labelcolor=INK)

    handles = [
        Line2D([], [], marker="o", ls="", color=DOT, ms=3.6, alpha=0.55,
               label="灰点＝每一次开火时的判定距离"),
        Line2D([], [], marker="o", ls="", color=INK, ms=6.5,
               label="黑点＝这一档的众数（出现次数最多的判定距离）"),
        Line2D([], [], color=CAPC, lw=2.0, label="红线＝射程七成（判定距离的上限）"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.44, -0.30), ncol=3,
              frameon=False, fontsize=7.2, handletextpad=0.6, columnspacing=1.6)

    fig.savefig(os.path.join(OUT, "fig_gate_hist.png"), dpi=600, facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(OUT, "fig_gate_hist.svg"), facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    for t in TIERS:
        cnt = collections.Counter(by[t])
        top = cnt.most_common(2)
        print("rng=%.1f n=%4d 上限 %.1f 众数 %s" % (t, sum(cnt.values()), 0.7 * t, top))


if __name__ == "__main__":
    main()
