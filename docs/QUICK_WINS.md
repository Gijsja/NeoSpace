# Quick Wins & Optimizations

## ⚡️ msgspec Consistency ✅ COMPLETE

Status: 100% of JSON endpoints optimized.

### Notifications (`routes/notifications.py`)

- [x] `mark_read` endpoint
- [x] `delete_notification` endpoint

### Rooms (`queries/rooms.py`)

- [x] `create_room` endpoint

### Profile Scripts (`mutations/profile_scripts.py`)

- [x] `pin_script` endpoint
- [x] `unpin_script` endpoint
- [x] `reorder_scripts` endpoint

### Stickers (`mutations/profile.py`)

- [x] `add_sticker`

## 🧹 Codebase Hygiene

- [ ] **Dependency Audit**: Verify `msgspec` is the sole JSON parser for API requests.
- [ ] **Test Coverage**: Ensure new optimizations are covered by existing or new tests.
