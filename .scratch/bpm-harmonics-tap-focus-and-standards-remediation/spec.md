# Spec: BPM Harmonics, Tap Tempo Focus, and Domain Standards Remediation

Status: implemented

## Problem Statement

Following the initial delivery of the dual-band BPM analysis engine and Tap Tempo tools, a thorough code review and user inspection uncovered critical usability, architectural, and standard compliance gaps:

1. **Persistent Domain Glossary Violations**: Forbidden terms explicitly barred by the domain glossary (`CONTEXT.md`)—namely `ITEM:` in keyboard HUD notifications, `搜尋藝人、專輯` in the search input placeholder, and `drawer-album-title` in drawer element IDs—persisted across multiple review cycles. Previous remediation passes missed these occurrences because regression test suites lacked negative assertions (`assertNotIn`) targeting these exact strings.
2. **`T` Key Tap Tempo Blocked by Input Auto-Focus**: Opening manual edit mode automatically set browser focus to `#custom-bpm-input`. Because the global keyboard listener terminates early when `activeElement` is an input field, pressing the physical `T` key failed to trigger tempo tapping, forcing users to manually click outside or blur the input before keyboard tapping would function.
3. **Harmonic Comb Filtering Gaps and High-Tempo Octave Blindness**:
   - The cross-harmonic penalty only checked the 3:4 ratio (`subLag34`) and completely omitted the 4:3 cross-harmonic ratio (`subLag43`), failing to dampen reverse polyrhythmic accents.
   - The candidate lag computation was restricted strictly between lag 60 and 171. Consequently, tracks faster than 140 BPM (lag < 85) had half-lags (`halfLag < 43`) that fell below `minLag`, rendering the 0.5x octave harmonic bonus completely unreachable for high-speed styles such as 174–180 BPM Drum & Bass.
   - The mid-band filter Q factor was set to 0.7 instead of the specified 1.0.
4. **Tap Tempo Desynchronization from Staged Display**: Tapping tempo updated the numeric text input value but neglected to update the companion staged BPM display element and its status indicator in real-time.
5. **Code Duplication and Cryptic Variable Naming**: BPM boundary clamping (40.0–300.0) and rounding logic were duplicated across multiple manual adjustment handlers, while dual-band spectral flux calculations utilized cryptic two-letter abbreviations (`sL`, `sM`, `diffL`, `diffM`).

## Solution

1. **Definitive Global Domain Terminology Cleanup and Test Hardening**: Replace every instance of forbidden terms (`ITEM:`, `專輯`, `album`) with approved domain vocabulary (`RELEASE:`, `作品`, `release`). Add strict negative regression assertions (`assertNotIn`) to the test suite to permanently eliminate regression.
2. **Non-Intrusive Edit Mode Focus Interaction**: When expanding manual edit mode, do not auto-focus the numeric input field. Keep focus on the container or the Tap button so pressing the `T` key immediately triggers tempo tapping without keyboard input interference. Allow users to explicitly click the input field when direct numeric entry is desired.
3. **Comprehensive Harmonic Comb Evaluation and Octave Lag Expansion**:
   - Extend the raw autocorrelation calculation window across lags 30 to 340, ensuring all tempos within the 70–200 BPM target range can access both half-lag (double-speed octave) and double-lag (half-speed octave) correlation values.
   - Implement both 3:4 and 4:3 cross-harmonic dampening penalties (~0.65x factor), eliminating syncopated polyrhythmic traps in fast electronic music.
   - Align mid-band filter Q factor to 1.0.
4. **Real-Time Tap Tempo Staged Synchronization**: Update both the numeric input field and `#staged-bpm-val` during tapping, adjusting the status badge to indicate an unsaved staged state. Cap the rolling tap history to the most recent 10 taps to filter human timing jitter while preserving the 2-second idle reset.
5. **Shared Clamping Helper and Clear Naming**: Unify BPM clamping and 0.1 precision formatting into a shared utility function, rename spectral flux variables to descriptive identifiers (`sampleLow`, `sampleMid`, `diffLow`, `diffMid`), and deduplicate test assertions.

## User Stories

1. As a DJ navigating releases with keyboard shortcuts (J/K), I want the HUD notifications to display `RELEASE: 1/N` instead of forbidden terms like `ITEM:`, so that the interface complies strictly with the project's domain model.
2. As a user searching my library, I want the search input placeholder to prompt for "搜尋藝人、作品 (Esc 清除)..." instead of using the forbidden word "專輯", maintaining clean terminology throughout the interface.
3. As a developer running regression tests, I want the test suite to assert that forbidden terms (`ITEM:`, `RELEASE WEEKS`, `搜尋藝人、專輯`, `drawer-album-title`) do not exist anywhere in template files, so that regressions are caught before reaching code review.
4. As a DJ clicking "✏️ Edit" in the BPM popover, I want the panel to open without trapping focus inside the numeric input field, so that I can immediately press the physical `T` key on my keyboard to start tapping the beat.
5. As a DJ tapping tempo with the physical `T` key or mouse clicks, I want both the numeric input field and the staged BPM label to update synchronously in real-time, so that I can verify the calculated tempo without having to click "套用" first.
6. As a DJ tapping tempo, I want the system to calculate the running average over the most recent 10 taps, so that early timing inaccuracies do not skew the settled tempo.
7. As a DJ who stops tapping, I want the tap queue to automatically reset after 2 seconds of inactivity, so that a fresh rhythm sequence can begin cleanly.
8. As a DJ auditing a fast 178 BPM Drum & Bass Track, I want the harmonic comb filter to evaluate the half-lag octave (~34 frames) without being blocked by premature minimum lag guards, so that high-tempo tracks receive proper octave reinforcement.
9. As an audio curator evaluating breakbeat tracks, I want both 3:4 and 4:3 cross-harmonic ratios to receive explicit dampening penalties, so that off-beat syncopation and cross-rhythms do not outrank the fundamental pulse.
10. As an audio engineer inspecting the DSP pipeline, I want the mid-band bandpass filter to operate with a Q factor of 1.0, matching technical specifications for transient isolation.
11. As a developer maintaining the codebase, I want all BPM manual adjustments to route through a unified clamping and rounding helper, ensuring consistent boundaries (40.0–300.0) without duplicated code.
12. As a developer reading the spectral flux analysis implementation, I want variable names to clearly state `sampleLow`, `sampleMid`, `diffLow`, and `diffMid`, so that the DSP code is understandable and self-documenting.

