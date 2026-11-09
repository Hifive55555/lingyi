#!/usr/bin/env python
"""
逐智能体的实机应用截图（带 2–3 处标注）
=======================================
fig_apply-ship       舰艇编队与登陆区（船只自卫）
fig_apply-aircombat  机群与瞄准标记（空空交战）
fig_apply-sam        地空导弹营单元（地空导弹营）
fig_apply-airspace   巡逻区与制空责任区（空战躲避的作战空域）
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PAPER))
FIG = os.path.join(PAPER, "figures")
SRC = os.path.join(ROOT, "work", "lp", "full")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY, MID, ACC = "#1a1a1a", "#6b6b6b", "#ff2d2d"
WHT = "#ffffff"


def setup():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({"font.family": ["Source Han Sans"], "font.size": 7,
                         "savefig.dpi": 300, "svg.fonttype": "path"})


def load(n):
    return np.asarray(Image.open(os.path.join(SRC, n)).convert("RGB"))


def panel(im, box, tags, out, figsize=(6.3, 1.95)):
    x0, y0, x1, y1 = box
    c = im[y0:y1, x0:x1]
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(c)
    ax.axis("off")
    for xy, xytext, text in tags:
        ax.annotate(text, xy=(xy[0] - x0, xy[1] - y0),
                    xytext=(xytext[0] - x0, xytext[1] - y0),
                    fontsize=6.2, color=WHT, ha="left", va="center", zorder=20,
                    bbox=dict(boxstyle="round,pad=0.30", fc=ACC, ec="none",
                              alpha=0.92),
                    arrowprops=dict(arrowstyle="-|>", color=ACC, lw=1.1,
                                    shrinkA=1, shrinkB=3,
                                    connectionstyle="arc3,rad=0.10"))
    for ext in ("svg", "pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{out}.{ext}"), bbox_inches="tight",
                    dpi=600 if ext == "png" else None)
    plt.close(fig)
    print(f"  → figures/{out}.svg")


def main():
    setup()
    print("生成实机应用截图：")
    im1460 = load("r_1460.jpg")
    im0920 = load("r_0920.jpg")

    panel(im0920, (150, 600, 950, 1055),
          [((480, 830), (200, 660), "登陆区与舰艇编队"),
           ((300, 760), (170, 980), "舰位与历史航迹"),
           ((700, 800), (560, 1010), "责任区边界（BP-T71xx）")],
          "fig_apply-ship", figsize=(6.3, 2.0))

    panel(im1460, (900, 620, 1560, 1060),
          [((1120, 860), (930, 660), "机群与瞄准十字"),
           ((1430, 900), (1290, 690), "航迹折转")],
          "fig_apply-aircombat", figsize=(6.3, 2.15))

    panel(im1460, (1320, 290, 1960, 560),
          [((1712, 470), (1440, 545), "地空导弹营单元（霍克导弹 [P3, TAS] #31）"),
           ((1500, 335), (1690, 315), "来袭目标")],
          "fig_apply-sam", figsize=(6.3, 1.6))

    panel(im1460, (1080, 560, 1900, 900),
          [((1520, 700), (1160, 800), "阵风 2 巡逻区"),
           ((1300, 760), (1150, 620), "制空责任区"),
           ((1780, 700), (1800, 830), "TB3 巡逻区")],
          "fig_apply-airspace", figsize=(6.3, 2.1))


if __name__ == "__main__":
    main()
