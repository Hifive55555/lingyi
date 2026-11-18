#!/usr/bin/env python3
"""地导/雷达三态机的切换统计：raw/logs/*.err -> data/decoy_switches.csv。

为什么要单独写一个解析器：`events.py` 的规则级事件表是围绕**交战行为**
（规避、开火、发弹）设计的，三态机的"进模式 / 关雷达 / 回退"不属于交战行为，
在那边只会落成 `sam_unparsed`。这一节的结论要能回溯到某个 CSV 的某一列，
所以把这几类日志行单独抽出来。

口径：
* 一局=一次"已可加载想定"到下一局开始之间。
* `mode_in`：`[地空导弹营] <单元> 初始模式：<模式>`；
  `enter_maneuver`：`[地空导弹营] <单元> 进入机动：航向 <h>°...`；
  `radar_off`：`[地空导弹营] <单元> 雷达关（重发）`。
* 单元分类：名字里含 `雷达` 的归 `radar`（诱饵侧），含 `地空导弹`/`导弹连`/
  `导弹排` 的归 `sam`（发射车侧）。
* 只保留 `V3_*` 两个臂（双模式专项），其余臂的这三类行没有对照意义。

用法：
    python analysis/decoy_metrics.py
"""

from __future__ import annotations

import glob
import json
import os
import re

import pandas as pd

RAW = os.path.join("raw", "logs")
OUT = os.path.join("data", "decoy_switches.csv")

RE_EP = re.compile(r"已可加载想定")
RE_MODE = re.compile(r"\[地空导弹营\]\s+(.+?)\s+初始模式：(\S+)")
RE_MAN = re.compile(r"\[地空导弹营\]\s+(.+?)\s+进入机动：航向\s*(-?\d+)")
RE_ROFF = re.compile(r"\[地空导弹营\]\s+(.+?)\s+雷达关（重发）")
RE_SIMT = re.compile(r"^(\S+ \S+)")


def kind_of(unit: str) -> str:
    if "雷达" in unit:
        return "radar"
    return "sam"


def parse_file(path: str, arm: str) -> list[dict]:
    rows: list[dict] = []
    ep = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if RE_EP.search(line):
                ep += 1
                continue
            m_t = RE_SIMT.match(line)
            ts = m_t.group(1) if m_t else ""
            m = RE_MODE.search(line)
            if m:
                rows.append(dict(arm=arm, episode=ep, unit=m.group(1).strip(),
                                 kind=kind_of(m.group(1)), event="mode_in",
                                 heading="", ts=ts))
                continue
            m = RE_MAN.search(line)
            if m:
                rows.append(dict(arm=arm, episode=ep, unit=m.group(1).strip(),
                                 kind=kind_of(m.group(1)), event="enter_maneuver",
                                 heading=m.group(2), ts=ts))
                continue
            m = RE_ROFF.search(line)
            if m:
                rows.append(dict(arm=arm, episode=ep, unit=m.group(1).strip(),
                                 kind=kind_of(m.group(1)), event="radar_off",
                                 heading="", ts=ts))
    return rows


def main() -> None:
    rows: list[dict] = []
    for path in sorted(glob.glob(os.path.join(RAW, "V3_*.err"))):
        arm = os.path.basename(path)[:-4]
        rows.extend(parse_file(path, arm))
    df = pd.DataFrame(rows)
    if df.empty:
        print("没有解析到任何行")
        return
    df.to_csv(OUT, index=False, encoding="utf-8")
    print("写出 %s：%d 行" % (OUT, len(df)))

    # 一局内同一单元的"进入机动"按局去重（同一局里重复刷的行只算一次切换）
    sw = df[df.event == "enter_maneuver"].drop_duplicates(
        subset=["arm", "episode", "unit"])
    print("\n自动切换到机动：按 (臂, 局, 单元) 去重")
    for arm, g in sw.groupby("arm"):
        n_ep = g.episode.nunique()
        print("  %-18s %3d 次 / %d 局（%.1f 次每局）  单元 %d 个：%s" % (
            arm, len(g), n_ep, len(g) / n_ep, g.unit.nunique(),
            ", ".join(sorted(g.unit.unique()))))
        by_kind = g.groupby("kind").size().to_dict()
        print("      按类：%s" % by_kind)

    print("\n初始模式（每局一次的快照）")
    mi = df[df.event == "mode_in"].drop_duplicates(
        subset=["arm", "episode", "unit"])
    for arm, g in mi.groupby("arm"):
        print("  %-18s %s" % (arm, g.groupby("mode").size().to_dict()
                               if "mode" in g else
                               g.unit.map(kind_of).value_counts().to_dict()))

    print("\n航向分布（向南=180）")
    print(sw.groupby(["kind", "heading"]).size().to_dict())


if __name__ == "__main__":
    main()
