# -*- coding: utf-8 -*-
"""
监控小窗的窗口管理（跟「灵弈小窗」是两套独立进程、独立端口，可以同时开）。

分工：
  · 智能体（monitor_ai.py）在客户端进程里跑，负责算，WebSocket 开在 127.0.0.1:8762
  · 本进程只负责“把页面放到最前面”：起一个本地网页服务（127.0.0.1:8763），
    用 Edge/Chrome 的 --app 模式开成无地址栏小窗口，并定期检查是否被全屏的
    灵弈客户端盖住，盖住就重新置顶。

三种运行模式：
  （默认）     开窗口 + 置顶
  --serve-only  只起页面服务，不开浏览器（调试 / 在别的机器上看页面）
  --check       用 Edge 无头模式把页面渲一张 png 出来（**不需要可见桌面**），
                用来验证“页面到底能不能渲染”——本次灰屏排查就是靠它定位的

⚠ 曾经的两个坑（都修掉了，别改回去）：
  1. 以前靠窗口标题「监控小窗」找自己的窗口，而页面在有单元被攻击时会把标题改成
     「监控 x/y/z」——标题一变就找不到窗口，4 秒后判定“窗口被关了”直接退出，
     页面服务随之消失 → 页面 ERR_ABORTED / 灰屏。
     现在：① 页面标题始终以「监控小窗」开头；② 退出条件改成“浏览器进程真的没了”。
  2. 计划任务以管理员（高完整性级别）起，Edge 的渲染进程在 --app 小窗里会崩
     （RenderProcessGone + crashpad dump）。现在默认加 --no-sandbox --disable-gpu。
"""
import asyncio
import ctypes
import ctypes.wintypes as wt
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from aiohttp import web

HERE = Path(__file__).resolve().parent
WEB = HERE / "lymonitor" / "web"
LOGS = HERE / "logs"
PID_FILE = LOGS / "launcher.pid"
LOG_FILE = LOGS / "launcher.log"
PAGE_PORT = int(os.environ.get("LY_MONITOR_PAGE_PORT", "8763"))
AGENT_PORT = int(os.environ.get("LY_MONITOR_PORT", "8762"))
TITLE = "监控小窗"
W, H = 520, 900

# 浏览器命令行开关（可用环境变量关闭其中某几个）
NO_SANDBOX = os.environ.get("LY_MONITOR_NO_SANDBOX", "1") == "1"
NO_GPU = os.environ.get("LY_MONITOR_NO_GPU", "1") == "1"

user32 = ctypes.WinDLL("user32", use_last_error=True)
dwm = ctypes.WinDLL("dwmapi")
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]
user32.GetWindow.argtypes = [wt.HWND, wt.UINT]
user32.GetWindow.restype = wt.HWND
user32.GetWindowLongW.argtypes = [wt.HWND, ctypes.c_int]
user32.GetForegroundWindow.restype = wt.HWND
user32.IsWindow.argtypes = [wt.HWND]
user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
HWND_TOPMOST = wt.HWND(-1)                  # 64 位下必须按指针传，按 int 传会被截成无效句柄
SWP_FLAGS = 0x0001 | 0x0002 | 0x0010         # 不改大小、不挪、不抢焦点
GW_HWNDPREV = 3
WS_EX_TOPMOST = 0x8


def session_id():
    try:
        import ctypes.wintypes as _wt
        pid = ctypes.wintypes.DWORD(0) if False else None
        return ctypes.c_ulong(0).value if False else _my_session()
    except Exception:
        return '?'


def _my_session():
    """当前进程所在 Windows 会话号。Edge/Plat 这类 Qt/Chromium 程序在 Session 0
    会直接报「Failed to create a message-only window: 拒绝访问」，
    所以日志里必须带这个数（1 = 交互桌面，0 = 服务/SSH）。"""
    try:
        sid = ctypes.c_ulong(0)
        ctypes.windll.kernel32.ProcessIdToSessionId(
            ctypes.windll.kernel32.GetCurrentProcessId(), ctypes.byref(sid))
        return sid.value
    except Exception:
        return '?'


def log(msg):
    line = '[%s][sess=%s] %s' % (time.strftime('%H:%M:%S'), _my_session(), msg)
    print(line, flush=True)
    try:
        LOGS.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


# ---------------------------------------------------------------------- 网页服务
def page():
    """页面里 /web/xxx.js 带上修改时间当版本号，改完刷新就是新的。"""
    html = (WEB / "monitor.html").read_text(encoding="utf-8")

    def ver(m):
        f = WEB / m.group(1)[5:]
        return f'{m.group(1)}?v={int(f.stat().st_mtime) if f.exists() else 0}"'

    html = re.sub(r'(/web/[\w.]+\.(?:js|css))"', ver, html)
    return web.Response(text=html, content_type="text/html",
                        headers={"Cache-Control": "no-store"})


