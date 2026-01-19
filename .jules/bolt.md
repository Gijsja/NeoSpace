## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-19 - [Backfill Pagination]
**Learning:** The `/backfill` HTTP endpoint was returning ALL messages in the database, posing a severe performance risk. This shows that having a "working" WebSocket equivalent doesn't guarantee the HTTP fallback is optimized.
**Action:** Always verify "helper" HTTP endpoints when optimizing WebSocket-heavy apps.
