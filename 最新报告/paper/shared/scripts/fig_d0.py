#!/usr/bin/env python
"""图 11：$d_0$ 的形状，以及固定分档在哪些弹速上已经落在导弹可达范围之内。

两个面板各回答一个问题：
  (a) d0 随导弹初速怎么长 —— 超线性。三条曲线是三个目标速度，同一初速下目标越快、可达范围越短。
  (b) 判定距离 / d0 小于 1 就说明"动手时已经进入导弹可达范围"。两条固定常数档（20 km / 50 km）
      各是一条下降的双曲线，与 1.0 的交点就是它们开始落进可达范围的弹速；1.2 d0 那条是常数 1.2。

原图第二个面板画的是 d0(V0, Va) 的填色等值线，等于把 (a) 的函数再画一遍，而且等值线看不出
"对 Va 二次"。换成本图后，两个面板一个给形状、一个给后果，都和正文的论点直接对应。

字体用思源黑体 Regular（原来那版是 Light，笔画太细，印出来像宋体）。
输出：paper/shared/figures/fig3-d0.{png,svg}
"""
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

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
INK = "#171b20"
MUTED = "#6b737d"
GRID = "#e9edf1"
SEQ = ("#a4bcd9", "#6d92be", "#2b5d8f")   # 目标速度 600/900/1200：单色顺序梯度
C1, C2, C3 = "#6b737d", "#2b5d8f", "#b23a2b"  # 固定 20 km（灰）/ 固定 50 km（靛）/ 本规则（朱砂）

T_A = 240.0        # s
V_TERM = 500.0     # km/h


def d0(V0, Va):
    """线性衰减下的临界距离（km）"""
    V0 = np.asarray(V0, dtype=float)
    if np.isscalar(Va) or np.ndim(Va) == 0:
        Va = float(Va)
        if Va <= V_TERM:                      # 目标慢于终端速度：最大值落在区间端点
            return T_A * (V0 + V_TERM) / 2 / 3600 - T_A * Va / 3600
        return T_A * (V0 - Va) ** 2 / (2 * (V0 - V_TERM)) / 3600
    raise ValueError


def crossing(gate_km, Va=900.0):
    """判定距离 = d0 时的弹速（km/h），用二分找"""
    lo, hi = V_TERM + 1, 6000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if d0(mid, Va) < gate_km:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    if os.path.exists(CJK):
        font_manager.fontManager.addfont(CJK)
        family = font_manager.FontProperties(fname=CJK).get_name()
    else:
        family = "Noto Sans CJK SC"
    figstyle.apply(mpl)          # 统一：7 pt 正文 / 6.4 pt 刻度 / 0.6 pt 轴线 / 只留左下 spine
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [family, "Noto Sans CJK SC"],
        "axes.unicode_minus": False,
    })

    V0 = np.linspace(1400, 4000, 400)
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(6.1, 2.45),
        gridspec_kw=dict(left=0.085, right=0.985, top=0.90, bottom=0.175, wspace=0.30),
    )

    # ---------------- (a) d0 随初速 ----------------
    for color, Va in zip(SEQ, (600, 900, 1200)):
        ax1.plot(V0, d0(V0, Va), color=color, lw=1.3, label=f"$V_a$ = {Va} km/h")
    ax1.set_xlim(1400, 4000)
    ax1.set_ylim(0, 115)
    ax1.set_xticks(range(1500, 4001, 500))
    ax1.set_yticks(range(0, 101, 20))
    ax1.set_xlabel("导弹初速 $V_0$ / (km/h)", labelpad=3)
    ax1.set_ylabel("临界距离 $d_0$ / km", labelpad=2)
    ax1.grid(True, color=GRID, lw=0.5)
    ax1.set_axisbelow(True)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)
    ax1.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)
    ax1.legend(loc="upper left", fontsize=7.2, frameon=False,
               handlelength=1.4, labelspacing=0.32, borderpad=0.1)
    ax1.text(-0.005, 1.045, "(a)", transform=ax1.transAxes, fontsize=9,
             fontweight="bold", va="bottom")

    # ---------------- (b) 判定距离 / d0 ----------------
    va = 900.0
    ax2.axhspan(0, 1, color="#b23a2b", alpha=0.055, lw=0)
    ax2.axhline(1.0, color=INK, lw=0.8, ls="--")
    ax2.plot(V0, 20 / d0(V0, va), color=C1, lw=1.3, label="固定 20 km 档")
    ax2.plot(V0, 50 / d0(V0, va), color=C2, lw=1.3, label="固定 50 km 档")
    ax2.plot(V0, np.full_like(V0, 1.2), color=C3, lw=1.3, ls=(0, (5, 2)),
             label="按 $1.2\\,d_0$ 实时算")

    # 两个交点只在图上留一个空心圈，具体数值写进题注——标在图上会和曲线、1.2 线打架
    for gate, color in ((20, C1), (50, C2)):
        xc = crossing(gate, va)
        ax2.plot([xc], [1.0], "o", ms=3.6, mfc="white", mec=color, mew=1.1, zorder=5)
    ax2.text(1520, 0.58, "可达范围内", fontsize=7.2, color="#b23a2b")
    ax2.text(3960, 1.05, "可达范围外", fontsize=7.2, color=MUTED, ha="right")

    ax2.set_xlim(1400, 4000)
    ax2.set_ylim(0, 2.2)
    ax2.set_xticks(range(1500, 4001, 500))
    ax2.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    ax2.set_xlabel("来袭弹初速 $V_0$ / (km/h)", labelpad=3)
    ax2.set_ylabel("判定距离 $/\\, d_0$（$V_a$ = 900 km/h）", labelpad=2)
    ax2.grid(True, color=GRID, lw=0.5)
    ax2.set_axisbelow(True)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.tick_params(length=2, pad=1.5, colors=MUTED, labelcolor=INK)
    ax2.legend(loc="upper right", fontsize=7.2, frameon=False,
               handlelength=1.5, labelspacing=0.32, borderpad=0.1)
    ax2.text(-0.005, 1.045, "(b)", transform=ax2.transAxes, fontsize=9,
             fontweight="bold", va="bottom")

    out_png = os.path.join(FIG, "fig3-d0.png")
    out_svg = os.path.join(FIG, "fig3-d0.svg")
    fig.savefig(out_png, dpi=600, facecolor="white", bbox_inches="tight",
                pad_inches=0.02)
    fig.savefig(out_svg, facecolor="white", bbox_inches="tight", pad_inches=0.02)
    print("→", out_png, "| 交点：20 km", f"{crossing(20):.0f}", "km/h；50 km",
          f"{crossing(50):.0f}", "km/h")


if __name__ == "__main__":
    main()
