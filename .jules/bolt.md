## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-16 - [Unbounded WebSocket Backfill]
**Learning:** The WebSocket `request_backfill` event was fetching ALL messages for a room, creating a massive bottleneck (fetching thousands of rows) on every room join. This essentially transferred the entire database table to every client on connection.
**Action:** Always implement explicit limits (e.g., `LIMIT 50`) and cursor-based pagination (`before_id`) for any list endpoints. Never rely on "fetch all" logic for core entities like messages.
