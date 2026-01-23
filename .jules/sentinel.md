# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-13 - Path Traversal in File Serving
**Vulnerability:** The `serve_unsharded_user_file` endpoint allowed path traversal via `..` in the `category` parameter, enabling access to the uploads root directory.
**Learning:** Fallback routes often miss security checks applied to primary routes. Explicit input validation for directory components is critical even when using `send_from_directory` if the directory path itself is constructed dynamically.
**Prevention:** Ensure all file serving routes validate input parameters against `..` and restrict them to allowlisted characters where possible.
