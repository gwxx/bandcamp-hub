import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
AUTH_DIR = BASE_DIR / ".auth"
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

DATA_DIR.mkdir(parents=True, exist_ok=True)
AUTH_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "bandcamp.db"
LOG_PATH = DATA_DIR / "app.log"
CREDENTIALS_PATH = AUTH_DIR / "credentials.json"
TOKEN_PATH = AUTH_DIR / "token.json"

logger = logging.getLogger("bandcamp_hub")
logger.setLevel(logging.INFO)

if not logger.handlers:
    rf_handler = RotatingFileHandler(LOG_PATH, maxBytes=1024 * 1024, backupCount=1, encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    rf_handler.setFormatter(formatter)
    logger.addHandler(rf_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
