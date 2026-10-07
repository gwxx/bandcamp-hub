# Spec: Sync Cap Toast Notification, Escape Key Hierarchy, and Boundary Hardening

Status: ready-for-agent

## Problem Statement

Following the initial delivery of the selectable sync batch size and docked bottom player, a code review identified several usability, architectural, and edge-handling gaps:

1. **Imperceptible Cap Warning**: When an incremental sync hits the user-selected batch limit (e.g. 20 or 50 emails), the notice explaining that older historical emails can be retrieved via the 30-day force rescan is displayed via a transient keyboard HUD. Because this HUD auto-dismisses after only 850ms, users cannot read the 55-character explanation before it vanishes, leaving them unaware of why older releases were not pulled.
2. **Disruptive Escape Key Behavior**: When evaluating music and examining details in the BPM analyzer or multi-track drawer, pressing the `Escape` key immediately closes the entire player and halts audio playback, rather than progressively closing the open floating panel. Furthermore, the BPM panel is not properly closed when the player dock closes.
3. **Backend Upper Bound Ceiling Vulnerability**: The synchronization pipeline enforces a minimum batch size of 1 message but does not constrain the upper bound. Direct API requests can pass arbitrary values (e.g. 1000), bypassing the designed 200-message ceiling and exhausting quotas.
4. **Redundant Query Parameters and Missing Edge Tests**: Forced rescanning sends redundant batch limits over SSE, while test suites lack assertions for boundary inputs (such as zero, negative, or excessive limits), and model validation contains primitive obsession smells.

## Solution

1. **Persistent Top Toast Notification**: When incremental synchronization reaches the batch limit, present a dedicated glass-panel Toast notification banner below the header for 5 seconds. The banner includes a direct "前往設定" (Open Settings) action button that immediately opens the settings modal to access the 30-day force rescan, along with an explicit close button.
2. **Tiered Progressive Escape Key Handling**: Structure the keyboard `Escape` handler into a tiered hierarchy that closes the topmost transient UI layer first without interrupting playback. If settings or help modals are open, close them. Otherwise, if the BPM popover or multi-track drawer is open, close only the popover/drawer while audio continues playing seamlessly. Only if no sub-panels or modals are active will `Escape` close the player dock. Additionally, ensure `closePlayer()` cleanly closes all child panels.
3. **Rigorous Backend Clamping and URL Parameter Cleanup**: Clamp the effective sync batch size strictly between 1 and 200 in the synchronization engine and FastAPI route parameter declarations. Remove redundant limit query parameters on forced rescans.
4. **Boundary Verification and Standards Alignment**: Add automated test cases covering edge-case sync limits (zero, negative, and oversized integers). Refactor BPM model boundaries into declarative Pydantic field constraints and deduplicate test mock scaffolding.

## User Stories

1. As a DJ triaging weekly releases with a 20-item limit, I want to see a clear, readable toast notification when sync reaches the 20-item ceiling, so that I understand why earlier releases did not appear without the message disappearing before I can read it.
2. As a user reading the sync limit warning toast, I want a "前往設定" (Open Settings) shortcut button inside the toast banner, so that I can immediately initiate a 30-day force rescan without hunting through the navigation menus.
3. As a user reading the sync limit warning toast, I want a close button ("✕") on the banner and an automatic 5-second fadeout, so that the notification does not permanently clutter my screen or block header controls.
4. As a music curator listening to a new release with the DJ BPM popover open, I want pressing the `Escape` key to close only the BPM popover, so that my music keeps playing uninterrupted.
5. As a music curator viewing an album's multi-track drawer, I want pressing `Escape` to close only the multi-track drawer, so that my audio playback continues smoothly in the bottom dock.
6. As a user with both the settings modal and the player open, I want pressing `Escape` to close the settings modal first, so that my ongoing music session remains undisturbed.
7. As a user who has no modals or popovers open, I want pressing `Escape` to close the bottom player dock and stop playback, so that I can quickly silence audio and dismiss the interface when needed.
8. As a user clicking the close button on the bottom player dock, I want all child floating popovers (BPM panel and multi-track drawer) to close alongside the dock, so that detached popovers are never left floating orphaned on screen.
9. As a systems engineer, I want the backend synchronization pipeline to enforce a strict upper limit of 200 messages regardless of query parameters, so that external requests cannot degrade service performance or exhaust Gmail API quotas.
10. As an API client, I want `/api/sync/stream` to clamp negative or zero limits to 1 and oversized limits to 200, so that atypical input does not trigger unexpected 500 errors or pipeline failures.
11. As a frontend client triggering a 30-day force rescan, I want the SSE request URL to cleanly specify `/api/sync/stream?force_rescan=true` without redundant limit parameters, so that the request faithfully mirrors the specification.
12. As a developer maintaining the codebase, I want BPM updates to be validated declaratively between 40.0 and 300.0 BPM in the request schema, so that domain constraints are enforced uniformly at the input boundary.
13. As a developer running unit tests, I want edge-case parameters for sync batch sizes (such as negative numbers, zero, and values over 200) to be verified in automated tests, so that regressions in parameter clamping are detected immediately.
14. As a developer writing pipeline tests, I want reusable test mock context helpers, so that redundant mock scaffolding is eliminated and test suites remain readable and maintainable.

