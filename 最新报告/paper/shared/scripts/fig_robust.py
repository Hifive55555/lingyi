"""第 8 章新增面板：模型形式的两处稳健性检验。

fig7-robustness
  (a) 船只：9 组概率曲线形状下 R 与 B3 的拦截率与平均拦截距离
  (b) 船只：弹舱容量 K 对四个方案拦截率的影响
  (c) 地导：最优点随弹速与能量裕度系数 c 漂移
"""
from __future__ import annotations

import collections
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figures import ACC, ACC2, MID, GRAY, LIGHT, panel_tag, rd, save, setup  # noqa: E402


def fig7():
    setup()
    fig = plt.figure(figsize=(7.1, 2.55))
    gs = fig.add_gridspec(1, 3, width_ratios=(1.0, 1.0, 1.15), wspace=0.42)

    # ---------------- (a) 概率曲线形状
    ax = fig.add_subplot(gs[0])
    rows = rd("c_ship_probshape.csv")
    keys = sorted({(float(r["p_far"]), float(r["p_near"])) for r in rows})
    R = {k: next(float(r["intercept_rate"]) for r in rows
                 if (float(r["p_far"]), float(r["p_near"])) == k and r["scheme"].startswith("R"))
         for k in keys}
    B3 = {k: next(float(r["intercept_rate"]) for r in rows
                  if (float(r["p_far"]), float(r["p_near"])) == k and r["scheme"].startswith("B3"))
          for k in keys}
    x = np.arange(len(keys))
    ax.bar(x - 0.19, [R[k] for k in keys], 0.36, color=ACC, label="R 双舰分层")
    ax.bar(x + 0.19, [B3[k] for k in keys], 0.36, color=LIGHT, edgecolor=GRAY,
           linewidth=0.4, label="B3 双舰均半射程")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(a*100)}/{int(b*100)}" for a, b in keys], fontsize=5.2, rotation=90)
    ax.set_xlabel("远端 / 近端单发概率（%）")
    ax.set_ylabel("拦截率（8 枚来袭）")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.085), ncol=2,
              handlelength=1.2, columnspacing=1.0)
    panel_tag(ax, "a")
    note = f"B3>$R$：{sum(1 for k in keys if B3[k] > R[k])}/{len(keys)}"
    ax.text(0.03, 0.94, note, transform=ax.transAxes, fontsize=6, color=GRAY, va="top")

    # ---------------- (b) 弹舱
    ax2 = fig.add_subplot(gs[1])
    rows = rd("c_ship_magazine.csv")
    Ks = sorted({int(r["magazine"]) for r in rows})
    style = {"R 双舰分层": (ACC, "o-"), "B1 单舰双层": (MID, "s--"),
             "B2 双舰同时MAX": (LIGHT, "^:"), "B3 双舰均½Dmax": (ACC2, "d-.")}
    for name, (c, m) in style.items():
        ys = [next(float(r["intercept_rate"]) for r in rows
                   if int(r["magazine"]) == k and r["scheme"] == name) for k in Ks]
        ax2.plot(Ks, ys, m, color=c, ms=3, label=name.split(" ")[0] if name.startswith("R") else name)
    ax2.set_xlabel("每舰弹舱 K（枚）")
    ax2.set_ylabel("拦截率（8 枚来袭）")
    ax2.set_xticks(Ks)
    ax2.set_ylim(0, 1.02)
    ax2.legend(loc="lower right", fontsize=5.6, handlelength=1.6)
    panel_tag(ax2, "b")

    # ---------------- (c) 地导最优点漂移
    ax3 = fig.add_subplot(gs[2])
    rows = rd("d_sam_margin.csv")
    by = collections.defaultdict(dict)
    for r in rows:
        by[(float(r["v0"]), float(r["c_margin"]))][float(r["fire_fraction"])] = float(r["p_total"])
    cs = sorted({float(r["c_margin"]) for r in rows})
    v0s = sorted({float(r["v0"]) for r in rows})
    cols = {2500.0: MID, 3000.0: ACC, 3500.0: ACC2}
    for v0 in v0s:
        best = [max(by[(v0, c)], key=by[(v0, c)].get) for c in cs]
        ax3.plot(cs, best, "o-", ms=3.2, color=cols[v0], label=f"$V_0$ = {int(v0)} km/h")
    ax3.axvline(0.6, color=GRAY, ls="--", lw=0.7)
    ax3.text(0.405, 0.172, "本文取值 c = 0.6", fontsize=5.8, color=GRAY)
    ax3.axhline(0.6, color=ACC, ls=":", lw=0.8)
    ax3.text(0.395, 0.645, "讲解取值 0.6$D_{max}$", fontsize=5.8, color=ACC)
    ax3.set_xlabel("能量裕度分母系数 c")
    ax3.set_ylabel("最优开火比例 / $D_{max}$")
    ax3.set_xticks(cs)
    ax3.set_yticks([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
    ax3.set_ylim(0.15, 0.75)
    ax3.legend(loc="upper left", bbox_to_anchor=(0.0, 0.63), fontsize=5.8, handlelength=1.6)
    panel_tag(ax3, "c", dx=-0.16)

    save(fig, "fig7-robustness")


if __name__ == "__main__":
    fig7()
