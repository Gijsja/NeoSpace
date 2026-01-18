## 2026-01-11 - [Middleware N+1 Query]
**Learning:** Middleware hooks like `before_request` in Flask execute for EVERY request, including static assets if served by the app. A DB query here is a hidden performance killer.
**Action:** Always filter `request.path` in global middleware to exclude static/asset paths before running expensive operations.

## 2026-01-18 - [Stress Test DB Corruption Risk]
**Learning:** `tests/stress_test.py` does not correctly inject the temporary database path into the application configuration. Running it wipes/corrupts the local development database (`neospace.db`) because `create_app()` defaults to the production/dev config.
**Action:** Do NOT run `stress_test.py` locally without fixing the config injection or using a throwaway environment. Use `tests/test_performance.py` instead.
