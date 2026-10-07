# Spec: Code Review Remediation and Domain Aggregate Alignment

Status: ready-for-agent

## Problem Statement

Following the two-axis code review across repo standards and originating requirements, four specific inconsistencies, edge-case bugs, and test coverage gaps were identified:

1. **Post-Analysis Tempo Upper-Bound Defect**: The client-side audio analysis completion callback contained an obsolete, hardcoded upper boundary check (`<= 240` BPM). Valid high-tempo music between 241 and 300 BPM (e.g., speed metal, breakcore, fast jungle, or uptempo electronic tracks) triggered an erroneous failure alert despite the system-wide validation boundary being 40.0 to 300.0 BPM.
2. **Domain Aggregate Boundary Ambiguity (Release vs Track)**: The action button labeled the BPM operation as analyzing "曲目 BPM" (Track BPM). However, in accordance with the domain model in `CONTEXT.md` and database architecture, BPM is stored at the `Release` aggregate level. Attributing Release-level metadata solely as Track-level caused conceptual confusion between the currently playing audio stream and the catalog entity.
3. **Duplicated Client-Side Validation Logic**: Number validation and error alert handling for custom BPM entry were redundantly implemented across manual input parsing and staged commit handlers.
4. **Test Suite Coverage & Traceability Gaps**: The test suite lacked template string assertions for the 60–180 BPM autocorrelation range and conditional save button visibility, omitted boundary checks in the proxy test suite, and retained misattributed ticket identifiers in historical UI test docstrings.

## Solution

1. **Synchronize Post-Analysis Verification to 300 BPM**:
   - Update the analysis completion condition in the tempo controller to accept values up to 300.0 BPM (`estimatedBpm >= 40 && estimatedBpm <= 300`), eliminating the false-positive failure alert for fast tempos.
2. **Harmonize Domain Aggregation in User Interface**:
   - Refine the BPM analysis button copy to "分析目前播放曲目 BPM" (Analyze Current Playing Track BPM).
   - Provide an explicit tooltip and contextual label clarifying that the analyzed tempo will be assigned as the base BPM for the active Release entity, reconciling the physical act of listening to a single track with Release-level metadata storage.
3. **Consolidate Client-Side Boundary Validation**:
   - Extract a centralized validation helper `validateBpm(val)` in the frontend script to handle boundary checking (`40.0 <= bpm <= 300.0`) and user notification in one place.
   - Retain the existing backend procedural validation raising HTTP 400 Bad Request to guarantee backward compatibility with current API contracts.
4. **Complete Test Suite Coverage & Clean Traceability**:
   - Add template assertions to verify the presence of the 60–180 BPM octave doubling normalization logic and the state-driven conditional save button toggle in template tests.
   - Add boundary value validation tests (39.9, 40.0, 300.0, 300.1) to the proxy test module.
   - Update test docstrings in the UI refinement test module to clearly categorize historical tests as regression guardrails and prevent ticket number collisions.

## User Stories

1. As a DJ auditioning a 260 BPM breakcore track, I want the tempo analyzer to accept the analyzed result instead of rejecting it at 240 BPM, so that I can accurately audition and catalog high-speed genres.
2. As a curator listening to high-tempo speedcore or drum'n'bass, I want the analysis completion check to honor the full 40.0 to 300.0 BPM spectrum, so that the player never displays false failure alerts for fast music.
3. As a user clicking the analysis button, I want the label to read "分析目前播放曲目 BPM", so that I understand the system is analyzing the track audio currently playing in the dock.
4. As a user cataloging a release, I want the tooltip to clarify that the analyzed tempo applies to the entire Release, so that I understand why the BPM is associated with the release card.
5. As a listener entering a custom BPM value, I want consistent validation between the manual text input and the commit action, so that I receive predictable feedback regardless of where I submit the value.
6. As an API client submitting an invalid BPM of 39.9 or 300.1, I want the server to return an HTTP 400 Bad Request with a clear message, so that invalid data is never persisted.
7. As an API client submitting valid boundary values of 40.0 or 300.0, I want the server to return an HTTP 200 OK, so that legitimate extreme tempos are accepted.
8. As a QA engineer running the test suite, I want template tests to verify that the 60–180 BPM normalization loop is present in the rendered HTML, so that regressions in the autocorrelation algorithm are caught immediately.
9. As a QA engineer running tests, I want template tests to verify the conditional visibility logic for the save button, so that regressions in the staged state machine are prevented.
10. As a developer reviewing test files, I want historical tests to be clearly labeled as regression guardrails rather than active sprint tickets, so that issue traceability remains unambiguous.

## Implementation Decisions

- **Tempo Upper-Bound Synchronization**:
  - The client-side analysis completion check will evaluate bounds strictly between 40.0 and 300.0.
  - Any calculated BPM outside this unified range falls back to the manual inspection notification.

- **Domain Model & Copy Alignment**:
  - The primary analysis action button copy will toggle between:
    - "🔍 分析目前播放曲目 BPM" (when the active Release has no persisted BPM)
    - "🔄 重新分析目前播放曲目 BPM" (when the active Release already has a persisted BPM)
  - The button `title` attribute will inform the user: "此 BPM 將作為此 Release 之基準節奏" (This BPM will serve as the base tempo for this Release).
  - The active Release record in the database continues to store the aggregate `bpm` column without schema alteration.

- **Validation Consolidation**:
  - A shared JavaScript helper `validateBpm(val)` validates that input is numeric and within `[40, 300]`, emitting an alert and returning `false` if invalid.
  - The backend Pydantic model remains a bare float with procedural validation in the route handler, returning HTTP 400 Bad Request to maintain contract stability.

- **Test Suite Hygiene & Verification**:
  - The template test suite will inspect `index.html` for `while (bpm < 60)` and `btnSave.classList.toggle('hidden'`.
  - The proxy test suite will incorporate boundary tests matching those in the resilience test suite.
  - UI refinement test docstrings will label historical assertions (e.g. 320px dock width, enlarged seek buttons, bulk listened) as regression tests.

## Testing Decisions

- **What makes a good test**:
  - Tests verify external HTTP responses (status codes 200 vs 400) under edge conditions.
  - Tests verify rendered template structure and key state management hooks without executing browser-specific audio graphs.
- **Modules to be tested**:
  - API router: endpoint validation under boundary inputs (39.9, 40.0, 300.0, 300.1).
  - Web template: inclusion of 60–180 BPM octave loop, conditional save button toggle, domain labels, and circular geometry styling.
- **Prior art**:
  - `tests/test_audio_resilience_and_bpm.py`: existing FastAPI TestClient patterns.
  - `tests/test_ui_refinements.py`: template file reading and regex/string assertion patterns.

## Out of Scope

- Modifying the SQLite database schema or splitting BPM into per-track columns in `tracks_json`.
- Changing backend validation errors to HTTP 422 Unprocessable Entity.
- Reworking Web Audio API autocorrelation mathematical models.

## Further Notes

- This specification completely addresses all findings from the Standards and Spec code reviews, resolving every identified defect while respecting established domain definitions.
