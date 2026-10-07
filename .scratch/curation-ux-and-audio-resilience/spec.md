# Spec: Curation UX, DJ Tempo Control, and Resilient Audio Playback

Status: implemented

## Problem Statement

When using Bandcamp Hub for weekly music discovery and DJ set preparation, users encounter several friction points across the timeline, playback engine, and curation controls:

1. **Opaque Timeline Intervals**: Weekly Digests identify releases only by ISO Week strings (e.g. `2026-W38`). Users cannot easily correlate which calendar dates correspond to that curation window without external reference tools.
2. **Stale Audio Stream Failures (HTTP 410 Gone)**: Bandcamp preview MP3 stream URLs embed time-limited cryptographic tokens. When users open Bandcamp Hub after hours or days, stored stream URLs expire. Attempting to play tracks results in silent failures or browser playback errors, forcing the user to trigger a redundant, time-consuming Gmail sync to refresh streams.
3. **Ghost Track Fallback & Misleading 0:00 Tracks**: When a multi-track Release contains unreleased or unstreamable tracks (duration `0.0` and no track-level stream URL), the player erroneously falls back to the release-level stream URL. When users click different tracks displaying `0:00`, the player displays each track's title but plays the exact same single preview track repeatedly, misleading the curator.
4. **Lack of DJ Tempo Curation (BPM & Pitch Control)**: DJs evaluating tracks for live mixing cannot preview how tracks sound at different tempos or record BPM values directly into their Evergreen Vault.
5. **Jacket Interaction Misalignment**: Curators expecting to open the canonical Bandcamp release page by clicking the album cover jacket find that it hijacks audio playback instead of opening the store page.
6. **Track Audit Memory Loss**: Within multi-track releases, users cannot visually discern which individual tracks they have already auditioned during their session or across visits.
7. **Control Clipping & Visual Noise**: The floating dynamic vinyl capsule dock clips the rightmost external link icon on standard desktop viewports. Text-heavy buttons ("已聽", "收藏") crowd the interface, while typography on small metadata tags strains readability.
8. **Stalled Continuous Playback**: When advancing to the next release, if that release is completely devoid of playable preview streams, playback abruptly halts instead of smoothly advancing to the next playable release.

## Solution

A cohesive upgrade across the presentation, playback resilience, and curation workflow:

1. **Explicit Calendar Intervals**: Every Weekly Digest header displays full calendar bounds (`YYYY-MM-DD ~ YYYY-MM-DD`), and the sidebar timeline surfaces compact bounds (`MM/DD - MM/DD`), dynamically computed from the ISO Week.
2. **On-Demand Resilient Stream Auto-Recovery**: The backend exposes an on-demand stream refreshment interface. When the client encounters a 410 Gone or media loading failure, it automatically invokes this endpoint in the background to re-scrape fresh Bandcamp stream tokens and persist them to the Evergreen Vault, resuming playback with zero human intervention.
3. **Strict Stream URL Isolation & Non-Blocking Notices**: Remove the erroneous track-to-release stream fallback. Unstreamable tracks are explicitly rendered with a disabled state and "無試聽" duration marker. Clicking unstreamable tracks triggers a non-blocking HUD notice without interrupting active audio.
4. **DJ Tempo Control with Master Tempo**: Integrate a persistent BPM and speed controller into the vinyl capsule player dock. Users can adjust playback speed from `0.8x` to `1.2x` with native browser pitch preservation (`preservesPitch = true`), view real-time adjusted BPM values, and persist measured base BPMs to the database.
5. **Decoupled Jacket Store Navigation**: Clicking the album jacket opens the release in Bandcamp in a new window, while card body and title clicks manage audio playback.
6. **Persistent Track Audition Dimming**: Auditioned tracks are automatically recorded in persistent client storage and rendered with dimmed text, providing an immediate visual history of reviewed tracks.
7. **Refined Typography & Streamlined Iconography**: Widen the player dock container to 1024px with balanced padding. Replace text buttons with unified, minimalist icons (Bandcamp parallelogram SVG for external links, circular checkmark for Listened state, pure star for curation filters). Scale typography up by one full step across all text levels.
8. **Smart Auto-Skipping Playback**: Advancing playback across releases automatically skips entirely unstreamable releases, seeking forward until a release with playable audio is found and loaded.

## User Stories

