#!/usr/bin/env python
"""
文稿插图（Nature 风格 / matplotlib）
==================================
图契约（每个面板必须承载一条独立证据，不为装饰而画）

F1 架构      核心结论：五个智能体不是并列关系，而是"一个共享观测底座 + 四个
             互不相交的决策域"；决定性的耦合点是监控输出（弹型+弹速）。
             F1a 数据流与决策域划分；F1b 单体决策状态机（以空战躲避为例）。

F2 空战躲避  核心结论：分档掉头规则的方向正确，但 50 km 档对 >3300 km/h 的
             来袭弹仍不足；垂直扭的收益只出现在晚掉头分支，且取决于来袭弹的
             转弯能力（ω）——它是一个"抓对手过载极限"的规则，而非普适增益。
             F2a 交会几何；F2b 存活率相图；F2c 存活—时长 Pareto；F2d 策略对比。

F3 打空战    核心结论：临界距离 d0 有闭式解，且线性衰减与 MOD 衰减相差约 35%，
             这使"按固定 WRA 距离开火"必然在尾追态势下浪费弹；0.8·d0 判定在
             全部算例中把无效发射率从 87%–100% 压到 0，同时保住先射权。
             F3a 解析 d0；F3b d0 等值线；F3c 策略对比（命中率/先射优势）。

F4 高度与地导 核心结论：高低差在纯运动学下只值 ±18% 的有效交距，但足以把
             处于包线边缘的交战从"必中"推到"必失"；地导开火时机同理——单发
             概率随距离单调下降，3/5 Dmax 并非最优点。
             F4a d0 vs 高度比；F4b 地导开火比例 vs 综合概率。

F5 船只自卫  核心结论：分层补射在"拦截率—拦截距离"平面上并非占优方案，而是
             在"提前拦截换安全裕度"上做的一次取舍；真正的增益来自**弹舱分担**
             （单船方案在 8 枚以上来袭时崩溃）。
             F5a 四方案权衡；F5b 累计拦截曲线；F5c 规模效应。

F6 敏感性    核心结论：存活由能量参数主导；机动参数只在近距离扭动分支起作用，
             且存在 ω 悬崖与换向周期的非单调共振。
             F6a OAT 龙卷风图；F6b ω 悬崖。

导出：SVG（文字转路径，避免 CJK 字体依赖）+ PDF + TIFF(600dpi)
"""
import csv
import math
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
DATA = os.path.join(PAPER, "data")
FIG = os.path.join(PAPER, "figures")

# ---------------------------------------------------------------- 样式
CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")

GRAY = "#1a1a1a"
MID = "#6b6b6b"
LIGHT = "#c9c9c9"
ACC = "#b3261e"          # 强调色（我们的方案）
ACC2 = "#1f4e79"         # 次要色


def setup():
    if os.path.exists(CJK):
        mpl.font_manager.fontManager.addfont(CJK)
        mpl.rcParams["font.family"] = ["Source Han Sans"]
    mpl.rcParams.update({
        "font.size": 7,
        "axes.linewidth": 0.6,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.edgecolor": GRAY,
        "axes.labelcolor": GRAY,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "text.color": GRAY,
        "legend.frameon": False,
        "legend.fontsize": 6.4,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.4,
        "ytick.labelsize": 6.4,
        "lines.linewidth": 1.0,
        "savefig.dpi": 600,
    })


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"),
                    bbox_inches="tight", dpi=600 if ext == "png" else None)
    plt.close(fig)
    print(f"  → figures/{name}.svg")


def panel_tag(ax, s, dx=-0.13, dy=1.04):
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="bottom", ha="left", color="#000")


