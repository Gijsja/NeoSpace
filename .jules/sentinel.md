# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-21 - Unauthenticated Chat History
**Vulnerability:** The `/backfill` and `/unread` endpoints in `routes/chat.py` were accessible without authentication, potentially exposing chat history to unauthorized users.
**Learning:** Routes added via `Blueprint.add_url_rule` do not automatically inherit security decorators; `@login_required` must be explicitly applied to the view function or passed as a decorator to `add_url_rule`.
**Prevention:** Always verify authentication requirements for new endpoints, especially those returning user data, and write negative tests (unauthorized access) to confirm protection.
