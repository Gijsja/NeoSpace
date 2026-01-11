# NeoSpace Documentation

> Unified technical specification for the NeoSpace platform.

---

# Project Overview

<!-- Refactored from: BLUEPRINT.md "Philosophy", NEOSPACE_ARCHITECTURE.md "Directive" -->

**NeoSpace** is a server-authoritative, WebSocket-driven creative communication platform. A modern reinterpretation of classic BBS and early social web aesthetics (MySpace, forums, GeoCities) with a strong anti-algorithm philosophy.

> **The server is the single source of truth. Always.**

This system trades convenience for reliability. Every decision prioritizes correctness over velocity.

## Hardware Constraints

- **Host**: 2013 Mac (Dual Core, 8-16GB RAM) running Linux
- **Philosophy**: No Docker. No build steps. No "Clean Architecture" boilerplate.

## Key Views

<!-- Refactored from: BLUEPRINT.md "Key Views" -->

| View        | Purpose                        |
| ----------- | ------------------------------ |
| Login       | Authentication with tab toggle |
| Chat        | Main messaging interface       |
| Wall        | Personal Identity Canvas       |
| Code Editor | Creative Sandbox               |
| Directory   | User discovery                 |
| Desktop     | Unified 3-pane power view      |

---

# Design Principles

## The NeoSpace Manifesto

<!-- Refactored from: BLUEPRINT.md "The NeoSpace Manifesto" -->

**"The Anti-Social Network"**

1. **Anti-algorithm**: No recommendations, only exploration
2. **User Ownership**: Your data is yours. Profiles are raw, not forms
3. **Chaos as Feature**: If it breaks, it's art
4. **Social Without Performance**: No likes, no counts, just vibes

## The 4 Pillars

<!-- Refactored from: BLUEPRINT.md "The 4 Pillars" -->

| Pillar                   | Description                          |
| ------------------------ | ------------------------------------ |
| **Identity Canvas**      | Dynamic, customizable profile walls  |
| **Radical Transparency** | System Internals expose the metal    |
| **Creative Sovereignty** | Embedded code sandbox for expression |
| **Organic Presence**     | Visualize human connection           |

## The Five Invariants

<!-- Refactored from: PROTOCOL.md "The Five Invariants" -->

Violating any invariant is a **critical bug**.

| #   | Invariant              | Implication                                           |
| --- | ---------------------- | ----------------------------------------------------- |
| 1   | **Server Authority**   | Client never derives state locally                    |
| 2   | **No Inference**       | State comes only from `message` and `backfill` events |
| 3   | **Canonical Backfill** | `request_backfill` yields exact same state as live    |
| 4   | **Safe Deletion**      | Deleted content returned as `null`, never leaked      |
| 5   | **Idempotency**        | Multiple reconnects produce same result               |

## The Laws

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "The Laws" -->

1. **Short Transactions**: Never perform I/O inside `with db:`. Prepare files first, then commit.
2. **No Over-Abstraction**: Reject Repository/Clean Architecture patterns. Use vertical slices.
3. **Hybrid Caching**: Public data → Caddy (HTTP cache); Private data → Python `lru_cache`; No Redis unless necessary.
4. **msgspec for Speed**: Use `msgspec.Struct` for hot-path JSON.

## Chesterton's Fence Rule

<!-- Refactored from: PROTOCOL.md "The Chesterton's Fence Rule" -->

> Do not delete code unless you understand why it exists.

- `routes/` — Core business logic, preserve
- `mutations/` — All state changes, preserve
- `queries/` — Read operations, preserve
- When uncertain, keep legacy running in parallel

---

# Architecture

## System Diagram

<!-- Refactored from: BLUEPRINT.md "Architecture" -->

```
┌─────────────┐     WebSocket      ┌─────────────┐
│   Client    │◄──────────────────►│   Server    │
│  (Browser)  │     HTTP REST      │   (Flask)   │
└─────────────┘◄──────────────────►└──────┬──────┘
                                          │
                                   ┌──────▼──────┐
                                   │   SQLite    │
                                   │   (WAL)     │
                                   └─────────────┘
```

## Evolution Layers

<!-- Refactored from: BLUEPRINT.md "Evolution Layers" -->

| Layer  | Name        | Status    | Scope                                 |
| ------ | ----------- | --------- | ------------------------------------- |
| **E1** | The Bedrock | 🛡️ Frozen | Backend semantics, DB schema, sockets |
| **E2** | UX          | 🔄 Active | Layout, interactions, styling         |

