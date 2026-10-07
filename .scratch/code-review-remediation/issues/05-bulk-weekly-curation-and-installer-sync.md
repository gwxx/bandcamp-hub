# 05: Bulk Weekly Curation & Installer Package Sync

**What to build:**
Curators can mark an entire ISO Week digest as Listened in a single transactional request. All architectural fixes, schema pragmas, and interface updates across all preceding tickets are synchronized and packed into the standalone installer bootstrap script (setup_project.py).

**Blocked by:** 03: Asymmetric Curation State Machine, 04: Non-Blocking Paginated Notification Synchronization

**Status:** ready-for-agent

- [x] Provide POST /api/releases/bulk-listened accepting a week string or list of release IDs.
- [x] Frontend uses bulk endpoint for markWeekAllListened.
- [x] Standalone installer setup_project.py is regenerated and matches all source code and documents.
- [x] All Python files pass py_compile without errors.
