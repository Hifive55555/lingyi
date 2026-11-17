#!/usr/bin/env python
"""
图 1 架构图（独立脚本）
======================
figures.py 里的其余图与本文件互不影响；本文件只输出 figures/fig1-architecture.*。

图契约
  核心结论：五个智能体不是并列关系，而是"一个共享观测底座 + 四个互不相交的
            决策域"；能量阈值 500 km/h 是跨域公共判据。
  面板 a：数据流与决策域划分（层次：观测 → 底座 → 四域 → 动作）
  面板 b：单体决策状态机（以空战单元自卫为例）
"""
import math
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
FIG = os.path.join(PAPER, "figures")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY = "#1a1a1a"
MID = "#6b6b6b"
LIGHT = "#c9c9c9"
ACC = "#b3261e"


def setup():
    if os.path.exists(CJK):
        mpl.font_manager.fontManager.addfont(CJK)
        mpl.rcParams["font.family"] = ["Source Han Sans"]
    mpl.rcParams.update({
        "font.size": 7, "axes.linewidth": 0.6,
        "axes.spines.right": False, "axes.spines.top": False,
        "axes.edgecolor": GRAY, "axes.labelcolor": GRAY,
        "xtick.color": GRAY, "ytick.color": GRAY, "text.color": GRAY,
        "legend.frameon": False, "legend.fontsize": 6.4,
        "svg.fonttype": "path", "pdf.fonttype": 42,
        "axes.titlesize": 8, "axes.labelsize": 7,
        "xtick.labelsize": 6.4, "ytick.labelsize": 6.4,
        "lines.linewidth": 1.0, "savefig.dpi": 600,
    })


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"),
                    bbox_inches="tight", dpi=600 if ext == "png" else None)
    plt.close(fig)
    print(f"  -> figures/{name}.svg")


def panel_tag(ax, s, dx=-0.02, dy=1.02):
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="bottom", ha="left", color="#000")


