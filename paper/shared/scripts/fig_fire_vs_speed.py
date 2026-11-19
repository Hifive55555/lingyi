#!/usr/bin/env python
"""图：开火判定距离由哪一项决定，加大系数有没有用。

(a) 相图。横轴目标速度、纵轴系数 c；曲线 c = 0.7R / d0(Va) 是分界：
    线上方 c·d0 超过射程七成，判定距离被射程项钉住；线下方由 d0 决定。
    三套配置的开火样本按各自 c 画成刻度线，一眼看出各自落在哪个区。
(b) 边际效应。三套配置开火时的弹目距离箱线，同一根上限线：
    c 从 0.6 加到 0.8 变化明显，0.8 到 1.0 不再变化。

数据：最新报告/实验v2/data/events.csv 的 fire_aam（射程 111.1 km 档）。
"""
import csv
import os
import re

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
BASE = "/home/hifive/School/2026latter/兵棋比赛智能体报告/最新报告"
EVENTS = os.path.join(BASE, "实验v2", "data", "events.csv")
OUT = os.path.join(BASE, "paper", "shared", "figures")

V0, VT, T_S, R_MAIN = 4000.0, 500.0, 240.0, 111.1
CAP = 0.7 * R_MAIN
INK, MUTED, GRID = "#22252b", "#6b7378", "#e4e7ea"
C6, C8, C10 = "#6b5ca5", "#2f6db3", "#c98a2b"
FILL_D0, FILL_CAP = "#dce7f5", "#f6e6cf"
ARMS = {"V2_WB_f06": 0.6, "V2_A0_new": 0.8, "V2_WA_f08": 0.8, "V2_WC_f10": 1.0}


def d0(va):
    return T_S / 3600.0 * (V0 - va) ** 2 / (2.0 * (V0 - VT))


def load():
    pv = re.compile(r"Va=([\d.]+)")
    pr = re.compile(r"rng_km=([\d.]+)")
    out = {0.6: ([], []), 0.8: ([], []), 1.0: ([], [])}
    for r in csv.DictReader(open(EVENTS, encoding="utf-8")):
        if r["event"] != "fire_aam" or not r["detail"]:
            continue
        mv, mr = pv.search(r["detail"]), pr.search(r["detail"])
        if not (mv and mr) or abs(float(mr.group(1)) - R_MAIN) > 1e-6:
            continue
        c = ARMS.get(r["arm"])
        if c is None:
            continue
        out[c][0].append(float(mv.group(1)))
        out[c][1].append(float(r["dist_km"]))
    return out


def main():
    font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_manager.FontProperties(fname=CJK).get_name()],
        "font.size": 9.5, "svg.fonttype": "path", "figure.dpi": 300,
        "axes.edgecolor": "#9aa0a8", "axes.linewidth": 0.6, "axes.unicode_minus": False,
    })
    rows = load()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.6, 3.15),
                                 gridspec_kw=dict(width_ratios=[1.18, 1.0], wspace=0.30))
    fig.subplots_adjust(left=0.095, right=0.985, top=0.90, bottom=0.175)

    # ---------- (a) 谁在限制 ----------
    va = np.linspace(90.0, 1010.0, 500)
    edge = CAP / d0(va)
    ax.fill_between(va, edge, 1.35, color=FILL_CAP, lw=0, zorder=0)
    ax.fill_between(va, 0.35, edge, color=FILL_D0, lw=0, zorder=0)
    ax.plot(va, edge, color=INK, lw=1.8, zorder=3)

    colors = {0.6: C6, 0.8: C8, 1.0: C10}
    for c in (0.6, 0.8, 1.0):
        v = np.array(rows[c][0])
        ax.plot(v, np.full_like(v, c) + np.linspace(-0.028, 0.028, len(v)),
                "|", color=colors[c], ms=9, mew=1.1, alpha=0.55, zorder=4)

    ax.text(600, 1.20, "射程项在这里说了算", fontsize=8.6, color="#8a6a2f", ha="center")
    ax.text(690, 0.50, "$d_0$ 在这里说了算", fontsize=8.6, color="#2f5b8a", ha="center")
    ax.annotate("$c$ 从 0.8 加到 1.0，\n整段都在上限区里打", xy=(880, 1.0), xytext=(600, 1.06),
                fontsize=7.8, color=C10,
                arrowprops=dict(arrowstyle="-|>", color=C10, lw=0.7, shrinkA=2, shrinkB=3))
    ax.set_xlim(90, 1015)
    ax.set_ylim(0.4, 1.32)
    ax.set_yticks([0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.6", "0.8", "1.0"])
    ax.set_xlabel("目标速度 / (km/h)", labelpad=3)
    ax.set_ylabel("系数 $c$", labelpad=3)
    ax.set_title("(a)", loc="left", fontsize=10.5, pad=5)

    # ---------- (b) 加大系数有没有用 ----------
    pos = [0, 1, 2]
    data = [np.array(rows[c][1]) for c in (0.6, 0.8, 1.0)]
    bp = bx.boxplot(data, positions=pos, widths=0.46, patch_artist=True, showfliers=False,
               medianprops=dict(color="white", lw=1.5),
               whiskerprops=dict(color=MUTED, lw=0.8),
               capprops=dict(color=MUTED, lw=0.8),
               boxprops=dict(lw=0.9))
    for patch, c in zip(bp["boxes"], (0.6, 0.8, 1.0)):
        patch.set_facecolor(colors[c])
        patch.set_edgecolor(colors[c])
    for i, (c, d) in enumerate(zip((0.6, 0.8, 1.0), data)):
        bx.annotate("%.1f" % np.median(d), xy=(i, np.median(d)), xytext=(0, -2),
                    textcoords="offset points", ha="center", va="top",
                    fontsize=7.8, color="white")
    bx.axhline(CAP, color="#a0433a", lw=1.3, ls=(0, (7, 3)), zorder=1)
    bx.text(-0.58, CAP + 1.6, "射程七成上限 %.1f km" % CAP, fontsize=7.8, color="#a0433a")
    bx.set_xticks(pos)
    bx.set_xticklabels(["0.6", "0.8", "1.0"])
    bx.set_xlim(-0.6, 2.6)
    bx.set_ylim(10, 95)
    bx.set_xlabel("系数 $c$", labelpad=3)
    bx.set_ylabel("开火时的弹目距离 / km", labelpad=3)
    bx.set_title("(b)", loc="left", fontsize=10.5, pad=5)

    for a in (ax, bx):
        a.grid(True, color=GRID, lw=0.5)
        a.set_axisbelow(True)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
        a.tick_params(length=2, pad=2, colors=MUTED, labelcolor=INK)

    fig.savefig(os.path.join(OUT, "fig_fire_vs_speed.png"), dpi=600, facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    fig.savefig(os.path.join(OUT, "fig_fire_vs_speed.svg"), facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    for c in (0.6, 0.8, 1.0):
        d = np.array(rows[c][1])
        v = np.array(rows[c][0])
        print("c=%.1f n=%4d 开火距离中位 %.1f km  P10-P90 %.1f-%.1f  判据触及上限占比 %.0f%%"
              % (c, len(d), np.median(d), np.percentile(d, 10), np.percentile(d, 90),
                 100 * np.mean(CAP / d0(v) <= c)))


if __name__ == "__main__":
    main()
