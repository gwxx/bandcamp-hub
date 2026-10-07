# Spec: Configurable Sync Batch Size and Docked Bottom Player Layout

Status: ready-for-agent

## Problem Statement

When users discover and curate music using Bandcamp Hub, they encounter two primary friction points that impede efficiency and comfort:

1. **Slow and Monolithic Sync Pipeline**:
   - The current incremental synchronization pipeline hardcodes a limit of 200 Gmail notification messages.
   - For every single email, the system retrieves full payload data, parses HTML, extracts Bandcamp links, and reverse-scrapes track metadata and streaming URLs.
   - Processing 200 notifications sequentially takes several minutes. Users who only want a rapid daily check of recent releases are forced to endure an excessively long wait, with no way to choose a faster, smaller batch size (e.g. 20 or 50 releases).

2. **Cramped and Obscuring Floating Player Capsule**:
   - The audio player is designed as a floating capsule centered with margins above the viewport bottom edge (`bottom-6`, `max-w-7xl`, `rounded-full`).
   - The center transport and timeline section is capped at a narrow width (`max-w-2xl`), while the track and artist title column is restricted to `max-w-[220px]`.
   - On typical laptop screens (1280px–1440px wide), the numerous controls (10s seek buttons, track skip, play/pause, 1/3-1/2-2/3 cue triggers, DJ BPM pill, time indicators, volume slider, star, and listened toggles) squeeze the timeline progress bar down to an unusable sliver, while long release or track titles get truncated prematurely. Furthermore, floating above the bottom margin takes up valuable viewport area without utilizing the full horizontal breadth of the screen.

## Solution

1. **Configurable Sync Batch Size Selection**:
   - Introduce a batch size selector dropdown adjacent to the "立即同步" (Instant Sync) button in the header.
   - Provide presets for `20`, `50` (system default), `100`, and `200` notifications.
   - Remember user preference across sessions using browser local storage.
   - Pass the chosen batch limit through the Server-Sent Events (SSE) synchronization endpoint to the backend Gmail querying pipeline.
   - Advance the incremental `sync_watermark` to the current time, and if the number of matching candidate messages reaches the selected batch cap, append a considerate reminder in the completion notification advising the user that more historical notifications may exist in Gmail and can be retrieved via the 30-day force rescan feature.
   - Keep the "強制重新掃描 30 天" (Force Rescan 30 Days) action in settings anchored to a thorough 200-message ceiling.

2. **Full-Width Docked Bottom Player Bar**:
   - Restructure the player from a floating capsule into an edge-to-edge docked bottom bar (`bottom-0`, `w-full`) inspired by modern desktop music streaming applications.
   - Style with top border framing, subtle backdrop blur, and dark studio aesthetic.
   - Maximize horizontal space distribution:
     - Expand the track information container to `max-w-xs` (320px), preventing premature title truncation.
     - Expand the center transport, DJ cue controls, and timeline progress bar to `max-w-4xl flex-1`, providing ample room for scrubbing and tempo inspection.
     - Retain generous spacing for right-hand utility controls (shuffle, loop, volume slider, star, listened status, external link).
   - Ensure the multi-track drawer floats centered above the docked bar (`max-w-5xl mx-auto mb-2`) with rounded corners and backdrop blur for comfortable reading.
   - Ensure the DJ BPM tempo popover opens upwards (`bottom-full mb-3`) seamlessly above the bar.
   - Add sufficient bottom padding to the main viewport content area so no cards or pagination controls are obscured when scrolled to the bottom.

## User Stories

1. As a daily music curator, I want to select a fast batch of 20 or 50 releases when running an instant sync, so that I can see the latest additions in seconds rather than waiting several minutes.
2. As a weekend power user, I want the option to select 100 or 200 releases, so that I can perform a comprehensive ingestion of all accumulated notifications.
3. As a user, I want my selected batch size preference to be remembered when I refresh or revisit the application, so that I do not need to reselect my preferred setting every time.
4. As a user triggering a sync, I want the system default batch size to be 50, so that I receive an optimal balance of discovery volume and Gmail API round-trip responsiveness.
5. As a curator, when a sync batch reaches the selected cap, I want a clear completion notification explaining that older notifications remain and can be ingested via the 30-day force rescan, so that I never wonder whether older emails were silently skipped.
6. As a user performing a 30-day force rescan from the settings modal, I want it to always scan up to the full 200-message capacity, so that historical recovery remains deep and comprehensive.
7. As a listener using a 13-inch or 15-inch laptop, I want the player bar to be docked edge-to-edge across the bottom of the screen, so that horizontal space is maximized and controls do not look cramped.
8. As a DJ scrubbing through a track, I want the timeline progress bar to have a wide, comfortable horizontal span, so that I can seek to precise song sections with confidence.
9. As a music lover reading long track or album titles, I want the title column to accommodate up to 320px, so that rich titles are not clipped after only a few characters.
10. As a listener auditioning multi-track releases, I want the multi-track drawer to open centered above the bottom player bar at a focused reading width (max-w-5xl), so that track titles remain legible and cohesive.
11. As a DJ adjusting track tempo, I want the BPM panel to pop up cleanly above the docked player bar, so that pitch sliders and tempo analysis controls are easy to manipulate without covering transport buttons.
12. As a user browsing the bottom of the release list, I want the page to provide bottom spacing so that the last release cards and the "Load More" button are fully visible above the docked player bar.
13. As a user who closes the player, I want the player bar to slide downwards smoothly out of view, and slide back up when a new track starts playing.

