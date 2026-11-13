#!/usr/bin/env python
"""模板对齐版专用图：全局任务总览 / 细节标注 / 能力雷达 / 性能曲线 / 三节量化边界。

素材：work/frames/{red,blue}/*.jpg（由 scripts/extract_frames.py 从比赛录屏抽帧）
输出：paper/shared/figures/align-*.png
"""
import math
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from PIL import Image
from matplotlib.patches import FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PAPER))
FIG = os.path.join(PAPER, "figures")
FR = os.path.join(ROOT, "work", "frames")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
GRAY = "#333333"
ACC = "#e01b24"
BLUE = "#1a5fb4"
WHT = "#ffffff"


def setup():
    mpl.font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": ["Source Han Sans"],
        "svg.fonttype": "path", "pdf.fonttype": 42, "savefig.dpi": 300,
        "font.size": 7, "axes.unicode_minus": False,
    })


def load(side, name):
    return np.asarray(Image.open(os.path.join(FR, side, name)).convert("RGB"))


def shot(name, img, tags, figsize=(6.6, 4.13), note="", crop=None,
         box_color=ACC, legend=None):
    """在截图上打引线标注。tags: [(xy, xytext, text)]，坐标为原图像素。"""
    if crop:
        x0, y0, x1, y1 = crop
        img = img[y0:y1, x0:x1]
        tags = [((a[0] - x0, a[1] - y0), (b[0] - x0, b[1] - y0), t)
                for a, b, t in tags]
    H, W = img.shape[:2]
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(img, extent=(0, W, H, 0))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    for (xy, xytext, text) in tags:
        ax.annotate(
            text, xy=xy, xytext=xytext, fontsize=6.4, color=WHT,
            ha="left", va="center", zorder=20,
            bbox=dict(boxstyle="round,pad=0.30", fc=box_color, ec="none", alpha=0.93),
            arrowprops=dict(arrowstyle="-|>", color=box_color, lw=1.2,
                            shrinkA=1, shrinkB=3,
                            connectionstyle="arc3,rad=0.10"),
        )
    if legend:
        for i, (color, txt) in enumerate(reversed(legend)):
            ax.add_patch(mpl.patches.Rectangle(
                (W * 0.014, H * (0.955 - i * 0.038)), W * 0.012, H * 0.018,
                transform=ax.transData, fc=color, ec="none", zorder=21))
            ax.text(W * 0.032, H * (0.964 - i * 0.038), txt, fontsize=5.6,
                    color=WHT, va="center", zorder=21,
                    bbox=dict(boxstyle="square,pad=0.16", fc="#00000088", ec="none"))
    if note:
        ax.text(W - 8, H - 6, note, fontsize=5.4, color=WHT, ha="right",
                va="bottom", alpha=0.9, zorder=21,
                bbox=dict(boxstyle="square,pad=0.18", fc="#00000066", ec="none"))
    plt.subplots_adjust(0, 0, 1, 1)
    save(fig, name)


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    p = os.path.join(FIG, f"{name}.png")
    fig.savefig(p, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"  → figures/{name}.png")


# ---------------------------------------------------------------- 全局任务总览
def overview_red():
    im = load("red", "red_0300s.jpg")
    tags = [
        ((1010, 780), (1180, 640), "① 地空导弹营与拦截包线\n（三层同心圆＝探测/发射/不可逃逸区）"),
        ((1090, 950), (1170, 1080), "② 登陆准备区（宝剑海滩，黄色多边形）"),
        ((1690, 500), (1500, 380), "③ 北制空巡逻区（A-100 / 苏-57 前出方向）"),
        ((1210, 1105), (760, 1230), "④ 巡逻区与责任区边界\n（端点标 RP-T71xx）"),
        ((330, 1400), (420, 1520), "⑤ 登陆编队（7 艘坦克登陆舰 + 23900 船坞登陆舰）"),
        ((560, 430), (330, 300), "⑥ 机场出击走廊（支援任务航路，绿线）"),
        ((2050, 105), (1830, 215), "⑦ 帧耗时读数 37 / 37 ms"),
    ]
    shot("align-ov-red", im, tags,
         note="客户端全屏录屏 2560×1600｜选手 1 红方视角 05:00",
         legend=[(ACC, "红＝本方"), (BLUE, "蓝＝对方"), ("#d8c400", "黄＝登陆准备区")])


