
import pytest
from db import init_db, get_db

def test_cat_memories_index_usage(app):
    """
    Verify that the critical query in CatStore.recalculate_relationship
    uses the optimized index idx_cat_memories_lookup.
    """
    with app.app_context():
        init_db()
        db = get_db()

        # Seed dependencies for Foreign Keys
        db.execute("INSERT INTO users (id, username, password_hash) VALUES (1, 'user1', 'hash')")
        # cat_factions is referenced by cat_personalities
        db.execute("INSERT INTO cat_factions (id, name) VALUES (1, 'faction1')")
        # cat_personalities
        db.execute("INSERT INTO cat_personalities (id, name, faction_id) VALUES (1, 'cat1', 1)")

        # Populate with some data
        db.execute("INSERT INTO cat_memories (source_cat_id, target_user_id, expires_at, opinion_modifier) VALUES (1, 1, '2025-01-01', 1.0)")

        # Critical query from services/cats/store.py
        query = "SELECT SUM(opinion_modifier) FROM cat_memories WHERE source_cat_id = ? AND target_user_id = ? AND expires_at > datetime('now')"

        cursor = db.execute(f"EXPLAIN QUERY PLAN {query}", (1, 1))
        plan = cursor.fetchall()

        print("\nQuery Plan:")
        found = False
        for row in plan:
            detail = row['detail']
            print(detail)
            if "USING INDEX idx_cat_memories_lookup" in detail:
                found = True

        assert found, f"Query is not using the expected index 'idx_cat_memories_lookup'. Plan: {[row['detail'] for row in plan]}"
