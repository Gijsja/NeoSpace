# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-24 - Unauthenticated Data Exposure in Chat
**Vulnerability:** The `/backfill` endpoint in `routes/chat.py` was exposed without authentication, allowing any user to download the entire message history.
**Learning:** `add_url_rule` does not automatically apply blueprint-level protections or decorators unless explicitly wrapped (e.g., `login_required(view_func)`).
**Prevention:** Always verify that sensitive endpoints registered via `add_url_rule` or `route` decorators have explicit authentication checks, especially when refactoring or splitting routes.
