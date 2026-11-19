# -*- coding: utf-8 -*-
"""
环境自检：确认「灵弈自带的 Python」能直接跑智能体与小窗（不再建 .venv）。

背景：小窗原本配了一个 `.venv`，但它建的时候就是
`python -m venv --system-site-packages`，aiohttp 全部继承自灵弈自带的 ray210
（pyvenv.cfg 里 home 指向 ray210）—— 等于只是一个启动壳，还额外带来
「换机器必须重建 + pyvenv.cfg 写死旧路径 + 占 20 MB」三个麻烦。
故改为直接使用 ray210：本脚本只做检查，**不建虚拟环境、不装任何东西**。
比赛机没有外网，装不了包也补不了依赖 —— 检查不过就终止并上报，别在现场折腾。

检查项：
  ① ray210 存在，且是 Python 3.9（entitys 下的 .pyd 是 cp39 扩展，别无选择）
  ② aiohttp 可导入（小窗 agent.py / launcher.py 的唯一第三方依赖）
  ③ psutil 可导入（可选，只影响 launcher 关旧窗口）
  ④ `from engine.LingYi.entitys.player import Player` 能过（等价于智能体开局导入）
  ⑤ 打印「灵弈小窗.bat 该填的 call :try 那一行」

用法（任意 Python 3.6+ 都能跑本脚本，它自己只调 subprocess）：
    python tools/check_env.py
    python tools/check_env.py --lingyi "E:\\LingYi"      # 灵弈装在别处
    python tools/check_env.py --bat                       # 只输出 bat 该加的那行

退出码：0 = 全过；1 = 有硬性项没过（终止，现场不修）。
"""
from __future__ import print_function

import argparse
import os
import subprocess
import sys

# 灵弈的常见安装位置（和 灵弈小窗.bat 里的探测顺序保持一致）
COMMON_ROOTS = (r'D:\LingYi', r'C:\LingYi', r'E:\LingYi', r'F:\LingYi')

REL_PY = os.path.join('intelligent', 'new_env', 'ray210', 'python.exe')
REL_AI = os.path.join('intelligent', 'ai')

OK, BAD, WARN = '[OK]  ', '[FAIL]', '[WARN]'


def say(tag, text):
    print('%s %s' % (tag, text))


def find_lingyi(explicit=None):
    """返回灵弈安装根目录（含 intelligent\\new_env\\ray210\\python.exe 的那层）。"""
    cands = []
    if explicit:
        cands.append(explicit)
    env = os.environ.get('LINGYI_HOME') or os.environ.get('LY_HOME')
    if env:
        cands.append(env)
    # 从本脚本位置反推：逐级上溯，哪级下面有 intelligent\new_env\ray210\python.exe
    # 就算灵弈根（脚本放在 engine\LingYi\tools、ai\tools、intelligent\tools 都能对上）
    up = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        up = os.path.dirname(up)
        if not up or up == os.path.dirname(up):
            break
        cands.append(up)
    cands.extend(COMMON_ROOTS)
    for c in cands:
        if not c:
            continue
        if os.path.isfile(os.path.join(c, REL_PY)):
            return os.path.abspath(c)
    return None


