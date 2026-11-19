#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""配色体检：把「科研绘图方法」里能自动判定的几条落成检查项。

检查项（对应文献里的硬性建议）
1. 分类色两两可分：CIE76 ΔE ≥ 20（正常视觉）
2. 色觉障碍安全：红绿色盲（deutan / protan）模拟后 ΔE ≥ 12
3. 灰度安全：去色后相邻梯度亮度差 ≥ 4（L*）
4. 顺序梯度单调：L* 单调递减，无"彩虹"
5. 对比度：正文/轴线对白底 ≥ 4.5:1（WCAG AA），图元描边 ≥ 3:1
6. 图内色相数 ≤ 5（含中性）：数现有 PNG 的主色，抓"彩虹流程图"残留

用法
    python figstyle_audit.py                 # 调色板体检 + 全部图扫描
    python figstyle_audit.py --palette       # 只看调色板
    python figstyle_audit.py --figures ../figures/*.png
    python figstyle_audit.py --cvd fig.png   # 出一张模拟色盲效果图
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as F  # noqa: E402

# ---------------------------------------------------------------- 色彩空间
def hex2rgb255(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def to_linear(rgb):
    c = rgb / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def rel_lum(rgb):
    r, g, b = to_linear(np.asarray(rgb, float))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


M_RGB2XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                      [0.2126729, 0.7151522, 0.0721750],
                      [0.0193339, 0.1191920, 0.9503041]])
WHITE = np.array([0.95047, 1.0, 1.08883])


def lab(rgb):
    xyz = M_RGB2XYZ @ to_linear(np.asarray(rgb, float))
    t = xyz / WHITE
    f = np.where(t > 216 / 24389, np.cbrt(t), (24389 / 27 * t + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def delta_e(c1, c2):
    return float(np.linalg.norm(lab(c1) - lab(c2)))


# Viénot/Brettel 简化的红绿色盲模拟（LMS 空间投影）
_LMS = np.array([[17.8824, 43.5161, 4.11935],
                 [3.45565, 27.1554, 3.86714],
                 [0.0299566, 0.184309, 1.46709]])
_LMS_INV = np.linalg.inv(_LMS)
_SIM = {
    "deutan": np.array([[1.0, 0.0, 0.0], [0.494207, 0.0, 1.24827], [0.0, 0.0, 1.0]]),
    "protan": np.array([[0.0, 2.02344, -2.52581], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
}


def simulate_cvd(rgb, kind="deutan", strength=1.0):
    rgb = np.asarray(rgb, float)
    lin = to_linear(rgb) * 255.0
    out = _LMS_INV @ _SIM[kind] @ _LMS @ lin
    out = np.clip(out / 255.0, 0, 1)
    srgb = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
    srgb = np.clip(srgb * 255, 0, 255)
    if strength < 1.0:
        srgb = strength * srgb + (1 - strength) * rgb
    return np.round(srgb).astype(int)


# ---------------------------------------------------------------- 检查项
OK, WARN, FAIL = "ok  ", "WARN", "FAIL"


def report_row(name, value, level, note=""):
    print(f"  [{level}] {name:<22} {value}{('  ' + note) if note else ''}")
    return level == FAIL


def audit_palette():
    print("\n== 1. 分类色两两可分（ΔE ≥ 20）==")
    cats = F.CATEGORICAL
    worst = (999, None)
    for i in range(len(cats)):
        for j in range(i + 1, len(cats)):
            d = delta_e(hex2rgb255(cats[i]), hex2rgb255(cats[j]))
            if d < worst[0]:
                worst = (d, (cats[i], cats[j]))
    lvl = FAIL if worst[0] < 20 else (WARN if worst[0] < 25 else OK)
    report_row(f"{len(cats)} 色最小 ΔE", f"{worst[0]:.1f}", lvl,
               f"{worst[1][0]} vs {worst[1][1]}" if worst[0] < 25 else "")

    print("\n== 2. 色觉障碍安全（模拟后 ΔE ≥ 12）==")
    for kind in ("deutan", "protan"):
        worst = (999, None)
        for i in range(len(cats)):
            for j in range(i + 1, len(cats)):
                a = simulate_cvd(hex2rgb255(cats[i]), kind)
                b = simulate_cvd(hex2rgb255(cats[j]), kind)
                d = delta_e(a, b)
                if d < worst[0]:
                    worst = (d, (cats[i], cats[j]))
        lvl = FAIL if worst[0] < 12 else (WARN if worst[0] < 18 else OK)
        report_row(f"{kind} 最小 ΔE", f"{worst[0]:.1f}", lvl,
                   f"{worst[1][0]} vs {worst[1][1]}" if worst[0] < 18 else "")

    print("\n== 3. 顺序梯度（L* 必须单调）==")
    for nm, ramp in (("SEQ", F.SEQ), ("RAMP[indigo]", F.RAMP["indigo"])):
        ls = [lab(hex2rgb255(c))[0] for c in ramp]
        mono = all(b < a for a, b in zip(ls, ls[1:]))
        gaps = [a - b for a, b in zip(ls, ls[1:])]
        lvl = OK if mono and min(gaps) >= 4 else FAIL
        report_row(nm, " ".join(f"{v:.0f}" for v in ls), lvl,
                   f"最小跨步 {min(gaps):.1f}" if min(gaps) < 6 else "")

    print("\n== 4. 对比度（对白底）==")
    for nm, c, need in (("INK 正文", F.INK, 4.5), ("MID 次级文字", F.MID, 4.5),
                        ("INDIGO 线", F.INDIGO, 3.0), ("BRICK 线", F.BRICK, 3.0),
                        ("TEAL 线", F.TEAL, 3.0), ("SAND 线", F.SAND, 3.0),
                        ("SOFT 弱化", F.SOFT, 1.0), ("GRID 网格", F.GRID, 1.0)):
        r = contrast(hex2rgb255(c), np.array([255, 255, 255]))
        lvl = OK if r >= need else FAIL
        report_row(nm, f"{r:.1f}:1", lvl, f"需 ≥ {need}" if r < need else "")

    print("\n== 5. 语义色在灰度下的可分性（L* 差）==")
    pairs = [("INDIGO/BRICK", F.INDIGO, F.BRICK), ("INDIGO/TEAL", F.INDIGO, F.TEAL),
             ("BRICK/TEAL", F.BRICK, F.TEAL), ("MID/INK", F.MID, F.INK)]
    for nm, a, b in pairs:
        g = abs(lab(hex2rgb255(a))[0] - lab(hex2rgb255(b))[0])
        lvl = OK if g >= 10 else (WARN if g >= 6 else FAIL)
        report_row(nm, f"ΔL* {g:.1f}", lvl, "需 ≥ 10（否则打印/黑白会糊）" if g < 10 else "")


# ---------------------------------------------------------------- 图扫描
def scan_figure(path, min_frac=0.004):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((900, 900))
    a = np.asarray(im).reshape(-1, 3)
    # 去掉接近白的底与抗锯齿杂色
    q = (a // 8) * 8 + 4
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)
    tot = counts.sum()
    out = []
    for i in order:
        frac = counts[i] / tot
        if frac < min_frac:
            break
        c = keys[i]
        if rel_lum(c) > 0.93:          # 白底
            continue
        out.append((tuple(int(v) for v in c), frac))
        if len(out) >= 14:
            break
    # 按色相归族
    import colorsys
    fams = {}
    for c, frac in out:
        h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in c])
        if s < 0.10 or (s < 0.18 and v > 0.85):
            k = "gray"
        elif h < 0.045 or h >= 0.94:
            k = "red"
        elif h < 0.14:
            k = "orange"
        elif h < 0.20:
            k = "sand"
        elif h < 0.45:
            k = "green-teal"
        elif h < 0.56:
            k = "cyan"
        elif h < 0.72:
            k = "blue"
        elif h < 0.87:
            k = "violet"
        else:
            k = "magenta"
        fams[k] = fams.get(k, 0) + frac
    named = {k: round(v, 3) for k, v in sorted(fams.items(), key=lambda x: -x[1]) if v >= 0.01}
    return named


def audit_figures(paths):
    print("\n== 6. 逐图扫描：非中性色族数 ≤ 4 ==")
    bad = []
    for p in sorted(paths):
        try:
            fams = scan_figure(p)
        except Exception as e:  # pragma: no cover
            print(f"  [skip] {os.path.basename(p)}: {e}")
            continue
        chroma = {k: v for k, v in fams.items() if k != "gray"}
        lvl = OK if len(chroma) <= 4 else WARN
        if len(chroma) > 4:
            bad.append(os.path.basename(p))
        print(f"  [{lvl}] {os.path.basename(p):<34} "
              f"{len(chroma)} 色族  " + " ".join(f"{k}:{v}" for k, v in fams.items()))
    if bad:
        print("\n  色族偏多（考虑合并）: " + ", ".join(bad))
    return bad


def cvd_preview(path, out_prefix):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(float)
    h, w, _ = a.shape
    flat = a.reshape(-1, 3)
    panels = [np.asarray(im)]
    for kind in ("deutan", "protan"):
        sim = np.array([simulate_cvd(c, kind) for c in flat], dtype=np.uint8)
        panels.append(sim.reshape(h, w, 3))
    # 灰度
    g = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
    panels.append(np.repeat(g[..., None], 3, axis=2).astype(np.uint8))
    sheet = Image.new("RGB", (w, h * 4 + 30), "white")
    for i, p in enumerate(panels):
        sheet.paste(Image.fromarray(p.astype(np.uint8)), (0, i * (h + 10)))
    out = out_prefix + "-cvd.png"
    sheet.save(out)
    print(f"  → {out}  （正常 / deutan / protan / 灰度）")


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    args = argv[1:]
    if args and args[0] == "--cvd":
        cvd_preview(args[1], args[2] if len(args) > 2 else "/tmp/cvd")
        return
    if "--palette" not in args:
        pl = args[args.index("--figures") + 1:] if "--figures" in args else \
            sorted(glob.glob(os.path.join(figdir, "*.png")))
    else:
        pl = []
    print("=" * 66)
    print(" 报告配色体检 ｜ 主体色 靛蓝 #1f3b5c，强调 朱砂 #b23a2b")
    print("=" * 66)
    audit_palette()
    if pl:
        audit_figures(pl)
    print()


if __name__ == "__main__":
    main(sys.argv)
