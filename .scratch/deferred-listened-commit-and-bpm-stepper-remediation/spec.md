# Spec: Deferred Listened Commit, BPM Stepper Realignment, and Domain Standards

Status: implemented

## Problem Statement

When users listen to music in the default "Unlistened-First" view, the playback engine automatically marks a release as listened once playback reaches the 30-second mark. This triggers an immediate background data refetch and DOM reconstruction. Because the release is now marked as listened, it is instantly pruned from the unlistened list while still playing. This causes severe UX disruptions:
1. The currently playing release card abruptly vanishes from the screen in mid-playback.
2. The keyboard navigation selection index is disrupted, causing keyboard focus to jump unexpectedly to a completely different release card.
3. Clicking the release title link in the bottom-docked player fails to jump back to the card in the main stream because the DOM anchor has been unmounted.
4. Users cannot easily access the multi-track drawer or tracklist of the release they are currently enjoying without manually switching filter tabs.

Additionally, three secondary usability and architectural issues were identified:
- The tempo adjustment stepper buttons in the DJ panel adjust playback speed by percentage (`-1%`, `+1%`) rather than absolute BPM increments, which contradicts DJ standard workflow where tempo is matched in precise BPM steps.
- When opening manual BPM edit mode, focus management fails to protect against input trapping, so typing or clicking in the numeric input field can intercept or block subsequent keyboard `T` key Tap tempo inputs.
- Residual occurrences of the forbidden domain term "專輯" (Album) persist in code comments, and regression tests lack a global negative guardrail.

## Solution

1. **Deferred Listened Commit Mechanism**:
   - Defer the removal of playing releases from the active view. When a track passes the 30-second listening threshold, the system records that the release has met the listening criteria in memory without immediately refetching the stream or destroying DOM elements.
   - The listened state is committed to the database and the unlistened stream refreshed only when playback transitions away to a different release (via auto-play advance, playlist navigation, or manual card selection).
   - Switching tracks within the same multi-track release never triggers commit or stream refresh.
   - If the player is closed or the browser tab unloaded after meeting the threshold, the pending listened status is committed cleanly in the background.
   - Manual `L` keypresses or dock button clicks update the release status immediately, but the card remains anchored on-screen with an updated listened visual style (dimmed opacity and checkmark) until navigation to another release occurs.

2. **Absolute BPM Pitch Stepper**:
   - Replace percentage-based stepper controls with `[-1 BPM]`, `[原速 (1.0x)]`, and `[+1 BPM]` controls.
   - Each click adjusts effective playback speed by exactly `±1.0 BPM` by dynamically calculating the required Web Audio playback rate relative to the release's base BPM.
   - If a release has no established base BPM, fall back gracefully to a standard reference baseline of 120.0 BPM, displaying a clear reference indicator to the user.
   - Eliminate percentage units from pitch controls, titles, and HUD notices, presenting all tempo adjustments in BPM.

3. **Tap Tempo Focus Lock and Input Guard**:
   - Automatically assign and retain focus on the Tap Tempo button when entering edit mode or tapping.
   - Attach a defensive keyboard listener to the numeric input field so pressing the `T` key automatically blurs the input field, transfers focus to the Tap button, and triggers tap tempo calculation without key interference.

4. **Global Domain Vocabulary Cleansing**:
   - Eradicate all remaining instances of the forbidden term "專輯" (Album) from template comments, replacing them with canonical domain terms ("發行" / "Release").
   - Upgrade regression test suites with a global negative assertion guaranteeing that "專輯" never appears in user-facing templates.

5. **Test Suite Hygiene and Deduplication**:
   - Hoist repeated regular expression imports to module scope and remove duplicated normalization loop assertions across test cases.

## User Stories

1. As a listener browsing unlistened music, I want the currently playing release card to stay visible on the screen even after passing 30 seconds of playback, so that my view does not suddenly disappear while I am enjoying the track.
2. As a listener using keyboard shortcuts (J/K), I want my card selection focus to remain locked to the currently playing release, so that the cursor does not jump to a random release in mid-playback.
3. As a listener using the bottom-docked player, I want clicking the release title link to reliably scroll back to the active release card in the stream, so that I can inspect album artwork and notes whenever I want.
4. As a listener playing a multi-track release, I want moving between tracks 1, 2, and 3 of the same release to keep the release firmly anchored in the unlistened list, so that the album is not prematurely dismissed.
5. As a listener who finishes or skips to the next release, I want the previous release to be officially committed as listened and archived from the unlistened filter upon the transition, so that my inbox remains clean.
6. As a listener who closes the player after listening to a full track, I want the release to be saved as listened upon player exit, so that my listening progress is preserved even if I don't queue another song.
7. As a listener closing or refreshing the tab, I want any release that surpassed the 30-second threshold to be committed in the background, so that my listened history is never lost.
8. As a listener who manually presses the `L` key on the currently playing release, I want the card to reflect the listened visual styling without instantly disappearing, so that I can finish listening without my interface resetting.
9. As a DJ preparing a mix, I want the tempo stepper buttons to adjust speed by exactly `+1 BPM` and `-1 BPM`, so that I can match beats using actual tempo values rather than abstract percentages.
10. As a DJ adjusting pitch on a 124 BPM house track, I want clicking `+1 BPM` to increase the speed to exactly 125.0 BPM, so that the tempo corresponds directly to standard DJ equipment.
11. As a DJ adjusting pitch on a track whose BPM has not yet been analyzed, I want the system to calculate `±1 BPM` against a standard 120.0 BPM reference, so that I can still adjust tempo smoothly without errors.
12. As a DJ glancing at the HUD notifications while adjusting speed, I want the HUD to report `SPEED: 125.0 BPM (+1.0 BPM)` instead of percentages, so that I receive immediate, actionable tempo feedback.
13. As a DJ clicking "Edit" to customize BPM, I want keyboard focus to land on the Tap Tempo button by default, so that I can immediately press `T` to tap the rhythm.
14. As a DJ who accidentally clicks into the numeric BPM text input, I want pressing `T` to automatically blur the text field and register a tempo tap, so that I am never locked out of keyboard tapping.
15. As a DJ tapping tempo repeatedly, I want focus to remain securely on the Tap button after each tap, so that rapid successive keypresses are seamlessly recorded.
16. As an open-source contributor, I want code comments and templates to use the canonical domain term "發行 (Release)" exclusively, so that terminology strictly adheres to the project domain model.
17. As a developer running unit tests, I want the test suite to assert that the term "專輯" does not appear anywhere in template markup or comments, so that regressions are caught before deployment.
18. As a developer maintaining the test suite, I want test imports and assertions to be clean and deduplicated, so that test runs are efficient and straightforward to read.

