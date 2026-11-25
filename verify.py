# -*- coding: utf-8 -*-
"""verify.sh 的 Windows 等价物：同一套检查，逐项 PASS/FAIL。

用法：python verify.py            全跑
      python verify.py --quick    跳过离线自测
"""
import os
import subprocess
import sys

# Windows 控制台/CI 默认 cp1252，print 中文会 UnicodeEncodeError；强制 UTF-8
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception:                                     # noqa: BLE001
        pass
os.environ.setdefault('PYTHONUTF8', '1')                  # 子进程也按 UTF-8 跑

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
QUICK = '--quick' in sys.argv

PY_FILES = [
    '智能体代码/Mission_all_red.py', '智能体代码/Mission_all_blue_hh.py',
    '智能体代码/BattlefieldMonitor.py', '智能体代码/SamBattalionDefense.py',
    '智能体代码/ShipClusterDefense.py',
    '小窗/overlay/agent.py', '小窗/overlay/launcher.py', '小窗/overlay_ai.py',
    '小窗/overlay/monitor.py', '小窗/overlay/monitor_core.py', 'pack.py',
]


def run(label, args):
    print('%-46s' % label, end='', flush=True)
    try:
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=300)
    except Exception as e:                       # noqa: BLE001
        print('FAIL'); print('    ' + repr(e)); return False
    if p.returncode == 0:
        print('PASS'); return True
    print('FAIL')
    for line in (p.stdout + p.stderr).strip().splitlines()[-15:]:
        print('    ' + line)
    return False


def main():
    passed = failed = 0

    def check(label, args):
        nonlocal passed, failed
        if run(label, args):
            passed += 1
        else:
            failed += 1

    print('== 1) 语法编译 ==')
    for f in PY_FILES:
        check('py_compile ' + f, [PY, '-m', 'py_compile', f])

    print('== 2) 任务表 vs xlsx ==')
    check('check_table.py (红方)', [PY, os.path.join('智能体代码', 'tools', 'check_table.py')])
    check('check_table_blue.py (蓝方)', [PY, os.path.join('智能体代码', 'tools', 'check_table_blue.py')])
    check('check_111.py (红方原文坐标)', [PY, os.path.join('智能体代码', 'tools', 'check_111.py')])

    if not QUICK:
        print('== 3) 离线自测 ==')
        check('selftest_offline.py (红方)', [PY, os.path.join('智能体代码', 'tools', 'selftest_offline.py')])
        check('selftest_blue_hh.py (蓝方)', [PY, os.path.join('智能体代码', 'tools', 'selftest_blue_hh.py')])

    print('== 4) 打包清单 ==')
    out = os.path.join(os.environ.get('TEMP') or '/tmp', 'ly-verify-out')
    check('pack.py --no-zip (清单/文件校验)', [PY, 'pack.py', '--no-zip', '--name', '_verify', '--out', out])

    print()
    print('结果：通过 %d 项，失败 %d 项' % (passed, failed))
    if failed:
        print('→ 有失败项，别提交。逐条看上面的 FAIL 输出。')
        return 1
    print('→ 全绿。目标机上再跑一次 check_env.py（见 AGENTS.md §5）就可以部署了。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
