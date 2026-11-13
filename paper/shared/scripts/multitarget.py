"""多目标 / 多波次端到端：火力分配 × 开火规则。

第 9 章的单机 1v1 只能证明"阈值位置"的后果。这里把规模放大到
2 机对 4 机、两波进入，检验两件单机实验看不到的事：
  ① 多目标时"先射权"是否还是决定性优势；
  ② 火力分配（齐射 / 每目标一发 / 就近优先）是否改变结论。

模型口径（与第 9 章一致，仍是交战级压缩）：
- 双方各机带 2 枚弹；单发命中由第 4 章的规避模型解算，开火距离取本方开火线。
- 对手固定按 60 海里（111.1 km）开火，分配为最近优先。
- 我方开火规则 ∈ {0.8 d0, 固定 60 海里, 固定 90 海里}
  我方分配 ∈ {最近优先, 每目标至多一发, 双发齐射}

输出：g_multitarget.csv
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from comparative import engage_evade, d0_linear, _write  # noqa: E402

V0_OURS = 2500.0
V0_THEIRS = 2500.0
VA = 900.0
NM = 1.852
WRA_THEIRS = 60.0 * NM
EVADER = "A2 掉头距离全取 50 km"
AMMO = 3
N_WAVE = 2
N_THEIRS = 4


def _fire_line(rule):
    if rule == "0.8 d0":
        return 0.8 * d0_linear(V0_OURS, VA)
    if rule == "固定 60 海里":
        return 60.0 * NM
    if rule == "固定 90 海里":
        return 90.0 * NM
    raise ValueError(rule)


def _hit(shot_range, v_mis, rng):
    r = engage_evade(v_mis, EVADER, d_start=min(shot_range, 110.0),
                     v_esc=VA, rng=rng)
    return bool(r["hit"])


def _engage(rule, assign, rng, opp_rule="固定 60 海里"):
    line = _fire_line(rule)
    opp_line = _fire_line(opp_rule)
    ours = [{"id": i, "alive": True, "ammo": AMMO} for i in range(2)]
    theirs = [{"id": i, "alive": False, "ammo": AMMO} for i in range(N_THEIRS)]
    shots = kills = losses = 0
    ranges = []

    for wave in range(2):
        for i in range(N_WAVE * wave, min(N_THEIRS, N_WAVE * (wave + 1))):
            theirs[i]["alive"] = True
            theirs[i]["ammo"] = AMMO

        for who in ("ours", "theirs"):
            shooters = ours if who == "ours" else theirs
            targets = theirs if who == "ours" else ours
            got = {t["id"]: 0 for t in targets}
            for s in shooters:
                if not s["alive"]:
                    continue
                while s["ammo"] > 0:
                    live = [t for t in targets if t["alive"]]
                    if not live:
                        break
                    if who == "ours" and assign == "双发齐射":
                        # 一轮齐射：同一目标一次打出两发，事后才知道结果
                        live = [t for t in live if got[t["id"]] == 0]
                        if not live:
                            break
                        t = live[0]
                        for _ in range(min(2, s["ammo"])):
                            s["ammo"] -= 1
                            got[t["id"]] += 1
                            shots += 1
                            ranges.append(line)
                            if _hit(line, V0_OURS, rng) and t["alive"]:
                                t["alive"] = False
                                kills += 1
                        continue
                    if who == "ours" and assign == "每目标至多一发":
                        live = [t for t in live if got[t["id"]] == 0]
                        if not live:
                            break
                    t = live[0]
                    s["ammo"] -= 1
                    got[t["id"]] += 1
                    if who == "ours":
                        shots += 1
                        ranges.append(line)
                        if _hit(line, V0_OURS, rng) and t["alive"]:
                            t["alive"] = False
                            kills += 1
                        break          # 每个决策轮每机只打一发
                    else:
                        if _hit(opp_line, V0_THEIRS, rng) and t["alive"]:
                            t["alive"] = False
                            losses += 1
                        break
        if not any(s["alive"] for s in ours):
            break

    return {
        "our_survivors": sum(1 for s in ours if s["alive"]),
        "their_kills": kills,
        "our_losses": losses,
        "shots": shots,
        "hit_rate": (kills / shots) if shots else 0.0,
        "mean_fire_range_km": float(np.mean(ranges)) if ranges else 0.0,
    }


def exp_g(outdir, n=200, seed=2026):
    rng = np.random.default_rng(seed)
    rows = []
    for opp in ("固定 60 海里", "0.8 d0"):
      for rule in ("0.8 d0", "固定 60 海里", "固定 90 海里"):
        for assign in ("每目标至多一发", "最近优先", "双发齐射"):
            acc = [_engage(rule, assign, rng, opp_rule=opp) for _ in range(n)]
            agg = {k: float(np.mean([a[k] for a in acc])) for k in acc[0]}
            rows.append({"opp_rule": opp, "fire_rule": rule, "assignment": assign, "n": n,
                         "our_survivors": round(agg["our_survivors"], 2),
                         "their_kills": round(agg["their_kills"], 2),
                         "our_losses": round(agg["our_losses"], 2),
                         "shots": round(agg["shots"], 2),
                         "hit_rate": round(agg["hit_rate"], 4),
                         "mean_fire_range_km": round(agg["mean_fire_range_km"], 1)})
            print(f"  G 对手{opp:<10s} {rule:<10s} {assign:<8s} 存活={rows[-1]['our_survivors']:.2f}/2 "
                  f"击杀={rows[-1]['their_kills']:.2f}/4 命中={rows[-1]['hit_rate']:.3f}",
                  flush=True)
    _write(outdir, "g_multitarget.csv", rows)
    return rows


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(HERE), "data")
    exp_g(out)
