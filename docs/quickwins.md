# Quick Wins & CatNetwork Backlog

## 🚨 CatNetwork Support & Security (High Priority)

- [ ] **Audit Logs**: Track admin actions in `admin_ops` table.
- [ ] **Role-Based Access**: Formalize `is_staff` vs `is_superuser`.

## 🧠 Cat Knowledge & State (Feature)

- [ ] **Long-term Memory**: Implement vector embeddings for chat history analysis.
- [ ] **Gossip Protocol**: Allow cats to share `cat_memories` when they are in the same room.

## 🧩 UI/UX "Left on the Table"

- [ ] **Keyboard Shortcuts**: Global `?` modal to show hotkeys.
- [ ] **Sound Effects**: Add subtle UI sfx (click, hover, success) using `Howler.js` (optional).

## ⚡️ Performance & Clean Code

- [ ] **Database Archival**: Move old messages to `messages_archive` table to keep queries fast.

## ❤️ Emotional Intelligence Upgrade (Completed)

> **Status**: Successfully implemented PAD Model, Relationship Graph, and Dynamic Avatars in Sprint 26.

## 🔮 Future: The "Rimworld" Relationship Layer

> **Status**: Core logic (Affinity -100 to +100) implemented. Next step: Complex behavioral trees based on affinity.

---

## Archive (Completed Wins)

- [x] **Secure Admin Endpoints**: Added `@login_required` to seeding.
- [x] **Secure Speech Endpoint**: Protected `/cats/speak`.
- [x] **CSRF Validation**: Standardized in `ui/js/friends.js`.
- [x] **Persistence Layer**: Moved `_cat_state` to DB.
- [x] **Bot User Sync**: Implemented `seed_cat_bot_users` update logic.
- [x] **Wall Stickers**: Integrated drag-and-drop palette.
- [x] **Visual Polish**: Implemented dynamic avatar switching.
