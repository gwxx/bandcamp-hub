# 01: Player Dock Geometry Widening and Edge Margin Protection

**What to build:**
Expand the floating vinyl capsule player `#player-dock` maximum width to `1280px` (`max-w-7xl`) and enlarge internal capsule padding to `px-8 py-3`. The outer rightmost Bandcamp logo and all utility buttons are fully protected with ample margin from the capsule's curved border radius (`rounded-full`), completely eliminating clipping, squeezing, and overflowing.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] `#player-dock` width container expanded to `max-w-7xl` (`1280px`) with responsive fluid width
- [x] Inner capsule padding set to `px-8 py-3`, providing a generous 32px safety clearance from pill curve ends
- [x] Rightmost Bandcamp external link icon preserves at least 24px of clearance from the curved capsule edge without clipping
- [x] Middle transport and progress container adapts smoothly to the wider layout without visual gaps
