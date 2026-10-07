# 02: Top Sync Cap Notice Toast Banner with Direct Settings Link

**What to build:**
When an incremental sync reaches the configured batch limit, display an eye-catching, non-blocking Toast notification banner directly beneath the top navigation header instead of relying on the transient 850ms HUD. The banner remains visible for 5 seconds (with an explicit dismiss button) and includes a "前往設定" (Open Settings) action button that launches the settings modal so the user can easily initiate a 30-day force rescan to retrieve older releases.

**Blocked by:** 01: Backend Boundary Clamping, URL Cleanup, and Edge Testing

**Status:** resolved

- [x] Add `#sync-toast-banner` container beneath `<header>` in `app/templates/index.html` styled with dark glass-panel treatment (`glass-panel border border-bc-500/40 text-xs font-mono text-zinc-200 shadow-2xl`).
- [x] Add `showSyncToast(message, effectiveLimit)` function in `app/templates/index.html` that reveals the banner with a 5-second auto-dismiss timer.
- [x] Include an inline action button `<button onclick="openSettings(); closeSyncToast();">⚙️ 前往設定重掃</button>` inside the banner.
- [x] Include an explicit close button `<button onclick="closeSyncToast()">✕</button>` inside the banner.
- [x] In `startSync`, when `data.message` indicates reaching the single-sync limit, trigger `showSyncToast(...)` alongside the status text update.
- [x] In `tests/test_ui_refinements.py`, add automated assertions verifying the existence, structure, and action binding of `#sync-toast-banner`.

## Comments
- Implemented `#sync-toast-banner` below `<header>` with dark glass-panel styling.
- Added `showSyncToast` with 5-second auto-dismiss timer and `closeSyncToast`.
- Bound inline action to `openSettings(); closeSyncToast();`.
- Connected `showSyncToast` to completion SSE message in `startSync`.
- Verified in `tests/test_ui_refinements.py` with passing tests.
