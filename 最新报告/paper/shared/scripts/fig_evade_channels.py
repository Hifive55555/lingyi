#!/usr/bin/env python
"""图：规避触发由哪一条条件判出，以及"触发点落在判定距离内侧"这件事与采样周期无关。

(a) 三条触发通道的构成（判定距离 / 25 km 兜底 / 60 s 兜底及其他）。
    数据：实验v2/data/events.csv 的 evade_beam start 事件。
(b) 「触发距离 ÷ 判定距离」的分布，三组对照：
    30 s 决策间隔（v1 批次）、5 s（本次基线）、5 s + 放宽威胁入口（CPA 3→8 km、TGO 900→1800 s）。
    中位线用数字标出：三组几乎重合，说明偏差不是采样造成的。

输出：paper/shared/figures/fig_evade_channels.{png,svg}
"""
import csv
import os
import sys
import re
import statistics as st

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # 统一配色与排版（唯一色源）

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
FIG = os.path.join(PAPER, "figures")
EVENTS = os.path.join(os.path.dirname(os.path.dirname(PAPER)), "实验v2", "data", "events.csv")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
INK = "#171b20"
MUTED = "#6b737d"
GRID = "#e9edf1"
C1, C2, C3 = "#2b5d8f", "#b0883a", "#b23a2b"

ARMS = [("A0_new", "A0\n$1.2d_0$"), ("A1_old_fixed", "A1\n固定 50/20"),
        ("B1_evade_fix50", "B1\n固定 50/20")]


def channel(r):
    d, g = float(r["dist_km"]), float(r["gate_km"])
    t = float(r["tgo_s"]) if r["tgo_s"] else None
    if d <= g:
        return "gate"
    if d <= 25.0:
        return "25km"
    return "other"


def load_events():
    rows = [r for r in csv.DictReader(open(EVENTS, encoding="utf-8"))
            if r["event"] == "evade_beam" and r["evade_phase"] == "start"
            and r["dist_km"] and r["gate_km"]]
    return rows


def parse_log(path):
    """.err 日志 -> [(sim_t, dist, gate)]；用 TAC 汇总行的周期号换算仿真时刻（5 s/周期）"""
    ev = re.compile(r"规避\[([^\]]+)\] (?:正横机动|掉头)（弹速(\d+) 距离([\d.]+) 门限([\d.]+)")
    cc = re.compile(r"TAC 汇总：周期(\d+)")
    out, cyc = [], 0
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8", errors="replace"):
        m = cc.search(line)
        if m:
            cyc = int(m.group(1))
            continue
        m = ev.search(line)
        if m:
            out.append((cyc * 5.0, float(m.group(3)), float(m.group(4))))
    return out


