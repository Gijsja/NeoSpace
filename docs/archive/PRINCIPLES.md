# Core Principles & Invariants

> **The server is the single source of truth. Always.**

This system deliberately trades convenience for reliability. Every design decision prioritizes correctness and determinism over feature velocity.

---

## The NeoSpace Manifesto

---

## The NeoSpace Manifesto

**"The Anti-Social Network"**

1.  **Anti-algorithm**: No recommendations, only exploration. Discovery is active, not passive.
2.  **User Ownership**: Your data is yours. Profile customization is raw (HTML/CSS), not just a form.
3.  **Chaos as Feature**: Embrace the messiness of human connection. If it breaks, it's art.
4.  **Social Without Performance**: No likes, no counts, just vibes. Connection > Validation.

---

---

## The Five Invariants (Non-Negotiable)

Violating any invariant is a critical bug.

| #   | Invariant              | Implication                                                        |
| --- | ---------------------- | ------------------------------------------------------------------ |
| 1   | **Server Authority**   | Client never derives state locally; trust only server events.      |
| 2   | **No Inference**       | All state comes purely from `message` and `backfill` events.       |
| 3   | **Canonical Backfill** | `request_backfill` must yield the exact same state as live events. |
| 4   | **Safe Deletion**      | Deleted content is scrubbed (returned as `null`), never leaked.    |
| 5   | **Idempotency**        | Multiple reconnects must produce the same result.                  |

---

---

## Agile Process (Sprints & Milestones)

We operate in iterative **Sprints**. We build on **The Bedrock** (E1) which provides a stable foundation for experimentation.

### Process

1.  **Sprints**: 1-2 week cycles with a specific theme (e.g., "Identity", "Sonic").
2.  **Milestones**: Major feature clusters (e.g., "Unified Desktop").
3.  **Quick Wins**: Low-effort, high-impact tasks prioritized between sprints.

---

### Invariant Checks

Violating an invariant is a critical bug. Always prioritize correctness over new features.
