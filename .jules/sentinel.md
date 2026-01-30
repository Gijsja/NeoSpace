# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-14 - Path Traversal in File Download
**Vulnerability:** The `serve_unsharded_user_file` endpoint allowed path traversal via the `category` URL parameter, enabling access to arbitrary files.
**Learning:** `os.path.join` resolves `..` segments, and `send_from_directory` only validates the final filename against the provided directory path. If the directory path itself is constructed using unvalidated user input containing `..`, the jail is broken.
**Prevention:** Always validate all path components against `..` before passing them to `os.path.join` or `send_from_directory`.
