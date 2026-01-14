## 2026-01-14 - [Unbounded Query in Hot Path]
**Learning:** The `/backfill` endpoint (both HTTP and Socket.IO) was executing `SELECT * FROM messages` without any LIMIT or room filtering. This is a classic "works in dev, explodes in prod" pattern.
**Action:** Always enforce hard LIMITs on list endpoints and ensure `WHERE` clauses filter by the parent entity (e.g., `room_id`). Defaulting to a safe limit (e.g., 500) protects the DB from massive reads.
