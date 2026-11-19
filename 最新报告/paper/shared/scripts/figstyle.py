#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全文档统一配色 v2 —— 「一组主体色」方案。

主体色（占画面 80%）
    INDIGO 靛蓝   #1f3b5c   结构、平台、流程、坐标系、默认系列
    INDIGO 的浅底 #e6edf4 / #f2f6fa

强调色（只给"论点"用，占 5–10%）
    BRICK  朱砂   #b23a2b   我方规则 / 核心判据 / 阈值线
    浅底          #f8e9e5

辅助色（第三、第四类对象，少量）
    TEAL   青     #2e7d74
    SAND   砂金   #b0883a

中性
    INK    #171b20（文字/轴线）  MID #6b737d  SOFT #a4acb5
    LIGHT  #d8dde3（分隔/网格较深一档）  GRID #e9edf1  PANEL #f3f5f7

用法
    import figstyle
    figstyle.apply()
    figstyle.INDIGO / BRICK / TEAL / SAND
    figstyle.CATEGORICAL              # 并列类别
    figstyle.SEQ                      # 顺序变量（单色梯度）
    figstyle.map_color(h, kind="svg") # 旧色 → 新色
    python figstyle.py --svg  a.svg b.svg     # 示意图重上色（结构不动）
    python figstyle.py --plot x.py            # 脚本内 hex 重映射
