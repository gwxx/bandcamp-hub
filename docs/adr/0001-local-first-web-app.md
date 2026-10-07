# 0001. Local-first Web App Architecture

Bandcamp Hub is architected as a local-first web application running on FastAPI and SQLite, rather than a centralized cloud SaaS or an Electron desktop bundle.

## Context
Users connect their personal Google/Gmail accounts to scan Bandcamp notification emails. Hosting this as a centralized SaaS would require storing third-party OAuth refresh tokens on a remote server, introducing significant security liabilities, privacy compliance costs, and infrastructure hosting overhead. Conversely, packaging with Electron introduces large binary footprints and complex cross-platform distribution.

## Decision
We chose a local-first Python/FastAPI web application paired with SQLite in WAL mode. Google OAuth credentials and tokens (`.auth/`) and the music database (`data/bandcamp.db`) remain entirely on the user's local disk. The web interface is rendered locally and accessed via `http://127.0.0.1:8000`.

## Consequences
- **Privacy & Security**: Zero risk of multi-tenant credential leakage; users retain complete ownership of their music discovery data.
- **Portability**: The entire application can be launched via standard Python scripts (`run.py`, `start_hub.bat`) with zero hosting cost.
- **Single-User Constraint**: The application is tailored for single-user concurrent access per local instance.
