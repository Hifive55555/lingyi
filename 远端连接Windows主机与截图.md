# 远端 Windows 靶机：登录与截图方法

> 记录时间：2026-11-17 · 环境：本机 NixOS（zsh） → 远端 Windows 11

## 1. 目标机信息

| 项 | 值 |
| --- | --- |
| 地址 | `10.42.97.205:22` |
| 用户名 | `Hifive` |
| 密码 | `hifive` |
| 主机名 | `HIFIVE-ASUS` |
| 系统 | Windows 11（`Microsoft Windows [版本 10.0.22631.4751]`） |
| 登录名 | `HIFIVE-ASUS\Hifive`，SID `S-1-5-21-1746777246-2050036752-2573328351-1001` |
| 权限 | 管理员（High Mandatory Level） |
| 默认 shell | `cmd.exe`（Win32-OpenSSH） |
| 显示 | 单屏 2560×1440，控制台会话为 **Session 1** |

## 2. 登录方法

### 2.1 为什么不能直接用 `sshpass`

本机（NixOS）没有 `sshpass`，而 nixpkgs 镜像返回 404 装不上：

```
nix build nixpkgs#sshpass   # → tuna 镜像 404 Not Found
```

改用 OpenSSH 自带的 askpass 机制，**无需任何额外依赖**。

### 2.2 密码应答脚本

`~/.cache/pi-ssh/askpass.sh`（权限 700）：

```sh
#!/bin/sh
echo "hifive"
```

### 2.3 一键登录封装

`~/.cache/pi-ssh/ssh-hifive`（权限 700）：

```sh
#!/bin/sh
SSH_ASKPASS=/home/hifive/.cache/pi-ssh/askpass.sh SSH_ASKPASS_REQUIRE=force DISPLAY=:0 \
setsid -w ssh -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  Hifive@10.42.97.205 "$@"
```

用法：

```sh
~/.cache/pi-ssh/ssh-hifive 'hostname'                 # Hifive-ASUS
~/.cache/pi-ssh/ssh-hifive 'chcp 65001 >nul & dir'    # 正确显示中文
```

关键点：

- `SSH_ASKPASS_REQUIRE=force` —— 强制走 askpass，即使有 tty 也不用交互输入；
- `setsid -w` —— 脱离控制终端，否则 ssh 会直接读 /dev/tty 而绕过 askpass；
- `DISPLAY=:0` —— 部分 OpenSSH 版本要求非空 DISPLAY 才启用 askpass（此处无实际图形用途）；
- `PreferredAuthentications=password` + `PubkeyAuthentication=no` —— 避免先试公钥再回落到密码。

### 2.4 中文乱码

远端 `cmd.exe` 默认 GBK 代码页，SSH 通道输出会是乱码。**所有命令前加 `chcp 65001 >nul &`**：

```sh
ssh-hifive 'chcp 65001 >nul & query session'
```

## 3. 截图方法（核心）

### 3.1 踩到的坑：Session 0 隔离

Win32-OpenSSH 的 `sshd` 以服务身份运行在 **Session 0**，而用户桌面在 **Session 1**。
在 SSH 会话里直接 `System.Drawing.CopyFromScreen`：

- 要么抛异常，要么得到全黑图；
- 因为 Session 0 没有可见桌面（`winsta0` 是隔离的）。

验证方式：

```sh
ssh-hifive 'chcp 65001 >nul & query session'
#  >services                 0  断开
#   console      Hifive       1  运行中     ← 真正的桌面在这里
```

### 3.2 解法：计划任务投递到 Session 1

用 `LogonType Interactive` 的计划任务，任务会在用户已登录的交互会话（Session 1）中执行。

**必须用 SID 而不是 `域名\用户名`**，否则报错：
`No mapping between account names and security IDs was done.`

#### 步骤 1：上传截图脚本 `C:\Windows\Temp\pi-shot.ps1`

