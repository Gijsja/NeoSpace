# Core Invariants

These rules are **non-negotiable**. Violating any invariant is a critical bug.

## The Five Invariants

| #   | Invariant                                | Implication                                 |
| --- | ---------------------------------------- | ------------------------------------------- |
| 1   | **Server is the single source of truth** | Client never derives state locally          |
| 2   | **Client never infers state**            | All state comes from server events          |
| 3   | **Backfill is canonical**                | Reconnect must yield identical state        |
| 4   | **Deleted content is never leaked**      | Soft-deleted messages return `null` content |
| 5   | **Reconnect is idempotent**              | Multiple reconnects produce same result     |

## Enforcement

- **Invariant 1-2**: Client only renders from `message` and `backfill` events
- **Invariant 3**: `request_backfill` returns full message history with current state
- **Invariant 4**: Deleted messages have `content: null`, `deleted: true`
- **Invariant 5**: `after_id` parameter enables incremental sync

## Testing

These invariants are verified in `tests/test_socket_contract.py` and `tests/test_mutations.py`.
