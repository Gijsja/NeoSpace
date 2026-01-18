## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-18 - [Unbounded DB Queries in Hot Paths]
**Learning:** The `/backfill` endpoint was fetching the ENTIRE message history (O(N)) on every call, causing a massive scalability bottleneck.
**Action:** Always verify that list endpoints support pagination (limit/offset or cursor) and have a hard default limit.

## 2026-01-18 - [Broken Dependency Pins]
**Learning:** `requirements.txt` pinned `blinker==1.7.0` but `Flask 3.1.2` requires `blinker>=1.9.0`. This prevented running tests without modifying the environment.
**Action:** When dependencies are broken, fix them locally to verify changes, but be careful about committing global dependency changes without explicit instruction.
