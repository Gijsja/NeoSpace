## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-23 - [Socket Backfill Performance]
**Learning:** The `request_backfill` socket event was fetching ALL messages for `after_id=0`, causing performance issues with large datasets. The HTTP backfill endpoint `queries/backfill.py` also selects all messages.
**Action:** Implemented limits: 100 messages for initial load (`after_id=0`) and 1000 for sync (`after_id>0`). Always check for unbounded `SELECT` statements in message retrieval logic.