## Implementation Decisions

### 1. Domain Terminology Cleansing and Test Hardening
- In `app/templates/index.html`:
  - Replace `ITEM: ${selectedIndex + 1}/${flatCards.length}` with `RELEASE: ${selectedIndex + 1}/${flatCards.length}`.
  - Replace `placeholder="搜尋藝人、專輯 (Esc 清除)..."` with `placeholder="搜尋藝人、作品 (Esc 清除)..."`.
  - Replace `id="drawer-album-title"` with `id="drawer-release-title"`.
- In `tests/test_ui_refinements.py`:
  - Add explicit negative assertions:
    - `self.assertNotIn("ITEM:", self.html_content)`
    - `self.assertNotIn("搜尋藝人、專輯", self.html_content)`
    - `self.assertNotIn("drawer-album-title", self.html_content)`

### 2. Tap Tempo Focus Interaction
- In `toggleBpmEditMode()`:
  - Populate `customInput.value` with the current staged BPM.
  - Do NOT invoke `customInput.focus()`.
  - Leave focus on the modal container or assign focus to `#btn-tap-tempo`.
- In `handleTapTempo()`:
  - Keep focus on `#btn-tap-tempo` so subsequent physical `T` keypresses continue triggering the tap handler.

### 3. Harmonic Comb Filtering Completion and Octave Lag Expansion
- Expand `rawCorr` lag calculation range from `minLag=60, maxLag=171` to:
  - `corrMinLag = 30` (equivalent to 400 BPM at 200 Hz).
  - `corrMaxLag = 342` (equivalent to 35 BPM at 200 Hz).
- For candidate lags within the target 70–200 BPM window (`lag = 60` to `171`):
  - Half-lag octave: `halfLag = Math.round(lag / 2)`. Because `corrMinLag = 30`, `halfLag` is always within the computed range (`30 <= halfLag <= 85`). Add `0.35 * rawCorr[halfLag]` unconditionally.
  - Double-lag octave: `doubleLag = lag * 2`. Add `0.35 * rawCorr[doubleLag]` unconditionally.
  - 3:4 cross-harmonic penalty: if `rawCorr[Math.round(lag * 0.75)] > 0.4 * rawCorr[lag]`, multiply score by 0.65.
  - 4:3 cross-harmonic penalty: if `rawCorr[Math.round(lag * 1.333)] > 0.4 * rawCorr[lag]`, multiply score by 0.65.
- Update `midFilter.Q.value = 1.0`.

### 4. Tap Tempo Real-Time Staged BPM Display
- In `handleTapTempo()`:
  - When $\ge 2$ taps are recorded, compute `calculatedBpm = clampBpm(60000 / avgInterval)`.
  - Update `customInput.value = calculatedBpm`.
  - Update `stagedBpm = calculatedBpm`.
  - Update `document.getElementById('staged-bpm-val').innerText = stagedBpm`.
  - Update status tag to `'Tap 測速 (待儲存)'` with amber highlight.
  - Retain rolling queue of at most 10 timestamps (`if (tapTimestamps.length > 10) tapTimestamps.shift();`).

### 5. Shared Utility and Code Cleanliness
- Define `function clampBpm(val)` returning `Math.max(40, Math.min(300, Math.round(val * 10) / 10))`.
- Refactor `nudgeStagedBpm`, `nudgeCustomBpmInput`, and `handleTapTempo` to use `clampBpm`.
- In `analyzeAudioBpm`, rename variables to `sampleLow`, `sampleMid`, `diffLow`, `diffMid`.
- Clean up duplicate assertions in `tests/test_ui_refinements.py`.

## Testing Decisions

- **What makes a good test**:
  - Tests verify user-observable behavior and external DOM/API contracts rather than internal variable names.
  - Tests verify that forbidden terms (`ITEM:`, `專輯`, `album`) are strictly absent from template source code.
  - Tests verify that `findRmsPeakOffset`, dual-band filters, 200 Hz frame rate, 70–200 BPM normalization, and Tap tempo DOM elements are present.
  - Tests verify that `customInput.focus()` is not invoked on edit mode open.
  - Tests verify that both 3:4 and 4:3 harmonic penalties and expanded octave boundaries are present.
- **Modules to be tested**:
  - `tests/test_ui_refinements.py`.
- **Prior Art**:
  - `tests/test_ui_refinements.py`: Existing tests for domain terminology harmonization, BPM normalization, and player dock behavior.

## Out of Scope

- Introducing server-side Python audio analysis libraries (`librosa`, `aubio`, `scipy`).
- Altering SQLite database schemas.
- Visual waveform rendering or DJ cue markers.

## Further Notes

- Maintains strict compliance with `CONTEXT.md` (Release, Track, ISO Week, Evergreen Vault).
- Preserves offline resilience and rapid client-side response times.
