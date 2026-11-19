# -*- coding: utf-8 -*-
"""灵弈小窗（跟网页版指挥台是两个项目）：灵弈客户端全屏打，上面强制置顶叠一个小窗口，补客户端灰掉的
  Shift+F1 武器分配、F2 油门高度。双击 灵弈小窗.bat 起这个；客户端那边导入 agent/overlay_ai.py（类名 Agent）供态势、下指令
  - 本进程自己当网页服务（127.0.0.1:8761 给小窗页面），页面直接连智能体 127.0.0.1:8760
  - 小窗是 Edge / Chrome 的 --app 窗口
  - 每 0.25 秒看一眼被盖住没有，盖住了就重新置顶（客户端全屏也压得住）
  - 全局热键（默认 Alt+Q 武器分配、Alt+W 油门高度、Alt+E 防空值班，settings.json "keys" 可改）：按下呼出小窗并切面板，
    小窗开着且就在这个面板时再按一次收起；热键被这里抢走，客户端收不到这几个键
  - 再双击会关掉旧的换新的；小窗关了这个进程就退"""
import asyncio
import ctypes
import ctypes.wintypes as wt
import json
import os
import re
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

from aiohttp import web

HERE = Path(__file__).resolve().parent
WEB = HERE / "web"
LOGS = HERE / "logs"
LAUNCH_LOG = LOGS / "launcher.log"


class _Tee:
    """stdout/stderr 同时写进 overlay/logs/launcher.log。

    双击 bat 起的窗口一关，控制台输出就没了 —— 上一版排查时这里什么都没有。
    """
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            try:
                st.write(s)
                st.flush()
            except Exception:
                pass
        return len(s)

    def flush(self):
        for st in self.streams:
            try:
                st.flush()
            except Exception:
                pass

    def isatty(self):
        return False


def setup_log():
    """把 stdout/stderr 接一份到 logs/launcher.log（超过 2MB 覆盖重来）。"""
    try:
        LOGS.mkdir(parents=True, exist_ok=True)
        try:
            if LAUNCH_LOG.exists() and LAUNCH_LOG.stat().st_size > 2 * 1024 * 1024:
                os.replace(str(LAUNCH_LOG), str(LOGS / "launcher.1.log"))
        except Exception:
            pass
        f = open(str(LAUNCH_LOG), "a", encoding="utf-8", buffering=1)
        f.write("\n==== %s launcher 启动 pid=%s ====\n"
                % (time.strftime("%Y-%m-%d %H:%M:%S"), os.getpid()))
        sys.stdout = _Tee(sys.__stdout__ or sys.stdout, f)
        sys.stderr = _Tee(sys.__stderr__ or sys.stderr, f)
        return f
    except Exception:
        return None
PID_FILE = LOGS / "launcher.pid"
PAGE_PORT = int(os.environ.get("LY_OVERLAY_PAGE_PORT", "8761"))
TITLE = "灵弈小窗"
W, H = 480, 860
# 小窗专用浏览器 profile：默认放 %LOCALAPPDATA%\LingYiOverlay\browser
#   - 放 C 盘：目标机 D 只剩几百 MB
#   - 独立目录：不跟用户日常 Edge 抢单例，也便于出问题时整个删掉重来
PROFILE = Path(os.environ.get("LY_OVERLAY_PROFILE")
               or (Path(os.environ.get("LOCALAPPDATA") or str(LOGS))
                   / "LingYiOverlay" / "browser"))
# 开窗方式：1=Edge --app（无地址栏，但这台机器上 network service 会崩）；
#           0=普通窗口（带地址栏，用户实测能正常显示）
APP_MODE = (os.environ.get("LY_OVERLAY_APP") or "0") not in ("0", "", "no", "false")
DEFAULT_KEYS = {"weapon": "Alt+Q", "thralt": "Alt+W", "sam": "Alt+E"}
KEY_CN = {"weapon": "武器分配", "thralt": "油门高度", "sam": "防空值班"}
KEY = {"n": 0, "k": ""}             # 热键按了几次 / 最后按的哪个（页面轮询 /key）
STATE = {"hwnd": None, "tab": "weapon", "hidden": False}

user32 = ctypes.WinDLL("user32", use_last_error=True)
dwm = ctypes.WinDLL("dwmapi")
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]
user32.GetWindow.argtypes = [wt.HWND, wt.UINT]
user32.GetWindow.restype = wt.HWND
user32.GetWindowLongW.argtypes = [wt.HWND, ctypes.c_int]
user32.GetForegroundWindow.restype = wt.HWND
user32.IsWindow.argtypes = [wt.HWND]
user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
MOD = {"alt": 1, "ctrl": 2, "shift": 4, "win": 8}
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
HWND_TOPMOST = wt.HWND(-1)          # 64 位下必须按指针传，按 int 传会被截成 0xFFFFFFFF（无效句柄，置顶不生效）
SWP_FLAGS = 0x0001 | 0x0002 | 0x0010          # 不改大小、不挪、不抢焦点
GW_HWNDPREV = 3
WS_EX_TOPMOST = 0x8


