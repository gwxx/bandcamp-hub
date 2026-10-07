import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

class TestAudioResilienceAndBpm(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.db_path = self.data_dir / "test_audio.db"
        self.patcher_db = patch("app.database.DB_PATH", self.db_path)
        self.patcher_api_db = patch("app.routers.api.DB_PATH", self.db_path)
        self.patcher_db.start()
        self.patcher_api_db.start()

        from app.database import init_db, get_db_connection
        init_db()
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO releases (id, url, title, artist, iso_week, is_listened, is_starred, stream_url, tracks_json, bpm, first_synced_at, updated_at)
                   VALUES (1, 'https://test.bandcamp.com/album/1', 'Test Release', 'Test Artist', '2026-W38', 0, 0, 'https://old.expired.stream/token', '[]', NULL, '2026-09-20', '2026-09-20');"""
            )
            conn.commit()

        from app.main import app
        self.client = TestClient(app)

    def tearDown(self):
        self.patcher_api_db.stop()
        self.patcher_db.stop()
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_patch_release_bpm_success(self):
        resp = self.client.patch("/api/releases/1/bpm", json={"bpm": 124.0})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["bpm"], 124.0)

        from app.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute("SELECT bpm FROM releases WHERE id = 1;").fetchone()
            self.assertEqual(row["bpm"], 124.0)

    def test_patch_release_bpm_not_found(self):
        resp = self.client.patch("/api/releases/999/bpm", json={"bpm": 128.0})
        self.assertEqual(resp.status_code, 404)

    def test_patch_release_bpm_validation(self):
        # Sub-40.0 values must be rejected
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": -5.0}).status_code, 400)
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 39.9}).status_code, 400)
        # Over-300.0 values must be rejected
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 300.1}).status_code, 400)
        # Valid boundaries 40.0 and 300.0 must be accepted
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 40.0}).status_code, 200)
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 300.0}).status_code, 200)

    @patch("app.routers.api.scrape_bandcamp_metadata", new_callable=AsyncMock)
    def test_refresh_stream_success(self, mock_scrape):
        mock_scrape.return_value = {
            "url": "https://test.bandcamp.com/album/1",
            "title": "Test Release Fresh",
            "artist": "Test Artist",
            "cover_image_url": "https://f4.bcbits.com/img/fresh.jpg",
            "entity_type": "album",
            "entity_id": "12345",
            "stream_url": "https://t4.bcbits.com/stream/fresh_token_123",
            "tracks_json": '[{"track_num": 1, "title": "Fresh Track 1", "duration": 210, "stream_url": "https://t4.bcbits.com/stream/fresh_token_123"}]'
        }

        resp = self.client.post("/api/releases/1/refresh-stream")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["stream_url"], "https://t4.bcbits.com/stream/fresh_token_123")
        self.assertEqual(len(data["tracks"]), 1)
        self.assertEqual(data["tracks"][0]["title"], "Fresh Track 1")

        from app.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute("SELECT stream_url, tracks_json FROM releases WHERE id = 1;").fetchone()
            self.assertEqual(row["stream_url"], "https://t4.bcbits.com/stream/fresh_token_123")
            self.assertIn("Fresh Track 1", row["tracks_json"])

    def test_refresh_stream_not_found(self):
        resp = self.client.post("/api/releases/999/refresh-stream")
        self.assertEqual(resp.status_code, 404)

if __name__ == "__main__":
    unittest.main()
