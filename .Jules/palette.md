## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-24 - Custom UI Macro Accessibility
**Learning:** The project's custom `ui_macros.html` library explicitly disables keyboard focus on helper buttons (using `tabindex="-1"`) and lacks ARIA labels, making form interactions like password toggles inaccessible to screen reader and keyboard users.
**Action:** Audit all components in `ui_macros.html` for `tabindex="-1"` usage on interactive elements and ensure ARIA labels are bound to dynamic Alpine.js state where appropriate.
