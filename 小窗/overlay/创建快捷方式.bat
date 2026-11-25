@echo off
rem 生成/修复当前电脑上的「灵弈小窗」「小窗截图」快捷方式（换安装目录后重跑一次即可）
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0创建快捷方式.ps1" %*
if errorlevel 1 pause
if /i not "%~1"=="-Quiet" pause
