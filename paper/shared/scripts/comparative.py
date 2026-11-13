#!/usr/bin/env python
"""
对比实验 / 消融 / 敏感性 / 端到端
================================
在 scripts/sim_experiments.py 的运动学内核之上，构造「本方案 vs 基线 vs 消融」的
受控对比，供文稿第 4–8 章使用。

与 sim_experiments.py 的分工
  sim_experiments.py   单规则验证（每个实验只回答"这条规则是否成立"）
  comparative.py       受控对比（同一个指标上，不同策略集的相对表现）

策略集（Policy）
  R    完整规则（分档掉头 + 垂直扭 + 能量阈值脱离）
  B0   无规避：保持航向直到命中
  B1   平台默认：弹速降为 0 才脱离（等价于飞行中不规避）
  B2   固定掉头距离 40 km，无垂直扭
  B3   分档掉头，但无垂直扭
  A1   去掉能量阈值（弹速归零才脱离 → 不反打）
  A2   去掉垂直扭（= B3）
  A3   去掉分档（固定 50 km）

输出：paper/data/*.csv
用法：python paper/scripts/comparative.py all --seed 2026
"""
import argparse
import csv
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))  # 仓库根目录
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from sim_experiments import (  # noqa: E402
    DT, R_KILL, T_MAX, V_TERM, OMEGA_MAX, Body, closest_approach, kmh,
    speed_of, wrap, _critical_range,
)

# ------------------------------------------------------------------ 策略集
POLICIES = {
    "R  分档+垂直扭+能量阈值": dict(tiered=True, beam=True, energy_stop=500.0),
    "B0 弹速归零才脱离": dict(tiered=False, beam=False, energy_stop=0.0, no_turn=True),
    "B1 单一固定掉头 25 km": dict(tiered=False, beam=False, energy_stop=500.0, fixed=25.0),
    "B2 单分档(仅 >2500 判 50 km)": dict(knife=True, beam=True, energy_stop=500.0),
    "B3 分档但无垂直扭": dict(tiered=True, beam=False, energy_stop=500.0),
    "A1 去掉能量阈值(不反打)": dict(tiered=True, beam=True, energy_stop=0.0),
    "A2 掉头距离全取 50 km": dict(tiered=False, beam=True, energy_stop=500.0, fixed=50.0),
    "A3 掉头距离全取 20 km": dict(tiered=False, beam=True, energy_stop=500.0, fixed=20.0),
    "P 按 d0 插值 (1.2 d0)": dict(tiered=False, beam=False, energy_stop=500.0,
                                  d0rule=1.2),
}


def d0_linear(v0, va, t_burn=240.0):
    """线性衰减下的闭式临界距离（km），与文稿 §5.2 的推导一致"""
    T = t_burn / 3600.0
    if v0 <= va:
        return 0.0
    if va <= V_TERM:
        return T * (v0 - V_TERM) / 2.0 + T * (V_TERM - va)
    return T * (v0 - va) ** 2 / (2.0 * (v0 - V_TERM))


def turn_distance(v0, pol, v_esc=900.0):
    """按策略给出掉头距离（km）"""
    if pol.get("no_turn"):
        return -1.0
    if "d0rule" in pol:
        return min(100.0, pol["d0rule"] * d0_linear(v0, v_esc))
    if "fixed" in pol:
        return pol["fixed"]
    if pol.get("knife"):
        return 50.0 if v0 > 2500 else 20.0
    if pol.get("tiered"):
        if v0 > 2500:
            return 50.0
        if v0 >= 1500:
            return 20.0
        return 10.0
    return 25.0


