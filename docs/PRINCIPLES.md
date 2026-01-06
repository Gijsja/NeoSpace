# Core Principles & Invariants

> **The server is the single source of truth. Always.**

This system deliberately trades convenience for reliability. Every design decision prioritizes correctness and determinism over feature velocity.

---

## The NeoSpace Manifesto

We are building an **Anti-Social Network**.

1.  **Anti-algorithm**: No recommendations, only exploration. Discovery is active, not passive.
2.  **User Ownership**: Your data is yours. Profile customization is raw (HTML/CSS), not just a form.
3.  **Chaos as Feature**: Embrace the messiness of human connection. If it breaks, it's art.
4.  **Social Without Performance**: No likes, no counts, just vibes. Connection > Validation.

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

## Frozen Core (Stability Guarantee)

The backend core semantics are "frozen" to ensure stability.

### What is Frozen?

- **Database Schema**: The fundamental shape of `messages`.
- **Socket Payloads**: The structure of `message` and `backfill` events.
- **Business Logic**: Ownership checks, soft-delete behavior.

### Making Changes

Changes to the frozen core require a new **Epoch** (e.g., E2 -> E3). This requires:

1. A clear migration plan.
2. Backward compatibility strategy.
3. Full test suite update.

_Formerly `CORE_INVARIANTS.md` and `CORE_FROZEN.md`_
