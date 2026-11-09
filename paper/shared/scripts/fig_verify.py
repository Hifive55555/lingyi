#!/usr/bin/env python
"""
效果验证文档专用插图
====================
fig_verify-timeline  一次推演的态势演化（6 个时刻的事实快照，不做解释性标注）
fig_verify-collab    人机协同的分工与两条操控通道
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)                     # paper/shared
ROOT = os.path.dirname(os.path.dirname(PAPER))    # repo root
FIG = os.path.join(PAPER, "figures")
SRC = os.path.join(ROOT, "work", "lp", "full")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY, MID, LIGHT, ACC, ACC2 = "#1a1a1a", "#6b6b6b", "#c9c9c9", "#b3261e", "#1f4e79"


def setup():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": ["Source Han Sans"], "font.size": 7,
        "svg.fonttype": "path", "pdf.fonttype": 42, "savefig.dpi": 600,
        "axes.spines.right": False, "axes.spines.top": False,
        "text.color": GRAY,
    })


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), bbox_inches="tight",
                    dpi=600 if ext == "png" else None)
    plt.close(fig)
    print(f"  → figures/{name}.svg")


def crop(name, box):
    im = np.asarray(Image.open(os.path.join(SRC, name)).convert("RGB"))
    x0, y0, x1, y1 = box
    return im[y0:y1, x0:x1]


# ---------------------------------------------------------------- 时间线
def verify_timeline():
    shots = [("r_0300.jpg", "00:05"), ("r_0580.jpg", "09:40"),
             ("r_0920.jpg", "15:20"), ("r_1180.jpg", "19:40"),
             ("r_1460.jpg", "24:20"), ("r_1740.jpg", "29:00")]
    fig, axes = plt.subplots(2, 3, figsize=(6.3, 3.05))
    for ax, (f, tc) in zip(axes.ravel(), shots):
        im = np.asarray(Image.open(os.path.join(SRC, f)).convert("RGB"))
        ax.imshow(im)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_linewidth(0.4)
            sp.set_color(MID)
        ax.text(0.02, 0.95, tc, transform=ax.transAxes, fontsize=6.4,
                color="white", va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.22", fc=GRAY, ec="none",
                          alpha=0.75))
    fig.subplots_adjust(wspace=0.05, hspace=0.05)
    save(fig, "fig_verify-timeline")


# ---------------------------------------------------------------- 分工图
def verify_collab():
    fig, ax = plt.subplots(figsize=(6.3, 2.35))
    ax.set_xlim(0, 100)
    ax.set_ylim(-4, 40)
    ax.axis("off")

    def box(x, y, w, h, text, fc="white", ec=GRAY, lw=0.7, fs=6.2, ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                    fc=fc, ec=ec, lw=lw, linestyle=ls, zorder=3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, zorder=4, linespacing=1.35)

    def arrow(p, q, text="", color=MID, ls="-", rad=0.0, dy=1.6):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=6,
                                     lw=0.8, color=color, linestyle=ls,
                                     zorder=2,
                                     connectionstyle=f"arc3,rad={rad}"))
        if text:
            ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, text,
                    fontsize=5.4, color=color, ha="center", va="bottom")

    # 左：操作手
    box(2, 26, 17, 9, "操作手 A\n（红方）", fc="#f4f4f4")
    box(2, 5, 17, 9, "操作手 B\n（蓝方）", fc="#f4f4f4")
    ax.text(10.5, 36.6, "我方 2 人 · 各打一方", fontsize=5.8, color=ACC,
            ha="center")

    # 中：平台
    box(30, 12, 26, 20, "灵弈推演循环\n\n每步：读态势 →\n下发指令 → 推进", fs=6.0)
    arrow((19, 30), (30, 27), "手动操控", color=ACC2)
    arrow((19, 9), (30, 17), "手动操控", color=ACC2)

    # 右：五个智能体（自上而下，与架构图同序）
    names = ["监控", "地空导弹营", "空战躲避", "船只自卫", "打空战"]
    ys = []
    for i, n in enumerate(names):
        y = 30.5 - i * 7.4
        ys.append(y)
        box(66, y, 20, 5.6, n, fs=5.9,
            ec=ACC if n in ("空战躲避", "打空战") else GRAY,
            lw=0.9 if n in ("空战躲避", "打空战") else 0.6)
    # 总线式连接，避免五根箭头挤在一点
    ax.plot([62, 62], [ys[-1] + 2.8, ys[0] + 2.8], color=MID, lw=0.8, zorder=2)
    ax.plot([56, 62], [22, 22], color=MID, lw=0.8, zorder=2)
    for y in ys:
        arrow((62, y + 2.8), (66, y + 2.8), "", color=MID)
    ax.text(58.6, 23.4, "step()", fontsize=5.4, color=MID, ha="center")

    # 底：证据层
    box(30, 1, 26, 6.5, "录屏 / 导出态势", fc="#f4f4f4", ls="--")
    arrow((43, 12), (43, 7.5), "", color=MID, ls="--")
    ax.text(99, -2.2, "红框：代码中确有实现　|　其余：仅规则设计",
            fontsize=5.3, color=ACC, va="top", ha="right")

    ax.text(50, 39.4, "两条通道：操作手手动下指令，智能体在 step() 中下指令；"
            "两者在界面上不可区分",
            fontsize=5.6, color=MID, ha="center")
    save(fig, "fig_verify-collab")


def main():
    setup()
    print("生成效果验证插图：")
    for fn in (verify_timeline, verify_collab):
        try:
            fn()
        except Exception as e:
            print(f"  ! {fn.__name__} 失败: {e}")


if __name__ == "__main__":
    main()
