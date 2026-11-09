#!/usr/bin/env bash
# 构建两篇文稿
# 用法：
#   ./build.sh            两篇都构建
#   ./build.sh design     只构建设计报告
#   ./build.sh verify     只构建效果验证文档
#   ./build.sh watch      监听设计报告
set -euo pipefail
cd "$(dirname "$0")"

build() {
  local d="$1" name="$2"
  [[ -f "$d/main.typ" ]] || { echo "跳过 $d（无 main.typ）"; return; }
  typst compile --root . "$d/main.typ" "$d/main.pdf" 2>&1 \
    | grep -vE "unknown font family: (simsun|simhei)" || true
  echo "built: $(pwd)/$d/main.pdf  ($name)"
}

case "${1:-all}" in
  design) build design 智能体设计报告 ;;
  verify) build verify 效果验证文档 ;;
  watch)  exec typst watch --root . design/main.typ design/main.pdf ;;
  all)    build design 智能体设计报告; build verify 效果验证文档 ;;
  *) echo "用法: ./build.sh [all|design|verify|watch]"; exit 1 ;;
esac
