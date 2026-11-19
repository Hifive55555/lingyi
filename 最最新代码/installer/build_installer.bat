@echo off
rem ============================================================================
rem  Build the Windows installer (setup.exe) with Inno Setup.
rem
rem  How to use (on the Windows PC that has Inno Setup 6):
rem    1) unzip the package (the zip produced by pack.sh / pack.py)
rem    2) double-click this file:  installer\build_installer.bat
rem    3) result:  <package>\dist\LingYiOverlay_setup_<ver>.exe  (Chinese name inside)
rem
rem  What it does:
rem    a) runs ..\pack.py --no-zip --name _pkg --out ..\build
rem       -> stages exactly the same file list that gets deployed
rem    b) finds ISCC.exe (Inno Setup compiler) and compiles setup.iss
rem
rem  Notes:
rem    * No internet needed; pack.py only uses the Python standard library.
rem    * If Inno Setup is not installed, download it once on any PC; the .iss
rem      can also be compiled later with the Inno Setup GUI ("Compile").
rem ============================================================================
setlocal enabledelayedexpansion
set "HERE=%~dp0"
set "PKGROOT=%HERE%.."
set "ISCC="

echo [1/3] locating python ...
set "PY="
if exist "%PKGROOT%\..\intelligent\new_env\ray210\python.exe" set "PY=%PKGROOT%\..\intelligent\new_env\ray210\python.exe"
if not defined PY if exist "%PKGROOT%\..\..\intelligent\new_env\ray210\python.exe" set "PY=%PKGROOT%\..\..\intelligent\new_env\ray210\python.exe"
if not defined PY for %%C in (py python python3) do (
    if not defined PY (
        where %%C >nul 2>nul && set "PY=%%C"
    )
)
if not defined PY (
    echo [STOP] no python found. Install Python 3.8+ or run pack.py inside the rig's ray210.
    pause & exit /b 1
)
echo       python = %PY%

echo [2/3] staging payload ...
pushd "%PKGROOT%"
"%PY%" -X utf8 pack.py --no-zip --name _pkg --out build
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" (
    echo [STOP] pack.py failed ^(rc=%RC%^). Fix the missing files it listed, then run again.
    pause & exit /b 1
)
if not exist "%PKGROOT%\build\_pkg\deploy.ps1" (
    echo [STOP] staging dir has no deploy.ps1: %PKGROOT%\build\_pkg
    pause & exit /b 1
)

echo [3/3] locating Inno Setup compiler ...
for %%P in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    "C:\Program Files\Inno Setup 5\ISCC.exe"
) do (
    if not defined ISCC if exist %%P set "ISCC=%%~P"
)
if not defined ISCC (
    for /f "delims=" %%K in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" /v InstallLocation 2^>nul ^| find "InstallLocation"') do (
        for /f "tokens=2,*" %%A in ("%%K") do if exist "%%B\ISCC.exe" set "ISCC=%%B\ISCC.exe"
    )
)
if not defined ISCC (
    echo [STOP] ISCC.exe not found. Install Inno Setup 6, or open setup.iss in the
    echo        Inno Setup GUI and press Compile (Ctrl+F9).
    echo        Payload is already staged at: %PKGROOT%\build\_pkg
    pause & exit /b 2
)
echo       ISCC = %ISCC%

pushd "%HERE%"
"%ISCC%" /Qp setup.iss
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" (
    echo [STOP] Inno Setup compile failed ^(rc=%RC%^). See the messages above.
    pause & exit /b %RC%
)

echo.
echo [OK] installer written to:
dir /b "%PKGROOT%\dist\*setup*.exe"
echo.
echo Next: copy that setup.exe to the competition PC and run it there
echo       (it must run as a NORMAL user - NOT "Run as administrator").
pause
exit /b 0
