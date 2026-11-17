# -*- coding: utf-8 -*-
"""无头引擎的启动 / 探活 / 关闭（远端 Windows 靶机）。

为什么需要这一层
----------------
灵弈的推演引擎 ``Plat.exe`` 是 Qt 控制台程序，**必须有可用的窗口站**
（Session 1 交互式桌面）。SSH 登录落在 Session 0，直接起会立刻失败：

    CreateWindow() for QEventDispatcherWin32 internal window failed (拒绝访问)
    Qt: INTERNAL ERROR: failed to install GetMessage hook: 5

因此本模块统一用「**计划任务 + Interactive 登录类型（SID）+ Highest**」把
启动动作投递到 Session 1，再用 TCP 探活确认 21001/22001 已监听。

引擎启动参数（实测正确形态，12 个参数）::

    Plat.exe <房间GUID> <ip> <rpc端口> <dds端口> 0 <ip> 0 0 <ip> 0 "" <房间名>

> 踩坑记录：官方 ``Data\\lyengine\\run.bat`` 里的 11 参数形态（``LOCAL ... 20001 0
> 127.0.0.1 6379 <密码> <房间>``）在本机会**一直挂着不监听**（CPU 0、无 21001），
> 换成上面 12 参数形态后 6~9 秒就绪。Redis 连不上只会刷日志，不影响 RPC。
"""
from __future__ import annotations

import base64
import os
import socket
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_SSH = os.path.expanduser("~/.cache/pi-ssh/ssh-hifive")
DEFAULT_HOST = os.environ.get("SCE_HOST", "10.42.97.205")
DEFAULT_LINGYI = os.environ.get("SCE_LINGYI", "D:/LingYi")


class RemoteError(RuntimeError):
    pass


# ---------------------------------------------------------------- 远端执行
class Target(object):
    """一台 Windows 靶机（通过 OpenSSH 命令行操作）。"""

    def __init__(self, host: str = DEFAULT_HOST, ssh: str = None,
                 lingyi: str = DEFAULT_LINGYI, timeout: float = 120.0):
        self.host = host
        self.ssh = ssh or os.environ.get("SCE_SSH", DEFAULT_SSH)
        self.lingyi = lingyi.rstrip("/")
        self.timeout = timeout
        self._cache = {}

    # ---------------- 基础通道
    def run(self, cmd: str, timeout: Optional[float] = None, check: bool = True) -> str:
        """在远端 cmd.exe 里跑一条命令（开启 UTF-8 代码页）。"""
        full = "chcp 65001 >nul & " + cmd
        p = subprocess.run([self.ssh, full], capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=timeout or self.timeout)
        out = (p.stdout or "") + (p.stderr or "")
        out = "\n".join(l for l in out.splitlines() if not l.startswith("** "))
        if check and p.returncode != 0:
            raise RemoteError("远端命令失败(%d)：%s\n%s" % (p.returncode, cmd, out[-1500:]))
        return out

    def ps(self, script: str, timeout: Optional[float] = None, check: bool = True) -> str:
        """执行一段 PowerShell（UTF-16LE + base64，避开中文与引号地狱）。"""
        b64 = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        cmd = ("powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass "
               "-EncodedCommand %s" % b64)
        p = subprocess.run([self.ssh, "chcp 65001 >nul & " + cmd], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=timeout or self.timeout)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        if check and p.returncode != 0:
            raise RemoteError("PowerShell 失败(%d)：%s\n%s" % (p.returncode, script[:400], err[-1500:]))
        return out

    def put(self, local: str, remote: str) -> int:
        """分块 base64 上传（单条 ssh 命令行有 ~8KB 上限，必须切块）。"""
        data = base64.b64encode(open(local, "rb").read()).decode("ascii")
        self.ps("[IO.File]::WriteAllText('%s','')" % remote)
        # 单条 ssh 命令行上限约 8KB；脚本经 UTF-16LE+base64 后体积×2.67，
        # 所以一次最多传 2000 个 base64 字符（≈1500 字节原文）
        step = 2000
        for i in range(0, len(data), step):
            chunk = data[i:i + step]
            self.ps("[IO.File]::AppendAllText('%s','%s')" % (remote, chunk))
        size = self.ps("$b=[Convert]::FromBase64String([IO.File]::ReadAllText('%s'));"
                       "[IO.File]::WriteAllBytes('%s',$b); (Get-Item '%s').Length"
                       % (remote, remote, remote))
        return int(size.strip() or 0)

    def get(self, remote: str, local: str, chunk: int = 60000) -> str:
        """下载（按块取 base64，避免 ssh 输出被截断）。"""
        n = int(self.ps("(Get-Item '%s').Length" % remote).strip())
        buf = []
        off = 0
        while off < n:
            buf.append(self.ps("$b=[IO.File]::ReadAllBytes('%s');$n=[Math]::Min(%d,$b.Length-%d);"
                               "[Convert]::ToBase64String($b,%d,$n)" % (remote, chunk, off, off)).strip())
            off += chunk
        open(local, "wb").write(base64.b64decode("".join(buf)))
        return local

    # ---------------- 常用查询
    def exists(self, path: str) -> bool:
        return self.ps("Test-Path '%s'" % path).strip().lower() == "true"

    def file_size(self, path: str) -> int:
        try:
            return int(self.ps("if (Test-Path '%s') {(Get-Item '%s').Length} else {0}"
                               % (path, path)).strip())
        except ValueError:
            return 0

    def find_plat_pids(self) -> List[int]:
        out = self.ps("(Get-Process Plat -ErrorAction SilentlyContinue).Id -join ','")
        return [int(x) for x in out.replace("\r", "").split(",") if x.strip().isdigit()]

    def listening(self, port: int) -> bool:
        out = self.ps("(Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue "
                      "| Measure-Object).Count" % port)
        return out.strip() not in ("", "0")

    # ---------------- 计划任务
    def register_task(self, name: str, cmdline: str, minutes: int = 720) -> None:
        """注册一个 Interactive + Highest 的计划任务（任务体是一条 cmd 命令行）。"""
        script = """
try { schtasks /delete /tn %(name)s /f *> $null } catch { }
$sid  = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$act  = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c %(cmd)s'
$prin = New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Highest
$set  = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes %(mins)d) `
          -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName %(name)s -Action $act -Principal $prin -Settings $set -Force | Out-Null
"registered"
""" % dict(name=name, cmd=cmdline, mins=minutes)
        self.ps(script)

    def start_task(self, name: str) -> None:
        self.ps("Start-ScheduledTask -TaskName %s; 'ok'" % name)

    def delete_task(self, name: str) -> None:
        self.ps("try { schtasks /delete /tn %s /f *> $null } catch { }; 'ok'" % name, check=False)

    def session_ok(self) -> bool:
        """确认存在一个 Active 的交互式控制台会话（Session 1 才能起引擎）。"""
        out = self.run("query session", check=False)
        return "console" in out and "Active" in out


