# 02: Tap Tempo Focus Remediation, Real-Time Sync, and Shared Clamping

**What to build:**
Remediate the manual BPM edit mode keyboard focus behavior, enable real-time staged synchronization during Tap tempo, and extract a unified boundary clamping helper. Opening manual edit mode (`toggleBpmEditMode()`) will no longer auto-focus the numeric text input, ensuring the physical `T` key can immediately trigger `handleTapTempo()` without input field interception. During tempo tapping, both `#custom-bpm-input` and `#staged-bpm-val` will synchronously reflect the running average with an updated status tag. Extract `clampBpm(val)` to eliminate duplicated 40.0–300.0 boundary clamping across handlers.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] `toggleBpmEditMode()` no longer auto-focuses `#custom-bpm-input`, keeping focus on `#btn-tap-tempo` or the container
- [x] Physical `T` key triggers `handleTapTempo()` immediately upon opening edit mode without requiring prior manual blur
- [x] `handleTapTempo()` synchronously updates `custom-bpm-input.value`, `stagedBpm`, and `staged-bpm-val.innerText`
- [x] Status tag dynamically updates to `'Tap 測速 (待儲存)'` with amber highlight during tempo tapping
- [x] `clampBpm(val)` helper function encapsulates 40.0–300.0 boundary clamping and 0.1 precision rounding, called by `nudgeStagedBpm`, `nudgeCustomBpmInput`, and `handleTapTempo`
- [x] Rolling queue in `handleTapTempo()` is capped to the 10 most recent timestamps while preserving the 2-second idle timeout
- [x] Automated regression tests in `tests/test_ui_refinements.py` assert absence of `customInput.focus()`, usage of `clampBpm`, and real-time staged BPM element synchronization