def engage_evade(v0, policy, bearing_deg=0.0, d_start=110.0,
                 v_esc=900.0, beam_r=20.0, beam_flip=8.0, dt=DT,
                 model="linear", t_burn=240.0, omega=OMEGA_MAX,
                 jitter=0.08, rng=None, fixed_override=None):
    """
    单次交战。返回 dict(hit, t, v_end, phase, shots_ok, r_turn)
      t          交战时长（s）—— 越大表示脱离战场越久、燃油代价越高
      shots_ok   是否出现「弹速降到 energy_stop 以下 → 可掉头反打」的机会
    """
    rng = rng or np.random
    pol = POLICIES[policy] if isinstance(policy, str) else policy
    stop = pol["energy_stop"]
    # 掉头距离按**标称**弹速判定，避免抖动把分档边界搅混
    r_turn = fixed_override if fixed_override is not None else turn_distance(v0, pol, v_esc)
    ac = Body(x=d_start, y=0.0, z=8.0, psi=math.pi, v=v_esc)
    mis = Body(x=0.0, y=0.0, z=8.0, psi=0.0, v=v0)
    ac.v = v_esc * (1 + jitter * (rng.random() - 0.5) * 2)
    v0 = v0 * (1 + jitter * (rng.random() - 0.5) * 2)
    phase, t, flip_t, side = 0, 0.0, 0.0, 1.0
    while t < T_MAX:
        p_prev = ac.pos - mis.pos
        d = float(np.linalg.norm(p_prev))
        los = math.atan2(ac.y - mis.y, ac.x - mis.x)
        if pol.get("no_turn"):
            pass
        elif phase == 0 and r_turn > 0 and d <= r_turn:
            phase = 1
            ac.psi = wrap(los)
            ac.v = v_esc * 1.2
            flip_t = t
        elif phase == 1 and pol["beam"] and d <= beam_r and mis.v > ac.v:
            phase = 2
            side = 1.0 if rng.random() < 0.5 else -1.0
            flip_t = t
        if phase == 1:
            ac.psi = wrap(los)
        elif phase == 2:
            if t - flip_t > beam_flip:
                side *= -1.0
                flip_t = t
            ac.psi = wrap(los + side * math.pi / 2.0)
        av = kmh(ac.v) * dt
        ac.x += av * math.cos(ac.psi)
        ac.y += av * math.sin(ac.psi)
        v = speed_of(model, v0, t, t_burn)
        if d > 1e-9:
            want = math.atan2((ac.y - mis.y), (ac.x - mis.x))
            dp = wrap(want - mis.psi)
            lim = omega * dt
            mis.psi += max(-lim, min(lim, dp))
        sv = kmh(v) * dt
        mis.x += sv * math.cos(mis.psi)
        mis.y += sv * math.sin(mis.psi)
        mis.z += (ac.z - mis.z) / max(d, 1e-6) * sv
        p_now = ac.pos - mis.pos
        dmin, _ = closest_approach(p_prev, (p_now - p_prev) / dt, dt)
        if dmin < R_KILL:
            return {"hit": True, "t": t, "v_end": v, "phase": phase,
                    "v0": v0, "r_turn": r_turn, "shots_ok": False}
        if v <= V_TERM:
            return {"hit": False, "t": t, "v_end": v, "phase": phase,
                    "v0": v0, "r_turn": r_turn, "shots_ok": v <= stop}
        t += dt
    return {"hit": False, "t": t, "v_end": mis.v, "phase": phase,
            "v0": v0, "r_turn": r_turn, "shots_ok": mis.v <= stop}


# ------------------------------------------------------------------ 实验 A
def exp_a(outdir, n=1000, seed=2026):
    """空战单元自卫：策略 × 弹速 → 存活率 / 交战时长 / 反打机会率"""
    rng = np.random.default_rng(seed)
    v0s = [1500, 2000, 2500, 3000, 3500]
    rows = []
    for pol in POLICIES:
        for v0 in v0s:
            hits = shots = 0
            ts = []
            for _ in range(n):
                r = engage_evade(v0, pol, rng=rng)
                hits += int(r["hit"])
                shots += int(r.get("shots_ok", False))
                ts.append(r["t"])
            rows.append({"policy": pol, "v0_kmh": v0, "n": n,
                         "kill_rate": round(hits / n, 4),
                         "survive_rate": round(1 - hits / n, 4),
                         "counter_attack_rate": round(shots / n, 4),
                         "t_median_s": round(float(np.median(ts)), 1),
                         "t_mean_s": round(float(np.mean(ts)), 1)})
            print(f"  A {pol:<26s} V0={v0:5d} 存活={1-hits/n:.3f} "
                  f"反打={shots/n:.3f} T={np.median(ts):5.1f}s", flush=True)
    _write(outdir, "a_evade_policy.csv", rows)

    # Pareto 扫描：固定掉头距离 10–65 km
    par = []
    for v0 in v0s:
        for r in (10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65):
            hits, ts, shots = 0, [], 0
            for _ in range(n):
                o = engage_evade(v0, "R  分档+垂直扭+能量阈值", rng=rng,
                                 fixed_override=float(r))
                hits += int(o["hit"])
                shots += int(o.get("shots_ok", False))
                ts.append(o["t"])
            par.append({"v0_kmh": v0, "r_turn_km": r,
                        "survive_rate": round(1 - hits / n, 4),
                        "t_median_s": round(float(np.median(ts)), 1),
                        "counter_attack_rate": round(shots / n, 4)})
            print(f"  A-pareto V0={v0} R={r:2d}km 存活={1-hits/n:.3f} "
                  f"T={np.median(ts):5.1f}s", flush=True)
    _write(outdir, "a_evade_pareto.csv", par)
    return rows, par


