# 04: DJ Tempo Control, Live Pitch Shifting, and BPM Persistence

**What to build:**
A DJ tempo control mechanism embedded directly in the vinyl capsule mini player. A capsule badge displays the current adjusted BPM and playback rate (e.g. `-- BPM (1.0x)` or `124 BPM (1.0x)`). Clicking it opens a DJ popover panel with a 0.80x–1.20x pitch slider, -1% / +1% nudge buttons, and a 1.0x reset button. Playback adjusts in real time via HTML5 `audio.playbackRate` with `preservesPitch = true` (Master Tempo). Users can input and save a base BPM, persisted to the database via `PATCH /api/releases/{release_id}/bpm`.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Mini player displays an interactive BPM / speed badge
- [x] Popover panel allows tempo speed adjustment between 0.80x and 1.20x with real-time recalculation of effective BPM
- [x] `audio.preservesPitch = true` prevents vocal and instrumental key alteration when speed changes
- [x] Backend exposes `PATCH /api/releases/{release_id}/bpm` which updates `releases.bpm` in SQLite
- [x] Base BPM input can be saved and persists upon subsequent playback of that release
- [x] Automated integration tests cover the BPM endpoint and database persistence under `tests/test_audio_resilience_and_bpm.py`