1. As a music curator, I want to see the start and end dates of each ISO Week in the digest header, so that I know the exact calendar date range of the releases I am auditing.
2. As a music curator, I want the sidebar timeline to display compact date ranges next to week identifiers, so that I can quickly jump to specific dates without expanding headers.
3. As a DJ, I want tracks with expired Bandcamp stream tokens to auto-refresh in the background when played, so that I can listen to music immediately without having to run a manual Gmail sync.
4. As a DJ, I want the system to persist refreshed stream URLs back to the local database, so that subsequent plays of the same track do not re-scrape Bandcamp.
5. As a music curator, I want unstreamable tracks in multi-track releases to be clearly identified as "無試聽", so that I am not confused by 0:00 durations.
6. As a music curator, I want clicking an unstreamable track to show a non-blocking HUD notification, so that my current audio playback is not interrupted.
7. As a music curator, I want each track in a multi-track release to only play its own unique audio stream, so that I never hear the same preview track under different track names.
8. As a DJ, I want a tempo controller in the mini player, so that I can audition how a track sounds when sped up or slowed down for my DJ sets.
9. As a DJ, I want the tempo controller to preserve the original musical pitch (Master Tempo / Key Lock), so that vocal and instrumental timbres do not distort when tempo shifts.
10. As a DJ, I want to view the real-time adjusted BPM as I adjust playback speed, so that I know the exact target tempo.
11. As a DJ, I want to manually input and save a base BPM for any release, so that my BPM data persists in the Evergreen Vault for future reference.
12. As a music curator, I want clicking the album cover jacket to open the release directly on Bandcamp, so that I can quickly inspect liner notes or purchase vinyl.
13. As a music curator, I want clicking the card title or body to start audio playback, so that jacket external navigation does not prevent easy playback.
14. As a music curator, I want individual tracks I have played to automatically turn grey, so that I can keep track of which tracks in an EP or album I have already listened to.
15. As a music curator, I want played track dimming to persist when I refresh or reopen the page, so that I don't re-listen to tracks by accident.
16. As a music curator, I want played track dimming to avoid extra checkbox symbols, so that the tracklist remains visually sleek and readable.
17. As a music curator, I want the mini player dock to be wide enough so that the Bandcamp link icon does not clip against the pill boundary, so that the UI looks polished and comfortable.
18. As a music curator, I want the "Listened" toggle button on cards and the player to be a clean circular icon, so that it takes up less space while remaining intuitive.
19. As a music curator, I want the top header "Starred" filter to display as a clean star icon, so that navigation feels concise and modern.
20. As a music curator, I want all UI text sizes scaled up by one degree, so that micro-labels and artist names are effortless to read.
21. As a DJ, I want the player to automatically skip over releases that have zero streamable tracks when advancing to the next release, so that continuous playback does not stall on silent preorder pages.
22. As a DJ, I want the player to smoothly scroll the active card into view when auto-skipping to the next playable release, so that my screen stays synchronized with the playing audio.

## Implementation Decisions

### 1. ISO Week Interval Computation
- Compute the calendar interval directly on the client using the ISO-8601 standard algorithm: Week 1 of an ISO year is the week containing January 4th. Day 1 is Monday and Day 7 is Sunday.
- Format for main headers: `YYYY-Www (YYYY-MM-DD ~ YYYY-MM-DD)`.
- Format for sidebar timeline: `YYYY-Www (MM/DD - MM/DD)`.

### 2. Audio Stream On-Demand Refresh API & Client Auto-Recovery
- Add a new backend endpoint: `POST /api/releases/{release_id}/refresh-stream`.
- The endpoint queries the Release from the database by ID, invokes the scraper to re-fetch and parse the canonical page HTML, updates the database record with the new `stream_url`, `tracks_json`, and `updated_at`, and returns the refreshed JSON payload.
- On the client side, attach an `error` listener to the global `<audio>` element. If playback fails (or returns HTTP 403/410), invoke the refresh endpoint automatically.
- Upon receiving fresh URLs, update the active client model, assign the new URL to `audio.src`, call `audio.play()`, and flash a non-blocking HUD notice: `🔄 音訊連結已更新`.

### 3. Track Audio Stream Isolation & Non-Streamable UX
- Remove `const streamUrl = track.stream_url || rel.stream_url;`. A track without its own `stream_url` must NOT inherit the release stream.
- In the tracklist render function, evaluate each track:
  - If `!track.stream_url`: render the right-side duration as "無試聽", set cursor to `not-allowed`, and attach a click handler that triggers `triggerHUD('⚠️', '此曲目未開放試聽，可前往原站收聽')` without touching audio playback.
  - If `track.stream_url`: render the formatted duration `formatTime(track.duration)` and allow standard playback.