"""
from __future__ import annotations

import colorsys
import re
import sys

# ---------------------------------------------------------------- 主体色
INDIGO = "#2b5d8f"
INDIGO_TINT = "#e7eef7"
INDIGO_PALE = "#f3f7fc"
INDIGO_DEEP = "#1b3f63"

# ---------------------------------------------------------------- 强调 / 辅助
BRICK = "#b23a2b"
BRICK_TINT = "#f8e9e5"
BRICK_DEEP = "#7d2419"

TEAL = "#33907f"
TEAL_TINT = "#e4f0ed"
TEAL_DEEP = "#226b5f"

SAND = "#b0883a"
SAND_TINT = "#f7efde"
SAND_DEEP = "#7a5c22"

STEEL = "#6c8fb8"
MAUVE = "#6f4a6b"

# ---------------------------------------------------------------- 中性
INK = "#171b20"
MID = "#6b737d"
SOFT = "#a4acb5"
LIGHT = "#d8dde3"
GRID = "#e9edf1"
PANEL = "#f3f5f7"
WHITE = "#ffffff"

FAMILY = {
    "indigo": {"fill": INDIGO_TINT, "line": INDIGO, "deep": INDIGO_DEEP},
    "brick": {"fill": BRICK_TINT, "line": BRICK, "deep": BRICK_DEEP},
    "teal": {"fill": TEAL_TINT, "line": TEAL, "deep": TEAL_DEEP},
    "sand": {"fill": SAND_TINT, "line": SAND, "deep": SAND_DEEP},
    "gray": {"fill": PANEL, "line": MID, "deep": "#3d444b"},
}

CATEGORICAL = [INDIGO, BRICK, TEAL, SAND, STEEL, MAUVE]
SEQ = ["#d3dfee", "#a4bcd9", "#6d92be", INDIGO, INDIGO_DEEP]
SEQ2 = [BRICK_TINT, "#e2b3aa", BRICK, BRICK_DEEP]

RAMP = {
    "indigo": ["#f7fafd", INDIGO_TINT, "#b9cde3", "#6d92be", INDIGO, INDIGO_DEEP, "#122c47"],
    "brick": ["#fdf4f2", BRICK_TINT, "#dfa79d", BRICK, BRICK_DEEP, "#571811"],
    "teal": ["#f3faf8", TEAL_TINT, "#a7ccc5", "#4f9d8f", TEAL, TEAL_DEEP, "#0f312d"],
    "sand": ["#fdf9f1", SAND_TINT, "#e0c894", SAND, SAND_DEEP, "#4f3c15"],
    "gray": ["#f8f9fa", PANEL, "#c8d0d8", MID, "#3d444b", "#22262a"],
}

# ================================================================
# 旧色 → 新色（两层：drawio/历史脚本 → v1 → v2）
# ================================================================
# 第一层：v1 时期的颜色（上一版铺过的色）
V1_TO_V2_SVG = {
    "#e4ebf4": INDIGO_TINT,     # 蓝底 → 靛蓝浅底
    "#2f5b9a": INDIGO,          # 蓝主 → 靛蓝
    "#f7e4e1": BRICK_TINT,      # 红底 → 朱砂浅底
    "#b3261e": BRICK,           # 红主 → 朱砂
    "#e6f0e8": PANEL,           # 绿底 → 中性（示意图里"支撑/采集"类）
    "#3c8c5a": MID,
    "#ece8f4": TEAL_TINT,       # 紫底 → 青（平台内核一类）
    "#6b5ca5": TEAL,
    "#faf1de": SAND_TINT,       # 橙底 → 砂金
    "#c08a2e": SAND,
    "#faf3dc": PANEL,           # 黄底 → 中性（输入/工具框）
    "#b8901f": MID,
    "#f2f4f6": PANEL,
    "#1f2328": INK,
    "#8a611c": SAND_DEEP,
    # v1 中性阶
    "#6a737d": MID, "#a8b0b9": SOFT, "#d7dbe0": LIGHT, "#e8ebee": GRID,
    "#f2f4f6": PANEL, "#939da8": SOFT, "#c2c7cd": LIGHT, "#c9ced4": LIGHT,
    "#f7f8f9": "#f8f9fa", "#fafbfc": "#fbfcfd", "#f6faf7": "#f6faf8",
    "#fdf7ea": "#fdf8ee", "#fdf7e6": "#fdf8ea", "#efeee9": "#f0f0ec",
    "#f9edd8": "#f9f0e0", "#f5f9fc": "#f6fafd",
}
V1_TO_V2_PLOT = dict(V1_TO_V2_SVG)
V1_TO_V2_PLOT.update({"#e6f0e8": TEAL_TINT, "#3c8c5a": TEAL})   # 图里绿保留为第三色

# 第二层：drawio 默认色板 / 早期脚本调色板 → v1
_ORIG_TO_V1 = {
    # drawio 默认
    "#dae8fc": "#e4ebf4", "#6c8ebf": "#2f5b9a",
    "#d5e8d4": "#e6f0e8", "#82b366": "#3c8c5a",
    "#f8cecc": "#f7e4e1", "#b85450": "#b3261e",
    "#e1d5e7": "#ece8f4", "#9673a6": "#6b5ca5",
    "#ffe6cc": "#faf1de", "#d79b00": "#c08a2e",
    "#fff2cc": "#faf3dc", "#d6b656": "#b8901f",
    "#f5f5f5": "#f2f4f6", "#666666": "#6a737d",
    # 早期脚本
    "#b03a2e": "#b3261e", "#a33c3c": "#b3261e", "#a0433a": "#b3261e",
    "#c62f2f": "#b3261e", "#cc0000": "#b3261e", "#990000": "#b3261e",
    "#d81e06": "#b3261e", "#e51400": "#b3261e", "#b20000": "#b3261e",
    "#ff2d2d": "#c9463d", "#ff9999": "#f0c4be", "#ff0000": "#b3261e",
    "#d62728": "#b3261e", "#d64545": "#b3261e", "#e01b24": "#b3261e",
    "#1f4e79": "#2f5b9a", "#1a5fb4": "#2f5b9a", "#3d6fb0": "#2f5b9a",
    "#2f6db3": "#2f5b9a", "#2f6f9f": "#2f5b9a", "#3370ff": "#2f5b9a",
    "#1f77b4": "#2f5b9a", "#4c78a8": "#2f5b9a", "#4a90d9": "#4079c4",
    "#035df7": "#2f5b9a", "#0000ff": "#2f5b9a", "#0000cc": "#2f5b9a",
    "#1b3f8f": "#2f5b9a", "#3f8a5f": "#3c8c5a", "#26a269": "#3c8c5a",
    "#2ca02c": "#3c8c5a", "#8c564b": "#2b8a8a", "#c98a2b": "#c08a2e",
    "#d8c400": "#c08a2e", "#e08a1e": "#c08a2e", "#ff7f0e": "#c08a2e",
    "#b0720a": "#c08a2e", "#8a5a00": "#8a611c", "#7a6b00": "#8a611c",
    "#5d5200": "#8a611c", "#9467bd": "#6b5ca5", "#7a5cd6": "#6b5ca5",
    "#7b3fa0": "#6b5ca5", "#7a4f9c": "#6b5ca5", "#c64600": "#8a611c",
    "#000000": "#1f2328", "#1a1a1a": "#1f2328", "#222222": "#1f2328",
    "#22252b": "#1f2328", "#333333": "#1f2328", "#3d4248": "#1f2328",
    "#1f2937": "#1f2328", "#4a4a4a": "#3f464c", "#4d4d4d": "#474e55",
    "#5f676d": "#6a737d", "#5b6472": "#6a737d", "#6b6b6b": "#6a737d",
    "#6b7378": "#6a737d", "#6b7280": "#6a737d", "#4b5563": "#6a737d",
    "#8a8a8a": "#a8b0b9", "#8a93a0": "#a8b0b9", "#9a9a9a": "#a8b0b9",
    "#9aa0a8": "#a8b0b9", "#9c9c9c": "#939da8", "#c9c9c9": "#d7dbe0",
    "#cccccc": "#d7dbe0", "#d5d5d5": "#d7dbe0", "#dcdcdc": "#d7dbe0",
    "#dddddd": "#d7dbe0", "#e4e7ea": "#e8ebee", "#e2e5e9": "#e8ebee",
    "#d9dce1": "#d7dbe0", "#cfd4da": "#d7dbe0", "#d5d9de": "#d7dbe0",
    "#d8dde6": "#d7dbe0", "#c9d2e3": "#c9d4e4", "#f7f7f7": "#f7f8f9",
    "#f7f8fa": "#f7f8f9", "#fbfbfb": "#fafbfc", "#f0f0f0": "#f4f6f8",
    "#f4f4f4": "#f4f6f8", "#f7fdf6": "#f6faf7", "#fdf6e3": "#fdf7ea",
    "#fffbe6": "#fdf7e6", "#ece9df": "#efeee9", "#fbe3bf": "#f9edd8",
    "#f6d5d2": "#f7e4e1", "#d9e6f5": "#e4ebf4", "#f4f8fb": "#f5f9fc",
    "#b3b3b3": "#c2c7cd", "#bbbbbb": "#c9ced4", "#33556e": "#33556e",
}

# 新色自身恒等（保证可重复执行）
_IDENT = set(FAMILY[k][p].lower() for k in FAMILY for p in FAMILY[k])
_IDENT |= set(c.lower() for c in CATEGORICAL + SEQ + SEQ2)
_IDENT |= set(c.lower() for c in RAMP for _ in [0])
_IDENT |= {c.lower() for r in RAMP.values() for c in r}
_IDENT |= {c.lower() for c in (INK, MID, SOFT, LIGHT, GRID, PANEL, WHITE,
                               INDIGO_PALE, STEEL, MAUVE, "#c9463d", "#f0c4be",
                               "#4079c4", "#3f464c", "#474e55", "#c9d4e4",
                               "#f4f6f8", "#f7f8f9", "#fafbfc", "#f6faf7",
                               "#fdf7ea", "#fdf7e6", "#efeee9", "#f9edd8",
                               "#f5f9fc", "#c2c7cd", "#c9ced4", "#939da8",
                               "#33556e", "#a8b0b9")}

def _build(mapping):
    tab = {}
    for _k, _v1 in _ORIG_TO_V1.items():
        tab[_k] = mapping.get(_v1, _v1)
    for _k, _v in mapping.items():
        tab.setdefault(_k, _v)
    for _c in _IDENT:
        tab[_c] = _c
    return tab


LEGACY = _build(V1_TO_V2_SVG)        # 示意图：绿 → 灰
LEGACY_PLOT = _build(V1_TO_V2_PLOT)  # 数据图：绿 → 青

# v2 收尾：示意图里剩下的零散色（分组虚线、深色描边、淡粉圈等）
RESIDUAL = {
    "#7e8690": MID,          # drawio 分组虚线框
    "#7a2318": BRICK_DEEP,   # 深朱砂描边
    "#162d46": INDIGO_DEEP,
    "#233f60": INDIGO,
    "#474e55": "#3d444b",    # 深灰文字
    "#6f8eb1": STEEL,
    "#6183a9": STEEL,
    "#c2c7cd": LIGHT,
    "#f0c4be": "#e2b3aa",    # 淡粉虚线圈 → SEQ2 中间档
    "#c9d4e4": "#dbe6f1",
    "#f7f8f9": "#f7fafd",
    "#f4f6f8": PANEL,
}

# 靛蓝提亮：#1f3b5c → #2b5d8f（用户反馈"蓝偏暗沉"）
_OLD_INDIGO = {"#1f3b5c": INDIGO, "#12263c": INDIGO_DEEP,
               "#e6edf4": INDIGO_TINT, "#f2f6fa": INDIGO_PALE,
               "#adc1d8": "#b9cde3", "#a9c0d8": "#a4bcd9",
               "#7f5580": MAUVE}

# 上一轮定过的 teal / mauve 微调（青提亮、藕偏红），保留前向映射便于重刷
_OLD_TEAL, _OLD_MAUVE = "#2e7d74", "#7c5c7c"
for _tab in (LEGACY, LEGACY_PLOT):
    _tab.update({"(old)": None})
    _tab.pop("(old)", None)
    _tab[_OLD_TEAL] = TEAL
    _tab[_OLD_MAUVE] = MAUVE
    _tab.update(_OLD_INDIGO)
    _tab.update(RESIDUAL)


# ---------------------------------------------------------------- 工具
def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _rgb2hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb)


def lum(h):
    r, g, b = _hex2rgb(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mix(a, b, t):
    ra, rb = _hex2rgb(a), _hex2rgb(b)
    return _rgb2hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def _family_of(h):
    r, g, b = _hex2rgb(h)
    hh, s_, v = colorsys.rgb_to_hsv(r, g, b)
    if s_ < 0.18:                     # 近中性：一律走灰阶
        return "gray"
    deg = hh * 360
    if deg < 12 or deg >= 330:
        return "brick"
    if deg < 110:                     # 橙 / 黄 / 橄榄
        return "sand"
    if deg < 190:                     # 青绿
        return "teal"
    if deg < 300:                     # 蓝 / 靛
        return "indigo"
    return "brick"


def map_color(h, kind="svg"):
    """旧色 → v2 色。查不到就按"同色相 + 同明度"落到 v2 梯度上。"""
    key = h.lower()
    tab = LEGACY_PLOT if kind == "plot" else LEGACY
    if key in tab:
        return tab[key]
    if not re.fullmatch(r"#[0-9a-f]{6}", key):
        return h
    ramp = RAMP[_family_of(key)]
    lums = [lum(c) for c in ramp]
    L = lum(key)
    if L >= lums[0]:
        return ramp[0]
    if L <= lums[-1]:
        return ramp[-1]
    for i in range(len(ramp) - 1):
        if lums[i + 1] <= L <= lums[i]:
            t = (lums[i] - L) / max(lums[i] - lums[i + 1], 1e-6)
            return mix(ramp[i], ramp[i + 1], t)
    return ramp[2]


# ---------------------------------------------------------------- matplotlib
def apply(mpl=None, base_size: float = 7.0):
    import matplotlib as _mpl
    mpl = mpl or _mpl
    rc = mpl.rcParams
    rc.update({
        "figure.facecolor": WHITE, "axes.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "font.size": base_size, "axes.titlesize": base_size + 1,
        "axes.labelsize": base_size,
        "xtick.labelsize": base_size - 0.6, "ytick.labelsize": base_size - 0.6,
        "legend.fontsize": base_size - 0.6,
        "axes.linewidth": 0.6, "axes.edgecolor": INK,
        "axes.labelcolor": INK, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": INK, "ytick.color": INK,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.2, "ytick.major.size": 2.2,
        "xtick.direction": "out", "ytick.direction": "out",
        "lines.linewidth": 1.0, "lines.markersize": 3.0,
        "patch.linewidth": 0.6,
        "grid.color": GRID, "grid.linewidth": 0.5,
        "legend.frameon": False, "legend.handlelength": 1.6,
        "legend.borderaxespad": 0.2, "legend.labelspacing": 0.3,
        "axes.axisbelow": True, "axes.grid": True,
        "axes.prop_cycle": mpl.cycler(color=CATEGORICAL),
        "svg.fonttype": "path", "pdf.fonttype": 42,
        "savefig.dpi": 600, "figure.dpi": 120,
    })
    return mpl


def apply_axes(ax, grid_axis="y"):
    ax.grid(True, axis=grid_axis, color=GRID, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK)
        ax.spines[s].set_linewidth(0.6)
    return ax


# ---------------------------------------------------------------- SVG 重上色
COLOR_TOKEN = (r"(?:#[0-9a-fA-F]{6}\b"
               r"|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(?:,\s*[\d.]+\s*)?\))")

SVG_ATTR = re.compile(
    r'(?P<attr>\b(?:fill|stroke|stop-color|flood-color|color|background-color)'
    r'\s*[:=]\s*["\']?)'
    r'(?P<val>' + COLOR_TOKEN + r')'
)


def to_hex(tok):
    """#rrggbb 或 rgb(a)(r, g, b, [a]) → #rrggbb（alpha 丢弃，图里不用半透明色块）。"""
    if tok.startswith("#"):
        return tok.lower()
    nums = re.findall(r"[\d.]+", tok)
    r, g, b = (int(float(x)) for x in nums[:3])
    return f"#{r:02x}{g:02x}{b:02x}"


