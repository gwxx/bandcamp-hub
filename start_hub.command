#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "[INFO] 正在建立 Python 虛擬環境 (.venv)..."
    python3 -m venv .venv || { echo "[ERROR] 建立虛擬環境失敗"; exit 1; }
fi

echo "[INFO] 檢查並補齊相依套件..."
./.venv/bin/pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet -r requirements.txt

echo "[INFO] 啟動 Bandcamp-Hub 本機伺服器..."
./.venv/bin/python run.py
