#!/usr/bin/env python
"""
灵弈人机协同智能体 —— 自建对抗仿真实验
======================================
用途：为《智能体设计报告》生成可复现的实验数据与图。
说明：**本仿真为独立自建模型，不调用灵弈平台**。它把讲解视频中口头描述的
      决策规则实现为一个 2D/2.5D 运动学对抗模型，用蒙特卡洛重复取得成功率类指标。

统一单位约定
------------
距离 km　速度 km/h　时间 s　角度 rad
1 km/h = 1/3600 km/s

运动学模型
----------
* 纯追踪（pure pursuit）+ 限转过载：追踪方航向每步朝目标方位角转动，
  最大角速度 `OMEGA_MAX`（模拟导弹可用过载）。
* 导弹速度衰减（两种，均可选）：
    linear  V(t) = V0 - (V0-V_TERM)/T_BURN * t
    mod     V(t) = V0 * (V_TERM/V0)^(t/T_BURN)      # 前段平缓、后段快速衰减
  当 V(t) <= V_TERM(500 km/h) 视为能量耗尽 → 判定"未命中"。
* 目标机速度恒定，可"加力"提升至 V_ESC 倍率。
* 命中判据：三维相对距离 < R_KILL(0.1 km)。

实验清单
--------
E1  空战躲避：弹速 × 掉头距离 → 躲避成功率（二维表 + 三维曲面）
E2  打空战：追击模型求临界距离 d0(V0,V敌)，并比较三种开火策略的命中率
E3  高度差：不同高度比 → 命中率（引入爬升/俯冲对有效速度的修正）
E4  地空导弹营：不同开火距离比例 → 拦截成功率
E5  船只自卫：单船 MAX D / 双船 MAX+MAX / 双船 MAX+½Dmax 的拦截弹消耗与拦截率

用法
----
  python scripts/sim_experiments.py all      --out docs/实验
  python scripts/sim_experiments.py e1       --out docs/实验
"""
import argparse
import csv
import json
import math
import os
from dataclasses import dataclass, field

import numpy as np

# ----------------------------------------------------------------- 常量
V_TERM = 500.0        # km/h，弹速低于此值视为能量耗尽（讲解 04:13–04:26 的"临界值"）
R_KILL = 0.1          # km，命中判定半径
DT = 0.5              # s，积分步长
T_MAX = 900.0         # s，单次对抗上限
OMEGA_MAX = math.radians(25.0)   # rad/s，追踪方最大转向角速度（可用过载的等价表示）
NM_KM = 1.852         # 1 海里 = 1.852 km

# 弹速模型默认参数（可由 --speed-model 切换）
# 能量衰减时间常数。取值使有效射程落在与想定同量级：
#   R_eff(V0) = (V0+V_TERM)/2 * T_BURN / 3600
#   V0=1500 → 66.7 km；V0=2500 → 100 km；V0=3000 → 116.7 km
#   （想定中流星/蝰蛇 60 海里≈111 km，箭 90 海里≈167 km）
T_BURN_DEFAULT = 240.0   # s


# ----------------------------------------------------------------- 基础
def kmh(v):
    return v / 3600.0


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


@dataclass
class Body:
    x: float
    y: float
    z: float
    psi: float
    v: float          # km/h

    @property
    def pos(self):
        return np.array([self.x, self.y, self.z])


def speed_of(kind, v0, t, t_burn=T_BURN_DEFAULT):
    """导弹速度衰减模型"""
    if kind == "linear":
        v = v0 - (v0 - V_TERM) * (t / t_burn)
    else:  # mod
        r = max(V_TERM / v0, 1e-6)
        v = v0 * (r ** (t / t_burn))
    return max(v, 0.0)


