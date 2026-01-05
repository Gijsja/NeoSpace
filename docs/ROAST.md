# Roast

A critical self-review of project risks.

---

## Primary Risk

> **UX pressure eroding core guarantees.**

As the project evolves, there will be pressure to:

- Add "just one more" socket event
- Tweak backend logic for frontend convenience
- Bypass ownership checks for admin features
- Add client-side state that diverges from server

**Each exception weakens the architecture.**

---

## Mitigation Strategy

| Defense                | Implementation                                            |
| ---------------------- | --------------------------------------------------------- |
| **Version discipline** | Epoch boundaries (E1/E2/E3) are hard gates                |
| **Frozen docs**        | [CORE_FROZEN](CORE_FROZEN.md) is the contract             |
| **Test coverage**      | Core invariants have tests that must pass                 |
| **Code review**        | Any `mutations/` or `sockets.py` change requires scrutiny |

---

## Warning Signs

Watch for these anti-patterns:

- [ ] "Let's just add this field to the payload"
- [ ] "The client can handle this edge case"
- [ ] "We'll fix the tests later"
- [ ] "It works, ship it"

---

## The Rule

> _If in doubt, don't change the core. Wait for E3._
