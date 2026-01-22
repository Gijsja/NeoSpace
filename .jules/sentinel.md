# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-22 - Unauthenticated Chat History
**Vulnerability:** Chat history (`/backfill`) and unread counts (`/unread`) were accessible without authentication, allowing data leakage.
**Learning:** `Blueprint.add_url_rule` does not inherit `@login_required` from the blueprint or module level; it must be applied explicitly to the view function.
**Prevention:** When using `add_url_rule`, verify if the target view function requires authentication and wrap it with `login_required` if necessary.