def main():
    if os.path.exists(CJK):
        font_manager.fontManager.addfont(CJK)
        fam = font_manager.FontProperties(fname=CJK).get_name()
    else:
        fam = "Noto Sans CJK SC"
    figstyle.apply(mpl)          # 统一：7 pt 正文 / 6.4 pt 刻度 / 0.6 pt 轴线 / 只留左下 spine
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [fam, "Noto Sans CJK SC"],
        "axes.unicode_minus": False,
    })

    rows = load_events()
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(6.0, 2.55),
        gridspec_kw=dict(left=0.085, right=0.985, top=0.90, bottom=0.20, wspace=0.46),
    )

    # ---------- (a) 通道构成 ----------
    names = ["gate", "25km", "other"]
    labels = {"gate": "判定距离触发", "25km": "25 km 兜底", "other": "60 s 兜底及其他"}
    colors = {"gate": C1, "25km": C2, "other": C3}
    ys = np.arange(len(ARMS))[::-1]
    for y, (arm, _) in zip(ys, ARMS):
        sub = [r for r in rows if r["arm"] == arm]
        n = len(sub)
        left = 0.0
        for k in names:
            v = sum(1 for r in sub if channel(r) == k) / n * 100
            ax1.barh(y, v, left=left, height=0.52, color=colors[k],
                     edgecolor="white", lw=0.6,
                     label=labels[k] if y == ys[0] else None)
            if v >= 8:
                ax1.text(left + v / 2, y, f"{v:.0f}%", ha="center", va="center",
                         fontsize=7.2, color="white", fontweight="bold")
            left += v
        ax1.text(99, y - 0.40, f"n={n}", va="bottom", ha="right", fontsize=6.6, color=MUTED)
    ax1.set_yticks(ys)
    ax1.set_yticklabels([lab for _, lab in ARMS], fontsize=7.4, linespacing=1.35)
    ax1.set_xlim(0, 100)
    ax1.set_xticks([0, 25, 50, 75, 100])
    ax1.set_xlabel("规避起始事件的触发通道占比 / %", labelpad=2)
    ax1.grid(axis="x", color=GRID, lw=0.5)
    ax1.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax1.spines[s].set_visible(False)
    ax1.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=7.0,
               frameon=False, handlelength=1.2, columnspacing=1.1, handletextpad=0.5)
    ax1.text(-0.02, 1.13, "(a)", transform=ax1.transAxes, fontsize=9,
             fontweight="bold", va="bottom")

    # ---------- (b) 比值分布：三组对照 ----------
    gate30 = [float(r["dist_km"]) / float(r["gate_km"]) for r in rows
              if r["arm"] == "A0_new" and channel(r) == "gate"]
    base5 = [(d / g) for _, d, g in parse_log("/tmp/v5_a0.err") if g > 0]
    wide5 = [(d / g) for _, d, g in parse_log("/tmp/v5_wide.err") if g > 0]

    groups = [("30 s（v1）", gate30, C1), ("5 s", base5, C2),
              ("5 s + 宽入口", wide5, C3)]
    data = [g[1] for g in groups if g[1]]
    pos = list(range(1, len(data) + 1))
    _Q98 = max(float(np.percentile(np.asarray(d, float), 98)) for d in data)
    _YTOP = max(_Q98, 1.2) * 1.14
    bp = ax2.boxplot(data, positions=pos, widths=0.5, showfliers=False,
                     patch_artist=True, medianprops=dict(color=INK, lw=1.1))
    for p, (_, _, col) in zip(bp["boxes"], [g for g in groups if g[1]]):
        p.set(facecolor=col, alpha=0.34, edgecolor=col, lw=0.9)
    for i, (lab, vals, col) in enumerate([g for g in groups if g[1]]):
        ax2.plot([i + 1], [st.median(vals)], "o", ms=3.4, color=col, zorder=5)
        ax2.text(i + 1, 1.115, f"{st.median(vals):.2f}", ha="center", fontsize=7.0,
                 color=col, fontweight="bold", va="top")
    ax2.axhline(1.0, ls=(0, (5, 4)), color=INK, lw=0.8)
    ax2.text(len(pos) + 0.42, 1.08, "判定距离", fontsize=6.4, color=MUTED, ha="right", va="bottom")
    ax2.set_xticks(pos)
    ax2.set_xticklabels([g[0] for g in groups if g[1]], fontsize=6.8)
    ax2.set_ylim(0, 1.15)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_ylabel("触发距离 ÷ 判定距离", labelpad=4, fontsize=7.6)
    ax2.grid(axis="y", color=GRID, lw=0.5)
    ax2.set_axisbelow(True)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)
    ax2.text(-0.02, 1.10, "(b)", transform=ax2.transAxes, fontsize=9,
             fontweight="bold", va="bottom")


    out_png = os.path.join(FIG, "fig_evade_channels.png")
    out_svg = os.path.join(FIG, "fig_evade_channels.svg")
    fig.savefig(out_png, dpi=600, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out_svg, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    for lab, vals, _ in [g for g in groups if g[1]]:
        print("%-14s n=%4d 中位 %.3f" % (lab, len(vals), st.median(vals)))


if __name__ == "__main__":
    main()
