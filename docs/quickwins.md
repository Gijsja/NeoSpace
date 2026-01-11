# Quick Wins & CatNetwork Backlog

## 🛠️ Code Quality & Tech Debt (New via Review)

- [x] **Config Centralization**: Moved env var reads to `config.py`.
- [x] **Type Hinting**: Partially implemented in core utilities and services.
- [x] **Mutation Decorators**: Create `@mutation_handler` to reduce boilerplate (try/catch/retry) in mutation functions.
- [ ] **API Documentation**: generating OpenAPI spec using `Flask-RESTX` or similar.
- [x] **Frontend Reconnect**: Add exponential backoff to `ChatSocket.js`.
- [ ] **Test Coverage**: Add non-IO domain logic tests.
- [x] **Prometheus**: Add basic `/metrics` endpoint.

## 🚨 CatNetwork Support & Security (High Priority)

- [x] **Audit Logs**: Track admin actions in `admin_ops` table.
- [ ] **Role-Based Access**: Formalize `is_staff` vs `is_superuser`.

## 🧠 Cat Knowledge & State (Feature)

- [ ] **Long-term Memory**: Implement vector embeddings for chat history analysis.
- [ ] **Gossip Protocol**: Allow cats to share `cat_memories` when they are in the same room.

## 🧩 UI/UX "Left on the Table"

- [x] **Keyboard Shortcuts**: Global `?` modal to show hotkeys.
- [ ] **Sound Effects**: Add subtle UI sfx (click, hover, success) using `Howler.js` (optional).

## ⚡️ Performance & Clean Code

- [x] **Database Archival**: Move old messages to `messages_archive` table to keep queries fast.
- [ ] **Bun Integration**: Evaluate replacing `npm` with `bun` for 25x faster installs and zero-config testing.

---

## Archive (Completed Wins)

- [x] **Secure Admin Endpoints**: Added `@login_required` to seeding.
- [x] **Secure Speech Endpoint**: Protected `/cats/speak`.
- [x] **CSRF Validation**: Standardized in `ui/js/friends.js`.
- [x] **Persistence Layer**: Moved `_cat_state` to DB.
- [x] **Bot User Sync**: Implemented `seed_cat_bot_users` update logic.
- [x] **Wall Stickers**: Integrated drag-and-drop palette.
- [x] **Visual Polish**: Implemented dynamic avatar switching.
