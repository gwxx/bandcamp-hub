# Spec: BPM Panel Geometry, Weekly Triage Iconography, and Transport Button Scaling

Status: ready-for-agent

## Problem Statement

When users audition releases and curate music in the application, three visual and ergonomic friction points impede a seamless workflow:

1. **BPM Popover Geometry Inconsistency**: Opening the DJ BPM popover initially causes the panel to render at a narrow, constrained width (~240px) because it only encompasses the initial analysis button and slider. Once tempo analysis completes and the staging control bar (`[-2]`, BPM value, `[+2]`, `[Edit]`) appears, the popover suddenly snaps wider to 320px. This abrupt dimensional shift feels unpolished, jarring, and causes visual jumping.
2. **Weekly Triage Button Inconsistency**: At the top right of each weekly section header, the "mark all as listened" action is currently represented as plain text ("✓ 一鍵已聽"). This contrasts sharply with the sleek vinyl studio iconography used throughout Release cards and the player dock (which feature circular border-framed check icons), creating visual disjointedness.
3. **Transport Seek Hitbox & Legibility**: The 10-second rewind (`-10s`) and fast-forward (`+10s`) pill buttons in the floating player dock are currently compact (`h-7`, 28px height, `text-xs` 12px font). While functional, their click hitboxes feel undersized and difficult to target rapidly compared to the enlarged primary transport and play controls.

## Solution

1. **Standardized 320px BPM Popover Baseline**: Fix the popover container width to a stable 320px (`w-80`). The popover immediately opens with the exact spacious width matching the post-analysis staging layout, eliminating dimension shifting and layout jumps across all analysis, editing, and pitch-shifting states.
2. **Iconographic Weekly Triage Button**: Transform the weekly "mark all listened" action into an icon-first button conforming to the design language of Release cards and the player dock. It displays a circular border button: when the week contains unlistened releases, it shows an open circle icon (`ICON_UNCHECKED`) with a tooltip ("一鍵標記本週全部已聽"); upon click or when all releases in the week are listened, it illuminates with the checked circle icon (`ICON_CHECKED`), providing immediate visual gratification.
3. **Enlarged Two-Step Transport Pill Buttons**: Scale up the 10-second rewind and fast-forward buttons by two increments. The pill height increases from 28px (`h-7`) to 36px (`h-9`), padding expands to `px-3`, and the font/glyph size increases from `text-xs` (12px) to `text-sm font-bold` (14px bold). This substantially expands the touch/click target area and enhances visual clarity.

## User Stories

1. As a DJ auditioning tracks, I want the BPM panel to open at a spacious 320px from the very first click, so that the panel does not jump in width when the analysis completes.
2. As a curator browsing music, I want the weekly section header's "mark all listened" button to share the same iconography as the Release cards, so that the application maintains a cohesive visual identity.
3. As a listener scrubbing through a long mix or track, I want the 10-second rewind and fast-forward buttons to have larger hitboxes and clearer typography, so that I can click them effortlessly without misclicking adjacent controls.
4. As a power user rapidly triaging weekly releases, I want the weekly triage icon button to display an open circle when unlistened releases remain, so that I can instantly discern which weeks still need curation.
5. As a power user, I want the weekly triage icon button to display a vibrant checked icon once all releases in that week are listened, so that I feel a clear sense of progress and completion.
6. As a user on a laptop touchpad or touchscreen, I want the 36px height on the 10-second skip buttons, so that I have a comfortable target that avoids triggering accidental seeks.
7. As a curator manually adjusting tempo, I want the manual edit mode in the BPM panel to fit comfortably within the 320px container without horizontal scrolling or wrapping, so that the numeric input and action buttons remain aligned.
8. As a desktop user navigating with a mouse, I want helpful tooltip text on the weekly triage icon button, so that the icon's purpose is immediately self-evident before clicking.
9. As a music lover monitoring audio playback, I want the 10-second transport controls to visually harmonize with the surrounding playback buttons (`w-11 h-11` play button and `w-5 h-5` track skip buttons), maintaining aesthetic balance in the player dock.
10. As a user who frequently opens and closes the DJ BPM panel, I want the popover to animate smoothly without horizontal resizing jitter, so that the interface feels responsive and sturdy.

## Implementation Decisions

- **Fixed Popover Width Specification**:
  - The popover panel container adopts a fixed width of 320px (`w-80` / 20rem).
  - Internal sections (base BPM analysis button, staged adjustment review row, custom manual input mode, and real-time pitch slider) take full width of the parent container without exceeding 320px.
  - The staging display container and manual edit container toggle display modes smoothly within this fixed geometry.

- **Weekly Triage Iconography Specification**:
  - The weekly section header replaces text "✓ 一鍵已聽" with a rounded button container (`p-1.5 rounded-lg border`).
  - When `unlistenedInWeek > 0`, the button renders the unlistened circular SVG icon (`ICON_UNCHECKED`) with muted border styling and hover accent.
  - When `unlistenedInWeek === 0`, the button renders the listened checked circular SVG icon (`ICON_CHECKED`) with active border styling.
  - The button retains `onclick="markWeekAllListened(weekStr)"` and includes `title="將本週全部標記為已聽"` for accessibility and hover guidance.

- **Transport Button Dimensions Specification**:
  - Rewind 10s and fast-forward 10s buttons maintain the capsule pill shape (`rounded-full`).
  - Height increases from 28px (`h-7`) to 36px (`h-9`), and horizontal padding increases from `px-2` to `px-3`.
  - Content labels scale up to `text-sm font-bold` (14px bold), keeping glyphs (`⏪`, `⏩`) and digits (`10`) crisply aligned.
  - Flexible layout within the transport button group preserves 6px (`space-x-1.5`) spacing without wrapping or crowding adjacent buttons.

## Testing Decisions

- **What makes a good test**:
  - Verify observable DOM properties and user-facing behavior rather than ephemeral internal styling.
  - Verify that the bulk-listened endpoint `/api/releases/bulk-listened` functions idempotently and updates the curation state for all releases in an ISO Week.
  - Verify that client templates output stable element classes and appropriate accessibility attributes (tooltips, SVG icons, button dimensions).
- **Modules to be tested**:
  - Backend API: `app/routers/api.py` (bulk listened endpoint regression verification).
  - Frontend Template: `app/templates/index.html` (BPM popover width class, weekly header triage icon button, 10s button geometry).
- **Prior Art**:
  - `tests/test_audio_resilience_and_bpm.py`: Unit and endpoint test patterns for release actions and BPM PATCH operations.
  - `tests/test_bpm_analyzer_and_proxy.py`: Stream proxy and tempo endpoints.

## Out of Scope

- Introducing customizable skip intervals (e.g. 5s, 15s, 30s) beyond the standard 10-second step.
- Adding undo functionality or two-way unlistening to the weekly bulk-listened action.
- Resizing the main play/pause button or the track skip buttons beyond their recently established scale.

## Further Notes

- All changes are purely frontend ergonomic and visual enhancements, maintaining 100% backwards compatibility with existing backend models, SQLite schemas, and API contracts.
