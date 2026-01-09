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

## 🧹 Codebase Hygiene ✅ COMPLETE

- [x] **Dependency Audit**: `msgspec` is the sole JSON parser for all API requests. Converted remaining `request.get_json()` calls in `mutations/sticker.py`.
- [x] **Test Coverage**: All 166 tests pass. Service layer tests cover `dm_service`, `wall_service`, and `profile_service`.
