# Sprint 25: The Facelift (UI/UX)

**Date Range**: 2026-01-11 to 2026-01-18

## Goals

1.  **Visual Consistency**: Audit and unify all UI elements (buttons, inputs, spacing) to strict Neubrutalist guidelines.
2.  **Micro-interactions**: Implement smooth transitions, hover states, and loading skeletons.
3.  **Mobile Polish**: Ensure core views (Wall, Chat, Feed) are 100% usable on mobile.

## Backlog

### 🎨 Visual Consistency ("The Audit")
- [x] **Sidebar Refactor**: Reorganized navigation and added "Review" / "Features" sections.
- [x] **User Directory**: Wired up `/directory` to show users by default.
- [x] **Tailwind Config Review**: Unified color palette and type scale in `ui/js/tailwind_config.js` (Runtime) & `tailwind.config.js`.
- [x] **Component Standardization**: Created `ui_macros.html` library.
  - [x] Buttons (Primary, Secondary, Danger, Ghost, Outline).
  - [x] Inputs (Standardized with Neobrutalist borders).
  - [x] Cards/Containers (Hard shadows and consistent padding).
  - [x] Badges (Variant support added).
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
