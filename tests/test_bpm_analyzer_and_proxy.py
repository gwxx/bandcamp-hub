import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

class TestBpmAnalyzerAndProxy(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.db_path = self.data_dir / "test_bpm_proxy.db"
        self.patcher_db = patch("app.database.DB_PATH", self.db_path)
        self.patcher_api_db = patch("app.routers.api.DB_PATH", self.db_path)
        self.patcher_db.start()
        self.patcher_api_db.start()

        from app.database import init_db, get_db_connection
        init_db()
        with get_db_connection() as conn:
            tracks_json = json.dumps([
                {"track_num": 1, "title": "Track 1", "duration": 180.0, "stream_url": "https://stream.mock/t1.mp3"},
                {"track_num": 2, "title": "Track 2", "duration": 200.0, "stream_url": "https://stream.mock/t2.mp3"}
            ])
            conn.execute(
                """INSERT INTO releases (id, url, title, artist, iso_week, is_listened, is_starred, stream_url, tracks_json, bpm, first_synced_at, updated_at)
                   VALUES (1, 'https://test.bandcamp.com/album/1', 'Test Release', 'Test Artist', '2026-W38', 0, 0, 'https://stream.mock/rel.mp3', ?, NULL, '2026-09-20', '2026-09-20');""",
                (tracks_json,)
            )
            conn.execute(
                """INSERT INTO releases (id, url, title, artist, iso_week, is_listened, is_starred, stream_url, tracks_json, bpm, first_synced_at, updated_at)
                   VALUES (2, 'https://test.bandcamp.com/album/2', 'Empty Release', 'Test Artist 2', '2026-W38', 0, 0, '', '[]', NULL, '2026-09-20', '2026-09-20');"""
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

    def test_stream_proxy_not_found(self):
        resp = self.client.get("/api/releases/999/stream-proxy")
        self.assertEqual(resp.status_code, 404)

    def test_stream_proxy_no_stream(self):
        resp = self.client.get("/api/releases/2/stream-proxy")
        self.assertEqual(resp.status_code, 404)

    @patch("httpx.AsyncClient")
    def test_stream_proxy_success(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        async def fake_chunks(chunk_size=65536):
            yield b"MOCK_MP3_DATA_CHUNK_1"
            yield b"MOCK_MP3_DATA_CHUNK_2"
        mock_response.aiter_bytes = fake_chunks

        mock_client = MagicMock()
        class AsyncContext:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        mock_client.stream.return_value = AsyncContext()

        class ClientContext:
            async def __aenter__(self):
                return mock_client
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        mock_client_cls.return_value = ClientContext()

        resp = self.client.get("/api/releases/1/stream-proxy?track_index=0")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"MOCK_MP3_DATA_CHUNK_1", resp.content)
        self.assertEqual(resp.headers.get("content-type"), "audio/mpeg")
        self.assertEqual(resp.headers.get("access-control-allow-origin"), "*")

    def test_staged_bpm_update_and_nudge(self):
        # 測試儲存經由 -2/+2 調整後的 BPM
        resp = self.client.patch("/api/releases/1/bpm", json={"bpm": 126.5})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["bpm"], 126.5)

        from app.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute("SELECT bpm FROM releases WHERE id = 1;").fetchone()
            self.assertEqual(row["bpm"], 126.5)

    def test_patch_release_bpm_validation_boundaries(self):
        """Ticket 03: Verify boundary inputs for PATCH /api/releases/{release_id}/bpm (39.9, 40.0, 300.0, 300.1)."""
        # Rejections below 40.0
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 39.9}).status_code, 400)
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 0.0}).status_code, 400)
        # Rejections above 300.0
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 300.1}).status_code, 400)
        # Accept valid boundary values
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 40.0}).status_code, 200)
        self.assertEqual(self.client.patch("/api/releases/1/bpm", json={"bpm": 300.0}).status_code, 200)

if __name__ == "__main__":
    unittest.main()
