# 03: Absolute BPM Pitch Stepper and Fallback

**What to build:**
Realign the DJ pitch controls from percentage offsets to absolute BPM increments. Replace the stepper buttons with `[-1 BPM]`, `[原速 (1.0x)]`, and `[+1 BPM]`, removing all percentage text from the pitch section. Implement `nudgeBpmPitch(deltaBpm)` to adjust playback speed by exactly `±1.0 BPM` relative to the release's base BPM (clamped between 0.80x and 1.20x). If the current release has no established base BPM (`-- BPM`), fall back to a standard reference baseline of 120.0 BPM and display an informative `(以 120 為基準)` indicator. Update pitch labels, sliders, and HUD notifications (`SPEED: {bpm} BPM (±1.0 BPM)`) to reflect BPM units consistently.

**Blocked by:** 01-domain-glossary-cleansing-and-test-hygiene

**Status:** resolved

- [x] Stepper buttons in the DJ panel are updated to `[-1 BPM]`, `[原速 (1.0x)]`, and `[+1 BPM]`
- [x] Percentage labels (`-1%`, `+1%`, `-20%`, `+20%`, etc.) are removed from the pitch controls and slider scale
- [x] `nudgeBpmPitch(deltaBpm)` calculates `playbackRate = (currentEffectiveBpm + deltaBpm) / baseBpm`, clamping between 0.80x and 1.20x
- [x] Releases without a base BPM fall back to 120.0 BPM as reference baseline and display `(以 120 為基準)`
- [x] HUD notifications report tempo changes as `SPEED: {effBpm} BPM ({deltaBpm >= 0 ? '+' : ''}{deltaBpm} BPM)`
- [x] Automated regression tests in `tests/test_ui_refinements.py` assert presence of BPM stepper buttons, absence of `%` in pitch buttons, and correct math fallback
- [x] All tests in `tests/test_ui_refinements.py` pass cleanly