## Implementation Decisions

### 1. Deferred Listened Commit Architecture
- Introduce a pending commit tracking state in the player runtime (`pendingListenedReleaseId = null`).
- In the 30-second listening threshold callback:
  - If the active release is unlistened, record `pendingListenedReleaseId = activeRelease.id`.
  - Do NOT trigger stream refetching or DOM re-rendering.
  - Optionally update the docked player listen button state to indicate completion.
- In `playRelease(newRel)`:
  - Check whether `pendingListenedReleaseId` is set and differs from `newRel.id`.
  - If a previous release is pending commit, asynchronously send the `PATCH /api/releases/{id}/listened` request and trigger state synchronization before switching active releases.
  - Reset `pendingListenedReleaseId = null`.
- In `closePlayer()` and window `beforeunload` event handlers:
  - If `pendingListenedReleaseId` is non-null, fire the listened commit to ensure no listened state is lost when the session ends.
- In `toggleListen(id)`:
  - When the user manually toggles the active playing release, persist the status to the backend.
  - If viewing the unlistened filter, update the on-screen card's CSS class to the listened style (e.g. 55% opacity and checkmark badge) without purging the card element from the DOM until navigation away occurs.

### 2. Absolute BPM Pitch Stepper & Reference Fallback
- Replace the pitch stepper buttons:
  - Label decrement button as `[-1 BPM]`.
  - Label center button as `[原速 (1.0x)]` (resets rate to 1.0).
  - Label increment button as `[+1 BPM]`.
- Define the tempo calculation helper:
  - Retrieve current base BPM from staged BPM or release metadata. If neither is available, use a fallback reference base of `120.0 BPM`.
  - Calculate `currentEffectiveBpm = baseBpm * currentPitch`.
  - On nudge: `targetEffectiveBpm = currentEffectiveBpm + deltaBpm`.
  - Set `newPitch = targetEffectiveBpm / baseBpm`.
  - Clamp `newPitch` to the safe playback rate boundaries (0.80x to 1.20x).
  - Update `audio.playbackRate`, pitch slider position, and UI labels.
- Format pitch display label as `速度微調: +X.X BPM (X.XXx)` (or `-X.X BPM (X.XXx)`). If using fallback base, append `(以 120 為基準)`.
- Format HUD notification string as `SPEED: {effBpm} BPM ({deltaBpm >= 0 ? '+' : ''}{deltaBpm} BPM)`.

### 3. Tap Tempo Defensive Focus Management
- When opening manual edit mode, explicitly invoke focus on the Tap Tempo button element.
- In the tap tempo handler, maintain focus on the Tap Tempo button.
- Add an event listener to the custom BPM numeric input: on `keydown`, if the key is `t` or `T`, prevent default event propagation, blur the input element, set focus to the Tap button, and call the tap tempo handler.

### 4. Domain Glossary Enforcement
- Clean all remaining template comments containing "專輯", replacing them with "發行".
- In the test suite, replace localized negative assertions with a global negative assertion against "專輯" across the entire template content.

### 5. Test Suite Refactoring
- Move `import re` statements to the module header of the UI refinement test suite.
- Remove duplicate assertions of BPM normalization while-loops.

## Testing Decisions

- **Behavior Over Implementation**: Tests assert observable user interactions, DOM contract IDs, button text labels, and HTTP endpoints rather than internal JavaScript variable names.
- **Modules Tested**:
  - `app/templates/index.html`: Verified for presence of `-1 BPM` / `+1 BPM` buttons, absence of `%` in stepper controls, defensive focus handlers, deferred commit hooks, and absence of forbidden glossary terms.
  - `tests/test_ui_refinements.py`: Enhanced with test cases for deferred commit mechanics, absolute BPM stepper math, focus defense, and global glossary negative assertions.
- **Prior Art**:
  - Follows established patterns in `tests/test_ui_refinements.py` (TestUIRefinements) and `tests/test_sync_pipeline.py`.

## Out of Scope

- Changing the backend database schema or API routes for release listening status (the existing `PATCH /api/releases/{id}/listened` endpoint is preserved).
- Altering the Web Audio DSP autocorrelation algorithms or filter parameters developed in the previous iteration.
- Adding playlist queuing or custom playlist reordering.

## Further Notes

- The deferred commit architecture directly preserves DOM identity during playback, ensuring seamless integration between the linear timeline view, multi-track drawer, and bottom-docked player.