## Technology Stack

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "The 'Max Juice' Technology Stack", PROTOCOL.md "The No-Build Stack" -->

| Layer             | Choice             | Rationale                                   |
| :---------------- | :----------------- | :------------------------------------------ |
| **Reverse Proxy** | Caddy              | Auto-HTTPS, Zstd compression, micro-caching |
| **App Server**    | Gunicorn gthread   | Thread-based workers; SQLite-friendly       |
| **Framework**     | Flask              | Lightweight, paired with Flask-SocketIO     |
| **Database**      | SQLite (WAL)       | Zero-latency, in-process. Tuned via PRAGMA  |
| **Serialization** | msgspec            | 10-80x faster than Pydantic                 |
| **Styling**       | Tailwind CSS (CDN) | No build required                           |
| **Reactivity**    | Alpine.js (CDN)    | Lightweight                                 |
| **Frontend**      | Vanilla JS         | HTML-over-WebSockets. No React, no Webpack  |

**FORBIDDEN:** React, Vue, Webpack, Vite, `npm`, `package.json`

## Database Configuration

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "Database 'God Mode' Configuration" -->

```python
db = sqlite3.connect('app.db', timeout=15)  # 15s retry window

db.execute('PRAGMA journal_mode = WAL;')           # Readers don't block writers
db.execute('PRAGMA synchronous = NORMAL;')         # Balanced durability
db.execute('PRAGMA cache_size = -512000;')         # 512MB RAM cache
db.execute('PRAGMA mmap_size = 2147483648;')       # 2GB memory-mapped I/O
db.execute('PRAGMA temp_store = MEMORY;')          # Sorts in RAM
```

### Database Schema

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "Database Schema" -->

**Core Tables:**

| Table             | Purpose                                                |
| ----------------- | ------------------------------------------------------ |
| `users`           | User accounts (username, bcrypt hash, avatar color)    |
| `messages`        | Chat messages (scoped by room_id)                      |
| `profiles`        | User profile data (bio, status, avatar, anthem, theme) |
| `direct_messages` | E2E encrypted DMs with per-user soft delete            |
| `scripts`         | User-created sandbox scripts (p5.js, Three.js)         |

**Feature Tables:**

| Table              | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `profile_stickers` | Draggable wall stickers (emoji, images)          |
| `profile_scripts`  | Pinned scripts on profile walls (max 3)          |
| `profile_stickers` | Draggable wall stickers (emoji, images)          |
| `profile_scripts`  | Pinned scripts on profile walls (max 3)          |
| `profile_posts`    | Modular canvas posts (text, image, link, script) |

### Cat System Engine

<!-- Refactored from: SPRINT.md "Sprint 26: Emotional Intelligence" -->

The Cat System is a deterministic emotional simulation engine driven by the **PAD Model** (Pleasure, Arousal, Dominance).

**Core Components:**

1.  **PAD State**: A 3-dimensional float vector `[P, A, D]` representing the cat's current emotion.
    *   **Pleasure**: Valence (Happy vs. Unhappy).
    *   **Arousal**: Energy (Excited vs. Bored).
    *   **Dominance**: Confidence (Dominant vs. Submissive).
2.  **Affinity Integration**: Relationships are calculated dynamically based on Faction compatibility (e.g., "Anarchs" love errors, "Sentinels" hate them).
3.  **Deed System**: Events are not just logs; they are "Deeds" with emotional impact (e.g., `login_success` = +Pleasure, `system_crash` = -Dominance).
4.  **Dynamic Assets**: Avatars switch states (Zen, Playful, Grumpy) based on real-time PAD values.

## Server Configuration

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "Server Configuration" -->

```bash
gunicorn -w 4 --threads 16 --worker-class gthread \
    --worker-tmp-dir /dev/shm --bind 0.0.0.0:5000 "app:create_app()"
```

| Setting      | Value    | Rationale                          |
| ------------ | -------- | ---------------------------------- |
| Workers      | 4        | One per core (2013 dual-core + HT) |
| Threads      | 16       | ~64 concurrent requests            |
| Worker class | gthread  | SQLite-compatible threading        |
| Tmp dir      | /dev/shm | RAM-backed heartbeat               |

## Caddy Configuration

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "The Caddy Layer" -->

