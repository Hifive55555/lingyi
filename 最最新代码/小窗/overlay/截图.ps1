# -*- coding: utf-8 -*-
<#
    给「灵弈小窗 / 监控小窗」截图，存到 D:\LingYi\小窗截图\<日期_时间>\ 下。

    为什么单独写一个：这两个窗口是无边框置顶窗口，Alt+PrintScreen / 截图工具
    经常截到的是被它们盖住的客户端。这里按窗口标题枚举出真实窗口矩形，把窗口
    提到最前再按矩形裁一张，主小窗和监控小窗各一张，另外补一张全屏。

    用法：
      双击 截图.bat
      或  powershell -NoProfile -ExecutionPolicy Bypass -File 截图.ps1 [-Open]
    参数：
      -Out <目录>   换输出目录（默认 D:\LingYi\小窗截图）
      -Open        截完自动打开文件夹
#>
[CmdletBinding()]
param(
    [string]$Out = 'D:\LingYi\小窗截图',
    [switch]$Open
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class Win {
    public delegate bool EnumProc(IntPtr h, IntPtr p);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, ref int pid);
    public struct RECT { public int left, top, right, bottom; }
}
"@

function Find-Windows {
    $found = New-Object System.Collections.ArrayList
    $cb = [Win+EnumProc]{
        param($h, $p)
        if ([Win]::IsWindowVisible($h)) {
            $sb = New-Object System.Text.StringBuilder 512
            [void][Win]::GetWindowText($h, $sb, 512)
            $t = $sb.ToString()
            # 只认我们自家的窗口（进程名 overlay_wv2）；按标题匹配会把 Edge
            # 打开的同一个页面也截进来（页面标题就叫“灵弈小窗”）。
            $ok = $false
            try {
                $pid2 = 0
                [void][Win]::GetWindowThreadProcessId($h, [ref]$pid2)
                $pn = (Get-Process -Id $pid2 -ErrorAction SilentlyContinue).ProcessName
                if ($pn -eq 'overlay_wv2') { $ok = $true }
            } catch { }
            if (-not $ok -and ($t -like '灵弈小窗*' -or $t -like '监控小窗*')) { $ok = $true }
            if ($ok) {
                $r = New-Object Win+RECT
                [void][Win]::GetWindowRect($h, [ref]$r)
                if (($r.right - $r.left) -gt 100 -and ($r.bottom - $r.top) -gt 100) {
                    [void]$found.Add([pscustomobject]@{ hwnd = $h; title = $t; rect = $r })
                }
            }
        }
        return $true
    }
    [void][Win]::EnumWindows($cb, [IntPtr]::Zero)
    return $found
}

function Save-Rect($rect, $path) {
    $w = $rect.right - $rect.left
    $h = $rect.bottom - $rect.top
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($rect.left, $rect.top, 0, 0, $bmp.Size)
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    return (Get-Item $path).Length
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$dir = Join-Path $Out $stamp
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Write-Host "输出目录：$dir"

$wins = Find-Windows
if ($wins.Count -eq 0) {
    Write-Host '[WARN] 没找到小窗。先双击 灵弈小窗.bat，等两个窗口都出来了再截。'
}

foreach ($w in $wins) {
    # 置顶 + 提最前，不然截到的可能是盖在上面的客户端
    [void][Win]::ShowWindow($w.hwnd, 5)
    [void][Win]::SetWindowPos($w.hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0001 -bor 0x0002 -bor 0x0010)
    [void][Win]::SetForegroundWindow($w.hwnd)
    Start-Sleep -Milliseconds 350
    $r = New-Object Win+RECT
    [void][Win]::GetWindowRect($w.hwnd, [ref]$r)
    $name = if ($w.title -like '监控小窗*') { '监控小窗' } else { '主小窗' }
    $p = Join-Path $dir ("$name.png")
    $sz = Save-Rect $r $p
    Write-Host ("  {0}  {1}x{2}  {3:N0} KB  {4}" -f $name, ($r.right - $r.left), ($r.bottom - $r.top), ($sz / 1KB), $p)
}

# 再来一张全屏，方便看两个窗口和客户端的位置关系
$vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
$full = New-Object System.Drawing.Bitmap $vs.Width, $vs.Height
$g = [System.Drawing.Graphics]::FromImage($full)
$g.CopyFromScreen($vs.X, $vs.Y, 0, 0, $full.Size)
$fp = Join-Path $dir '全屏.png'
$full.Save($fp, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $full.Dispose()
Write-Host ("  全屏  {0:N0} KB  {1}" -f ((Get-Item $fp).Length / 1KB), $fp)

$last = Join-Path $Out '最新.txt'
$dir | Set-Content -Path $last -Encoding UTF8

if ($Open) { Start-Process explorer.exe $dir }
Write-Host '完成。'
