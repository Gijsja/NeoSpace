## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-22 - Keyboard Accessibility for Interactive Helpers
**Learning:** Custom interactive elements inside forms (like "Show Password" toggles) are often overlooked in keyboard navigation. Explicitly managing `tabindex`, `aria-label`, and `focus-visible` states is critical for ensuring these helpers are accessible to keyboard and screen reader users.
**Action:** When creating or reviewing UI macros that include interactive buttons, always verify they are reachable via Tab key and announce their state changes to screen readers.
