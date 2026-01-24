## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-12 - [SQLite Deferred Row Loading]
**Learning:** SQLite can skip loading the main table page during an ORDER BY if the index contains the sort key (even if it's not a fully covering index). This "Deferred Row Loading" reduced a feed query from 0.011s to 0.0002s (50x speedup) by avoiding random access to the main table for rows that are eventually discarded by `LIMIT`.
**Action:** When sorting by `created_at` with a `LIMIT`, ensure `created_at` is in the index used for filtering (e.g., `(profile_id, created_at)`), even if other columns are needed for the result.
