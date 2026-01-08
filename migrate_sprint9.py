"""
Sprint 9 Migration: Discord-Style Rooms

Adds:
- rooms table for channel management
- room_id column to messages for scoping
- Seeds default rooms (#general, #random)
"""

import sqlite3
import sys

DB_PATH = "app.db"


def migrate():
    """Run the rooms migration."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Sprint 9: Adding rooms support...")
    
    # 1. Create rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            room_type TEXT DEFAULT 'text',
            is_default INTEGER DEFAULT 0,
            created_by INTEGER REFERENCES users(id),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Created rooms table")
    
    # 2. Check if room_id column exists in messages
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'room_id' not in columns:
        # Add room_id column with default 1 (general)
        cursor.execute("ALTER TABLE messages ADD COLUMN room_id INTEGER DEFAULT 1")
        print("  ✓ Added room_id column to messages")
    else:
        print("  ⚠ room_id column already exists")
    
    # 3. Create index for room-scoped queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_room 
        ON messages(room_id, created_at)
    """)
    print("  ✓ Created messages room index")
    
    # 4. Seed default rooms
    default_rooms = [
        ('general', 'General discussion', 'text', 1),
        ('random', 'Off-topic chaos', 'text', 1),
        ('announcements', 'Official announcements', 'announcement', 1),
    ]
    
    for name, description, room_type, is_default in default_rooms:
        try:
            cursor.execute(
                "INSERT INTO rooms (name, description, room_type, is_default) VALUES (?, ?, ?, ?)",
                (name, description, room_type, is_default)
            )
            print(f"  ✓ Seeded #{name}")
        except sqlite3.IntegrityError:
            print(f"  ⚠ #{name} already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Sprint 9 migration complete!")


if __name__ == "__main__":
    migrate()