```caddyfile
:80 {
    encode zstd gzip                              # Compression
    handle /static/* { file_server }              # Bypass Python
    @cacheable { method GET; path /wall/* }
    header @cacheable Cache-Control "max-age=1"   # Micro-cache
    reverse_proxy 127.0.0.1:5000                  # Flask backend
}
```

## Real-Time Protocol (Socket.IO)

<!-- Refactored from: PROTOCOL.md "Real-Time Protocol (Socket.IO)" -->

### Client → Server Events

| Event              | Payload             | Description                  |
| ------------------ | ------------------- | ---------------------------- |
| `join_room`        | `{room: string}`    | Join a chat room             |
| `send_message`     | `{content: string}` | Send message to current room |
| `request_backfill` | `{after_id: int}`   | Request message history      |
| `typing`           | `{}`                | Broadcast typing indicator   |
| `stop_typing`      | `{}`                | Clear typing indicator       |

### Server → Client Events

| Event         | Payload                                | Description           |
| ------------- | -------------------------------------- | --------------------- |
| `connected`   | `{ok, username}`                       | Connection confirmed  |
| `room_joined` | `{room, room_id}`                      | Room join confirmed   |
| `message`     | `{id, user, content, created_at, ...}` | New message broadcast |
| `backfill`    | `{phase, messages[]}`                  | Message history batch |
| `typing`      | `{user}`                               | User is typing        |
| `error`       | `{message}`                            | Error notification    |

## Directory Structure

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "Directory Structure" -->

```
SBBS/
├── app.py                 # Flask application factory
├── db.py                  # Database schema, connection pool, retry logic
├── auth.py                # Authentication blueprint (login/register/logout)
├── sockets.py             # WebSocket event handlers
├── core.crypto.py        # AES-256-GCM encryption utilities
│
├── routes/                # HTTP route blueprints
├── mutations/             # Database write operations
├── queries/               # Database read operations
├── templates/             # Jinja2 HTML templates
├── ui/                    # Static frontend assets
├── static/                # Uploaded files & assets
├── tests/                 # pytest test suite
├── scripts/               # Migration utilities
└── docs/                  # Documentation
```

## Startup Scripts

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "Startup Scripts" -->

| Script          | Purpose                          |
| --------------- | -------------------------------- |
| `startlocal.sh` | Dev mode with Flask debug server |
| `startprod.sh`  | Gunicorn gthread (no Caddy)      |
| `startstack.sh` | Full stack: Caddy + Gunicorn     |

## Debugging Runbook

<!-- Refactored from: PROTOCOL.md "Debugging Runbook" -->

> **Golden Rule:** Assume the client is wrong.

**Diagnostic Steps:**

1. **Check Socket Traffic** — DevTools → Network → WS tab
2. **Trigger Backfill** — `socket.emit("request_backfill", { after_id: 0 })`
3. **Check Server Logs** — `python startlocal.py`
4. **Restart Server** — Nuclear option

**Quick Reference:**

| Symptom          | Likely Cause     | Fix              |
| ---------------- | ---------------- | ---------------- |
| Messages missing | Missed broadcast | Trigger backfill |
| Wrong user       | Header missing   | Check `g.user`   |
| 500 errors       | Database locked  | Restart server   |

---

# Roadmap & History

## Current Sprint

<!-- Refactored from: BLUEPRINT.md "Roadmap" -->

**Sprint #27**: _The Creator Economy_ (Proposed)

**Goals**: Script sharing ecosystem, branching narratives ("The Song"), and deeper collaborative tools.

## Recently Shipped

| Sprint | Theme                      | Features                                              |
| ------ | -------------------------- | ----------------------------------------------------- |
| #26    | Emotional Intelligence     | PAD Model, Cat Factions, Dialogue Engine, Audio       |
| #25    | The Facelift (UI/UX)       | Visual Consistency, Micro-interactions, Mobile Polish |
| #24    | v0.4 Release               | Version Bump, Docs, Tagging                           |
| #23    | Feature Expansion          | Service tests, Alembic, Cat errors, Script publishing |
| #22    | Live Wire UI               | Notification Center, Badges, Toasts                   |
| #21    | The Feed UI                | Home Stream, Infinite Scroll                          |
| #20    | Social Actions UI          | Follow/Unfollow, Top 8 Grid                           |
| #19    | Search UI                  | Js-based Search, User/Post tabs                       |
| #18    | Security Hardening         | CSRF, CSP, Rate Limiting (Ironclad)                   |
| #17    | Search API                 | User and Post search endpoints                        |
| #16    | Feed API                   | `/feed` endpoint, Pagination                          |
| #15    | Live Wire                  | Notifications API, Follow triggers                    |
| #14    | Social Graph               | Friends, Top 8, Follow/Unfollow                       |
| #13    | Speed Demon                | msgspec structs for hot paths                         |
| #12    | Modular Canvas             | Profile posts (text/image/link/audio)                 |
| #11    | NeoSpace Foundations       | Audio Anthem, Identity First                          |
| #10    | Unified Desktop            | 3-pane layout, Tool Integration                       |
| #9     | Sonic Identity             | Voice Intros, Waveform Player                         |
| #8     | Creative Sandbox           | Scripts API, Code Editor                              |
| #7     | Identity & Transparency    | Wall Stickers, System Internals                       |
| #6     | User Profiles              | Profile Wall, DMs, Directory                          |

