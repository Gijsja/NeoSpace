# Sprint 24: v0.4 Release

**Date Range**: 2026-01-09 to 2026-01-11

## Goals

1.  **Release v0.4.0**: Official alpha release of the "Feature Expanded" version.
2.  **Documentation Polish**: Ensure docs are aligned with the new release.
3.  **Tagging**: Git tag `v0.4.0` as a stable verification point.

## Backlog

### 📦 Release Engineering
- [x] **Version Bump**
  - [x] Update `VERSION` to `0.4.0`.
  - [x] Update `README.md` badge.
- [ ] **Release Tag**
  - [ ] Run full test suite.
  - [ ] Commit release changes.
  - [ ] Create git tag `v0.4.0`.

## Acceptance Criteria
- `VERSION` file contains `0.4.0`.
- All tests pass (`pytest tests/`).
- `git describe --tags` returns `v0.4.0`.
