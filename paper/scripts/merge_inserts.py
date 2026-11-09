#!/usr/bin/env python
"""
把 insert/ 下的片段合入 main.typ
==============================
- 只做「插入」与「整节替换」，不删除、不改写你已经写过的句子
- 以**小节标题**为锚点，不依赖行号，因此你改了正文语言也不影响
- 写入前自动备份 main.typ → main.typ.bak，并打印 diff 摘要

用法：
  python paper/scripts/merge_inserts.py --dry-run    # 只看会改什么
  python paper/scripts/merge_inserts.py              # 实际写入
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
MAIN = os.path.join(PAPER, "main.typ")
INS = os.path.join(PAPER, "insert")

# (片段文件里的标签, 插入位置锚点标题, 模式)
# mode=before: 插在该标题之前；mode=after_block: 插在该标题所辖小节末尾
PLAN = [
    ("fig:schema1", "== 决策周期、可观测性与动作约束", "before"),
    ("fig:schema2", "= 敏感性分析", "before"),
    ("fig:schema3", "== 受控对比", "before"),
    ("fig:schema4", "== 与固定开火距离的对比", "before"),
    ("fig:schema5", "== 分层补射：收益不在效率，在距离", "before"),
]


def blocks(path):
    """把片段文件按 `#figure(` 起头切成独立块，返回 {label: text}"""
    src = open(path, encoding="utf-8").read()
    out, cur, label = {}, [], None
    for line in src.split("\n"):
        if line.startswith("#figure("):
            if label and cur:
                out[label] = "\n".join(cur).strip()
            cur, label = [line], None
        elif cur is not None:
            cur.append(line)
            m = re.search(r"<([\w:.-]+)>\s*$", line.strip())
            if m:
                label = m.group(1)
    if label and cur:
        out[label] = "\n".join(cur).strip()
    return out


def replace_section(lines, heading_prefix, new_text):
    """把以 heading_prefix 开头的小节整体替换为 new_text（保留标题行）"""
    for i, ln in enumerate(lines):
        if ln.startswith(heading_prefix):
            j = i + 1
            while j < len(lines) and not re.match(r"^(== |=== |= )", lines[j]):
                j += 1
            keep = lines[i]
            return lines[:i] + [keep, ""] + new_text.split("\n") + [""] + lines[j:]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = open(MAIN, encoding="utf-8").read()
    lines = src.split("\n")
    sch = blocks(os.path.join(INS, "SCHEMATICS.typ"))

    added = 0
    for label, anchor, mode in PLAN:
        if label not in sch:
            print(f"  ! 片段里找不到 {label}，跳过")
            continue
        if f"<{label}>" in src:
            print(f"  = {label} 已在 main.typ 中，跳过")
            continue
        idx = next((i for i, ln in enumerate(lines) if ln.startswith(anchor)), None)
        if idx is None:
            print(f"  ! 找不到锚点「{anchor}」，跳过 {label}")
            continue
        lines = lines[:idx] + sch[label].split("\n") + [""] + lines[idx:]
        added += 1
        print(f"  + {label} → 插在「{anchor}」之前")

    # 实战章节整节替换
    ev = open(os.path.join(INS, "EVIDENCE-SECTION.typ"), encoding="utf-8").read()
    body = "\n".join(l for l in ev.split("\n") if not l.startswith("//"))
    body = re.sub(r"^== .*\n", "", body, count=1).strip()
    new = replace_section(lines, "== 录屏的可核对边界", body)
    if new is None:
        print("  ! 找不到「== 录屏的可核对边界」，实战章节跳过")
    else:
        lines = new
        print("  ~ 实战章节已整节替换")

    out = "\n".join(lines)
    if out == src:
        print("\n没有需要合入的内容。")
        return
    print(f"\n新增片段 {added} 处；文件 {len(src)} → {len(out)} 字符")
    if args.dry_run:
        print("（dry-run，未写入）")
        return
    open(MAIN + ".bak", "w", encoding="utf-8").write(src)
    open(MAIN, "w", encoding="utf-8").write(out)
    print(f"已写入 {MAIN}（备份 main.typ.bak）")


if __name__ == "__main__":
    main()
