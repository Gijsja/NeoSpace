# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-26 - Inconsistent Path Traversal Checks
**Vulnerability:** The `serve_unsharded_user_file` route lacked the manual path traversal (`..`) checks present in its sibling `serve_user_file` route, potentially allowing directory escape.
**Learning:** Manual security checks duplicated across similar routes are prone to being missed in one or more instances.
**Prevention:** Centralize path validation logic into a single helper function or decorator applied to all file-serving endpoints to ensure consistent security controls.
