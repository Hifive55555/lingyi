# -*- coding: utf-8 -*-
<#
  在当前这台机器上创建「灵弈小窗」「小窗截图」桌面/开始菜单快捷方式。

  为什么不随包发 .lnk：
    .lnk 里存的是**绝对路径**（TargetPath=D:\LingYi\...\灵弈小窗.bat）。
    比赛机/别人电脑的灵弈装到别的盘或别的目录，这个 .lnk 就废了。
    所以改成“装完就地生成”：本脚本按**自己所在目录**推出绝对路径再写快捷方式，
    灵弈根目录换到哪都能用。

  用法（在 overlay 目录里）：
    powershell -NoProfile -ExecutionPolicy Bypass -File 创建快捷方式.ps1
    powershell ... -File 创建快捷方式.ps1 -Remove      # 删掉这两个快捷方式
    powershell ... -File 创建快捷方式.ps1 -NoStartMenu # 只建桌面
#>
param(
    [switch]$Remove,
    [switch]$NoStartMenu,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$sh = New-Object -ComObject WScript.Shell

function Say($s) { if (-not $Quiet) { Write-Host $s } }

# 目标：桌面（兼容 OneDrive 重定向桌面）+ 开始菜单
# [Environment]::GetFolderPath('Desktop') 会自动解析 OneDrive 重定向（本机就是
# C:\Users\A\OneDrive\桌面），所以只认这一个，别再往 %USERPROFILE%\Desktop 多加一份。
$desktops = @([Environment]::GetFolderPath('Desktop')) | Where-Object { $_ -and (Test-Path $_) }

$startDir = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
$targets = @()

$items = @(
    @{ Name = '灵弈小窗';   Bat = '灵弈小窗.bat' },
    @{ Name = '小窗截图';   Bat = '截图.bat' }
)

foreach ($it in $items) {
    $bat = Join-Path $here $it.Bat
    if (-not (Test-Path $bat)) { Say ("[WARN] 缺 " + $bat + "，跳过 " + $it.Name); continue }
    foreach ($dir in $desktops) {
        $targets += @{ Lnk = (Join-Path $dir ($it.Name + '.lnk')); Bat = $bat; Name = $it.Name }
    }
    if (-not $NoStartMenu -and (Test-Path $startDir)) {
        $targets += @{ Lnk = (Join-Path $startDir ($it.Name + '.lnk')); Bat = $bat; Name = $it.Name }
    }
}

foreach ($t in $targets) {
    if ($Remove) {
        if (Test-Path $t.Lnk) { Remove-Item $t.Lnk -Force; Say ("[删] " + $t.Lnk) }
        continue
    }
    $dir = Split-Path -Parent $t.Lnk
    if (-not (Test-Path $dir)) { continue }
    $lnk = $sh.CreateShortcut($t.Lnk)
    $lnk.TargetPath       = $t.Bat
    $lnk.WorkingDirectory = $here
    $lnk.Description      = '灵弈小窗（页面 127.0.0.1:8761）'
    $lnk.WindowStyle      = 7          # 最小化：别让黑色控制台挡着
    # 图标用 WebView2 宿主 exe（存在就用，没有就让系统给默认图标）
    $ico = Join-Path $here 'wv2\overlay_wv2.exe'
    if (Test-Path $ico) { $lnk.IconLocation = $ico + ',0' }
    $lnk.Save()
    Say ("[建] " + $t.Lnk + "  ->  " + $t.Bat)
}

if (-not $Remove) {
    Say ''
    Say '完成。桌面上的「灵弈小窗」现在指向本机真实路径：'
    Say ('    ' + (Join-Path $here '灵弈小窗.bat'))
    Say '（换电脑/换安装目录后，重跑一次这个脚本即可，不用改任何文件）'
}
