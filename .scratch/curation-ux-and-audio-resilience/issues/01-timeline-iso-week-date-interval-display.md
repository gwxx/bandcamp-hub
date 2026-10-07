# 01: Timeline ISO Week Date Interval Display

**What to build:**
Every Weekly Digest header and the sidebar timeline must dynamically surface the calendar date interval (Monday through Sunday) corresponding to its ISO Week identifier. The main digest header renders `YYYY-Www (YYYY-MM-DD ~ YYYY-MM-DD)` while the sidebar timeline renders a compact `YYYY-Www (MM/DD - MM/DD)` to preserve sidebar spacing.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Main digest headers display the full ISO calendar date interval `(YYYY-MM-DD ~ YYYY-MM-DD)` alongside the ISO Week number
- [x] Sidebar timeline items display the compact date interval `(MM/DD - MM/DD)`
- [x] Date intervals calculate accurately across leap years and year-boundary weeks
- [x] Typography and layout remain aligned and responsive without text wrapping glitches
