#!/usr/bin/env python
"""红方任务—单元分配图（**已撤稿，未进正文**）。

这张图最后被删掉了，原因是它不承担论证：它把表 6 / 表 7 已有的"每条任务分几个
执行单元"重画了一遍，而全文没有任何一条结论依赖这个分布（唯一被引用的
"制空 7 个、保船与北制空各 6 个"已并进表 7 的题注）。脚本留在这里只为记录
这份逐任务的单元数口径（可与 `SUPPORT_TASKS` / `PATROL_TASKS` 直接核对）。

以下是当时第三版的画法说明：红方任务—单元分配图（itemized 堆叠条）。

画法：一个任务组一根水平条，条里的每一段就是一条任务的执行单元数，段的宽度 = 该任务
分到的单元数，段与段之间留白分隔；条长 = 该组的合计单元数，条尾标一个数字。
这样一根条同时编码了三件事：这组有几条任务（段数）、每条摊几个单元（段宽）、
这组合计多少单元（条长）。支援组是一串窄段（一机一条航线），巡逻组是几段宽的加一串窄段
（少数几条撑起责任区）——两种用兵形态的差别一眼可见，且不需要读任何表格。

数据源：`最新报告/红方代码/Mission_all_red.py` 的 SUPPORT_TASKS / PATROL_TASKS，
与论文 @tab:mission-full-red、@tab:patrol-full-red 逐条同源：
支援 22 条 / 33 个单元，巡逻 16 条 / 53 个单元。
输出：paper/shared/figures/fig_task_alloc.{png,svg}
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
FIG = os.path.join(PAPER, "figures")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
INK = "#22252b"
MUTED = "#6b7378"
GRID = "#e4e7ea"
BLUE = "#3d6fb0"    # 支援任务
BLUE_L = "#6b93c8"
GREEN = "#3f8a5f"   # 巡逻任务
GREEN_L = "#72ad8b"

SUPPORT = [
    ("西段拦截", [("左阵风5", 4), ("左75-2", 1), ("左35-2", 1), ("左阵风1", 1),
                  ("左阵风2", 1), ("左阵风3", 1), ("左阵风4", 1), ("左阵风6", 1)]),
    ("中段支援", [("苏27-1", 2), ("轰炸机", 2), ("苏24下", 1), ("伊尔22", 1)]),
    ("东北方向", [("北35-1", 1), ("北35-2", 1), ("北阵风-1", 0), ("北阵风-2", 0)]),
    ("登陆编队", [("E", 4), ("C1", 3), ("D", 3), ("A", 2), ("B", 2), ("C2", 0)]),
]
PATROL = [
    ("反地面战", [("TB1", 4), ("TB2", 4), ("TB3", 4), ("阵风2", 3), ("阵风3", 3),
                  ("神经元3", 2), ("阵风1", 1), ("神经元1", 1), ("神经元2", 1)]),
    ("防空压制", [("S70-1", 3), ("S70-2", 3)]),
    ("制空 / 保船", [("右制空", 7), ("中间保船", 6), ("北制空", 6), ("左制空", 3)]),
    ("反潜", [("反潜巡逻", 2)]),
]

XMAX = 24.0
BAR_H = 0.58
SEG_GAP = 0.16


def draw_block(ax, groups, color, light, y0, title):
    """一个任务块：组标题 + 每个组一根 itemized 条。返回下一个可用的 y。"""
    ax.text(-0.6, y0, title, ha="left", va="center", fontsize=7.6,
            color=INK, fontweight="bold", clip_on=False)
    ax.plot([-0.6, XMAX], [y0 + 0.62, y0 + 0.62], color=GRID, lw=0.8, clip_on=False,
            zorder=1)
    y = y0 + 1.5
    for gi, (name, tasks) in enumerate(groups):
        ax.text(-1.0, y, name, ha="right", va="center", fontsize=7.2,
                color=INK, clip_on=False)
        x = 0.0
        segs = [(n, k) for n, k in tasks if k > 0]
        for si, (tn, k) in enumerate(segs):
            w = k - SEG_GAP
            ax.add_patch(Rectangle((x, y - BAR_H / 2), w, BAR_H,
                                   facecolor=color if si % 2 == 0 else light,
                                   edgecolor="white", lw=0.5, zorder=3))
            x += k
        tot = sum(k for _, k in tasks)
        ax.text(tot + 0.45, y, f"{tot}", ha="left", va="center", fontsize=7.0,
                color=INK, fontweight="bold", clip_on=False)
        empties = [n for n, k in tasks if k == 0]
        if empties:
            for ei, _ in enumerate(empties):
                ax.add_patch(Rectangle((-0.95 + ei * 0.52, y - BAR_H / 2),
                                       0.40, BAR_H, facecolor="white",
                                       edgecolor=color, lw=0.8, lw_joinstyle="miter", zorder=3))
        y += 1.0
    return y


def main():
    if os.path.exists(CJK):
        font_manager.fontManager.addfont(CJK)
        family = font_manager.FontProperties(fname=CJK).get_name()
    else:
        family = "Noto Sans CJK SC"
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [family, "Noto Sans CJK SC", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "svg.fonttype": "path",
        "figure.dpi": 300,
    })

    fig, ax = plt.subplots(figsize=(6.0, 2.95))
    fig.subplots_adjust(left=0.185, right=0.975, top=0.90, bottom=0.135)

    y = draw_block(ax, SUPPORT, BLUE, BLUE_L, 0.0,
                   "支援任务　22 条 / 33 个单元 · 平均每条 1.5 个单元")
    draw_block(ax, PATROL, GREEN, GREEN_L, y + 0.55,
               "巡逻任务　16 条 / 53 个单元 · 平均每条 3.3 个单元")

    ax.set_xlim(-1.1, XMAX + 1.4)
    ax.set_ylim(y + 4.3, -1.0)
    ax.set_yticks([])
    ax.set_xticks(range(0, 25, 4))
    ax.tick_params(axis="x", labelsize=7.0, colors=MUTED, length=2.0, pad=2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel("执行单元数（一个色段 = 一条任务，段宽 = 该任务分到的单元数）",
                  fontsize=6.9, color=MUTED, labelpad=3)

    out_png = os.path.join(FIG, "fig_task_alloc.png")
    out_svg = os.path.join(FIG, "fig_task_alloc.svg")
    fig.savefig(out_png, dpi=300)
    fig.savefig(out_svg)
    print("→", out_png, "\n→", out_svg)


if __name__ == "__main__":
    main()
