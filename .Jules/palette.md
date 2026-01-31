## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2025-05-23 - Reusable Component Accessibility
**Learning:** Common UI macros (like inputs with password toggles) can silently propagate accessibility issues (like `tabindex="-1"`) across the entire application if not carefully vetted. Fixing it in one macro fixes it everywhere.
**Action:** Audit `ui_macros.html` periodically as it's the source of truth for many components.
