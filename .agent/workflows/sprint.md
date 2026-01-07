---
description: Sprint-based development workflow for NeoSpace
---

# Sprint Workflow

## Before Starting a Sprint

1. Review current state:

   ```bash
   git log --oneline -5
   git status
   ```

   // turbo

2. Identify sprint goals (max 3-5 items per sprint)

3. Create sprint backlog in `docs/SPRINT.md` with:
   - Sprint number and date range
   - Goals (what will be shipped)
   - Acceptance criteria (how we know it's done)

## During a Sprint

4. For each feature:

   - Create a task boundary (PLANNING → EXECUTION → VERIFICATION)
   - Commit frequently with conventional commits (`feat:`, `fix:`, `refactor:`)
   - Test before moving to next feature

5. Standard commit prefixes:
   - `feat:` New feature
   - `fix:` Bug fix
   - `refactor:` Code restructuring
   - `docs:` Documentation
   - `style:` CSS/formatting
   - `test:` Test additions

## Ending a Sprint

6. Run tests:

   ```bash
   python -m pytest tests/ -v
   ```

7. Create a sprint summary commit:

   ```bash
   git add -A && git commit -m "sprint(N): Summary of what shipped"
   ```

   // turbo

8. Update `docs/SPRINT.md` with:
   - ✅ Completed items
   - 🔄 Rollover items (if any)
   - 📝 Notes/learnings

## Sprint Cadence

- **Duration**: 1-2 days (micro-sprints for solo dev)
- **Demo**: Quick browser test of new features
- **Retro**: Optional notes on what went well/badly
