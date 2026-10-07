# 02: Streamlined BPM Edit Mode and Tap Tempo Integration

**What to build:**
Enhance the DJ tempo popover panel with a streamlined manual edit mode and an interactive Tap Tempo calculator. The default BPM panel view remains minimal (`-2`, staged BPM display, `+2`, `✏️ Edit`, `Save`) and explicitly excludes unpractical half-speed (`÷2`) and double-speed (`×2`) buttons. Clicking "✏️ Edit" expands an advanced editing panel containing direct numeric input, quick `-2`/`+2` buttons, an interactive `[ 🥁 Tap (T) ]` button with tap counter indicator, and Apply/Cancel controls. Tapping records timestamps, computes running average BPM for $\ge 2$ taps, updates the input field in real time, and auto-resets after 2 seconds of inactivity. Pressing the physical `T` key on the keyboard when edit mode is active triggers the tap action.

**Blocked by:** 01-dual-band-web-audio-engine-and-harmonic-comb-filtering

**Status:** resolved

- [x] Default `#bpm-staged-container` maintains minimal layout (`-2`, staged value display, `+2`, `✏️ Edit`, and conditional `Save`)
- [x] Half-speed (`÷2`) and double-speed (`×2`) buttons are excluded from all BPM panel templates
- [x] Clicking `✏️ Edit` toggles `#bpm-edit-mode` displaying direct numeric input, `-2`/`+2` buttons, Tap button, Apply button, and Cancel button
- [x] `handleTapTempo()` maintains a rolling timestamp queue, auto-clearing if gap between taps exceeds 2000ms
- [x] Running average BPM is calculated for $\ge 2$ taps, clamped between 40 and 300, and immediately reflected in the input field
- [x] Tap button displays dynamic tap count feedback badge (e.g. `Tap (3)`)
- [x] Global keydown listener intercepts `T` / `t` when `#bpm-edit-mode` is open and activeElement is not the text input, triggering `handleTapTempo()`
- [x] Automated regression tests in `tests/test_ui_refinements.py` assert Tap Tempo DOM elements, `T` key event binding, absence of `÷2`/`×2` buttons, and edit mode toggle mechanics
