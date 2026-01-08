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

### Evolution Layers

| Layer  | Name        | Status    | Scope                                 |
| ------ | ----------- | --------- | ------------------------------------- |
| **E1** | The Bedrock | 🛡️ Frozen | Backend semantics, DB schema, sockets |
| **E2** | UX          | 🔄 Active | Layout, interactions, styling         |

---

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

### Current: Sprint #18 🚧

**Theme**: TBD

### Recently Shipped

| Sprint | Theme                   | Features                              |
| ------ | ----------------------- | ------------------------------------- |
| #17    | Search API              | User and Post search endpoints        |
| #16    | Feed API                | `/feed` endpoint, Pagination          |
| #15    | Live Wire               | Notifications API, Follow triggers    |
| #14    | Social Graph            | Friends, Top 8, Follow/Unfollow       |
| #13    | Speed Demon             | msgspec structs for hot paths         |
| #12    | Modular Canvas          | Profile posts (text/image/link/audio) |
| #11    | NeoSpace Foundations    | Audio Anthem, Identity First          |
| #10    | Unified Desktop         | 3-pane layout, Tool Integration       |
| #9     | Sonic Identity          | Voice Intros, Waveform Player         |
| #8     | Creative Sandbox        | Scripts API, Code Editor              |
| #7     | Identity & Transparency | Wall Stickers, System Internals       |
| #6     | User Profiles           | Profile Wall, DMs, Directory          |

---

## User Flow: The Creator Journey

1. **Spark** — Open NeoSpace, enter Code Mode
2. **Studio** — Write code, hot-reload canvas, fix errors
3. **Release** — Publish to room with caption
4. **Resonance** — Receive sticker feedback, get forked

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
