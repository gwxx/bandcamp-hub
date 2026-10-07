import os
import sys
import socket
import webbrowser
import threading
import time
import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
(BASE_DIR / "app" / "static").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "app" / "templates").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
(BASE_DIR / ".auth").mkdir(parents=True, exist_ok=True)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def find_available_port(start_port: int = 8000, max_attempts: int = 20) -> int:
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError(f"在 {start_port} 至 {start_port + max_attempts} 間找不到可用連接埠。")

def open_browser(port: int):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"\n🚀 Bandcamp-Hub 已啟動：{url}")
    webbrowser.open(url)

if __name__ == "__main__":
    port = find_available_port(8000)
    os.environ["APP_PORT"] = str(port)
    
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="info")
