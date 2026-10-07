# 03: Asymmetric Curation State Machine

**What to build:**
Starring a Release immediately marks it as Listened and dismisses it from the Unlistened triage view across both backend persistence and the frontend interface; unstarring retains the Listened state; marking as unlistened retains the Starred state. In addition, the 30-second playback timer dynamically checks the current review status and never accidentally flips a manually audited Release back to unlistened.

**Blocked by:** 01: Storage Engine Hardening & Online WAL Backup

**Status:** ready-for-agent

- [x] Starring (is_starred: 0 -> 1) implicitly promotes is_listened = 1 in both database and API response.
- [x] Unstarring (is_starred: 1 -> 0) preserves is_listened = 1.
- [x] Marking unlistened (is_listened: 1 -> 0) preserves is_starred = 1.
- [x] Frontend interface updates both star icon and listened checkmark immediately upon starring.
- [x] 30-second listen timer checks live status and prevents flipping manually listened releases back to 0.
