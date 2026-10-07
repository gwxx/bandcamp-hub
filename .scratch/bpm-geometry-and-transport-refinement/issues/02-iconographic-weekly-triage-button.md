# 02: Iconographic Weekly Triage Button

**What to build:**
Upgrade the weekly section header's "mark all as listened" action from plain text ("✓ 一鍵已聽") into an icon-first button conforming to the design language of Release cards and the player dock. It displays a border-framed circular button with `ICON_UNCHECKED` when unlistened releases remain in the week, and transitions to illuminated `ICON_CHECKED` when the week is fully listened, accompanied by an informative tooltip.

**Blocked by:** None (can start immediately)

**Status:** closed

- [x] Weekly section header replaces plain text button with a rounded border icon button (`p-1.5 rounded-lg border`)
- [x] Displays `ICON_UNCHECKED` when `unlistenedInWeek > 0`
- [x] Displays `ICON_CHECKED` with illuminated styling when `unlistenedInWeek === 0`
- [x] Clicking the icon triggers `markWeekAllListened(group.week)` to mark all releases in that week as listened
- [x] Includes `title="將本週全部標記為已聽"` for clear hover guidance
