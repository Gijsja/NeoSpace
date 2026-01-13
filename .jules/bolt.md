## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-13 - [Syncing Schema Definitions]
**Learning:** This codebase maintains database schema in two places: `db_schema.py` (SQLAlchemy/Metadata) and `db.py` (Raw SQL for `init_db`). These MUST be kept in sync manually. A missing index in `db.py` means it won't be created even if defined in `db_schema.py`.
**Action:** When adding indexes or columns, always grep for the table name and update BOTH files.

## 2026-01-13 - [Hidden Endpoint Bottleneck]
**Learning:** `queries/backfill.py` exposes a function `backfill_messages` that selects ALL messages from the table without filtering by room or limit. This is a potential DoS vector and performance catastrophe as data grows.
**Action:** Always audit "backfill" or "history" endpoints for limits and scope (room_id) filters.
