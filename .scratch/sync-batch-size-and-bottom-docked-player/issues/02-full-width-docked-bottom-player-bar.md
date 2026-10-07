# 02: Full-Width Docked Bottom Player Bar

**What to build:**
Transform the player dock from a cramped, floating capsule into a full-width bottom docked bar fixed to the bottom of the viewport (`bottom-0`, `w-full`). Decompress the horizontal space so that the track/artist title column expands to 320px (`max-w-xs`), preventing premature truncation, and the central transport and timeline area expands to `max-w-4xl flex-1` for smooth scrubbing and tempo interaction. Ensure the main content and pagination containers include sufficient bottom clearance (`pb-28`) so that content is never obscured when scrolled to the bottom.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] `#player-dock` is converted to an edge-to-edge docked bar at `fixed bottom-0 inset-x-0 w-full z-50` with top border framing and backdrop blur (`border-t border-studio-border bg-studio-900/95 backdrop-blur-xl shadow-2xl`).
- [x] Outer floating margins (`bottom-6`, `rounded-full`, `max-w-7xl`) are removed in favor of a container (`w-full max-w-[1600px] mx-auto px-6 py-3`).
- [x] Left track information container expands from `max-w-[220px]` to `max-w-xs` (320px).
- [x] Center transport and timeline progress bar container removes `max-w-2xl` and expands to `max-w-4xl flex-1`.
- [x] Right-hand utility buttons (shuffle, loop, volume slider, star, listened, external link) remain comfortably aligned without wrapping or crowding.
- [x] Show/hide slide animations smoothly toggle using `translate-y-full` when closed and `translate-y-0` when active.
- [x] Main page content area (`#main-content`, `#load-more-container`) maintains `pb-28` to `pb-32` clearance to prevent release cards from being occluded.
- [x] Automated tests in `tests/test_ui_refinements.py` verify the updated layout classes and geometry.

## Comments
- Implemented edge-to-edge fixed bottom bar layout in `app/templates/index.html`.
- Expanded track info container to `max-w-xs` and center controls to `max-w-4xl flex-1`.
- Verified layout and regression tests in `tests/test_ui_refinements.py`.
