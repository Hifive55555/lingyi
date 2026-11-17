"""两处结构性假设的稳健性扫描：船只的概率曲线与弹舱、地导的能量裕度系数。

与第 8 章的一次一变（OAT）不同，这里扫的是"模型形式"而不是"参数取值"：
p(d) 的形状、弹舱容量 K、能量裕度分母系数 c 都是我们自己设的，必须验证
主要结论不依赖它们。

输出：c_ship_probshape.csv、c_ship_magazine.csv、d_sam_margin.csv
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from comparative import (  # noqa: E402
    _critical_range, _flight_sam, _write,
)

V_TERM = 500.0


# ------------------------------------------------------------------ 船只
def _run_scheme(layers, size, runs, rng, dmax, p_far, p_near, K):
    def pk(d):
        d = min(d, dmax)
        return p_far + (p_near - p_far) * (1 - d / dmax)

    killed = 0
    dists = []
    for _ in range(runs):
        mag = {s: K for s, _ in layers}
        for _m in range(size):
            for ship, frac in layers:
                if mag[ship] <= 0:
                    continue
                mag[ship] -= 1
                if rng.random() < pk(dmax * frac):
                    killed += 1
                    dists.append(dmax * frac)
                    break
    return killed / (runs * size), (float(np.mean(dists)) if dists else 0.0)


SCHEMES = {
    "R 双舰分层": [("A", 1.0), ("B", 0.5)],
    "B1 单舰双层": [("A", 1.0), ("A", 0.5)],
    "B2 双舰同时MAX": [("A", 1.0), ("B", 1.0)],
    "B3 双舰均½Dmax": [("A", 0.5), ("B", 0.5)],
}


def ship_probshape(outdir, runs=200, seed=2026):
    """概率曲线形状：远端 0.20/0.35/0.50 × 近端 0.75/0.90/1.00"""
    rng = np.random.default_rng(seed)
    rows = []
    for p_far in (0.20, 0.35, 0.50):
        for p_near in (0.75, 0.90, 1.00):
            for name, layers in SCHEMES.items():
                rate, dist = _run_scheme(layers, 8, runs, rng, 60.0, p_far, p_near, 8)
                rows.append({"p_far": p_far, "p_near": p_near, "scheme": name,
                             "intercept_rate": round(rate, 4),
                             "mean_range_km": round(dist, 2)})
            r = {x["scheme"]: x["intercept_rate"] for x in rows[-4:]}
            print(f"  S1 p_far={p_far:.2f} p_near={p_near:.2f} "
                  f"R={r['R 双舰分层']:.3f} B3={r['B3 双舰均½Dmax']:.3f}", flush=True)
    _write(outdir, "c_ship_probshape.csv", rows)
    return rows


def ship_magazine(outdir, runs=200, seed=2026):
    """弹舱容量：K = 4/6/8/12（8 枚来袭，概率曲线取默认 0.35→0.90）"""
    rng = np.random.default_rng(seed)
    rows = []
    for K in (4, 6, 8, 12):
        for name, layers in SCHEMES.items():
            rate, dist = _run_scheme(layers, 8, runs, rng, 60.0, 0.35, 0.90, K)
            rows.append({"magazine": K, "scheme": name,
                         "intercept_rate": round(rate, 4),
                         "mean_range_km": round(dist, 2)})
        r = {x["scheme"]: x["intercept_rate"] for x in rows[-4:]}
        print(f"  S2 K={K:2d} R={r['R 双舰分层']:.3f} B1={r['B1 单舰双层']:.3f}", flush=True)
    _write(outdir, "c_ship_magazine.csv", rows)
    return rows


# ------------------------------------------------------------------ 地导
def sam_margin(outdir, n=300, seed=2026):
    """能量裕度分母系数 c：p = min(1, (V_end - 500) / (c V0))

    飞行段与 c 无关，先按 (V0, frac) 跑一次仿真拿到 p_geo 与 V_end，
    再对每个 c 解析地重算综合拦截概率。
    """
    rng = np.random.default_rng(seed)
    fr = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    rows = []
    for v0 in (2500.0, 3000.0, 3500.0):
        va = 900.0
        dmax = _critical_range(60.0, math.pi, va, (0.0, 0.0, 0.0), v0, climb=True)
        geo, vend = {}, {}
        for frac in fr:
            d_fire = dmax * frac
            hit, vs = 0, []
            for _ in range(n):
                r = _flight_sam(d_fire, v0, va, rng)
                hit += int(r["hit"])
                if r["hit"]:
                    vs.append(r["v_end"])
            geo[frac] = hit / n
            vend[frac] = float(np.mean(vs)) if vs else 0.0
        for c in (0.4, 0.5, 0.6, 0.7, 0.8, 1.0):
            best_frac, best_p = None, -1.0
            for frac in fr:
                margin = max(0.0, (vend[frac] - V_TERM) / (c * v0))
                p1 = min(1.0, margin) * geo[frac]
                salvos = max(1, min(2, int((dmax * frac - 15.0) / 10.0) + 1))
                p = 1 - (1 - p1) ** salvos
                rows.append({"v0": v0, "dmax_km": round(dmax, 1), "c_margin": c,
                             "fire_fraction": frac, "p_total": round(p, 4)})
                if p > best_p:
                    best_p, best_frac = p, frac
            p06 = [r["p_total"] for r in rows[-9:] if r["fire_fraction"] == 0.6][0]
            print(f"  S3 V0={v0:.0f} c={c:.1f} 最优={best_frac:.1f}Dmax "
                  f"({best_p:.3f})，0.6Dmax={p06:.3f}", flush=True)
    _write(outdir, "d_sam_margin.csv", rows)
    return rows


def main():
    out = os.path.join(os.path.dirname(HERE), "data")
    print("[S1] 船只概率曲线形状")
    ship_probshape(out)
    print("[S2] 船只弹舱容量")
    ship_magazine(out)
    print("[S3] 地导能量裕度系数")
    sam_margin(out)


if __name__ == "__main__":
    main()
