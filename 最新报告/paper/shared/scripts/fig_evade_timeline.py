#!/usr/bin/env python
"""图：一次交会 —— 距离、判定距离，以及"被当成威胁"与"开始规避"两个时刻。

单位修正：pi_tap 早批次把速度多乘了 1.852（平台给的就是 km/h），本脚本按 /1.852 还原；
还原后弹速 451 km/h、判定距离 82 km 与智能体日志的读数一致，可交叉验证。

输出：paper/shared/figures/fig_evade_timeline.{png,svg}
"""
import json
import math
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # 统一配色与排版（唯一色源）

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
FIG = "/home/hifive/School/2026latter/兵棋比赛智能体报告/最新报告/paper/shared/figures"
TAP = "/tmp/S5_TL2__1795092074__红方.jsonl"
UNIT, MID, K = "TB2 无人机#13", "MO-00001K7PT9FC9", 1.852
T_EVADE = 361.0                         # 来自日志的规避行（t=361）
INK, MUTED, GRID = "#171b20", "#6b737d", "#e9edf1"
C1, C2, C3 = "#2b5d8f", "#b0883a", "#b23a2b"
T_X, V_TERM = 240.0, 500.0


def d0(v0, va):
    th = T_X / 3600.0
    v0 = max(v0, V_TERM + 1.0)
    return th * (v0 - va) ** 2 / (2.0 * (v0 - V_TERM)) if va >= V_TERM \
        else th * (v0 + V_TERM) / 2.0 - th * va


def km(a, b, c, d):
    return math.hypot((a - c) * 111.32, (b - d) * 111.32 * math.cos(math.radians(49.5)))


def main():
    font_manager.fontManager.addfont(CJK)
    figstyle.apply(mpl)          # 统一配色与排版（唯一色源）
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_manager.FontProperties(fname=CJK).get_name()],
        "axes.unicode_minus": False,
    })

    rows, seen, vmax = [], set(), 0.0
    for line in open(TAP, encoding="utf-8"):
        d = json.loads(line)
        t = round(d.get("t") or 0)
        me = next((u for u in (d.get("own") or []) if u[0] == UNIT), None)
        mm = next((c for c in (d.get("cts") or []) if len(c) > 7 and c[1] == MID), None)
        if not (me and mm) or t in seen:
            continue
        seen.add(t)
        vs, va = mm[6] / K, me[5] / K
        vmax = max(vmax, vs)
        rows.append((t, km(me[2], me[3], mm[3], mm[4]),
                     1.2 * d0(vs, max(va, 300.0)),
                     1.2 * d0(vmax, max(va, 300.0))))
    t = np.array([r[0] for r in rows], float)
    dist = np.array([r[1] for r in rows])
    g_now = np.array([r[2] for r in rows])
    g_rule = np.array([r[3] for r in rows])

    fig, ax = plt.subplots(figsize=(6.0, 3.05))
    fig.subplots_adjust(left=0.10, right=0.975, top=0.965, bottom=0.175)

    ax.plot(t, dist, color=C1, lw=1.8, label="导弹到无人机的距离")
    ax.plot(t, g_rule, color=C3, lw=1.8, ls=(0, (1, 1.6)),
            label="规则用的判定距离（按见过的最高弹速）")
    ax.plot(t, g_now, color=C2, lw=1.4, ls=(0, (6, 2.4)), alpha=0.95,
            label="按当帧弹速算的判定距离")

    inside = g_rule >= dist
    t_in = float(t[np.argmax(inside)]) if inside.any() else None
    # 阴影：距离已经进到门限之内、却还没被当成威胁的那一段
    if t_in:
        ax.axvline(t_in, color=C2, lw=1.0, ls=(0, (3, 3)))
        ax.annotate("第 %.0f 秒：距离已进判定距离之内" % t_in,
                    xy=(t_in, g_rule[int(np.argmax(inside))]), xytext=(t_in - 92, 168),
                    fontsize=7.0, color=C2,
                    arrowprops=dict(arrowstyle="-|>", color=C2, lw=0.8, shrinkA=2, shrinkB=3))
    ax.axvspan(t_in, T_EVADE, color=C2, alpha=0.07, lw=0)
    ax.text((t_in + T_EVADE) / 2, 120, "这 164 秒里距离都够近，\n但还没被判定为“冲本机来”",
            fontsize=6.6, color=MUTED, ha="center")
    ax.axvline(T_EVADE, color=C3, lw=1.3)
    ax.annotate("第 %.0f 秒：开始规避\n（距离 30 km，判定距离 81 km）" % T_EVADE,
                xy=(T_EVADE, 30), xytext=(T_EVADE - 108, 46), fontsize=7.0, color=C3,
                arrowprops=dict(arrowstyle="-|>", color=C3, lw=0.8, shrinkA=2, shrinkB=3))

    ax.set_xlim(t[0], t[-1] + 8)
    ax.set_ylim(0, 190)
    ax.set_xlabel("推演时间 / s", labelpad=3)
    ax.set_ylabel("距离 / km", labelpad=3)
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2, pad=2, colors=MUTED, labelcolor=INK)
    ax.legend(loc="lower left", fontsize=6.6, frameon=False, handlelength=1.9,
              bbox_to_anchor=(0.005, 0.02))

    fig.savefig(FIG + "/fig_evade_timeline.png", dpi=600, facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    fig.savefig(FIG + "/fig_evade_timeline.svg", facecolor="white",
                bbox_inches="tight", pad_inches=0.02)
    print("帧 %d；末帧 距离 %.1f 判定 %.1f/规则 %.1f" %
          (len(t), dist[-1], g_now[-1], g_rule[-1]))


if __name__ == "__main__":
    main()
