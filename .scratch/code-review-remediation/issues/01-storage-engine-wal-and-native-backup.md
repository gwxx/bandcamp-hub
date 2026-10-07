# 01: Storage Engine Hardening & Online WAL Backup

**What to build:**
Ensure all SQLite database connections across the system strictly operate in Write-Ahead Logging (WAL) mode, and database backups are executed through SQLite's native online backup interface without risking uncommitted WAL transaction corruption or lock contention.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [x] All database access points use a unified connection factory setting PRAGMA journal_mode=WAL; and row factory.
- [x] Database backup and reset procedures use sqlite3.connect().backup() rather than raw shutil.copy2.
- [x] Unused dead-code generator get_db() is cleaned up or reconciled.
