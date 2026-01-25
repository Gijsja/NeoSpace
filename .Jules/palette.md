## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2025-01-28 - Accessible Password Toggles
**Learning:** Interactive elements inside macros (like password toggles) often get `tabindex="-1"` to avoid "cluttering" the tab order, but this excludes keyboard users completely.
**Action:** Always check `tabindex` on interactive icons/buttons and ensure they have visible focus states (`focus-visible`) and appropriate ARIA attributes (`aria-label`, `aria-pressed`) when using Alpine.js state.
