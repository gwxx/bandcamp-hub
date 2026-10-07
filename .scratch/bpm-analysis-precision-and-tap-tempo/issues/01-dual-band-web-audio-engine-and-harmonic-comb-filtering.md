# 01: Dual-Band Web Audio Engine and Harmonic Comb Filtering

**What to build:**
Upgrade the client-side Web Audio BPM analyzer to eliminate harmonic false-peak trapping (e.g. 133 vs 178 BPM). The analyzer pre-scans the decoded audio buffer to locate the continuous 30-second window with maximum RMS energy (avoiding cold ambient intros), splits the audio signal into dual frequency bands (50–180 Hz for kick/bass and 200–2500 Hz for snare/clap transients), runs at 200 Hz frame rate (5ms hop size), and applies harmonic comb filtering with an explicit penalty factor against non-integer 3:4, 4:3, and 2:3 cross-harmonics while expanding the normalization window to 70–200 BPM.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] Audio buffer is scanned in coarse segments to identify the continuous 30-second window with peak RMS rhythmic energy as `startOffset`
- [x] Dual-band biquad filters isolate low-frequency (50–180 Hz) and mid-frequency (200–2500 Hz) signals in `OfflineAudioContext`
- [x] Analysis frame rate runs at 200 Hz (5ms hop size, ~110 samples at 22.05 kHz) to halve high-BPM quantization error
- [x] Positive first-difference spectral flux onset envelopes from both bands are combined with weighted ratio
- [x] Autocorrelation lag evaluation applies harmonic comb scoring: integer harmonics ($1\times, 2\times, 0.5\times$) are rewarded, while non-integer 3:4, 4:3, and 2:3 cross-beat harmonics receive an explicit dampening penalty
- [x] Tempo normalization loop clamps between 70 and 200 BPM (`while (bpm < 70) bpm *= 2; while (bpm > 200) bpm /= 2;`)
- [x] Automated regression tests in `tests/test_ui_refinements.py` assert dual-band filter setup, 200 Hz hop calculations, harmonic comb penalties, RMS peak window selector, and 70–200 BPM normalization range