# ------------------------------------------------------------------ 实验 B
def exp_b(outdir, n=300, seed=2026):
    """
    打空战开火策略：在「迎头—转向逃逸」的完整交战中比较
      R  0.8·d0 判定
      B1 最大射程（不判定）
      B2 固定 60 海里（WRA 常数，不判定）
      B3 固定 30 km
    指标：命中率、平均开火距离、无效发射率（开火但追不上）
    """
    rng = np.random.default_rng(seed)
    v0_pairs = [(2500, 1000), (3000, 1000), (3000, 1200), (3500, 1100)]
    strategies = {
        "R 0.8·d0": ("d0", 0.8),
        "B1 最大射程 90nm": ("abs", 90 * 1.852),
        "B2 固定 60nm": ("abs", 60 * 1.852),
        "B3 固定 30km": ("abs", 30.0),
    }
    rows = []
    for v0, va in v0_pairs:
        d0 = _critical_range(30.0, 0.0, va, (0.0, 0.0, 8.0), v0, climb=False)
        for name, (kind, val) in strategies.items():
            d_fire = val * d0 if kind == "d0" else val
            hit = 0
            fired = 0
            for _ in range(n):
                # 初始距离在 0.5–1.0 倍开火距离内随机（进入包线后才开火）
                d_init = d_fire * (0.5 + 0.5 * rng.random())
                r = engage_tail(v0, va, d_init, rng=rng)
                fired += 1
                hit += int(r["hit"])
            # 先射时间差：本方开火包线 vs 对手 WRA 常数(60 海里)的到达时刻差
            v_close = (v0 + va) / 3600.0            # km/s，迎头接近速度
            t_ours = d_fire / v_close
            t_theirs = (60 * 1.852) / v_close
            rows.append({"v0_kmh": v0, "v_target_kmh": va,
                         "d0_km": round(d0, 1), "strategy": name,
                         "d_fire_km": round(d_fire, 1), "n": n,
                         "hit_rate": round(hit / n, 4),
                         "waste_rate": round(1 - hit / n, 4),
                         "t_first_shot_s": round(t_ours, 1),
                         "first_shot_advantage_s": round(t_theirs - t_ours, 1)})
            print(f"  B V0={v0} Va={va} {name:<14s} 开火={d_fire:6.1f}km "
                  f"命中={hit/n:.3f}", flush=True)
    _write(outdir, "b_aircombat_policy.csv", rows)
    return rows


def engage_tail(v0, va, d_init, rng=None, dt=DT, model="linear",
                t_burn=240.0):
    """尾追交战：目标匀速逃逸，弹从 d_init 处发射"""
    ac = Body(x=d_init, y=0.0, z=8.0, psi=0.0, v=va)
    mis = Body(x=0.0, y=0.0, z=8.0, psi=0.0, v=v0)
    t = 0.0
    while t < T_MAX:
        p_prev = ac.pos - mis.pos
        av = kmh(ac.v) * dt
        ac.x += av * math.cos(ac.psi)
        ac.y += av * math.sin(ac.psi)
        v = speed_of(model, v0, t, t_burn)
        d = ac.pos - mis.pos
        if math.hypot(d[0], d[1]) > 1e-9:
            want = math.atan2(d[1], d[0])
            dp = wrap(want - mis.psi)
            lim = OMEGA_MAX * dt
            mis.psi += max(-lim, min(lim, dp))
        sv = kmh(v) * dt
        mis.x += sv * math.cos(mis.psi)
        mis.y += sv * math.sin(mis.psi)
        mis.z += (ac.z - mis.z) / max(float(np.linalg.norm(d)), 1e-6) * sv
        p_now = ac.pos - mis.pos
        dmin, _ = closest_approach(p_prev, (p_now - p_prev) / dt, dt)
        if dmin < R_KILL:
            return {"hit": True, "t": t, "v_end": v}
        if v <= V_TERM:
            return {"hit": False, "t": t, "v_end": v}
        t += dt
    return {"hit": False, "t": t, "v_end": mis.v}


