# -*- coding: utf-8 -*-
"""重建 agent/overlay/.venv（用灵弈自带的 Python 3.9 + 它的 aiohttp/psutil），并做一次启动自检。

- 用 --system-site-packages：venv 直接继承灵弈环境里已装好的 aiohttp / psutil（无需联网）
- 启动自检用 8799 端口，避免和别人正在跑的小窗（8761）冲突
- 自检完把 launcher 和它开的 Edge 窗口一起关掉
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

OVERLAY = r'C:\Users\grea\Desktop\agent\overlay'
VENV = os.path.join(OVERLAY, '.venv')
LINGYI_PY = r'D:\LingYi\intelligent\new_env\ray210\python.exe'
TEST_PORT = 8799


def log(msg):
    print(msg, flush=True)


def rm(p):
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)
    elif os.path.exists(p):
        os.remove(p)


def main():
    log('=== 1. 删掉旧的 .venv ===')
    rm(VENV)
    log('removed: %s' % (not os.path.exists(VENV)))

    log('=== 2. 用灵弈的 Python 重建 ===')
    log('base: %s' % LINGYI_PY)
    rc = subprocess.call([LINGYI_PY, '-m', 'venv', '--system-site-packages', VENV])
    log('venv rc=%d' % rc)
    vpy = os.path.join(VENV, 'Scripts', 'python.exe')
    if not os.path.exists(vpy):
        log('FAIL: venv python 不存在')
        return 1

    log('=== 3. 验证依赖 ===')
    code = ('import sys, aiohttp, psutil;'
            'print("python", sys.version.split()[0]);'
            'print("aiohttp", aiohttp.__version__);'
            'print("psutil", psutil.__version__)')
    rc = subprocess.call([vpy, '-c', code])
    log('verify rc=%d' % rc)
    if rc != 0:
        return 1

    log('=== 4. 启动自检（端口 %d）===' % TEST_PORT)
    env = dict(os.environ)
    env['LY_OVERLAY_PAGE_PORT'] = str(TEST_PORT)
    p = subprocess.Popen([vpy, '-X', 'utf8', os.path.join(OVERLAY, 'launcher.py')],
                         cwd=OVERLAY, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ok = False
    try:
        deadline = time.time() + 12
        while time.time() < deadline:
            if p.poll() is not None:
                log('launcher 已退出，rc=%s' % p.returncode)
                break
            try:
                with socket.create_connection(('127.0.0.1', TEST_PORT), 1):
                    ok = True
                    break
            except OSError:
                time.sleep(0.4)
        if ok:
            with urllib.request.urlopen('http://127.0.0.1:%d/' % TEST_PORT, timeout=5) as r:
                body = r.read(200)
            log('HTTP %d, 前 80 字节: %r' % (r.status, body[:80]))
    finally:
        try:
            p.kill()
        except Exception:
            pass
        time.sleep(1)
        # 关掉它开的 Edge --app 窗口（按 user-data-dir 认）
        ps = ('Get-CimInstance Win32_Process -Filter "Name=\'msedge.exe\'" | '
              'Where-Object { $_.CommandLine -like \'*agent\\overlay\\logs\\browser*\' } | '
              'ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }')
        subprocess.call(['powershell', '-NoProfile', '-Command', ps])
        log('已清理 launcher 与它开的 Edge 窗口')

    log('=== 结论：%s ===' % ('可以启动' if ok else '启动失败'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