def overview_blue():
    im = load("blue", "blue_0959s.jpg")
    tags = [
        ((1980, 1090), (1560, 1250), "① 岸防展开线：反舰导弹排 / 装甲车 / 地空导弹连"),
        ((1050, 1030), (300, 900), "② 红方登陆准备区（本视角的黄色多边形）"),
        ((1000, 520), (620, 380), "③ 无人机载弹巡逻区（MQ-1C 诱饵）"),
        ((1060, 1255), (700, 1420), "④ 蓝方支援区域（C-5M 空投目标）与反舰导弹排"),
        ((1130, 1000), (1320, 860), "⑤ 任务参考点 RP-M32xx 与任务名\n（含预留占位任务）"),
    ]
    shot("align-ov-blue", im, tags,
         note="客户端全屏录屏 2560×1600｜选手 1 蓝方视角 16:00",
         legend=[(BLUE, "蓝＝本方"), (ACC, "红＝对方"), ("#d8c400", "黄＝区域")])


# ---------------------------------------------------------------- 细节标注
def details():
    fig = plt.figure(figsize=(6.6, 4.6))
    gs = fig.add_gridspec(2, 2, wspace=0.05, hspace=0.20)
    specs = [
        ("c_sam_label.jpg", "a　地空导弹营：单元标签与阵地",
         "标签“地空导弹营（霍克导弹 [P3, TAS]）#31”可直接读出；黄色菱形为本营阵地",
         [((760, 300), (300, 420), "标签给出对象名、武器型号与单元号")]),
        ("c_patrol.jpg", "b　巡逻区边界与任务参考点",
         "红色虚线为巡逻区边界，端点标 RP-T71xx；右上为“阵风 2 巡逻区”",
         [((300, 430), (700, 545), "端点编号 = 平台自动生成的任务参考点")]),
        ("c_landing.jpg", "c　登陆准备区：区域与端点",
         "“宝剑海滩登陆”区域（浅绿多边形），两端为 RP-T71xx 参考点",
         [((560, 480), (900, 600), "红方两栖舰船进区即开始 20 分钟计时")]),
        ("c_combat_marks.jpg", "d　交战密集区：机群、航迹与瞄准标记",
         "红色为红方机群，蓝线为其历史航迹，白色十字为当前瞄准点；蓝色图标为对方与中立单位",
         [((250, 260), (620, 420), "同一时刻多批目标与瞄准标记并存")]),
    ]
    for i, (fn, title, note, tags) in enumerate(specs):
        ax = fig.add_subplot(gs[i // 2, i % 2])
        img = np.asarray(Image.open(os.path.join(ROOT, "work", "lp", "full", fn)).convert("RGB"))
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)
            sp.set_color(GRAY)
        for (xy, xytext, text) in tags:
            ax.annotate(text, xy=xy, xytext=xytext, fontsize=5.6, color=WHT,
                        ha="left", va="center", zorder=20,
                        bbox=dict(boxstyle="round,pad=0.28", fc=ACC, ec="none", alpha=0.93),
                        arrowprops=dict(arrowstyle="-|>", color=ACC, lw=1.1,
                                        shrinkA=1, shrinkB=3,
                                        connectionstyle="arc3,rad=0.10"))
        ax.set_title(title, fontsize=6.6, pad=2.5, loc="left")
        ax.text(0.012, -0.05, note, transform=ax.transAxes, fontsize=4.9,
                color=GRAY, va="top", ha="left", wrap=True)
    fig.subplots_adjust(0.01, 0.07, 0.99, 0.97)
    save(fig, "align-detail")


# ---------------------------------------------------------------- 作战能力雷达
def radar():
    axes = ["1500 km/h\n存活率", "2500 km/h\n存活率", "3500 km/h\n存活率",
            "五档均值", "反打率"]
    data = {
        "R 现行分档 50/20": [1.000, 0.645, 0.781, 0.884, 0.88],
        "B1 固定 25 km": [1.000, 1.000, 0.619, 0.924, 0.92],
        "A2 固定 50 km": [1.000, 1.000, 0.790, 0.958, 0.96],
        "P 1.2×d0 插值": [1.000, 1.000, 1.000, 1.000, 1.00],
    }
    colors = [ACC, "#c64600", "#26a269", BLUE]
    n = len(axes)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(3.4, 3.0), subplot_kw=dict(polar=True))
    for (k, v), c in zip(data.items(), colors):
        vals = v + v[:1]
        ax.plot(ang, vals, lw=1.1, color=c, label=k)
        ax.fill(ang, vals, color=c, alpha=0.08)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(axes, fontsize=5.6)
    ax.set_ylim(0.4, 1.02)
    ax.set_yticks([0.5, 0.7, 0.9, 1.0])
    ax.set_yticklabels(["0.5", "0.7", "0.9", "1.0"], fontsize=4.6)
    ax.grid(lw=0.4, color="#bbbbbb")
    ax.spines["polar"].set_linewidth(0.4)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2,
              fontsize=5.4, frameon=False, handlelength=1.4)
    save(fig, "align-radar")


