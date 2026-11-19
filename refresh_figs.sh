#!/usr/bin/env bash
# 重新生成论文里用到的全部自制插图（两个脚本目录都在用，这里统一跑一遍）。
set -euo pipefail
PY=~/.venvs/ai-dev/bin/python
ROOT="/home/hifive/School/2026latter/兵棋比赛智能体报告"

echo "== A. 兵棋比赛智能体报告/paper/shared/scripts"
cd "$ROOT/paper/shared/scripts"
for s in fig_fire_vs_speed.py fig_gate_hist.py fig_evolve.py fig_fire_dist.py fig_perf_share.py; do
  printf '  %-24s' "$s"; $PY "$s" >/dev/null && echo OK
done

echo "== B. 最新报告/paper/shared/scripts"
cd "$ROOT/最新报告/paper/shared/scripts"
for s in fig_d0.py fig_evade_cdf.py fig_evade_channels.py fig_evade_timeline.py fig_task_alloc.py fig_tasks.py; do
  printf '  %-24s' "$s"; $PY "$s" >/dev/null && echo OK
done

echo "== 完成：$ROOT/最新报告/paper/shared/figures"
