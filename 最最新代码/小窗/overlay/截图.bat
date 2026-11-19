@echo off
rem ============================================================================
rem  给小窗截图：主小窗、监控小窗各一张 + 一张全屏
rem  存到 D:\LingYi\小窗截图\<日期_时间>\，并在资源管理器里打开
rem  （双击即可；找不到窗口会提示先开小窗）
rem ============================================================================
setlocal
set "HERE=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%HERE%截图.ps1" -Open
if errorlevel 1 pause
exit /b 0
