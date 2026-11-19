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
MON_TITLE = "监控小窗"          # 第二个窗口：被攻击监控（跟主小窗同一个智能体、同一个 ws）
MON_W, MON_H = 900, 880      # 空/海/陆 三列并排，够宽才不挤
MON_GAP = 12
MON_ENABLE = os.environ.get("LY_OVERLAY_NO_MONITOR", "0") == "0"
W, H = 480, 860
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
    """页面服务一挂，8761 就没人应答，小窗窗口立刻变灰 —— 所以挂了就重启。"""
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


def _spawn_browser(exe, args):
    """用 PowerShell 的 Start-Process 起浏览器。

    为什么不用 subprocess.Popen 直起：目标机实测同样的 exe/参数/profile，
    Popen 起的 --app 窗口标题停在 "127.0.0.1_/"、页面空白；改成
    `powershell Start-Process` 起就能正常渲染（已用截图对比确认）。
    """
    quoted = ",".join("'%s'" % a.replace("'", "''") for a in args)
    cmd = 'Start-Process -FilePath "%s" -ArgumentList %s' % (exe, quoted)
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", cmd], timeout=30,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print("Start-Process 起浏览器失败：%s" % e, flush=True)
        return None

    class _P(object):
        """只提供主循环要用的 pid / poll()：按浏览器 PID 认窗口 + 判断是否退出。"""
        def __init__(self, pid):
            self.pid = pid

        def poll(self):
            try:
                out = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "if (Get-Process -Id %d -ErrorAction SilentlyContinue) "
                     "{ 'alive' } else { 'gone' }" % self.pid],
                    stdout=subprocess.PIPE, timeout=10)
                return None if b"alive" in (out.stdout or b"") else 1
            except Exception:
                return None

    pid = 0
    for _ in range(20):                     # 最多等 10 秒拿到浏览器主进程 pid
        time.sleep(0.5)
        try:
            o = subprocess.run(["powershell", "-NoProfile", "-Command",
                                "(Get-CimInstance Win32_Process -Filter \"Name='msedge.exe'\" | "
                                "Where-Object { $_.CommandLine -like '*--user-data-dir*browser*' -and "
                                "$_.CommandLine -like '*--app=*' } | "
                                "Sort-Object CreationDate -Descending | "
                                "Select-Object -First 1).ProcessId"],
                               stdout=subprocess.PIPE, timeout=15)
            pid = int((o.stdout or b"0").decode("utf-8", "ignore").strip() or 0)
        except Exception:
            pid = 0
        if pid:
            break
    print("浏览器主进程 pid=%s" % (pid or "?"), flush=True)
    return _P(pid) if pid else None


def wait_port(port, timeout=15.0):
    """等到本机 port 真的能连通再开窗口（最多 15 秒）。"""
    import socket
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                dt = time.time() - t0
                if dt > 0.2:
                    print("页面服务就绪耗时 %.1f 秒" % dt, flush=True)
                return True
        except OSError:
            time.sleep(0.1)
    print("警告：%d 秒内页面服务还没就绪，仍尝试开窗口" % int(timeout), flush=True)
    return False


