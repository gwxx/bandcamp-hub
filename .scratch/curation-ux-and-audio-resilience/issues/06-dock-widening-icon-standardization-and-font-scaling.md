# 06: Player Dock Widening, Iconographic Standardization, and Typography Scaling

**What to build:**
Refine visual ergonomics and typography across the hub. The player dock capsule container expands to `max-w-5xl` (1024px) with `px-6 py-2.5` padding, giving right-side controls plenty of breathing room. Replace text-heavy buttons with modern icons: official Bandcamp parallelogram SVG logo for external links, circular checkmark icon (`○` unlistened / `✓` cyan listened) for curation toggle, and pure star `⭐` for the header starred filter. Scale up typography by one degree across all tiers for enhanced legibility.

**Blocked by:** 04: DJ Tempo Control, Live Pitch Shifting, and BPM Persistence

**Status:** closed

- [x] `#player-dock` maximum width expanded to `max-w-5xl` with `px-6` padding, eliminating clipping on rightmost icons
- [x] Bandcamp external links on player dock, card bottom, and cover badges use the official Bandcamp parallelogram SVG icon
- [x] Listened toggle buttons use single circular icons (`○` unlistened / `✓` listened) with tooltip hints
- [x] Top header Starred filter displays as a pure icon `⭐`
- [x] All typography classes increased by one size step across micro-labels, body text, buttons, and headings