def rd(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


# ---------------------------------------------------------------- 解析
T_BURN_H = 240.0 / 3600.0      # h
V_TERM = 500.0


def d0_linear(v0, va, t_burn_h=T_BURN_H):
    """线性衰减下的闭式临界距离（km）"""
    if v0 <= va:
        return 0.0
    if va <= V_TERM:
        return t_burn_h * (v0 - V_TERM) / 2.0 + t_burn_h * (V_TERM - va)
    return t_burn_h * (v0 - va) ** 2 / (2.0 * (v0 - V_TERM))


def d0_mod(v0, va, t_burn_h=T_BURN_H):
    """指数(MOD)衰减下的闭式临界距离（km）"""
    if v0 <= max(va, V_TERM):
        return 0.0
    ln = math.log(v0 / V_TERM)
    if va <= V_TERM:
        return t_burn_h * (v0 - V_TERM) / ln
    return t_burn_h / ln * ((v0 - va) - va * math.log(v0 / va))


# ---------------------------------------------------------------- F2
def fig2():
    rows_p = rd("a_evade_policy.csv")
    rows_par = rd("a_evade_pareto.csv")
    fig = plt.figure(figsize=(7.2, 2.6))
    gs = fig.add_gridspec(1, 3, wspace=0.52, width_ratios=[1.1, 1, 1])

    # --- a 存活率相图
    ax = fig.add_subplot(gs[0, 0])
    panel_tag(ax, "a")
    v0s = sorted({int(r["v0_kmh"]) for r in rows_par})
    rs = sorted({int(r["r_turn_km"]) for r in rows_par})
    Z = np.zeros((len(v0s), len(rs)))
    for r in rows_par:
        Z[v0s.index(int(r["v0_kmh"])), rs.index(int(r["r_turn_km"]))] = \
            float(r["survive_rate"])
    X, Y = np.meshgrid(rs, v0s)
    cf = ax.contourf(X, Y, Z, levels=np.linspace(0, 1, 11), cmap="Greys")
    ax.contour(X, Y, Z, levels=[0.5, 0.9], colors=[ACC, ACC2],
               linewidths=[0.8, 0.8], linestyles=["--", "-"])
    cb = fig.colorbar(cf, ax=ax, pad=0.02, fraction=0.05)

    cb.ax.tick_params(labelsize=6)
    # 规则分段
    ax.plot([20, 20], [1500, 2500], color=ACC, lw=2.0, alpha=0.85)
    ax.plot([50, 50], [2500, 3500], color=ACC, lw=2.0, alpha=0.85, ls=":")
    ax.plot([10, 10], [1400, 1500], color=ACC, lw=2.0, alpha=0.85)
    ax.text(21.0, 1590, "规则分档", fontsize=5.6, color=ACC)
    ax.text(49.0, 2600, "50 km\n仍不足", fontsize=5.2, color=ACC, ha="right", va="top", linespacing=1.3)
    ax.set_xlabel("掉头距离 / km")
    ax.set_ylabel("来袭弹速 / (km/h)")
    ax.set_title("存活率相图", fontsize=7, pad=4)

    # --- b Pareto
    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    mk = ["o", "s", "^", "D", "v"]
    rule_pick = {1500: 10, 2000: 20, 2500: 20, 3000: 50, 3500: 50}
    for i, v0 in enumerate(v0s):
        sub = [r for r in rows_par if int(r["v0_kmh"]) == v0]
        sub.sort(key=lambda r: int(r["r_turn_km"]))
        x = [int(r["r_turn_km"]) for r in sub]
        y = [float(r["survive_rate"]) for r in sub]
        ax.plot(x, y, marker=mk[i], ms=2.4, lw=0.7, color=plt.cm.Greys(
            0.30 + 0.14 * i), label=f"{v0}", zorder=2)
        rp = rule_pick.get(v0)
        if rp in x:
            ax.plot([rp], [y[x.index(rp)]], marker="*", ms=8, color=ACC,
                    mec="white", mew=0.4, zorder=5)
    ax.plot([], [], marker="*", ms=7, ls="none", color=ACC,
            label="规则取值点")
    ax.set_xlabel("掉头距离 / km")
    ax.set_ylabel("存活率")
    ax.set_ylim(-0.04, 1.08)
    ax.legend(title="来袭弹速", fontsize=5.4, title_fontsize=5.4,
              ncol=2, loc="lower right")
    ax.set_title("存活率—掉头距离", fontsize=7, pad=4)

    # --- c 策略对比
    ax = fig.add_subplot(gs[0, 2])
    panel_tag(ax, "c")
    labels, vals, cols = [], [], []
    order = ["B0 弹速归零才脱离", "A3 掉头距离全取 20 km",
             "R  分档+垂直扭+能量阈值", "B2 单分档(仅 >2500 判 50 km)",
             "A1 去掉能量阈值(不反打)", "B1 单一固定掉头 25 km",
             "A2 掉头距离全取 50 km", "P 按 d0 插值 (1.2 d0)"]
    for pol in order:
        sub = [r for r in rows_p if r["policy"] == pol]
        if not sub:
            continue
        m = np.mean([float(r["survive_rate"]) for r in sub])
        labels.append(pol.split(" ")[0])
        vals.append(m)
        cols.append(ACC if pol.startswith("P") else LIGHT)

    y = np.arange(len(labels))
    ax.barh(y, vals, color=cols, height=0.62, ec=GRAY, lw=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6.0)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("全弹速平均存活率")
    for yy, v in zip(y, vals):
        ax.text(v + 0.02, yy, f"{v:.2f}", va="center", fontsize=5.8)
    ax.invert_yaxis()
    ax.set_title("策略对比", fontsize=7, pad=4)
    return fig


# ---------------------------------------------------------------- F3
def fig3():
    fig = plt.figure(figsize=(7.2, 2.6))
    gs = fig.add_gridspec(1, 3, wspace=0.34, width_ratios=[1, 1, 1.15])

    # --- a 解析 d0
    ax = fig.add_subplot(gs[0, 0])
    panel_tag(ax, "a")
    v0 = np.linspace(1200, 3600, 200)
    for va, ls in ((900, "-"), (1200, "--")):
        ax.plot(v0, [d0_linear(v, va) for v in v0], color=ACC, ls=ls, lw=1.0)
        ax.plot(v0, [d0_mod(v, va) for v in v0], color=ACC2, ls=ls, lw=1.0)
    ax.plot([], [], color=ACC, label="线性衰减")
    ax.plot([], [], color=ACC2, label="MOD 衰减")
    ax.plot([], [], color=GRAY, ls="-", label="V敌=900")
    ax.plot([], [], color=GRAY, ls="--", label="V敌=1200")
    rows = rd("../../docs/实验/e2_d0.csv")
    if rows:
        xs = [float(r["v0_kmh"]) for r in rows if r["v_target_kmh"] == "900"]
        ys = [float(r["d0_km"]) for r in rows if r["v_target_kmh"] == "900"]
        ax.plot(xs, ys, "o", ms=2.4, mfc="white", mec=GRAY, mew=0.5)
    ax.set_xlabel("导弹初速 / (km/h)")
    ax.set_ylabel("临界距离 $d_0$ / km")
    ax.legend(fontsize=5.2, loc="upper left")
    ax.set_title("$d_0$ 闭式解（点=数值二分）", fontsize=7)

    # --- b 等值线
    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    V0 = np.linspace(1200, 3600, 120)
    VA = np.linspace(700, 1400, 120)
    X, Y = np.meshgrid(V0, VA)
    Z = np.vectorize(d0_linear)(X, Y)
    cs = ax.contourf(X, Y, Z, levels=12, cmap="Greys")
    ax.contour(X, Y, Z, levels=[20, 40, 60, 80], colors=MID, linewidths=0.4)
    cb = fig.colorbar(cs, ax=ax, pad=0.03, fraction=0.05)
    cb.set_label("$d_0$ / km", fontsize=6.2, labelpad=6)
    cb.ax.tick_params(labelsize=5.8, pad=1.5)
    ax.set_xlabel("导弹初速 / (km/h)")
    ax.set_ylabel("目标速度 / (km/h)")
    ax.set_title("$d_0$ 等值线（尾追）", fontsize=7)

    # --- c 策略对比
    ax = fig.add_subplot(gs[0, 2])
    panel_tag(ax, "c")
    rows = rd("b_aircombat_policy.csv")
    strats = ["R 0.8·d0", "B3 固定 30km", "B2 固定 60nm", "B1 最大射程 90nm"]
    cols = [ACC, "#8c8c8c", "#b8b8b8", "#dcdcdc"]
    x = np.arange(len(strats))
    hr, adv = [], []
    for s in strats:
        sub = [r for r in rows if r["strategy"] == s]
        hr.append(np.mean([float(r["hit_rate"]) for r in sub]) if sub else 0)
        adv.append(np.mean([float(r["first_shot_advantage_s"]) for r in sub])
                   if sub else 0)
    ax.bar(x, hr, color=cols, ec=GRAY, lw=0.4, width=0.6)
    ax.set_ylim(0, 1.34)
    ax.set_ylabel("命中率")
    ax.set_xticks(x)
    ax.set_xticklabels(["$0.8d_0$\n(本方案)", "固定\n30 km", "固定\n60 nm",
                        "最大射程\n90 nm"], fontsize=6.0)
    for xi, v in zip(x, hr):
        ax.text(xi, v + 0.03, f"{v:.2f}", ha="center", fontsize=5.8)
    ax2 = ax.twinx()
    ax2.plot(x, adv, "o--", color=ACC2, ms=3.0, lw=0.8)
    ax2.axhline(0, color=LIGHT, lw=0.5)
    ax2.set_ylim(min(adv) - 18, max(adv) + 18)
    ax2.set_ylabel("先射时间差 / s", color=ACC2)
    ax2.tick_params(axis="y", colors=ACC2, labelsize=6)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(ACC2)
    ax.set_title("开火策略：命中率与先射权", fontsize=7)
    return fig


# ---------------------------------------------------------------- F4
def fig4():
    fig = plt.figure(figsize=(7.2, 2.5))
    gs = fig.add_gridspec(1, 2, wspace=0.30, width_ratios=[1, 1.1])

    ax = fig.add_subplot(gs[0, 0])
    panel_tag(ax, "a")
    rows = rd("../../docs/实验/e3_altitude.csv")
    if rows:
        r = [float(x["ratio_shooter_over_target"]) for x in rows]
        d = [float(x["d0_km"]) for x in rows]
        ax.plot(r, d, "o-", color=ACC, ms=3.2, lw=1.0)
        for xi, yi in zip(r, d):
            ax.annotate(f"{yi:.1f}", (xi, yi), textcoords="offset points",
                        xytext=(0, 6), fontsize=5.4, ha="center")
    ax.axvline(1.0, color=LIGHT, lw=0.7)
    ax.axvspan(0.9, 1.2, color="#f0f0f0", zorder=0)
    ax.text(1.05, min(d) + 0.6 if rows else 34, "规则容差带\n90%–120%",
            fontsize=5.6, color=MID, ha="left")
    ax.set_xlabel("射击方 / 目标 高度比")
    ax.set_ylabel("有效交距 $d_0$ / km")
    ax.set_title("高低差对有效交距的影响", fontsize=7)

    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    rows = rd("d_sam_opening.csv")
    if rows:
        f = [float(x["fire_fraction"]) for x in rows]
        p = [float(x["p_total"]) for x in rows]
        v = [float(x["v_end_kmh"]) for x in rows]
        ax.plot(f, p, "o-", color=ACC, ms=3.2, lw=1.0, label="综合拦截概率")
        ax.axvline(0.6, color=ACC2, ls="--", lw=0.8)
        ax.text(0.615, 0.42, "3/5 Dmax\n(讲解取值)", fontsize=5.6, color=ACC2)
        ax.plot([np.argmax(p) and f[int(np.argmax(p))]], [max(p)], "o",
                mfc="none", mec=ACC, ms=8)
        ax.set_ylim(0, 1.08)
        ax.set_xlabel("开火距离 / Dmax")
        ax.set_ylabel("综合拦截概率")
        ax2 = ax.twinx()
        ax2.plot(f, v, "s--", color=MID, ms=2.4, lw=0.7)
        ax2.set_ylabel("拦截末端弹速 / (km/h)", color=MID)
        ax2.tick_params(axis="y", colors=MID, labelsize=6)
        ax2.spines["right"].set_visible(True)
        ax2.spines["right"].set_color(MID)
    ax.set_title("地导开火时机：概率随距离单调下降", fontsize=7)
    return fig


# ---------------------------------------------------------------- F5
def fig5():
    fig = plt.figure(figsize=(7.2, 2.6))
    gs = fig.add_gridspec(1, 3, wspace=0.36, width_ratios=[1.1, 1, 1])

    schemes = {"R 双船分层": ACC, "B3 双船均½Dmax": ACC2,
               "B1 单船单层": "#8c8c8c", "B2 双船同时MAX": "#c4c4c4"}

    # --- a 权衡图
    ax = fig.add_subplot(gs[0, 0])
    panel_tag(ax, "a")
    rows = rd("c_ship_scheme.csv")
    for s, c in schemes.items():
        sub = [r for r in rows if r["scheme"] == s]
        if not sub:
            continue
        x = [float(r["mean_intercept_range_km"]) for r in sub]
        y = [float(r["intercept_rate"]) for r in sub]
        sz = [40 * float(r["shots_per_kill"]) for r in sub]
        ax.scatter(x, y, s=sz, color=c, ec=GRAY, lw=0.4, alpha=0.9, zorder=3)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="none", ms=4, color=c,
                      mec=GRAY, mew=0.4, label=s) for s, c in schemes.items()]
    ax.legend(handles=handles, fontsize=5.2, loc="lower left",
              handletextpad=0.3, borderpad=0.2)
    ax.set_xlabel("平均拦截距离 / km（越大越安全）")
    ax.set_ylabel("拦截率")
    ax.set_ylim(0.35, 0.95)
    ax.set_title("拦截率—拦截距离权衡（气泡=弹耗/拦截）", fontsize=7)

    # --- b 累计曲线
    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    rows = rd("c_ship_curve.csv")
    for s, c in schemes.items():
        sub = [r for r in rows if r["scheme"] == s and r["inbound"] == "8"]
        if not sub:
            continue
        sub.sort(key=lambda r: int(r["index"]))
        x = [int(r["index"]) for r in sub]
        y = np.cumsum([float(r["cum_intercept"]) for r in sub])
        ax.plot(x, y, marker="o", ms=2.2, lw=0.9, color=c, label=s)
    ax.set_xlabel("来袭弹序号")
    ax.set_ylabel("累计拦截数")
    ax.legend(fontsize=5.2, loc="upper left")
    ax.set_title("弹药消耗过程（8 枚）", fontsize=7)

    # --- c 规模效应
    ax = fig.add_subplot(gs[0, 2])
    panel_tag(ax, "c")
    rows = rd("c_ship_scheme.csv")
    for s, c in schemes.items():
        sub = [r for r in rows if r["scheme"] == s]
        if not sub:
            continue
        sub.sort(key=lambda r: int(r["inbound"]))
        ax.plot([int(r["inbound"]) for r in sub],
                [float(r["intercept_rate"]) for r in sub],
                marker="o", ms=2.4, lw=0.9, color=c, label=s)
    ax.set_xlabel("来袭规模 / 枚")
    ax.set_ylabel("拦截率")
    ax.set_title("规模效应：单船方案先崩", fontsize=7)
    return fig


