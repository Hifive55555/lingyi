#!/usr/bin/env python
"""红方任务总图：把 SUPPORT_TASKS / PATROL_TASKS 的参考点画成一张全局图。

数据源（与报告表 8、表 9 同源）：新增态势图和红方任务列表更新/Mission_all_red.py
输出：paper/shared/figures/fig_tasks-overview.png
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Polygon, Patch
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
FIG = os.path.join(PAPER, "figures")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
INK = "#22252b"
GRID = "#d9dce1"

# 支援任务：(任务名, 起点, 终点, 组)
SUPPORT = [
    ("左75-2", (50.121, -4.997), (49.725, -6.551), "西段拦截"),
    ("左35-2", (49.700, -4.700), (49.125, -6.151), "西段拦截"),
    ("左阵风1", (47.762, -6.389), (48.241, -7.546), "西段拦截"),
    ("左阵风2", (47.412, -6.467), (47.532, -7.959), "西段拦截"),
    ("左阵风3", (47.057, -6.566), (46.945, -7.903), "西段拦截"),
    ("左阵风4", (46.803, -6.496), (46.274, -7.503), "西段拦截"),
    ("左阵风5", (46.687, -5.712), (44.982, -4.716), "西段拦截"),
    ("左阵风6", (46.934, -5.339), (46.367, -2.652), "西段拦截"),
    ("苏27-1", (49.971, -1.484), (49.417, -1.993), "中段支援"),
    ("苏24下", (50.491, -1.297), (50.568, -1.106), "中段支援"),
    ("伊尔22", (51.899, -0.405), (52.097, 0.301), "中段支援"),
    ("轰炸机", (52.118, -1.755), (51.920, -1.687), "中段支援"),
    ("北35-1", (52.561, 1.545), (52.804, 4.193), "东北方向"),
    ("北35-2", (52.788, 1.551), (53.305, 3.445), "东北方向"),
    ("北阵风-1", (51.970, 1.613), (52.416, 3.421), "东北方向"),
    ("北阵风-2", (51.688, 2.640), (52.171, 4.702), "东北方向"),
    ("A", (49.165, -2.531), (49.171, -2.462), "登陆编队"),
    ("B", (49.678, -1.022), (49.625, -0.981), "登陆编队"),
    ("C1", (50.085, -0.857), (49.678, -1.022), "登陆编队"),
    ("C2", (49.692, -0.130), (49.609, -0.085), "登陆编队"),
    ("D", (50.436, 0.398), (50.198, 0.962), "登陆编队"),
    ("E", (51.355, 1.938), (51.285, 2.027), "登陆编队"),
]

# 巡逻任务：(任务名, 四点, 类型)
PATROL = [
    ("神经元1", ((49.254, -2.245), (49.154, -2.235), (49.146, -1.969), (49.264, -1.985)), "反地面战"),
    ("神经元2", ((49.391, -1.047), (49.213, -1.060), (49.175, -0.865), (49.376, -0.790)), "反地面战"),
    ("神经元3", ((49.344, -0.812), (49.192, -0.812), (49.192, -0.539), (49.344, -0.539)), "反地面战"),
    ("TB1", ((49.475, -1.511), (49.304, -1.511), (49.304, -1.249), (49.475, -1.249)), "反地面战"),
    ("TB2", ((49.335, -0.230), (49.172, -0.221), (49.172, 0.079), (49.355, 0.052)), "反地面战"),
    ("阵风1", ((49.692, 0.135), (49.444, 0.135), (49.444, 0.566), (49.692, 0.566)), "反地面战"),
    ("阵风2", ((49.887, 0.868), (49.263, 1.320), (50.236, 2.340), (50.421, 1.610)), "反地面战"),
    ("TB3", ((49.856, 1.404), (49.650, 1.404), (49.650, 1.717), (49.856, 1.717)), "反地面战"),
    ("阵风3", ((51.015, 2.170), (51.339, 3.220), (50.923, 3.330), (50.637, 2.224)), "反地面战"),
    ("S70-1", ((49.310, -2.354), (48.435, -1.721), (48.256, -0.058), (49.433, -0.403)), "防空压制"),
    ("S70-2", ((49.164, -0.091), (48.210, 0.004), (48.607, 2.441), (49.310, 1.625)), "防空压制"),
    ("中间保船", ((49.569, -1.297), (49.491, -1.364), (49.418, -0.672), (49.562, -0.739)), "防空/制空"),
    ("左制空", ((49.765, -2.429), (48.657, -3.290), (47.939, -0.314), (49.825, -0.609)), "防空/制空"),
    ("右制空", ((49.908, -0.446), (47.968, 0.011), (48.713, 2.897), (49.838, 0.703)), "防空/制空"),
    ("北制空", ((53.345, 2.489), (52.491, 2.130), (51.916, 5.827), (52.574, 6.018)), "防空/制空"),
    ("反潜巡逻", ((48.521, -7.537), (48.521, -6.437), (47.730, -6.437), (47.730, -7.537)), "反潜"),
]

SMALL_ZONES = {"神经元1", "神经元2", "神经元3", "TB1", "TB2",
               "阵风1", "阵风2", "中间保船"}

LANDING = [("泽西", (49.165, -2.531)), ("犹他", (49.678, -1.022)),
           ("宝剑", (49.692, -0.130)), ("皮伊", (50.436, 0.398)),
           ("马洛", (51.355, 1.938))]
# 五个区名的落点（lon, lat）：滩头一线太挤，自动避让也排不开，直接手动钉住
LANDING_POS = {"泽西": (-2.95, 48.98), "犹他": (-1.72, 49.16),
               "宝剑": (0.32, 49.10), "皮伊": (0.92, 50.10),
               "马洛": (2.38, 51.12)}

COL_SUP = {"西段拦截": "#1a5fb4", "中段支援": "#8a5a00",
           "东北方向": "#7b3fa0", "登陆编队": "#e01b24"}
PAT_EDGE = "#3b3f78"                    # 巡逻区统一边色，靠虚线样式分型
# 四种巡逻类型用四种虚线节奏：同一支笔画的，灰阶打印也能分开。
PAT_DASH = {"反地面战": (0, (3.2, 1.8)),      # 短虚
            "防空压制": (0, (7.0, 2.2)),      # 长虚
            "防空/制空": (0, (1.2, 1.6)),     # 密点
            "反潜": (0, (6.0, 1.6, 1.4, 1.6))}  # 点划线
# 淡填充：只给一点点底色，让虚拟多边形"有面积"，重叠处自然加深；
# 太深会盖住航线与标签，太浅又等于没填，0.05–0.09 之间是实测可辨的上限。
PAT_FILL = {"反地面战": 0.045, "防空压制": 0.065,
            "防空/制空": 0.058, "反潜": 0.090}

# 支援任务标签位置修正（dx, dy, ha），只写需要挪的
SUP_OFF = {
    "左阵风1": (0.25, -0.30, "left"), "左阵风2": (-0.30, 0.00, "right"),
    "左阵风3": (0.25, 0.00, "left"), "左阵风4": (0.25, -0.15, "left"),
    "苏27-1": (0.15, 0.10, "left"), "苏24下": (0.12, 0.06, "left"),
    "伊尔22": (0.15, 0.05, "left"), "轰炸机": (-0.10, 0.22, "right"),
    "北35-1": (0.10, -0.12, "left"), "北35-2": (0.10, 0.10, "left"),
    "北阵风-1": (0.10, -0.28, "left"), "北阵风-2": (0.10, 0.10, "left"),
    "A": (-0.12, 0.14, "right"), "B": (0.10, 0.12, "left"),
    "C1": (-0.12, 0.14, "right"), "C2": (0.12, -0.10, "left"),
    "D": (0.12, 0.10, "left"), "E": (0.12, 0.10, "left"),
    "左75-2": (0.10, 0.10, "left"), "左35-2": (-0.10, 0.12, "right"),
    "左阵风5": (0.12, -0.05, "left"), "左阵风6": (0.12, 0.08, "left"),
}
PAT_OFF = {"神经元1": (0.0, -0.12), "TB1": (-0.25, -0.15), "TB2": (0.15, -0.20),
           "阵风1": (0.0, -0.12), "阵风2": (0.20, -0.10), "TB3": (0.02, 0.02),
           "S70-1": (0.30, -0.42), "S70-2": (0.10, -0.30),
           "中间保船": (-0.05, -0.20), "左制空": (-0.35, -0.55),
           "右制空": (0.55, -0.65),
           "反潜巡逻": (0.60, 0.60), "阵风3": (0.22, -0.14), "北制空": (0.95, -0.30),
           "神经元2": (0.05, 0.16), "神经元3": (0.05, 0.16)}



LON_DEG = 68.0        # 在 49.5°N，1° 经度约 72 km，图上按显示比例折算
LAT_DEG = 110.0


IN_PER_DEG_X = 6.35 * 0.926 / (6.45 - (-8.5))     # 画布宽 × 轴占比 ÷ 经度跨度
IN_PER_DEG_Y = 4.95 * 0.900 / (54.55 - 44.25)     # 画布高 × 轴占比 ÷ 纬度跨度


def _box(cx, cy, text, fs):
    w = (len(text) * fs * 0.60 / 72.0) / IN_PER_DEG_X   # 近似宽（度）
    h = (fs * 1.12 / 72.0) / IN_PER_DEG_Y
    return (cy - w / 2, cx - h / 2, cy + w / 2, cx + h / 2)


def _hit(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def place(ax, lat, lon, text, color, fs, placed, anchor="center"):
    """在锚点周围找不与已有标签重叠的位置。anchor=end 表示标签放在点的右上。"""
    cands = []
    if anchor == "below":
        cands = [(0.0, -0.42), (0.42, -0.36), (-0.42, -0.36), (0.0, 0.40),
                 (0.45, 0.26), (-0.45, 0.26), (0.62, 0.0), (-0.62, 0.0)]
    elif anchor == "end":
        cands = [(0.22, 0.16), (0.22, -0.16), (-0.22, 0.16), (-0.22, -0.16),
                 (0.0, 0.30), (0.45, 0.0), (-0.45, 0.0), (0.0, -0.30)]
    else:
        cands = [(0.0, 0.0), (0.0, 0.20), (0.0, -0.20), (0.28, 0.0), (-0.28, 0.0),
                 (0.28, 0.20), (-0.28, 0.20), (0.28, -0.20), (-0.28, -0.20)]
    for dx, dy in cands:
        bb = _box(lat + dy, lon + dx, text, fs)
        if not any(_hit(bb, o) for o in placed):
            placed.append(bb)
            ax.text(lon + dx, lat + dy, text, fontsize=fs, color=color,
                    ha="center", va="center", zorder=7,
                    bbox=dict(fc="white", ec="none", alpha=0.80, pad=0.45))
            return
    bb = _box(lat + cands[0][1], lon + cands[0][0], text, fs)
    placed.append(bb)
    ax.text(lon + cands[0][0], lat + cands[0][1], text, fontsize=fs, color=color,
            ha="center", va="center", zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.80, pad=0.45))

def main():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": ["Source Han Sans"], "pdf.fonttype": 42,
        "font.size": 6.4, "axes.unicode_minus": False,
        "svg.fonttype": "path", "savefig.dpi": 340,
    })
    placed = []
    fig, ax = plt.subplots(figsize=(6.35, 4.95))
    ax.set_xlim(-8.5, 6.45)
    ax.set_ylim(44.25, 54.55)
    ax.set_aspect(1 / np.cos(np.radians(49.5)))
    ax.set_facecolor("#f7f8fa")
    for s in ax.spines.values():
        s.set_linewidth(0.6)
        s.set_color("#9aa0a8")
    ax.set_xticks(range(-8, 7, 2))
    ax.set_yticks(range(44, 55, 2))
    ax.set_xticklabels([f"{abs(t)}°{'W' if t < 0 else 'E'}" for t in range(-8, 7, 2)],
                       fontsize=6.0, color="#6b7280")
    ax.set_yticklabels([f"{t}°N" for t in range(44, 55, 2)],
                       fontsize=6.0, color="#6b7280")
    ax.grid(True, color=GRID, lw=0.45, zorder=0)
    ax.tick_params(length=2, width=0.5, colors="#6b7280", pad=1.5)

    # 登陆准备区（星号 + 区名；区名最先占位，后面的巡逻区名与航线名绕开它）
    for name, (la, lo) in LANDING:
        ax.plot(lo, la, marker="*", ms=8.0, mfc="#d8c400", mec="#7a6b00", mew=0.5, zorder=7)
        tlo, tla = LANDING_POS[name]
        placed.append(_box(tla, tlo, f"{name}海滩", 6.2))
        ax.text(tlo, tla, f"{name}海滩", fontsize=6.2, color="#5d5200",
                ha="center", va="center", zorder=8,
                bbox=dict(fc="#fffbe6", ec="none", alpha=0.88, pad=0.5))

    # 巡逻区：淡填充 + 不透明的虚线边框。
    # 注意不能对同一个 patch 直接给 alpha——那会把边框一起透明掉，
    # 上一版正是这样，虚线在浅底上几乎看不见，图上只剩区名。
    for name, pts, kind in PATROL:
        small = name in SMALL_ZONES
        # pts 是 (lat, lon)，画到图上要换序成 (lon, lat)，否则四个顶点会落到轴外
        xy = [(lo, la) for la, lo in pts]
        ax.add_patch(Polygon(xy, closed=True, facecolor=PAT_EDGE,
                             alpha=PAT_FILL[kind], edgecolor="none", zorder=2))
        ax.add_patch(Polygon(xy, closed=True, facecolor="none",
                             edgecolor=PAT_EDGE, lw=0.7 if small else 1.0,
                             ls=PAT_DASH[kind], joinstyle="miter", zorder=3))
        if small:
            continue
        cx = np.mean([p[0] for p in pts])
        cy = np.mean([p[1] for p in pts])
        dx, dy = PAT_OFF.get(name, (0.0, 0.0))
        place(ax, cx + dy, cy + dx, name, "#3b3f78", 6.0, placed)

    # 支援航线
    for name, a, b, grp in SUPPORT:
        ax.add_patch(FancyArrowPatch((a[1], a[0]), (b[1], b[0]),
                                     arrowstyle="-|>", mutation_scale=5.5,
                                     lw=0.95, color=COL_SUP[grp], alpha=0.9,
                                     shrinkA=1.0, shrinkB=0.6, zorder=4))
        ax.plot(a[1], a[0], marker="o", ms=1.9, color=COL_SUP[grp], zorder=5)
        place(ax, b[0], b[1], name, COL_SUP[grp], 6.0, placed, anchor="end")

    # 三个方向的分区提示
    for lo0, lo1, txt in [(-8.6, -3.4, "西段（左）"), (-3.0, 1.4, "中段"),
                          (1.6, 6.6, "东北方向")]:
        ax.plot([lo0, lo1], [54.15, 54.15], color="#9aa0a8", lw=0.6)
        ax.text((lo0 + lo1) / 2, 54.38, txt, fontsize=6.6, color="#4b5563",
                ha="center", va="center", weight="bold")

    h1 = [Line2D([0], [0], color=COL_SUP[k], lw=1.2, label=f"支援任务·{k}") for k in COL_SUP]
    h2 = [Patch(facecolor=PAT_EDGE, alpha=0.35, edgecolor=PAT_EDGE,
                ls=PAT_DASH[k], lw=1.0, label=f"巡逻区·{k}") for k in PAT_DASH]
    h3 = [Line2D([0], [0], marker="*", color="none", mfc="#d8c400", mec="#7a6b00",
                 ms=7, label="登陆准备区")]
    leg = ax.legend(handles=h1 + h2 + h3, loc="lower right", fontsize=5.7,
                    frameon=True, framealpha=0.92, edgecolor="#cfd4da",
                    ncol=2, columnspacing=1.0, handlelength=1.6,
                    borderpad=0.5, labelspacing=0.45)
    leg.set_zorder(10)
    fig.subplots_adjust(left=0.062, right=0.988, top=0.975, bottom=0.075)
    out = os.path.join(FIG, "fig_tasks-overview.png")
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.03)
    print("->", out)


if __name__ == "__main__":
    main()
