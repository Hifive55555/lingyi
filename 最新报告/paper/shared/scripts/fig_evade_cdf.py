#!/usr/bin/env python
"""图：把规避动作提前了多少——触发距离的累计分布（A0 vs 固定分档）。

同一份想定、同一份代码，只把判定距离从"固定 50/20 km"换成 $1.2d_0$。
横轴是触发规避时的弹目距离，纵轴是累计占比；两条竖直参考线是旧规则的两个常数档。
两条曲线的水平间距就是"同样多的规避，新规则早了多远"；按 2600 km/h 的接近速度折算成秒。

输出：paper/shared/figures/fig_evade_cdf.{png,svg}
"""
import csv
import os
import sys

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
INK, MUTED, GRID = "#171b20", "#6b737d", "#e9edf1"
C1, C2 = "#b23a2b", "#2b5d8f"   # 本次规则（朱砂）/ 旧分档（靛蓝）


def load():
    out = {}
    for r in csv.DictReader(open(EVENTS, encoding="utf-8")):
        if r["event"] != "evade_beam" or r["evade_phase"] != "start":
            continue
        if not r["dist_km"] or not r["speed_kmh"]:
            continue
        out.setdefault(r["arm"], []).append((float(r["dist_km"]), float(r["speed_kmh"])))
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

    d = load()
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(6.1, 2.75))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.90, bottom=0.175, wspace=0.33)

    ax.axvspan(0, 20, color="#b0883a", alpha=0.07, lw=0)
    for x, lab in ((20, "旧近档 20 km"), (50, None)):
        ax.axvline(x, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    ax.text(2.0, 0.055, "旧规则在这一段才动", fontsize=6.8, color=C2, ha="left")

    med = {}
    for arm, lab, col, n in (("A0_new", "$1.2d_0$（本次规则）", C1, 2095),
                             ("B1_evade_fix50", "固定 50/20 km 分档", C2, 568)):
        # 线型也编码语义：本次规则实线、旧分档虚线（色盲/黑白打印仍可分）
        xs = np.sort([x for x, _ in d.get(arm, [])])
        ys = np.arange(1, len(xs) + 1) / len(xs)
        ax.plot(xs, ys, color=col, lw=1.5, ls="-" if arm == "A0_new" else (0, (4, 2)),
                label=f"{lab}（n={n}）")
        med[arm] = float(np.median(xs))
        ax.plot([med[arm]], [0.5], "o", ms=4.2, color=col, zorder=5)

    gap = med["A0_new"] - med["B1_evade_fix50"]
    v = 2600.0                                  # km/h，弹速中位 1700 + 本机 900
    ax.annotate("", xy=(med["A0_new"], 0.5), xytext=(med["B1_evade_fix50"], 0.5),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9))
    ax.text((med["A0_new"] + med["B1_evade_fix50"]) / 2, 0.545,
            f"中位差 {gap:.1f} km ≈ {gap / v * 3600:.0f} s", fontsize=7.4,
            color=INK, ha="center")
    for arm, col in (("A0_new", C1), ("B1_evade_fix50", C2)):
        ax.text(med[arm], 0.47, f"{med[arm]:.1f}", fontsize=7.2, color=col,
                ha="center", va="top")

    ax.set_xlim(0, 62)
    ax.set_ylim(0, 1.02)
    ax.set_xticks(range(0, 61, 10))
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("开始规避时的弹目距离 / km", labelpad=2)
    ax.set_ylabel("累计占比", labelpad=2)
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)
    ax.legend(loc="upper left", fontsize=7.0, frameon=False, handlelength=1.6,
              bbox_to_anchor=(0.02, 0.90))

    # ---------- (b) 判定距离随来袭弹速度变化 ----------
    for arm, col, lab in (("A0_new", C1, "$1.2d_0$"),
                          ("B1_evade_fix50", C2, "固定 50/20 km")):
        pts = [(sp, g) for g, sp in
               [(float(r["gate_km"]), float(r["speed_kmh"]))
                for r in csv.DictReader(open(EVENTS, encoding="utf-8"))
                if r["event"] == "evade_beam" and r["evade_phase"] == "start"
                and r["arm"] == arm and r["gate_km"] and r["speed_kmh"]]]
        if not pts:
            continue
        xs = [x for x, _ in pts]
        ys = [y for _, y in pts]
        ax2.scatter(xs, ys, s=2.2, c=col, alpha=0.28 if arm == "A0_new" else 0.55,
                    lw=0)
        ax2.plot([], [], "o", ms=4, color=col, label=f"{lab}（{len(pts)} 次）")
    ax2.set_xlim(600, 2400)
    ax2.set_ylim(0, 100)
    ax2.set_xticks([1000, 1500, 2000])
    ax2.set_yticks([0, 25, 50, 75, 100])
    ax2.set_xlabel("来袭弹速度 / (km/h)", labelpad=2)
    ax2.set_ylabel("判定距离 / km", labelpad=2)
    ax2.grid(True, color=GRID, lw=0.5)
    ax2.set_axisbelow(True)
    for sp in ("top", "right"):
        ax2.spines[sp].set_visible(False)
    ax2.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)
    ax2.legend(loc="lower left", fontsize=6.8, frameon=False, handletextpad=0.4,
               bbox_to_anchor=(0.02, 0.02))
    ax2.text(0.03, 0.96, "(b)", transform=ax2.transAxes, fontsize=9, fontweight="bold",
             va="top")
    ax.text(0.03, 0.96, "(a)", transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top")

    out_png = os.path.join(FIG, "fig_evade_cdf.png")
    out_svg = os.path.join(FIG, "fig_evade_cdf.svg")
    fig.savefig(out_png, dpi=600, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out_svg, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    print("中位：A0 %.1f km，B1 %.1f km，差 %.1f km ≈ %.0f s"
          % (med["A0_new"], med["B1_evade_fix50"], gap, gap / v * 3600))


if __name__ == "__main__":
    main()
