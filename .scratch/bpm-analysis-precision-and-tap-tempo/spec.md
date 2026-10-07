# Spec: BPM Analysis Precision and Tap Tempo Refinement

Status: ready-for-agent

## Problem Statement

Users triaging electronic releases with fast, syncopated rhythms (such as Drum & Bass, Jungle, Breakbeat, and fast Rock) experience significant tempo inaccuracies with the built-in BPM analyzer. For example, a 178 BPM Drum & Bass track was analyzed as 133 BPM.

This failure stems from four compounded architectural flaws:
1. **Harmonic Cross-Beat Trapping**: Autocorrelation without harmonic comb filtering is easily fooled by 3:4 syncopated accents ($178 \times \frac{3}{4} = 133.5 \approx 133$), where dotted-quarter notes or complex breakbeat accents generate a higher correlation sum than the fundamental beat.
2. **Single 150 Hz Low-Pass Blindness**: The existing filter only captures sub-bass and kick drums below 150 Hz, leaving the engine completely deaf to mid-frequency snares, claps, and hi-hats that define the actual tempo.
3. **Coarse Temporal Quantization**: The 100 Hz frame rate (10ms hop size) creates a 5.3 BPM step-jump at 178 BPM (lag 33 = 181.8 BPM vs lag 34 = 176.5 BPM), driving correlation peaks toward neighboring lags.
4. **Cold Intro Sampling**: Blindly taking seconds 10 to 40 frequently samples ambient intros or drumless buildups rather than the active rhythmic groove.
5. **Lack of Tap Tempo Utility**: When tracks feature unusual time signatures or polyrhythms, users lack a quick "Tap Tempo" tool to rhythmically input the BPM, and must resort to guessing or manual numeric typing.

## Solution

1. **Dual-Band Web Audio Spectral Flux Engine**: Filter audio into two complementary frequency bands—a low-frequency band (50–180 Hz) for kick/bass and a mid-frequency band (200–2500 Hz) for snares/claps/transients—combining their onset envelopes to capture the full drum kit.
2. **200 Hz Frame Rate Resolution**: Double the analysis frame rate from 100 Hz to 200 Hz (5ms hop size), reducing temporal quantization error at tempos above 170 BPM to under 2 BPM.
3. **Harmonic Comb Filtering & Sub-Harmonic Penalty**: Implement harmonic comb evaluation on candidate autocorrelation lags, applying an explicit penalty factor against non-integer 3:4, 4:3, and 2:3 cross-harmonics while favoring fundamental and integer-octave peaks.
4. **RMS Energy Peak Window Search**: Pre-scan the decoded audio buffer to locate the continuous 30-second window exhibiting maximum RMS rhythmic energy, ensuring tempo detection operates on drops or main rhythm sections rather than quiet ambient intros.
5. **70–200 BPM Normalization Range**: Widen the standard normalization boundary from 60–180 BPM to 70–200 BPM, preventing 174–180 BPM Drum & Bass and fast electronic genres from being erroneously halved.
6. **Streamlined UI with Integrated Tap Tempo**: Maintain a clean default BPM panel view (`-2`, `[BPM display]`, `+2`, `✏️ Edit`, `Save`). When clicking "✏️ Edit", expand an advanced manual configuration mode featuring direct numeric input, `-2`/`+2` buttons, and an interactive "Tap" button (supporting keyboard `T` key tapping, with 2-second idle reset). Exclude unpractical half-speed (`÷2`) and double-speed (`×2`) buttons.

## User Stories

