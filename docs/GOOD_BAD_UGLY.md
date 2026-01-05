# Good / Bad / Ugly

An honest assessment of LocalBBS trade-offs.

---

## ✅ The Good

| Aspect                   | Why It Matters                                              |
| ------------------------ | ----------------------------------------------------------- |
| **Deterministic server** | Same input always produces same output. No race conditions. |
| **Clear invariants**     | Five rules that never break. Easy to verify correctness.    |
| **Server-authoritative** | No split-brain. Client trusts server completely.            |
| **Soft-delete**          | Messages can be "deleted" without data loss for auditing.   |
| **HTML escaping**        | XSS protection built into message creation.                 |

---

## ⚠️ The Bad

| Limitation            | Impact                                | Future Path            |
| --------------------- | ------------------------------------- | ---------------------- |
| **No authentication** | Users are trusted via `X-User` header | E3: Session/token auth |
| **Single room**       | All users share one global room       | E3: Multi-room support |
| **No rate limiting**  | Vulnerable to spam                    | E3: Request throttling |

---

## 🎭 The Ugly (Intentional)

These are _deliberate_ trade-offs, not bugs:

| Decision               | Rationale                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| **SQLite**             | Single-file DB simplifies deployment. WAL mode handles concurrency. Scaling is a future problem. |
| **No optimistic UI**   | Client waits for server confirmation. Slower UX, but zero state drift. Correctness > speed.      |
| **No offline support** | Requires connection. Simplifies sync logic. Local-first means server-local.                      |

---

> _"We chose boring technology on purpose."_
