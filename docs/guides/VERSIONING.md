# Versioning

Version and tagging policy for LocalBBS.

---

## Version Format

```
E<epoch>.<archive>.<patch>.<qualifier>
```

| Component   | Description                                               |
| ----------- | --------------------------------------------------------- |
| `E`         | Epoch — major architectural boundary (E1 = core, E2 = UX) |
| `archive`   | Feature archive within epoch                              |
| `patch`     | Bugfix or minor change                                    |
| `qualifier` | Build state: `full`, `partial`, `dev`                     |

**Example:** `E2.A1.1.full` = Epoch 2, Archive 1, Patch 1, full build.

---

## Tagging Rules

> **Tags represent deployable, truthful snapshots.**

| Rule         | Description                                  |
| ------------ | -------------------------------------------- |
| ✅ Tag       | All tests pass, system is deployable         |
| ❌ Don't Tag | Broken tests, incomplete features, WIP state |

```bash
# Good
git tag E2.A1.2.full
git push origin E2.A1.2.full

# Bad — don't tag if tests fail
pytest  # FAILED
git tag E2.A1.3.full  # ❌ Never do this
```

---

## Current Version

Check `VERSION` file in project root or `ui/VERSION` for UI-specific version.