# ---------------------------------------------------------------- F6
def fig6():
    fig = plt.figure(figsize=(7.2, 2.4))
    gs = fig.add_gridspec(1, 2, wspace=0.34, width_ratios=[1.15, 1])

    rows = rd("e_sensitivity.csv")
    ax = fig.add_subplot(gs[0, 0])
    panel_tag(ax, "a")
    if rows:
        groups = {}
        for r in rows:
            k = (r["policy"][:4], r["knob"])
            groups.setdefault(k, []).append(float(r["delta_vs_base"]))
        names = [f"{k[1]} ({k[0]})" for k in groups]
        lo = [min(v) for v in groups.values()]
        hi = [max(v) for v in groups.values()]
        y = np.arange(len(names))
        for i in range(len(names)):
            ax.barh(y[i], hi[i] - lo[i], left=lo[i], height=0.55,
                    color=ACC if "t_burn" == names[i] or "v_esc" == names[i]
                    else ACC2, ec=GRAY, lw=0.3, alpha=0.85)
        ax.set_yticks(y)
        ax.set_yticklabels(names, fontsize=6.0)
        ax.axvline(0, color=GRAY, lw=0.6)
        ax.set_xlabel("被击落概率变化（参数 0.6×–1.4×）")
        ax.invert_yaxis()
        ax.tick_params(axis="y", labelsize=5.6)
        ax.set_title("OAT 敏感性（红=能量类，蓝=机动类）", fontsize=7)

    ax = fig.add_subplot(gs[0, 1])
    panel_tag(ax, "b")
    if rows:
        sub = [r for r in rows if r["knob"] == "omega"]
        sub.sort(key=lambda r: float(r["value"]))
        x = [float(r["value"]) * 180 / math.pi for r in sub]
        y = [float(r["kill_rate"]) for r in sub]
        ax.plot(x, y, "o-", color=ACC, ms=3.2, lw=1.0)
        ax.set_xlabel("来袭弹最大角速度 ω / (°/s)")
        ax.set_ylabel("被击落概率", labelpad=2)
        ax.axhline(0.5, color=LIGHT, lw=0.6, ls=":")
        ax.annotate("过载悬崖", xy=(x[-2], y[-2]), xytext=(x[0], 0.85),
                    fontsize=6, color=ACC,
                    arrowprops=dict(arrowstyle="->", lw=0.5, color=ACC))
        ax.set_title("垂直扭的有效性取决于对手过载极限", fontsize=7)
    return fig


