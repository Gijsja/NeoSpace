# NeoSpace — Stack & Architecture

> Technical deep-dive into the NeoSpace platform.

---

## 📋 Project Goal

**NeoSpace** is a **server-authoritative, WebSocket-driven creative communication platform** — a modern reinterpretation of classic BBS and early social web aesthetics (think MySpace, forums, GeoCities) with a strong anti-algorithm philosophy.

### Core Philosophy

- **"The Anti-Social Network"** — No recommendations, no algorithms, only exploration
- **User Ownership** — Data sovereignty, raw profiles, no corporate forms
- **Chaos as Feature** — Imperfection and personality over polish
- **Social Without Performance** — No likes, no counts, just vibes

### The 4 Pillars

| Pillar                   | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| **Identity Canvas**      | Dynamic, customizable profile walls with stickers, scripts, and modules |
| **Radical Transparency** | System internals exposed — show the metal                               |
| **Creative Sovereignty** | Embedded code sandbox for self-expression (p5.js, Three.js)             |
| **Organic Presence**     | Real-time human connection via WebSockets                               |

---

## 🛠️ Technology Stack

### Backend

| Layer         | Technology              | Purpose                                        |
| ------------- | ----------------------- | ---------------------------------------------- |
| **Framework** | Flask 3.0.3             | Lightweight Python web framework               |
| **Real-time** | Flask-SocketIO 5.3.6    | WebSocket communication (bidirectional)        |
| **Database**  | SQLite (WAL mode)       | Single-file persistence with concurrent access |
| **Auth**      | bcrypt + Flask sessions | Password hashing & session management          |
| **Crypto**    | AES-256-GCM             | End-to-end encryption for DMs                  |
| **Testing**   | pytest + pytest-flask   | Automated test suite                           |

### Frontend

| Layer           | Technology       | Purpose                           |
| --------------- | ---------------- | --------------------------------- |
| **Templates**   | Jinja2 (HTML)    | Server-rendered views             |
| **Styling**     | Vanilla CSS      | Neubrutalist design system        |
| **JavaScript**  | Vanilla ES6+     | Client-side interactivity         |
| **Real-time**   | Socket.IO Client | WebSocket integration             |
| **Code Editor** | CodeMirror       | In-browser code editing (Sandbox) |
| **Graphics**    | p5.js, Three.js  | Creative script execution         |

### Infrastructure

| Component  | Configuration                                                 |
| ---------- | ------------------------------------------------------------- |
| **Server** | Gunicorn / Gevent                                             |
| **CORS**   | Restricted to localhost (dev)                                 |
| **Build**  | **No-Build Architecture** — Zero bundlers, zero transpilation |

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────────┐       WebSocket       ┌─────────────────────┐
│      Browser        │◄────────────────────►│       Flask         │
│  (Dumb Terminal)    │                       │  (Authoritative)    │
│                     │       HTTP REST       │                     │
│  • Templates        │◄────────────────────►│  • Routes           │
│  • Socket.IO        │                       │  • Mutations        │
│  • Vanilla JS       │                       │  • Queries          │
└─────────────────────┘                       └──────────┬──────────┘
                                                         │
                                              ┌──────────▼──────────┐
                                              │       SQLite        │
                                              │      (WAL Mode)     │
                                              │                     │
                                              │  • Connection Pool  │
                                              │  • Retry Logic      │
                                              │  • PRAGMA Tuned     │
                                              └─────────────────────┘
