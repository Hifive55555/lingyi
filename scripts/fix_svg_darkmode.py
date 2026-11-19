#!/usr/bin/env python3
"""把 draw.io 导出的「自适应明暗」SVG 固化为浅色主题。

问题：draw.io 导出的 SVG 带 `color-scheme: light dark` + 大量
`light-dark(<亮色>, <暗色>)` 与 `var(--ge-adaptive-bg/-fg, ...)`。
在深色模式浏览器 / 尊重 color-scheme 的转换器里，背景会取暗色
(#121212) 而变成黑底。

本脚本：
  1. 删除只包含 @supports (color: light-dark(...)) 的 <style> 块；
  2. 递归把 light-dark(A, B) 解析为 A（亮色分支）；
  3. 把 var(--ge-adaptive-bg/-fg, fallback) 解析为 fallback；
  4. 去掉根元素上的 color-scheme 声明。

用法：
  python scripts/fix_svg_darkmode.py <file-or-dir> [...]
  加 --dry-run 只报告不改写。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VAR_FALLBACK = {
    "--ge-adaptive-bg": "#ffffff",
    "--ge-adaptive-fg": "#000000",
    "--ge-dark-color": "#121212",
    "--ge-light-color": "#ffffff",
}

SUPPORTS_STYLE = re.compile(
    r'<style[^>]*>\s*@supports[^{]*light-dark[^{]*\{.*?\}\s*</style>', re.S
)
COLOR_SCHEME = re.compile(r'\s*color-scheme\s*:\s*[^;"\']+;?')


def _find_close(text: str, open_idx: int) -> int:
    """open_idx 指向 '('，返回匹配的 ')' 下标。"""
    depth = 0
    for i in range(open_idx, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced parentheses")


def _split_top_level(inner: str) -> list[str]:
    args, depth, cur = [], 0, []
    for c in inner:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == "," and depth == 0:
            args.append("".join(cur))
            cur = []
        else:
            cur.append(c)
    args.append("".join(cur))
    return args


def _resolve_func(text: str, name: str) -> str:
    """把 name(a, b, ...) 递归替换为 a。"""
    needle = name + "("
    while True:
        idx = text.find(needle)
        if idx < 0:
            return text
        open_idx = idx + len(name)
        close_idx = _find_close(text, open_idx)
        inner = text[open_idx + 1 : close_idx]
        args = _split_top_level(inner)
        repl = args[0].strip()
        text = text[:idx] + repl + text[close_idx + 1 :]


def fix(text: str) -> tuple[str, int]:
    before = text

    # 1. 删掉定义 --ge-adaptive-* 的 @supports 样式块
    text, n_style = SUPPORTS_STYLE.subn("", text)

    # 2. light-dark(a, b) -> a（递归，可能嵌套）
    text = _resolve_func(text, "light-dark")

    # 3. var(--ge-adaptive-bg, #fff) -> #fff
    while True:
        idx = text.find("var(")
        if idx < 0:
            break
        close_idx = _find_close(text, idx + 3)
        inner = text[idx + 4 : close_idx]
        args = _split_top_level(inner)
        var_name = args[0].strip()
        if len(args) > 1:
            repl = args[1].strip()
        else:
            repl = VAR_FALLBACK.get(var_name, "none")
        text = text[:idx] + repl + text[close_idx + 1 :]

    # 4. 根元素不再声明 color-scheme
    text, n_cs = COLOR_SCHEME.subn("", text)

    # 5. 收拾多余空白（仅限我们动过的 style 属性内）
    text = re.sub(r'style="\s+', 'style="', text)
    text = re.sub(r'style="([^"]*?)\s+"', r'style="\1"', text)
    text = re.sub(r'style="\s*"', 'style="background: #ffffff;"', text)

    return text, (len(before) != len(text)) + n_style + n_cs


def iter_svgs(targets: list[str]):
    for t in targets:
        p = Path(t)
        if p.is_dir():
            yield from sorted(p.rglob("*.svg"))
        elif p.suffix.lower() == ".svg":
            yield p


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    targets = [a for a in argv if not a.startswith("--")]
    if not targets:
        print(__doc__)
        return 2

    changed = skipped = 0
    for path in iter_svgs(targets):
        src = path.read_text(encoding="utf-8")
        if "light-dark(" not in src and "color-scheme" not in src:
            skipped += 1
            continue
        out, _ = fix(src)
        if out == src:
            skipped += 1
            continue
        if dry:
            print(f"[dry-run] 需要修复: {path}")
        else:
            path.write_text(out, encoding="utf-8")
            print(f"已修复: {path}")
        changed += 1

    print(f"\n共修复 {changed} 个，跳过 {skipped} 个（无自适应配色）。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
