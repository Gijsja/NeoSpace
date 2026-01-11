# Sprint Status

## Current Sprint: #27 (Active)

**Theme**: The Hardening (Security & Reliability)
**Focus**: Security Consolidation, Observability, Technical Debt Paydown

> **Objective**: Before expanding features, we must solidify the foundation. This sprint addresses critical findings from the Jan 2026 Code Review, ensuring NeoSpace is secure, stable, and ready for scale.

### Phases

#### Phase 1: Security Consolidation (Critical)
- [ ] **WebSocket Session Longevity**: Implement `validate_auth` with periodic re-checks to prevent stale/banned sessions from persisting.
- [ ] **Global Rate Limiting**: Expand `Flask-Limiter` coverage to all mutations and critical WebSocket events.
- [ ] **Access Control Hardening**: Centralize ownership checks (`check_ownership` helper) to prevent IDOR in Profile/Wall mutations.

#### Phase 2: Reliability & Observability (High)
- [ ] **DB Connection Safety**: Add logging/monitoring to `ConnectionPool` to track exhaustion.
- [ ] **Standardized Errors**: Implement `core/responses.py` for consistent JSON error formats.
- [ ] **Structured Logging**: Replace `print()` with `structlog` for production-grade visibility.

#### Phase 3: Integrity & DevOps (Medium)
- [ ] **Migration Rollbacks**: Create `rollback.py` and test infrastructure for Alembic.
- [ ] **Input Validation**: Centralize validation logic (username rules, etc.) in `core/validators.py`.

---

## Interactive Checklist (Sprint #27)

- [ ] **Planning**: Review detailed implementation plan in `neospace_review.md`.
- [ ] **Backend**: Implement `sockets.py` re-auth logic.
- [ ] **Backend**: Decorate all mutations with rate limits.
- [ ] **Ops**: Configure structured logging.

---

## Future Sprint: #28 (The Creator Economy)
*Deferred from #27 to prioritize hardening*

**Theme**: Script Sharing, Collaborative Coding, Branching Narratives

- [ ] **Script Publishing Flow**:
  - [ ] Allow publishing scripts from Codeground to Feed.
  - [ ] Implement "Fork" button on scripts.
- [ ] **The Song**:
  - [ ] Implement the branching narrative engine.
  - [ ] Allow collaborative editing of "Verse" nodes.

---

## Recently Completed

### Sprint #26: Emotional Intelligence
- **PAD Model**: Implemented Pleasure-Arousal-Dominance engine.
- **Dynamic Assets**: State-based avatar switching.
- **Security Hardening (Phase 1)**: Basic Socket Auth, CSP, CSRF, Secure Cookies.
