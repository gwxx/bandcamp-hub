import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

class TestCurationStateMachine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.db_path = self.data_dir / "test_state.db"
        self.patcher_db = patch("app.database.DB_PATH", self.db_path)
        self.patcher_api_db = patch("app.routers.api.DB_PATH", self.db_path)
        self.patcher_db.start()
        self.patcher_api_db.start()

        from app.database import init_db, get_db_connection
        init_db()
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO releases (id, url, title, artist, iso_week, is_listened, is_starred, first_synced_at, updated_at)
                   VALUES (1, 'https://test.bandcamp.com/album/1', 'Test 1', 'Artist 1', '2026-W36', 0, 0, '2026-09-03', '2026-09-03'),
                          (2, 'https://test.bandcamp.com/album/2', 'Test 2', 'Artist 2', '2026-W36', 0, 0, '2026-09-03', '2026-09-03');"""
            )
            conn.commit()

        from app.main import app
        self.client = TestClient(app)

    def tearDown(self):
        self.patcher_api_db.stop()
        self.patcher_db.stop()
        self.temp_dir.cleanup()

    def test_starring_implicitly_promotes_to_listened(self):
        # Initial: is_starred=0, is_listened=0
        resp = self.client.patch("/api/releases/1/star")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["is_starred"], 1)
        self.assertEqual(data["is_listened"], 1)

        # Database verification
        from app.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute("SELECT is_starred, is_listened FROM releases WHERE id = 1;").fetchone()
            self.assertEqual(row["is_starred"], 1)
            self.assertEqual(row["is_listened"], 1)

    def test_unstarring_retains_listened(self):
        # Promote to starred & listened first
        self.client.patch("/api/releases/1/star")

        # Now unstar
        resp = self.client.patch("/api/releases/1/star")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["is_starred"], 0)
        self.assertEqual(data["is_listened"], 1)  # Retained!

        # Database verification
        from app.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute("SELECT is_starred, is_listened FROM releases WHERE id = 1;").fetchone()
            self.assertEqual(row["is_starred"], 0)
            self.assertEqual(row["is_listened"], 1)

    def test_unlistening_retains_starred(self):
        # Promote to starred & listened first
        self.client.patch("/api/releases/1/star")

        # Now toggle listened (1 -> 0)
        resp = self.client.patch("/api/releases/1/listened")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["is_listened"], 0)
        self.assertEqual(data["is_starred"], 1)  # Star retained!

        # Database verification
        from app.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute("SELECT is_starred, is_listened FROM releases WHERE id = 1;").fetchone()
            self.assertEqual(row["is_listened"], 0)
            self.assertEqual(row["is_starred"], 1)

    def test_bulk_listened_endpoint(self):
        resp = self.client.post("/api/releases/bulk-listened", json={"release_ids": [1, 2]})
        self.assertEqual(resp.status_code, 200)

        from app.database import get_db_connection
        with get_db_connection() as conn:
            rows = conn.execute("SELECT is_listened FROM releases WHERE id IN (1, 2);").fetchall()
            for r in rows:
                self.assertEqual(r["is_listened"], 1)

if __name__ == "__main__":
    unittest.main()
