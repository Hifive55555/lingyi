#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图 1 人机协同总体架构图（重画版）
================================
输出：figures/fig1-architecture.{svg,png,pdf}  （覆盖旧的两面板架构图）
      figures/fig1b-evade-fsm.{svg,png,pdf}     （旧面板 b 的单体状态机，移到正文 2.3.2 节）

图契约
  核心结论：人机协同不是一个界面加一个脚本，而是**一份共享态势 + 两条视图 + 两条控制回路**。
           信息流单向自上而下（仿真 → 态势 → 后端 → 双视图），控制流旁路后端直插仿真内核。
  三条协同轴在图上各有落点：
    ① 决策协同 —— 人类操作手经“监听智能体（专用端口）”下发指令；决策智能体直接下发。
    ② 设计协同 —— 人类自然语言描述 → 想定编辑智能体 → .scen → 加载进仿真层。
    ③ 视图协同 —— 后端态势同时喂给“智能体视图（决策智能体）”与“人类视图（悬浮小窗）”。
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
FIG = os.path.join(PAPER, "figures")

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")

INK = "#1f2937"
MUTE = "#6b7280"
FAINT = "#9ca3af"

# 智能体侧（冷）、人类侧（暖）、共享底座（中性）、强调（蓝）
A_FILL, A_EDGE = "#eef3fb", "#4a6fa5"
H_FILL, H_EDGE = "#fdf2e9", "#c07a3a"
N_FILL, N_EDGE = "#f4f5f7", "#7c8593"
K_FILL, K_EDGE = "#e4ecfb", "#3370ff"
SIM_FILL, SIM_EDGE = "#ffffff", "#1f2937"
CTRL = "#b3261e"
C_FILL = "#fbeeee"


def setup():
    if os.path.exists(CJK):
        mpl.font_manager.fontManager.addfont(CJK)
        mpl.rcParams["font.family"] = ["Source Han Sans"]
    mpl.rcParams.update({
        "font.size": 7,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "savefig.dpi": 600,
        "text.color": INK,
    })


def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"),
                    bbox_inches="tight", pad_inches=0.04, transparent=False,
                    facecolor="white")


# ----------------------------------------------------------------- 绘图元件
def box(ax, x0, y0, x1, y1, text, fill, edge, size=7.2, weight="normal",
        lw=0.85, r=0.9, ls="-", color=None, valign="center"):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=lw, edgecolor=edge, facecolor=fill, linestyle=ls, zorder=2))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va=valign,
            fontsize=size, color=color or INK, weight=weight, zorder=3,
            linespacing=1.45)


def arrow(ax, x0, y0, x1, y1, color=MUTE, lw=0.8, ls="-", head=3.2, zorder=1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=f"-|>,head_width={head/12},head_length={head/9}",
                                color=color, linewidth=lw, linestyle=ls,
                                shrinkA=0, shrinkB=0), zorder=zorder)


def elbow(ax, pts, color=MUTE, lw=0.8, ls="-", head=3.2):
    """折线 + 末端箭头。pts 为 [(x,y), ...]，最后一段画箭头。"""
    for (x0, y0), (x1, y1) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, zorder=1,
                solid_capstyle="round")
    arrow(ax, *pts[-2], *pts[-1], color=color, lw=lw, ls=ls, head=head)


def tag(ax, x, y, label, color=INK):
    ax.text(x, y, label, fontsize=6.4, color=color, ha="center", va="center",
            style="italic", zorder=4)


def marker(ax, x, y, num, color):
    """①②③ 协同轴标号：小圆圈 + 数字。"""
    ax.scatter([x], [y], s=46, facecolor="white", edgecolor=color,
               linewidth=0.7, zorder=5)
    ax.text(x, y - 0.15, num, fontsize=5.6, color=color, ha="center",
            va="center", zorder=6, weight="bold")


