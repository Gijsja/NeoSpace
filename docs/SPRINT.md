# LocalBBS Sprint Tracker

## Current Sprint: #2 (SHIPPED ✅)

**Dates**: Jan 5-6, 2026  
**Theme**: Chat Functionality Polish

### Sprint Goals

- [x] Fix message hover actions (group-hover CSS)
- [x] Make sidebar rooms clickable (visual state sync)
- [x] Add typing indicators (animated dots + socket events)
- [x] Test with real WebSocket connection
- [x] Style refinements

### Shipped

All goals completed. ✅

---

## Previous Sprints

### Sprint #1 (SHIPPED ✅)

**Theme**: Foundation & UI Scaffold

- Git init + Tailwind CSS
- Three-pane dashboard
- Feature page scaffolds (Wall, Code Editor, Internals)
- Navigation wiring

---

## Sprint #3: Backend Integration & Live Testing (SHIPPED)

**Goal:** Verify WebSocket connectivity, fix server issues, and implement persistent state.

**Shipped Features:**

- [x] **Live WebSocket Connection**: Fixed `socket_glue.js` loading and server binding.
- [x] **Emoji Picker**: Added `emoji-picker-element` with UI integration.
- [x] **Persistent Room State**: Remembers last visited room across reloads.
- [x] **Server Accessibility**: Bound to `0.0.0.0` for full access.

### Next Steps (Sprint #4)

- [ ] **Message History**: Implement database storage for messages.
- [ ] **User Accounts**: Basic auth or session persistence.
- [ ] **File Uploads**: Drag and drop support.

---

## Backlog

### UI Polish

- [ ] Sticker drag-and-drop on wall
- [ ] Voice recording for voice intro
- [ ] Code editor syntax highlighting (CodeMirror/Monaco)

### Backend

- [ ] Multi-room support
- [ ] User authentication
- [ ] Persistent user profiles

### Creative Features

- [ ] Three.js/p5.js sandbox execution
- [ ] Code sharing to chat
- [ ] Ambient lobby visualization
