# 04: Deferred Listened Commit and Anchor Stabilization

**What to build:**
Implement the deferred listened commit mechanism to eliminate stream refetching and DOM destruction during active release playback. When playback exceeds the 30-second threshold, record `pendingListenedReleaseId = rel.id` in memory without calling `fetchReleases()` or unmounting cards. Defer committing the status to the backend until playback transitions away to a different release (in `playRelease` or `playNextTrack`). Switching between tracks within the same multi-track release never commits or unmounts the release. Ensure pending listened states are committed when exiting the player (`closePlayer()`) or closing the tab (`beforeunload`). If the user manually toggles listening via the `L` key or dock button during playback, persist status immediately but keep the active card visible with a dimmed (55% opacity) listened style until the user navigates to another release.

**Blocked by:** 01-domain-glossary-cleansing-and-test-hygiene

**Status:** resolved

- [x] Reaching the 30-second playback threshold sets `pendingListenedReleaseId = rel.id` without triggering `fetchReleases()` or removing the card in the unlistened filter
- [x] Transitioning to a different release (`newRel.id !== activeRelease.id`) in `playRelease()` commits the pending listened status via `PATCH /api/releases/{id}/listened` and refreshes the unlistened stream
- [x] Multi-track navigation within the same release (`rel.id === activeRelease.id`) does not trigger commit or unmount the release card
- [x] `closePlayer()` and window `beforeunload` execute background commit if `pendingListenedReleaseId` is non-null
- [x] Manual `L` keypresses or dock button clicks update the active release's visual style (55% opacity, checkmark) without abruptly unmounting the card from the DOM
- [x] Automated regression tests in `tests/test_ui_refinements.py` assert presence of deferred commit tracking, clean cross-release transition hooks, and player close handlers
- [x] All tests in `tests/test_ui_refinements.py` and full project suite pass cleanly
