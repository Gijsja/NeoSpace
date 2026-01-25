## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-25 - [Unbounded Socket Backfill]
**Learning:** The WebSocket `backfill` event was retrieving the entire message history for a room without a limit, leading to O(N) payload size growth and performance degradation.
**Action:** Always implement pagination limits (e.g., LIMIT 100) and optimized sorting (DESC limit then ASC sort) for initial data loads.
