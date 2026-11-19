@echo off
setlocal
rem ============================================================================
rem 灵弈小窗（跟网页版指挥台是两个项目，代码/端口都不共用）
rem   双击本文件 -> 起 launcher.py（页面服务 127.0.0.1:8761）+ 一个置顶 Edge 窗口
rem   客户端里「智能体调度 -> 智能体编辑 -> +」选 agent\overlay_ai.py（类名 Agent）
rem
rem Python 用哪个：**直接用灵弈自带的 ray210**，不建 .venv。
rem   实测 ray210 = Python 3.9.19 自带 aiohttp 3.9.5 / psutil 6.0.0，
rem   launcher.py 只依赖 stdlib + aiohttp，因此不需要独立虚拟环境。
rem   （agent.py 跑在引擎进程里，本来也只能是 ray210，别无选择。）
rem
rem 灵弈不装在默认位置时，二选一：
rem   1) set LY_PYTHON=<你的 python.exe 全路径>   然后重开窗口
rem   2) 在本文件里再加一条  call :try "全路径"
rem ============================================================================
set "HERE=%~dp0"
set "PY="

rem ① 手动指定优先
if defined LY_PYTHON call :try "%LY_PYTHON%"

rem ② 灵弈自带环境（标准部署：<灵弈>\intelligent\ai\agent\overlay\ 时 ..\..\.. = <灵弈>\intelligent）
call :try "%HERE%..\..\..\new_env\ray210\python.exe"

rem ③ 常见安装根目录兜底（灵弈换了盘符/目录名时）
for %%R in ("D:\LingYi" "C:\LingYi" "E:\LingYi" "F:\LingYi") do call :try "%%~R\intelligent\new_env\ray210\python.exe"

rem ④ 系统 PATH 里的 python（自己装过 aiohttp 才能用）
for /f "delims=" %%i in ('where python 2^>nul') do call :try "%%i"
for /f "delims=" %%i in ('where python3 2^>nul') do call :try "%%i"

if not defined PY goto nopython
"%PY%" -X utf8 "%HERE%launcher.py"
if errorlevel 1 pause
exit /b 0

:nopython
echo(
echo 没找到带 aiohttp 的 Python。
echo 灵弈自带的那个应该是：
echo     ^<灵弈安装目录^>\intelligent\new_env\ray210\python.exe
echo 如果灵弈不在 D:\LingYi，任选其一：
echo   1^) 先  set LY_PYTHON=^<上面那个 python.exe 的全路径^>  再双击本文件
echo   2^) 在本文件里加一条  call :try "全路径"
echo   3^) 用  python tools\check_env.py  查环境（在 智能体代码\tools\ 下）
echo(
pause
exit /b 1

:try
if defined PY exit /b 0
if not exist %1 exit /b 0
%1 -c "import aiohttp" >nul 2>nul
if errorlevel 1 exit /b 0
set "PY=%~1"
exit /b 0
