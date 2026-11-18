#!/usr/bin/env python3
"""平台在环实验作图：读取 data/*.csv（必要时回读原始 tap）输出 fig/*.png|svg。

图
  fig_arms_score.png   各 arm 红方得分布 + 均值/bootstrap 95% CI
  fig_losses.png       各 arm 红方 air/sea/land 损失堆叠（附蓝方损失对照）
  fig_score_curve.png  代表局（arm 内中位数得分局）得分-仿真时间曲线
  fig_metadata.png     步数分布 / 每步耗时分布

用法
  ~/.venvs/ai-dev/bin/python analysis/figs.py --data data --fig fig --tap raw/tap
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics

CJK_CANDIDATES = ["Source Han Sans SC", "Noto Sans CJK SC", "WenQuanYi Zen Hei", "SimHei"]
COLORS = ["#2f6f9f", "#d9754a", "#5a9e6f", "#8c6bb1", "#b5a642", "#7f7f7f"]


def setup_fonts() -> bool:
    """有中文字体就用中文标签；没有则退回英文并让 README 说明。"""
    available = {f.name for f in fm.fontManager.ttflist}
    for name in CJK_CANDIDATES:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name] + plt.rcParams["font.sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False
            return True
    print("[warn] 未找到中文字体，图中改用英文标签")
    return False


def labels(zh: bool, zh_text: str, en_text: str) -> str:
    return zh_text if zh else en_text


def save(fig: plt.Figure, fig_dir: Path, name: str) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".svg"):
        fig.savefig(fig_dir / f"{name}{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_arms_score(ep: pd.DataFrame, fig_dir: Path, zh: bool) -> None:
    arms = sorted(ep["arm"].unique())
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    data = [ep.loc[ep["arm"] == a, "red_score"].dropna().to_numpy(dtype=float) for a in arms]
    ax.boxplot(data, widths=0.5, showfliers=False,
               medianprops={"color": "#333333"}, boxprops={"color": "#666666"},
               whiskerprops={"color": "#666666"}, capprops={"color": "#666666"})
    jitter = np.linspace(-0.12, 0.12, max(len(v) for v in data)) if data else [0]
    rng = np.random.default_rng(20261118)
    for pos, values in enumerate(data, start=1):
        ax.scatter(pos + jitter[:len(values)], values, s=26, color=COLORS[(pos - 1) % len(COLORS)],
                   zorder=3, alpha=0.9)
        mean = float(values.mean())
        low, high = metrics.bootstrap_ci(values, 1000, rng)
        ax.errorbar(pos + 0.3, mean, yerr=[[mean - low], [high - mean]],
                    fmt="D", color="#b03a2e", capsize=5, markersize=6, lw=1.5, zorder=4,
                    label=labels(zh, "均值 ± bootstrap 95% CI", "mean ± bootstrap 95% CI")
                    if pos == 1 else None)
    ax.set_xticks(range(1, len(arms) + 1))
    ax.set_xticklabels([f"{a}\n(n={len(v)})" for a, v in zip(arms, data)])
    ax.set_ylabel(labels(zh, "红方最终得分", "Red final score"))
    ax.set_title(labels(zh, "各 arm 得分布",
                        "Score by arm"), fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    save(fig, fig_dir, "fig_arms_score")


def fig_losses(ep: pd.DataFrame, fig_dir: Path, zh: bool) -> None:
    arms = sorted(ep["arm"].unique())
    groups = [("red_loss_air", labels(zh, "红方空中", "Red air"), "#2f6f9f"),
              ("red_loss_sea", labels(zh, "红方水面", "Red sea"), "#5a9e6f"),
              ("red_loss_land", labels(zh, "红方地面", "Red land"), "#d9a44a")]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    x = np.arange(len(arms))
    width = 0.5 if len(arms) > 1 else 0.28
    bottom = np.zeros(len(arms))
    for col, label, color in groups:
        vals = np.array([ep.loc[ep["arm"] == a, col].mean() for a in arms], dtype=float)
        ax.bar(x, vals, width, bottom=bottom, label=label, color=color)
        bottom += vals
    for pos, total in enumerate(bottom):
        ax.text(pos, total, f"{total:.1f}", ha="center", va="bottom", fontsize=8)
    if "blue_loss_own_exact" in ep and ep["blue_loss_own_exact"].notna().any():
        blue = np.array([ep.loc[ep["arm"] == a, "blue_loss_own_exact"].mean() for a in arms], dtype=float)
        ax.scatter(x, blue, marker="_", s=350, linewidth=2, color="#b03a2e",
                   label=labels(zh, "蓝方自身兵力损失（对照）", "Blue own losses (reference)"), zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{a}\n(n={(ep['arm'] == a).sum()})" for a in arms])
    ax.set_xlim(-0.6, len(arms) - 0.4)
    ax.set_ylim(0, max(float(bottom.max()), 1.0) * 1.15)
    ax.set_ylabel(labels(zh, "平均损失单元数", "Mean lost units"))
    ax.set_title(labels(zh, "各 arm 红方损失构成（own 全量，消失即损失）",
                        "Red losses by arm (own list, disappeared = lost)"), fontsize=9)
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    ax.grid(axis="y", alpha=0.3)
    save(fig, fig_dir, "fig_losses")


def representative(ep: pd.DataFrame) -> pd.DataFrame:
    """每 arm 取红方得分最接近该 arm 中位数的一局作为代表局。"""
    picks = []
    for arm, group in ep.groupby("arm", sort=True):
        med = group["red_score"].median() if "red_score" in group else group["score_final"].median()
        score = group["red_score"] if "red_score" in group else group["score_final"]
        picks.append(group.loc[(score - med).abs().idxmin()])
    return pd.DataFrame(picks)


def fig_score_curve(ep: pd.DataFrame, tap_dir: Path, fig_dir: Path, zh: bool) -> None:
    picks = representative(ep)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    for idx, row in picks.iterrows():
        path = tap_dir / row["tap_file"]
        if not path.exists():
            print(f"[warn] 缺少 {path}，跳过该代表局")
            continue
        rows = metrics.read_jsonl(path)
        pass_rows, _ = metrics.select_pass(rows, {"steps": row["n_steps_tap"], "sim_end": row["sim_end_tap"]})
        t = np.array([r.get("t", 0.0) for r in pass_rows], dtype=float) / 60.0
        s = np.array([r.get("score", 0.0) for r in pass_rows], dtype=float)
        ax.plot(t, s, lw=1.4, color=COLORS[len(ax.lines) % len(COLORS)],
                label=f"{row['arm']} / {row['tap']}")
    ax.set_xlabel(labels(zh, "仿真时间 (min)", "Simulation time (min)"))
    ax.set_ylabel(labels(zh, "红方累计得分", "Red cumulative score"))
    ax.set_title(labels(zh, "代表局得分-时间曲线（每 arm 取中位数得分局）",
                        "Score vs time for representative episodes (median-score episode per arm)"), fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    save(fig, fig_dir, "fig_score_curve")


def fig_metadata(ep: pd.DataFrame, fig_dir: Path, zh: bool) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.8))
    arms = sorted(ep["arm"].unique())
    labels_x = [f"{a}\n(n={(ep['arm'] == a).sum()})" for a in arms]

    ax = axes[0]
    data = [ep.loc[ep["arm"] == a, "n_steps_tap"].dropna().to_numpy(dtype=float) for a in arms]
    ax.boxplot(data, widths=0.45, showfliers=False,
               medianprops={"color": "#333333"}, boxprops={"color": "#666666"},
               whiskerprops={"color": "#666666"}, capprops={"color": "#666666"})
    jitter = np.linspace(-0.1, 0.1, max(len(v) for v in data))
    for pos, values in enumerate(data, start=1):
        ax.scatter(pos + jitter[:len(values)], values, s=28,
                   color=COLORS[(pos - 1) % len(COLORS)], zorder=3)
    ax.set_xticks(range(1, len(arms) + 1))
    ax.set_xticklabels(labels_x, fontsize=8)
    ax.set_ylabel(labels(zh, "单局步数", "Steps per episode"))
    ax.set_title(labels(zh, "(a) 仿真步数", "(a) Steps per episode"), fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    ax = axes[1]
    x = np.arange(len(ep))
    order = ep.assign(_arm_rank=ep["arm"].map({a: i for i, a in enumerate(arms)})) \
               .sort_values(["_arm_rank", "tap"])
    mean = order["step_wall_mean"].to_numpy(dtype=float)
    p95 = order["step_wall_p95"].to_numpy(dtype=float)
    colors = [COLORS[arms.index(a) % len(COLORS)] for a in order["arm"]]
    ax.bar(x, mean, 0.6, color=colors, label=labels(zh, "每步耗时均值", "Mean step wall time"))
    ax.scatter(x, p95, marker="v", s=30, color="#b03a2e", zorder=4,
               label=labels(zh, "95 分位", "95th percentile"))
    ax.set_xticks(x)
    ax.set_xticklabels([str(t)[-10:] for t in order["tap"]], rotation=45, ha="right", fontsize=7)
    ax.set_ylabel(labels(zh, "秒 / 步", "Seconds per step"))
    ax.set_title(labels(zh, "(b) 每步写盘耗时（tap wall 差分）", "(b) Per-step wall time (tap diff)"), fontsize=9)
    ax.legend(fontsize=7)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    save(fig, fig_dir, "fig_metadata")


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="平台在环实验作图")
    ap.add_argument("--data", type=Path, default=here / "data")
    ap.add_argument("--fig", type=Path, default=here / "fig")
    ap.add_argument("--tap", type=Path, default=here / "raw" / "tap")
    args = ap.parse_args(argv)

    zh = setup_fonts()
    ep = pd.read_csv(args.data / "episode_metrics.csv")
    runs = pd.read_csv(args.data / "runs.csv")
    ep = ep.merge(runs[["tap", "red_score"]], on="tap", how="left")
    if ep.empty:
        print("[warn] 无可用局，未出图")
        return 1

    fig_arms_score(ep, args.fig, zh)
    fig_losses(ep, args.fig, zh)
    fig_score_curve(ep, args.tap, args.fig, zh)
    fig_metadata(ep, args.fig, zh)
    print(f"已输出 4 张图到 {args.fig}/ （各含 PNG + SVG）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
