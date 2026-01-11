
import sqlite3

DB_PATH = "neospace.db"

sql_songs = """
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT 'Untitled Track',
    data_json TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_public INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

index_sql = "CREATE INDEX IF NOT EXISTS idx_songs_user ON songs(user_id);"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creating songs table...")
cursor.execute(sql_songs)
print("Creating index...")
cursor.execute(index_sql)

conn.commit()
conn.close()
print("Migration applied: songs table created.")
