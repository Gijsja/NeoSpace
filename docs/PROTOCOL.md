# NeoSpace Protocol

> Rules, invariants, and development standards.

---

## The Five Invariants

Violating any invariant is a **critical bug**.

| #   | Invariant              | Implication                                           |
| --- | ---------------------- | ----------------------------------------------------- |
| 1   | **Server Authority**   | Client never derives state locally                    |
| 2   | **No Inference**       | State comes only from `message` and `backfill` events |
| 3   | **Canonical Backfill** | `request_backfill` yields exact same state as live    |
| 4   | **Safe Deletion**      | Deleted content returned as `null`, never leaked      |
| 5   | **Idempotency**        | Multiple reconnects produce same result               |

---

## The No-Build Stack

| Layer       | Technology     | Source                            |
| ----------- | -------------- | --------------------------------- |
| Core        | Python (Flask) | Server-side templates             |
| Styling     | Tailwind CSS   | `static/vendor/tailwindcss.js`    |
| Reactivity  | Alpine.js      | `static/vendor/alpine.min.js`     |
| Server Sync | HTMX           | `static/vendor/htmx.min.js`       |
| Icons       | Phosphor       | `static/vendor/phosphor/*.css`    |
| Charts      | ApexCharts     | `static/vendor/apexcharts.min.js` |

> **Assets are vendored locally** — no CDN dependency at runtime (except Google Fonts and emoji-picker).

**FORBIDDEN:** React, Vue, Webpack, Vite, `npm`, `package.json`

---

## The Chesterton's Fence Rule

> Do not delete code unless you understand why it exists.

- `routes/` — Core business logic, preserve
- `mutations/` — All state changes, preserve
- `queries/` — Read operations, preserve
- When uncertain, keep legacy running in parallel

---

## Debugging Runbook

> **Golden Rule:** Assume the client is wrong.

### Diagnostic Steps

1. **Check Socket Traffic** — DevTools → Network → WS tab
2. **Trigger Backfill** — `socket.emit("request_backfill", { after_id: 0 })`
3. **Check Server Logs** — `python startlocal.py`
4. **Restart Server** — Nuclear option

### Quick Reference

| Symptom          | Likely Cause     | Fix              |
| ---------------- | ---------------- | ---------------- |
| Messages missing | Missed broadcast | Trigger backfill |
| Wrong user       | Header missing   | Check `g.user`   |
| 500 errors       | Database locked  | Restart server   |

## <!-- Source: docs/archive/STACK_AND_ARCHITECTURE.md -->

## Real-Time Protocol (Socket.IO)

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

## Versioning

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

### Tagging Rules

- ✅ Tag when all tests pass
- ❌ Never tag broken builds

---

## Agile Process

1. **Sprints**: 1-2 week cycles with themes
2. **Milestones**: Major feature clusters
3. **Quick Wins**: Low-effort, high-impact between sprints

website login with username Kees and password Hond
