## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2026-01-16 - Dependency Conflict Resolution
**Learning:** `requirements.txt` pins were incompatible with `Flask==3.1.2` (requires `blinker>=1.9`, `itsdangerous>=2.2`, `Werkzeug>=3.1`). The repo was broken for fresh installs.
**Action:** When dependencies conflict with strict pins, verify the upstream requirements of the primary framework (Flask) and update the pinned versions of its direct dependencies to match the minimum requirements.
