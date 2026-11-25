@echo off
setlocal
rem ============================================================================
rem LingYi overlay launcher (this is NOT the web console project)
rem   double-click -> starts launcher.py (page server 127.0.0.1:8761) + a pinned Edge window
rem   in the client: Agent Scheduling -> Agent Editor -> "+" -> pick agent\overlay_ai.py (class Agent)
rem
rem Python: ONLY the one bundled with LingYi (ray210, Python 3.9.19 + aiohttp 3.9.5).
rem   No .venv, no pip install -- the competition machine has no internet.
rem   agent.py runs inside the engine process anyway, so ray210 is the only choice.
rem
rem Non-standard install path: set LY_PYTHON=<full path to python.exe> then double-click.
rem If nothing is found we stop and ask for a report; we never try to install anything.
rem ============================================================================
set "HERE=%~dp0"
set "PY="

rem (1) explicit override
if defined LY_PYTHON call :try "%LY_PYTHON%"

rem (2) standard layout: <LingYi>\intelligent\ai\agent\overlay\  =>  ..\..\.. = <LingYi>\intelligent
call :try "%HERE%..\..\..\new_env\ray210\python.exe"

rem (3) common install roots
for %%R in ("D:\LingYi" "C:\LingYi" "E:\LingYi" "F:\LingYi") do call :try "%%~R\intelligent\new_env\ray210\python.exe"

if not defined PY goto noenv
"%PY%" -X utf8 "%HERE%launcher.py"
if errorlevel 1 pause
exit /b 0

:noenv
echo(
echo [STOP] no bundled LingYi Python found (needs: import aiohttp)
echo        expected: ^<LingYi^>\intelligent\new_env\ray210\python.exe
echo        This tool does NOT create a venv and does NOT install packages.
echo        Please report these two things to whoever deploys this:
echo          1^) the LingYi install dir (the one containing APlatformLobby.exe)
echo          2^) what is inside ^<LingYi^>\intelligent\new_env
echo        Temporary override: set LY_PYTHON=^<full path to python.exe^>
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
