# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-15 - Unprotected Routes via add_url_rule
**Vulnerability:** The `/backfill` and `/unread` endpoints in `routes/chat.py` were accessible to unauthenticated users, leaking full chat history.
**Learning:** Routes registered via `bp.add_url_rule()` do not automatically inherit `@login_required` or other security middleware unless explicitly wrapped (e.g., `login_required(view_func)`).
**Prevention:** Always verify that view functions passed to `add_url_rule` are wrapped with necessary security decorators, especially for sensitive data endpoints.
