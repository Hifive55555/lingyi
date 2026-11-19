#!/usr/bin/env python
"""图：各配置空战开火时的发射距离分布（与规避比值图同一套画法）。

竖箱线：箱体四分位区间、箱内横线中位数、须线 1.5 倍四分位距；
深色为 v2 批次，红虚线为该型弹射程的七成 77.8 km。

数据：最新报告/实验v2/data/events.csv 的 fire_aam（dist_km）。
"""
import collections
import csv
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager

CJK = ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
       "/share/fonts/truetype/SourceHanSans.ttc")
BASE = "/home/hifive/School/2026latter/兵棋比赛智能体报告/最新报告"
EVENTS = os.path.join(BASE, "实验v2", "data", "events.csv")
OUT = os.path.join(BASE, "paper", "shared", "figures")
CAP = 77.8
SHORT = {"V2_A0_new": "A0 新规则(v2)", "V2_A1_old": "A1 旧规则(v2)",
         "V2_B1_evade50": "B1(v2)", "V2_C1_kturn08": "C1(v2)", "V2_C2_kturn16": "C2(v2)",
         "V2_WA_f08": "WA(v2)", "V2_WB_f06": "WB(v2)", "V2_WC_f10": "WC(v2)",
         "V2_WD_fix111": "WD(v2)", "V2_E1_sam03": "E1(v2)", "V2_E2_sam10": "E2(v2)",
         "V2_F1_nolayer": "F1(v2)"}
ORDER = ["V2_A0_new", "V2_A1_old", "V2_B1_evade50", "V2_C1_kturn08", "V2_C2_kturn16",
         "V2_WA_f08", "V2_WB_f06", "V2_WC_f10", "V2_WD_fix111", "V2_E1_sam03",
         "V2_E2_sam10", "V2_F1_nolayer"]


def main():
    font_manager.fontManager.addfont(CJK)
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_manager.FontProperties(fname=CJK).get_name()],
        "axes.unicode_minus": False, "svg.fonttype": "path",
    })
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(EVENTS, encoding="utf-8")):
        if r["event"] == "fire_aam" and r.get("dist_km"):
            by[r["arm"]].append(float(r["dist_km"]))
    arms = [a for a in ORDER if len(by.get(a, [])) >= 20]

    fig, ax = plt.subplots(figsize=(7.6, 3.8), dpi=300)
    bp = ax.boxplot([by[a] for a in arms], widths=.55, showfliers=False, patch_artist=True,
                    medianprops=dict(color='#171b20', lw=1.2))
    for i, p in enumerate(bp['boxes']):
        p.set_facecolor('#1f3b5c' if arms[i].startswith('V2_') or arms[i] == 'A0_new' else '#c9d4e4')
        p.set_edgecolor('#6b737d')
    ax.axhline(CAP, color='#b23a2b', lw=1.0, ls='--')
    ax.set_xlim(0.4, len(arms) + 1.5)
    ax.text(len(arms) + 0.6, CAP, '射程七成\n77.8 km', color='#b23a2b', fontsize=7,
            va='center', ha='left')
    ax.set_xticks(range(1, len(arms) + 1))
    ax.set_xticklabels([SHORT.get(a, a) for a in arms], rotation=35, ha='right', fontsize=7)
    ax.set_ylabel('开火距离 / km')
    ax.set_title('空战开火距离分布（红虚线为射程七成）')
    ax.grid(alpha=.25, axis='y')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig_fire_dist.png'))
    fig.savefig(os.path.join(OUT, 'fig_fire_dist.svg'))
    plt.close(fig)
    for a in arms:
        print('%-14s n=%4d 中位 %.1f' % (a, len(by[a]), sorted(by[a])[len(by[a]) // 2]))


if __name__ == '__main__':
    main()
