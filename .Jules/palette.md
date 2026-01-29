## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2025-10-26 - [Alpine.js Interactive Components]
**Learning:** Found interactive macros (like password toggles) in `ui_macros.html` lacking keyboard accessibility (negative tabindex) and screen reader support (missing aria-labels).
**Action:** When using Alpine.js for interactivity, ensure `x-bind:aria-label` is used for dynamic state and `focus-visible` classes are added for keyboard users.
