# Known Issues & Trade-offs

An honest assessment of the system's limitations and risks.

---

## 🏗 Architectural Trade-offs

### The Good (Why we did it)

- **Deterministic Server**: No split-brain, no race conditions.
- **Clear Invariants**: Easy to verify correctness.
- **Simple Stack**: SQLite + Flask = easy to deploy and debug.

### The Bad (Current limitations)

- **No Optimistic UI**: Slower perceived performance (client waits for server).
- **No Offline Support**: Simplified sync logic requires connection.
- **Single Room**: Currently limited to one global context (changing in E3).

### The "Ugly" (Intentional)

- **SQLite Concurrency**: Chosen for simplicity. Scaling is a future problem.
- **Polling/Reloads**: Used freely over complex delta updates.

---

## 🔥 Risk Assessment ("The Roast")

### Primary Risk: UX Feature Creep

**"UX pressure eroding core guarantees."**

As the project evolves (e.g., adding "MySpace" profiles), there is temptation to:

- Bypass server authority for "snappier" UI.
- Add client-side state that diverges from server.
- Tweak backend logic for frontend convenience.

### Mitigation Strategy

1.  **Epoch Boundaries**: respecting E1/E2/E3 gates.
2.  **Frozen Contracts**: Adhering to `docs/api/SOCKET_CONTRACT.md`.
3.  **Code Review**: Strict scrutiny on `mutations/` and `sockets.py`.

_Formerly `GOOD_BAD_UGLY.md` and `ROAST.md`_
