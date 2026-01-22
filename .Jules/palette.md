## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2025-05-23 - Interactive Helper Accessibility
**Learning:** Using `tabindex="-1"` on interactive helper elements (like password toggles) forces users to rely on mouse interaction, excluding keyboard users entirely. This is a common anti-pattern in "icon-only" helpers.
**Action:** Always ensure helper buttons are in the tab order and have `aria-label` attributes describing their function and current state. Use `focus-visible` to style focus states without affecting mouse users.
