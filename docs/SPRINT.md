# Sprint 25: The Facelift (UI/UX)

**Date Range**: 2026-01-11 to 2026-01-18

## Goals

1.  **Visual Consistency**: Audit and unify all UI elements (buttons, inputs, spacing) to strict Neubrutalist guidelines.
2.  **Micro-interactions**: Implement smooth transitions, hover states, and loading skeletons.
3.  **Mobile Polish**: Ensure core views (Wall, Chat, Feed) are 100% usable on mobile.

## Backlog

### 🎨 Visual Consistency ("The Audit")
- [ ] **Tailwind Config Review**: Unify color palette and spacing tokens in `tailwind.config.js`.
- [ ] **Component Standardization**:
  - [ ] Buttons (Primary, Secondary, Danger, Ghost).
  - [ ] Inputs (Text, Textarea, Select, Checkbox).
  - [ ] Cards/Containers (Border widths, shadows).
- [ ] **Typography**: Verify font weights and line heights across headers and body.

### ✨ Micro-interactions ("The Juice")
- [ ] **Transitions**: Add `x-transition` to all dropdowns, modals, and toasts.
- [ ] **Loading States**: Replace full-page spinners with component-level skeletons.
- [ ] **Feedback**: Add click/press states to all interactive elements.

### 📱 Mobile Polish ("The Squeeze")
- [ ] **Navigation**: Verify hamburger menu / bottom bar usage.
- [ ] **Chat View**: Ensure input doesn't get hidden by keyboard.
- [ ] **Wall View**: Fix masonry layout on single-column screens.

## Acceptance Criteria
- Style guide (`playground.html`) matches implementation.
- No horizontal scrolling on mobile (iPhone SE width).
- All interactive elements provide visual feedback.
