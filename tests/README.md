# Tests

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

## Test Structure

| File                      | Tests                         | Coverage |
| ------------------------- | ----------------------------- | -------- |
| `test_db.py`              | Database initialization       | 1 test   |
| `test_http.py`            | HTTP endpoints, static files  | 8 tests  |
| `test_mutations.py`       | Send, edit, delete operations | 12 tests |
| `test_socket_contract.py` | Payload structure, invariants | 15 tests |

## Test Categories

### Socket Contract (`test_socket_contract.py`)

- **Payload Contract**: Message structure validation
- **Backfill Contract**: Response format verification
- **Backfill Integration**: End-to-end backfill tests
- **Core Invariants**: Tests for rules in `CORE_INVARIANTS.md`
- **Edge Cases**: Boundary conditions, unicode, long content

### Mutation Tests (`test_mutations.py`)

- Send message (including XSS protection)
- Edit message (ownership, not found cases)
- Delete message (soft delete, ownership)

## CI/CD

Tests run automatically via GitHub Actions on push and PR to main/master.

See `.github/workflows/ci.yml` for configuration.
