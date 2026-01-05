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

### Sprint #4: Data Persistence & File Sharing

- [ ] **Message Timestamps**: Add `created_at` to schema, display in UI
- [ ] **File Uploads**: Drag-and-drop images to chat
- [ ] **Image Display**: Render uploaded images inline

### Sprint #5: OAuth Login (Google + Apple)

- [ ] **Google OAuth**: Cloud Console setup + credentials
- [ ] **Apple Sign-In**: Developer account + Sign in with Apple setup
- [ ] **Login Page**: Unified UI with Google & Apple buttons
- [ ] **OAuth Flow**: `/auth/google` + `/auth/apple` → callbacks → session
- [ ] **User Creation**: Auto-create user on first login (either provider)
- [ ] **Account Linking**: Link Google/Apple to same user if email matches
- [ ] **Session Management**: Secure HTTPOnly cookies, logout endpoint
- [ ] **Protected Routes**: Require auth for chat/profile

### Sprint #6: User Profiles & Social Wall

- [ ] **Profiles Table**: Bio, avatar, custom CSS storage
- [ ] **Profile Page**: Customizable wall (MySpace 2.0 style)
- [ ] **Direct Messages**: Private 1:1 chat with encryption at rest
- [ ] **User Directory**: Browse/search other users

### Sprint #7: Review, Views & Polish

- [ ] **Wall View**: Finish `wall.html` with sticker drag-drop
- [ ] **Code Editor**: Wire up Monaco/CodeMirror integration
- [ ] **Internals View**: Real connection stats in `internals.html`
- [ ] **UI Polish**: Animations, transitions, mobile responsive
- [ ] **Accessibility**: ARIA labels, keyboard navigation

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