# ----------------------------------------------------------------- 主图
def fig_architecture():
    fig, ax = plt.subplots(figsize=(7.4, 8.35))
    ax.set_xlim(-7, 105)
    ax.set_ylim(-25, 100)
    ax.axis("off")

    # ============ ② 设计协同：想定的来源 ============
    tag(ax, 50, 98.6, "② 设计协同 —— 战场的来源", MUTE)

    box(ax, 6, 89.5, 40, 96.4, "人类：中文作战场景描述", H_FILL, H_EDGE, size=7)
    box(ax, 44, 89.5, 76, 96.4,
        "想定编辑智能体\nNL → 规格 IR → Lua → .scen", A_FILL, A_EDGE, size=7)
    box(ax, 80, 89.5, 94, 96.4, ".scen", N_FILL, N_EDGE, size=7)
    arrow(ax, 40, 92.95, 44, 92.95, A_EDGE)
    arrow(ax, 76, 92.95, 80, 92.95, A_EDGE)

    # ============ 仿真层 ============
    box(ax, 20, 79.6, 80, 87.2,
        "仿真层（灵弈推演内核）\n时间推进 · 交战裁决 · 单元状态", SIM_FILL,
        SIM_EDGE, size=7.6, weight="bold", lw=1.2)
    arrow(ax, 87, 89.5, 87, 87.2, MUTE, ls=(0, (4, 2)))
    ax.text(88.8, 88.3, "加载", fontsize=6.4, color=MUTE, ha="left", va="center")

    # ============ 态势智能体 ============
    box(ax, 20, 66.0, 80, 74.6,
        "态势智能体（物理作战域三维监控）\n全量态势一次抽取 · 结构化",
        A_FILL, A_EDGE, size=7.4)
    arrow(ax, 50, 79.6, 50, 74.6, A_EDGE)
    ax.text(52.4, 77.0, "全量态势", fontsize=6.4, color=MUTE, ha="left", va="center")

    # ============ 后端态势：唯一真源 ============
    box(ax, 20, 52.2, 80, 60.8,
        "后端态势（唯一真源）\n人机共视同一份局面", K_FILL, K_EDGE, size=7.6,
        weight="bold", lw=1.15)
    arrow(ax, 50, 66.0, 50, 60.8, A_EDGE)
    ax.text(52.4, 63.2, "写入", fontsize=6.4, color=MUTE, ha="left", va="center")

    # ============ ③ 视图协同：两个分叉 ============
    tag(ax, 50, 48.3, "③ 视图协同 —— 同一份局面，两种粒度", MUTE)

    # 分叉主箭头
    elbow(ax, [(50, 52.2), (50, 50.4), (27, 50.4), (27, 46.6)], A_EDGE)
    elbow(ax, [(50, 52.2), (50, 50.4), (73, 50.4), (73, 44.8)], H_EDGE)

    # ---- 左：智能体视图 ----
    ax.text(27, 44.2, "智能体视图：全部细节", fontsize=6.8, color=A_EDGE,
            ha="center", va="center", weight="bold", zorder=3)
    agents = ["空战单元自卫（飞机）", "空空作战（战斗机）",
              "地空导弹营攻击与自卫（防空）", "登陆船只集群自卫（舰船）"]
    y = 37.2
    for name in agents:
        box(ax, 6, y, 48, y + 4.3, name, A_FILL, A_EDGE, size=6.8, r=0.7)
        y -= 5.1
    ax.text(27, 9.4, "四域互不相交，只读后端", fontsize=6.2, color=MUTE,
            ha="center", va="center", style="italic")
    # 左侧回流箭头起点（后面统一画）

    # ---- 右：人类视图 ----
    ax.text(73, 44.2, "人类视图：宏观收敛", fontsize=6.8, color=H_EDGE,
            ha="center", va="center", weight="bold", zorder=3)
    box(ax, 56, 32.4, 90, 41.4,
        "前端悬浮小窗\n上下文收紧：只留可决策的少数项\n封装操作按钮：看到即可下令",
        H_FILL, H_EDGE, size=6.9)
    box(ax, 56, 21.4, 90, 28.6, "人类操作手\n（选轴线 · 定优先级 · 放弃区域）",
        H_FILL, H_EDGE, size=6.9)
    arrow(ax, 73, 32.4, 73, 28.6, H_EDGE)
    ax.text(74.6, 30.5, "看", fontsize=6.4, color=MUTE, ha="left", va="center")

    # ============ ① 决策协同：两条控制回路 ============
    box(ax, 56, 10.4, 90, 18.0,
        "监听智能体（专用端口）\n常驻监听人类响应 · 转译为平台指令",
        C_FILL, CTRL, size=6.9, lw=1.0)
    arrow(ax, 73, 21.4, 73, 18.0, CTRL)
    ax.text(74.6, 19.7, "人类指令", fontsize=6.4, color=CTRL, ha="left", va="center")

    # 智能体指令：四域各引一条短线汇入左侧汇流线，再上插仿真层
    for cy in (39.35, 34.25, 29.15, 24.05):
        ax.plot([6, 4.2], [cy, cy], color=A_EDGE, lw=0.85, zorder=1)
    ax.plot([4.2, 4.2], [24.05, 83.4], color=A_EDGE, lw=0.85, zorder=1)
    arrow(ax, 4.2, 83.4, 20, 83.4, A_EDGE, lw=0.85)
    ax.text(1.5, 53.7, "智能体指令", fontsize=6.4, color=A_EDGE,
            ha="center", va="center", rotation=90)

    # 人类指令：监听智能体上行，沿右侧回插仿真层
    elbow(ax, [(90, 14.2), (96.6, 14.2), (96.6, 83.4), (80, 83.4)], CTRL,
          lw=0.85)
    ax.text(98.2, 51.5, "人类指令", fontsize=6.4, color=CTRL,
            ha="center", va="center", rotation=90)

    tag(ax, 73, 6.9, "① 决策协同 —— 指令经专用端口回插内核", CTRL)

    # ============ 横向图例 ============
    ax.plot([6, 11], [-24.2, -24.2], color=A_EDGE, lw=0.85)
    ax.text(11.9, -24.2, "信息流", fontsize=6.2, color=MUTE, va="center")
    ax.plot([21, 26], [-24.2, -24.2], color=CTRL, lw=0.85)
    ax.text(26.9, -24.2, "控制流（旁路后端，直插内核）", fontsize=6.2,
            color=MUTE, va="center")
    ax.plot([6, 11], [-21.6, -21.6], color=MUTE, lw=0.85, ls=(0, (4, 2)))
    ax.text(11.9, -21.6, "对局之外的批次回路", fontsize=6.2, color=MUTE, va="center")

    # ============ ④ 参数演化环 / ⑤ 双轨评估环（对局之外） ============
    tag(ax, 50, -2.4, "对局之外：一条批次回路", MUTE)

    # 左：④ 参数演化环
    box(ax, 4, -14.6, 48, -5.2,
        "④ 参数演化环（平台批量对局）\n单因子扫描 → 坐标上升 → θ 候选\n一圈只筛出坏方向，不做寻优",
        E_FILL if "E_FILL" in globals() else A_FILL,
        A_EDGE, size=6.8, lw=1.0)
    # 右：⑤ 双轨评估环
    box(ax, 54, -14.6, 96, -5.2,
        "⑤ 双轨评估环\n规则级读数 + 结局区间\n稳健性分级：可分辨 / 只报方向 / 不可分辨",
        K_FILL, K_EDGE, size=6.8, lw=1.0)

    # 智能体四域 → ④：把 θ 交出去
    arrow(ax, 27, 8.4, 27, -5.2, A_EDGE, lw=0.85, ls=(0, (4, 2)))
    ax.text(28.6, 1.2, "可调参数 θ", fontsize=6.2, color=MUTE,
            ha="left", va="center", rotation=90)

    # ④ → ⑤：候选与结局
    arrow(ax, 48, -9.9, 54, -9.9, A_EDGE, lw=0.85)
    ax.text(51, -8.4, "候选 · 结局", fontsize=6.1, color=MUTE,
            ha="center", va="center")

    # ⑤ → ①：结论与下一批取值回插
    elbow(ax, [(96, -17.2), (101.6, -17.2), (101.6, 83.4), (80, 83.4)], MUTE,
          lw=0.85, ls=(0, (4, 2)))

    ax.set_aspect("equal")
    return fig


