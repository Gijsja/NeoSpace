## Current Sprint: #28 (Active)

**Theme**: The Sovereign User (Phase 1)
**Focus**: Polishing the Single-Player Experience (Wall, Studio, Cats)

> **Objective**: Before we scale social features, the application must be a delightful creative toy for a single user.

### Tasks
#### 1. The Studio (Scripting)
- [ ] **Script Reliability**: Ensure Save/Load works 100% of the time (address audit findings).
- [ ] **Sandbox Polish**: extensive testing of p5.js integration.

#### 2. The Companion (Cats)
- [ ] **Cat Autonomy**: Verify cats react to user actions (Deeds) correctly.
- [ ] **Visual Feedback**: Ensure cat avatars update based on PAD state.

#### 3. Quality & Hygiene (Audit)
- [ ] **CI Enforcement**: `flake8` to prevent code rot.
- [ ] **Test Coverage**: specific tests for `services/script_service.py` and `services/cat_service.py`.

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full "Phased" oversight.

### Next Up: Sprint #29 (Social Connection)
Once the "Single Player" mode is solid, we enable the connections.
- Chat Polish
- Script Sharing


---

## Recently Completed

### Sprint #27.5: Bolt (Performance & Polish)
- **Observability**: Prometheus Metrics (`/metrics`), Audit Logs (`admin_ops`).
- **Resilience**: Frontend Reconnect (Exponential Backoff), Mutation Decorators.
- **UX**: Keyboard Shortcuts (`Shift + ?`), Database Archival for Speed.

### Sprint #27: The Hardening
- **Security**: WebSocket Session Re-Auth, Global Rate Limiting, Access Control Hardening.
- **Reliability**: Connection Pool Monitoring, Standardized Error Envelopes (`core/responses.py`).
- **Observability**: Structured Logging (`structlog`), Config Centralization (`config.py`).
- **DevOps**: Migration Rollback Script (`rollback.py`), Centralized Validators.


### Sprint #26: Emotional Intelligence
- **PAD Model**: Implemented Pleasure-Arousal-Dominance engine.
- **Dynamic Assets**: State-based avatar switching.
- **Security Hardening (Phase 1)**: Basic Socket Auth, CSP, CSRF, Secure Cookies.
