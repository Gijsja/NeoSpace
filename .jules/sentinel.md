# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-14 - Resource Exhaustion Gaps in Uploads and Search
**Vulnerability:** File upload endpoints (`/wall/post/upload`, `/chat/upload`) and search (`/search/`) were unrestricted, posing risks of DoS via disk filling or CPU exhaustion.
**Learning:** Shared logic functions (like mutations) used across multiple blueprints need their own decorators or must be decorated at the route registration level. Decorating the underlying function (e.g., `upload_file` in `mutations/`) is an effective way to secure all consumers at once.
**Prevention:** When refactoring logic into "mutations" or "services", ensure security constraints (rate limits, permissions) travel with the logic or are strictly enforced at all entry points.
