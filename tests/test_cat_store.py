
import pytest
from services.cats.store import CatStore
from db import get_db

@pytest.fixture
def base_cats():
    return [
        {
            "name": "Mochi",
            "priority": 10,
            "triggers": ["fish", "sleep"],
            "silence_bias": 0.2,
            "global_observer": True
        },
        {
            "name": "Tiger",
            "priority": 5,
            "triggers": ["hunt"],
            "silence_bias": 0.8,
            "global_observer": False
        }
    ]

def test_seed_personalities_and_get(app, base_cats):
    with app.app_context():
        CatStore.seed_personalities(base_cats)
        
        mochi = CatStore.get_cat_by_name("Mochi")
        assert mochi is not None
        assert mochi["priority"] == 10
        assert mochi["silence_bias"] == 0.2
        
        all_cats = CatStore.get_all_cats()
        assert len(all_cats) >= 2

def test_seed_bot_users(app, base_cats):
    with app.app_context():
        CatStore.seed_personalities(base_cats)
        CatStore.seed_bot_users(base_cats)
        
        db = get_db()
        mochi_user = db.execute("SELECT * FROM users WHERE username = 'Mochi'").fetchone()
        assert mochi_user is not None
        assert mochi_user["is_bot"] == 1
        assert mochi_user["bot_personality_id"] is not None
        
        # Check profile
        profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", (mochi_user["id"],)).fetchone()
        assert profile is not None
        assert profile["display_name"] == "MOCHI"

def test_update_cat_state(app, base_cats):
    with app.app_context():
        CatStore.seed_personalities(base_cats)
        cat = CatStore.get_cat_by_name("Mochi")
        
        CatStore.update_cat_state(cat["id"], (0.8, 0.5, 0.2))
        
        # Verify
        updated = CatStore.get_cat_by_name("Mochi")
        assert updated["pleasure"] == 0.8
        assert updated["arousal"] == 0.5
        assert updated["dominance"] == 0.2

def test_memories_and_relationships(app, base_cats):
    with app.app_context():
        # Setup cat and user
        CatStore.seed_personalities(base_cats)
        mochi = CatStore.get_cat_by_name("Mochi")
        
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('human', 'hash')")
        human_id = db.execute("SELECT id FROM users WHERE username = 'human'").fetchone()[0]
        db.commit()
        
        # Add positive memory
        CatStore.add_memory(mochi["id"], human_id, "pet", 10.0)
        
        affinity = CatStore.get_relationship(mochi["id"], human_id)
        assert affinity == 10.0
        
        count = CatStore.get_interaction_count(mochi["id"], human_id)
        assert count == 1
        
        # Add negative memory
        CatStore.add_memory(mochi["id"], human_id, "scold", -5.0)
        affinity = CatStore.get_relationship(mochi["id"], human_id)
        assert affinity == 5.0

def test_compatibility_factions(app, base_cats):
    with app.app_context():
        # Setup factions
        db = get_db()
        db.execute("INSERT INTO cat_factions (id, name) VALUES (1, 'Cute')")
        db.execute("INSERT INTO cat_factions (id, name) VALUES (2, 'Angry')")
        
        # Setup cats with factions
        db.execute('''
            INSERT INTO cat_personalities (name, faction_id) 
            VALUES ('Alice', 1), ('Bob', 1), ('Charlie', 2)
        ''')
        alice = db.execute("SELECT id FROM cat_personalities WHERE name = 'Alice'").fetchone()[0]
        bob_id = db.execute("SELECT id FROM cat_personalities WHERE name = 'Bob'").fetchone()[0]
        charlie_id = db.execute("SELECT id FROM cat_personalities WHERE name = 'Charlie'").fetchone()[0]
        
        # Make Bob and Charlie users/bots
        db.execute("INSERT INTO users (username, password_hash, is_bot, bot_personality_id) VALUES ('BobBot', 'h', 1, ?)", (bob_id,))
        bob_user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        db.execute("INSERT INTO users (username, password_hash, is_bot, bot_personality_id) VALUES ('CharlieBot', 'h', 1, ?)", (charlie_id,))
        charlie_user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.commit()
        
        # Recalculate Alice vs Bob (Same faction: +30)
        CatStore.recalculate_relationship(alice, bob_user_id)
        assert CatStore.get_relationship(alice, bob_user_id) == 30.0
        
        # Recalculate Alice vs Charlie (Rival faction: -10)
        CatStore.recalculate_relationship(alice, charlie_user_id)
        assert CatStore.get_relationship(alice, charlie_user_id) == -10.0
