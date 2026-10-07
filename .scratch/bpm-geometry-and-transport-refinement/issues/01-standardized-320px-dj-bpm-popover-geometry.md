# 01: Standardized 320px DJ BPM Popover Geometry

**What to build:**
Configure the DJ BPM popover panel container to a standardized fixed width of 320px (`w-80`). The popover immediately opens with this stable geometry matching the post-analysis staging and edit controls, completely eliminating dimensional snapping, layout jumping, or cramped layouts when initially opened.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] `#bpm-panel` container styled with fixed width of 320px (`w-80` / 20rem)
- [x] Initial state displaying "自動分析目前歌曲 BPM" and the speed slider renders comfortably within 320px
- [x] Staging state (`[-2]`, BPM value, `[+2]`, `[✏️ Edit]`, `[確認儲存]`) fits seamlessly without expanding or altering panel width
- [x] Manual edit mode (`custom-bpm-input`) aligns neatly with action buttons inside the 320px container
- [x] Panel opens and closes smoothly with zero width jumping or jitter
