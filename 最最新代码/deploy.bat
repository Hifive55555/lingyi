@echo off
setlocal
rem ============================================================================
rem One-click deploy: installs this folder's agents + overlay into LingYi.
rem   double-click -> powershell -ExecutionPolicy Bypass -File deploy.ps1
rem   dry run     -> deploy.bat -DryRun
rem   other root  -> deploy.bat -Lingyi "E:\LingYi"
rem No venv, no pip, no network: uses LingYi's bundled ray210 python only.
rem ============================================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy.ps1" %*
if errorlevel 1 (
    echo.
    echo [STOP] deploy failed, see messages above.
    pause
)
endlocal
