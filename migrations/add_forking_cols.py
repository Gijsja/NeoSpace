
import sqlite3

DB_PATH = "app.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Applying migration: Add forking columns to scripts...")

try:
    print("Adding parent_id...")
    cursor.execute("ALTER TABLE scripts ADD COLUMN parent_id INTEGER REFERENCES scripts(id);")
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

try:
    print("Adding root_id...")
    cursor.execute("ALTER TABLE scripts ADD COLUMN root_id INTEGER REFERENCES scripts(id);")
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

# SQLite does not support adding indexes via ALTER TABLE directly in the same statement usually, 
# but we can create them separately.
try:
    print("Creating idx_scripts_parent...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scripts_parent ON scripts(parent_id);")
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

try:
    print("Creating idx_scripts_root...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scripts_root ON scripts(root_id);")
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

conn.commit()
conn.close()
print("Migration forking_cols applied.")
