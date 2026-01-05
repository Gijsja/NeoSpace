# Evolution & Scope (E1 → E3)

Defines the architectural boundaries and "Epochs" of the project.

---

## The Epoch Model

We manage complexity by defining clear eras of development.

| Epoch  | Name                  | Status        | Scope                                                                |
| ------ | --------------------- | ------------- | -------------------------------------------------------------------- |
| **E1** | **Core Foundation**   | 🧊 Frozen     | Basic database schema, WebSocket Protocol, Flask setup.              |
| **E2** | **UX Polish**         | ✅ Complete   | Visual design, themes, client-side interactions (design/wireframes). |
| **E3** | **Identity & Social** | 🚧 **ACTIVE** | User accounts, Auth (Google/Apple), Profiles, DMs.                   |

---

## 🚧 E3: The Active Era

We are currently in **Epoch 3**. This means "breaking changes" to the Core are permitted **only** to support:

1.  **Authentication**: `users` table, sessions.
2.  **Profiles**: `profiles` table, schema expansion.
3.  **Privacy**: Direct Message schema vs Public Room schema.

### Allowed Changes in E3

- ✅ modifying `db.py` schema
- ✅ adding new routes (`/auth/*`)
- ✅ adding new socket events (`private_message`)

### Forbidden in E3

- ❌ Breaking existing E1 chat invariants (e.g., removing `backfill`)
- ❌ Changing the core philosophy (Server Authority)

---

_Formerly `V2_SCOPE.md`_
