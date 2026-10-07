# 04: Non-Blocking Paginated Notification Synchronization

**What to build:**
Users can initiate incremental or full synchronization without freezing the web interface or stopping music playback. The ingestion pipeline paginates through Gmail notifications up to a safe batch cap of 200 messages, computes ISO Weeks in UTC, and reliably advances the Sync Watermark only after the entire batch is persisted.

**Blocked by:** 01: Storage Engine Hardening & Online WAL Backup, 02: Resilient Metadata Fallback Parsing

**Status:** ready-for-agent

- [x] Google API Client network calls run in syncio.to_thread without blocking the FastAPI event loop.
- [x] Pagination loops through 
extPageToken up to a batch cap of 200 messages.
- [x] Notification timestamp calculation strictly specifies UTC timezone (datetime.fromtimestamp(..., tz=timezone.utc)).
- [x] Sync Watermark advances only after the paginated batch is fully processed and persisted.
