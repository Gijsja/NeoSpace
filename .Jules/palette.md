## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-10-24 - Accessibility Anti-Pattern: Explicit Tab Removal
**Learning:** Legacy UI macros in this codebase explicitly removed interactive helper elements (like password toggles) from the tab order using `tabindex="-1"`. This forces keyboard users to skip these controls entirely.
**Action:** When auditing legacy components, explicitly check for and remove `tabindex="-1"` on interactive elements unless they are truly decorative or managed by a roving tabindex.
