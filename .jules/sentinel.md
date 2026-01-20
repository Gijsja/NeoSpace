# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-20 - Unauthenticated Chat History Dump
**Vulnerability:** The `/backfill` and `/unread` endpoints in `routes/chat.py` were not decorated with `@login_required`, allowing any unauthenticated user to download the entire message history and metadata.
**Learning:** When using `Blueprint.add_url_rule` with imported view functions, it's easy to forget applying decorators like `@login_required` that might otherwise be on the function definition itself.
**Prevention:** Verify all routes added via `add_url_rule` include necessary security wrappers, especially for sensitive data retrieval endpoints.
