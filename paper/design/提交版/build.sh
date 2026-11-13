#!/usr/bin/env bash
# 构建"模板对齐版"报告。图片与 bib 在 ../../shared，需以 paper 目录为 root。
set -euo pipefail
cd "$(dirname "$0")"
uv run python extract.py          # 从 ../润色后/main.typ 抽取既有章节
uv run python fix_refs.py         # 章节重编号后的交叉引用修正
uv run python codewrap.py         # 代码块 → 代码 图（kind = 代码）
typst compile --root ../.. main.typ "联合作战人机协同智能体说明文档（模板对齐版）.pdf"
echo "done → 联合作战人机协同智能体说明文档（模板对齐版）.pdf"
