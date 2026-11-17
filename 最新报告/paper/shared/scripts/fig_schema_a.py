#!/usr/bin/env python3
"""规则示意图：空战单元自卫（schema-3）与空空作战（schema-4）。"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, FancyArrowPatch, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
OUT = os.path.join(PAPER, "schematics")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY, MID, LIGHT, ACC = "#1a1a1a", "#6b6b6b", "#c9c9c9", "#b3261e"


def setup():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": ["Source Han Sans", "DejaVu Sans"],
        "font.size": 7,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "savefig.dpi": 600,
        "axes.linewidth": 0.6,
        "axes.edgecolor": GRAY,
        "axes.labelcolor": GRAY,
        "axes.labelsize": 6.5,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "xtick.labelsize": 5.5,
        "ytick.labelsize": 5.5,
        "text.color": GRAY,
        "lines.linewidth": 0.8,
        "legend.frameon": False,
        "legend.fontsize": 5.5,
    })


def panel_tag(ax, label):
    ax.text(-0.02, 1.02, label, transform=ax.transAxes,
            fontsize=9, fontweight="bold", ha="left", va="bottom", color=GRAY)


def arrow(ax, start, end, color=GRAY, lw=0.7, style="-|>", ls="-",
          connectionstyle="arc3,rad=0", mutation_scale=6, zorder=3):
    patch = FancyArrowPatch(start, end, arrowstyle=style,
                            mutation_scale=mutation_scale, lw=lw,
                            color=color, linestyle=ls,
                            connectionstyle=connectionstyle,
                            shrinkA=0, shrinkB=0, zorder=zorder)
    ax.add_patch(patch)
    return patch


def leader(ax, text, xy, xytext, color=GRAY, ha="left", va="center"):
    return ax.annotate(text, xy=xy, xytext=xytext, fontsize=5.5,
                       color=color, ha=ha, va=va,
                       arrowprops=dict(arrowstyle="-", color=color,
                                       lw=0.55, shrinkA=2, shrinkB=2))


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"),
                    bbox_inches="tight", dpi=600 if ext == "png" else None)
    plt.close(fig)


def draw_aircraft(ax, x, y, direction=1, color=GRAY, scale=1.0, angle=0):
    """俯视飞机简符；direction 控制左右，angle 控制额外旋转角。"""
    theta = np.deg2rad(angle)

    def rotated(px, py):
        px = np.asarray(px) * scale * direction
        py = np.asarray(py) * scale
        return (x + px * np.cos(theta) - py * np.sin(theta),
                y + px * np.sin(theta) + py * np.cos(theta))

    ax.plot(*rotated([-1.5, 1.8], [0, 0]), color=color, lw=0.8,
            solid_capstyle="round", zorder=4)
    ax.plot(*rotated([-0.2, 0.5, -0.2], [-1.2, 0, 1.2]),
            color=color, lw=0.8, zorder=4)
    ax.plot(*rotated([-1.2, -0.8, -1.2], [-0.55, 0, 0.55]),
            color=color, lw=0.7, zorder=4)


def schema_3():
    fig = plt.figure(figsize=(6.1, 4.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.10, 1.0],
                          hspace=0.48, wspace=0.38,
                          left=0.075, right=0.965, top=0.94, bottom=0.09)

    # a：三段式规避几何。横坐标按距离等比例布置。
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 85)
    ax.set_ylim(0, 43)
    ax.axis("off")
    panel_tag(ax, "a")

    ax.text(81, 40.5, "V弹 = 3000 km/h", ha="right", va="top", fontsize=6.0)
    ax.text(81, 36.8, "d₀ = 58.8 km", ha="right", va="top",
            fontsize=6.3, color=ACC, fontweight="bold")

    draw_aircraft(ax, 6, 22, direction=1, scale=1.15)
    ax.text(5.5, 26.2, "我方飞机", ha="center", fontsize=5.8)
    ax.plot(79, 22, marker="<", ms=5.0, color=ACC, zorder=4)
    ax.text(79, 25.5, "来袭弹", ha="center", fontsize=5.8, color=ACC)

    # 唯一一条迎头接近线；三个竖刻度共用同一距离基准。
    ax.plot([6, 79], [22, 22], color=MID, lw=0.7, ls="--", zorder=1)
    arrow(ax, (73.5, 22), (66.5, 22), color=ACC, lw=0.8)
    arrow(ax, (9.5, 22), (16.5, 22), color=GRAY, lw=0.8)
    for distance in (10, 20, 50):
        x = 6 + distance
        ax.plot([x, x], [20.8, 23.2], color=MID, lw=0.65, zorder=2)
    leader(ax, "10 km", (16, 20.8), (16, 18.2), color=MID, ha="center")
    leader(ax, "20 km", (26, 21.0), (33, 19.0), color=MID, ha="center")
    leader(ax, "50 km", (56, 20.8), (56, 18.2), color=MID, ha="center")

    # 50 km：从共同接近线掉头并背向飞行。
    arrow(ax, (56, 22), (39, 32.5), color=ACC, lw=1.2,
          connectionstyle="arc3,rad=-0.42")
    arrow(ax, (39, 32.5), (12, 32.5), color=ACC, lw=1.2)
    leader(ax, "① 掉头 + 加力", (46.5, 30.5), (36, 39.2), color=ACC)

    # 20 km：从同一接近线引出三个折返，说明文字整体置于锯齿下方。
    zig_x = [26, 24.5, 27.5, 24.5, 26]
    zig_y = [22, 18, 14, 17, 11]
    ax.plot(zig_x, zig_y, color=ACC, lw=0.9, ls="--", zorder=3)
    ax.annotate("② 垂直扭动\n缩短分离速度 →", xy=(26.2, 13.0),
                xytext=(36, 6.5), fontsize=5.5, color=ACC,
                ha="left", va="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="-", color=ACC, lw=0.55,
                                shrinkA=3, shrinkB=2))

    # d0 竖线位于 50 km 外侧，直接显示固定规则的错侧。
    ax.plot([64.8, 64.8], [4.0, 34.0], color=ACC, lw=1.35, zorder=2)
    ax.text(65.8, 33.5, "d₀", color=ACC, fontsize=6.2,
            ha="left", va="top", fontweight="bold")

    # b：视线角速度。
    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    d = np.linspace(0.22, 25, 700)
    omega = 0.30 / d * 180 / np.pi
    dc = 0.30 / (25 * np.pi / 180)
    ax.axvspan(5, 25, color=LIGHT, alpha=0.3, zorder=0)
    ax.plot(d, omega, color=GRAY, lw=1.0, zorder=2)
    ax.axhline(25, color=MID, lw=0.75, ls="--", zorder=1)
    ax.plot([dc, dc], [0, 25], color=ACC, lw=0.75, ls="--", zorder=2)
    ax.plot(dc, 25, marker="o", ms=3.0, color=ACC, zorder=3)
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 80)
    ax.set_xticks([0, 5, 10, 15, 20, 25])
    ax.set_yticks([0, 25, 50, 75])
    ax.set_xlabel("d / km")
    ax.set_ylabel("ω_LOS / (°·s⁻¹)")
    ax.text(24.5, 27.2, "ω_max = 25 °/s", ha="right", va="bottom",
            fontsize=5.5, color=MID)
    leader(ax, "d_c ≈ 0.69 km", (dc, 25), (3.1, 36), color=ACC)
    leader(ax, "ω_LOS = V_a / d", (0.72, 0.30 / 0.72 * 180 / np.pi),
           (4.0, 53), color=GRAY)
    ax.text(15.2, 69, "该区间几何脱靶量\n可忽略", ha="center", va="center",
            fontsize=5.7, color=MID, linespacing=1.35)
    ax.tick_params(length=2.2, pad=2)

    # c：弹速衰减与反打点。
    ax = fig.add_subplot(gs[1, 0])
    panel_tag(ax, "c")
    t = np.linspace(0, 240, 500)
    tau = 120.0
    v2500 = 2500 * np.exp(-t / tau)
    v3500 = 3500 * np.exp(-t / tau)
    ax.fill_between(t, 0, 500, color=LIGHT, alpha=0.35, zorder=0)
    ax.plot(t, v2500, color=GRAY, lw=1.0, label="V0 = 2500")
    ax.plot(t, v3500, color=ACC, lw=1.1, label="V0 = 3500")
    ax.axhline(500, color=MID, lw=0.7, ls="--")
    hits = []
    for v0, color in ((2500, GRAY), (3500, ACC)):
        thit = tau * np.log(v0 / 500)
        hits.append(thit)
        ax.plot(thit, 500, marker="o", ms=3.0, color=color, zorder=4)
    leader(ax, "反打点", (hits[0], 500), (116, 930), color=GRAY)
    arrow(ax, (hits[1], 500), (hits[1], 70), color=ACC, lw=0.7,
          mutation_scale=5.5)
    ax.text(hits[1] - 4, 95, "t*", ha="right", va="bottom",
            fontsize=6.0, color=ACC)
    ax.text(120, 215, "能量耗尽区", ha="center", va="center",
            fontsize=5.7, color=MID)
    ax.text(81, 2020, "V0 = 2500", fontsize=5.7, color=GRAY,
            ha="left", va="center", rotation=-25)
    ax.text(69, 2800, "V0 = 3500", fontsize=5.7, color=ACC,
            ha="left", va="center", rotation=-25)
    ax.text(238, 545, "500", fontsize=5.5, color=MID, ha="right", va="bottom")
    ax.set_xlim(0, 240)
    ax.set_ylim(0, 3500)
    ax.set_xticks([0, 60, 120, 180, 240])
    ax.set_yticks([0, 500, 1500, 2500, 3500])
    ax.set_xlabel("t / s")
    ax.set_ylabel("弹速 / km·h⁻¹")
    ax.tick_params(length=2.2, pad=2)

    # d：固定数据裕度条形图。
    ax = fig.add_subplot(gs[1, 1])
    panel_tag(ax, "d")
    speeds = np.array([1500, 2000, 2500, 3000, 3500])
    d0 = np.array([12.0, 26.9, 42.7, 58.8, 75.1])
    rule = np.array([20, 20, 20, 50, 50])
    margins = np.array([1.67, 0.74, 0.47, 0.85, 0.67])
    x = np.arange(len(speeds))
    width = 0.32
    bars0 = ax.bar(x - width / 2, d0, width, color=MID, ec=MID, lw=0.4)
    barsr = ax.bar(x + width / 2, rule, width, color=LIGHT, ec=MID, lw=0.35)
    for bars, values in ((bars0, ["12.0", "26.9", "42.7", "58.8", "75.1"]),
                         (barsr, ["20", "20", "20", "50", "50"])):
        for bar, text in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.3,
                    text, ha="center", va="bottom", fontsize=5.5)
    ax.set_xlim(-0.6, 4.6)
    ax.set_ylim(0, 88)
    ax.set_xticks(x, [str(v) for v in speeds])
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_xlabel("V弹 / km·h⁻¹")
    ax.set_ylabel("距离 / km")
    ax.tick_params(length=2.2, pad=2)

    ax2 = ax.twinx()
    ax2.set_ylim(0, 1.9)
    ax2.set_yticks([0, 0.5, 1.0, 1.5])
    ax2.set_ylabel("裕度")
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(GRAY)
    ax2.spines["right"].set_linewidth(0.6)
    ax2.tick_params(length=2.2, pad=2)
    ax2.axhline(1.0, color=MID, lw=0.65, ls="--", zorder=1)
    ax2.plot(x, margins, color=ACC, lw=0.9, zorder=3)
    ax2.plot(x[margins < 1], margins[margins < 1], "o", ms=3.1,
             mfc=ACC, mec=ACC, mew=0.6, zorder=4)
    ax2.plot(x[margins >= 1], margins[margins >= 1], "o", ms=3.1,
             mfc="white", mec=ACC, mew=0.7, zorder=4)
    margin_offsets = [(0, 7), (0, 7), (0, -11), (0, 7), (0, 7)]
    for xi, yi, text, offset in zip(x, margins,
                                    ["1.67", "0.74", "0.47", "0.85", "0.67"],
                                    margin_offsets):
        ax2.annotate(text, (xi, yi), textcoords="offset points", xytext=offset,
                     ha="center", va="center", fontsize=5.5, color=ACC)
    ax2.text(-0.48, 1.035, "裕度 = 1（临界）", ha="left", va="bottom",
             fontsize=5.5, color=MID)
    handles = [Patch(facecolor=MID, edgecolor=MID, label="d₀"),
               Patch(facecolor=LIGHT, edgecolor=MID, lw=0.35, label="规则取值"),
               Line2D([0], [0], color=ACC, lw=0.9, marker="o", ms=3.0,
                      label="裕度")]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.10, 1.01),
              ncol=3, handlelength=1.3, handletextpad=0.45,
              columnspacing=0.9, borderaxespad=0)
    return fig


def schema_4():
    fig = plt.figure(figsize=(6.1, 2.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.60, 1.65, 1.00],
                          wspace=0.52, left=0.065, right=0.965,
                          top=0.91, bottom=0.23)

    # a：三态势，三幅小图使用同一虚线圆。
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    panel_tag(ax, "a")
    centers = [2.0, 6.2, 10.4]
    for cx in centers:
        # 每个态势都有独立、同大的 0.8 d0 虚线圆及标注。
        ax.add_patch(Ellipse((cx, 3.15), width=3.25, height=1.50,
                             fill=False, ec=MID, lw=0.6, ls="--", zorder=1))
        leader(ax, "0.8 d₀", (cx, 3.90), (cx, 5.05), color=MID, ha="center")

    # 迎头。
    draw_aircraft(ax, 0.90, 3.15, direction=1, scale=0.38)
    draw_aircraft(ax, 3.10, 3.15, direction=-1, color=ACC, scale=0.38)
    arrow(ax, (1.35, 3.15), (1.83, 3.15), color=GRAY, lw=0.65, mutation_scale=5)
    arrow(ax, (2.65, 3.15), (2.17, 3.15), color=ACC, lw=0.65, mutation_scale=5)
    ax.text(2.0, 3.48, "d", ha="center", va="bottom", fontsize=5.8)
    ax.text(2.0, 1.42, "迎头", ha="center", fontsize=6.0)

    # 切向：速度方向夹角约 60°。
    draw_aircraft(ax, 5.35, 2.65, direction=1, scale=0.35)
    draw_aircraft(ax, 6.95, 3.70, direction=1, color=ACC, scale=0.35, angle=240)
    arrow(ax, (5.70, 2.65), (6.62, 2.65), color=GRAY, lw=0.65, mutation_scale=5)
    arrow(ax, (6.65, 3.45), (5.98, 2.75), color=ACC, lw=0.65, mutation_scale=5)
    theta = np.linspace(0, np.pi / 3, 40)
    ax.plot(5.70 + 0.58 * np.cos(theta), 2.65 + 0.58 * np.sin(theta),
            color=MID, lw=0.55)
    ax.text(6.22, 3.14, "θ", fontsize=6.0, color=MID, ha="center")
    ax.text(6.2, 1.42, "切向", ha="center", fontsize=6.0)
    ax.text(6.2, 0.55, "命中概率最高", ha="center", fontsize=5.5, color=ACC)

    # 尾追。
    draw_aircraft(ax, 9.45, 3.15, direction=1, scale=0.35)
    draw_aircraft(ax, 11.25, 3.15, direction=1, color=ACC, scale=0.35)
    arrow(ax, (9.82, 3.15), (10.48, 3.15), color=GRAY, lw=0.65, mutation_scale=5)
    arrow(ax, (11.50, 3.15), (12.02, 3.15), color=ACC, lw=0.65, mutation_scale=5)
    ax.text(10.02, 2.45, "V弹", fontsize=5.5, ha="center")
    ax.text(11.25, 3.85, "V敌", fontsize=5.5, ha="center", color=ACC)
    ax.text(10.4, 1.42, "尾追", ha="center", fontsize=6.0)

    # b：四种策略的命中率与先射时间差。
    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    labels = ["0.8 d₀\n30.1–51.4 km", "固定\n30 km",
              "固定\n60 nm", "最大射程\n90 nm"]
    x = np.arange(4)
    hit_heights = [1.00, 1.00, 0.03, 0.00]
    bars = ax.bar(x, hit_heights, width=0.56,
                  color=[ACC, LIGHT, MID, LIGHT], ec=GRAY, lw=0.4, zorder=2)
    for xi, text, height in zip(x, ["1.00", "1.00", "0.03", "0.00"],
                                hit_heights):
        if xi == 2:
            continue
        label_x = xi - 0.12 if xi in (0, 1) else xi
        label_y = height + (0.130 if xi == 3 else 0.035)
        ax.text(label_x, label_y, text, ha="center", va="bottom",
                fontsize=5.5, zorder=5)
    # 低柱用短补齐线和引出标注保持可读。
    ax.annotate("0.03", xy=(x[2], 0.03), xytext=(x[2], 0.115),
                ha="center", va="bottom", fontsize=5.5,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.55,
                                shrinkA=1, shrinkB=1), zorder=5)
    ax.set_xlim(-0.58, 3.58)
    ax.set_ylim(0, 1.24)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_ylabel("命中率")
    ax.set_xticks(x, labels)
    ax.tick_params(axis="x", length=0, pad=3, labelsize=5.5)
    ax.tick_params(axis="y", length=2.0, pad=2)

    ax2 = ax.twinx()
    ax2.set_ylim(-78, 103)
    ax2.set_yticks([-50, 0, 50, 100])
    ax2.set_ylabel("先射时间差 / s")
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(GRAY)
    ax2.spines["right"].set_linewidth(0.6)
    ax2.tick_params(length=2.0, pad=2)
    ax2.axhline(0, color=MID, lw=0.6, ls="--", zorder=1)
    midpoints = np.array([65.0, 73.45, 0.0, -50.3])
    lower = np.array([46.7, 63.5, 0.0, -57.1])
    upper = np.array([83.3, 83.4, 0.0, -43.5])
    ax2.vlines(x, lower, upper, color=ACC, lw=0.75, zorder=3)
    ax2.plot(x, midpoints, color=ACC, lw=0.85, marker="o", ms=2.8, zorder=4)
    ax2.annotate("+46.7 … +83.3", (x[0], midpoints[0]),
                 xytext=(-2, -17), textcoords="offset points",
                 ha="center", va="top", fontsize=5.5, color=ACC,
                 bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
    ax2.annotate("+63.5 … +83.4", (x[1], midpoints[1]),
                 xytext=(0, 11), textcoords="offset points",
                 ha="center", va="bottom", fontsize=5.5, color=ACC)
    ax2.annotate("0", (x[2], 0), xytext=(0, 7), textcoords="offset points",
                 ha="center", va="bottom", fontsize=5.5, color=ACC)
    ax2.annotate("−43.5 … −57.1", (x[3], midpoints[3]),
                 xytext=(0, -18), textcoords="offset points",
                 ha="center", va="top", fontsize=5.5, color=ACC,
                 bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
    ax2.text(3.47, 3.5, "先射权分界", ha="right", va="bottom",
             fontsize=5.5, color=MID)
    arrow(ax2, (3.40, 72), (3.40, 91), color=ACC, lw=0.6, mutation_scale=5)
    ax2.text(3.28, 81.5, "本方先开火", ha="right", va="center",
             fontsize=5.5, color=ACC, rotation=90)
    arrow(ax2, (-0.43, -38), (-0.43, -58), color=ACC, lw=0.6, mutation_scale=5)
    ax2.text(-0.43, -68, "对手先开火", ha="left", va="center",
             fontsize=5.5, color=ACC,
             bbox=dict(facecolor="white", edgecolor="none", pad=0.5))

    # c：高低差剖面与比能量修正。
    ax = fig.add_subplot(gs[0, 2])
    panel_tag(ax, "c")
    ax.set_xlim(-2, 65)
    ax.set_ylim(5.25, 11.25)
    ax.set_xticks([])
    ax.set_yticks([6.67, 8, 10], ["6.67", "8", "10"])
    ax.set_xlabel("距离", labelpad=2)
    ax.set_ylabel("高度 / km", labelpad=2)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=2.0, pad=2)
    for h in (10, 8, 6.67):
        ax.plot([0, 44], [h, h], color=MID, lw=0.6, ls="--", zorder=1)
    ax.plot(44, 8, marker=">", ms=4.2, color=GRAY, zorder=5)
    ax.text(42.0, 9.60, "目标机 8 km", ha="right", va="bottom", fontsize=5.5)
    ax.text(0.8, 10.25, "我方", ha="left", va="bottom", fontsize=5.5)

    # 抛物线式轨迹：10→8 为俯冲，6.67→8 为爬升。
    s = np.linspace(0, 1, 160)
    for h0, bend, color, lw in ((10, 0.30, ACC, 1.05),
                                (8, 0.60, MID, 0.75),
                                (6.67, 0.45, MID, 0.75)):
        xx = 44 * s
        yy = (1 - s) * h0 + 8 * s + bend * 4 * s * (1 - s)
        ax.plot(xx, yy, color=color, lw=lw, zorder=3)
        arrow(ax, (xx[-3], yy[-3]), (xx[-1], yy[-1]), color=color,
              lw=lw, mutation_scale=5, zorder=4)

    # 高度差双箭头及三项 d0 对应关系。
    arrow(ax, (2.4, 6.67), (2.4, 10), color=MID, lw=0.6,
          style="<->", mutation_scale=5)
    ax.text(3.2, 9.05, "Δh", ha="left", va="center", fontsize=6.0, color=MID)
    for h, text, color in ((10, "d₀ = 44.4 km", ACC),
                           (8, "d₀ = 37.6 km", MID),
                           (6.67, "d₀ = 33.3 km", MID)):
        ax.text(46, h, text, ha="left", va="center", fontsize=5.5, color=color)
    ax.text(23, 5.58, "Δd₀ = ±18% / −11%", ha="center", va="bottom",
            fontsize=5.7, color=ACC)
    return fig


def main():
    setup()
    save(schema_3(), "schema-3-evasion")
    save(schema_4(), "schema-4-aircombat")
    print("已生成 schema-3-evasion 与 schema-4-aircombat 的 SVG/PDF/PNG。")


if __name__ == "__main__":
    main()