def settings():
    try:
        return json.loads((HERE / "settings.json").read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def keys():
    return dict(DEFAULT_KEYS, **(settings().get("keys") or {}))


def parse_key(text):
    """"Alt+Q" -> (修饰键, 虚拟键码)；认 Ctrl/Alt/Shift/Win + 字母 / 数字 / F1~F24 / ` """
    mods, vk = 0, None
    for part in text.replace(" ", "").split("+"):
        p = part.lower()
        if p in MOD:
            mods |= MOD[p]
        elif len(p) == 1 and p.isalnum():
            vk = ord(p.upper())
        elif p[:1] == "f" and p[1:].isdigit() and 1 <= int(p[1:]) <= 24:
            vk = 0x6F + int(p[1:])
        elif p in ("`", "~"):
            vk = 0xC0
    return mods, vk


# ---------------------------------------------------------------------- 网页服务（小窗页面 + 武器名 + 热键状态）
def page():
    """页面里的 /web/xxx.js|css 带修改时间当版本号，改了就拿新的"""
    html = re.sub(r'(/web/[\w.]+\.(?:js|css))"',
                  lambda m: f'{m.group(1)}?v={int((WEB / m.group(1)[5:]).stat().st_mtime) if (WEB / m.group(1)[5:]).exists() else 0}"',
                  (WEB / "overlay.html").read_text(encoding="utf-8"))
    return web.Response(text=html, content_type="text/html", headers={"Cache-Control": "no-store"})


def serve():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = web.Application()
    async def h_page(req):
        return page()

    async def h_catalog(req):
        return web.FileResponse(HERE / "weapons.json")

    async def h_key(req):
        return web.json_response(dict(KEY, keys=keys()))

    async def h_tab(req):
        if req.query.get("t") in DEFAULT_KEYS:
            STATE["tab"] = req.query["t"]
        return web.json_response({"ok": True})

    async def h_hide(req):
        hide()
        return web.json_response({"ok": True})

    app.router.add_get("/", h_page)
    app.router.add_get("/catalog", h_catalog)
    app.router.add_get("/key", h_key)
    app.router.add_get("/tab", h_tab)
    app.router.add_get("/hide", h_hide)
    app.router.add_static("/web/", WEB, show_index=False)
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    loop.run_until_complete(web.TCPSite(runner, "127.0.0.1", PAGE_PORT).start())
    print("页面服务已监听 127.0.0.1:%s" % PAGE_PORT, flush=True)
    try:
        loop.run_forever()
    except Exception:
        print("页面服务异常退出：\n%s" % traceback.format_exc(), flush=True)
        raise


def serve_forever():
    """页面服务挂了就重启 —— 一挂了 8761 没人应答，小窗窗口立刻变灰。"""
    while True:
        try:
            serve()
            return
        except Exception:
            print("页面服务重启中：\n%s" % traceback.format_exc(), flush=True)
            time.sleep(1)


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


def kill_profile_browsers():
    """杀掉正用我们 profile 的 msedge。

    Chromium 是单例：同 --user-data-dir 再启一次会“交接”给已有实例然后自己退出。
    之前那个已经崩成灰屏的实例还活着，于是每次双击 bat 都是「等很久 + 还是灰」。
    """
    try:
        import subprocess as _sp
        ps = ("Get-CimInstance Win32_Process -Filter \"Name='msedge.exe'\" | "
              "Where-Object { $_.CommandLine -like '*%s*' } | "
              "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
              % str(PROFILE))
        _sp.run(["powershell", "-NoProfile", "-Command", ps],
                stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, timeout=15)
        time.sleep(0.6)
    except Exception as e:
        print("清理旧浏览器失败：%s" % e, flush=True)
    for name in ("lockfile", "SingletonLock", "SingletonCookie", "SingletonSocket"):
        try:
            (PROFILE / name).unlink()
        except Exception:
            pass


def find_browser():
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
        for rel in ("Microsoft/Edge/Application/msedge.exe", "Google/Chrome/Application/chrome.exe"):
            if base and (Path(base) / rel).exists():
                return str(Path(base) / rel)
    return None


def title_of(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]


def find_windows(pid=None):
    """找小窗窗口。

    优先按**我们 spawn 的浏览器进程 PID**认（--app 窗口归属主进程），
    标题只作兜底：页面没渲染出来时标题是 "127.0.0.1:8761" 而不是
    "灵弈小窗"，只靠标题会一直找不到 —— 上一版就是这样：窗口明明开着，
    launcher 干等 60 秒后自己退出，8761 一关，窗口就变成灰屏。
    """
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        if pid:
            p = wt.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if p.value == pid:
                found.append(hwnd)
                return True
        if TITLE in title_of(hwnd):
            found.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    return found


def find_window(pid=None):
    found = find_windows(pid)
    return found[0] if found else None


def close_old():
    """上次留下的小窗（浏览器还开着）先关掉，不然新旧两个叠在一起"""
    for h in find_windows():
        user32.PostMessageW(h, 0x0010, 0, 0)
    for _ in range(30):
        if not find_windows():
            return
        time.sleep(0.1)


def cloaked(hwnd):
    v = ctypes.c_int(0)
    dwm.DwmGetWindowAttribute(wt.HWND(hwnd), 14, ctypes.byref(v), ctypes.sizeof(v))     # DWMWA_CLOAKED
    return v.value != 0


def rect(hwnd):
    r = wt.RECT()
    user32.GetWindowRect(wt.HWND(hwnd), ctypes.byref(r))
    return r


def covered(hwnd):
    """z 序里在小窗上面、看得见、跟小窗有重叠的窗口（全屏客户端、别的置顶窗口）"""
    me = rect(hwnd)
    h = user32.GetWindow(hwnd, GW_HWNDPREV)
    while h:
        if user32.IsWindowVisible(h) and not cloaked(h):
            r = rect(h)
            if r.right > r.left + 8 and r.bottom > r.top + 8 and \
                    r.left < me.right and r.right > me.left and r.top < me.bottom and r.bottom > me.top:
                return True
        h = user32.GetWindow(h, GW_HWNDPREV)
    return False


def hide():
    if STATE["hwnd"]:
        STATE["hidden"] = True
        user32.ShowWindow(STATE["hwnd"], 0)          # SW_HIDE，焦点自动回客户端


def show(hwnd):
    STATE["hidden"] = False
    user32.ShowWindow(hwnd, 5)                       # SW_SHOW
    bring_front(hwnd)


def pin(hwnd):
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS)