def run(py, code, timeout=60, env_extra=None):
    """用目标 python 跑一段代码，返回 (rc, stdout+stderr)。"""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        p = subprocess.Popen([py, '-X', 'utf8', '-c', code], env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:                                   # noqa: BLE001
        return -1, 'spawn failed: %s' % e
    try:
        out, _ = p.communicate(timeout=timeout)
    except Exception:                                        # noqa: BLE001
        p.kill()
        return -2, 'timeout after %ds' % timeout
    if isinstance(out, bytes):
        out = out.decode('utf-8', 'replace')
    return p.returncode, (out or '').strip()


def writable_tmp(cands):
    """找一个真能写的临时目录。

    不用 tempfile：在“账户改过名/没有可写 TEMP”的会话里，tempfile.gettempdir()
    会直接抛 FileNotFoundError，连 mkdtemp 都做不了。
    """
    for d in cands:
        if not d:
            continue
        try:
            if not os.path.isdir(d):
                os.makedirs(d)
            probe = os.path.join(d, '_ly_probe.tmp')
            with open(probe, 'w') as f:
                f.write('x')
            os.remove(probe)
            return d
        except Exception:                                    # noqa: BLE001
            continue
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description='灵弈自带 Python 环境自检（不建 venv）')
    ap.add_argument('--lingyi', help='灵弈安装根目录，如 D:\\LingYi')
    ap.add_argument('--bat', action='store_true', help='只打印 bat 该加的那一行')
    args = ap.parse_args(argv)

    root = find_lingyi(args.lingyi)
    if root is None:
        say(BAD, '没找到灵弈安装目录（找 %s 都失败）' % REL_PY)
        say(WARN, '用 --lingyi "X:\\你的灵弈目录" 指定，或 set LINGYI_HOME=...')
        return 1

    py = os.path.join(root, REL_PY)
    ai = os.path.join(root, REL_AI)
    bat_line = 'call :try "%~dp0..\\..\\..\\new_env\\ray210\\python.exe"'

    if args.bat:
        print(bat_line)
        return 0

    say(OK, '灵弈目录 : %s' % root)
    say(OK, '自带 Python: %s' % py)
    print('')

    bad = 0

    # ① 版本
    rc, out = run(py, 'import sys;print(sys.version.split()[0])')
    if rc == 0:
        ver = out.splitlines()[-1] if out else '?'
        if ver.startswith('3.9.'):
            say(OK, '① Python 版本 %s（cp39 扩展要求，正确）' % ver)
        else:
            say(BAD, '① Python 版本 %s —— 不是 3.9，entitys 的 .pyd 会 DLL load failed' % ver)
            bad += 1
    else:
        say(BAD, '① 跑不起来：%s' % out)
        bad += 1

    # ② aiohttp
    rc, out = run(py, 'import aiohttp;print(aiohttp.__version__)')
    if rc == 0:
        say(OK, '② aiohttp %s（小窗的唯一第三方依赖）' % out.splitlines()[-1])
    else:
        say(BAD, '② aiohttp 缺失 —— 小窗 agent.py / launcher.py 都起不来')
        say(WARN, '   不建 .venv、不联网装包（比赛机无外网）：直接上报，'
                  '换一台环境正常的机器')
        bad += 1

    # ③ psutil（可选）
    rc, out = run(py, 'import psutil;print(psutil.__version__)')
    if rc == 0:
        say(OK, '③ psutil %s' % out.splitlines()[-1])
    else:
        say(WARN, '③ psutil 缺失（可选，只影响 launcher 关掉旧窗口）')

    # ④ entitys 导入（等价于智能体开局那几行 import）
    #    注意：这条链会拉起 ray.rllib -> tensorflow -> absl，absl 要用 tempfile。
    #    若 TEMP/TMP 指向不可写的目录（本机就出现过：账户改名后 USERPROFILE 还是
    #    C:\Users\A，Temp 不可写），会报“No usable temporary directory”这种与
    #    entitys 无关的假失败。所以给它一个能写的 TEMP 再判。
    probe_tmp = writable_tmp([os.environ.get('TEMP'), os.environ.get('TMP'),
                              os.path.join(root, 'intelligent', 'ai', 'logs'),
                              ai, root, os.getcwd()])
    rc, out = run(py, 'import sys;sys.path.insert(0,r"%s");'
                      'from engine.LingYi.entitys.player import Player;'
                      'from engine.LingYi.entitys.agent_base import RuleAgentBase;'
                      'print(RuleAgentBase.__name__)' % ai,
                  env_extra={'TEMP': probe_tmp, 'TMP': probe_tmp}
                  if probe_tmp else None)
    if rc == 0:
        say(OK, '④ engine.LingYi.entitys 可导入（%s）' % out.splitlines()[-1])
    else:
        say(BAD, '④ entitys 导入失败 —— 看 %s\\engine\\LingYi\\entitys 是否完整' % ai)
        print('     ' + out.replace('\n', '\n     '))
        bad += 1

    # ⑤ 小窗文件是否就位
    overlay = os.path.join(ai, 'agent', 'overlay')
    for f in ('agent.py', 'launcher.py', 'web\\overlay.html', 'weapons.json'):
        p = os.path.join(overlay, f)
        say(OK if os.path.exists(p) else WARN,
            '⑤ 小窗文件 %s %s' % ('在' if os.path.exists(p) else '缺', p))

    # ⑥ 小窗状态目录可写（防空值班按钮靠它传指令，写不进去会静默失效）
    state_dir = (os.environ.get('LY_SAM_STATE_DIR')
                 or os.path.join(os.environ.get('LOCALAPPDATA') or
                                 os.environ.get('TEMP') or
                                 os.path.expanduser('~'), 'LingYiOverlay'))
    try:
        if not os.path.isdir(state_dir):
            os.makedirs(state_dir)
        probe = os.path.join(state_dir, '_probe.tmp')
        with open(probe, 'w') as f:
            f.write('x')
        os.remove(probe)
        say(OK, '⑥ 小窗状态目录可写 %s' % state_dir)
    except Exception as e:                                   # noqa: BLE001
        say(BAD, '⑥ 小窗状态目录不可写 %s —— 防空值班按钮会静默失效' % state_dir)
        say(WARN, '   %s；可用 LY_SAM_STATE_DIR 指到一个可写目录（小窗与'
                  ' SamBattalionDefense 两侧必须一致）' % e)
        bad += 1

    print('')
    if bad:
        say(BAD, '结论：%d 项硬性检查没过 —— 终止，不要上机跑' % bad)
        say(WARN, '本工具只检查、不安装；比赛机无外网，请把上面 [FAIL] 行'
                  '连同 <灵弈>\\intelligent\\new_env 的目录列表报上来')
    else:
        say(OK, '结论：可以直接用灵弈自带 Python 跑，不需要 .venv')
    say(WARN, '小窗 bat 里对应的一行：%s' % bat_line)
    return 0 if bad == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
