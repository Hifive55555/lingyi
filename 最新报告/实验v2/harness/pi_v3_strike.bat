@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set PI_SAM_INITIAL=strike
cd /d D:\LingYi\intelligent\ai
D:\LingYi\intelligent\new_env\ray210\python.exe -u pi_v2_drive.py D:\LingYi\exp\plan_v3_strike.json > D:\LingYi\exp\v2\drive_v3b.log 2>&1