def bring_front(hwnd):
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    pin(hwnd)
    fg = user32.GetForegroundWindow()
    me, other = ctypes.windll.kernel32.GetCurrentThreadId(), user32.GetWindowThreadProcessId(fg, None)
    attached = other and other != me and user32.AttachThreadInput(me, other, True)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    if attached:
        user32.AttachThreadInput(me, other, False)


def main():
    setup_log()
    print("launcher: HERE=%s PAGE_PORT=%s" % (HERE, PAGE_PORT))
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    kill_old()
    close_old()
    threading.Thread(target=serve_forever, daemon=True, name="page-server").start()
    time.sleep(0.5)
    url = f"http://127.0.0.1:{PAGE_PORT}/"
    exe = find_browser()
    proc = None
    if exe:
        scale = user32.GetDpiForSystem() / 96 if hasattr(user32, "GetDpiForSystem") else 1.0
        sw = user32.GetSystemMetrics(0) / scale
        # --disable-gpu：这台机器上 Edge 的 GPU/渲染进程崩过一次（Crashpad 有 7MB dmp），
        # 崩完窗口就是灰的。纯 2D 小窗用软件渲染足够，稳字优先。
        window_arg = f"--app={url}" if APP_MODE else f"--new-window={url}"
        try:
            PROFILE.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        kill_profile_browsers()
        ww, wh = (W, H) if APP_MODE else (W + 16, H + 40)
        args = [exe, window_arg, f"--window-size={ww},{wh}",
                f"--window-position={int(max(0, sw - W - 30))},60",
                f"--user-data-dir={PROFILE}", "--no-first-run", "--no-default-browser-check",
                "--disable-gpu", "--disable-gpu-compositing",
                "--disable-features=CalculateNativeWinOcclusion,RendererCodeIntegrity",
                "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                # 本机回环一律直连，绕开任何系统代理/加速器
                "--no-proxy-server", "--proxy-bypass-list=<-loopback>",
                # 把 Chromium 自己的日志接到 logs/browser.out，页面加载失败才看得见原因
                "--enable-logging=stderr", "--v=0"]
        try:
            BROW_OUT = open(str(LOGS / "browser.out"), "w", encoding="utf-8", errors="replace")
        except Exception:
            BROW_OUT = subprocess.DEVNULL
        print("小窗浏览器URL %s" % url, flush=True)
        proc = subprocess.Popen(args, stdout=BROW_OUT, stderr=subprocess.STDOUT)
        print("小窗浏览器已启动 pid=%s（%s, profile=%s, 日志 logs/browser.out）"
              % (proc.pid, "--app" if APP_MODE else "普通窗口", PROFILE), flush=True)
    else:
        import webbrowser
        webbrowser.open(url)
        print("没找到 Edge / Chrome，用默认浏览器开了小窗页面（不能置顶）", flush=True)
    ids = {}
    for i, (k, text) in enumerate(keys().items(), 1):
        mods, vk = parse_key(text)
        if vk and user32.RegisterHotKey(None, i, mods | MOD_NOREPEAT, vk):
            ids[i] = k
        else:
            print(f"热键 {text} 注册不上（被别的程序占了？），小窗照样能点", flush=True)
    print(f"灵弈小窗已打开；热键 " + " / ".join(f"{v} {KEY_CN.get(k, k)}" for k, v in keys().items()), flush=True)
    hwnd, seen, gone, last_find, last_pin = None, False, 0.0, 0.0, 0.0
    msg = wt.MSG()
    t0 = time.time()
    bpid = proc.pid if proc is not None else None
    relaunch = 0
    while True:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            if msg.message == WM_HOTKEY and msg.wParam in ids:
                k = ids[msg.wParam]
                if hwnd and not STATE["hidden"] and STATE["tab"] == k:
                    hide()                          # 开着且就在这个面板：再按一次收起
                    continue
                if hwnd:
                    show(hwnd)
                STATE["tab"] = k
                KEY["n"] += 1
                KEY["k"] = k
        now = time.time()
        if STATE["hidden"]:                         # 收起时窗口不可见，find_window 找不到，别当成关了
            if not user32.IsWindow(hwnd):
                break
            time.sleep(0.02)
            continue
        if now - last_find > 1.0:
            last_find = now
            h = find_window(bpid)           # 先按浏览器 PID 认，标题只兜底
            if h:
                if h != hwnd:
                    pin(h)
                    STATE["hwnd"] = h
                hwnd, seen, gone = h, True, 0.0
            elif seen:
                hwnd = STATE["hwnd"] = None
                gone = gone or now
                if now - gone > 4 and (proc is None or proc.poll() is not None):
                    break                   # 窗口没了且浏览器也退了：真关了
            elif bpid and proc is not None and proc.poll() is not None:
                break                       # 浏览器进程都没了，收工
            elif now - t0 > 25 and relaunch < 2:
                # 窗口一直没出来（渲染崩了/页面没加载）：重开一次，别干等 60 秒然后自己退
                relaunch += 1
                print("小窗窗口 %ds 没找到，重开浏览器（第 %d 次）" % (int(now - t0), relaunch), flush=True)
                try:
                    if proc is not None:
                        proc.kill()
                except Exception:
                    pass
                try:
                    if exe:
                        proc = subprocess.Popen(args, stdout=BROW_OUT, stderr=subprocess.STDOUT)
                        bpid = proc.pid
                        print("小窗浏览器已重启 pid=%s" % bpid, flush=True)
                except Exception as e:
                    print("重开失败：%s" % e, flush=True)
                t0 = now
            elif now - t0 > 60 and relaunch >= 2:
                # 重开两次都没找到窗口：不再自己退出（一退出 8761 就没了，窗口必灰），
                # 保持页面服务在跑，人可以在窗口里按 F5，或者关掉重开 bat。
                if not STATE.get("warned"):
                    STATE["warned"] = True
                    print("小窗窗口两次都没找到（可能渲染崩过）；页面仍在 "
                          "127.0.0.1:%s 上，可在窗口里按 F5，或关掉重开本 bat" % PAGE_PORT,
                          flush=True)
        if hwnd and now - last_pin > 0.25:
            last_pin = now
            try:
                if not user32.GetWindowLongW(hwnd, -20) & WS_EX_TOPMOST or covered(hwnd) or now - t0 < 30:
                    pin(hwnd)
            except Exception:
                pass
        time.sleep(0.02)
    for i in ids:
        user32.UnregisterHotKey(None, i)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            main()
            print("launcher: 正常退出（小窗关闭）")
        except Exception:
            import traceback
            try:
                LOGS.mkdir(parents=True, exist_ok=True)
                with open(str(LAUNCH_LOG), "a", encoding="utf-8") as f:
                    f.write("%s launcher 崩溃\n%s"
                            % (time.strftime("%Y-%m-%d %H:%M:%S"), traceback.format_exc()))
            except Exception:
                pass
            raise
