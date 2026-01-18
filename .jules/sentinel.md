# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-18 - Unprotected Helper Routes
**Vulnerability:** The `/backfill` and `/unread` endpoints in `routes/chat.py` were added via `add_url_rule` without `login_required`, bypassing authentication despite being sensitive.
**Learning:** Routes added via `Blueprint.add_url_rule` do not automatically inherit security decorators. They must be explicitly wrapped (e.g., `login_required(view_func)`).
**Prevention:** Audit all `add_url_rule` calls. Use `@blueprint.route` decorators where possible for better visibility, or explicit wrappers.
