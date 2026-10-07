# 03: Track Stream Isolation, 0:00 Duration Fix, and Non-Blocking Unstreamable Alert

**What to build:**
Multi-track releases must isolate each track's stream URL and strictly forbid falling back to the release-level stream URL when an individual track has no stream. In the tracklist, unstreamable tracks (e.g. unreleased preorder tracks with 0:00 duration) are marked with "無試聽" and given a disabled cursor. Clicking an unstreamable track displays a non-blocking HUD notice (`⚠️ 此曲目未開放試聽，可前往原站收聽`) without interrupting whatever audio is currently playing. Streamable tracks play their own distinct preview audio.

**Blocked by:** 02: Audio Stream Auto-Recovery for Expired Tokens (HTTP 410 Fix)

**Status:** closed

- [x] Remove `track.stream_url || rel.stream_url` fallback in the playback engine
- [x] Tracks without preview audio display "無試聽" instead of confusing 0:00 times in the card tracklist
- [x] Clicking unstreamable tracks triggers a non-blocking HUD alert without halting or interrupting active playback
- [x] Clicking any playable track plays that specific track's distinct audio stream rather than repeating the first preview track
