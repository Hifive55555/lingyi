#!/usr/bin/env bash
# 一键回归：本机（任意 Python 3 + openpyxl）就能跑，不需要灵弈、不需要 Windows。
# 用法：./verify.sh            全跑
#       ./verify.sh --quick    跳过 selftest（几十秒变几秒）
set -u
cd "$(dirname "$0")"
# 找 python：PYTHON 环境变量 > python3 > python
if [ -n "${PYTHON:-}" ]; then
  PY=$PYTHON
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "找不到 python（可用 PYTHON=/path/to/python ./verify.sh 指定）" >&2
  exit 2
fi
QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

pass=0; fail=0
run() {          # run "标签" 命令...
  local label="$1"; shift
  printf '%-46s' "$label"
  if out=$("$@" 2>&1); then
    echo "PASS"; pass=$((pass+1))
  else
    echo "FAIL"; fail=$((fail+1))
    echo "$out" | sed 's/^/    /' | tail -15
  fi
}

echo "== 1) 语法编译 =="
for f in 智能体代码/Mission_all_red.py 智能体代码/Mission_all_blue_hh.py \
         智能体代码/BattlefieldMonitor.py 智能体代码/SamBattalionDefense.py \
         智能体代码/ShipClusterDefense.py \
         小窗/overlay/agent.py 小窗/overlay/launcher.py 小窗/overlay_ai.py \
         小窗/overlay/monitor.py 小窗/overlay/monitor_core.py pack.py; do
  run "py_compile $f" "$PY" -m py_compile "$f"
done

echo "== 2) 引用体检（比赛机只能 ray210）=="
run "check_imports.py (依赖/外部环境)" "$PY" 智能体代码/tools/check_imports.py

echo "== 3) 任务表 vs xlsx =="
run "check_table.py (红方)"       "$PY" 智能体代码/tools/check_table.py
run "check_table_blue.py (蓝方)"  "$PY" 智能体代码/tools/check_table_blue.py
run "check_111.py (红方原文坐标)" "$PY" 智能体代码/tools/check_111.py

if [ "$QUICK" = "0" ]; then
  echo "== 4) 离线自测 =="
  run "selftest_offline.py (红方)"   "$PY" 智能体代码/tools/selftest_offline.py
  run "selftest_blue_hh.py (蓝方)"   "$PY" 智能体代码/tools/selftest_blue_hh.py
fi

echo "== 5) 打包清单 =="
run "pack.py --no-zip (清单/文件校验)" "$PY" pack.py --no-zip --name _verify --out /tmp/ly-verify-out

echo
echo "结果：通过 $pass 项，失败 $fail 项"
[ "$fail" = "0" ] || { echo "→ 有失败项，别提交。逐条看上面的 [FAIL] 输出。"; exit 1; }
echo "→ 全绿。目标机上再跑一次 check_env.py（见 AGENTS.md §5）就可以部署了。"
