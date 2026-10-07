import sqlite3
import shutil
from datetime import datetime
from app.config import DB_PATH, DATA_DIR, logger

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS releases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            cover_image_url TEXT,
            entity_type TEXT DEFAULT 'album',
            entity_id TEXT,
            stream_url TEXT,
            tracks_json TEXT,
            bpm REAL,
            key TEXT,
            iso_week TEXT NOT NULL,
            is_listened INTEGER DEFAULT 0,
            is_starred INTEGER DEFAULT 0,
            first_synced_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_watermark (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_successful_sync TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        conn.commit()

        cur = conn.cursor()
        cur.execute("PRAGMA table_info(releases);")
        columns = [row[1] for row in cur.fetchall()]
        required_cols = {
            "entity_type": "TEXT DEFAULT 'album'",
            "entity_id": "TEXT",
            "stream_url": "TEXT",
            "tracks_json": "TEXT",
            "bpm": "REAL",
            "key": "TEXT",
            "is_starred": "INTEGER DEFAULT 0"
        }
        for col, col_def in required_cols.items():
            if col not in columns:
                conn.execute(f"ALTER TABLE releases ADD COLUMN {col} {col_def};")
                logger.info(f"自動補齊資料庫欄位: {col}")
        conn.commit()
    logger.info("資料庫結構初始化與平滑檢查完成。")

def backup_and_reset_database() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = DATA_DIR / f"bandcamp_backup_{timestamp}.db"
    
    if DB_PATH.exists():
        with get_db_connection() as src_conn:
            with sqlite3.connect(backup_file) as dst_conn:
                src_conn.backup(dst_conn)
        logger.info(f"已建立資料庫自動備份快照：{backup_file.name}")
    
    with get_db_connection() as conn:
        conn.execute("DELETE FROM releases;")
        conn.execute("DELETE FROM sync_watermark;")
        conn.commit()
    
    logger.warning("資料庫已清空重設（保留 Gmail 驗證態）。")
    return backup_file.name
