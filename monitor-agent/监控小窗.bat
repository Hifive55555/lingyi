@echo off
rem 监控小窗：双击开置顶小窗；客户端里导入 monitor\monitor_ai.py（类名 Agent）并启动
D:\LingYi\intelligent\new_env\ray210\python.exe -X utf8 "%~dp0launcher.py"
if errorlevel 1 pause
