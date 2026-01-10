import sqlite3
import random

DB_PATH = "app.db"

def seed_rivalries():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Get All Cats and their Bot User IDs
    # We join cat_personalities with users on username (since we seeded them matching)
    query = """
    SELECT 
        c.id as cat_id, 
        c.name, 
        u.id as user_id,
        f.name as faction
    FROM cat_personalities c
    JOIN users u ON u.username = c.name
    LEFT JOIN cat_factions f ON c.faction_id = f.id
    """
    rows = cursor.execute(query).fetchall()
    cats = {row['name']: row for row in rows}

    print(f"Found {len(cats)} cats to tangle social threads for.")

    # 2. Define Dynamics
    # (Source Cat Name, Target Cat Name, Memory Type, Impact)
    relationships = [
        ("beans", "miso", "rivalry", -15.0), # Beans hates Miso
        ("miso", "beans", "rivalry", -25.0), # Miso hates Beans more
        ("root", "glitch", "alliance", 20.0), # Pirate loves Glitch
        ("glitch", "root", "alliance", 10.0),
        ("patch", "static", "distrust", -5.0),
        ("tofu", "beans", "friend", 15.0),
    ]

    # 3. Insert Memories
    count = 0
    for src_name, tgt_name, mem_type, impact in relationships:
        if src_name not in cats or tgt_name not in cats:
            print(f"Skipping {src_name}->{tgt_name} (Missing entities)")
            continue

        src = cats[src_name]
        tgt = cats[tgt_name]

        cursor.execute("""
            INSERT INTO cat_memories (source_cat_id, target_user_id, memory_type, opinion_modifier, expires_at)
            VALUES (?, ?, ?, ?, datetime('now', '+30 days'))
        """, (src['cat_id'], tgt['user_id'], mem_type, impact))
        count += 1
        print(f"Logged: {src_name} formed '{mem_type}' memory of {tgt_name} ({impact})")

        # Also trigger Relationship update (hacky: manually doing SQL for update)
        # In real app store.recalculate_relationship handles this.
        cursor.execute("""
            INSERT INTO cat_relationships (source_cat_id, target_user_id, affinity, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(source_cat_id, target_user_id) DO UPDATE SET
                affinity = affinity + ?
        """, (src['cat_id'], tgt['user_id'], impact, impact))

    conn.commit()
    conn.close()
    print(f"Done. {count} memories seeded.")

if __name__ == "__main__":
    seed_rivalries()
