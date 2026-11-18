@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set PI_SHIP_LAYERED=0
cd /d D:\LingYi\intelligent\ai
D:\LingYi\intelligent\new_env\ray210\python.exe -u pi_v2_drive.py D:\LingYi\exp\plan_ship_nolayered.json > D:\LingYi\exp\v2\drive_ship0.log 2>&1