# ---------------------------------------------------------------- 性能曲线
def perf():
    N = np.array([50, 100, 200, 400])
    per_unit = {"物理作战域监控（7.4 µs/单元）": 7.4e-3,
                "空战单元自卫（10.4 µs/机）": 10.4e-3,
                "空空作战（7.0 µs/机）": 7.0e-3,
                "地空导弹营（4.8 µs/营）": 4.8e-3}
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    for (k, v), c in zip(per_unit.items(), [ACC, BLUE, "#26a269", "#c64600"]):
        ax.plot(N, N * v, "-o", ms=3.0, lw=1.0, color=c, label=k)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(N)
    ax.set_xticklabels([str(x) for x in N], fontsize=5.4)
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_xlim(45, 450)
    ax.set_ylim(0.15, 12)
    ax.set_yticks([0.2, 0.5, 1, 2, 5, 10])
    ax.set_yticklabels(["0.2", "0.5", "1", "2", "5", "10"], fontsize=5.4)
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_xlabel("同类单元数 N（对数轴）", fontsize=6.2)
    ax.set_ylabel("单步规则判定耗时 / ms（对数轴）", fontsize=6.2)
    ax.grid(lw=0.3, color="#dddddd", which="both")
    ax.legend(fontsize=4.9, frameon=False, loc="upper left")
    ax.text(52, 0.24, "决策间隔的墙钟预算为 3000 ms；\n最重的曲线在 N=400 时也仅占 0.15%",
            fontsize=4.8, color=GRAY)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "align-perf")


# ---------------------------------------------------------------- 三节量化边界
def boundary():
    figs = []
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.0))

    # (a) BOL：目标点偏差 → 单发命中概率（搜索半径 r 为参数）
    ax = axs[0]
    dev = np.linspace(0.5, 20, 200)
    for r, c in [(4, ACC), (8, "#c64600"), (12, BLUE)]:
        p = np.where(dev <= r, 1.0, (r / dev) ** 2)
        ax.plot(dev, p, lw=1.1, color=c, label=f"搜索半径 {r} km")
    ax.set_xlabel("目标点偏差 / km", fontsize=6.0)
    ax.set_ylabel("单发命中概率", fontsize=6.0)
    ax.set_title("a　BOL 纯方位打击", fontsize=6.4, loc="left")
    ax.legend(fontsize=5.0, frameon=False)
    ax.grid(lw=0.3, color="#dddddd")
    ax.tick_params(labelsize=5.2)
    ax.spines[["top", "right"]].set_visible(False)

    # (b) 加油：M/M/c 排队利用率与平均等待
    ax = axs[1]
    lam = np.linspace(0.5, 12, 300)       # 架次/小时
    mu = 60.0 / 6.0                        # 每架 6 分钟，10 架次/小时
    for c, col in [(1, ACC), (2, "#c64600"), (3, BLUE)]:
        rho = lam / (c * mu)
        ok = rho < 0.98
        ax.plot(lam[ok], rho[ok], lw=1.1, color=col, label=f"{c} 架加油机")
    ax.axvline(10, color=GRAY, ls=":", lw=0.8)
    ax.text(10.2, 0.25, "本场 1 架 A-330-200\n的饱和点", fontsize=5.0, color=GRAY)
    ax.set_xlabel("加油需求率 /（架次每小时）", fontsize=6.0)
    ax.set_ylabel("加油机利用率 ρ", fontsize=6.0)
    ax.set_title("b　加油规划（排队模型）", fontsize=6.4, loc="left")
    ax.legend(fontsize=5.0, frameon=False)
    ax.grid(lw=0.3, color="#dddddd")
    ax.tick_params(labelsize=5.2)
    ax.spines[["top", "right"]].set_visible(False)

    # (c) 预警机：雷达地平线 vs 包线约束
    ax = axs[2]
    h_t = np.linspace(0.05, 6, 300)                 # km
    for h_r, col in [(6, ACC), (8, "#c64600"), (10, BLUE)]:
        d = 3.57 * (math.sqrt(h_r * 1000) + np.sqrt(h_t * 1000))
        ax.plot(d, h_t, lw=1.1, color=col, label=f"站位高度 {h_r} km")
    for x, txt in [(60, "敌 SAM 包线\n60 km"), (100, "我 SAM 包线\n100 km")]:
        ax.axvline(x, color=GRAY, ls=":", lw=0.8)
        ax.text(x + 4, 5.2, txt, fontsize=4.8, color=GRAY, va="top")
    ax.set_xlabel("雷达地平线距离 / km", fontsize=6.0)
    ax.set_ylabel("目标高度 / km", fontsize=6.0)
    ax.set_title("c　预警机站位（地平线 vs 包线）", fontsize=6.4, loc="left")
    ax.set_xlim(0, 400)
    ax.legend(fontsize=5.0, frameon=False, loc="lower right")
    ax.grid(lw=0.3, color="#dddddd")
    ax.tick_params(labelsize=5.2)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save(fig, "align-boundary")
    # 单面板另存，便于分节引用
    for i, name in enumerate(["align-bol", "align-fuel", "align-aew"]):
        f2, a2 = plt.subplots(figsize=(2.3, 2.0))
        src = axs[i]
        for ln in src.get_lines():
            a2.plot(ln.get_xdata(), ln.get_ydata(), lw=1.1,
                    color=ln.get_color(), label=ln.get_label())
        for ln in src.collections:
            pass
        a2.set_xlabel(src.get_xlabel(), fontsize=5.8)
        a2.set_ylabel(src.get_ylabel(), fontsize=5.8)
        a2.set_title(src.get_title(), fontsize=6.2, loc="left")
        a2.tick_params(labelsize=5.0)
        a2.grid(lw=0.3, color="#dddddd")
        a2.spines[["top", "right"]].set_visible(False)
        a2.legend(fontsize=4.6, frameon=False)
        if name == "align-aew":
            a2.set_xlim(0, 400)
        f2.tight_layout()
        save(f2, name)