# ----------------------------------------------------------------- 旧面板 b
def fig_evade_fsm():
    """原图 1(b)：空战单元自卫的单体状态机。移入 2.3.2 节。"""
    fig, ax = plt.subplots(figsize=(4.6, 3.15))
    ax.set_xlim(-4, 112)
    ax.set_ylim(28, 96)
    ax.axis("off")

    def node(x0, y0, x1, y1, text, dim=False):
        box(ax, x0, y0, x1, y1, text,
            "#f2f2f3" if dim else "#f8f8f9",
            "#a4a9b2" if dim else "#7c8593",
            size=6.5, r=1.4, lw=0.8)

    node(8, 80, 40, 91, "巡航")
    node(54, 80, 86, 91, "迎头接近")
    node(54, 58, 86, 69, "尾追逃逸")
    node(54, 34, 86, 45, "垂直扭动")
    node(8, 34, 40, 45, "反打")
    node(88, 58, 110, 69, "被击落", dim=True)

    # 巡航 → 迎头接近
    arrow(ax, 40, 85.5, 54, 85.5, MUTE)
    ax.text(47, 93.4, "发现来袭弹", fontsize=5.6, color=MUTE,
            ha="center", va="center")

    # 迎头接近 → 尾追逃逸
    arrow(ax, 70, 80, 70, 69, MUTE)
    ax.text(71.6, 74.6, "d ≤ d_turn（随弹速）", fontsize=5.6, color=MUTE,
            ha="left", va="center")

    # 尾追逃逸 → 垂直扭动
    arrow(ax, 70, 58, 70, 45, CTRL)
    ax.text(71.6, 51.5, "d ≤ 20 km 且 V弹 > V我", fontsize=5.8, color=CTRL,
            ha="left", va="center")

    # 垂直扭动 → 反打
    arrow(ax, 54, 39.5, 40, 39.5, CTRL)
    ax.text(47, 41.6, "V弹 < 500", fontsize=5.6, color=CTRL,
            ha="center", va="center")

    # 反打 → 巡航（左缘回流）
    elbow(ax, [(8, 39.5), (1.0, 39.5), (1.0, 85.5), (8, 85.5)], MUTE)
    ax.text(-1.6, 62.5, "再次接敌", fontsize=5.8, color=MUTE,
            ha="center", va="center", rotation=90)

    # 尾追逃逸 → 被击落（虚线）
    arrow(ax, 86, 63.5, 88, 63.5, MUTE, ls=(0, (3.4, 1.8)))
    ax.text(87, 55.2, "始终不规避", fontsize=5.2, color=MUTE,
            ha="center", va="center", style="italic")

    ax.set_aspect("equal")
    return fig


if __name__ == "__main__":
    setup()
    save(fig_architecture(), "fig1-architecture")
    save(fig_evade_fsm(), "fig1b-evade-fsm")
    print("wrote fig1-architecture.* / fig1b-evade-fsm.*")
