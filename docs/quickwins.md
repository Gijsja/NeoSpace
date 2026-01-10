# Quick Wins & CatNetwork Backlog

## 🚨 CatNetwork Support & Security (High Priority)

- [x] **Secure Admin Endpoints**: The `/cats/seed` endpoint in `routes/cats.py` is currently public.
  - *Action*: Add `@login_required` and check for admin status (or at least `is_staff`/`is_superuser` if available) before allowing seeding.
- [x] **Secure Speech Endpoint**: `POST /cats/speak` takes a raw body to determine responses.
  - *Action*: Ensure only trusted internal services or authorized clients can trigger arbitrary cat speech, or validate that the event actually occurred.
- [x] **Validation**: `ui/js/friends.js` has a "relaxed" CSRF check.
  - *Action*: Standardize CSRF token retrieval using the `getCsrfToken` helper and ensure the backend strictly enforces it.

## 🧠 Cat Knowledge & State (Feature)

- [x] **Persistence Layer**: Currently, `_cat_state` in `services/cat_service.py` is stored in global memory.
  - *Consequence*: "Familiarity", "Mood", and "Energy" reset on every server restart.
  - *Fix*: Create a `cat_state` table or use a Redis/Cache store to persist relationships with users (`user_id`, `cat_name`, `familiarity`, `last_interaction`).
- [ ] **Bot User Sync**: `seed_cat_bot_users` creates users but doesn't auto-update their avatars if the personality definition changes.
  - *Fix*: Update the seeder to refresh metadata for existing bot users.

## 🧩 UI/UX "Left on the Table"

- [x] **Cat Reactions in Frontend**: `trigger_cat_response` returns data (`cat`, `line`, `avatar`), but `ui/js/friends.js` only dispatches a `friend-added` event.
  - *Todo*: Ensure there is a listener (likely in `layout.html` or a global `CatCompanion.js`) that actually *shows* the cat notification (toast/bubble) when this event fires.
- [ ] **Wall Stickers Integration**: `WallStickers.js` handles generic images.
  - *Idea*: Add a "Cat Sticker Pack" tab that pulls from `get_cat_personalities` to allow users to stick their favorite cats on walls.

## ⚡️ Performance & Clean Code

- [x] **Service Refactor**: `cat_service.py` mixes data (templates) and logic.
  - *Refactor*: Move `BASE_CATS` and `DIALOGUE_TEMPLATES` to a JSON/YAML config or database table to allow dynamic updates without code redeploys.

## ❤️ Emotional Intelligence Upgrade (Love/Hate Inspired)

To make the CatSystem feel "alive" rather than just random, we can adopt a simplified version of the **PAD (Pleasure, Arousal, Dominance)** emotional model found in systems like *Pixel Crushers' Love/Hate*.

### 1. The PAD Model
Instead of a single `mood` scalar, track a 3D emotional state for each cat:
- **Pleasure**: Happiness vs. Unhappiness (e.g., purring vs. hissing).
- **Arousal**: Excitement vs. Boredom (e.g., zoomies vs. sleeping).
- **Dominance**: Confidence vs. Fear (e.g., demanding food vs. hiding).

**Implementation**:
- Update `_cat_state` (or the new DB table) to store `pad: [float, float, float]`.
- Map current `energy` to `arousal`.

### 2. Deed-Based Evaluation
Events aren't just triggers; they are **Deeds** that having meaning.
- **Define Deeds**:
  - `login_success`: Pleasure +10, Arousal +5 (User is present!)
  - `timeout`: Pleasure -5, Arousal -20 (Boring...)
  - `system_error`: Pleasure -20, Dominance -10 (Confusing/Scary) OR Dominance +20 (Mocking/Superior, depending on personality).

### 3. Relationships & Factions
Cats shouldn't just react to "the system"; they should react to **YOU**.
- **Relationship Table**: `(cat_id, target_id, affinity, pad_perception)`
- **Factions**: 
  - `UserFaction`: The player.
  - `SystemFaction`: The server/backend.
- **Dynamics**:
  - If `SystemFaction` fails (error 500), a "Chaotic" cat (Anti-System) might gain Pleasure (Mockery).
  - A "Friendly" cat might lose Pleasure (Sympathy).

### 4. Memory & Gossip (Future)
- **Short-term Memory**: "You logged in 5 times today" -> High Arousal (Annoyance).
- **Gossip**: One cat witnessing a deed could "tell" others, spreading the emotional impact.

### Action Plan
- [x] **Phase 1**: Refactor `cat_service.py` to use `PAD` instead of `mood`.
- [x] **Phase 2**: Define a `Deed` configuration (event -> PAD impact).
- [x] **Phase 3**: Implement `evaluate_deed(cat, deed)` logic to update state.
- [x] **Phase 4**: Frontend Integration (Penguin UI Toaster + `CatCompanion.js`).

## 🔮 Future: The "Rimworld" Relationship Layer

- [ ] **Unified Social Graph**: Implement `cat_relationships` table to track affinity (`-100` to `+100`) between:
  - Cat -> Human
  - Cat -> Cat (via Bot Users)
- [ ] **Memory System**: `cat_memories` table to store temporary interaction history (e.g., "Witnessed embarrassing post").
- [ ] **Visual Updates**: Replace placeholder cat images with pixel art variations for each emotional state (50 states).
