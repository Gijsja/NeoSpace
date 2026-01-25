## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-25 - [WebSocket Backfill Pagination]
**Learning:** Fetching unlimited message history in WebSockets (`request_backfill`) is a silent performance killer. It increases startup time and bandwidth usage significantly as history grows.
**Action:** Always implement pagination limits (e.g. limit 100) for initial socket data loads, even if the frontend doesn't explicitly request a page size.
