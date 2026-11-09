#!/usr/bin/env bash
# 构建文稿 PDF
# 用法: ./build.sh          生成 main.pdf
#       ./build.sh watch    监听改动自动重建
set -euo pipefail
cd "$(dirname "$0")"
if [[ "${1:-}" == "watch" ]]; then
  exec typst watch main.typ main.pdf
fi
typst compile main.typ main.pdf
echo "built: $(pwd)/main.pdf"
