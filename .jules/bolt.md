## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-11 - [Unbounded List Endpoints]
**Learning:** Endpoints that return lists (like `/backfill`) must enforce strict pagination (LIMIT) and filtering (WHERE) by default. `SELECT *` or unbounded queries are DoS vectors and performance killers.
**Action:** Always implement `limit` and `offset` (or cursor-based pagination) and appropriate filters (e.g., `room_id`) for any list endpoint.