def fig4b():
    """单独输出「地导开火时机」面板，供效果验证文档与表格并排使用"""
    fig, ax = plt.subplots(figsize=(3.15, 2.5))
    rows = rd("d_sam_opening.csv")
    f = [float(x["fire_fraction"]) for x in rows]
    p = [float(x["p_total"]) for x in rows]
    v = [float(x["v_end_kmh"]) for x in rows]
    ax.plot(f, p, "o-", color=ACC, ms=3.0, lw=1.0)
    ax.axvline(0.6, color=ACC2, ls="--", lw=0.8)
    ax.text(0.615, 0.45, "3/5 Dmax", fontsize=5.6, color=ACC2)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("开火距离 / Dmax")
    ax.set_ylabel("综合拦截概率")
    ax2 = ax.twinx()
    ax2.plot(f, v, "s--", color=MID, ms=2.2, lw=0.7)
    ax2.set_ylabel("末端弹速 / (km/h)", color=MID, fontsize=6.2)
    ax2.tick_params(axis="y", colors=MID, labelsize=6)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(MID)
    return fig


def main():
    setup()
    print("生成插图：")
    for fn, name in ((fig2, "fig2-evasion"),
                     (fig3, "fig3-aircombat"),
                     (fig4, "fig4-altitude-sam"),
                     (fig5, "fig5-ship"),
                     (fig6, "fig6-sensitivity"),
                     (fig4b, "fig4b-sam-opening")):
        try:
            save(fn(), name)
        except Exception as e:      # 缺数据时不让整批失败
            print(f"  ! {name} 失败: {e}")


if __name__ == "__main__":
    main()
