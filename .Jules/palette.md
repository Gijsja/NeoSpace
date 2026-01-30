## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-23 - Custom Interactive Elements Accessibility
**Learning:** Custom interactive elements (like password toggles) hidden from the tab order via `tabindex="-1"` are inaccessible to keyboard users.
**Action:** Always ensure interactive elements are focusable and have visible focus states (`focus-visible:ring`), even if the default outline is removed.
