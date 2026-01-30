## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-26 - [SQLite Order By vs Filter]
**Learning:** SQLite optimizer may prioritize `ORDER BY` over highly selective filters, causing full table scans if no global index exists on the sort column.
**Action:** Use a composite covering index on `(filter_col, sort_col)` (e.g., `(profile_id, created_at)`) to enable "Deferred Row Loading" and efficient filtering, avoiding slow table scans on large tables.
