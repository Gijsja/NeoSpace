## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-23 - Interactive Helper Buttons
**Learning:** Helper buttons inside input wrappers (like password toggle) were explicitly removed from tab order (`tabindex="-1"`), making them inaccessible to keyboard users. This seems to be a pattern to avoid cluttering the tab order, but it excludes critical functionality.
**Action:** Always ensure interactive helper elements inside inputs are keyboard accessible (tabindex="0" or default) and provide clear focus indicators (e.g., `focus-visible:ring`).
