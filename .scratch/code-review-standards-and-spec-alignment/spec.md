# Spec: Code Review Standards Alignment and BPM State Machine Refinement

Status: ready-for-agent

## Problem Statement

Following the comprehensive code review across both Standards and Spec axes, four discrepancies and visual/architectural friction points were identified:

1. **Tempo Octave Doubling Distortion & Validation Asymmetry**: The client tempo analyzer algorithm used a restricted range (70 ~ 165 BPM), which improperly doubled slow tempos (60–69 BPM) and halved fast tempos (166–180 BPM). Simultaneously, the backend validation accepted sub-1.0 BPM values while the frontend rejected values below 40.0 BPM, causing a boundary mismatch.
2. **BPM Panel State Machine Incompleteness**: When a Track already possesses a persisted base BPM, the analysis action button statically read "自動分析目前歌曲 BPM" instead of offering a clear "重新分析" (Re-analyze) option. Furthermore, the "確認儲存至資料庫" button was displayed continuously even when no edits had occurred, creating redundant click opportunities, and the analysis progress state lacked the specified "⚡ 分析中..." text and pulse animation.
3. **Weekly Triage Button Geometry Disparity**: While the specification designated a circular border button (`rounded-full`) to echo vinyl grooved aesthetics, the weekly triage button was implemented as a rounded rectangle (`rounded-lg`), creating visual inconsistency with surrounding circular icons.
4. **Domain Terminology Divergence (`CONTEXT.md`)**: User interface copy and heads-up display (HUD) notices drifted into forbidden synonyms ("歌曲" instead of standard "曲目", "COMPLETED" instead of "LISTENED"), and unit test fixtures used non-standard domain terms ("Test Album" instead of "Test Release").

## Solution

1. **Standardized Octave Doubling & Unified 40–300 BPM Validation**:
   - Expand the tempo octave normalization range in the Web Audio autocorrelation engine to 60 ~ 180 BPM, faithfully preserving natural tempos across slow downtempo/hip-hop and high-speed drum & bass/jungle.
   - Synchronize both frontend and backend numeric input validation strictly to the range of 40.0 to 300.0 BPM.
2. **Comprehensive BPM Action State Machine & Dynamic Save Trigger**:
   - Dynamically adjust the analysis button text: display "🔍 自動分析目前曲目 BPM" when no BPM exists, and "🔄 重新分析目前曲目 BPM" when a persisted BPM is present.
   - During active analysis, display "⚡ 分析中..." and apply a pulsing visual indicator (`animate-pulse`).
   - Dynamically reveal the "✓ 確認儲存至資料庫" button only when the staged BPM value differs from the database record (`stagedBpm !== activeRelease.bpm`), hiding it when values are synchronized.
   - Maintain the subtle asterisk indicator (`${effBpm}* BPM`) in the player dock to clearly signpost unsaved staged adjustments.
3. **Circular Geometry for Weekly Triage Action**:
   - Update the weekly section header's "mark all listened" button container to a concentric circular border button (`rounded-full`), harmonizing with the interior circular icon and vinyl aesthetic.
4. **Domain Terminology Harmonization with `CONTEXT.md`**:
   - Standardize all UI copy from "歌曲" to "曲目" (Track).
   - Update the bulk-listened HUD feedback to "WEEK {week}: LISTENED".
   - Standardize test fixtures and mocks to use "Test Release" in place of "Test Album".

## User Stories

1. As a DJ auditioning a 65 BPM downtempo track, I want the tempo analyzer to report 65 BPM rather than artificially doubling it to 130 BPM, so that the musical tempo reflects the genuine groove.
2. As a curator listening to a 174 BPM drum & bass release, I want the tempo analyzer to preserve 174 BPM rather than cutting it in half to 87 BPM, so that the high-energy pacing is maintained.
3. As a user adjusting BPM, I want both the frontend and backend to enforce the same 40.0 to 300.0 BPM boundary, so that I experience predictable validation regardless of the entry point.
4. As a user viewing a release with an existing BPM, I want the panel button to clearly indicate "🔄 重新分析目前曲目 BPM", so that I understand clicking it will re-evaluate the audio.
5. As a curator auditing tempo adjustments, I want the "確認儲存至資料庫" button to appear only when I have actually adjusted the value, so that I do not accidentally re-save unchanged data.
6. As a listener scrubbing through tracks, I want to see "⚡ 分析中..." with a pulsing animation while the audio is being analyzed, so that I have clear visual feedback that calculation is underway.
7. As a curator looking at the player capsule, I want the asterisk badge (`124* BPM`) to signal when my staged BPM has not yet been committed to the database, so that I do not forget to save my work.
8. As a user browsing the weekly timeline, I want the weekly triage button to feature a perfectly circular outline, so that it matches the circular design language of the vinyl hub.
9. As a music curator reading the interface, I want all labels to consistently refer to "曲目" rather than "歌曲", so that terminology strictly adheres to the project domain model.
10. As a power user marking a week as listened, I want the HUD notification to announce "LISTENED", reinforcing the curation state machine conventions.

## Implementation Decisions

- **Tempo Normalization & Validation Decision**:
  - The Web Audio autocorrelation analyzer normalizes tempo via `while (bpm < 60) bpm *= 2; while (bpm > 180) bpm /= 2;`.
  - The API endpoint `PATCH /api/releases/{release_id}/bpm` validates `payload.bpm < 40.0 or payload.bpm > 300.0` and raises HTTP 400.
  - The frontend edit mode enforces numeric bounds of `min="40" max="300"`.

- **BPM State Machine Decision**:
  - A helper evaluates whether an active Release has an existing valid BPM and whether the staged value differs from the database record.
  - Button text alternates between "🔍 自動分析目前曲目 BPM" and "🔄 重新分析目前曲目 BPM".
  - During processing, button disabled state is applied, icon becomes "⚡", and text displays "分析中..." with Tailwind `animate-pulse`.
  - The save button container is conditionally rendered or given class `hidden` unless `stagedBpm !== null && (!activeRelease || activeRelease.bpm !== stagedBpm)`.

- **Weekly Header Icon Button Geometry Decision**:
  - The button element in `renderAccordion` applies `p-1.5 rounded-full border` instead of `rounded-lg`.

- **Domain Terminology Decision**:
  - Replace all user-facing instances of "歌曲" with "曲目" in `index.html`.
  - Update `markWeekAllListened` HUD call to emit `LISTENED`.
  - Rename test fixture descriptions across test suites from "Album" to "Release".

## Testing Decisions

- **What makes a good test**:
  - Test external API boundaries and HTTP responses under edge conditions (e.g. BPM values of 39.9, 40.0, 300.0, 300.1).
  - Verify template output reflects the circular button styling, updated domain terms, and state-driven save button presence.
- **Modules to be tested**:
  - `app/routers/api.py`: `test_patch_release_bpm_validation` verifies 40.0 to 300.0 bounds.
  - `app/templates/index.html`: template string checks for `rounded-full` on weekly header button, `曲目` terminology, and 60–180 BPM normalization range.
  - `tests/test_ui_refinements.py` & `tests/test_bpm_analyzer_and_proxy.py`: updated fixtures and assertions.
- **Prior Art**:
  - `tests/test_audio_resilience_and_bpm.py`: existing validation and resilience test suites.

## Out of Scope

- Modifying the underlying SQLite schema or adding new database columns.
- Altering the Web Audio filter frequency cutoff or autocorrelation sampling rate.
- Introducing multi-track batch tempo analysis.

## Further Notes

- All changes represent targeted refinements adhering to feedback from the Standards and Spec axes, maintaining total compatibility with existing client workflows.