## Implementation Decisions

- **Sync Pipeline & API Layer**:
  - The synchronization pipeline accepts an optional `limit` integer parameter (default 50).
  - The Gmail message fetching procedure passes `limit` as the `max_cap` boundary.
  - The SSE endpoint `/api/sync/stream` accepts `limit: int = 50` and passes it through to the pipeline.
  - When `force_rescan` is True, the limit is unconditionally overridden to 200.
  - When `total_msgs >= limit`, the pipeline appends an informative note to the completion payload: `"同步完成！已收納/更新 X 首作品（已達單次上限 Y 封；若需補齊更早歷史可至設定執行強制重掃）"`.
  - Incremental `sync_watermark` continues to record the current UTC timestamp upon successful completion.

- **Header Batch Selector UI**:
  - A stylized select element is placed immediately preceding the "立即同步" button within the header action group.
  - Options include 20, 50, 100, and 200.
  - Value changes trigger an update to browser local storage (`bandcamp_hub_sync_limit`).
  - Page initialization reads this local storage key, defaulting to 50 if unset.
  - The `startSync(forceRescan)` JavaScript function reads the current select value and appends `&limit=${selectedLimit}` to the SSE request URL when `forceRescan` is false.

- **Full-Width Docked Bottom Player**:
  - The footer container transitions from `fixed bottom-6 inset-x-0 mx-auto max-w-7xl w-[calc(100%-2rem)] rounded-full` to `fixed bottom-0 inset-x-0 w-full z-50 rounded-none border-t border-studio-border bg-studio-900/95 backdrop-blur-xl shadow-2xl`.
  - The inner wrapper is configured as `w-full max-w-[1600px] mx-auto px-6 py-3 flex items-center justify-between gap-6`.
  - The left track info column expands its maximum width constraint from `max-w-[220px]` to `max-w-xs` (320px).
  - The center transport and timeline column removes the `max-w-2xl` ceiling and adopts `max-w-4xl flex-1`, allowing the linear progress bar to expand proportionally.
  - The right-hand secondary utility button group maintains comfortable padding and hitboxes without shrinkage.
  - Show/hide animations transition using `translate-y-full` when closed and `translate-y-0` when active.
  - Page main content and load-more containers maintain `pb-28` to `pb-32` bottom clearance.

- **Multi-Track Drawer & DJ BPM Popover**:
  - The multi-track drawer is constrained to `max-w-5xl mx-auto mb-2` positioned directly above the bottom bar, retaining glass styling and rounded corners (`rounded-2xl`).
  - The DJ BPM panel positions with `bottom-full mb-3 left-0`, maintaining its standardized 320px width without clipping.

## Testing Decisions

- **What makes a good test**:
  - Tests verify external behavior, parameter validation, and user-observable outcomes rather than transient styling details.
  - Tests verify that `/api/sync/stream` respects custom `limit` parameters, enforces defaults, and handles edge conditions (e.g. invalid numbers, force rescan override).
  - Tests verify that HTML templates produce the expected DOM IDs, select option values, layout structure, and responsive container classes.
- **Modules to be tested**:
  - Backend synchronization pipeline: `tests/test_sync_pipeline.py`.
  - API endpoint integration: `tests/test_sync_pipeline.py` or new test suite for sync query parameters.
  - Frontend template layout: `tests/test_ui_refinements.py`.
- **Prior Art**:
  - `tests/test_sync_pipeline.py`: Existing tests for `fetch_messages_paginated` with `max_cap` assertions.
  - `tests/test_ui_refinements.py`: Existing DOM string assertion tests verifying classes, layout attributes, and player dock elements.

## Out of Scope

- Arbitrary numeric input or freeform typing for sync batch sizes (fixed to 20, 50, 100, 200).
- Scheduled background background cron syncs (sync remains user-triggered).
- Collapsible or miniature player mode (bottom bar remains consistent during playback).
- Altering the core audio playback engine, Web Audio API context, or HTML5 Audio elements.

## Further Notes

- All changes maintain strict adherence to the domain glossary in `CONTEXT.md` (Release, Track, ISO Week, Sync Watermark, Listened, Starred).
- ADR-0003 is fully preserved; incremental synchronization continues to advance the watermark while preserving the 30-day force rescan escape hatch.
