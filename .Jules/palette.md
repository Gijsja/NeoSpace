## 2024-05-22 - Skip Link Implementation
**Learning:** Alpine.js forms with artificial delays and `@submit.prevent` can be tricky to automate with Playwright `click()`. Using keyboard simulation (`press("Enter")`) on the final input is a more robust way to trigger submission events in this specific stack.
**Action:** When testing Alpine.js forms in this repo, prefer keyboard interactions for submission over button clicks if button clicks fail to trigger state changes.

## 2024-05-23 - Interactive Helpers Accessibility
**Learning:** Found interactive helper buttons (password toggle) configured with `tabindex="-1"`, likely to prevent "cluttering" tab order for mouse users, but this renders them inaccessible to keyboard users.
**Action:** Always check `tabindex` on interactive elements inside macros. Interactive helpers must be keyboard accessible. Use `aria-label` to clarify their purpose.

## 2024-05-23 - Alpine.js ARIA Attributes
**Learning:** Alpine.js removes attributes when the bound value is `false`. For ARIA attributes like `aria-pressed` that need to persist as `"false"`, use a ternary expression: `:aria-pressed="show ? 'true' : 'false'"`.
**Action:** Use string values for boolean ARIA attributes in Alpine.js bindings.