## Implementation Decisions

### 1. Dedicated Top Toast Notification Banner
- A dedicated banner element will be placed beneath the top navigation header.
- Styled using the application's glass-panel aesthetic with cyan accent borders and clear typography.
- When an incremental sync completes with `total_msgs >= effective_limit`, the frontend slides this banner into view with a 5-second automatic timer.
- Includes an inline action button linking directly to the settings dialog (`openSettings()`) and a dismiss button (`closeToast()`).
- Regular HUD messages (playback status, triage shortcuts) remain short-lived (850ms) and unaffected by this change.

### 2. Progressive Escape Hierarchy State Machine
- When an `Escape` key event is intercepted outside input text fields, the event handler follows a strict priority waterfall:
  1. If `#settings-modal` is visible: close settings modal; prevent default; return.
  2. If `#help-modal` is visible: close help modal; prevent default; return.
  3. If `#bpm-panel` is visible: close BPM panel; prevent default; return.
  4. If `#multi-track-drawer` is visible: close multi-track drawer; prevent default; return.
  5. If `#player-dock` is in its active/open position: execute `closePlayer()`; prevent default; return.
- The `closePlayer()` routine will explicitly ensure `#bpm-panel` and `#multi-track-drawer` are hidden when the player is dismissed.

### 3. Backend Parameter Clamping and URL Cleanup
- In the backend synchronization service, compute `effective_limit` as `200 if force_rescan else min(200, max(1, limit))`.
- In the FastAPI router, declare `limit` with `Query(50, ge=1, le=200)`.
- In the frontend `startSync` routine, force rescan will construct `/api/sync/stream?force_rescan=true`, omitting `&limit=200`.

### 4. Schema Validation and Test Scaffolding Consolidation
- Update the BPM update request model with Pydantic field constraints restricting values between 40.0 and 300.0.
- Factor repetitive Gmail and database mock context managers in `test_sync_pipeline.py` into a consolidated test helper.

## Testing Decisions

- **What makes a good test**:
  - Tests verify user-observable behavior and external API contracts rather than implementation minutiae.
  - Tests verify that `/api/sync/stream` cleanly clamps boundary parameters (negative numbers, zero, oversized values, and default values).
  - Tests verify that HTML template markup contains the toast notification structure, action links, and updated Escape handling logic.
  - Tests verify that BPM update requests reject values outside the 40.0–300.0 boundary.
- **Modules to be tested**:
  - Backend synchronization pipeline and API endpoint: `tests/test_sync_pipeline.py`.
  - Frontend DOM elements and interaction scripts: `tests/test_ui_refinements.py`.
- **Prior Art**:
  - `tests/test_sync_pipeline.py`: Existing tests for `fetch_messages_paginated` and `run_sync_pipeline`.
  - `tests/test_ui_refinements.py`: Existing DOM assertion tests for template elements and player dock behavior.

## Out of Scope

- Modifying the underlying SQLite database schema or tables (`releases`, `sync_watermark`).
- Changing the core audio playback engine or Web Audio API tempo detection algorithms.
- Custom notification sound effects or desktop push notifications.

## Further Notes

- Maintains strict compliance with `CONTEXT.md` terminology (Release, Track, ISO Week, Sync Watermark).
- Preserves ADR-0003 principles for incremental sync while ensuring robust historical recovery via the 30-day force rescan.
