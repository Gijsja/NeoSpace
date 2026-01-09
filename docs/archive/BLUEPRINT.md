# NeoSpace Blueprint

> The single source of truth for architecture, vision, and roadmap.

---

## Philosophy

> **The server is the single source of truth. Always.**

This system trades convenience for reliability. Every decision prioritizes correctness over velocity.

---

## Architecture

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



## The NeoSpace Manifesto

**"The Anti-Social Network"**

1. **Anti-algorithm**: No recommendations, only exploration
2. **User Ownership**: Your data is yours. Profiles are raw, not forms
3. **Chaos as Feature**: If it breaks, it's art
4. **Social Without Performance**: No likes, no counts, just vibes

---

## The 4 Pillars

1. **Identity Canvas** — Dynamic, customizable profile walls
2. **Radical Transparency** — System Internals expose the metal
3. **Creative Sovereignty** — Embedded code sandbox for expression
4. **Organic Presence** — Visualize human connection

---

## Roadmap

### Current: Sprint 23 (Active)

**Theme**: Feature Expansion & Hardening

**Goals**:
- **Testing**: Service Layer Tests & Database Migrations (Alembic)
- **UI**: Neopunk Ghettoblaster, Cat Error Pages, Guestbook Collage
- **Features**: Script Publishing, Video/Omegle Research

### Recently Shipped

| Sprint      | Theme                   | Features                                                   |
| ----------- | ----------------------- | ---------------------------------------------------------- |
| **Stage 2** | **Maturation**          | Service layer, ES6 modules, vendored assets, CSP hardening |
| #22         | Live Wire UI            | Notification Center, Badges, Toasts                        |
| #21         | The Feed UI             | Home Stream, Infinite Scroll                               |
| #20         | Social Actions UI       | Follow/Unfollow, Top 8 Grid                                |
| #19         | Search UI               | Js-based Search, User/Post tabs                            |
| #18         | Security Hardening      | CSRF, CSP, Rate Limiting (Ironclad)                        |
| #17         | Search API              | User and Post search endpoints                             |
| #16         | Feed API                | `/feed` endpoint, Pagination                               |
| #15         | Live Wire               | Notifications API, Follow triggers                         |
| #14         | Social Graph            | Friends, Top 8, Follow/Unfollow                            |
| #13         | Speed Demon             | msgspec structs for hot paths                              |
| #12         | Modular Canvas          | Profile posts (text/image/link/audio)                      |
| #11         | NeoSpace Foundations    | Audio Anthem, Identity First                               |
| #10         | Unified Desktop         | 3-pane layout, Tool Integration                            |
| #9          | Sonic Identity          | Voice Intros, Waveform Player                              |
| #8          | Creative Sandbox        | Scripts API, Code Editor                                   |
| #7          | Identity & Transparency | Wall Stickers, System Internals                            |
| #6          | User Profiles           | Profile Wall, DMs, Directory                               |

<!-- Source: docs/archive/ROADMAP.md -->

### Legacy Sprints (Historical)

| Sprint | Theme               | Features                                 |
| ------ | ------------------- | ---------------------------------------- |
| #5     | Authentication      | Standard User/Pass Auth, Sessions        |
| #4     | Data Persistence    | Message Timestamps, File Uploads         |
| #3     | Backend Integration | Live WebSocket, Persistent Room State    |
| #2     | Chat Functionality  | Message Hover Actions, Typing Indicators |
| #1     | Foundation          | Git init, Tailwind CSS, 3-pane scaffold  |

---

<!-- Source: docs/archive/KNOWN_ISSUES.md -->

## Known Trade-offs

### The Good (Why we did it)

- **Deterministic Server**: No split-brain, no race conditions.
- **Clear Invariants**: Easy to verify correctness.
- **Simple Stack**: SQLite + Flask = easy to deploy and debug.

### The Bad (Current limitations)

- **No Optimistic UI**: Slower perceived performance (client waits for server).
- **No Offline Support**: Simplified sync logic requires connection.

### The "Ugly" (Intentional)

- **SQLite Concurrency**: Chosen for simplicity. Scaling is a future problem.
- **Polling/Reloads**: Used freely over complex delta updates.

---


## Key Views

| View        | Purpose                        |
| ----------- | ------------------------------ |
| Login       | Authentication with tab toggle |
| Chat        | Main messaging interface       |
| Wall        | Personal Identity Canvas       |
| Code Editor | Creative Sandbox               |
| Directory   | User discovery                 |
| Desktop     | Unified 3-pane power view      |
