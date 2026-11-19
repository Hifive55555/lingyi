#!/usr/bin/env python
"""图：CPA（最近接近点）判定的几何示意 —— 单面板、只画几何。

只画几何的理由：三条判据（90 km / 3 km / 900 s）是三个数，画成三根"算 / 不算"的标尺
并不能让读者多看出一件事；这张图要回答的只有一个问题——为什么不按当前距离筛，
而要按最近接近点判。三条门限写在正文与伪代码里。

配色沿用全文约定：红＝本方（本机），蓝＝敌方（来袭弹）。
画布按"内容外接框"给，`#figure` 里居中插入后左右自动对称，不会偏。

输出：paper/shared/schematics/schema-3-cpa.{svg,png,pdf}
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
OUT = os.path.join(PAPER, "schematics")

GRAY = "#3d4248"     # 几何线
MID = "#5f676d"      # 次要文字
RED = "#c62f2f"      # 本方（本机）
BLUE = "#2f6db3"     # 敌方（来袭弹）

# ---- 几何：先定本机与航迹方向，垂足与弹位由此推出 -------------------------
A = (150.0, 190.0)                  # 本机
U = (-0.900, 0.436)                 # 相对速度方向（单位向量，指向左下）
MISS = 110.0                        # 脱靶量（到航迹的垂距）
C = (A[0] + U[1] * MISS, A[1] - U[0] * MISS)      # 垂足（CPA）：本机沿法向 (u_y, -u_x) 投到航迹上
M0 = (C[0] - 330 * U[0], C[1] - 330 * U[1])       # 来袭弹当前位置
V_LEN = 160.0
V_END = (M0[0] + V_LEN * U[0], M0[1] + V_LEN * U[1])
P_OUT = (M0[0] - 130 * U[0], M0[1] - 130 * U[1])  # 航迹来向
P_IN = (C[0] + 200 * U[0], C[1] + 200 * U[1])     # 航迹去向

FS, FS_B = 16, 17                   # 正文标注 / 主体名称（画布像素），见文末 K 的说明
K = 0.90                            # 场景坐标缩放：整幅图缩到 0.9，字按 1/0.9 画回去，
                                    # 于是印出来"图小了、字没小"。


def line(x1, y1, x2, y2, color=GRAY, w=1.5, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d}{m}/>')


def text(x, y, s, size=FS, color=GRAY, weight="400", anchor="start"):
    # 字号除以 K：外层 <g scale(K)> 会把它乘回去，最终仍是指定的像素大小
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size / K:.2f}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def aircraft(x, y, scale=1.0, fill=RED):
    pts = [(22, 0), (5, -4.5), (-1, -15), (-8, -15), (-3.5, -4.5),
           (-15, -4.5), (-17, -7.5), (-19.5, -7.5), (-19.5, 7.5), (-17, 7.5),
           (-15, 4.5), (-3.5, 4.5), (-8, 15), (-1, 15), (5, 4.5)]
    ang = math.radians(-28)
    ca, sa = math.cos(ang), math.sin(ang)
    d = [f"{x + (px * ca - py * sa) * scale:.2f},"
         f"{y + (px * sa + py * ca) * scale:.2f}" for px, py in pts]
    return f'<polygon points="{" ".join(d)}" fill="{fill}"/>'


def missile(x, y, u, scale=1.0, fill=BLUE):
    ang = math.degrees(math.atan2(u[1], u[0]))
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang:.1f}) '
            f'scale({scale})">'
            f'<path d="M16,-4.6 A4.6,4.6 0 0 1 16,4.6 L-18,4.6 L-22,0 L-18,-4.6 Z" '
            f'fill="{fill}"/></g>')


body = []
body.append(line(P_IN[0], P_IN[1], P_OUT[0], P_OUT[1], color=BLUE, w=1.8, dash="9 7"))
body.append(line(A[0], A[1], C[0], C[1], color=GRAY, w=1.3, dash="3 4"))
# 直角标记
e1 = ((C[0] - A[0]) / MISS, (C[1] - A[1]) / MISS)
k = 12
q1 = (C[0] + e1[0] * k, C[1] + e1[1] * k)
q2 = (q1[0] + U[0] * k, q1[1] + U[1] * k)
q3 = (C[0] + U[0] * k, C[1] + U[1] * k)
body.append(f'<polyline points="{q1[0]:.1f},{q1[1]:.1f} {q2[0]:.1f},{q2[1]:.1f} '
            f'{q3[0]:.1f},{q3[1]:.1f}" fill="none" stroke="{GRAY}" stroke-width="1.1"/>')
body.append(line(A[0], A[1], M0[0], M0[1], color=GRAY, w=1.5))
body.append(line(M0[0], M0[1], V_END[0], V_END[1], color=BLUE, w=2.4, marker="ahb"))
body.append(aircraft(*A, scale=1.55))
body.append(missile(M0[0], M0[1], U, scale=1.55))
body.append(f'<circle cx="{C[0]:.1f}" cy="{C[1]:.1f}" r="4.4" fill="{GRAY}"/>')

# ---- 标注 ---------------------------------------------------------------
body.append(text(A[0] - 38, A[1] + 4, "本机", size=FS_B, color=RED,
                 weight="600", anchor="end"))
body.append(text(M0[0] + 16, M0[1] + 34, "来袭弹", size=FS_B, color=BLUE, weight="600"))
body.append(text((A[0] + M0[0]) / 2, (A[1] + M0[1]) / 2 - 12, "r 当前弹目距离",
                 size=FS, color=MID, anchor="middle"))
body.append(text(P_OUT[0] - 4, P_OUT[1] - 10, "相对航迹", size=FS, color=BLUE,
                 anchor="end"))
body.append(text(V_END[0] - 4, V_END[1] + 26, "相对速度", size=FS, color=BLUE,
                 anchor="end"))
body.append(text(C[0] + 16, C[1] + 26, "CPA", size=FS_B, color=GRAY, weight="600"))
body.append(text(C[0] - 20, (A[1] + C[1]) / 2 + 26, "脱靶量", size=FS, color=MID,
                 anchor="end"))

# ---- 画布＝内容外接框（含 12 px 余量），保证插入后居中 ---------------------
X0, Y0, X1, Y1 = 10, 55, 690, 395
W, H = X1 - X0, Y1 - Y0

svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W * K:.0f}" height="{H * K:.0f}"
     viewBox="{X0 * K:.1f} {Y0 * K:.1f} {W * K:.1f} {H * K:.1f}" version="1.1" fill="{GRAY}">
  <defs>
    <marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7"
            markerHeight="7" orient="auto"><path d="M0.5,0.8 L9.6,5 L0.5,9.2 z"
            fill="{BLUE}"/></marker>
  </defs>
  <rect x="{X0 * K:.1f}" y="{Y0 * K:.1f}" width="{W * K:.1f}" height="{H * K:.1f}" fill="#ffffff"/>
  <g transform="scale({K})">
{chr(10).join("    " + b for b in body)}
  </g>
</svg>
'''
path = os.path.join(OUT, "schema-3-cpa.svg")
open(path, "w", encoding="utf-8").write(svg)
print("->", path, f"viewBox {X0} {Y0} {W} {H}")
