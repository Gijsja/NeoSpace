# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-14 - Unauthenticated Message Backfill Leak
**Vulnerability:** The `/backfill` endpoint in `chat` blueprint was accessible without authentication and dumped all messages from all rooms.
**Learning:** `bp.add_url_rule` accepts a view function as is. If the function isn't decorated with `@login_required` (either in definition or when passed), it's public.
**Prevention:** When using `add_url_rule`, always verify if the view function needs `@login_required` wrapper. Prefer decorating the function definition if it's always protected.
