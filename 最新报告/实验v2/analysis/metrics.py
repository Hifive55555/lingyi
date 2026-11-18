#!/usr/bin/env python3
"""平台在环实验数据管道：灵弈平台原始日志 -> 可复现 CSV。

输入
  runs.jsonl        每局一行的结果记录（arm/theta/tap/steps/red_score/blue_score/sim_end/ok/wall_s ...）
  tap/              态势采样，每局两份：<arm>__<ts>__红方.jsonl 与 <arm>__<ts>__蓝方.jsonl

输出（默认 data/）
  runs.csv          每局一行（对齐 tap 之后的结果表）
  episode_metrics.csv  每局派生指标
  arm_summary.csv   按 arm 聚合（n/均值/标准差/bootstrap 95% CI）

用法
  ~/.venvs/ai-dev/bin/python analysis/metrics.py --runs raw/runs.jsonl --tap raw/tap --out data
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

FULL_LENGTH_S = 10800.0        # 场景满时长；sim_end 达到该值即视为满时长
FULL_LENGTH_TOL = 1.0          # 平台时间步长 30 s，留 1 s 容差
MUNITION_CTS_TYPE = 1          # cts.type == 1：在飞弹药
CTS_UNIT_GROUPS = {0: "air", 2: "sea", 3: "sea"}   # 可见蓝方实体类型 -> 分组（1 为弹药，7/8 为设施，17 为声呐浮标）；潜艇归入 sea
CTS_FACILITY_TYPES = {7, 8}    # 机场/雷达/地面设施：整局常驻，不计损失
CTS_EXPENDABLE_TYPES = {17}    # 声呐浮标：一次性消耗品，不计损失

SUMMARY_METRICS = [
    "red_score", "blue_score", "steps", "sim_end",
    "red_loss_total", "red_loss_air", "red_loss_sea", "red_loss_land",
    "red_units_initial", "red_units_final",
    "red_damaged_units_final", "red_mean_damage_final",
    "blue_loss_cts_approx", "blue_loss_cts_air_approx", "blue_loss_cts_sea_approx",
    "blue_loss_own_exact", "blue_loss_own_air", "blue_loss_own_sea", "blue_loss_own_land",
    "score_final", "score_peak", "score_auc",
    "engage_peak_type1", "engage_mean_type1", "munition_models",
    "step_wall_mean", "step_wall_p95", "full_length",
]


# ---------------------------------------------------------------- 原始日志读取
def read_jsonl(path: Path) -> list[dict]:
    """逐行解析 JSONL，跳过空行与写盘时被截断的半行（批量实验进行中会出现）。"""
    rows, bad = [], 0
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    if bad:
        print(f"[warn] {path.name}: 跳过 {bad} 行不完整 JSON", file=sys.stderr)
    return rows


@dataclass(frozen=True)
class TapFile:
    arm: str
    ts: str
    side: str            # "红方" / "蓝方"
    tag: str             # f"{arm}__{ts}"，与 runs.jsonl 的 tap 字段对齐
    path: Path


def index_tap(tap_dir: Path) -> dict[str, list[TapFile]]:
    """按文件名拆出 arm / 时间戳 / 阵营，返回 {'红方': [...], '蓝方': [...]}。"""
    out: dict[str, list[TapFile]] = {"红方": [], "蓝方": []}
    for path in sorted(tap_dir.glob("*.jsonl")):
        parts = path.stem.split("__")
        if len(parts) < 2 or parts[-1] not in out:
            continue
        side = parts[-1]
        if len(parts) >= 3:                      # <arm>__<ts>__<side>
            arm, ts = "__".join(parts[:-2]), parts[-2]
            tag = f"{arm}__{ts}"
        else:                                    # <arm>__<side>（本地样本命名）
            arm = "__".join(parts[:-1])
            ts, tag = "", arm
        out[side].append(TapFile(arm, ts, side, tag, path))
    return out


def split_passes(rows: list[dict]) -> list[list[dict]]:
    """按步序 i 回绕切段。

    同一局的重启（或同一文件被两次进程追加）会让 i 从大值跳回 1；同一 tag 文件里因此可能
    出现多段记录。每段是一个独立尝试，只有一段与 runs.jsonl 的 steps/sim_end 对得上。
    """
    passes, cur, prev_i = [], [], -1
    for row in rows:
        i = row.get("i", 0)
        if cur and i <= prev_i:
            passes.append(cur)
            cur = []
        cur.append(row)
        prev_i = i
    if cur:
        passes.append(cur)
    return passes


def pass_cost(pass_rows: list[dict], steps: float | None, sim_end: float | None) -> float:
    """该段与 runs.jsonl 记录的一致度，越小越像同一局。"""
    t_end = pass_rows[-1].get("t", 0.0)
    n_steps = (pass_rows[-1].get("i", len(pass_rows)) - pass_rows[0].get("i", 1))
    cost = 0.0
    if steps is not None:
        cost += abs(n_steps - steps)
    if sim_end is not None:
        cost += abs(t_end - sim_end)
    cost -= 1e-6 * len(pass_rows)     # 完全一致时取更长的那段
    return cost


def select_pass(rows: list[dict], run: dict) -> tuple[list[dict], int]:
    passes = split_passes(rows)
    best = min(passes, key=lambda p: pass_cost(p, run.get("steps"), run.get("sim_end")))
    return best, len(passes)


# ---------------------------------------------------------------- 派生指标计算
def _disappeared(first: dict, last: dict, last_obs: int) -> list[str]:
    """在观测窗口内出现过、但在最后一个观测点已消失的对象名。"""
    return [name for name, idx in last.items() if idx < last_obs]


def _group_counts(names, group_of: dict) -> dict[str, int]:
    counts = {"air": 0, "sea": 0, "land": 0}
    for name in names:
        key = group_of.get(name, "land")
        counts[key] = counts.get(key, 0) + 1
    return counts


def munition_model(name: str) -> str:
    """'防空导弹#117' -> '防空导弹'；去掉序号以统计弹药型号种类数。"""
    return re.sub(r"\s*#\d+\s*$", "", name).strip()


def episode_metrics(run: dict, red_rows: list[dict], blue_rows: list[dict] | None,
                    tap_file: str, pass_count: int) -> dict:
    """单局派生指标。red_rows/blue_rows 已各自选定为同一段记录。"""
    n_rows = len(red_rows)
    last_idx = n_rows - 1
    t = np.array([r.get("t", 0.0) for r in red_rows], dtype=float)
    score = np.array([r.get("score", 0.0) for r in red_rows], dtype=float)
    wall = np.array([r.get("wall", np.nan) for r in red_rows], dtype=float)

    # --- 红方自身兵力：own 中"出现后消失"= 损失（本方全量，口径最硬）
    own_first, own_last, own_side = {}, {}, {}
    for idx, row in enumerate(red_rows):
        for unit in row.get("own") or []:
            name, kind = unit[0], unit[1]
            own_first.setdefault(name, idx)
            own_last[name] = idx
            own_side[name] = kind
    red_gone = _disappeared(own_first, own_last, last_idx)
    red_loss = _group_counts(red_gone, own_side)
    final_own = red_rows[-1].get("own") or []
    final_damage = [u[7] for u in final_own if len(u) > 7]

    # --- 蓝方：cts 可见实体的消失量（近似，纯情报视角）
    cts_rows = [r for r in red_rows if r.get("cts")]
    cts_first, cts_last, cts_type = {}, {}, {}
    engage_counts = []
    for idx, row in enumerate(cts_rows):
        munitions = 0
        for unit in row["cts"]:
            name, utype = unit[0], unit[1]
            cts_first.setdefault(name, idx)
            cts_last[name] = idx
            cts_type[name] = utype
            if utype == MUNITION_CTS_TYPE:
                munitions += 1
        engage_counts.append(munitions)
    blue_gone = [n for n in _disappeared(cts_first, cts_last, len(cts_rows) - 1)
                 if cts_type[n] in CTS_UNIT_GROUPS]
    blue_group = {n: CTS_UNIT_GROUPS[cts_type[n]] for n in blue_gone}
    blue_loss_cts = _group_counts(blue_gone, blue_group)
    munitions_models = {munition_model(n) for n, k in cts_type.items() if k == MUNITION_CTS_TYPE}

    # --- 蓝方自身兵力（若拉到了蓝方 tap，则损失是确数而非近似）
    blue_own = {"initial": np.nan, "final": np.nan, "total": np.nan,
                "air": np.nan, "sea": np.nan, "land": np.nan}
    if blue_rows:
        b_first, b_last, b_side = {}, {}, {}
        for idx, row in enumerate(blue_rows):
            for unit in row.get("own") or []:
                name, kind = unit[0], unit[1]
                b_first.setdefault(name, idx)
                b_last[name] = idx
                b_side[name] = kind
        b_gone = _disappeared(b_first, b_last, len(blue_rows) - 1)
        b_loss = _group_counts(b_gone, b_side)
        blue_own = {
            "initial": len(b_first), "final": len(blue_rows[-1].get("own") or []),
            "total": len(b_gone), "air": b_loss["air"], "sea": b_loss["sea"], "land": b_loss["land"],
        }

    # --- 时间开销：tap 写盘间隔近似每步耗时（含平台内部开销）
    d_wall = np.diff(wall) if n_rows > 1 else np.array([])
    d_wall = d_wall[np.isfinite(d_wall)]
    sim_end = float(t[-1])
    # 满时长判定用 runs.jsonl 的 sim_end（平台登记值）；tap 末行 t 可能比它早一个采样点
    sim_end_ref = float(run.get("sim_end") or sim_end)
    auc = float(np.trapezoid(score, t) if hasattr(np, "trapezoid") else np.trapz(score, t))

    row = {
        "tap": run.get("tap") or tap_file,
        "arm": run.get("arm", ""),
        "theta": run.get("theta", ""),
        "episode": run.get("episode", 1),
        "tap_file": tap_file,
        "tap_passes": pass_count,
        "n_steps_tap": n_rows - 1,
        "sim_end_tap": round(sim_end, 2),
        "full_length": int(sim_end_ref >= FULL_LENGTH_S - FULL_LENGTH_TOL),
        "score_final": float(score[-1]),
        "score_peak": float(np.nanmax(score)),
        "score_auc": auc,
        "red_units_initial": len(own_first),
        "red_units_final": len(final_own),
        "red_loss_total": len(red_gone),
        "red_loss_air": red_loss["air"],
        "red_loss_sea": red_loss["sea"],
        "red_loss_land": red_loss["land"],
        "red_damaged_units_final": int(sum(1 for d in final_damage if d > 0)),
        "red_mean_damage_final": float(np.mean(final_damage)) if final_damage else np.nan,
        "blue_contacts_distinct": len(cts_first),
        "blue_loss_cts_approx": len(blue_gone),
        "blue_loss_cts_air_approx": blue_loss_cts["air"],
        "blue_loss_cts_sea_approx": blue_loss_cts["sea"],
        "blue_units_initial": blue_own["initial"],
        "blue_units_final": blue_own["final"],
        "blue_loss_own_exact": blue_own["total"],
        "blue_loss_own_air": blue_own["air"],
        "blue_loss_own_sea": blue_own["sea"],
        "blue_loss_own_land": blue_own["land"],
        "engage_peak_type1": int(max(engage_counts)) if engage_counts else 0,
        "engage_mean_type1": float(np.mean(engage_counts)) if engage_counts else np.nan,
        "munition_models": len(munitions_models),
        "step_wall_mean": float(d_wall.mean()) if d_wall.size else np.nan,
        "step_wall_p95": float(np.percentile(d_wall, 95)) if d_wall.size else np.nan,
    }
    return row


# ---------------------------------------------------------------- 局级聚合
def bootstrap_ci(values: np.ndarray, n_boot: int, rng: np.random.Generator) -> tuple[float, float]:
    if values.size == 0:
        return (np.nan, np.nan)
    if values.size == 1:
        return (float(values[0]), float(values[0]))
    means = rng.choice(values, size=(n_boot, values.size), replace=True).mean(axis=1)
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def arm_summary(episodes: pd.DataFrame, n_boot: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for arm, group in episodes.groupby("arm", sort=True):
        for metric in SUMMARY_METRICS:
            if metric not in group:
                continue
            values = pd.to_numeric(group[metric], errors="coerce").dropna().to_numpy(dtype=float)
            if values.size == 0:
                continue
            low, high = bootstrap_ci(values, n_boot, rng)
            records.append({
                "arm": arm, "metric": metric, "n": int(values.size),
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if values.size > 1 else np.nan,
                "ci_low": low, "ci_high": high,
                "n_boot": n_boot,
            })
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------- 主流程
def match_tap(run: dict, red_files: list[TapFile], blue_files: list[TapFile],
              cache: dict[Path, list[dict]]) -> tuple[TapFile | None, TapFile | None]:
    """把一条 runs.jsonl 记录对到它的红/蓝 tap 文件；优先按 tap 字段精确对齐。"""
    tag = run.get("tap")
    candidates = [f for f in red_files if tag and f.tag == tag]
    if not candidates:
        candidates = [f for f in red_files if f.arm == run.get("arm")]
    if not candidates:
        return None, None
    scored = []
    for f in candidates:
        rows = cache.setdefault(f.path, read_jsonl(f.path))
        if not rows:
            continue
        p = min(split_passes(rows), key=lambda p: pass_cost(p, run.get("steps"), run.get("sim_end")))
        scored.append((pass_cost(p, run.get("steps"), run.get("sim_end")), f))
    if not scored:
        return None, None
    red = min(scored)[1]
    blue = next((f for f in blue_files if f.tag == red.tag), None)
    return red, blue


def build(runs_path: Path, tap_dir: Path, out_dir: Path, n_boot: int, seed: int) -> pd.DataFrame:
    runs = read_jsonl(runs_path)
    files = index_tap(tap_dir)
    cache: dict[Path, list[dict]] = {}
    out_dir.mkdir(parents=True, exist_ok=True)

    kept_runs, episodes, skipped = [], [], []
    seen_tap = set()
    for run in runs:
        key = run.get("tap") or f"{run.get('arm')}|{run.get('episode')}|{run.get('ts')}"
        if key in seen_tap:
            continue                       # 同一局重复追加，保留首次
        seen_tap.add(key)
        if run.get("ok") is not True:
            skipped.append((key, f"ok={run.get('ok')}"))
            continue
        red, blue = match_tap(run, files["红方"], files["蓝方"], cache)
        if red is None:
            skipped.append((key, "无对应红方 tap"))
            continue
        red_rows, n_passes = select_pass(cache[red.path], run)
        blue_rows = select_pass(cache.setdefault(blue.path, read_jsonl(blue.path)), run)[0] if blue else None
        if blue and not blue_rows:
            blue_rows = None
        if not run.get("tap"):
            run = {**run, "tap": red.tag}   # 本地样本无 tap 字段时用文件名推得的 tag 对齐
        ep = episode_metrics(run, red_rows, blue_rows, red.path.name, n_passes)
        episodes.append(ep)
        kept_runs.append({
            "arm": run.get("arm", ""), "theta": run.get("theta", ""),
            "tap": run.get("tap"), "episode": run.get("episode", 1),
            "ts": run.get("ts", ""), "steps": run.get("steps"),
            "red_score": run.get("red_score"), "blue_score": run.get("blue_score"),
            "winner": run.get("winner"), "sim_end": run.get("sim_end"),
            "ok": run.get("ok"), "wall_s": run.get("wall_s"),
            "step_avg_s": run.get("step_avg_s"),
            "tap_file_red": red.path.name,
            "tap_file_blue": blue.path.name if blue else "",
            "tap_steps": ep["n_steps_tap"],
        })

    runs_df = pd.DataFrame.from_records(kept_runs)
    ep_df = pd.DataFrame.from_records(episodes)
    summary_source = ep_df
    if not runs_df.empty and not ep_df.empty:
        # runs.jsonl 的得分/步数/仿真时刻是平台登记值，作为聚合口径（与 tap 派生列应一致）
        summary_source = ep_df.merge(
            runs_df[["tap", "red_score", "blue_score", "steps", "sim_end"]], on="tap", how="left")
        drift = ep_df[["tap", "score_final", "n_steps_tap"]].merge(
            runs_df[["tap", "red_score", "steps"]], on="tap")
        bad = drift[(drift["score_final"] != drift["red_score"]) | (drift["n_steps_tap"] != drift["steps"])]
        print(f"tap 与 runs.jsonl 一致性: {len(drift) - len(bad)}/{len(drift)} 局得分与步数一致"
              + ("" if bad.empty else f"，不一致: {bad['tap'].tolist()}"))
    summary_df = arm_summary(summary_source, n_boot, seed) if not ep_df.empty else pd.DataFrame()

    runs_df.to_csv(out_dir / "runs.csv", index=False, encoding="utf-8")
    ep_df.to_csv(out_dir / "episode_metrics.csv", index=False, encoding="utf-8")
    summary_df.to_csv(out_dir / "arm_summary.csv", index=False, encoding="utf-8")

    print(f"输入 runs.jsonl: {len(runs)} 条，计入 {len(ep_df)} 局，跳过 {len(skipped)} 条")
    for key, why in skipped:
        print(f"  skip {key}: {why}")
    if not ep_df.empty:
        print(ep_df.groupby("arm").size().to_string())
    return ep_df


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="灵弈平台在环实验：原始日志 -> CSV")
    ap.add_argument("--runs", type=Path, default=here / "raw" / "runs.jsonl")
    ap.add_argument("--tap", type=Path, default=here / "raw" / "tap")
    ap.add_argument("--out", type=Path, default=here / "data")
    ap.add_argument("--boot", type=int, default=1000, help="bootstrap 重采样次数（>=1000）")
    ap.add_argument("--seed", type=int, default=20261118)
    args = ap.parse_args(argv)
    build(args.runs, args.tap, args.out, args.boot, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
