import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.db_path = self.data_dir / "test_bandcamp.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_db_connection_enables_wal_mode(self):
        with patch("app.database.DB_PATH", self.db_path):
            from app.database import get_db_connection
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
                self.assertEqual(mode.lower(), "wal")
            finally:
                conn.close()

    def test_backup_and_reset_uses_native_backup(self):
        with patch("app.database.DB_PATH", self.db_path), patch("app.database.DATA_DIR", self.data_dir):
            from app.database import init_db, get_db_connection, backup_and_reset_database
            init_db()
            with get_db_connection() as conn:
                conn.execute(
                    """INSERT INTO releases (url, title, artist, iso_week, first_synced_at, updated_at)
                       VALUES ('https://test.bandcamp.com/album/test', 'Test Title', 'Test Artist', '2026-W36', '2026-09-03', '2026-09-03');"""
                )
                conn.commit()

            backup_name = backup_and_reset_database()
            backup_file = self.data_dir / backup_name
            self.assertTrue(backup_file.exists())

            # Verify backup has the data
            with sqlite3.connect(backup_file) as b_conn:
                count = b_conn.execute("SELECT COUNT(*) FROM releases;").fetchone()[0]
                self.assertEqual(count, 1)

            # Verify main DB was reset
            with get_db_connection() as conn:
                count = conn.execute("SELECT COUNT(*) FROM releases;").fetchone()[0]
                self.assertEqual(count, 0)

if __name__ == "__main__":
    unittest.main()
