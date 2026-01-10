import sqlite3
import os

DB_PATH = 'app.db'

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Adding text_content column to profile_stickers...")
        cursor.execute("ALTER TABLE profile_stickers ADD COLUMN text_content TEXT")
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column text_content already exists.")
        else:
            print(f"Error adding column: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
