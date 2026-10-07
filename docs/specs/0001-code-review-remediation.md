# Spec: Code Review Full Remediation & State Machine Hardening

## Problem Statement

When curating new music releases, users encounter unexpected behavior, silent crashes, and performance freezes. Specifically:
1. Auditing music using the inbox triage workflow is disrupted because marking a Release as Starred does not automatically mark it as Listened, leaving favored music lingering in the Unlistened view. Furthermore, automated 30-second playback auditing can inadvertently unmark a manually listened release due to stale interface timers.
2. Routine incremental synchronization locks up the web interface because background network requests freeze the server's asynchronous event loop. Users with large Gmail notification backlogs risk permanently dropping releases beyond the initial 50 emails due to missing pagination coupled with aggressive watermark progression.
3. Certain releases crash the scraper completely when falling back to standard metadata extraction, causing sync jobs to halt or fail unpredictably.
4. Database snapshot operations risk producing corrupted backups because the storage engine's write-ahead log transactions are not safely flushed prior to file copies.

## Solution

Provide a reliable, non-blocking, and seamless music discovery experience that strictly honors the curation state machine, preserves all incoming releases across high-volume notification batches, and ensures data durability:
1. Enforce the asymmetric one-way promotion state machine across both backend persistence and the interactive interface, ensuring that starring a Release immediately promotes it to Listened while preserving curation states during unstarring and unlistening.
2. Offload all synchronous network operations to background worker threads, eliminating web server UI lockups during synchronization.
3. Introduce robust pagination to notification queries with a safe upper batch boundary (200 notifications), accurately capturing all pending releases before advancing the Sync Watermark.
4. Correct OpenGraph metadata fallback string extraction to eliminate crashes, and enforce SQLite native online backup APIs with active Write-Ahead Logging to guarantee backup consistency.

## User Stories

1. As a music curator, I want marking a Release as Starred to automatically mark it as Listened, so that favorited works are immediately cleared from my Unlistened triage queue.
2. As a music curator, I want unstarring a Release to keep its Listened status intact, so that I do not have to re-evaluate music I have already audited.
3. As a music curator, I want marking a Starred Release as unlistened to preserve its Starred status, so that I can queue my favorite music for a second listen without losing my purchase bookmark.
4. As a music curator, I want the web interface to remain fast and responsive while a background sync is running, so that I can continue listening to music without stuttering or frozen controls.
5. As a heavy Bandcamp subscriber with more than 50 unread release notifications, I want synchronization to paginate and ingest all pending emails up to 200 items in a single run, so that no releases are permanently skipped or lost.
6. As a music curator, I want notifications arriving on Sunday night or Monday morning UTC to be partitioned into the exact correct ISO Week, regardless of my computer's local timezone settings.
7. As a listener, I want the automatic 30-second listen timer to recognize if I already manually marked a Release as Listened, so that it never accidentally reverts my manual review state back to unlistened.
8. As a DJ reviewing a full ISO Week digest, I want a single bulk action to mark an entire week's releases as Listened in one request, so that I do not flood the system with individual network calls.
9. As a music curator encountering a Release with non-standard webpage formatting, I want the scraper to cleanly extract the title and artist from fallback metadata without crashing, so that the Release is still saved to my Evergreen Vault as a Degraded Release.
10. As a system administrator or user performing a database reset, I want the automatic backup snapshot to use the database engine's native backup channel, so that all active transactions in the Write-Ahead Log are flushed without database corruption.
11. As a user reviewing synchronization logs, I want all releases and tracks to flow through typed data models, so that logging and parsing anomalies are clearly identified.
12. As a user operating across multiple browser tabs, I want state machine transitions performed in one tab to reflect immediately in other tabs without requiring manual page reloads.

## Implementation Decisions

### 1. Asymmetric Curation State Machine
- Curation state transitions must follow a strict one-way promotion logic:
  - Transition `Star (0 -> 1)`: Mutates `is_starred = 1` and `is_listened = 1`. Returns both updated states.
  - Transition `Unstar (1 -> 0)`: Mutates `is_starred = 0`. Retains existing `is_listened` value.
  - Transition `Toggle Listened (1 -> 0)`: Mutates `is_listened = 0`. Retains existing `is_starred` value.
  - Transition `Toggle Listened (0 -> 1)`: Mutates `is_listened = 1`. Retains existing `is_starred` value.
- The state transition logic is unified in a dedicated persistence service rather than duplicated across multiple route handlers.
- Both the backend API contract and the frontend UI state update atomically based on server response.

### 2. High-Capacity Paginated Notification Synchronization
- The email ingestion pipeline will paginate through matching Gmail message IDs using page tokens until no further pages exist or until reaching a safe batch cap of 200 notifications per sync run.
- The Sync Watermark timestamp advances only after all paginated messages within the current batch are fully processed and persisted.
- Notification receipt timestamps must be interpreted strictly in UTC timezone before extracting the ISO Week identifier (`YYYY-Www`).

### 3. Asynchronous Concurrency & Thread Isolation
- All third-party synchronous blocking SDK calls (Google API Client network executions) must be offloaded to asynchronous worker threads using execution pool delegates. The server's main asynchronous event loop must never be blocked by network I/O.
- The sync pipeline concurrency lock (`Sync Lock`) remains active to guarantee mutually exclusive synchronization runs.

### 4. Resilient Metadata Extraction Hierarchy
- Metadata extraction fallback parser must safely split and unpack title and artist strings across all delimited variants (`", by "`, `" - "`, `" by "`, `" | "`), ensuring index-safe extraction.
- In-memory data transfer between extraction, ingestion, and persistence modules must use explicit structured domain records rather than dynamic untyped tuples.

### 5. Storage Engine & Backup Consistency
- All SQLite database connections across all processes and modules must explicitly initialize Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and standard timeout pragmas upon opening.
- Database backup and reset procedures must replace raw filesystem file copies with SQLite's native online backup interface (`connection.backup`), ensuring that all uncommitted write-ahead log pages are merged cleanly.

### 6. Batch Operations Contract
- Provide a bulk curation endpoint accepting an ISO Week identifier or an array of Release identifiers to set `is_listened = 1` in a single transactional write.

## Testing Decisions

### What Makes a Good Test
Tests must evaluate external behavior rather than internal private variables. A good test asserts:
- Given an unlistened release, triggering a Star action sets both `is_starred = 1` and `is_listened = 1`.
- Given a starred release, unstarring sets `is_starred = 0` while keeping `is_listened = 1`.
- Given a notification query with 75 messages across two pagination pages, all 75 releases are ingested and the Sync Watermark advances accurately.
- Given HTML with OpenGraph fallback title structures, the scraper returns clean Title and Artist strings without throwing unhandled exceptions.
- Given a database in WAL mode with active transactions, executing a backup produces a readable SQLite file matching row counts.

### Modules Under Test
1. **Curation State Machine**: Tested via HTTP API routes and database state assertions.
2. **Metadata Extraction Pipeline**: Tested via mock HTML fixtures containing edge-case title patterns.
3. **Database Consistency & Backup**: Tested via simulated WAL writes and backup verification.

### Testing Seam
- **Primary Seam**: HTTP API Layer (`TestClient`) and Service Interface functions. All curation state transitions and bulk operations are verified through their public endpoints.

## Out of Scope
- Direct integration with third-party streaming services (Spotify, Apple Music, SoundCloud).
- Automatic purchase or download of audio files from Bandcamp.
- Multi-user authentication and remote multi-tenant database hosting.

## Further Notes
- If `docs/agents/issue-tracker.md` is missing from the repository, run `/setup-matt-pocock-skills` to configure automated issue tracker syncing.
