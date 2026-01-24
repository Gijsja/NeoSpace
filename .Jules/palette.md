## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-22 - Keyboard Access for Custom Controls
**Learning:** Custom interactive elements like "show password" toggles inside inputs are often excluded from the tab order (`tabindex="-1"`) to avoid clutter, but this makes them inaccessible to keyboard users.
**Action:** Always ensure interactive helper buttons are keyboard-focusable and use `aria-label` and `aria-pressed` (or similar) to communicate state changes dynamically.
