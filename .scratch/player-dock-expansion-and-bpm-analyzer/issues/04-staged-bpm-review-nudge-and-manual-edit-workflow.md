# 04: Staged BPM Review, -2/+2 Nudge, and Manual Edit Workflow

**What to build:**
Deliver the comprehensive DJ BPM interactive state machine within the player dock's popover panel. When open, users can trigger "🔍 自動分析目前歌曲 BPM". Once computed, the BPM is held in a temporary staging state with instant `[-2]` and `[+2]` nudge buttons, an `[✏️ Edit]` toggle to expose a direct numeric input field for custom manual entry, and an explicit `[確認儲存]` (Save) button that calls `PATCH /api/releases/{id}/bpm` to commit the value to the database and update the player capsule display. Retain live playback pitch shifting (`0.8x ~ 1.2x`) with native pitch preservation (`preservesPitch = true`).

**Blocked by:** 03: Client-Side Web Audio Tempo Analyzer Engine with Proxy Fallback

**Status:** closed

- [x] DJ Tempo popover displays prominent "🔍 自動分析目前歌曲 BPM" action button when active Release has no saved BPM
- [x] During analysis, shows loading indicator (`⚡ 分析中...`) and temporarily disables triggers
- [x] Staging state displays detected BPM with immediate `[-2]` and `[+2]` nudge buttons that adjust the staged value
- [x] `[✏️ Edit]` toggle switches to an inline numeric input field allowing arbitrary manual BPM overrides
- [x] `[確認儲存]` button commits the staged BPM to SQLite via `PATCH /api/releases/{id}/bpm` and updates the player capsule badge
- [x] Real-time playback speed slider (`0.80x ~ 1.20x`) and `±1%` nudge buttons continue dynamically scaling effective BPM while preserving pitch
