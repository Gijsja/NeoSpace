# Core Frozen

> ⚠️ **The backend core is frozen as of E1.**

## What This Means

No semantic changes are permitted to the following during E2 (UX) work:

- Database schema (`messages` table structure)
- HTTP endpoint behavior (`/send`, `/edit`, `/delete`, `/backfill`, `/unread`)
- Socket event payloads (`message`, `backfill`, `connected`)
- Core business logic (ownership checks, soft-delete, HTML escaping)

## Why

Stability enables:

- Predictable client behavior
- Safe UI experimentation
- Reliable test baselines
- Zero-regression guarantee

## Exceptions

Changes require a new epoch (E3) with:

1. Migration plan
2. Backward compatibility strategy
3. Full test suite update

See also: [CORE_INVARIANTS](CORE_INVARIANTS.md) | [V2_SCOPE](V2_SCOPE.md)
