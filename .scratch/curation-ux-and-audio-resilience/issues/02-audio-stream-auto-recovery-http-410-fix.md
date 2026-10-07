# 02: Audio Stream Auto-Recovery for Expired Tokens (HTTP 410 Fix)

**What to build:**
When Bandcamp MP3 preview streams expire due to time-limited URL signatures, attempting to play them causes HTTP 410 Gone errors. An on-demand backend endpoint (`POST /api/releases/{id}/refresh-stream`) re-scrapes the target release on Bandcamp to harvest fresh tokenized streams and update the Evergreen Vault database. The client player automatically catches media loading errors, calls the refresh endpoint in the background, updates its audio source, and resumes playback with zero human intervention and no manual Gmail sync needed.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Backend provides `POST /api/releases/{release_id}/refresh-stream` that re-scrapes the Bandcamp release URL, updates `stream_url` and `tracks_json` in the SQLite database, and returns the refreshed data
- [x] Client `<audio>` element catches error events, triggers the background refresh silently, and seamlessly retries playback with the fresh stream URL
- [x] Non-blocking HUD toast notifies the user that the stream link has been refreshed
- [x] Automated integration test validates the endpoint and database persistence under `tests/test_audio_resilience_and_bpm.py`