1. As a DJ auditing a 178 BPM Drum & Bass Track, I want the client-side Web Audio engine to accurately calculate ~178 BPM instead of trapping on the 133 BPM 3:4 syncopated harmonic, so that I do not need to manually override standard genre tempos.
2. As a music curator listening to a Release with an ambient or slow-building intro, I want the analyzer to automatically scan the audio buffer for the 30-second window with highest RMS energy, so that the analysis executes on the main drop or chorus instead of drumless intro pads.
3. As a DJ reviewing breakbeat and syncopated electronic Tracks, I want onset detection to evaluate both low-frequency kicks and mid-frequency snares, so that polyrhythmic interaction between drum elements is captured.
4. As an audio curator evaluating high-tempo tracks, I want the analysis frame rate to run at 200 Hz (5ms hop size), so that temporal quantization error at tempos above 170 BPM is halved.
5. As a DJ curating across diverse genres, I want the automatic tempo normalization window to span 70 to 200 BPM, so that fast 174–180 BPM Drum & Bass is not halved to 87–90 BPM and 182 BPM Hardcore is not cut down to 91 BPM.
6. As a user viewing the DJ tempo popover panel, I want the default display to remain minimal and compact, so that screen space is preserved and essential controls are immediately readable.
7. As a DJ fine-tuning an analyzed tempo, I want the default view to provide immediate `-2` and `+2` adjustment buttons, so that minor pitch differences can be nudged with a single click.
8. As a DJ evaluating an ambiguous or complex track, I want to click "✏️ Edit" to expand a dedicated manual editing mode, so that I can directly type a known BPM, tap the beat, or adjust values.
9. As a DJ in manual edit mode, I want a dedicated "Tap" button, so that I can manually tap the rhythm with my mouse and have the average BPM computed in real-time.
10. As a power-user DJ in manual edit mode, I want pressing the `T` key on my physical keyboard to trigger the Tap tempo function, so that I can rhythmically tap the tempo on my keyboard without mouse cursor fatigue.
11. As a DJ tapping tempo, I want tapping 2 or more beats to immediately update the numeric input field and staged BPM display with the running average, so that I can visually verify convergence within 4 to 8 beats.
12. As a DJ who pauses between tapping sequences, I want the Tap tempo counter to automatically reset after 2 seconds of inactivity, so that a new tapping sequence starts cleanly without mixing into previous intervals.
13. As a user who values interface simplicity, I want double-speed (`×2`) and half-speed (`÷2`) buttons to be excluded from the interface, so that redundant controls that I find unpractical do not clutter my workflow.
14. As a user finishing manual BPM edits, I want dedicated "套用" (Apply) and "✕" (Cancel) buttons in the edit view, so that I can safely accept or discard my adjustments.
15. As a user who has finalized a staged BPM, I want the "✓ 確認儲存至資料庫" button to persist the value to the Evergreen Vault, so that the tempo is preserved across sessions and tabs.
16. As a developer writing regression tests, I want automated assertions validating the 200 Hz dual-band onset logic, harmonic comb weighting, 70–200 BPM normalization boundary, and Tap tempo reset timing, so that future refactors cannot re-introduce harmonic trapping regressions.

## Implementation Decisions

### 1. Dual-Band Filtering and 200 Hz Spectral Flux Engine
- The Web Audio analysis routine constructs two parallel BiquadFilter nodes:
  - Low-Band: Low-pass filter at 180 Hz with Q=1.0 to isolate kick drums and low-end bass stabs.
  - Mid-Band: Band-pass or high-pass/low-pass combination centered between 200 Hz and 2500 Hz with Q=1.0 to isolate snares, rimshots, claps, and hi-hat transients.
- Hop size is configured to 5ms (200 Hz frame rate at 22.05 kHz sample rate, `hopSize = sampleRate / 200 = ~110 samples`), doubling temporal resolution.
- Onset envelopes are calculated via positive first-difference spectral flux on both bands and combined with normalized weighting ($0.6 \times \text{Low} + 0.4 \times \text{Mid}$).

### 2. Intelligent RMS Energy Peak Search
- Prior to full rendering or analysis, the decoded audio buffer is coarsely sampled in 5-second segments to compute Root-Mean-Square (RMS) power.
- The 30-second window yielding the highest cumulative RMS energy is selected as `startOffset`, ensuring the analysis window locks onto the main rhythm section/drop and skips quiet ambient intros.

