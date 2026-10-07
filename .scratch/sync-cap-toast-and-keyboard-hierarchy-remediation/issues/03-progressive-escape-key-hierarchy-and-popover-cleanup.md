# 03: Progressive Escape Key Hierarchy and Popover Cleanup

**What to build:**
Refactor the keyboard `Escape` handler into a tiered state machine that closes topmost floating overlays first (Settings Modal -> Help Modal -> BPM Popover -> Multi-Track Drawer) without disrupting ongoing music playback. Closing the bottom player dock via `Escape` only occurs when all sub-panels and modals are already closed. Ensure `closePlayer()` cleanly closes all floating popovers (`#bpm-panel` and `#multi-track-drawer`) to prevent orphaned UI artifacts.

**Blocked by:** 02: Top Sync Cap Notice Toast Banner with Direct Settings Link

**Status:** resolved

- [x] In `app/templates/index.html`, refactor the `Escape` key event branch in `setupKeyboard()` into a prioritized hierarchy:
  1. If `#settings-modal` is open, call `closeSettings()`.
  2. Else if `#help-modal` is open, call `closeHelp()`.
  3. Else if `#bpm-panel` is open, call `toggleBpmPanel()` or hide `#bpm-panel`.
  4. Else if `#multi-track-drawer` is open, call `toggleMultiTrackDrawer()` or hide `#multi-track-drawer`.
  5. Else if `#player-dock` is active (`translate-y-0`), call `closePlayer()`.
- [x] In `closePlayer()`, explicitly ensure `#bpm-panel.classList.add('hidden')` and `#multi-track-drawer.classList.add('hidden')`.
- [x] In `tests/test_ui_refinements.py`, add assertions verifying that `closePlayer` references both `#bpm-panel` and `#multi-track-drawer` hiding, and that Escape hierarchy respects sub-panel priority.

## Comments
- Implemented tiered progressive Escape key handling in `setupKeyboard()`.
- Added `#bpm-panel` hiding to `closePlayer()`.
- Added assertions in `tests/test_ui_refinements.py` covering Escape hierarchy and popover teardown.
- Verified all 41 tests pass with code 0.
