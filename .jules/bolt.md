## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-27 - [Unbounded WebSocket Backfill]
**Learning:** Unbounded `SELECT *` queries in WebSocket "join room" handlers are dangerous. They scale linearly with history size and can crash the server or freeze clients.
**Action:** Always implement `LIMIT` clauses in message history queries. Use `LIMIT 100` for initial loads (latest messages) and pagination for older history.
