
import sqlite3

DB_PATH = "app.db"

sql_factions = """
CREATE TABLE IF NOT EXISTS cat_factions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    traits TEXT
);
"""

sql_states = """
CREATE TABLE IF NOT EXISTS cat_states (
    cat_id INTEGER PRIMARY KEY,
    pleasure REAL DEFAULT 0,
    arousal REAL DEFAULT 0,
    dominance REAL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cat_id) REFERENCES cat_personalities(id)
);
"""

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creating cat_factions...")
cursor.execute(sql_factions)

print("Creating cat_states...")
cursor.execute(sql_states)

print("Adding faction_id to cat_personalities...")
try:
    cursor.execute("ALTER TABLE cat_personalities ADD COLUMN faction_id INTEGER REFERENCES cat_factions(id);")
except sqlite3.OperationalError as e:
    # SQLite might throw specific errors if column exists
    print(f"Note: {e}")

conn.commit()
conn.close()
print("Migration applied manually.")
