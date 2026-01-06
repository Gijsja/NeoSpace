# Developer Log (DEVLOG)

One continuous log of all development sessions.

---

## Session: 2026-01-06 (Sprint 10 & 11)

### Focus

- **Sprint 10 Completion**: Unified Desktop, Context Pane, Window Controls.
- **Sprint 11 Quick Wins**: Audio Anthem, Vision to Docs.
- **Cleanup**: Documentation professionalization.

### 1. Unified Desktop (Sprint 10)

**Context Pane Enhancements**:

- Updated `queries/directory.py` to fetch `status_message`, `now_activity`, `voice_intro_path`, and `anthem_url`.
- Updated `desktop.html` to display a "Mini Profile" in the right sidebar.
- Added playback controls for "Voice Intro" directly in the side pane.

**Electron Polish**:

- Added `-webkit-app-region: drag` to the top header for native window dragging.
- Added Mac-style traffic light buttons (Red/Yellow/Green) for visual parity.

### 2. Audio Anthem (Sprint 11 Quick Win)

**Goal**: Allow users to set a background music track for their profile.

- **DB**: Added `anthem_url` and `anthem_autoplay` to `profiles`.
- **Backend**: Updated `profile.py` mutations.
- **Frontend**: Added hidden `<audio>` player to `wall.html`.
- **UI**: Added a floating "Mute/Unmute" toggle button.

### 3. Documentation Pivot

- **NeoSpace Manifesto**: Updated `PRINCIPLES.md` to officialize the "Anti-Social Network" vision.
- **Unfrozen Core**: Removed "Epoch" constraints; moved to standard **Agile Sprints**.
- **Renames**: `EVOLUTION.md` -> `HISTORY.md`.
- **Cleanup**: Moved corporate guides to `docs/specs/`.

### 4. Previous Session: UI Polish & Pinned Scripts (Earlier on Jan 6)

**Design System Updates (`styles.css`)**:

- Added glass variants, micro-interactions, and consistent animations.
- Polished Login, Desktop, and Directory views.

**Pinned Scripts**:

- Users can now pin Sandbox scripts to their profile wall.
- Implemented `profile_scripts` table and corresponding API endpoints.
- Added "Run Preview" modal with sandboxed iframe.

---
