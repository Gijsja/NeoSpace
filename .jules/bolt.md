## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-16 - [Unbounded Data Fetching]
**Learning:** The `/backfill` endpoint was performing a `SELECT *` on the messages table without pagination, causing massive payloads and latency as data grew.
**Action:** Always enforce pagination (limit/cursor) on list endpoints, even if the initial dataset is small.
