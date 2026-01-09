# Sprint 23: Feature Expansion & Hardening

**Date Range**: 2026-01-09 to 2026-01-11

## Goals

1. **Testing & Stability**: Complete service layer unit tests and establish database migrations.
2. **Audio & Visuals**: Implement Neopunk Ghettoblaster UI and Cat Error pages.
3. **Feature Completion**: Finalize script publishing flow and evaluate/expand component library.
4. **Research**: Plan Video/Omegle feature.

## Backlog

### 🧪 Quality Assurance
- [x] **Service Layer Tests**
  - [x] Fix `db_session` fixture in `tests/services/conftest.py`.
  - [x] Complete unit tests for `dm_service.py`, `wall_service.py`, `profile_service.py`.
- [x] **Database Migrations**
  - [x] Finalize Alembic configuration.
  - [x] Create and apply baseline migration (`alembic revision --autogenerate`).
- [x] **Codebase Hygiene**
  - [x] Verify `msgspec` usage across all endpoints.
  - [x] Audit dependencies.

### 🎨 UI/UX
- [x] **Neopunk Ghettoblaster**
  - [x] Implement retro-futurist audio player UI (server-rendered HTML + Alpine.js).
  - [x] Integrate with Voice Note module.
- [x] **Cat Error Pages**
  - [x] Implement custom 404/500 pages with cat illustrations.
- [x] **Component Library**
  - [x] Evaluate UI libraries (Penguin, Pinemix, Oxbow).
  - [x] Implement missing components: Avatar, Badge, Skeleton, Switch, Tabs.
  - [x] Create `playground.html` for component showcase.
- [x] **Guestbook Collage Mode**
  - [x] Implement drag-and-drop image stickers on profile walls.
  - [x] Backend support for sticker coordinates/rotation.
  - [x] Frontend stickers logic (`WallStickers.js`).

### 🚀 Features
- [x] **Script Publishing**
  - [x] Add "Publish" button to Codeground.
  - [x] Backend support for script posts.
  - [x] Inline script player in Feed.
- [x] **Video/Omegle**
  - [x] Assess architecture for real-time video.
  - [x] Propose integration plan (See `docs/video_architecture.md`).

## Acceptance Criteria
- All service layer tests pass (`pytest tests/services`).
- Migrations system is operational (`alembic upgrade head`).
- Audio player functions correctly in the UI.
- Error pages displayed correctly.
- Scripts can be published and run in the feed.