# ------------------------------------------------------------------ 实验 C
def exp_c(outdir, n=4000, seed=2026):
    """
    登陆船只集群自卫：方案 × 来袭规模 → 拦截率 / 弹耗 / 弹药耗尽时的泄漏分布
    附带返回「按来袭序号」的累计拦截率曲线（用于过程图）
    """
    rng = np.random.default_rng(seed)
    dmax, p_far, p_near, K = 60.0, 0.35, 0.90, 8

    def pk(d):
        d = min(d, dmax)
        return p_far + (p_near - p_far) * (1 - d / dmax)


    schemes = {
        "R 双船分层": [("A", 1.0), ("B", 0.5)],
        "B1 单船双层": [("A", 1.0), ("A", 0.5)],
        "B2 双船同时MAX": [("A", 1.0), ("B", 1.0)],
        "B3 双船均½Dmax": [("A", 0.5), ("B", 0.5)],
    }
    rows, curves = [], []
    for size in (4, 8, 12):
        for name, layers in schemes.items():
            killed_tot = shots = 0
            per_index = np.zeros(size)
            kill_dist = []
            for _ in range(n // 4):
                mag = {"A": K, "B": K}
                for m in range(size):
                    killed = False
                    for ship, frac in layers:
                        if killed or mag[ship] <= 0:
                            continue
                        mag[ship] -= 1
                        shots += 1
                        if rng.random() < pk(dmax * frac):
                            killed = True
                            kill_dist.append(dmax * frac)
                    if killed:
                        killed_tot += 1
                        per_index[m] += 1
            tot = (n // 4) * size
            rows.append({"scheme": name, "inbound": size,
                         "runs": n // 4, "intercept_rate": round(killed_tot / tot, 4),
                         "shots_per_inbound": round(shots / tot, 3),
                         "shots_per_kill": round(shots / max(killed_tot, 1), 3),
                         "mean_intercept_range_km": round(
                             float(np.mean(kill_dist)) if kill_dist else 0.0, 2)})
            for m in range(size):
                curves.append({"scheme": name, "inbound": size, "index": m + 1,
                               "cum_intercept": round(per_index[m] / (n // 4), 4)})
            print(f"  C {name:<16s} 来袭{size:2d} 拦截={killed_tot/tot:.3f} "
                  f"弹耗/拦截={shots/max(killed_tot,1):.2f}", flush=True)
    _write(outdir, "c_ship_scheme.csv", rows)
    _write(outdir, "c_ship_curve.csv", curves)
    return rows, curves


# ------------------------------------------------------------------ 实验 D
def exp_d(outdir, n=400, seed=2026):
    """地空导弹营：开火比例 → 拦截概率（含解析能量裕度）"""
    rng = np.random.default_rng(seed)
    v0, va = 3000.0, 900.0
    dmax = _critical_range(60.0, math.pi, va, (0.0, 0.0, 0.0), v0, climb=True)
    rows = []
    for frac in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        d_fire = dmax * frac
        hit = 0
        v_ends = []
        for _ in range(n):
            r = _flight_sam(d_fire, v0, va, rng)
            hit += int(r["hit"])
            if r["hit"]:
                v_ends.append(r["v_end"])
        p_geo = hit / n
        v_end = float(np.mean(v_ends)) if v_ends else 0.0
        margin = max(0.0, (v_end - V_TERM) / (0.6 * v0))
        salvos = max(1, min(2, int((d_fire - 15.0) / 10.0) + 1))
        rows.append({"dmax_km": round(dmax, 1), "fire_fraction": frac,
                     "d_fire_km": round(d_fire, 1),
                     "kinematic_hit_rate": round(p_geo, 4),
                     "v_end_kmh": round(v_end, 0),
                     "p_single": round(min(1.0, margin) * p_geo, 4),
                     "salvos": salvos,
                     "p_total": round(1 - (1 - min(1.0, margin) * p_geo) ** salvos, 4)})
        print(f"  D 开火={frac:.1f}Dmax 末端={v_end:6.0f}km/h "
              f"综合P={rows[-1]['p_total']:.3f}", flush=True)
    _write(outdir, "d_sam_opening.csv", rows)
    return rows


def _flight_sam(d_fire, v0, va, rng):
    ac = Body(x=d_fire, y=0.0, z=8.0, psi=math.pi, v=va)
    mis = Body(x=0.0, y=0.0, z=0.0, psi=0.0, v=v0)
    t, pen, g = 0.0, 0.0, 9.81
    while t < T_MAX:
        p_prev = ac.pos - mis.pos
        av = kmh(ac.v) * DT
        ac.x += av * math.cos(ac.psi)
        ac.y += av * math.sin(ac.psi)
        v_nom = speed_of("linear", v0, t, 240.0)
        dist3 = max(float(np.linalg.norm(ac.pos - mis.pos)), 1e-6)
        pen += 2 * g * ((ac.z - mis.z) / dist3 * kmh(v_nom) * DT * 1000.0)
        v = math.sqrt(max((v_nom / 3.6) ** 2 - pen, 1.0)) * 3.6
        d = ac.pos - mis.pos
        if math.hypot(d[0], d[1]) > 1e-9:
            want = math.atan2(d[1], d[0])
            dp = wrap(want - mis.psi)
            mis.psi += max(-OMEGA_MAX * DT, min(OMEGA_MAX * DT, dp))
        sv = kmh(v) * DT
        mis.x += sv * math.cos(mis.psi)
        mis.y += sv * math.sin(mis.psi)
        mis.z += (ac.z - mis.z) / dist3 * sv
        p_now = ac.pos - mis.pos
        dmin, _ = closest_approach(p_prev, (p_now - p_prev) / DT, DT)
        if dmin < R_KILL:
            return {"hit": True, "v_end": v}
        if v <= V_TERM:
            return {"hit": False, "v_end": v}
        t += DT
    return {"hit": False, "v_end": mis.v}


# ------------------------------------------------------------------ 实验 E
def exp_e(outdir, n=400, seed=2026):
    """
    敏感性分析（一次一变 / OAT）

    关键设计：参数只在其**起作用的工作点**上扫。
      * 能量参数（t_burn、v_esc）在 R 策略（50 km 早掉头）上扫——此时交战由能量决定
      * 机动参数（omega、beam_r、beam_flip）在 A3 策略（20 km 晚掉头）上扫——此时垂直扭真的被触发
    这样得到的敏感度才反映"参数在何处重要"，而不是"参数在未激活处无影响"。
    """
    rng = np.random.default_rng(seed)
    base = dict(t_burn=240.0, omega=OMEGA_MAX, beam_r=20.0, v_esc=900.0,
                beam_flip=8.0)
    plan = {
        "R  分档+垂直扭+能量阈值": ["t_burn", "v_esc"],
        "A3 掉头距离全取 20 km": ["omega", "beam_r", "beam_flip", "v_esc"],
    }
    mults = [0.6, 0.8, 1.0, 1.2, 1.4]
    v0 = 3000
    rows = []
    bases = {}
    for pol, knobs in plan.items():
        kills = 0
        for _ in range(n):
            kills += int(engage_evade(v0, pol, rng=rng, **base)["hit"])
        bases[pol] = kills / n
        print(f"  E 基准 {pol}: kill={bases[pol]:.3f}", flush=True)
        for knob in knobs:
            for m in mults:
                kw = dict(base)
                kw[knob] = base[knob] * m
                kills = 0
                for _ in range(n):
                    kills += int(engage_evade(v0, pol, rng=rng, **kw)["hit"])
                rows.append({"policy": pol, "knob": knob, "multiplier": m,
                             "value": round(kw[knob], 2),
                             "kill_rate": round(kills / n, 4),
                             "delta_vs_base": round(kills / n - bases[pol], 4),
                             "base_kill_rate": round(bases[pol], 4)})
            print(f"  E 敏感性 {pol} / {knob} 完成", flush=True)
    _write(outdir, "e_sensitivity.csv", rows)
    return rows, bases


# ------------------------------------------------------------------ 实验 F
def exp_f(outdir, n=600, seed=2026):
    """
    端到端 1v1：我方规则集 vs 对手固定 WRA 常数

    场景：双方同高、迎头接近，初始 180 km，各自携带同型弹（初速 V0）。
      * 我方开火判定：d <= 0.8·d0(V0, V敌)          （§5 的判据）
      * 对手开火判定：d <= 60 海里 = 111.1 km        （固定 WRA 常数）
      谁先满足条件谁先开火；被射击方立即按 d_turn = 1.2·d0 掉头规避。
      弹按纯追踪飞行，V <= 500 km/h 判失效。
    结局四分类：我方胜 / 对手胜 / 双亡 / 双存
    """
    rng = np.random.default_rng(seed)
    NM = 1.852
    rows = []
    for v0, va in ((2500, 900), (3000, 1000), (3500, 1100)):
        d0 = d0_linear(v0, va)
        res = {"我方胜": 0, "对手胜": 0, "双亡": 0, "双存": 0}
        t_first_ours = t_first_theirs = 0.0
        for _ in range(n):
            outcome = _duel(v0, va, d0, rng, NM)
            res[outcome[0]] += 1
            t_first_ours += outcome[1]
            t_first_theirs += outcome[2]
        rows.append({
            "v0_kmh": v0, "v_target_kmh": va, "d0_km": round(d0, 1),
            "n": n,
            "win_rate": round(res["我方胜"] / n, 4),
            "loss_rate": round(res["对手胜"] / n, 4),
            "both_dead": round(res["双亡"] / n, 4),
            "both_alive": round(res["双存"] / n, 4),
            "t_first_fire_ours_s": round(t_first_ours / n, 1),
            "t_first_fire_theirs_s": round(t_first_theirs / n, 1),
        })
        print(f"  F V0={v0} Va={va}: 我方胜={res['我方胜']/n:.3f} "
              f"对手胜={res['对手胜']/n:.3f} 双存={res['双存']/n:.3f} "
              f"首火时刻 我方={t_first_ours/n:.0f}s 对手={t_first_theirs/n:.0f}s",
              flush=True)
    _write(outdir, "f_duel.csv", rows)
    return rows


def _duel(v0, va, d0, rng, NM):
    """
    简化 1v1：只用一维沿视线的距离演化，加上"弹能否追上"的解析判据。
    在双方都迎头接近的前段，沿视线距离以 (V0 + Va) 收缩；开火后转为尾追。
    """
    D0 = 180.0
    d_ours = min(0.8 * d0, D0)
    d_theirs = min(60 * NM, D0)
    v_close = (v0 + va) / 3600.0
    t_ours = (D0 - d_ours) / v_close if d_ours < D0 else 0.0
    t_theirs = (D0 - d_theirs) / v_close if d_theirs < D0 else 0.0

    # 我方先开火的概率：如果同时满足，按距离更远者先（时间更早）
    ours_first = t_ours <= t_theirs
    # 我方弹：从 d_ours 处发射，目标在其后开始逃逸 → 用 d0 判可达性
    ours_hits = d_ours <= d0
    # 对手弹：从 d_theirs 处发射，同样判可达性
    theirs_hits = d_theirs <= d0
    # 随机命中抖动（±10% 距离误差）
    j = 1 + 0.10 * (rng.random() - 0.5) * 2
    ours_hits = ours_hits and (d_ours * j <= d0)
    theirs_hits = theirs_hits and (d_theirs * j <= d0)

    if ours_hits and theirs_hits:
        return ("双亡", t_ours, t_theirs)
    if ours_hits:
        return ("我方胜", t_ours, t_theirs)
    if theirs_hits:
        return ("对手胜", t_ours, t_theirs)
    return ("双存", t_ours, t_theirs)


# ------------------------------------------------------------------ 工具
def _write(outdir, name, rows):
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, name)
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  → {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["all", "a", "b", "c", "d", "e", "f"])
    ap.add_argument("--out", default=os.path.join(HERE, "..", "data"))
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if a.which in ("all", "a"):
        exp_a(out, n=a.n or 1000, seed=a.seed)
    if a.which in ("all", "b"):
        exp_b(out, n=(a.n or 600) // 3, seed=a.seed + 1)
    if a.which in ("all", "c"):
        exp_c(out, n=a.n or 4000, seed=a.seed + 2)
    if a.which in ("all", "d"):
        exp_d(out, n=(a.n or 1200) // 4, seed=a.seed + 3)
    if a.which in ("all", "e"):
        exp_e(out, n=a.n or 150, seed=a.seed + 4)
    if a.which in ("all", "f"):
        exp_f(out, n=a.n or 600, seed=a.seed + 5)


if __name__ == "__main__":
    main()
