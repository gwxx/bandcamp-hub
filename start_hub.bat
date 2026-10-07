@echo off
chcp 65001 >nul
title Bandcamp Hub Launcher

cd /d "%~dp0"

if not exist ".venv" (
    echo [INFO] 正在建立 Python 虛擬環境 (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] 無法建立虛擬環境，請確認系統已安裝 Python 3.10+。
        pause
        exit /b 1
    )
)

echo [INFO] 檢查並補齊相依套件...
call .\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
call .\.venv\Scripts\python.exe -m pip install --quiet -r requirements.txt

echo [INFO] 啟動 Bandcamp-Hub 本機伺服器...
call .\.venv\Scripts\python.exe run.py

if %errorlevel% neq 0 (
    echo [ERROR] 伺服器異常終止。
    pause
)
