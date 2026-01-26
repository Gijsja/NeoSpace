# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-20 - File Path Traversal
**Vulnerability:** The `serve_unsharded_user_file` route allowed path traversal because the `category` URL parameter was used in `os.path.join` without validation, enabling access to parent directories.
**Learning:** While `send_from_directory` protects the `filename` argument, it does not protect the directory path itself if it's constructed from user input.
**Prevention:** Always validate and sanitize user input before using it in filesystem path construction, even if using "safe" functions like `send_from_directory` for the final step.
