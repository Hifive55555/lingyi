@echo off
rem ============================================================================
rem  Build the Windows installer (setup.exe) with Inno Setup 6.
rem
rem  How to use (on a Windows PC that has Inno Setup 6 installed):
rem    1) unzip the package (the zip produced by pack.sh / pack.py)
rem    2) double-click:  installer\build_installer.bat
rem    3) result:        <package>\dist\LingYiOverlay_setup_<ver>.exe
rem
rem  What it does:
rem    a) runs ..\pack.py --no-zip --name _pkg --out build
rem       (same file list that gets deployed; fails loudly if a key file is missing)
rem    b) finds ISCC.exe and compiles setup.iss
rem
rem  Notes:
rem    * No internet needed; pack.py only uses the Python standard library.
rem    * Written with labels instead of "( ... )" blocks on purpose: cmd chokes on
rem      "Program Files (x86)" inside for-lists and blocks ("... was unexpected").
rem ============================================================================
setlocal
set "HERE=%~dp0"
set "PKGROOT=%HERE%.."
set "ISCC="

echo [1/3] locating python ...
set "PY="
if exist "%PKGROOT%\..\..\intelligent\new_env\ray210\python.exe" set "PY=%PKGROOT%\..\..\intelligent\new_env\ray210\python.exe"
if not defined PY if exist "%PKGROOT%\..\intelligent\new_env\ray210\python.exe" set "PY=%PKGROOT%\..\intelligent\new_env\ray210\python.exe"
if not defined PY if exist "D:\LingYi\intelligent\new_env\ray210\python.exe" set "PY=D:\LingYi\intelligent\new_env\ray210\python.exe"
if not defined PY if exist "C:\LingYi\intelligent\new_env\ray210\python.exe" set "PY=C:\LingYi\intelligent\new_env\ray210\python.exe"
if not defined PY call :findpy py
if not defined PY call :findpy python
if not defined PY call :findpy python3
if not defined PY goto nopy
echo       python = %PY%

echo [2/3] staging payload ...
pushd "%PKGROOT%"
"%PY%" -X utf8 pack.py --no-zip --name _pkg --out build
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" goto badpack
if not exist "%PKGROOT%\build\_pkg\deploy.ps1" goto badpack

echo [3/3] locating Inno Setup compiler ...
call :tryiscc "C:\Program Files (x86)\Inno Setup 6"
call :tryiscc "C:\Program Files\Inno Setup 6"
call :tryiscc "D:\Program Files (x86)\Inno Setup 6"
call :tryiscc "D:\Program Files\Inno Setup 6"
call :tryiscc "E:\Program Files (x86)\Inno Setup 6"
call :tryiscc "C:\Program Files (x86)\Inno Setup 5"
call :tryiscc "%ProgramFiles(x86)%\Inno Setup 6"
call :tryregiscc
if not defined ISCC goto noiscc
echo       ISCC = %ISCC%

pushd "%HERE%"
"%ISCC%" /Qp setup.iss
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" goto badcompile

echo.
echo [OK] installer written to:
dir /b "%PKGROOT%\dist\*setup*.exe"
echo.
echo Next: copy that setup.exe to the competition PC and run it there
echo       as a NORMAL user - do NOT use "Run as administrator".
pause
exit /b 0

rem ------------------------------------------------------------------ helpers
:findpy
if defined PY exit /b 0
where %1 >nul 2>nul
if errorlevel 1 exit /b 0
set "PY=%1"
exit /b 0

:tryiscc
if defined ISCC exit /b 0
if exist "%~1\ISCC.exe" set "ISCC=%~1\ISCC.exe"
exit /b 0

:tryregiscc
if defined ISCC exit /b 0
for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" /v InstallLocation 2^>nul') do call :regline "%%B"
exit /b 0

:regline
if defined ISCC exit /b 0
if exist "%~1\ISCC.exe" set "ISCC=%~1\ISCC.exe"
exit /b 0

rem ------------------------------------------------------------------ errors
:nopy
echo [STOP] no python found.
echo        Install Python 3.8+ (or run this inside the rig's ray210 env).
pause
exit /b 1

:badpack
echo [STOP] pack.py failed (rc=%RC%). Fix the missing files it listed, then run again.
pause
exit /b 1

:noiscc
echo [STOP] ISCC.exe not found.
echo        Install Inno Setup 6, or open setup.iss in the Inno Setup GUI and press Ctrl+F9.
echo        Payload is already staged at: %PKGROOT%\build\_pkg
pause
exit /b 2

:badcompile
echo [STOP] Inno Setup compile failed (rc=%RC%). See the messages above.
pause
exit /b 1
