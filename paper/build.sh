#!/usr/bin/env bash
# 构建两篇文稿。用法：./build.sh [all|design|verify|watch]
set -uo pipefail
cd "$(dirname "$0")"

build() {
  local d="$1" name="$2"
  [[ -f "$d/main.typ" ]] || { echo "跳过 $d（无 main.typ）"; return 1; }
  local log
  if log=$(typst compile --root . "$d/main.typ" "$d/main.pdf" 2>&1); then
    echo "built: $(pwd)/$d/main.pdf  ($name)"
  else
    echo "FAILED: $d  ($name)"
    echo "$log" | grep -vE "unknown font family: (simsun|simhei)" | head -25
    return 1
  fi
}

case "${1:-all}" in
  design) build design 智能体设计报告 ;;
  verify) build verify 效果验证文档 ;;
  watch)  exec typst watch --root . design/main.typ design/main.pdf ;;
  all)    rc=0; build design 智能体设计报告 || rc=1; build verify 效果验证文档 || rc=1; exit $rc ;;
  *) echo "用法: ./build.sh [all|design|verify|watch]"; exit 1 ;;
esac
