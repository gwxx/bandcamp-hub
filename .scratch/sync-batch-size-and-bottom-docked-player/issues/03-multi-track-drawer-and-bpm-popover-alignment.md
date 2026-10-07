# 03: Multi-Track Drawer and BPM Popover Geometry Alignment

**What to build:**
Align the child floating panels above the newly docked bottom player bar: ensure the multi-track drawer (`#multi-track-drawer`) opens centered above the player bar at a comfortable reading constraint (`max-w-5xl mx-auto mb-2`) with glass styling and rounded corners, and ensure the DJ BPM tempo popover (`#bpm-panel`) pops upwards cleanly (`bottom-full mb-3 left-0`) above the docked player bar without horizontal scrollbars, jitter, or clipping.

**Blocked by:** 02: Full-Width Docked Bottom Player Bar

**Status:** resolved

- [x] `#multi-track-drawer` is styled to center above the docked player bar with `max-w-5xl mx-auto mb-2`, retaining glass styling, border framing, and rounded corners (`rounded-2xl`).
- [x] `#bpm-panel` positions cleanly upwards with `bottom-full mb-3 left-0`, maintaining its standardized 320px (`w-80`) geometry without clipping.
- [x] Toggling the drawer and the BPM panel does not induce layout shifts or horizontal scrollbars on the docked player bar.
- [x] Keyboard shortcut handling (Escape to close open panels/player) remains fully functional.
- [x] Automated tests in `tests/test_ui_refinements.py` verify the updated geometry and placement.

## Comments
- Set drawer bounds to `max-w-5xl mx-auto mb-2`.
- Adjusted `#bpm-panel` to `bottom-full mb-3 left-0`.
- Verified UI tests in `tests/test_ui_refinements.py`.
