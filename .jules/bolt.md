## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-02-14 - [Unbounded Backfill Queries]
**Learning:** The HTTP backfill endpoint was executing `SELECT * FROM messages`, fetching the entire chat history. This creates a linear performance degradation as the application ages and message count grows.
**Action:** Always enforce a hard `LIMIT` on historical data queries (e.g., last 50 items) and implement cursor-based pagination for accessing older data.
