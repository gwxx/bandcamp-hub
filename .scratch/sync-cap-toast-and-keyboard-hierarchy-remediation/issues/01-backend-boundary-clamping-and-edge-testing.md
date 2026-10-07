# 01: Backend Boundary Clamping, URL Cleanup, and Edge Testing

**What to build:**
Enforce strict clamping of the sync batch limit between 1 and 200 in both the synchronization pipeline and the FastAPI route, preventing quota bypasses and pipeline failures from abnormal input. Clean up the frontend forced rescan call to omit redundant limit parameters. Add automated test coverage asserting boundary and extreme values (negative, zero, and excessive limits), refactor BPM update validation to use declarative Pydantic field constraints, and deduplicate test mock scaffolding.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] In `app/services/sync_pipeline.py`, compute `effective_limit = 200 if force_rescan else min(200, max(1, limit))`.
- [x] In `app/routers/api.py`, declare `limit: int = Query(50, ge=1, le=200)` for `/api/sync/stream`.
- [x] In `app/routers/api.py`, update `BpmUpdateRequest` to declare `bpm: float | None = None` with encapsulated domain validation method and remove redundant procedural range checks.
- [x] In `app/routers/api.py`, extract a reusable timestamp helper for `now_iso` to reduce duplication.
- [x] In `app/templates/index.html`, update `startSync(true)` to call `/api/sync/stream?force_rescan=true` without appending `&limit=200`.
- [x] In `tests/test_sync_pipeline.py`, add test cases verifying `limit <= 0` clamps to 1 and `limit > 200` clamps to 200.
- [x] In `tests/test_sync_pipeline.py`, deduplicate triple-mock context manager scaffolding across tests into a shared helper.

## Comments
- Implemented `min(200, max(1, limit))` in `app/services/sync_pipeline.py`.
- Updated `/api/sync/stream` to use `Query(50, ge=1, le=200)`.
- Extracted `get_now_iso()` helper and encapsulated `validate_bpm_range()` on `BpmUpdateRequest`.
- Cleaned up `startSync(true)` URL parameter in `index.html`.
- Added boundary tests and deduplicated mock fixture in `tests/test_sync_pipeline.py`.
- Verified all 39 tests pass with code 0.
