## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-23 - Keyboard Trap in Helper Buttons
**Learning:** The `tabindex="-1"` attribute on helper buttons (like password visibility toggles) creates a keyboard trap for users who rely on tab navigation, preventing them from accessing critical form functionality.
**Action:** Ensure all interactive form helpers remain in the natural tab order (remove `tabindex="-1"`) and use `focus-visible` styles to maintain a clean aesthetic for mouse users while supporting keyboard navigation.