## Legacy Sprints

<!-- Refactored from: BLUEPRINT.md "Legacy Sprints (Historical)" -->

| Sprint | Theme               | Features                                 |
| ------ | ------------------- | ---------------------------------------- |
| #5     | Authentication      | Standard User/Pass Auth, Sessions        |
| #4     | Data Persistence    | Message Timestamps, File Uploads         |
| #3     | Backend Integration | Live WebSocket, Persistent Room State    |
| #2     | Chat Functionality  | Message Hover Actions, Typing Indicators |
| #1     | Foundation          | Git init, Tailwind CSS, 3-pane scaffold  |

## User Flow: The Creator Journey

<!-- Refactored from: BLUEPRINT.md "User Flow: The Creator Journey" -->

1. **Spark** — Open NeoSpace, enter Code Mode
2. **Studio** — Write code, hot-reload canvas, fix errors
3. **Release** — Publish to room with caption
4. **Resonance** — Receive sticker feedback, get forked

## Completed: Phase 4 (msgspec) ✅

<!-- Refactored from: NEOSPACE_ARCHITECTURE.md "Sprint Backlog: Phase 4 (msgspec)" -->

100% of JSON endpoints now use `msgspec.Struct` for hot-path serialization.

## Versioning

<!-- Refactored from: PROTOCOL.md "Versioning" -->

```
E<epoch>.<archive>.<patch>.<qualifier>
```

| Component   | Description              |
| ----------- | ------------------------ |
| `E`         | Epoch (E1=core, E2=UX)   |
| `archive`   | Feature archive          |
| `patch`     | Bugfix                   |
| `qualifier` | `full`, `partial`, `dev` |

**Example:** `E2.A1.1.full`

**Tagging Rules:**

- ✅ Tag when all tests pass
- ❌ Never tag broken builds

## Agile Process

<!-- Refactored from: PROTOCOL.md "Agile Process" -->

1. **Sprints**: 1-2 week cycles with themes
2. **Milestones**: Major feature clusters
3. **Quick Wins**: Low-effort, high-impact between sprints

---

# Known Trade-offs

<!-- Refactored from: BLUEPRINT.md "Known Trade-offs" -->

## The Good (Why we did it)

- **Deterministic Server**: No split-brain, no race conditions.
- **Clear Invariants**: Easy to verify correctness.
- **Simple Stack**: SQLite + Flask = easy to deploy and debug.

## The Bad (Current limitations)

- **No Optimistic UI**: Slower perceived performance (client waits for server).
- **No Offline Support**: Simplified sync logic requires connection.

## The "Ugly" (Intentional)

- **SQLite Concurrency**: Chosen for simplicity. Scaling is a future problem.
- **Polling/Reloads**: Used freely over complex delta updates.

---

# Open Questions / Conflicts

_No unresolved conflicts identified in source documents._

---

# Appendix: Removed Redundancies

The following passages were identified as duplicates and consolidated:

1. **"Server is the single source of truth"** — Appeared in both `BLUEPRINT.md` (line 9) and `NEOSPACE_ARCHITECTURE.md` (via directive). Consolidated into Project Overview.

2. **Technology Stack** — Overlapping tables in `PROTOCOL.md` ("The No-Build Stack") and `NEOSPACE_ARCHITECTURE.md` ("The 'Max Juice' Technology Stack"). Merged into single comprehensive table under Architecture.

3. **"No React, Vue, Webpack"** — Stated in both `PROTOCOL.md` (line 30) and `NEOSPACE_ARCHITECTURE.md` (line 20). Consolidated under "FORBIDDEN" in Technology Stack.

---

_Last refactored: 2026-01-09_
