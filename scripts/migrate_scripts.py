
import sqlite3
from db import DB_PATH

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    try:
        # Create scripts table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL DEFAULT 'Untitled',
            content TEXT NOT NULL,
            script_type TEXT DEFAULT 'p5', -- 'p5', 'three', 'vanilla'
            is_public INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        );
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_scripts_user ON scripts(user_id);')
        print("Created scripts table.")
        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
