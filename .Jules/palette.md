## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-24 - Accessible Helper Buttons
**Learning:** Helper buttons in `ui_macros.html` (like password toggles) were hardcoded with `tabindex="-1"`, making them inaccessible to keyboard users. This seems to be a legacy pattern for "icon-only" buttons to prevent them from stopping the tab flow, but it violates WCAG.
**Action:** Always check `tabindex` on macro-generated components. Interactive elements must be focusable. Used `focus-visible` to style the focus ring only when navigating by keyboard, preserving the clean look for mouse users.