def recolor_svg_text(text, kind="svg"):
    n = 0

    def sub(m):
        nonlocal n
        old = m.group("val")
        new = map_color(to_hex(old), kind)
        if new.lower() != to_hex(old):
            n += 1
        return m.group("attr") + new

    out = SVG_ATTR.sub(sub, text)

    # 剩下裸色值（如 mxfile 里的 style 字符串、CSS 块）
    def sub_any(m):
        nonlocal n
        tok = m.group(0)
        new = map_color(to_hex(tok), kind)
        if new.lower() != to_hex(tok):
            n += 1
        return new

    out = re.sub(COLOR_TOKEN, sub_any, out)
    return out, n


def recolor_svg_file(path, kind="svg"):
    src = open(path, encoding="utf-8").read()
    out, n = recolor_svg_text(src, kind)
    if n:
        open(path, "w", encoding="utf-8").write(out)
    return n


if __name__ == "__main__":
    import glob
    import os

    kind = "svg"
    files = []
    for a in sys.argv[1:]:
        if a == "--plot":
            kind = "plot"
        elif a == "--svg":
            kind = "svg"
        else:
            files.append(a)
    if not files:
        print(__doc__)
        sys.exit(2)
    for pat in files:
        for p in sorted(glob.glob(pat)):
            if p.endswith(".py"):
                src = open(p, encoding="utf-8").read()
                hits = {}

                def sub(m):
                    new = map_color(m.group(0), kind)
                    hits[m.group(0).lower()] = new
                    return new

                out = re.sub(r"#[0-9a-fA-F]{6}\b", sub, src)
                if out != src:
                    open(p, "w", encoding="utf-8").write(out)
                print(f"{p}: {len(hits)} 种颜色 → " +
                      ", ".join(f"{k}→{v}" for k, v in sorted(hits.items())))
            elif p.endswith(".svg"):
                print(f"{p}: {recolor_svg_file(p, kind)} 处颜色替换")
