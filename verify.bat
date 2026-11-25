@echo off
rem 一键回归（Windows）：需要 PATH 里有 python，且装了 openpyxl
setlocal
cd /d "%~dp0"
python verify.py %*
