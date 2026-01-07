# NeoSpace "Creative OS" Roadmap

We are transforming NeoSpace from a chat app into a **Creative Communication Operating System**. This roadmap aligns with the "4 Pillars of Innovation" from our design mockups.

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

### Quick Wins (Sprint 11 Early Access) ✅

**Theme**: NeoSpace Foundations

- [x] **Audio Anthem**: Profile background music with autoplay and mute controls.
- [x] **Vision to Docs**: Updated `PRINCIPLES.md` with the "NeoSpace Manifesto" (Anti-algorithm, Chaos, User Ownership).

## Upcoming

### Sprint #10 (SHIPPED ✅)

**Theme**: Unified Desktop (The WebOS)

**Goal**: The "Mega-View" for power users.

- [x] **Desktop Shell**: 3-pane layout (Chat / Stage / Context).
- [x] **Tool Integration**: Sandbox, Wall, and Internals running in the stage.
- [x] **Context Pane**: Dynamic side-panel (Voice/Docs).
- [x] **Electron Polish**: Native window controls.

### Sprint #11 (SHIPPED ✅)

**Theme**: NeoSpace Foundations

- [x] **Audio Anthem**: Profile background music.
- [x] **Identity First**: Hero blocks and status lines.

### Sprint #12 (IN PROGRESS 🚧)

**Theme**: The Modular Canvas

**Goal**: Transform the profile wall into a mixed-media masonry grid.

- [ ] **Data Layer**: Generic `profile_posts` table (Text, Image, Link).
- [ ] **UI**: Unified Masonry Grid for Scripts + Posts.
- [ ] **Modules**:
  - [ ] **Note Block**: Markdown text.
  - [ ] **Image Block**: visual media.
  - [ ] **Link Block**: "Current Obsession" preview.

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
