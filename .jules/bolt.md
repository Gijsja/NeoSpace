## 2026-01-11 - [Middleware N+1 Query & Unbounded Selects]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets. Always filter `request.path`.
**Action:** Audit global middleware and skip logic for static/asset paths.
**Learning:** Unbounded `SELECT *` without LIMIT is a ticking time bomb, even in "small" apps.
**Action:** Always default to a sensible LIMIT (e.g. 500) for lists, even if pagination isn't implemented yet.
**Learning:** SQLite initialization in tests often uses raw SQL strings (`db.py`) instead of SQLAlchemy Metadata (`db_schema.py`). Both must be updated.
**Action:** Check `db.py` or `schema.sql` when adding indexes, not just the SQLAlchemy model.
