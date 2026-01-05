# V2 Scope

Defines the boundary between frozen core (E1) and active UX layer (E2).

---

## ✅ Allowed in E2

| Category               | Examples                                                        |
| ---------------------- | --------------------------------------------------------------- |
| **Layout**             | Flexbox, grid, spacing, responsive breakpoints                  |
| **Styling**            | Colors, fonts, transitions, themes                              |
| **Accessibility**      | ARIA labels, keyboard nav, focus management                     |
| **Interaction Polish** | Animations, hover states, loading indicators                    |
| **Client-Side UX**     | Local notifications, scroll behavior, input validation feedback |

---

## ❌ Forbidden in E2

| Category              | Examples                                             |
| --------------------- | ---------------------------------------------------- |
| **Backend Semantics** | Database schema, business logic, ownership rules     |
| **Socket Changes**    | Event names, payload structure, new fields           |
| **API Changes**       | Endpoint behavior, response format, status codes     |
| **Server State**      | Any modification to `mutations/` or `queries/` logic |

---

## Decision Tree

```
Is it visible only to the browser?
├─ Yes → Probably E2-safe ✅
└─ No → Requires E3 epoch ❌
```

See also: [CORE_FROZEN](CORE_FROZEN.md) | [CORE_INVARIANTS](CORE_INVARIANTS.md)
