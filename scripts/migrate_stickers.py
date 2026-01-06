
import sqlite3
import os

DB_PATH = "app.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("No database found, nothing to migrate.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        # Check if column exists
        cursor.execute("PRAGMA table_info(profile_stickers)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "placed_by" not in columns:
            print("Adding 'placed_by' column to profile_stickers...")
            cursor.execute("ALTER TABLE profile_stickers ADD COLUMN placed_by INTEGER REFERENCES users(id)")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column 'placed_by' already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
