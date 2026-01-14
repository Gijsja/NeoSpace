## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-23 - Interactive Macros Accessibility
**Learning:** The project's UI macros (specifically `ui_macros.html`) often hardcode `tabindex="-1"` on interactive elements like password toggles, making them keyboard inaccessible by default.
**Action:** When using or modifying UI macros, always check and override `tabindex` and ensure dynamic ARIA labels are present for state-changing buttons.