# ---------------------------------------------------------------- F1
def fig1():
    fig = plt.figure(figsize=(6.1, 2.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1], wspace=0.12,
                          left=0.025, right=0.995, bottom=0.04, top=0.94)

    # --- F1a 数据流与决策域：四条水平泳道
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis("off")
    panel_tag(ax, "a", dx=-0.02, dy=1.02)

    lanes = [
        (9.35, 1.35, "观测"),
        (7.75, 1.35, "底座"),
        (2.35, 5.15, "决策域"),
        (0.95, 1.15, "动作"),
    ]
    for y, h, label in lanes:
        ax.add_patch(plt.Rectangle((0, y), 12, h, fc="#f7f7f7", ec="none",
                                   zorder=0))
        ax.text(0.28, y + h / 2, label, rotation=90, ha="center", va="center",
                fontsize=5.5, color=MID, zorder=3)

    def box(x, y, w, h, text, fc="white", ec=GRAY, lw=0.7, fs=5.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                    fc=fc, ec=ec, lw=lw, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, zorder=3, linespacing=1.2)

    def arrow(x1, y1, x2, y2, color=MID):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=6, lw=0.7, color=color,
                                     zorder=1, connectionstyle="arc3,rad=0.0"))

    box(0.85, 9.52, 3.15, 1.0, "战场态势\n（平台只读观测）")
    box(0.85, 7.93, 3.15, 1.0, "物理作战域三维监控\n输出：弹型 + 弹速", ec=ACC, lw=1.1,
        fs=5.2)
    arrow(2.425, 9.52, 2.425, 8.99)
    ax.text(8.1, 8.43, "唯一公共信息底座", fontsize=5.8, color=MID,
            ha="center", va="center")

    # 物理作战域三维监控右侧引出一条竖直总线，四条等长水平支线分别进入各决策域。
    bus_x = 4.60
    domain_x, domain_w, domain_h = 5.10, 3.45, 0.92
    domain_centers = [6.65, 5.45, 4.25, 3.05]
    ax.plot([4.0, bus_x, bus_x], [8.43, 8.43, domain_centers[-1]],
            color=MID, lw=0.7, zorder=1)
    domain_texts = [
        ("空战单元自卫\n（飞机）", 5.6),
        ("空空作战\n（战斗机）", 5.6),
        ("地空导弹营攻击与自卫\n（防空单元）", 4.8),
        ("登陆船只集群自卫\n（雷鸣号 / 23900）", 5.2),
    ]
    for yc, (text, fs) in zip(domain_centers, domain_texts):
        arrow(bus_x, yc, domain_x, yc)
        box(domain_x, yc - domain_h / 2, domain_w, domain_h, text, fs=fs)

    ax.text(10.15, 4.85, "四域互不相交\n彼此无直接耦合\n仅共享弹型 + 弹速",
            fontsize=5.8, color=MID, ha="center", va="center",
            linespacing=1.45)
    box(0.85, 1.12, 10.85, 0.75,
        "各域独立输出动作：关雷达 · 掉头 · 开火 · 召机", fs=5.8)

    # 跨域判据使用贯穿面板底部的浅灰注记带。
    ax.add_patch(FancyBboxPatch((0, 0.08), 12, 0.62,
                                boxstyle="round,pad=0.02", fc="#f7f7f7",
                                ec="none", zorder=0))
    ax.text(6, 0.39, "能量阈值 500 km/h 为跨域公共判据",
            fontsize=5.8, color=MID, ha="center", va="center")

    # --- F1b 状态机
    ax = fig.add_subplot(gs[0, 1])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    panel_tag(ax, "b", dx=-0.02, dy=1.02)

    nodes = [(1.8, 7.2, "巡航"),
             (4.9, 7.2, "迎头\n接近"),
             (7.8, 4.25, "尾追\n逃逸"),
             (4.9, 1.3, "垂直\n扭动"),
             (1.8, 1.3, "反打")]
    terminal = (8.0, 1.3, "被击落")
    node_w, node_h = 2.1, 1.25
    for x, y, text in nodes:
        ax.add_patch(FancyBboxPatch(
            (x - node_w / 2, y - node_h / 2), node_w, node_h,
            boxstyle="round,pad=0.08,rounding_size=0.18",
            fc="white", ec=GRAY, lw=0.7, zorder=2))
        ax.text(x, y, text, ha="center", va="center", fontsize=5.8,
                zorder=3, linespacing=1.2)
    ax.add_patch(FancyBboxPatch(
        (terminal[0] - node_w / 2, terminal[1] - node_h / 2), node_w, node_h,
        boxstyle="round,pad=0.08,rounding_size=0.18",
        fc="#f7f7f7", ec=MID, lw=0.7, zorder=2))
    ax.text(terminal[0], terminal[1], terminal[2], ha="center", va="center",
            fontsize=5.8, color=MID, zorder=3)

    def boundary(index, toward):
        x, y, _ = nodes[index]
        tx, ty, _ = nodes[toward]
        dx, dy = tx - x, ty - y
        scale = min((node_w / 2) / abs(dx) if dx else math.inf,
                    (node_h / 2) / abs(dy) if dy else math.inf)
        return x + scale * dx, y + scale * dy

    def edge(a, b, color=MID):
        ax.add_patch(FancyArrowPatch(boundary(a, b), boundary(b, a),
                                     arrowstyle="-|>", mutation_scale=6,
                                     lw=0.7, color=color, zorder=1,
                                     shrinkA=1, shrinkB=1,
                                     connectionstyle="arc3,rad=0.0"))

    def edge_label(x, y, text, color=MID, rotation=0):
        ax.text(x, y, text, fontsize=5.5, color=color, ha="center", va="center",
                linespacing=1.25, rotation=rotation, zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.8))

    edge(0, 1)
    edge_label(3.35, 7.9, "发现来袭弹")
    edge(1, 2)
    edge_label(7.75, 6.3, "d ≤ d_turn(V弹)")
    edge(2, 3, color=ACC)
    ax.annotate("d ≤ 20 km\n且 V弹 > V我", xy=(6.55, 2.92),
                xytext=(8.05, 3.0), fontsize=5.5, color=ACC,
                ha="center", va="center", linespacing=1.25, zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.8),
                arrowprops=dict(arrowstyle="-", color=ACC, lw=0.6,
                                shrinkA=2, shrinkB=2))
    edge(3, 4, color=ACC)
    edge_label(3.35, 0.45, "V弹 < 500", color=ACC)

    # 不规避直接进入终端；虚线沿右侧布设，避免与规避路径交叉。
    ax.plot([5.95, 9.55, 9.55], [7.2, 7.2, 1.3],
            color=MID, lw=0.7, ls="--", zorder=1)
    ax.add_patch(FancyArrowPatch((9.55, 1.3), (9.05, 1.3),
                                 arrowstyle="-|>", mutation_scale=6,
                                 lw=0.7, color=MID, ls="--", zorder=1))
    edge_label(9.12, 4.9, "始终不规避", rotation=90)

    # 反打后再次接敌：实线回路从左侧返回迎头接近。
    ax.plot([0.75, 0.25, 0.25, 4.9], [1.3, 1.3, 9.25, 9.25],
            color=MID, lw=0.7, zorder=1)
    ax.add_patch(FancyArrowPatch((4.9, 9.25), (4.9, 7.825),
                                 arrowstyle="-|>", mutation_scale=6,
                                 lw=0.7, color=MID, zorder=1))
    edge_label(0.62, 4.7, "再次接敌", rotation=90)
    return fig




def main():
    setup()
    print("生成架构图：")
    save(fig1(), "fig1-architecture")


if __name__ == "__main__":
    main()
