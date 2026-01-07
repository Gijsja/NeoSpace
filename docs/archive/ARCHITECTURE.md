# Project Overview

**NeoSpace** is a server-authoritative creative communication platform designed for correctness, determinism, and debuggability.

## Philosophy

> The server is the single source of truth. Always.

This system deliberately trades convenience for reliability. Every design decision prioritizes predictable behavior over feature velocity.

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

## Evolution Model

The system is split into two distinct layers:

| Layer  | Name        | Status    | Scope                                               |
| ------ | ----------- | --------- | --------------------------------------------------- |
| **E1** | The Bedrock | 🛡️ Stable | Backend semantics, database schema, socket payloads |
| **E2** | UX          | 🔄 Active | Layout, accessibility, interaction polish           |

**This separation ensures reliability.** See `CORE_INVARIANTS.md`.

## Key Documents

- **[CORE_INVARIANTS](CORE_INVARIANTS.md)** — Rules that must never be violated
- **[SOCKET_CONTRACT](SOCKET_CONTRACT.md)** — WebSocket event specifications
- **[API_REFERENCE](API_REFERENCE.md)** — HTTP endpoint documentation

## Current Version

See [VERSION](../VERSION) file or run the server for current build tag.

## Design Layer (Creative OS)

The user experience layer ("Creative OS") is documented in `docs/design/`:

- **[WIREFRAMES](design/WIREFRAMES.md)**: Full visual specification (Login, Chat, Wall, Code Mode).
- **[Project Brief](design/project_brief.md)**: Executive summary and vision.
- **[User Journey](design/user_journey.md)**: Functional maps for key flows (Creator Mode).