def kill_profile_browsers():
    """杀掉正用我们 profile 的 msedge，并清掉单例锁。

    Chromium 是单例：同 --user-data-dir 再启一次会“交接”给已有实例然后自己退出。
    目标机实测：上一次留下的 8 个 msedge 还在时，新起的窗口标题一直是
    "127.0.0.1_/"、页面压根没加载；全部杀干净后同样的参数就正常渲染了。
    """
    try:
        import subprocess as _sp
        ps = ("Get-CimInstance Win32_Process -Filter \"Name='msedge.exe'\" | "
              "Where-Object { $_.CommandLine -like '*%s*' } | "
              "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
              % str(LOGS / "browser"))
        _sp.run(["powershell", "-NoProfile", "-Command", ps],
                stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, timeout=15)
        time.sleep(0.8)
    except Exception as e:
        print("清理旧小窗浏览器失败：%s" % e, flush=True)
    # 注意：不要删 profile 里的 lockfile / Singleton* —— 实测删了之后新实例
    # 会起一个空白窗口（标题停在 URL），保留锁文件反而正常。


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
    """找小窗窗口：优先按我们 spawn 的浏览器 PID 认，标题只兜底。

    页面没加载出来时标题是 "127.0.0.1_/" 而不是 "灵弈小窗"，只靠标题会一直
    找不到 → 上一版就是干等 60 秒后自己退出 → 页面服务一关窗口永远是灰的。
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
        if TITLE in title_of(hwnd) or MON_TITLE in title_of(hwnd):
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

    url = "http://127.0.0.1:%d/" % PAGE_PORT
    host = HERE / "wv2" / "overlay_wv2.exe"     # 自带的 WebView2 宿主，普通权限启动
    exe = find_browser()
    if not exe and not host.exists():
        import webbrowser
        webbrowser.open(url)
        print("没找到 Edge / Chrome，用默认浏览器开了小窗页面（不能置顶）", flush=True)
        return

    scale = user32.GetDpiForSystem() / 96 if hasattr(user32, "GetDpiForSystem") else 1.0
    sw = user32.GetSystemMetrics(0) / scale
    prof = os.environ.get("LY_OVERLAY_PROFILE")   # 想要独立 profile 才设，默认用用户日常的
    # 用普通窗口(--new-window)而不是 --app：这台机器上由 launcher 派生的
    # --app 实例反复出现“标题停在 127.0.0.1_/、内容纯灰”，而普通窗口用户
    # 自己验证过能正常显示。代价是多一条地址栏。
    mode = os.environ.get("LY_OVERLAY_APP", "0")
    win_arg = ("--app=" + url) if mode not in ("0", "", "no", "false") else ("--new-window=" + url)
    ww, wh = (W, H) if mode not in ("0", "", "no", "false") else (W + 16, H + 40)
    barg = [win_arg, "--window-size=%d,%d" % (ww, wh),
            "--window-position=%d,60" % int(max(0, sw - W - 30)),
            "--no-first-run",
            "--no-default-browser-check", "--disable-sync", "--disable-extensions",
            "--disable-component-update",
            "--disable-features=msImplicitSignin,msEdgeSyncPromo,EdgeSyncPromo,msEdgeIdentityFRE",
            "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows"]
    if prof:
        barg.insert(3, "--user-data-dir=" + prof)

    # 用户数据目录（UDF）绝不能放 %LOCALAPPDATA%：这台机的
    # C:\Users\A\AppData\Local 不可写（新建子目录直接 WinError 5 拒绝访问），
    # 那正是 Edge 的 --app 窗口一直灰屏、WebView2 报 0x80070005 的根因。
    # 默认交给宿主用 exe 同级的 overlay_wv2.exe.WebView2（实测在普通权限下正常）。
    udf = os.environ.get("LY_OVERLAY_UDF", "")

    def spawn(tag, page=None, w=W, h=H, title=TITLE, x=-1, y=60):
        """开一个窗口。page 默认主小窗，第二个窗口用 web/monitor.html。

        首选自带的 WebView2 宿主：它只是把同一份页面装进一个窗口，不依赖
        msedge.exe，也不会再出现“派生实例不导航”的灰屏。args：
            <url> <宽> <高> <UDF> <窗口标题> <x> <y>
        """
        page = page or url
        if host.exists():
            try:
                if udf:
                    os.makedirs(udf, exist_ok=True)
                pr = subprocess.Popen([str(host), page, str(w), str(h), udf,
                                       title, str(int(x)), str(int(y))])
                print("%s 窗口已启动 pid=%s（WebView2, %s）" % (title, pr.pid, tag), flush=True)
                return pr
            except Exception as e:
                print("启动 WebView2 宿主失败：%s，改用 Edge" % e, flush=True)
        if not exe:
            return None
        """起浏览器。实测这台机器上“冷启动的第一个实例”经常不完成导航
        （窗口标题停在 127.0.0.1_/、纯灰），第二个实例才正常 —— 所以外面
        会按“标题没变成灵弈小窗”重开，tag 只用于日志。"""
        try:
            args2 = list(barg)
            if page != url:
                args2 = [a.replace("--app=" + url, "--app=" + page)
                          .replace("--new-window=" + url, "--new-window=" + page) for a in args2]
            pr = subprocess.Popen([exe] + args2)
            print("%s 浏览器已启动 pid=%s（%s）" % (title, pr.pid, tag), flush=True)
            return pr
        except Exception as e:
            print("启动浏览器失败：%s" % e, flush=True)
            return None

    wait_port(PAGE_PORT)
    if os.environ.get("LY_OVERLAY_NO_BROWSER"):
        print("LY_OVERLAY_NO_BROWSER=1：只跑页面服务，不开浏览器", flush=True)
        while True:
            time.sleep(3600)
    if prof:
        kill_profile_browsers()
    proc = spawn("默认 profile" if not prof else "独立 profile " + prof,
                 x=int(max(0, sw - W - 30)), y=60)
    proc_mon, mon_hwnd = None, None
    if MON_ENABLE:
        proc_mon = spawn("监控小窗", page=url + "web/monitor.html", w=MON_W, h=MON_H,
                         title=MON_TITLE,
                         x=int(max(0, sw - W - 30 - MON_W - MON_GAP)), y=60)
    else:
        print("LY_OVERLAY_NO_MONITOR=1：不开监控小窗", flush=True)

    ids = {}
    for i, (k, text) in enumerate(keys().items(), 1):
        mods, vk = parse_key(text)
        if vk and user32.RegisterHotKey(None, i, mods | MOD_NOREPEAT, vk):
            ids[i] = k
        else:
            print("热键 %s 注册不上（被别的程序占了？），小窗照样能点" % text, flush=True)
    print("灵弈小窗已打开；热键 " + " / ".join(
        "%s %s" % (v, KEY_CN.get(k, k)) for k, v in keys().items()), flush=True)

    hwnd, seen, gone = None, False, 0.0
    last_find = last_pin = last_mon = 0.0
    msg = wt.MSG()
    bpid = proc.pid if proc is not None else None
    loaded_at = 0.0
    spawn_t = time.time()
    tries = 1
    while True:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            if msg.message == WM_HOTKEY and msg.wParam in ids:
                k = ids[msg.wParam]
                if hwnd and not STATE["hidden"] and STATE["tab"] == k:
                    hide()
                    continue
                if hwnd:
                    show(hwnd)
                STATE["tab"] = k
                KEY["n"] += 1
                KEY["k"] = k
        now = time.time()
        if STATE["hidden"]:
            if not user32.IsWindow(hwnd):
                break
            time.sleep(0.02)
            continue

        if now - last_find > 1.0:
            last_find = now
            loaded = False
            h = find_window(bpid)
            if h is None and tries <= 4:
                h = find_window(None)           # 兜底：按标题找一个
            if h:
                if h != hwnd:
                    pin(h)
                    STATE["hwnd"] = h
                hwnd, seen, gone = h, True, 0.0
                if TITLE in title_of(h):
                    loaded = True
                    if not loaded_at:
                        loaded_at = now
                        print("小窗页面已加载（%.0f 秒）" % (now - spawn_t), flush=True)
            else:
                hwnd = STATE["hwnd"] = None
                if seen:
                    gone = gone or now
                    if now - gone > 6 and (proc is None or proc.poll() is not None):
                        break                   # 真被关了
            if not loaded and now - spawn_t > 40 and not STATE.get("warned"):
                STATE["warned"] = True
                print("小窗页面 40 秒未加载（标题=%r）；页面服务仍在 %s，"
                      "可在窗口里按 F5 或关掉重开本 bat"
                      % (title_of(h) if h else "", url), flush=True)

        # 监控小窗：只负责按 pid 认窗口 + 置顶，不参与热键/隐藏逻辑
        if proc_mon is not None and now - last_mon > 0.5:
            last_mon = now
            hm = find_window(proc_mon.pid)
            if hm and hm != mon_hwnd:
                mon_hwnd = hm
            if mon_hwnd and user32.IsWindow(mon_hwnd):
                try:
                    pin(mon_hwnd)
                except Exception:
                    pass
            elif proc_mon.poll() is not None:
                proc_mon = None            # 用户把监控小窗关了，就不再管它

        if hwnd and now - last_pin > 0.25:
            last_pin = now
            try:
                if not user32.GetWindowLongW(hwnd, -20) & WS_EX_TOPMOST or covered(hwnd) or now - spawn_t < 30:
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
            print("launcher: 正常退出（小窗关闭）", flush=True)
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