def main():
    setup()
    print("生成模板对齐版插图：")
    for fn in (overview_red, overview_blue, details, radar, perf, boundary, theaters, sequence):
        try:
            fn()
        except Exception as e:
            print(f"  ! {fn.__name__} 失败: {e}")



# ---------------------------------------------------------------- 战区部署图（裁剪 + 标注）
def theaters():
    red = load("red", "red_0300s.jpg")
    blue = load("blue", "blue_0959s.jpg")

    west = (0, 260, 1180, 1600)
    shot("align-west", red, [
        ((560, 580), (600, 420), "① 伊尔-22PP 电子侦察机前出"),
        ((700, 780), (760, 900), "② 地空导弹营包线（西缘）"),
        ((350, 1390), (420, 1180), "③ 登陆编队与马洛海滩登陆准备区"),
    ], figsize=(4.4, 5.0), crop=west,
        note="红方视角 05:00｜西段（西经 8°–5°）")

    mid = (700, 300, 1900, 1520)
    shot("align-mid", red, [
        ((1094, 943), (1150, 1180), "① 宝剑海滩登陆准备区"),
        ((943, 757), (1000, 620), "② 中央拦截线（本例为一次交战）"),
        ((1483, 1024), (1530, 860), "③ 阵风 2 巡逻区（中段值班）"),
    ], figsize=(4.4, 5.0), crop=mid,
        note="红方视角 05:00｜中段（西经 2°–东经 2°）")

    ne = (1400, 180, 2560, 1180)
    shot("align-ne", red, [
        ((1513, 407), (1560, 300), "① 北鹰狮-1 支援航线"),
        ((1699, 496), (1740, 640), "② 北制空巡逻区（A-100 / 苏-57 前出）"),
        ((2200, 279), (2050, 380), "③ 东北方向地空导弹营"),
    ], figsize=(4.8, 4.2), crop=ne,
        note="红方视角 05:00｜东北干预方向（东经 2° 以东）")

    bl = (850, 600, 2250, 1500)
    shot("align-coast", blue, [
        ((1059, 1175), (1150, 1010), "① 反舰导弹排阵地（黄框）"),
        ((908, 1252), (700, 1400), "② 蓝方支援区域（C-5M 空投目标）"),
        ((1500, 1000), (1560, 860), "③ 岸防单元与任务连线"),
    ], figsize=(4.8, 3.9), crop=bl,
        note="蓝方视角 16:00｜岸防与支援区域")


# ---------------------------------------------------------------- 连续帧（同一视角，6 s 间隔）
def sequence():
    import matplotlib.image as mpimg
    files = [("t1626", "27:26"), ("t1632", "27:32"), ("t1638", "27:38")]
    box = (700, 520, 1500, 1240)
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.3))
    for ax, (fn, label) in zip(axs, files):
        img = mpimg.imread(os.path.join(ROOT, "work", "frames", "seq2", f"{fn}.jpg"))
        x0, y0, x1, y1 = box
        ax.imshow(img[y0:y1, x0:x1])
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_linewidth(0.4); sp.set_color(GRAY)
        ax.set_title(f"t = {label}", fontsize=5.6, pad=1.5, loc="left")
    fig.subplots_adjust(0.005, 0.01, 0.995, 0.95, wspace=0.03)
    save(fig, "align-seq")

if __name__ == "__main__":
    main()
