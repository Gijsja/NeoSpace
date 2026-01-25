# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-25 - Path Traversal in File Serving
**Vulnerability:** Authenticated users could bypass the user directory structure by passing `..` in the `category` parameter of `serve_unsharded_user_file`, allowing access to the uploads root.
**Learning:** Inconsistent validation logic (present in `serve_user_file` but missing in `serve_unsharded_user_file`) creates security gaps.
**Prevention:** Centralize path validation logic or ensure all file serving routes use the same strict validation utility.
