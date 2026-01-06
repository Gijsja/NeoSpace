
import sqlite3
import sys

DB_PATH = "app.db"

def migrate():
    print(f"Migrating {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check existing columns to avoid errors
        c.execute("PRAGMA table_info(profiles)")
        columns = [info[1] for info in c.fetchall()]
        
        new_columns = [
            ("status_message", "TEXT"),
            ("status_emoji", "TEXT"),
            ("now_activity", "TEXT"),
            ("now_activity_type", "TEXT")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column {col_name}...")
                c.execute(f"ALTER TABLE profiles ADD COLUMN {col_name} {col_type}")
            else:
                print(f"Column {col_name} already exists.")
                
        conn.commit()
        conn.close()
        print("Migration complete.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
