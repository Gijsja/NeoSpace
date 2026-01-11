import sqlite3
DB_PATH = "app.db"
conn = sqlite3.connect(DB_PATH)
try:
    print("Adding last_deed_id column...")
    conn.execute("ALTER TABLE cat_states ADD COLUMN last_deed_id INTEGER")
    print("Done.")
except Exception as e:
    print(f"Error (maybe exists): {e}")
conn.commit()
conn.close()
