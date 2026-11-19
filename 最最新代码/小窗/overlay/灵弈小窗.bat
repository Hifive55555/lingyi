@echo off
setlocal
rem LingYi overlay (different from the web console project).
rem Double-click to open the always-on-top overlay; in the client import agent/overlay_ai.py (class Agent).
rem launcher.py needs Python 3.8+ with aiohttp. If your python.exe lives elsewhere,
rem add its full path as another "call :try" line below.
set "HERE=%~dp0"
set "PY="
call :try "%HERE%.venv\Scripts\python.exe"
call :try "%HERE%..\..\..\.venv\Scripts\python.exe"
call :try "D:\Programs\anacondaanzhuang\envs\pytorch3.8\python.exe"
call :try "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
for /f "delims=" %%i in ('where python 2^>nul') do call :try "%%i"
for /f "delims=" %%i in ('where python3 2^>nul') do call :try "%%i"
if not defined PY goto nopython
"%PY%" -X utf8 "%HERE%launcher.py"
if errorlevel 1 pause
exit /b 0

:nopython
echo(
echo No Python with aiohttp found (need 3.8 or newer). Two ways to fix:
echo   1^) install it for your Python:  python -m pip install aiohttp
echo   2^) add your python.exe full path as another "call :try" line in this .bat
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
