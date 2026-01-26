## 2026-01-26 - [Socket Backfill Pagination]
**Learning:** Initial full data loads (like chat history) via WebSocket must be paginated to prevent memory exhaustion and slow start times.
**Action:** Limit initial loads (e.g., `after_id=0`) to a fixed count (e.g., 100) using `ORDER BY id DESC LIMIT N` in a subquery, then re-sorting. Cap sync requests (`after_id > N`) to a reasonable batch size (e.g., 500).
