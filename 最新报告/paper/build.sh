#!/usr/bin/env bash
# 构建"模板对齐版"报告。本目录自包含：插图在 shared/figures、shared/schematics，参考文献在 shared/ref.bib。
set -euo pipefail
cd "$(dirname "$0")"
typst compile main.typ "联合作战人机协同智能体说明文档（模板对齐版）.pdf"
echo "done → 联合作战人机协同智能体说明文档（模板对齐版）.pdf"
