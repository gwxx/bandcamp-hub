# 0003. Gmail Watermark Incremental Synchronization

Email sync queries against the Gmail API utilize a Unix timestamp watermark boundary (`after:<timestamp>`) stored in SQLite to achieve efficient, non-redundant incremental scanning.

## Context
A user's Gmail mailbox may contain years of historical emails. Fetching all matching emails on every sync run would exhaust Gmail API quotas, degrade response times, and redundantly re-parse already ingested releases.

## Decision
We maintain a singleton table `sync_watermark` recording `last_successful_sync` (Unix timestamp). Routine sync queries append `after:{watermark}` to the Gmail search query string. Full historical rescanning is supported as an explicit opt-in parameter (`force_rescan=true`), which ignores the watermark and falls back to a 30-day default window (`newer_than:30d`).

## Consequences
- **Minimal API Footprint**: Typical incremental sync cycles inspect only a handful of newly arrived messages.
- **Concurrency Isolation**: Background sync is guarded by an in-memory `asyncio.Lock` to prevent race conditions during watermark updates.
