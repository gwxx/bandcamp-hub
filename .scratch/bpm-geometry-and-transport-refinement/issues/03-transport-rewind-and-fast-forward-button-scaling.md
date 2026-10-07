# 03: Transport Rewind and Fast-Forward Button Scaling

**What to build:**
Scale up the 10-second rewind (`-10s`) and fast-forward (`+10s`) transport pill buttons in the floating player dock by two increments. Enlarge height from 28px (`h-7`) to 36px (`h-9`), horizontal padding from `px-2` to `px-3`, and font/glyph size from `text-xs` (12px) to `text-sm font-bold` (14px bold). This substantially expands the touch and click hitboxes, improves instant legibility, and harmonizes with the enlarged primary play controls.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Rewind 10s button scaled to `h-9 px-3 text-sm font-bold flex items-center justify-center gap-1`
- [x] Fast-forward 10s button scaled to `h-9 px-3 text-sm font-bold flex items-center justify-center gap-1`
- [x] Visual harmony preserved with adjacent track skip (`w-5 h-5`) and central play (`w-11 h-11`) buttons without layout wrapping
- [x] Click event listeners `seekRelative(-10)` and `seekRelative(10)` remain fully functional and responsive
