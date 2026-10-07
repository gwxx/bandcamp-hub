# 05: Album Jacket Store Navigation & Persistent Audition History Dimming

**What to build:**
Clicking the vinyl jacket cover image navigates directly to the release page on Bandcamp in a new browser tab. Audio playback remains triggered by clicking the card body, album title, or individual tracks. Individual tracks that have been auditioned are stored in `localStorage` and automatically rendered with dimmed dark grey styling (`text-zinc-500 opacity-60`), without visual checkmark prefixes, persisting across page reloads.

**Blocked by:** 03: Track Stream Isolation, 0:00 Duration Fix, and Non-Blocking Unstreamable Alert

**Status:** closed

- [x] Clicking the album jacket opens the canonical Bandcamp URL in a new tab without triggering card audio playback
- [x] Hover overlay on jacket presents a clean Bandcamp external link affordance instead of a play button
- [x] Clicking card title, artist, or card body starts release audio playback smoothly
- [x] When a track plays, its audition state is recorded in `localStorage`
- [x] Previously auditioned tracks render in dimmed dark grey styling (`text-zinc-500 opacity-60`) without adding checkmark characters