```

### Server Authority Model

> **The server is the single source of truth. Always.**

- Frontend is a **"dumb terminal"** — receives HTML fragments via WebSockets
- All state mutations go through the server
- Client never constructs messages; server broadcasts authoritative data
- Session-based auth: WebSocket connections validated against Flask sessions

### Evolution Layers

| Layer  | Name        | Status    | Scope                                          |
| ------ | ----------- | --------- | ---------------------------------------------- |
| **E1** | The Bedrock | 🛡️ Frozen | Backend semantics, DB schema, socket protocols |
| **E2** | UX          | 🔄 Active | Layout, interactions, styling, frontend polish |

---

## 📁 Directory Structure

```
NeoSpace/
├── app.py                 # Flask application factory
├── db.py                  # Database schema, connection pool, retry logic
├── auth.py                # Authentication blueprint (login/register/logout)
├── sockets.py             # WebSocket event handlers
├── core.crypto.py        # AES-256-GCM encryption utilities
│
├── routes/                # HTTP route blueprints
│   ├── chat.py            # Chat room endpoints
│   ├── directory.py       # User directory
│   ├── messages.py        # Message REST API
│   ├── profiles.py        # Profile management
│   ├── rooms.py           # Room management
│   ├── scripts.py         # Sandbox scripts API
│   ├── views.py           # Server-rendered page views
│   └── wall.py            # Profile wall endpoints
│
├── mutations/             # Database write operations
│   ├── dm.py              # Direct message mutations
│   ├── file_mutations.py  # File upload handling
│   ├── message_mutations.py # Message CRUD
│   ├── profile.py         # Profile updates
│   ├── profile_scripts.py # Pinned scripts
│   ├── scripts.py         # Sandbox script CRUD
│   └── wall.py            # Wall sticker/module mutations
│
├── queries/               # Database read operations
│   ├── backfill.py        # Message history queries
│   ├── directory.py       # User search/listing
│   ├── rooms.py           # Room queries
│   └── unread.py          # Unread message counts
│
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Layout with sidebar navigation
│   ├── app.html           # Main chat interface
│   ├── dashboard.html     # Desktop 3-pane view
│   ├── directory.html     # User directory page
│   └── wall.html          # Profile wall canvas
│
├── ui/                    # Static frontend assets
│   ├── css/               # Neubrutalist CSS
│   ├── js/                # Client-side JavaScript
│   └── views/             # Additional view components
│
├── static/                # Uploaded files & assets
├── tests/                 # pytest test suite
├── scripts/               # Migration utilities
└── docs/                  # Documentation
```

---

## 💾 Database Schema

### Core Tables

| Table             | Purpose                                                |
| ----------------- | ------------------------------------------------------ |
| `users`           | User accounts (username, bcrypt hash, avatar color)    |
| `messages`        | Chat messages (scoped by room_id)                      |
| `profiles`        | User profile data (bio, status, avatar, anthem, theme) |
| `direct_messages` | E2E encrypted DMs with per-user soft delete            |
| `scripts`         | User-created sandbox scripts (p5.js, Three.js)         |

### Feature Tables

| Table              | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `profile_stickers` | Draggable wall stickers (emoji, images)          |
| `profile_scripts`  | Pinned scripts on profile walls (max 3)          |
| `profile_posts`    | Modular canvas posts (text, image, link, script) |

### SQLite Optimizations

```sql
PRAGMA journal_mode = WAL;      -- Concurrent reads during writes
PRAGMA synchronous = NORMAL;    -- Balanced durability
PRAGMA mmap_size = 268435456;   -- 256MB memory-mapped I/O
PRAGMA cache_size = -64000;     -- 64MB page cache
PRAGMA busy_timeout = 30000;    -- 30s lock retry
```

---

## 🔌 Real-Time Protocol (Socket.IO)

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

---

## 🧩 Key Features by Sprint

| Sprint  | Theme                   | Features                                              |
| ------- | ----------------------- | ----------------------------------------------------- |
| **#6**  | User Profiles           | Profile wall, DMs, User directory                     |
| **#7**  | Identity & Transparency | Wall stickers, System internals                       |
| **#8**  | Creative Sandbox        | Scripts API, CodeMirror editor, p5.js/Three.js runner |
| **#9**  | Sonic Identity          | Voice intros, Waveform player                         |
| **#10** | Unified Desktop         | 3-pane layout, Tool integration                       |
| **#11** | NeoSpace Foundations    | Audio anthem (MySpace-style), Identity first          |
| **#12** | Modular Canvas          | Profile posts (text/image/link/script blocks)         |

---

## 🚀 Running the Application

```bash
# Setup virtual environment (first time)
./scripts/setup_venv.sh

# Start the server
./startlocal.sh

# Run tests
source .venv/bin/activate
pytest
```

**Access**: [http://localhost:5000](http://localhost:5000)

---

## 🎨 Design Philosophy

- **Neubrutalist Aesthetic** — Bold borders, raw geometry, intentional roughness
- **No-Build** — Pure HTML/CSS/JS, zero bundlers
- **Server Rendered** — Jinja2 templates, HTML-over-WebSocket
- **Performance** — SQLite WAL with connection pooling & retry logic

---

_Last Updated: 2026-01-08_
