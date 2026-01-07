# NeoSpace Agent Memory

> State tracking for ongoing development.

## Sources of Truth

| Question              | Document            |
| --------------------- | ------------------- |
| What are we building? | `docs/BLUEPRINT.md` |
| How do we code it?    | `docs/PROTOCOL.md`  |

## Current State

- **Date:** 2026-01-07
- **Phase:** No-Build Architecture (HTMX + Alpine.js)
- **Status:** Active development

## Migration Queue

1. [x] **Directory** - HTMX for server-rendered user cards ✅
2. [x] **Login Form** - Alpine.js for tab toggle + form ✅
3. [ ] **Message Composer** - `/app.html`
4. [ ] **Wall Grid** - `/wall.html`

## Decisions Log

| Date       | Decision          | Rationale                          |
| ---------- | ----------------- | ---------------------------------- |
| 2026-01-07 | No-Build stack    | No Node.js, CDN-only               |
| 2026-01-07 | HTMX + Alpine.js  | Server-rendered + local reactivity |
| 2026-01-07 | Consolidated docs | BLUEPRINT + PROTOCOL only          |
