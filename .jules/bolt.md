## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-11 - [Unbounded DB Queries]
**Learning:** The `/backfill` endpoint was fetching the entire `messages` table (SELECT *) without pagination, causing O(N) performance degradation as history grew.
**Action:** Always check existing endpoints for missing `LIMIT` clauses or pagination. Implemented cursor-based pagination (limit, before_id, after_id) to cap fetching at 50 records.
