#!/usr/bin/env python
"""规则示意图：监控、地空导弹营与船只自卫。"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (
    Arc,
    Circle,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
OUT = os.path.join(PAPER, "schematics")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY, MID, LIGHT, ACC = "#1a1a1a", "#6b6b6b", "#c9c9c9", "#b3261e"


def setup():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": ["Source Han Sans"],
        "font.size": 7,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "savefig.dpi": 600,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "legend.frameon": False,
        "text.color": GRAY,
        "axes.edgecolor": GRAY,
    })


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(
            os.path.join(OUT, f"{name}.{ext}"),
            bbox_inches="tight",
            dpi=600 if ext == "png" else None,
        )
    plt.close(fig)
    print(f"  -> schematics/{name}.svg/.pdf/.png")


def panel_tag(ax, label):
    ax.text(-0.02, 1.02, label, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="bottom", ha="left", color=GRAY)


def arrow(ax, start, end, color=MID, lw=0.7, style="-|>", ls="-",
          rad=0.0, scale=6, zorder=3):
    patch = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=scale,
        lw=lw, color=color, linestyle=ls, zorder=zorder,
        connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0,
    )
    ax.add_patch(patch)
    return patch


def rect(ax, x, y, w, h, ec=GRAY, lw=0.7, fc="none", ls="-",
         rounded=False, zorder=2):
    if rounded:
        patch = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.10",
            fc=fc, ec=ec, lw=lw, ls=ls, zorder=zorder,
        )
    else:
        patch = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls,
                          zorder=zorder)
    ax.add_patch(patch)
    return patch


# ---------------------------------------------------------------- 监控
def schema_1():
    fig = plt.figure(figsize=(6.1, 2.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.22, 1.0], wspace=0.18,
                          left=0.035, right=0.985, bottom=0.07, top=0.89)

    # a：公共监控底座的一进三出，以及尚未实现的判定算法。
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    panel_tag(ax, "a")

    rect(ax, 0.35, 1.0, 2.05, 6.1, lw=0.7)
    ax.text(1.375, 6.35, "战场态势\n（只读）", ha="center", va="center",
            fontsize=6.1, linespacing=1.35)
    for i, yy in enumerate((2.15, 3.35, 4.55)):
        xx = np.linspace(0.72, 2.02, 40)
        yy_curve = yy + 0.22 * np.sin(np.linspace(0.0, 2.4 + i * 0.4, 40))
        ax.plot(xx, yy_curve, color=GRAY, lw=0.6, zorder=3)
        ax.plot(xx[-1], yy_curve[-1], marker=">", ms=2.8, color=GRAY,
                zorder=3)

    rect(ax, 4.0, 1.8, 4.15, 5.2, ec=ACC, lw=1.2)
    ax.text(6.075, 6.42, "监控智能体", ha="center", va="center",
            fontsize=6.5, color=ACC, fontweight="bold")
    ax.text(6.075, 5.35, "筛选：指向本方的弹", ha="center", va="center",
            fontsize=5.9)
    ax.text(6.075, 4.42, "输出：弹型 ＋ 弹速", ha="center", va="center",
            fontsize=5.9)
    rect(ax, 4.72, 2.48, 2.72, 0.92, ec=MID, lw=0.7, ls="--")
    ax.text(6.08, 2.94, "判定算法未实现", ha="center", va="center",
            fontsize=5.8, color=MID)

    arrow(ax, (2.4, 4.35), (4.0, 4.35), color=GRAY, lw=1.0, scale=7)
    ax.text(3.2, 4.72, "每步观测", ha="center", va="bottom", fontsize=5.6)

    outputs = ((6.0, "飞机"), (4.05, "船"), (2.10, "地空导弹营"))
    for yy, label in outputs:
        rect(ax, 10.05, yy - 0.48, 1.65, 0.96, lw=0.7)
        ax.text(10.875, yy, label, ha="center", va="center", fontsize=5.8)
    arrow(ax, (8.15, 4.4), (10.05, 6.0), color=MID)
    arrow(ax, (8.15, 4.35), (10.05, 4.05), color=MID)
    arrow(ax, (8.15, 4.3), (10.05, 2.10), color=MID)
    ax.text(9.12, 5.47, "时刻调用", ha="center", va="bottom", fontsize=5.3,
            color=MID, rotation=25)
    ax.text(9.10, 4.43, "时刻调用", ha="center", va="bottom", fontsize=5.3,
            color=MID)
    ax.text(9.10, 2.93, "时刻调用", ha="center", va="bottom", fontsize=5.3,
            color=MID, rotation=-25)

    # b：指向判据与最近接近几何。
    ax = fig.add_subplot(gs[0, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    panel_tag(ax, "b")

    M = np.array([2.0, 5.15])
    P = np.array([6.75, 6.45])
    ax.plot(M[0], M[1], marker="o", ms=4.0, color=GRAY, zorder=4)
    ax.text(M[0] - 0.15, M[1] - 0.55, "我方单位 M", ha="center", va="top",
            fontsize=5.8)
    ax.plot(P[0], P[1], marker="^", ms=5.2, color=ACC, zorder=4)
    ax.text(P[0] + 0.15, P[1] + 0.40, "来袭弹 P", ha="center", va="bottom",
            fontsize=5.8, color=ACC)
    ax.plot([M[0], P[0]], [M[1], P[1]], color=MID, lw=0.7, ls="--")
    direction = (M - P) / np.linalg.norm(M - P)
    extension = P + 1.32 * (M - P)
    ax.plot([P[0], extension[0]], [P[1], extension[1]], color=MID,
            lw=0.6, ls="--", zorder=1)
    ax.text(4.18, 6.14, "d", ha="center", va="bottom", fontsize=6.3,
            color=MID, rotation=15)

    v_end = np.array([8.75, 7.25])
    arrow(ax, tuple(P), tuple(v_end), color=ACC, lw=0.9, scale=6)
    ax.text(8.90, 7.28, "速度 v", ha="left", va="center", fontsize=5.6,
            color=ACC)
    ax.add_patch(Arc(P, 2.35, 2.35, angle=0, theta1=-31, theta2=25,
                     ec=MID, lw=0.6))
    ax.text(7.92, 6.12, "θ", fontsize=6.5, color=MID, ha="center",
            va="center")
    ax.text(9.82, 7.92, "判据示意 · 实现未给出（存疑 E1）", fontsize=5.5,
            color=MID, ha="right", va="top")

    # 距离轴与两条判据虚线。
    arrow(ax, (0.72, 1.25), (9.35, 1.25), color=GRAY, lw=0.7, scale=6)
    ax.text(0.72, 0.93, "0", ha="center", va="top", fontsize=5.6)
    ax.text(9.18, 0.93, "30 km", ha="right", va="top", fontsize=5.6)
    x_kill = 0.72 + 8.35 * 0.1 / 30.0
    x_min = 6.15
    ax.plot([x_kill, x_kill], [0.92, 2.35], color=MID, lw=0.65, ls="--")
    ax.plot([x_min, x_min], [0.92, 2.35], color=MID, lw=0.65, ls="--")
    ax.text(0.95, 2.55, "R_kill = 0.1 km", ha="left", va="bottom",
            fontsize=5.4, color=MID)
    ax.text(x_min, 2.55, "d_min", ha="center", va="bottom", fontsize=5.6,
            color=MID)
    ax.text(x_min, 0.28, "最近接近点", ha="center", va="center", fontsize=5.6)
    return fig


# ------------------------------------------------------------ 地空导弹营
def schema_2():
    fig = plt.figure(figsize=(6.1, 2.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.32, 1.0], wspace=0.15,
                          left=0.035, right=0.985, bottom=0.065, top=0.89)

    # a：常态监视、两个分支及弹消失后的回路。
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 9.0)
    ax.axis("off")
    panel_tag(ax, "a")

    rect(ax, 0.20, 4.0, 1.80, 1.0, rounded=True, lw=0.75)
    ax.text(1.10, 4.50, "常态", ha="center", va="center", fontsize=6.2)

    diamond = Polygon([(2.60, 4.50), (4.30, 5.65), (6.00, 4.50),
                       (4.30, 3.35)], closed=True, fc="none", ec=GRAY,
                      lw=0.75, zorder=2)
    ax.add_patch(diamond)
    ax.text(4.30, 4.50, "监控返回\n来袭弹？", ha="center", va="center",
            fontsize=5.7, linespacing=1.3)
    arrow(ax, (2.00, 4.50), (2.60, 4.50), color=GRAY, lw=0.75)

    rect(ax, 7.50, 6.40, 5.75, 1.40, rounded=True, lw=0.75)
    ax.text(10.375, 7.10, "开雷达 + 自由开火 + 停车", ha="center",
            va="center", fontsize=5.8)
    rect(ax, 7.50, 1.00, 5.75, 1.40, rounded=True, lw=0.75)
    ax.text(10.375, 1.70, "关雷达 + 加速跑", ha="center", va="center",
            fontsize=5.9)

    arrow(ax, (5.65, 5.15), (7.50, 6.92), color=MID)
    ax.text(6.40, 6.34, "是", fontsize=5.7, color=MID, ha="center",
            va="bottom")
    arrow(ax, (5.63, 3.83), (7.50, 1.90), color=MID)
    ax.text(6.30, 2.62, "否", fontsize=5.7, color=MID, ha="center",
            va="top")
    arrow(ax, (13.25, 7.10), (13.25, 1.70), color=MID, lw=0.7)
    arrow(ax, (8.40, 1.00), (4.30, 3.35), color=MID, lw=0.7, rad=-0.30)
    ax.text(5.45, 0.42, "弹消失", fontsize=5.6, color=MID, ha="center",
            va="center")

    arrow(ax, (10.38, 6.40), (10.38, 5.55), color=ACC, lw=1.2, scale=6)
    ax.text(10.38, 5.08, "d ≤ 3/5 D_max → 发弹", fontsize=5.8, color=ACC,
            ha="center", va="center")

    # b：按 100.8 与 60.5 的实际比例绘制射程圆。
    ax = fig.add_subplot(gs[0, 1])
    D_MAX = 100.8
    D_FIRE = 60.5
    assert abs(D_FIRE / D_MAX - 0.6) < 0.0002
    ax.set_xlim(-118, 124)
    ax.set_ylim(-118, 124)
    ax.set_aspect("equal")
    ax.axis("off")
    panel_tag(ax, "b")

    ax.add_patch(Circle((0, 0), D_MAX, fill=False, ec=MID, lw=0.75))
    ax.add_patch(Circle((0, 0), D_FIRE, fill=False, ec=ACC, lw=0.9,
                        ls="--"))
    ax.text(0, 105.0, "D_max = 100.8", ha="center", va="bottom",
            fontsize=5.5, color=MID)
    ax.text(0, 64.0, "0.6 D_max = 60.5", ha="center", va="bottom",
            fontsize=5.4, color=ACC)

    ax.plot(0, 0, marker="s", ms=4.4, color=GRAY, zorder=5)
    ax.text(4.0, -8.0, "SAM", fontsize=5.8, ha="left", va="top")

    unit = np.sqrt(0.5)
    p_max = np.array([D_MAX * unit, D_MAX * unit])
    p_fire = np.array([D_FIRE * unit, D_FIRE * unit])
    arrow(ax, (101.0, 101.0), (3.0, 3.0), color=GRAY, lw=0.75, scale=6,
          zorder=3)
    ax.plot(p_fire[0], p_fire[1], marker="*", ms=8.0, color=ACC,
            mec=ACC, zorder=6)
    ax.text(32.0, 33.0, "发弹点", fontsize=5.7, color=ACC, ha="right",
            va="top")
    ax.text(79.0, 63.0, "最大可拦截边界", fontsize=5.3, color=MID,
            ha="left", va="top")

    arrow(ax, (-D_MAX, 0), (-D_FIRE, 0), color=MID, lw=0.65,
          style="<->", scale=6)
    ax.text(-80.6, 7.0, "0.4 D_max\n能量裕度", fontsize=5.4, color=MID,
            ha="center", va="bottom", linespacing=1.35)
    ax.text(116.0, -108.0, "D_max 由模型二分求得，非外部给定",
            fontsize=5.2, color=MID, ha="right", va="bottom")
    return fig


# --------------------------------------------------------------- 船只自卫
def _ship(ax, x, y, label, landing=False):
    if landing:
        rect(ax, x - 0.72, y - 0.20, 1.44, 0.40, ec=GRAY, lw=0.65,
             fc=LIGHT, zorder=4)
        rect(ax, x - 0.18, y + 0.20, 0.48, 0.18, ec=GRAY, lw=0.5,
             fc=LIGHT, zorder=4)
    else:
        hull = Polygon([(x - 0.55, y - 0.16), (x + 0.55, y - 0.16),
                        (x + 0.35, y + 0.18), (x - 0.35, y + 0.18)],
                       closed=True, fc=LIGHT, ec=GRAY, lw=0.65, zorder=4)
        ax.add_patch(hull)
    ax.text(x, y - 0.43, label, fontsize=5.3, ha="center", va="top",
            zorder=5)


def _plane(ax, x, y, s=0.45):
    points = np.array([
        (0.00, 1.00), (0.12, 0.24), (0.72, -0.08), (0.70, -0.23),
        (0.12, -0.08), (0.14, -0.62), (0.34, -0.78), (0.00, -0.70),
        (-0.34, -0.78), (-0.14, -0.62), (-0.12, -0.08),
        (-0.70, -0.23), (-0.72, -0.08), (-0.12, 0.24),
    ]) * s
    ax.add_patch(Polygon(points + (x, y), closed=True, fc=ACC, ec=ACC,
                         lw=0.5, zorder=5))


def schema_5():
    fig = plt.figure(figsize=(6.1, 3.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.0], wspace=0.16,
                          left=0.035, right=0.985, bottom=0.06, top=0.89)

    # a：海域、两类区域、四类来袭航迹及召机驱离。
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")
    panel_tag(ax, "a")

    coast = np.array([(0.10, 8.85), (1.15, 7.85), (0.75, 6.95),
                      (1.70, 6.05), (1.30, 5.15), (2.15, 4.25),
                      (1.75, 3.40), (2.45, 2.40), (1.95, 1.35),
                      (2.55, 0.10)])
    sea = np.vstack([coast, [(12.0, 0.10), (12.0, 8.85)]])
    ax.add_patch(Polygon(sea, closed=True, fc=LIGHT, ec="none", alpha=0.14,
                         zorder=0))
    ax.plot(coast[:, 0], coast[:, 1], color=GRAY, lw=0.6, zorder=2)

    abde = np.array([(2.20, 0.65), (6.35, 0.85), (6.70, 4.90),
                     (2.70, 5.15)])
    c_zone = np.array([(6.95, 0.55), (11.80, 0.75), (11.70, 4.75),
                       (7.00, 5.00)])
    ax.add_patch(Polygon(abde, closed=True, fill=False, ec=MID, lw=0.75,
                         ls="--", zorder=1))
    ax.add_patch(Polygon(c_zone, closed=True, fill=False, ec=ACC, lw=0.8,
                         ls="-.", zorder=1))
    ax.text(2.70, 0.95, "ABDE 区", fontsize=5.8, color=MID, ha="left",
            va="bottom")
    ax.text(11.35, 0.98, "C 区", fontsize=5.8, color=ACC, ha="right",
            va="bottom")

    _ship(ax, 3.65, 2.95, "雷鸣号 1")
    _ship(ax, 5.25, 1.70, "雷鸣号 2")
    _ship(ax, 9.25, 1.80, "23900 舰", landing=True)

    # 两枚指向 ABDE 区，两枚指向 C 区。
    missile_data = [
        ((2.90, 6.55), (3.20, 5.05), "卢卡斯", (2.90, 7.02), GRAY),
        ((5.10, 7.20), (5.00, 5.02), "海马斯", (5.10, 7.68), GRAY),
        ((7.10, 6.80), (7.10, 5.12), "卢卡斯", (6.70, 7.28), GRAY),
        ((11.35, 5.05), (10.72, 3.70), "158C", (11.55, 5.50), ACC),
    ]
    for start, end, label, label_pos, color in missile_data:
        ax.plot(*start, marker="^", ms=4.8, color=color, zorder=5)
        arrow(ax, start, end, color=color, lw=0.7, scale=6, zorder=3)
        ax.text(*label_pos, label, fontsize=5.4, color=color, ha="center",
                va="bottom", zorder=6)

    # 23900 对 C 区卢卡斯的激光处置。
    arrow(ax, (9.25, 2.18), (7.10, 6.62), color=ACC, lw=0.75,
          style="-", scale=6, zorder=2)
    ax.text(8.00, 4.92, "激光束", fontsize=5.2, color=ACC, ha="right",
            va="center", rotation=64)

    # 苏-57 驱离照射机；点线由红色断开符截断。
    _plane(ax, 9.45, 4.05, s=0.46)
    ax.text(9.45, 3.48, "苏-57", fontsize=5.4, color=ACC, ha="center",
            va="top")
    ax.plot(10.65, 8.00, marker="^", ms=5.0, color=MID, zorder=5)
    ax.text(10.65, 8.48, "敌方照射机", fontsize=5.3, color=MID,
            ha="center", va="bottom")
    ax.plot([9.72, 10.50], [4.38, 7.78], color=MID, lw=0.75, ls=":",
            zorder=2)
    ax.plot(10.24, 6.35, marker="x", ms=7.0, mec=ACC, mew=1.3,
            ls="none", zorder=7)
    ax.text(11.72, 6.92, "持续照射", fontsize=5.2, color=MID, ha="right",
            va="center")
    arrow(ax, (9.72, 4.42), (10.38, 7.72), color=ACC, lw=0.9,
          rad=-0.34, scale=6, zorder=4)
    ax.text(8.15, 8.35, "召机驱离照射机", fontsize=5.4, color=ACC,
            ha="center", va="center")

    # b：以矩形与文字手绘三行三列矩阵（表头另占一行）。
    ax = fig.add_subplot(gs[0, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    panel_tag(ax, "b")

    x_edges = [0.15, 2.20, 5.90, 9.85]
    y_edges = [0.30, 2.55, 4.45, 5.95, 6.70]
    # 一类 / C 区单元格的浅红强调。
    ax.add_patch(Rectangle((x_edges[2], y_edges[2]),
                           x_edges[3] - x_edges[2], y_edges[3] - y_edges[2],
                           fc=ACC, ec="none", alpha=0.08, zorder=0))
    rect(ax, x_edges[0], y_edges[0], x_edges[-1] - x_edges[0],
         y_edges[-1] - y_edges[0], ec=GRAY, lw=0.6, zorder=1)
    for xx in x_edges[1:-1]:
        ax.plot([xx, xx], [y_edges[0], y_edges[-1]], color=LIGHT, lw=0.4,
                zorder=1)
    ax.plot([x_edges[0], x_edges[-1]], [y_edges[3], y_edges[3]],
            color=GRAY, lw=0.8, zorder=1)
    for yy in (y_edges[1], y_edges[2]):
        ax.plot([x_edges[0], x_edges[-1]], [yy, yy], color=LIGHT, lw=0.4,
                zorder=1)

    headers = ("区域", "ABDE 处置", "C 处置")
    for j, text in enumerate(headers):
        ax.text((x_edges[j] + x_edges[j + 1]) / 2,
                (y_edges[3] + y_edges[4]) / 2, text, fontsize=5.8,
                fontweight="bold", ha="center", va="center")

    rows = [
        ("一类\n卢卡斯", "雷鸣号\nd<3 km 自卫", "不拦 → 23900\n激光"),
        ("二类\n海马斯 /\n反舰导弹排", "雷鸣号\nD_max 开火",
         "一号 D_max，\n二号 ½D_max 补拦"),
        ("三类\n158C / 154C", "关雷达 + 切向背身\n+ 加力；召苏-57", "同左"),
    ]
    # rows 的顺序与 y_edges 从下到上的存储顺序相反。
    for i, row in enumerate(rows):
        lower, upper = y_edges[3 - i], y_edges[4 - i]
        for j, text in enumerate(row):
            ax.text((x_edges[j] + x_edges[j + 1]) / 2, (lower + upper) / 2,
                    text, fontsize=5.2, ha="center", va="center",
                    linespacing=1.45, zorder=2)
    return fig


def main():
    setup()
    print("生成规则示意图：")
    for fn, name in ((schema_1, "schema-1-monitor"),
                     (schema_2, "schema-2-sam"),
                     (schema_5, "schema-5-ship")):
        save(fn(), name)


if __name__ == "__main__":
    main()
