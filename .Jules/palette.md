## 2024-05-22 - Toast Accessibility Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-22 - Toast ARIA Roles
**Learning:** Toast notifications implemented as dynamic overlays need explicit `role="log"` (or `status`/`alert`) and `aria-live="polite"` to be announced by screen readers. Pure visual overlays are invisible to AT users.
**Action:** Always verify "pop-up" messages have appropriate ARIA roles and live region attributes.