def closest_approach(p0, vrel, dt):
    """
    匀速直线下，两体相对位置 p0、相对速度 vrel（km, km/s）在 dt 内的最小距离。
    用于离散采样下的命中判定：步长内两体可能已经"擦过"，不能只用逐点距离。
    """
    vv = float(np.dot(vrel, vrel))
    if vv < 1e-12:
        return float(np.linalg.norm(p0)), 0.0
    ts = -float(np.dot(p0, vrel)) / vv
    ts = max(0.0, min(dt, ts))
    return float(np.linalg.norm(p0 + vrel * ts)), ts


def step_pursuer(m, tgt, t, v0, model, dz_rate=0.0):
    """追踪方按纯追踪 + 限转角推进"""
    d = tgt.pos - m.pos
    dxy = math.hypot(d[0], d[1])
    if dxy > 1e-9:
        want = math.atan2(d[1], d[0])
        dp = wrap(want - m.psi)
        limit = OMEGA_MAX * DT
        m.psi += max(-limit, min(limit, dp))
    v = speed_of(model, v0, t)
    sv = kmh(v) * DT
    m.x += sv * math.cos(m.psi)
    m.y += sv * math.sin(m.psi)
    # 高度：追踪方按剩余距离线性收敛到目标高度（模拟俯冲/爬升）
    dist = np.linalg.norm(tgt.pos - m.pos)
    if dist > 1e-6:
        dz = (tgt.z - m.z) / max(dist, 1e-6) * sv
        m.z += max(-abs(sv), min(abs(sv), dz))
    return v


def climb_penalty(v_kmh, dzdt_kmps, g=9.81):
    """
    高度机动的**比能量**修正（不是拍脑袋系数）：
    把速度 v 换算成 m/s，爬升高度增量 dh = dzdt*dt 时
        v_eff = sqrt(max(v^2 - 2g*dh_abs, 0))        （爬升耗能）
    俯冲时反向获得能量：v_eff = sqrt(v^2 + 2g*dh) 受最大速度上限约束。
    这里对每步的高度变化率折算为"等效爬升"，用于 E3/E4 的高低差仿真。
    注：dzdt_kmps 为 (km/s)，内部换算为 m/s。
    """
    v = v_kmh / 3.6                     # m/s
    dh = dzdt_kmps * 1000.0 * DT        # 该步的高度变化 m
    v2 = v * v - 2 * g * dh
    return math.sqrt(max(v2, 1.0)) * 3.6


# ----------------------------------------------------------------- E1
def run_intercept(v0_kmh, r_turn, bearing_deg, model="linear", jitter=0.1,
                  v_esc_kmh=900.0, d_start=110.0, dt=DT,
                  beam_r=20.0, beam_flip=8.0):
    """
    单次交战（对应讲解 02:33–04:26 的空战躲避三段规则）：
      阶段 0  迎头接近（飞机朝导弹方向飞）
      阶段 1  距离 <= r_turn：180° 掉头 + 加力，尾追逃逸
      阶段 2  距离 <= beam_r(20 km) 且 V弹 > V机：改为"时刻垂直于弹方向"扭动
              （每 beam_flip 秒换一次转向，模拟讲解中的"来回扭"）
    导弹：纯追踪 + 限转角（过载约束），速度按 model 衰减。
    返回 (是否命中, 交战时长, 末弹速, 结束阶段)
    """
    ac = Body(x=d_start, y=0.0, z=8.0, psi=math.pi, v=v_esc_kmh)
    mis = Body(x=0.0, y=0.0, z=8.0, psi=0.0, v=v0_kmh)
    ac.v = v_esc_kmh * (1 + jitter * (np.random.random() - 0.5) * 2)
    v0 = v0_kmh * (1 + jitter * (np.random.random() - 0.5) * 2)
    phase = 0
    t = 0.0
    flip_t = 0.0
    side = 1.0
    while t < T_MAX:
        p_prev = ac.pos - mis.pos
        d = float(np.linalg.norm(p_prev))
        los = math.atan2(ac.y - mis.y, ac.x - mis.x)
        if phase == 0 and d <= r_turn:
            phase = 1
            ac.psi = wrap(los)          # 背向逃逸（沿弹→机连线方向）
            ac.v = v_esc_kmh * 1.2      # 加力
            flip_t = t
        elif phase == 1 and d <= beam_r and mis.v > ac.v:
            phase = 2
            side = 1.0 if np.random.random() < 0.5 else -1.0
            flip_t = t
        if phase == 1:
            ac.psi = wrap(los)          # 持续背向
        elif phase == 2:
            if t - flip_t > beam_flip:
                side *= -1.0
                flip_t = t
            ac.psi = wrap(los + side * math.pi / 2.0)   # 时刻垂直于弹方向
        av = kmh(ac.v) * dt
        ac.x += av * math.cos(ac.psi)
        ac.y += av * math.sin(ac.psi)
        v = step_pursuer(mis, ac, t, v0, model)
        # 命中：看这一步内的最近接近点
        p_now = ac.pos - mis.pos
        dmin, _ = closest_approach(p_prev, (p_now - p_prev) / dt, dt)
        if dmin < R_KILL:
            return True, t, mis.v, phase
        if v <= V_TERM:
            return False, t, v, phase
        t += dt
    return False, t, mis.v, phase


