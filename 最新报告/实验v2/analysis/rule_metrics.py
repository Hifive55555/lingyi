#!/usr/bin/env python3
"""规则级指标：data/events.csv -> data/rule_metrics.csv + data/rule_metrics.md。

口径（详见 analysis/README.md 的「规则级事件抽取」一节）：

* **抽样单位是「局」**，不是事件。所有 mean/ci 都按局聚合：每个指标先在局内求值，
  再对局做 bootstrap（`n_boot=1000`、种子 `20261118`，与 `metrics.py` 同口径）。
  分布类指标的 `p10/p50/p90` 是**池化到事件**后的分位数（即「所有触发点的分布」）。
* `ratio_gate = dist/gate` 是**规则自身的判据比值**，不依赖任何 θ，可跨臂直接比。
* 规避事件的 `evade_phase=start` 才是规则真正触发的时刻；`replot` 是同一段规避里
  每 30 s 一次的重画航线，dist 已经更小，**不能**混进触发分布。

用法：
    python analysis/rule_metrics.py                 # data/events.csv -> data/rule_metrics.{csv,md}
    python analysis/rule_metrics.py --events /tmp/e.csv --out-csv /tmp/r.csv --out-md /tmp/r.md
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

N_BOOT = 1000
SEED = 20261118
BASE_ARM = "A0_new"

# 指标表：name -> (kind, event 过滤, 取值列或计数名, 单位)
#   kind = "dist"  取该事件集合某一列的分布
#   kind = "count" 取该事件集合在每局内的出现次数
#   kind = "frac"  取该事件集合在每局内的比例（分母 = 该集合内非空的取值数）
METRICS = [
    # -- 规模 -----------------------------------------------------------------
    ("episodes_loaded", "arm", None, None, "局"),
    ("episodes_stepped", "arm", None, None, "局"),
    # -- 规避 ---------------------------------------------------------------
    ("evade_start_count", "count", ("event", "evade_beam", "evade_phase", "start"), None, "次/局"),
    ("evade_replot_count", "count", ("event", "evade_beam", "evade_phase", "replot"), None, "次/局"),
    ("evade_end_count", "count", ("event", "evade_end", None, None), None, "次/局"),
    ("threat_count", "count", ("event", "threat", None, None), None, "条/局"),
    ("evade_start_ratio_gate", "dist", ("event", "evade_beam", "evade_phase", "start"), "ratio_gate", "ratio"),
    ("evade_start_dist_km", "dist", ("event", "evade_beam", "evade_phase", "start"), "dist_km", "km"),
    ("evade_start_gate_km", "dist", ("event", "evade_beam", "evade_phase", "start"), "gate_km", "km"),
    ("evade_start_gap_km", "dist", ("event", "evade_beam", "evade_phase", "start"), "gap_km", "km"),
    ("evade_start_speed_kmh", "dist", ("event", "evade_beam", "evade_phase", "start"), "speed_kmh", "km/h"),
    ("evade_start_frac_inside_gate", "frac", ("event", "evade_beam", "evade_phase", "start"),
     "is_inside_gate", ""),
    ("evade_start_frac_deep_half", "frac", ("event", "evade_beam", "evade_phase", "start"),
     "is_deep_half", ""),
    ("evade_start_frac_override", "frac", ("event", "evade_beam", "evade_phase", "start"),
     "is_override", ""),
    # -- 空战开火 -----------------------------------------------------------
    ("fire_aam_count", "count", ("event", "fire_aam", None, None), None, "次/局"),
    ("fire_aam_ratio_d0", "dist", ("event", "fire_aam", None, None), "ratio_d0", "ratio"),
    # -- 地导 ---------------------------------------------------------------
    ("sam_fire_count", "count", ("event", "sam_fire", None, None), None, "次/局"),
    ("sam_fire_rejected_count", "count", ("event", "sam_fire_rejected", None, None), None, "次/局"),
    ("sam_intercept_count", "count", ("event", "sam_intercept", None, None), None, "次/局"),
    ("sam_radar_off_count", "count", ("event", "sam_radar_off", None, None), None, "次/局"),
    ("sam_radar_on_count", "count", ("event", "sam_radar_on", None, None), None, "次/局"),
    ("sam_standby_count", "count", ("event", "sam_standby", None, None), None, "条/局"),
    ("sam_fire_ratio_dmax", "dist", ("event", "sam_fire", None, None), "ratio_dmax", "ratio"),
    ("sam_fire_ratio_gate", "dist", ("event", "sam_fire", None, None), "ratio_gate", "ratio"),
    ("sam_fire_dist_km", "dist", ("event", "sam_fire", None, None), "dist_km", "km"),
    # -- 舰船 ---------------------------------------------------------------
    ("ship_defense_count", "count", ("event", "ship_defense", None, None), None, "次/局"),
]


def _select(events, spec):
    """按 (列, 值, 列, 值) 过滤事件表。"""
    col1, val1, col2, val2 = spec
    df = events
    if col1 is not None:
        df = df[df[col1] == val1]
    if col2 is not None:
        df = df[df[col2] == val2]
    return df


def _bootstrap_mean(groups, n_boot=N_BOOT, seed=SEED):
    """按局（cluster）重采样的 bootstrap 区间：重采样局，再池化其全部事件求均值。"""
    rng = np.random.default_rng(seed)
    arrays = [g for g in groups if len(g)]
    if not arrays:
        return (np.nan, np.nan)
    k = len(arrays)
    vals = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, k, k)
        pool = np.concatenate([arrays[i] for i in pick])
        vals[b] = pool.mean() if len(pool) else np.nan
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return (float(lo), float(hi))


def _summarise(name, unit, per_episode_values, pooled, n_episodes, n_events, total,
               percentiles=True):
    pooled = np.asarray(pooled, dtype=float)
    groups = [np.asarray(v, dtype=float) for v in per_episode_values.values()]
    if pooled.size:
        mean, std = float(pooled.mean()), float(pooled.std(ddof=1)) if pooled.size > 1 else np.nan
        if percentiles:
            p10, p50, p90 = (float(x) for x in np.percentile(pooled, [10, 50, 90]))
        else:
            p10 = p50 = p90 = np.nan
    else:
        mean = std = p10 = p50 = p90 = np.nan
    lo, hi = _bootstrap_mean(groups)
    return {
        "metric": name, "unit": unit, "n_episodes": n_episodes, "n_events": n_events,
        "sum": total, "mean": mean, "std": std, "p10": p10, "p50": p50, "p90": p90,
        "ci_low": lo, "ci_high": hi,
    }


def compute_arm(arm, events):
    rows = []
    starts = events[events["event"] == "episode_start"]
    loaded = len(starts)
    stepped = starts[starts["step_index"].fillna(0) > 0]
    ep_with_steps = set(stepped["episode_idx"].astype(int))
    n_ep = len(ep_with_steps)

    for name, kind, spec, col, unit in METRICS:
        if name == "episodes_loaded":
            rows.append({"metric": name, "unit": unit, "n_episodes": loaded, "n_events": "",
                         "sum": loaded, "mean": float(loaded), "std": np.nan, "p10": np.nan,
                         "p50": np.nan, "p90": np.nan, "ci_low": np.nan, "ci_high": np.nan})
            continue
        if name == "episodes_stepped":
            rows.append({"metric": name, "unit": unit, "n_episodes": n_ep, "n_events": "",
                         "sum": n_ep, "mean": float(n_ep), "std": np.nan, "p10": np.nan,
                         "p50": np.nan, "p90": np.nan, "ci_low": np.nan, "ci_high": np.nan})
            continue

        df = _select(events, spec)
        if kind == "count":
            per_ep = df.groupby("episode_idx").size().reindex(sorted(ep_with_steps), fill_value=0)
            rows.append(_summarise(name, unit, {ep: [v] for ep, v in per_ep.items()},
                                   per_ep.values, n_ep, int(len(df)), int(len(df))))
        elif kind in ("dist", "frac"):
            df = df.assign(_v=pd.to_numeric(df[col], errors="coerce")).dropna(subset=["_v"])
            vals = df["_v"].to_numpy()
            per_ep = {int(ep): g["_v"].to_numpy() for ep, g in df.groupby("episode_idx")}
            total = float(vals.sum()) if kind == "frac" else ""
            # frac 指标的分位数没有意义（池化后只有 0/1），只报比例与按局区间
            rows.append(_summarise(name, unit, per_ep, vals, len(per_ep),
                                   int(len(vals)), total, percentiles=(kind == "dist")))
    return rows


def _read_events(path):
    events = pd.read_csv(path)
    num = ["sim_t", "step_index", "dist_km", "speed_kmh", "gate_km", "d0_km", "cpa_km",
           "tgo_s", "ratio_gate", "dmax_km", "ratio_dmax"]
    for c in num:
        events[c] = pd.to_numeric(events[c], errors="coerce")

    # 派生列（只在这里定义一次，CSV 里不落盘，保证 events.csv 保持原始粒度）
    events["gap_km"] = events["gate_km"] - events["dist_km"]
    r = events["ratio_gate"]
    events["is_inside_gate"] = (r < 1.0).astype(float).where(r.notna())
    events["is_deep_half"] = (r < 0.5).astype(float).where(r.notna())
    events["is_override"] = (r > 1.0).astype(float).where(r.notna())
    d0 = events["d0_km"]
    events["ratio_d0"] = (events["dist_km"] / d0).where(d0 > 0)
    return events


def _fmt(x, nd=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if x == "":
        return "—"
    return ("%." + str(nd) + "f") % x


def _cell(kind, row):
    """md 单元格：count/dist 报「均值 [P10–P90]」，frac 报「比例（分母）」。"""
    if row is None:
        return "—"
    if kind == "frac":
        if not row["n_events"]:
            return "不可得"
        return "%s（分母 %d）" % (_fmt(row["mean"]), int(row["n_events"]))
    if kind == "dist" and not row["n_events"]:
        return "不可得"
    nd = 2 if kind == "count" else 3
    return "%s [%s–%s]" % (_fmt(row["mean"], nd), _fmt(row["p10"], 1 if kind == "count" else 3),
                           _fmt(row["p90"], 1 if kind == "count" else 3))


def write_md(summary, arms, path, n_note):
    lines = []
    lines.append("# 规则级指标对比（自动生成，勿手改）")
    lines.append("")
    lines.append("生成命令：`python analysis/rule_metrics.py`（输入 `data/events.csv`）。")
    lines.append("口径与近似项见 `analysis/README.md`「规则级事件抽取」一节。")
    lines.append("")
    lines.append(n_note)
    lines.append("")
    lines.append("## 1. 各臂并排（`均值 [P10–P90]`；分位数池化到事件，次数类为每局计数）")
    lines.append("")
    lines.append("比例类指标写作 `比例（分母=可用于判定的触发数）`。"
                 "均值与差值的 95% 区间按局 bootstrap（`n_boot=1000`，种子 `20261118`），"
                 "见 `data/rule_metrics.csv` 的 `ci_low/ci_high`。")
    lines.append("")
    order = [m for m, *_ in METRICS]
    units = {m: u for m, _, _, _, u in METRICS}
    kinds = {m: k for m, k, _, _, _ in METRICS}
    header = "| 指标 | 单位 | " + " | ".join(arms) + " |"
    lines.append(header)
    lines.append("| --- | --- | " + " | ".join("---" for _ in arms) + " |")
    for m in order:
        cells = []
        for a in arms:
            row = summary.get((a, m))
            if row is not None and m in ("episodes_loaded", "episodes_stepped"):
                cells.append(str(int(row["mean"])))
            else:
                cells.append(_cell(kinds[m], row))
        lines.append("| `%s` | %s | %s |" % (m, units[m] or "—", " | ".join(cells)))
    lines.append("")

    lines.append("## 2. 与 `%s` 的差" % BASE_ARM)
    lines.append("")
    lines.append("`噪声` = `|Δ| ≤ A0 自身 std`（同配置重复的带宽，见《实验设计》§4.3）；"
                 "`可分辨` = 超出该带宽。**方向是否与先验一致**要按《实验设计》§3.2 "
                 "逐条判读——本表只给差值与噪声判定，不替你判方向。")
    lines.append("")
    if len(arms) < 2:
        lines.append("当前快照只有 **%d** 个臂（`%s`），因此没有可比较的差；"
                     "批量实验补齐 `.err` 后重跑本脚本即可自动填表。" % (len(arms), ", ".join(arms)))
    else:
        others = [a for a in arms if a != BASE_ARM]
        lines.append("| 指标 | A0 自身 std | " + " | ".join(others) + " |")
        lines.append("| --- | --- | " + " | ".join("---" for _ in others) + " |")
        base = summary
        for m in order:
            if m in ("episodes_loaded", "episodes_stepped"):
                continue
            cells = []
            b0 = base.get((BASE_ARM, m))
            cells.append(_fmt(b0["std"], 3) if b0 is not None else "—")
            for a in others:
                x = base.get((a, m))
                if b0 is None or x is None or np.isnan(b0["mean"]) or np.isnan(x["mean"]):
                    cells.append("—")
                    continue
                d = x["mean"] - b0["mean"]
                sd = b0["std"]
                tag = "噪声" if (not np.isnan(sd) and abs(d) <= sd) else "可分辨"
                cells.append("%+.3f（%s）" % (d, tag))
            lines.append("| `%s` | %s |" % (m, " | ".join(cells)))
    lines.append("")
    lines.append("## 3. 不可得项")
    lines.append("")
    lines.append("见 `analysis/README.md`「规则级事件抽取 §4 不可得与近似项」：")
    lines.append("空战开火比值、舰船拦截、地导 `d0` 三项在本快照下的可用性在那里逐条说明。")
    lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description="events.csv -> rule_metrics.csv/.md")
    ap.add_argument("--events", default=os.path.join("data", "events.csv"))
    ap.add_argument("--out-csv", default=os.path.join("data", "rule_metrics.csv"))
    ap.add_argument("--out-md", default=os.path.join("data", "rule_metrics.md"))
    args = ap.parse_args(argv)

    if not os.path.exists(args.events):
        print("缺少 %s（先跑 analysis/events.py）" % args.events, file=sys.stderr)
        return 2

    events = _read_events(args.events)
    arms = list(dict.fromkeys(events["arm"].astype(str)))
    arms.sort(key=lambda a: (a != BASE_ARM, a))

    summary = {}
    records = []
    for arm in arms:
        for row in compute_arm(arm, events[events["arm"] == arm]):
            row = {"arm": arm, **row}
            summary[(arm, row["metric"])] = row
            records.append(row)

    cols = ["arm", "metric", "unit", "n_episodes", "n_events", "sum", "mean", "std",
            "p10", "p50", "p90", "ci_low", "ci_high"]
    out = pd.DataFrame(records)[cols]
    out.to_csv(args.out_csv, index=False, float_format="%.6g")

    note = ("当前数据含 %d 个臂：%s。" % (len(arms), "、".join("`%s`" % a for a in arms))
            + "臂间比较只在同一 `analysis/events.py` 口径下成立。")
    write_md(summary, arms, args.out_md, note)

    print("已写 %s（%d 行）与 %s" % (args.out_csv, len(out), args.out_md))
    for m in ("evade_start_count", "evade_start_ratio_gate", "evade_start_frac_inside_gate",
              "evade_start_frac_deep_half", "fire_aam_count", "sam_fire_count",
              "sam_fire_ratio_dmax", "ship_defense_count"):
        r = summary.get((arms[0], m))
        if r is None:
            continue
        print("  %-30s mean=%s p10=%s p50=%s p90=%s n_ev=%s n_ep=%s" % (
            m, _fmt(r["mean"]), _fmt(r["p10"]), _fmt(r["p50"]), _fmt(r["p90"]),
            r["n_events"], r["n_episodes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
