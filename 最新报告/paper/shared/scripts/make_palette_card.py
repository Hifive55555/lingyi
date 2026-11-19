#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成配色样张（给作者/审阅者看的一套色）。

输出：最新报告/paper/shared/style/palette.png
"""
import os
import sys

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as F  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "style"))


CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")


def main():
    from matplotlib import font_manager
    if os.path.exists(CJK):
        font_manager.fontManager.addfont(CJK)
        fam = font_manager.FontProperties(fname=CJK).get_name()
        mpl.rcParams["font.family"] = ["sans-serif"]
        mpl.rcParams["font.sans-serif"] = [fam, "Noto Sans CJK SC"]
    F.apply(base_size=8)
    os.makedirs(OUT, exist_ok=True)
    fig = plt.figure(figsize=(7.2, 4.9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)

    ax.text(4, 66, "报告统一配色 v2 ｜ 主体色：靛蓝", fontsize=13, weight="bold", color=F.INK)
    ax.text(4, 62.2, "靛蓝打底（结构/平台/默认系列），朱砂只标论点（我方规则/阈值），青与砂金作第三、四类；顺序变量走单色梯度。",
            fontsize=8, color=F.MID)

    # 语义六族
    ax.text(4, 57.0, "五个色族（fill 浅底 ／ line 主色 ／ deep 深色）",
            fontsize=9, weight="bold", color=F.INK)
    y = 51
    for name, fam in F.FAMILY.items():
        ax.text(4, y + 1.1, f"{name}", fontsize=8, color=F.INK, ha="left")
        x = 15
        for k in ("fill", "line", "deep"):
            ax.add_patch(Rectangle((x, y), 13, 4.4, facecolor=fam[k],
                                   edgecolor=F.LIGHT, linewidth=0.6))
            ax.text(x + 6.5, y + 1.6, fam[k], fontsize=6.4, ha="center",
                    color=F.WHITE if k == "deep" else F.INK)
            x += 13.6
        y -= 6.2

    # 中性
    ax.text(62, 57.0, "中性阶（文字／轴线／网格／底板）", fontsize=9,
            weight="bold", color=F.INK)
    yy = 51
    for nm in ("ink", "mid", "soft", "light", "grid", "panel"):
        c = getattr(F, nm.upper())
        ax.add_patch(Rectangle((62, yy), 9, 4.4, facecolor=c,
                               edgecolor=F.LIGHT, linewidth=0.6))
        ax.text(72.2, yy + 2.2, f"{nm}  {c}", fontsize=6.6, va="center", color=F.INK)
        yy -= 6.2

    ax.text(62, 16.0, "并列类别（分类色序）", fontsize=8, color=F.INK)
    x = 62
    for c in F.CATEGORICAL:
        ax.add_patch(Rectangle((x, 11.6), 4.2, 3.2, facecolor=c, edgecolor="none"))
        x += 4.5
    ax.text(62, 8.0, "顺序变量（单色梯度）", fontsize=8, color=F.INK)
    x = 62
    for c in F.SEQ:
        ax.add_patch(Rectangle((x, 3.8), 6.0, 3.2, facecolor=c, edgecolor="none"))
        x += 6.4
    ax.text(12.5, 4.6, "顺序变量（同一参数的若干取值）→ 单色梯度；\n"
                       "不同对象（我方/对手/基线）→ 不同色相。",
            fontsize=7.4, color=F.MID)

    p = os.path.join(OUT, "palette.png")
    fig.savefig(p, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    print("→", p)


if __name__ == "__main__":
    main()
