# Sentinel Journal

## 2026-01-11 - Auth Rate Limiting Gap
**Vulnerability:** Authentication endpoints (`/auth/login`, `/auth/register`) were completely unrestricted, allowing brute-force attacks.
**Learning:** Even with `Flask-Limiter` initialized globally, standard `Blueprint` routes are not automatically protected unless explicitly decorated or configured with default limits.
**Prevention:** Audit all `Blueprint` routes for `@limiter` decorators, especially those handling credentials or expensive operations.

## 2026-01-31 - Path Traversal in File Serving
**Vulnerability:** The `serve_unsharded_user_file` endpoint blindly accepted `category` URL parameter and used it to construct a directory path, allowing authenticated users to traverse up and access arbitrary files in the uploads directory.
**Learning:** `send_from_directory` only protects the final `filename` from traversal. It does NOT protect against traversal in the `directory` argument itself if that directory is constructed from user input.
**Prevention:** Always validate and sanitize all user-supplied path segments (like `category`) before passing them to `os.path.join`, even if `send_from_directory` is used later.
