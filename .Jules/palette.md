## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2025-05-23 - Interactive Helper Accessibility
**Learning:** Found a pattern where interactive helper buttons (like password toggles) were explicitly removed from the tab order using `tabindex="-1"`. This makes them completely inaccessible to keyboard users.
**Action:** Always audit icon-only helper buttons for `tabindex` and ensure they have accessible labels and visible focus states.
