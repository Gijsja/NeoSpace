
import sqlite3
from db import DB_PATH

def migrate():
    print(f"Migrating database at {DB_PATH} for Voice Sprint...")
    conn = sqlite3.connect(DB_PATH)
    try:
        # Check if columns exist
        cursor = conn.execute("PRAGMA table_info(profiles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'voice_intro_path' not in columns:
            print("Adding voice_intro_path...")
            conn.execute("ALTER TABLE profiles ADD COLUMN voice_intro_path TEXT")
        
        if 'voice_waveform_json' not in columns:
            print("Adding voice_waveform_json...")
            conn.execute("ALTER TABLE profiles ADD COLUMN voice_waveform_json TEXT")
            
        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