### 3. Harmonic Comb Filtering & Cross-Harmonic Penalty
- Autocorrelation search computes correlation across candidate lags corresponding to 70–200 BPM at 200 Hz ($lag_{min} = \frac{200 \times 60}{200} = 60$; $lag_{max} = \frac{200 \times 60}{70} = 171$).
- Candidate peaks are evaluated with harmonic comb weighting:
  - Harmonics at integer ratios ($1\times, 2\times, 0.5\times$) are scored positively.
  - Cross-harmonics at 3:4 and 4:3 ratios ($\sim 1.33\times$ and $\sim 0.75\times$) receive an explicit dampening penalty factor ($\sim 0.65\times$), preventing syncopated 3:4 accents from overriding the fundamental tempo.
- Normalization loop is clamped to 70–200 BPM (`while (bpm < 70) bpm *= 2; while (bpm > 200) bpm /= 2;`).

### 4. UI Streamlining and Tap Tempo Integration
- Default view in `#bpm-staged-container` remains uncluttered:
  - `-2` button, staged BPM value display, `+2` button, `✏️ Edit` toggle button.
  - Conditional `✓ 確認儲存至資料庫` button.
- Half-speed (`÷2`) and double-speed (`×2`) buttons are explicitly omitted.
- Expanded manual edit mode (`#bpm-edit-mode`) includes:
  - Direct numeric input field (`#custom-bpm-input`).
  - Quick `-2` and `+2` buttons.
  - `🥁 Tap` tempo button (`#btn-tap-tempo`) with visual tap counter badge.
  - `套用` (Apply) and `✕` (Cancel) toggle buttons.
- Tap tempo logic maintains a rolling queue of timestamps (`performance.now()`):
  - Gaps $> 2000ms$ clear previous taps.
  - 2 or more taps compute average delta $\Delta t$ and derive $\text{BPM} = \text{round}((60000 / \Delta t) \times 10) / 10$.
  - BPM is clamped between 40 and 300 and immediately reflected in `#custom-bpm-input`.
- Keyboard listener intercepts key `T` or `t` when `#bpm-edit-mode` is visible and activeElement is not the text input itself, triggering the tap handler.

## Testing Decisions

- **What makes a good test**:
  - Tests verify user-observable behavior and external DOM/API contracts rather than internal variable names.
  - Tests verify that the HTML template includes dual-band audio filtering, 200 Hz hop calculations, harmonic comb filtering logic, and the 70–200 BPM normalization range.
  - Tests verify that the template contains the RMS energy peak selector and proper Tap tempo DOM elements (`#btn-tap-tempo`) and `T` key event listeners.
  - Tests verify that `÷2` and `×2` buttons are not rendered in the template.
  - Tests verify that the backend PATCH `/api/releases/{id}/bpm` endpoint continues to validate 40.0–300.0 BPM ranges.
- **Modules to be tested**:
  - Frontend template and client script integration: `tests/test_ui_refinements.py`.
  - Backend API contract and database persistence: `tests/test_bpm_analyzer_and_proxy.py` and `tests/test_audio_resilience_and_bpm.py`.
- **Prior Art**:
  - `tests/test_ui_refinements.py`: Existing tests for BPM panel width (`w-80`), conditional save button toggling, and BPM validation logic.

## Out of Scope

- Installing heavy server-side Python DSP libraries (such as `librosa`, `aubio`, `scipy`, or `ffmpeg`).
- Modifying SQLite database schemas or `releases` table schema.
- Automatic beat grid visual waveforms or DJ cue-point dragging.

## Further Notes

- Maintains strict compliance with `CONTEXT.md` domain concepts (Release, Track, ISO Week, Evergreen Vault).
- Preserves offline resilience and low client-side latency.
