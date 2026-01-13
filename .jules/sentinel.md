# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-13 - Unauthenticated Data Dump in Utility Route
**Vulnerability:** The `/backfill` endpoint dumped the entire `messages` table without authentication or limits.
**Learning:** Utility endpoints added for specific features (like WebSocket backfill) often escape standard security reviews if they are not part of the main CRUD flow.
**Prevention:** Always verify authentication and apply resource limits (LIMIT clauses) on all endpoints that return collections of data.