def serve(block=True):
    """起页面服务。block=False 时返回 (loop, runner) 由调用方收尾。"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = web.Application()

    async def h_page(req):
        return page()

    async def h_ping(req):
        return web.json_response({"ok": True, "agent": AGENT_PORT})

    app.router.add_get("/", h_page)
    app.router.add_get("/ping", h_ping)
    app.router.add_static("/web/", WEB, show_index=False)
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    loop.run_until_complete(web.TCPSite(runner, "127.0.0.1", PAGE_PORT).start())
    log('页面服务已监听 http://127.0.0.1:%d/（数据来自 127.0.0.1:%d）' % (PAGE_PORT, AGENT_PORT))
    if block:
        loop.run_forever()
    return loop, runner


def serve_in_thread():
    t = threading.Thread(target=serve, daemon=True, name="page-srv")
    t.start()
    return t


# ---------------------------------------------------------------------- 窗口
def kill_old():
    try:
        import psutil
        pid = int(PID_FILE.read_text())
        if pid != os.getpid() and "launcher.py" in " ".join(psutil.Process(pid).cmdline()):
            psutil.Process(pid).kill()
            time.sleep(0.5)
    except Exception:
        pass
    LOGS.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def find_browser():
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                 os.environ.get("LOCALAPPDATA")):
        for rel in ("Microsoft/Edge/Application/msedge.exe",
                    "Google/Chrome/Application/chrome.exe"):
            if base and (Path(base) / rel).exists():
                return str(Path(base) / rel)
    return None


def title_of(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


def find_windows():
    """按标题前缀找小窗（页面标题始终以「监控小窗」开头，见 monitor.js）。"""
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd) and TITLE in title_of(hwnd):
            found.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    return found


def close_old():
    for h in find_windows():
        user32.PostMessageW(h, 0x0010, 0, 0)     # WM_CLOSE
    for _ in range(30):
        if not find_windows():
            return
        time.sleep(0.1)


def cloaked(hwnd):
    v = ctypes.c_int(0)
    dwm.DwmGetWindowAttribute(wt.HWND(hwnd), 14, ctypes.byref(v), ctypes.sizeof(v))   # DWMWA_CLOAKED
    return v.value != 0


def rect(hwnd):
    r = wt.RECT()
    user32.GetWindowRect(wt.HWND(hwnd), ctypes.byref(r))
    return r


def covered(hwnd):
    """z 序在小窗上面、看得见、跟小窗有重叠的窗口（全屏客户端、别的置顶窗）。"""
    me = rect(hwnd)
    h = user32.GetWindow(hwnd, GW_HWNDPREV)
    while h:
        if user32.IsWindowVisible(h) and not cloaked(h):
            r = rect(h)
            if r.right > r.left + 8 and r.bottom > r.top + 8 and \
                    r.left < me.right and r.right > me.left and \
                    r.top < me.bottom and r.bottom > me.top:
                return True
        h = user32.GetWindow(h, GW_HWNDPREV)
    return False


def pin(hwnd):
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS)


def profile_dir(name='browser'):
    """给浏览器找一个可写的独立 profile 目录。

    ⚠ 实测（2026-11-17）：目标机上的 `ray210\python.exe` **建不了 %TEMP% 下的目录**
      （`PermissionError [WinError 5] 拒绝访问`，同一时刻 PowerShell 建同一路径却成功，
       像杀软的行为拦截），而项目内 `logs\browser` 一直都行。
      所以这里按“项目内 → %TEMP%”的顺序试，**任何一步都不抛异常**。
    """
    cands = [LOGS / name, LOGS / (name + '_%d' % os.getpid()),
             Path(os.environ.get("TEMP") or os.environ.get("TMP") or ".") / ('ly_' + name)]
    for d in cands:
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log('profile 目录不可用 %s（%s）' % (d, e))
            continue
        for junk in ("lockfile", "SingletonLock", "SingletonSocket", "SingletonCookie"):
            try:
                (d / junk).unlink()
            except Exception:
                pass
        log('浏览器 profile = %s' % d)
        return d
    log('⚠ 所有 profile 目录都建不了，退化成临时 profile（不稳定）')
    return None


def browser_flags(profile, extra=()):
    f = ([f'--user-data-dir={profile}'] if profile else []) + [
         '--no-first-run', '--no-default-browser-check',
         '--disable-background-timer-throttling',
         '--disable-renderer-backgrounding',
         '--disable-backgrounding-occluded-windows',
         '--hide-crash-restore-bubble',      # 别弹“上次未正常关闭，恢复页面”的气泡
         '--noerrdialogs']
    if NO_SANDBOX:
        f.append('--no-sandbox')          # 管理员（高完整性级别）下渲染进程沙箱会崩
    if NO_GPU:
        f += ['--disable-gpu', '--disable-gpu-compositing']
    return f + list(extra)


def check_render(out_png=None, timeout=60):
    """用 Edge/Chrome 无头模式把页面渲一张图 —— 不需要可见桌面。
    返回 (ok, 说明)。"""
    exe = find_browser()
    if not exe:
        return False, '找不到 Edge/Chrome'
    out = Path(out_png or (LOGS / 'render-check.png'))
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    prof = profile_dir('browser_check')
    cmd = [exe, '--headless=new'] + browser_flags(prof) + [
        f'--screenshot={out}', f'--window-size={W},{H}', '--hide-scrollbars',
        f'http://127.0.0.1:{PAGE_PORT}/']
    log('无头渲染检查：%s' % ' '.join(cmd))
    try:
        p = subprocess.run(cmd, timeout=timeout, capture_output=True)
    except Exception as e:
        return False, '启动失败 %s' % e
    for _ in range(40):
        if out.exists() and out.stat().st_size > 1000:
            return True, '%s (%d 字节)' % (out, out.stat().st_size)
        time.sleep(0.25)
    err = (p.stderr or b'')[-800:].decode('utf-8', 'replace')
    return False, '没生成图片；退出码=%s stderr=%s' % (p.returncode, err)


def open_window(url, profile):
    exe = find_browser()
    if not exe:
        import webbrowser
        webbrowser.open(url)
        log('没找到 Edge / Chrome，用默认浏览器打开（不能置顶）')
        return None
    try:
        scale = user32.GetDpiForSystem() / 96 if hasattr(user32, "GetDpiForSystem") else 1.0
    except Exception:
        scale = 1.0
    sw = user32.GetSystemMetrics(0) / scale
    args = [exe, f'--app={url}', f'--window-size={W},{H}',
            f'--window-position={int(max(0, sw - W - 30))},60'] + browser_flags(profile)
    p = subprocess.Popen(args)
    log('已启动浏览器 pid=%d' % p.pid)
    return p


def main():
    mode = 'run'
    for a in sys.argv[1:]:
        if a in ('--serve-only', '-s'):
            mode = 'serve'
        elif a in ('--check', '-c'):
            mode = 'check'
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    if mode == 'serve':
        LOGS.mkdir(parents=True, exist_ok=True)
        serve(block=True)
        return

    if mode == 'check':
        LOGS.mkdir(parents=True, exist_ok=True)
        ok, why = check_render()
        log('无头渲染检查：%s —— %s' % ('通过' if ok else '失败', why))
        sys.exit(0 if ok else 1)

    # ---- 正常运行：页面服务 + 置顶窗口 ----
    kill_old()
    close_old()
    serve_in_thread()
    time.sleep(0.8)
    url = (f"http://127.0.0.1:{PAGE_PORT}/"
           + ("" if AGENT_PORT == 8762 else f"?agent=127.0.0.1:{AGENT_PORT}"))
    prof = profile_dir('browser')
    proc = open_window(url, prof)
    log('客户端里导入 monitor-agent\\monitor_ai.py（类名 Agent）并启动即可出数据')

    hwnd, last_find, last_pin = None, 0.0, 0.0
    t0 = time.time()
    gone_since = 0.0
    relaunch = 0
    while True:
        now = time.time()
        if now - last_find > 1.0:
            last_find = now
            w = find_windows()
            h = w[0] if w else None
            if h:
                if h != hwnd:
                    pin(h)
                    log('找到小窗 hwnd=%s' % h)
                hwnd, gone_since = h, 0.0
            else:
                hwnd = None
                gone_since = gone_since or now
                # 退出条件：**浏览器进程真的没了**，或 60 秒都没出现窗口。
                # 不能只看“找不到窗口”——标题一变就找不到，会把自己退掉（老 bug）。
                dead = (proc is not None and proc.poll() is not None)
                if dead:
                    if relaunch < 2 and now - t0 < 3600:
                        relaunch += 1
                        log('浏览器进程已退出，第 %d 次重开' % relaunch)
                        proc = open_window(url, prof)
                        time.sleep(1.0)
                        continue
                    log('浏览器退出且不重开，收工')
                    break
                if now - gone_since > 60 and now - t0 > 90:
                    log('60 秒没找到小窗窗口，收工（浏览器进程还在 pid=%s）'
                        % (getattr(proc, 'pid', '?')))
                    break
        if hwnd and now - last_pin > 0.25:
            last_pin = now
            try:
                if not user32.GetWindowLongW(hwnd, -20) & WS_EX_TOPMOST \
                        or covered(hwnd) or now - t0 < 30:
                    pin(hwnd)
            except Exception:
                pass
        time.sleep(0.02)


if __name__ == "__main__":
    if sys.platform == "win32":
        main()
    else:
        print("只有 Windows 上才需要 launcher（置顶窗口）。Linux 上直接看 "
              f"http://127.0.0.1:{PAGE_PORT}/ 即可。")
