@echo off
rem ============================================================================
rem  pack: build a zip of the latest agents + overlay, ready to copy to the rig
rem    double-click        -> dist\LingYiOverlay_<timestamp>.zip
rem    pack.bat --with-entitys   also include the platform libs
rem    pack.bat --no-zip         folder only (handy for robocopy)
rem  Python: prefers LingYi's bundled ray210, falls back to py/python on PATH.
rem ============================================================================
setlocal
set "HERE=%~dp0"
set "PY="
if exist "%HERE%..\intelligent\new_env\ray210\python.exe" set "PY=%HERE%..\intelligent\new_env\ray210\python.exe"
if defined PY goto run
for %%C in (py python) do (
    if not defined PY (
        where %%C >nul 2>nul && set "PY=%%C"
    )
)
:run
if not defined PY goto nopy
"%PY%" -X utf8 "%HERE%pack.py" %*
if errorlevel 1 pause
exit /b 0
:nopy
echo [STOP] no python found. Run pack.py with any Python 3.8+ (pack.sh works on Linux).
pause
exit /b 1