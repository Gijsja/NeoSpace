# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-29 - Unauthenticated Backfill Data Leak
**Vulnerability:** The HTTP endpoint `/backfill` (served by `queries/backfill.py`) allowed unauthenticated users to retrieve the entire message history of the application without pagination.
**Learning:** Redundant or legacy endpoints that duplicate WebSocket functionality can become forgotten backdoors if not audited.
**Prevention:** Regularly audit `routes/` for endpoints that expose sensitive data and verify they have `@login_required` or equivalent checks. Remove redundant HTTP endpoints if WebSockets are the primary transport.

## 2026-01-29 - Unbounded WebSocket Query
**Vulnerability:** The WebSocket event `request_backfill` queried messages with `WHERE id > ?` but without a `LIMIT` clause.
**Learning:** Infinite scroll implementations often neglect the server-side `LIMIT`, relying on the client to ask for small chunks. A malicious or buggy client requesting `after_id=0` triggers a full table scan and massive payload.
**Prevention:** Always enforce server-side `LIMIT` on list queries, regardless of client parameters.