### 4. DJ Tempo Controller & BPM Persistence
- Add a BPM capsule indicator to the mini player dock displaying the current speed and BPM (e.g. `-- BPM (1.0x)` or `124 BPM (1.0x)`).
- Clicking the capsule opens a popover DJ control panel containing:
  - Pitch adjustment slider ranging from `0.80x` to `1.20x` (step `0.01`).
  - Nudge buttons: `-1%` and `+1%`.
  - A `Reset (1.0x)` button.
  - A BPM input field and "儲存" button to persist base BPM for the active release.
- Audio playback speed is controlled via native HTML5 `audio.playbackRate = speed` with `audio.preservesPitch = true`.
- Add a backend endpoint: `PATCH /api/releases/{release_id}/bpm` accepting `{"bpm": float}` to persist the base BPM to the `releases` table.

### 5. Album Jacket Decoupled Navigation
- In the release card template, wrap the cover image in an anchor link `<a href="${rel.url}" target="_blank" onclick="event.stopPropagation()">` or bind a click handler that opens `rel.url` via `window.open(rel.url, '_blank')`.
- Remove the hover play overlay on the jacket; replace it with a subtle Bandcamp logo overlay linking externally.
- Audio playback for the release is triggered by clicking the card body, album title, or specific tracks.

### 6. Persistent Played Track Audition History
- Maintain a set of played track keys (`${release_id}_${track_index}`) in `localStorage` under key `bc_hub_played_tracks`.
- When a track begins playing, add its key to the set and serialize it to `localStorage`.
- When rendering cards and tracklists, check if the track key exists in the played set. If present and not currently actively playing, apply dimmed styles (`text-zinc-500 opacity-60`).

### 7. Viewport & Iconographic Polish
- Expand the `#player-dock` maximum width from `max-w-4xl` (896px) to `max-w-5xl` (1024px) with `px-6 py-2.5` padding.
- Replace text buttons:
  - Bandcamp external links: replace `↗` with the official Bandcamp parallelogram SVG icon.
  - Listened buttons: replace text with a single circular check icon (`○` when unlistened, `✓` in cyan when listened).
  - Starred filter button: replace `<span>⭐</span> 收藏` with `<span>⭐</span>`.
- Scale Tailwind typography classes up by one tier across the stylesheet.

### 8. Playback Auto-Skipping Across Releases
- When advancing playback (`playNextTrack` reaching the end of a release or invoking next release):
  - Check whether the target candidate release contains any playable tracks (`tracks.some(t => !!t.stream_url) || !!rel.stream_url`).
  - If the candidate release has no playable audio, increment `selectedIndex` iteratively until a release with playable audio is found (or the entire list is traversed).
  - Load and play the first playable track of the resolved release and scroll its card into view smoothly.

## Testing Decisions

### What Makes a Good Test
- Tests should execute against the highest possible architectural seam: HTTP requests to the FastAPI application (`TestClient`) verifying full request/response contracts, status codes, and SQLite database persistence.
- Tests must verify external observable behavior rather than internal private functions.
- Client-side pure calculations (such as ISO week date range math) should be verified through deterministic unit fixtures.

### Modules to Test
1. **API Endpoints (`app/routers/api.py`)**:
   - `POST /api/releases/{release_id}/refresh-stream`: Validate stream URL refreshment, database update, and fallback handling when Bandcamp scraping succeeds or fails.
   - `PATCH /api/releases/{release_id}/bpm`: Validate BPM schema validation, persistence into SQLite, and updated return payload.
2. **Scraper Resilience (`app/services/scraper_service.py`)**:
   - Verify that scraping handles missing stream files gracefully and populates track metadata with duration and stream isolation.
3. **Database Layer (`app/database.py`)**:
   - Ensure SQLite schema supports `bpm` updates and record integrity.

### Prior Art
- `tests/test_state_machine.py`: Demonstrates isolating SQLite with a temporary directory, initializing test records, and asserting state transitions via FastAPI `TestClient`.
- `tests/test_scraper.py`: Demonstrates testing DOM parsing and TralbumData extraction against mock payloads.

## Out of Scope

- Independent Web Audio API DSP pitch shifting (modifying pitch without changing tempo).
- Automated server-side acoustic beat detection or waveform audio analysis.
- Bandcamp cart, user collection, or purchase transaction management.
- Multi-user authentication or cloud database synchronization.

## Further Notes

- The ISO Week date algorithm accurately accounts for leap years and 53-week ISO calendar years.
- HTML5 `audio.preservesPitch = true` is supported across modern Chromium, WebKit (Safari), and Gecko (Firefox) engines.
