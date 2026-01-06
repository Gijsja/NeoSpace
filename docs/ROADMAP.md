# LocalBBS "Creative OS" Roadmap

We are transforming LocalBBS from a chat app into a **Creative Communication Operating System**. This roadmap aligns with the "4 Pillars of Innovation" from our design mockups.

### Sprint #7 (SHIPPED ✅)

**Theme**: Identity & Transparency

- Wall Guestbook (Stickers)
- System Internals (Connection Doctor)
- UI Polish & Mobile Responsiveness

---

## Future Sprints

### Sprint #8 (SHIPPED ✅)

**Theme**: Creative Sovereignty (The Sandbox)

- Data Layer (Scripts Table & API)
- The Sandbox UI (Editor & Runner)
- Verification (Persistence & Safety)

### Sprint #9 (SHIPPED ✅)

**Theme**: Sonic Identity

**Goal**: Allow users to record and display a "Voice Intro" on their profile with a rich waveform visualization.

- [x] **Database & Backend**:
  - [x] Add `voice_intro` and `voice_waveform` columns to `profiles`.
  - [x] create `/profile/voice` upload endpoint.
- [x] **UI: Recording**:
  - [x] Create `voice-recorder` component.
  - [x] Implement `MediaRecorder` logic + real-time canvas visualizer.
- [x] **UI: Playback**:
  - [x] Add "Voice Card" to `wall.html`.
  - [x] Interactive waveform player (click to seek).

## Upcoming

### Sprint #10: Unified Desktop (The Dashboard)

**Goal**: The "Mega-View" for power users.

- **Dashboard Layout**: 3-pane view unifing Nav, Chat, and Context.
- **Mini-Wall**: Compact profile summary in the side panel.
- **Electron Polish**: Native window controls and system tray.

---

## Legacy Roadmap (Archived)

### Sprint #1 (SHIPPED ✅)

**Theme**: Foundation & UI Scaffold

- Git init + Tailwind CSS
- Three-pane dashboard
- Feature page scaffolds

### Sprint #2 (SHIPPED ✅)

**Theme**: Chat Functionality Polish

- Fix message hover actions
- Sidebar interaction sync
- Typing indicators

### Sprint #3 (SHIPPED ✅)

**Theme**: Backend Integration

- Live WebSocket Connection
- Persistent Room State

### Sprint #4 (SHIPPED ✅)

**Theme**: Data Persistence

- Message Timestamps
- File Uploads

### Sprint #5 (SHIPPED ✅)

**Theme**: Authentication

- Standard User/Pass Auth
- Session Management

### Sprint #6 (SHIPPED ✅)

**Theme**: User Profiles

- Customizable Profile Wall
- Direct Messages with Encryption
- User Directory
