#!/usr/bin/env python
"""
实战素材图（录屏截图 + 标注）
=============================
素材来自 4 段比赛录屏（2560×1600）。本脚本只做**裁剪、缩放、标注**，不改动内容，
不臆造画面里没有的元素。每张图的标注都指向画面上真实存在的对象。

fig_evidence-1  实战态势总览：责任区 / 巡逻区 / 登陆区 / 地空导弹营 / 红蓝单位
fig_evidence-2  三处可核对细节：(a) 地空导弹营单元 (b) 巡逻区与责任区边界 (c) 交战时机群

输出：paper/figures/fig_evidence-*.png（照片底图，故只出位图 300 dpi）
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PAPER))
FIG = os.path.join(PAPER, "figures")
SRC = os.path.join(ROOT, "work", "lp", "full")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY = "#1a1a1a"
ACC = "#ff2d2d"
WHT = "#ffffff"


def setup():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": ["Source Han Sans"],
        "svg.fonttype": "path", "pdf.fonttype": 42, "savefig.dpi": 300,
        "font.size": 7,
    })


def load(name):
    return np.asarray(Image.open(os.path.join(SRC, name)).convert("RGB"))


def crop(im, box):
    x0, y0, x1, y1 = box
    return im[y0:y1, x0:x1]


def callout(ax, xy, xytext, text, fs=7.2, color=ACC):
    """带引线 + 白底的标注框"""
    ax.annotate(
        text, xy=xy, xytext=xytext, fontsize=fs, color=WHT,
        ha="left", va="center", zorder=20,
        bbox=dict(boxstyle="round,pad=0.32", fc=color, ec="none", alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                        shrinkA=2, shrinkB=2,
                        connectionstyle="arc3,rad=0.12"),
    )


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    p = os.path.join(FIG, f"{name}.png")
    fig.savefig(p, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"  → figures/{name}.png")


# ---------------------------------------------------------------- 图 1
def evidence1():
    im = load("r_1460.jpg")          # 14:40 附近，交战最密集的一帧
    H, W = im.shape[:2]
    fig, ax = plt.subplots(figsize=(6.3, 3.94))
    ax.imshow(im, extent=(0, W, H, 0))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    def tag(xy, xytext, text, fs=6.6):
        ax.annotate(
            text, xy=xy, xytext=xytext, fontsize=fs, color=WHT,
            ha="left", va="center", zorder=20,
            bbox=dict(boxstyle="round,pad=0.30", fc=ACC, ec="none", alpha=0.93),
            arrowprops=dict(arrowstyle="-|>", color=ACC, lw=1.2,
                            shrinkA=1, shrinkB=3,
                            connectionstyle="arc3,rad=0.10"),
        )

    # ① 登陆区
    tag((1150, 700), (430, 640), "① 登陆区（登剑海滩登陆）")
    # ② 巡逻区
    tag((1745, 700), (1830, 610), "② 巡逻区\n（阵风 2，另有 TB1/2/3、\nS70-1/2、左制空）")
    # ③ 责任区边界
    tag((640, 905), (300, 1000), "③ 责任区边界\n（端点标 BP-T71xx）")
    # ④ 地空导弹营
    tag((1500, 430), (1560, 300), "④ 地空导弹营（霍克导弹 [P3, TAS]）#31")
    # ⑤ 红蓝单位
    tag((1290, 950), (700, 1240), "⑤ 红=本方 / 蓝=对方，细线为历史航迹")

    ax.text(W - 20, H - 14,
            "客户端全屏录屏 2560×1600｜选手 1 红方视角 14:40",
            fontsize=5.4, color=WHT, ha="right", va="bottom", alpha=0.85)
    save(fig, "fig_evidence-1")


# ---------------------------------------------------------------- 图 2
def evidence2():
    fig = plt.figure(figsize=(6.3, 1.62))
    gs = fig.add_gridspec(1, 3, wspace=0.05, width_ratios=[1.45, 1, 1.15])

    specs = [
        ("r_1460.jpg", (1280, 290, 2080, 530), "a　地空导弹营单元",
         "标签：地空导弹营（霍克 [P3,TAS]）#31"),
        ("r_1460.jpg", (1350, 600, 1900, 830), "b　巡逻区与责任区边界", None),
        ("r_0920.jpg", (200, 620, 1000, 1060), "c　舰群航迹与瞄准标记", None),
    ]
    for i, (src, box, title, note) in enumerate(specs):
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(crop(load(src), box))
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_linewidth(0.5)
            sp.set_color(GRAY)
        ax.set_title(title, fontsize=6.8, pad=2.5, loc="left")
        if note:
            ax.text(0.015, -0.055, note, transform=ax.transAxes,
                    fontsize=5.2, color=GRAY, va="top", ha="left")
    save(fig, "fig_evidence-2")


def main():
    setup()
    print("生成实战素材图：")
    for fn in (evidence1, evidence2):
        try:
            fn()
        except Exception as e:
            print(f"  ! {fn.__name__} 失败: {e}")


if __name__ == "__main__":
    main()
