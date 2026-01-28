# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-28 - Unbounded WebSocket Backfill
**Vulnerability:** The `request_backfill` WebSocket event allowed fetching the entire message history (`SELECT * WHERE id > 0`), enabling DoS via memory/bandwidth exhaustion.
**Learning:** WebSocket event handlers often bypass standard HTTP middleware (like pagination or rate limiting) if not explicitly implemented. "Real-time" code often prioritizes speed over safety controls found in REST APIs.
**Prevention:** Enforce hard `LIMIT` clauses on all list-returning WebSocket events and implement "initial load" vs "sync" pagination strategies.
