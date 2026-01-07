
import sqlite3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrate_sprint12")

DB_PATH = "app.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Create table if not exists (Copied from db.py)
        logger.info("Creating profile_posts table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            
            module_type TEXT NOT NULL, -- 'text', 'image', 'link', 'script'
            content_payload TEXT,      -- JSON data (e.g. {text: "Hi"}, {script_id: 1})
            style_payload TEXT,        -- JSON style data (w, h, color)
            display_order INTEGER NOT NULL DEFAULT 0,
            
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        );
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_profile ON profile_posts(profile_id, display_order);')
        
        # 2. Migrate existing Pinned Scripts
        logger.info("Migrating existing pinned scripts...")
        
        # Check if profile_scripts exists before trying to read it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profile_scripts'")
        if cursor.fetchone():
            scripts = cursor.execute("SELECT * FROM profile_scripts").fetchall()
            
            count = 0
            for s in scripts:
                # Check if already migrated to avoid duplicates if run multiple times
                # We assume if a script post exists for this profile/script_id, it's done.
                # However, content_payload is JSON string, so naive check is hard.
                # Let's check by querying ID and display_order? No, better to just be idempotent if possible.
                # For now, simplistic check:
                
                payload = json.dumps({"script_id": s["script_id"]})
                
                exists = cursor.execute(
                    "SELECT id FROM profile_posts WHERE profile_id = ? AND module_type = 'script' AND content_payload = ?",
                    (s["profile_id"], payload)
                ).fetchone()
                
                if not exists:
                    cursor.execute(
                        """INSERT INTO profile_posts 
                           (profile_id, module_type, content_payload, display_order, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (s["profile_id"], 'script', payload, s["display_order"], s["created_at"])
                    )
                    count += 1
            
            logger.info(f"Migrated {count} pinned scripts to profile_posts.")
        else:
            logger.info("No profile_scripts table found, skipping migration.")

        conn.commit()
        logger.info("Migration Sprint 12 complete.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
