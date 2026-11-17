# -*- coding: utf-8 -*-
"""
监控小窗的窗口管理（跟「灵弈小窗」是两套独立进程、独立端口，可以同时开）。

分工：
  · 智能体（monitor_ai.py）在客户端进程里跑，负责算，WebSocket 开在 127.0.0.1:8762
  · 本进程只负责“把页面放到最前面”：起一个本地网页服务（127.0.0.1:8763），
    用 Edge/Chrome 的 --app 模式开成无地址栏小窗口，并每 0.25 秒检查一次是否被
    全屏的灵弈客户端盖住，盖住就重新置顶。

双击 monitor\\监控小窗.bat 起这个；页面里的数据来自智能体，本进程不碰任何态势。
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
PAGE_PORT = int(os.environ.get("LY_MONITOR_PAGE_PORT", "8763"))
AGENT_PORT = int(os.environ.get("LY_MONITOR_PORT", "8762"))
TITLE = "监控小窗"
W, H = 520, 900

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


def serve():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = web.Application()

    async def h_page(req):
        return page()

    app.router.add_get("/", h_page)
    app.router.add_static("/web/", WEB, show_index=False)
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    loop.run_until_complete(web.TCPSite(runner, "127.0.0.1", PAGE_PORT).start())
    print(f"监控小窗页面：http://127.0.0.1:{PAGE_PORT}/   （数据来自 127.0.0.1:{AGENT_PORT}）", flush=True)
    loop.run_forever()


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


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    kill_old()
    close_old()
    threading.Thread(target=serve, daemon=True).start()
    time.sleep(0.5)
    url = (f"http://127.0.0.1:{PAGE_PORT}/"
           + ("" if AGENT_PORT == 8762 else f"?agent=127.0.0.1:{AGENT_PORT}"))
    exe = find_browser()
    if exe:
        scale = user32.GetDpiForSystem() / 96 if hasattr(user32, "GetDpiForSystem") else 1.0
        sw = user32.GetSystemMetrics(0) / scale
        subprocess.Popen([exe, f"--app={url}", f"--window-size={W},{H}",
                          f"--window-position={int(max(0, sw - W - 30))},60",
                          f"--user-data-dir={LOGS / 'browser'}", "--no-first-run",
                          "--no-default-browser-check",
                          "--disable-background-timer-throttling",
                          "--disable-renderer-backgrounding",
                          "--disable-backgrounding-occluded-windows"])
    else:
        import webbrowser
        webbrowser.open(url)
        print("没找到 Edge / Chrome，用默认浏览器打开了页面（不能置顶）", flush=True)

    print("监控小窗已打开；客户端里导入 monitor\\monitor_ai.py（类名 Agent）并启动即可出数据", flush=True)
    hwnd, seen, gone, last_find, last_pin = None, False, 0.0, 0.0, 0.0
    t0 = time.time()
    while True:
        now = time.time()
        if now - last_find > 1.0:
            last_find = now
            w = find_windows()
            h = w[0] if w else None
            if h:
                if h != hwnd:
                    pin(h)
                hwnd, seen, gone = h, True, 0.0
            elif seen:
                hwnd = None
                gone = gone or now
                if now - gone > 4:          # 小窗被关了，本进程退出
                    break
            elif now - t0 > 60:             # 一直没开出来
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
        print("只有 Windows 上才需要 launcher（置顶窗口）；Linux 直接看 "
              f"http://127.0.0.1:{PAGE_PORT}/ 即可。")
