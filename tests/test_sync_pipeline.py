import unittest
import base64
from datetime import datetime, timezone
from unittest.mock import MagicMock
from app.services.sync_pipeline import fetch_messages_paginated, extract_email_html, compute_iso_week_utc

class TestSyncPipeline(unittest.TestCase):
    def test_fetch_messages_paginated_multiple_pages(self):
        service = MagicMock()
        mock_list = service.users().messages().list

        # Mock page 1 and page 2 responses
        page1 = {
            "messages": [{"id": f"msg_{i}"} for i in range(50)],
            "nextPageToken": "token_page_2"
        }
        page2 = {
            "messages": [{"id": f"msg_{i}"} for i in range(50, 75)],
            "nextPageToken": None
        }
        mock_list.return_value.execute.side_effect = [page1, page2]

        msgs = fetch_messages_paginated(service, "query", max_cap=200)
        self.assertEqual(len(msgs), 75)
        self.assertEqual(msgs[0]["id"], "msg_0")
        self.assertEqual(msgs[-1]["id"], "msg_74")

    def test_fetch_messages_paginated_respects_max_cap(self):
        service = MagicMock()
        mock_list = service.users().messages().list
        page1 = {
            "messages": [{"id": f"msg_{i}"} for i in range(50)],
            "nextPageToken": "token_2"
        }
        mock_list.return_value.execute.return_value = page1

        msgs = fetch_messages_paginated(service, "query", max_cap=30)
        self.assertEqual(len(msgs), 30)

    def test_extract_email_html_multipart(self):
        html_sample = "<p>New Release!</p>"
        b64_data = base64.urlsafe_b64encode(html_sample.encode("utf-8")).decode("utf-8")
        payload = {
            "parts": [
                {"mimeType": "text/plain", "body": {"data": "plain"}},
                {"mimeType": "text/html", "body": {"data": b64_data}}
            ]
        }
        result = extract_email_html(payload)
        self.assertEqual(result, html_sample)

    def test_compute_iso_week_utc(self):
        # Sunday 2026-08-30 23:30:00 UTC is in 2026-W35
        # In UTC+8 (Taiwan), this would be Monday 2026-08-31 07:30:00 (which is 2026-W36)
        dt_sunday_utc = datetime(2026, 8, 30, 23, 30, 0, tzinfo=timezone.utc)
        timestamp = dt_sunday_utc.timestamp()
        
        iso_week = compute_iso_week_utc(timestamp)
        self.assertEqual(iso_week, "2026-W35")

    def test_run_sync_pipeline_signature_and_defaults(self):
        import inspect
        from app.services.sync_pipeline import run_sync_pipeline
        sig = inspect.signature(run_sync_pipeline)
        self.assertIn("limit", sig.parameters)
        self.assertEqual(sig.parameters["limit"].default, 50)
        self.assertEqual(sig.parameters["force_rescan"].default, False)

    def test_run_sync_pipeline_custom_limit_with_cap_notice(self):
        import asyncio
        import json
        from unittest.mock import patch
        from app.services.sync_pipeline import run_sync_pipeline

        async def _run():
            with self._mock_sync_pipeline(messages=[{"id": f"m{i}"} for i in range(20)]) as mock_fetch:
                with patch("app.services.sync_pipeline.extract_email_html", return_value=""), \
                     patch("app.services.sync_pipeline.scrape_bandcamp_metadata", return_value=None):
                    
                    events = []
                    async for event in run_sync_pipeline(force_rescan=False, limit=20):
                        if event.startswith("data: "):
                            events.append(json.loads(event[6:].strip()))

                    complete_event = next(e for e in events if e.get("status") == "complete")
                    self.assertIn("已達單次上限 20 封", complete_event["message"])
                    self.assertIn("強制重掃", complete_event["message"])
                    mock_fetch.assert_called_once()
                    self.assertEqual(mock_fetch.call_args[0][2], 20)

        asyncio.run(_run())

    def test_run_sync_pipeline_force_rescan_forces_200(self):
        import asyncio
        from app.services.sync_pipeline import run_sync_pipeline

        async def _run():
            with self._mock_sync_pipeline(messages=[]) as mock_fetch:
                async for _ in run_sync_pipeline(force_rescan=True, limit=20):
                    pass

                mock_fetch.assert_called_once()
                self.assertEqual(mock_fetch.call_args[0][2], 200)

        asyncio.run(_run())

    def test_run_sync_pipeline_clamps_limits(self):
        import asyncio
        from app.services.sync_pipeline import run_sync_pipeline

        async def _run():
            # Test negative/zero limit clamps to 1
            with self._mock_sync_pipeline(messages=[]) as mock_fetch:
                async for _ in run_sync_pipeline(force_rescan=False, limit=-10):
                    pass
                self.assertEqual(mock_fetch.call_args[0][2], 1)

            # Test oversized limit clamps to 200
            with self._mock_sync_pipeline(messages=[]) as mock_fetch:
                async for _ in run_sync_pipeline(force_rescan=False, limit=999):
                    pass
                self.assertEqual(mock_fetch.call_args[0][2], 200)

        asyncio.run(_run())

    def test_sync_stream_endpoint_forwards_limit(self):
        from starlette.testclient import TestClient
        from unittest.mock import patch
        from app.main import app

        client = TestClient(app)
        async def dummy_pipeline(force_rescan=False, limit=50):
            yield f"data: {{\"status\": \"test\", \"limit\": {limit}}}\n\n"

        with patch("app.routers.api.run_sync_pipeline", side_effect=dummy_pipeline) as mock_pipe:
            resp = client.get("/api/sync/stream?limit=100")
            self.assertEqual(resp.status_code, 200)
            mock_pipe.assert_called_once_with(force_rescan=False, limit=100)

    def test_sync_stream_endpoint_boundary_clamping(self):
        from starlette.testclient import TestClient
        from unittest.mock import patch
        from app.main import app

        client = TestClient(app)
        async def dummy_pipeline(force_rescan=False, limit=50):
            yield f"data: {{\"status\": \"test\", \"limit\": {limit}}}\n\n"

        with patch("app.routers.api.run_sync_pipeline", side_effect=dummy_pipeline) as mock_pipe:
            # Negative limit clamped to 1
            resp_neg = client.get("/api/sync/stream?limit=-10")
            self.assertEqual(resp_neg.status_code, 200)
            mock_pipe.assert_called_with(force_rescan=False, limit=1)

            # Zero limit clamped to 1
            resp_zero = client.get("/api/sync/stream?limit=0")
            self.assertEqual(resp_zero.status_code, 200)
            mock_pipe.assert_called_with(force_rescan=False, limit=1)

            # Oversized limit clamped to 200
            resp_over = client.get("/api/sync/stream?limit=999")
            self.assertEqual(resp_over.status_code, 200)
            mock_pipe.assert_called_with(force_rescan=False, limit=200)

    def test_bpm_update_pydantic_validation(self):
        from starlette.testclient import TestClient
        from unittest.mock import patch
        from app.main import app

        client = TestClient(app)
        with patch("app.routers.api.get_db_connection") as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn
            mock_cur = mock_conn.cursor.return_value
            mock_cur.fetchone.return_value = {"id": 1}

            # Out of bounds: < 40.0
            resp_low = client.patch("/api/releases/1/bpm", json={"bpm": 35.0})
            self.assertEqual(resp_low.status_code, 400)

            # Out of bounds: > 300.0
            resp_high = client.patch("/api/releases/1/bpm", json={"bpm": 350.0})
            self.assertEqual(resp_high.status_code, 400)

            # Valid BPM: 124.5
            resp_ok = client.patch("/api/releases/1/bpm", json={"bpm": 124.5})
            self.assertEqual(resp_ok.status_code, 200)
            self.assertEqual(resp_ok.json()["bpm"], 124.5)

    from contextlib import contextmanager
    @contextmanager
    def _mock_sync_pipeline(self, messages=None):
        from unittest.mock import patch
        with patch("app.services.sync_pipeline.build_gmail_service") as mock_auth, \
             patch("app.services.sync_pipeline.get_db_connection") as mock_db, \
             patch("app.services.sync_pipeline.fetch_messages_paginated") as mock_fetch:
            mock_auth.return_value = MagicMock()
            mock_db.return_value.__enter__.return_value = MagicMock()
            mock_fetch.return_value = messages if messages is not None else []
            yield mock_fetch

if __name__ == "__main__":
    unittest.main()