def exp_e1(outdir, n=120, models=("linear",)):
    """弹速 × 掉头距离 → 躲避成功率"""
    v0s = [1000, 1500, 2000, 2500, 3000]
    rts = [10, 20, 30, 40, 50, 60]
    rows = []
    for model in models:
        for v0 in v0s:
            for rt in rts:
                hits = 0
                for i in range(n):
                    bearing = (np.random.random() - 0.5) * 20.0
                    hit = run_intercept(v0, rt, bearing, model=model)[0]
                    hits += int(hit)
                rows.append({"model": model, "v0_kmh": v0, "r_turn_km": rt,
                             "n": n, "hits": hits,
                             "kill_rate": hits / n,
                             "dodge_rate": 1 - hits / n})
                print(f"  E1 {model} V0={v0:5d} R={rt:3d}km "
                      f"击杀率={hits/n:.2f}", flush=True)
    path = os.path.join(outdir, "e1_dodge.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"→ {path}")
    return rows


# ----------------------------------------------------------------- E2
def max_hit_range(v0_kmh, v_target_kmh, model="linear", lo=1.0, hi=200.0,
                  tol=0.5):
    """二分求临界距离 d0：目标匀速逃逸时，弹刚好能在能量耗尽前追上"""
    def hits(d):
        # 目标沿正东逃逸，导弹从正西朝东追（迎头后追尾）
        ac = Body(x=d, y=0.0, z=8.0, psi=0.0, v=v_target_kmh)
        mis = Body(x=0.0, y=0.0, z=8.0, psi=0.0, v=v0_kmh)
        t = 0.0
        while t < T_MAX:
            if np.linalg.norm(ac.pos - mis.pos) < R_KILL:
                return True
            av = kmh(ac.v) * DT
            ac.x += av * math.cos(ac.psi)
            ac.y += av * math.sin(ac.psi)
            v = step_pursuer(mis, ac, t, v0_kmh, model)
            if v <= V_TERM:
                return False
            t += DT
        return False
    if not hits(lo):
        return 0.0
    if hits(hi):
        return hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if hits(mid):
            lo = mid
        else:
            hi = mid
    return lo


def exp_e2(outdir):
    """追击模型求 d0 + 三种开火策略命中率"""
    v0s = [1500, 2000, 2500, 3000, 3500]
    vts = [800, 900, 1000, 1100, 1200]
    rows = []
    for v0 in v0s:
        for vt in vts:
            d0 = max_hit_range(v0, vt)
            rows.append({"v0_kmh": v0, "v_target_kmh": vt, "d0_km": round(d0, 1)})
            print(f"  E2 V0={v0} V敌={vt} → d0={d0:.1f} km", flush=True)
    path = os.path.join(outdir, "e2_d0.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # 三种开火策略命中率：0.8 d0 / ¾ d0 / 最大射程
    pol = []
    for v0 in v0s:
        vt = 1000
        d0 = max_hit_range(v0, vt)
        for name, frac, cap in (("0.8·d0", 0.8, None),
                                ("0.75·d0", 0.75, None),
                                ("最大射程 90nm", None, 90 * NM_KM)):
            d_fire = cap if cap is not None else d0 * frac
            hit = 0
            n = 40
            for _ in range(n):
                hit += int(max_hit_range(v0, vt) >= d_fire)
            pol.append({"v0_kmh": v0, "policy": name,
                        "d_fire_km": round(min(d_fire, 200), 1),
                        "in_range_rate": hit / n})
    path = os.path.join(outdir, "e2_policy.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(pol[0]))
        w.writeheader()
        w.writerows(pol)
    print(f"→ {path}")
    return rows, pol


# ----------------------------------------------------------------- E3
def _flight(p_ac, psi_ac, v_ac, p_mis, v0, model, t_max=T_MAX,
            callbacks=(), climb=False):
    """
    通用单次交战内核：目标匀速直线，导弹纯追踪 + 限转角 + 能量衰减。
    callbacks: [(t, fn)] ，在 t 时刻调用 fn(state) 修改目标航向（规则型决策）。
    返回 dict(hit, t, v_end, dmin)
    """
    ac = Body(x=p_ac[0], y=p_ac[1], z=p_ac[2], psi=psi_ac, v=v_ac)
    mis = Body(x=p_mis[0], y=p_mis[1], z=p_mis[2], psi=math.atan2(
        p_ac[1] - p_mis[1], p_ac[0] - p_mis[0]), v=v0)
    t = 0.0
    fired = set()
    dmin_all = 1e9
    g = 9.81
    v_pen = 0.0           # 累计比能量亏损 (m^2/s^2)：爬升为正、俯冲为负
    while t < t_max:
        for i, (tc, fn) in enumerate(callbacks):
            if i not in fired and t >= tc:
                fired.add(i)
                fn(ac, mis, t)
        p_prev = ac.pos - mis.pos
        av = kmh(ac.v) * DT
        ac.x += av * math.cos(ac.psi)
        ac.y += av * math.sin(ac.psi)
        v_nom = speed_of(model, v0, t)
        v = v_nom
        if climb:
            # 比能量亏损累计：爬升 dh>0 扣 v^2，俯冲 dh<0 补 v^2
            dist3 = max(float(np.linalg.norm(ac.pos - mis.pos)), 1e-6)
            dh = (ac.z - mis.z) / dist3 * kmh(v_nom) * DT * 1000.0   # m
            v_pen += 2.0 * g * dh
            v_nom_ms = v_nom / 3.6
            v = math.sqrt(max(v_nom_ms ** 2 - v_pen, 1.0)) * 3.6
        sv = kmh(v) * DT
        # 导弹：限转角后推进
        d = ac.pos - mis.pos
        if math.hypot(d[0], d[1]) > 1e-9:
            want = math.atan2(d[1], d[0])
            dp = wrap(want - mis.psi)
            lim = OMEGA_MAX * DT
            mis.psi += max(-lim, min(lim, dp))
        mis.x += sv * math.cos(mis.psi)
        mis.y += sv * math.sin(mis.psi)
        dist = max(float(np.linalg.norm(ac.pos - mis.pos)), 1e-6)
        mis.z += (ac.z - mis.z) / dist * sv
        p_now = ac.pos - mis.pos
        dmin, _ = closest_approach(p_prev, (p_now - p_prev) / DT, DT)
        dmin_all = min(dmin_all, dmin)
        if dmin < R_KILL:
            return {"hit": True, "t": t, "v_end": v, "dmin": dmin}
        if v <= V_TERM:
            return {"hit": False, "t": t, "v_end": v, "dmin": dmin_all}
        t += DT
    return {"hit": False, "t": t, "v_end": v, "dmin": dmin_all}


def _critical_range(launch, ac_psi, v_t, mis_pos, v0, model="linear",
                    climb=True, lo=0.5, hi=300.0, tol=0.4):
    """二分求最大可命中交距：launch 为初始水平距离"""
    def ok(d):
        p_ac = (d * math.cos(0.0), 0.0, 8.0) if ac_psi == 0.0 else (d, 0.0, 8.0)
        r = _flight(p_ac, ac_psi, v_t, mis_pos, v0, model, climb=climb,
                    t_max=T_MAX)
        return r["hit"]
    if not ok(lo):
        return 0.0
    if ok(hi):
        return hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def exp_e3(outdir, n=60):
    """
    高度差对**有效交距**的影响（讲解 17:19–18:17：双方同高；高打低好打、低打高不好打）

    高度比 = 射击方高度 / 目标高度 ∈ {0.80,0.90,1.00,1.10,1.20}
    指标：
      d0_km      尾追临界发射距离（二分求得，目标匀速逃逸）
      命中率     在固定交距 d_fixed 处的命中率
    物理：导弹爬升/俯冲需消耗比能量 → 有效速度按 climb_penalty 折减。
    """
    ratios = [0.80, 0.90, 1.00, 1.10, 1.20]
    v0, h_t, v_t = 2500.0, 8.0, 1000.0    # h_t 单位 km
    d_fixed = 36.0
    rows = []
    for ratio in ratios:
        h_s = h_t / ratio
        d0 = _critical_range(d_fixed, 0.0, v_t, (0.0, 0.0, h_s), v0, climb=True)
        hits = 0
        for _ in range(n):
            r = _flight((d_fixed, 0.0, h_t), 0.0, v_t, (0.0, 0.0, h_s), v0,
                        "linear", climb=True)
            hits += int(r["hit"])
        rows.append({"h_target_m": int(h_t * 1000),
                     "h_shooter_m": int(h_s * 1000),
                     "ratio_shooter_over_target": round(ratio, 2),
                     "d0_km": round(d0, 1), "d_fixed_km": d_fixed,
                     "v0_kmh": v0, "v_target_kmh": v_t,
                     "n": n, "hits": hits, "hit_rate": round(hits / n, 3)})
        print(f"  E3 高度比={ratio:.2f} (射击方 {h_s*1000:.0f} m) "
              f"d0={d0:.1f} km 命中率={hits/n:.2f}", flush=True)
    path = os.path.join(outdir, "e3_altitude.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"→ {path}")
    return rows


def exp_e4(outdir, n=150):
    """
    地空导弹营：开火距离占 Dmax 的比例 → 拦截成功率
    （讲解 02:20 记为 3/5 Dmax 发弹；此处对比 0.2–1.0 Dmax）

    先由模型二分求出该弹对 900 km/h 迎头目标的**最大可拦截距离**，作为 Dmax，
    再在该比例序列上统计拦截率。
    """
    v0, v_t = 3000.0, 900.0
    dmax = _critical_range(60.0, math.pi, v_t, (0.0, 0.0, 0.0), v0, climb=True)
    print(f"  E4 模型最大可拦截距离 Dmax ≈ {dmax:.1f} km")
    fracs = [0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
    R_MIN = 15.0        # km，最近开火距离（再近来不及）
    RELOAD_GAP = 10.0   # km，两次射击之间的目标位移（约等于再装填 8 s 的接近量）
    rows = []
    for f_ in fracs:
        d_fire = dmax * f_
        hits, v_ends = 0, []
        for _ in range(n):
            r = _flight((d_fire, 0.0, 8.0), math.pi, v_t,
                        (0.0, 0.0, 0.0), v0, "linear", climb=True)
            hits += int(r["hit"])
            if r["hit"]:
                v_ends.append(r["v_end"])
        p_geo = hits / n                       # 运动学能否到达
        v_end = float(np.mean(v_ends)) if v_ends else 0.0
        # 端game 能量裕度 → 单发杀伤概率
        margin = max(0.0, (v_end - V_TERM) / (0.6 * v0))
        p_single = min(1.0, margin) * p_geo
        # 可用射击次数：从 d_fire 打到 R_MIN 之间能安排几次
        salvos = max(1, min(2, int((d_fire - R_MIN) / RELOAD_GAP) + 1))
        p_total = 1 - (1 - p_single) ** salvos
        rows.append({"dmax_km": round(dmax, 1), "fire_fraction": f_,
                     "d_fire_km": round(d_fire, 1), "v0_kmh": v0,
                     "v_target_kmh": v_t, "n": n, "kinematic_hit_rate": p_geo,
                     "v_end_kmh": round(v_end, 0),
                     "p_single_shot": round(p_single, 3),
                     "salvos": salvos,
                     "p_intercept_total": round(p_total, 3)})
        print(f"  E4 开火比例={f_:.1f}Dmax ({d_fire:.0f} km) "
              f"末端速度={v_end:.0f} km/h 单发P={p_single:.2f} "
              f"射击次数={salvos} 综合P={p_total:.2f}", flush=True)
    path = os.path.join(outdir, "e4_sam.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"→ {path}")
    return rows


def exp_e5(outdir, n=2000):
    """
    船只自卫：弹药受限下的三种拦截方案（讲解 09:00–09:36）

    设定
      * 单发拦截概率随距离递减：p(d) = p_far + (p_near-p_far)*(1-d/dmax)
        d=dmax → 0.35；d=0   → 0.90        （自设，报告中注明）
      * 每船弹舱 K=8 发；一波 8 枚来袭反舰弹
      * 方案
        S1 单船单层  仅 A 船，Dmax 与 ½Dmax 各射一发（2 发/枚）
        S2 双船同时  A、B 均在 Dmax 同时各射一发（2 发/枚，都在远界）
        S3 双船分层  A 在 Dmax 射 1 发；未被拦下则 B 在 ½Dmax 补 1 发
    指标：拦截率、单目标平均弹耗、每拦截一枚的弹耗、弹舱打空率
    """
    dmax = 60.0
    p_far, p_near = 0.35, 0.90
    n_inbound = 8
    K = 8

    def p_kill(d):
        d = min(d, dmax)
        return p_far + (p_near - p_far) * (1 - d / dmax)

    rows = []
    for name in ("S1 单船单层", "S2 双船同时MAX", "S3 双船分层"):
        killed_total = 0
        shots = 0
        dry = 0
        for _ in range(n):
            mag = {"A": K, "B": K}
            for _m in range(n_inbound):
                killed = False
                if name == "S1 单船单层":
                    for d in (dmax, dmax * 0.5):
                        if killed or mag["A"] <= 0:
                            break
                        mag["A"] -= 1; shots += 1
                        if np.random.random() < p_kill(d):
                            killed = True
                elif name == "S2 双船同时MAX":
                    for ship in ("A", "B"):
                        if killed or mag[ship] <= 0:
                            continue
                        mag[ship] -= 1; shots += 1
                        if np.random.random() < p_kill(dmax):
                            killed = True
                else:
                    if mag["A"] > 0:
                        mag["A"] -= 1; shots += 1
                        if np.random.random() < p_kill(dmax):
                            killed = True
                    if not killed and mag["B"] > 0:
                        mag["B"] -= 1; shots += 1
                        if np.random.random() < p_kill(dmax * 0.5):
                            killed = True
                if killed:
                    killed_total += 1
            if mag["A"] <= 0 or (name != "S1 单船单层" and mag["B"] <= 0):
                dry += 1
        tot_in = n * n_inbound
        rows.append({"scheme": name, "n": n, "inbound_per_run": n_inbound,
                     "magazine_per_ship": K,
                     "intercept_rate": round(killed_total / tot_in, 4),
                     "shots_per_inbound": round(shots / tot_in, 3),
                     "shots_per_kill": round(shots / max(killed_total, 1), 3),
                     "magazine_dry_rate": round(dry / n, 4)})
        print(f"  E5 {name}: 拦截率={killed_total/tot_in:.3f} "
              f"弹耗/枚={shots/tot_in:.2f} 弹耗/拦截={shots/max(killed_total,1):.2f} "
              f"弹舱打空率={dry/n:.2f}", flush=True)
    path = os.path.join(outdir, "e5_ship.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"→ {path}")
    return rows


# ----------------------------------------------------------------- 出图
def make_figures(outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm

    # 中文字体
    for p in ("/nix/store/9n90ncp7hilfk9jisq2h24w6d7axysf4-source-han-sans-2.005"
              "/share/fonts/truetype/SourceHanSans.ttc",):
        if os.path.exists(p):
            fm.fontManager.addfont(p)
            plt.rcParams["font.family"] = "Source Han Sans"
            break
    plt.rcParams["axes.unicode_minus"] = False
    figs = []

    # E1 三维曲面
    p = os.path.join(outdir, "e1_dodge.csv")
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        v0s = sorted({int(r["v0_kmh"]) for r in rows})
        rts = sorted({int(r["r_turn_km"]) for r in rows})
        Z = np.zeros((len(v0s), len(rts)))
        for r in rows:
            Z[v0s.index(int(r["v0_kmh"])), rts.index(int(r["r_turn_km"]))] = \
                float(r["kill_rate"])
        X, Y = np.meshgrid(rts, v0s)
        fig = plt.figure(figsize=(7.2, 5.2))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="k", linewidth=0.3,
                        alpha=0.9)
        ax.set_xlabel("掉头距离 / km")
        ax.set_ylabel("来袭弹速 / (km/h)")
        ax.set_zlabel("被击落概率")
        ax.set_title("空战躲避：弹速 × 掉头距离 → 被击落概率")
        f = os.path.join(outdir, "fig_e1_dodge_surface.png")
        fig.tight_layout(); fig.savefig(f, dpi=200); plt.close(fig); figs.append(f)

        fig, ax = plt.subplots(figsize=(6.4, 4.2))
        for i, v0 in enumerate(v0s):
            ax.plot(rts, Z[i], marker="o", label=f"V弹={v0} km/h")
        ax.set_xlabel("掉头距离 / km"); ax.set_ylabel("躲避成功率")
        ax.set_title("不同弹速下掉头距离对躲避成功率的影响")
        ax.grid(alpha=0.3); ax.legend(fontsize=8)
        f = os.path.join(outdir, "fig_e1_dodge_lines.png")
        fig.tight_layout(); fig.savefig(f, dpi=200); plt.close(fig); figs.append(f)

    # E2 d0 曲面 + 等值线
    p = os.path.join(outdir, "e2_d0.csv")
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        v0s = sorted({int(r["v0_kmh"]) for r in rows})
        vts = sorted({int(r["v_target_kmh"]) for r in rows})
        Z = np.zeros((len(v0s), len(vts)))
        for r in rows:
            Z[v0s.index(int(r["v0_kmh"])), vts.index(int(r["v_target_kmh"]))] = \
                float(r["d0_km"])
        X, Y = np.meshgrid(vts, v0s)
        fig, ax = plt.subplots(figsize=(6.4, 4.4))
        cs = ax.contourf(X, Y, Z, levels=12, cmap="magma")
        fig.colorbar(cs, label="临界距离 d0 / km")
        ax.set_xlabel("目标速度 / (km/h)"); ax.set_ylabel("导弹初速 / (km/h)")
        ax.set_title("追击模型求得的临界发射距离 d₀")
        f = os.path.join(outdir, "fig_e2_d0_contour.png")
        fig.tight_layout(); fig.savefig(f, dpi=200); plt.close(fig); figs.append(f)

    # E3 高度比
    p = os.path.join(outdir, "e3_altitude.csv")
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        x = [float(r["ratio_shooter_over_target"]) for r in rows]
        y = [float(r["hit_rate"]) for r in rows]
        fig, ax = plt.subplots(figsize=(6.0, 4.0))
        ax.plot(x, y, "o-", color="#2b6cb0")
        ax.axvline(1.0, ls="--", c="gray", lw=1)
        ax.set_xlabel("高度比（射击方高度 / 目标高度）"); ax.set_ylabel("命中率")
        ax.set_title("高低差对空空导弹命中率的影响")
        ax.grid(alpha=0.3)
        f = os.path.join(outdir, "fig_e3_altitude.png")
        fig.tight_layout(); fig.savefig(f, dpi=200); plt.close(fig); figs.append(f)

    # E4 开火比例
    p = os.path.join(outdir, "e4_sam.csv")
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        x = [float(r["fire_fraction"]) for r in rows]
        y = [float(r["p_intercept_total"]) for r in rows]
        fig, ax = plt.subplots(figsize=(6.0, 4.0))
        ax.plot(x, y, "s-", color="#c53030")
        ax.axvline(0.6, ls="--", c="gray", lw=1)
        ax.annotate("3/5 Dmax", xy=(0.6, min(y)), xytext=(0.62, min(y) + 0.02),
                    fontsize=9)
        ax.set_xlabel("开火距离 / Dmax"); ax.set_ylabel("综合拦截概率")
        ax.set_title("地空导弹营：开火时机对综合拦截概率的影响")
        ax.grid(alpha=0.3)
        f = os.path.join(outdir, "fig_e4_sam.png")
        fig.tight_layout(); fig.savefig(f, dpi=200); plt.close(fig); figs.append(f)

    # E5 方案对比
    p = os.path.join(outdir, "e5_ship.csv")
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        names = [r["scheme"] for r in rows]
        rate = [float(r["intercept_rate"]) for r in rows]
        shots = [float(r["shots_per_inbound"]) for r in rows]
        idx = np.arange(len(names))
        fig, ax1 = plt.subplots(figsize=(7.0, 4.2))
        ax1.bar(idx - 0.2, rate, 0.4, label="拦截率", color="#2b6cb0")
        ax1.set_ylabel("拦截率"); ax1.set_ylim(0, 1.05)
        ax2 = ax1.twinx()
        ax2.bar(idx + 0.2, shots, 0.4, label="单目标平均弹耗", color="#dd6b20")
        ax2.set_ylabel("单目标平均弹耗 / 枚")
        ax1.set_xticks(idx); ax1.set_xticklabels(names, fontsize=9)
        ax1.set_title("船只自卫：三种拦截方案的效能与代价")
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
        f = os.path.join(outdir, "fig_e5_ship.png")
        fig.tight_layout(); fig.savefig(f, dpi=200); plt.close(fig); figs.append(f)

    print("图：")
    for f in figs:
        print("  ", f)
    return figs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["all", "e1", "e2", "e3", "e4", "e5", "fig"])
    ap.add_argument("--out", default="docs/实验")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    np.random.seed(args.seed)
    if args.which in ("all", "e1"):
        exp_e1(args.out, n=args.n or 120)
    if args.which in ("all", "e2"):
        exp_e2(args.out)
    if args.which in ("all", "e3"):
        exp_e3(args.out, n=args.n or 80)
    if args.which in ("all", "e4"):
        exp_e4(args.out, n=args.n or 200)
    if args.which in ("all", "e5"):
        exp_e5(args.out, n=(args.n or 400) // 4)
    if args.which in ("all", "fig"):
        make_figures(args.out)


if __name__ == "__main__":
    main()
