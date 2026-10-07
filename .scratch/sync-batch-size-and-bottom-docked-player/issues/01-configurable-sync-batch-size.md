# 01: Configurable Sync Batch Size

**What to build:**
A user can select their preferred sync batch size (20, 50, 100, 200) directly beside the "立即同步" (Instant Sync) button in the top header. The choice is persisted in browser local storage and defaults to 50. Initiating a sync streams updates only up to the requested batch size. Upon completion, if the batch ceiling was met, the system provides a clear reminder that older notifications can be retrieved using the 30-day force rescan. The 30-day force rescan in settings continues to scan up to the full 200 ceiling.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] A styled `<select id="sync-limit-select">` with options 20, 50, 100, 200 is positioned adjacent to the "立即同步" button in the header.
- [x] User's batch size selection is stored in `localStorage` under `bandcamp_hub_sync_limit` and loaded on initialization, falling back to 50.
- [x] `startSync(forceRescan)` appends `&limit=${selectedLimit}` to `/api/sync/stream` when `forceRescan` is false.
- [x] Endpoint `/api/sync/stream` and backend function `run_sync_pipeline` accept `limit: int = 50` and enforce `max_cap = limit` in `fetch_messages_paginated`.
- [x] When `force_rescan=True`, `limit` is forced to 200.
- [x] When `total_msgs >= limit`, the completion SSE message includes: `"同步完成！已收納/更新 X 首作品（已達單次上限 Y 封；若需補齊更早歷史可至設定執行強制重掃）"`.
- [x] Automated tests in `tests/test_sync_pipeline.py` verify custom limits, default limits, force rescan override, and completion messages.

## Comments
- Implemented `limit: int = 50` in `run_sync_pipeline` and `/api/sync/stream`.
- Added styled `<select id="sync-limit-select">` in header with `localStorage` persistence.
- Verified unit and endpoint tests in `tests/test_sync_pipeline.py`.
