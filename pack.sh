#!/usr/bin/env bash
# 打包最新智能体 + 小窗（Linux/macOS 用；Windows 用 pack.bat）
#   ./pack.sh                 生成 dist/灵弈小窗+红方智能体_<时间戳>.zip
#   ./pack.sh --with-entitys  连平台库一起打
#   ./pack.sh --no-zip        只生成目录（用 robocopy 拷更省事）
set -euo pipefail
cd "$(dirname "$0")"
for py in python3 python ~/.venvs/ai-dev/bin/python; do
  if command -v "$py" >/dev/null 2>&1; then exec "$py" pack.py "$@"; fi
done
echo "[STOP] 找不到 python3，先 activate 一个环境再跑" >&2
exit 1
