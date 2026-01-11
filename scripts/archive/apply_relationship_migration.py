import sqlite3

DB_PATH = "neospace.db"

sql_memories = """
CREATE TABLE IF NOT EXISTS cat_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_cat_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    memory_type TEXT NOT NULL,
    opinion_modifier REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY(source_cat_id) REFERENCES cat_personalities(id),
    FOREIGN KEY(target_user_id) REFERENCES users(id)
);
"""

sql_relationships = """
CREATE TABLE IF NOT EXISTS cat_relationships (
    source_cat_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    affinity REAL DEFAULT 0.0,
    compatibility REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_cat_id, target_user_id),
    FOREIGN KEY(source_cat_id) REFERENCES cat_personalities(id),
    FOREIGN KEY(target_user_id) REFERENCES users(id)
);
"""

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creating cat_memories...")
cursor.execute(sql_memories)

print("Creating cat_relationships...")
cursor.execute(sql_relationships)

conn.commit()
conn.close()
print("Relationship/Memory tables created.")