# ---------------------------------------------------------------- 引擎管理
@dataclass
class EngineInfo:
    port: int = 21001
    dds_port: int = 22001
    room: str = "sce-builder"
    pid: Optional[int] = None
    ready: bool = False
    started_at: float = 0.0


class EngineManager(object):
    """在靶机上拉起/关闭一个无头引擎。"""

    def __init__(self, target: Optional[Target] = None, port: int = 21001,
                 dds_port: int = 22001, room: str = "sce-builder",
                 extra: Optional[dict] = None):
        self.t = target or Target()
        self.port = port
        self.dds_port = dds_port
        self.room = room
        self.task = "PiSceEngine%d" % port
        self.bat = "%s/Data/lyengine/pi_sce_engine_%d.bat" % (self.t.lingyi, port)
        self.log = "%s/Data/lyengine/pi_sce_engine_%d.log" % (self.t.lingyi, port)

    # -------------------------------------------------- 内部
    def _write_bat(self) -> None:
        room_guid = str(uuid.uuid4())
        content = (
            "@echo off\r\n"
            "cd /d %(ly)s\\Data\\lyengine\r\n"
            "Plat.exe %(guid)s 127.0.0.1 %(port)d %(dds)d 0 127.0.0.1 0 0 127.0.0.1 0 \"\" %(room)s "
            "> %(log)s 2>&1\r\n"
        ) % dict(ly=self.t.lingyi.replace("/", "\\"), guid=room_guid, port=self.port,
                 dds=self.dds_port, room=self.room, log=self.log.replace("/", "\\"))
        tmp = "/tmp/_sce_engine_%d.bat" % self.port
        open(tmp, "w", encoding="utf-8").write(content)
        self.t.put(tmp, self.bat)

    # -------------------------------------------------- 对外
    def status(self) -> EngineInfo:
        pids = self.t.find_plat_pids()
        ready = self.t.listening(self.port)
        return EngineInfo(self.port, self.dds_port, self.room,
                          pid=pids[0] if pids else None, ready=ready)

    def start(self, wait: float = 90.0, force: bool = False) -> EngineInfo:
        """启动引擎并等待 RPC 端口就绪。"""
        info = self.status()
        if info.ready and not force:
            return info
        if force and info.pid:
            self.stop()
        if not self.t.session_ok():
            raise RemoteError("靶机没有 Active 的控制台会话（Session 1）——"
                              "引擎是 Qt 程序，Session 0 起不来。请先登录控制台/RDP。")
        self._write_bat()
        self.t.register_task(self.task, self.bat.replace("/", "\\"))
        self.t.start_task(self.task)
        t0 = time.time()
        while time.time() - t0 < wait:
            if self.t.listening(self.port):
                info = self.status()
                info.ready = True
                info.started_at = t0
                return info
            time.sleep(2)
        tail = self.t.run("powershell -NoProfile -Command \"Get-Content '%s' -Tail 15\""
                          % self.log, check=False)
        raise RemoteError("引擎在 %.0f 秒内没有监听 %d 端口。日志尾部：\n%s" % (wait, self.port, tail))

    def stop(self) -> None:
        self.t.ps("Get-Process Plat -ErrorAction SilentlyContinue | Stop-Process -Force; 'ok'")
        self.t.delete_task(self.task)

    @staticmethod
    def stop_all(target: Target) -> None:
        """杀掉靶机上**所有** Plat.exe。

        实测：官方框架（Deduction）在被拉起/退出时会按进程名管理 Plat.exe，
        会顺手把我们在别的端口上起的建想定引擎一起清掉。所以「建想定」和
        「冒烟跑推演」这两件事要串行做（CLI 里已自动处理）。
        """
        target.ps("Get-Process Plat -ErrorAction SilentlyContinue | Stop-Process -Force; 'ok'")

    def tail_log(self, n: int = 20) -> str:
        return self.t.run("powershell -NoProfile -Command \"Get-Content '%s' -Tail %d\""
                          % (self.log, n), check=False)
