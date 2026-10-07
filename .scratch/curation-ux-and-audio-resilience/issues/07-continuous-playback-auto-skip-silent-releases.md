# 07: Continuous Playback Auto-Skipping Across Silent Releases

**What to build:**
When continuous playback or the "Next" action advances across releases, releases that contain zero streamable preview audio are automatically skipped. The playback engine searches forward in sequence until it finds the next release that contains at least one playable track, starts playing its first playable track, and smoothly scrolls the newly active card into view.

**Blocked by:** 03: Track Stream Isolation, 0:00 Duration Fix, and Non-Blocking Unstreamable Alert, 05: Album Jacket Store Navigation & Persistent Audition History Dimming

**Status:** closed

- [x] Advancing to the next release checks if the target release has at least one streamable track
- [x] If target release is entirely unstreamable, the player automatically iterates forward to the next playable release
- [x] First playable track of the resolved release begins playing immediately
- [x] The active release card smoothly scrolls into view in the main window
- [x] Loop and shuffle navigation modes respect the unstreamable auto-skip rule