```powershell
$log = "C:\Windows\Temp\pi-shot.log"
function L($m){ Add-Content -Path $log -Value ("[" + (Get-Date -Format "HH:mm:ss") + "] " + $m) -Encoding UTF8 }
Set-Content -Path $log -Value "start" -Encoding UTF8
L ("SessionId=" + (Get-Process -Id $PID).SessionId)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen   # 多屏时取整块虚拟屏
L ("VirtualScreen=" + $b.Width + "x" + $b.Height + " @" + $b.X + "," + $b.Y)

$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.X, $b.Y, 0, 0, $bmp.Size)
$out = "C:\Windows\Temp\pi-shot.png"
if (Test-Path $out) { Remove-Item $out -Force }
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
L ("SAVED=" + $out + " bytes=" + (Get-Item $out).Length)
```

#### 步骤 2：注册并启动计划任务

```powershell
$act  = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument '-NoProfile -ExecutionPolicy Bypass -File C:\Windows\Temp\pi-shot.ps1'
$sid  = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$prin = New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName 'PiShot' -Action $act -Principal $prin -Force
Start-ScheduledTask     -TaskName 'PiShot'
Start-Sleep -Seconds 5
Get-ScheduledTaskInfo   -TaskName 'PiShot' | Select-Object LastTaskResult, LastRunTime
```

预期日志（`C:\Windows\Temp\pi-shot.log`）：

```
[09:11:08] SessionId=1                       ← 关键：不是 0
[09:11:08] VirtualScreen=2560x1440 @0,0
[09:11:08] SAVED=C:\Windows\Temp\pi-shot.png bytes=5093758
```

#### 步骤 3：取回图片

无 `scp` 交互麻烦，直接 base64 走 stdout：

```sh
ssh-hifive "powershell -NoProfile -Command \"[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\\Windows\\Temp\\pi-shot.png'))\"" \
  2>/dev/null | tr -d '\r\n' > /tmp/shot.b64
base64 -d /tmp/shot.b64 > /tmp/shot.png
```

#### 步骤 4：清理

```sh
ssh-hifive 'chcp 65001 >nul & schtasks /delete /tn PiShot /f'
ssh-hifive 'chcp 65001 >nul & del C:\Windows\Temp\pi-shot.png C:\Windows\Temp\pi-shot.ps1 C:\Windows\Temp\pi-shot.log'
```

### 3.3 备选方案（未验证，留作参考）

- **`CreateProcessAsUser`**：管理员权限下用 `WTSQueryUserToken(1)` + `DuplicateTokenEx` + `CreateProcessAsUser` 指定 `winsta0\default`，可省掉计划任务，但要写 C# P/Invoke。
- **`PsExec -i 1`**：Sysinternals 工具，需额外下载。
- **在 Session 1 里常驻一个代理**（如 VNC / 自建 WebSocket 服务），SSH 只做控制通道。

## 4. 远端文件传输小工具

上传任意本地 PowerShell 脚本（避免引号地狱）：

```sh
B64=$(base64 -w0 local.ps1)
ssh-hifive "powershell -NoProfile -Command \"[IO.File]::WriteAllBytes('C:\\Windows\\Temp\\x.ps1',[Convert]::FromBase64String('$B64'))\""
ssh-hifive 'chcp 65001 >nul & powershell -NoProfile -ExecutionPolicy Bypass -File C:\Windows\Temp\x.ps1'
```

注意：`powershell -Command -`（从 stdin 读脚本）在该环境会**截断且无报错**，不要用，一律落盘再 `-File` 执行。

## 5. 安全提示

⚠️ 密码 `hifive` 以明文形式存放在 `askpass.sh` 中。仅适用于内网实验环境。正式使用建议：

```sh
# 1. 生成密钥
ssh-keygen -t ed25519 -C pi@nixos
# 2. 用现有密码通道推送公钥（Windows 侧 authorized_keys 位于
#    C:\ProgramData\ssh\administrators_authorized_keys，且需 icacls 收紧权限）
# 3. 之后去掉 PreferredAuthentications=password，并把 askpass 脚本删除
```

Windows 管理员组用户走的是 `administrators_authorized_keys` 而不是 `~/.ssh/authorized_keys`，这是最容易卡住的一步：

```powershell
$f = "$env:ProgramData\ssh\administrators_authorized_keys"
Add-Content -Path $f -Value "ssh-ed25519 AAAA... pi@nixos"
icacls $f /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
```
