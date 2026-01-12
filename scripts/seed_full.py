import sys
import os
import random
import sqlite3
import json
from datetime import datetime, timedelta

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from db import get_db
from werkzeug.security import generate_password_hash

app = create_app()

# --- DATA ---

# ONLY ONE USER
HANDLES = ["antigravity"]

BIOS = [
    "The Architect.", 
    "System Administrator.", 
    "Operating in the shadows.",
    "Grid Master."
]

STATUSES = [
    "Compiling...", "Online", "Monitoring", "In the mainframe"
]

ACTIVITIES = [
    ("working", "System Maintenance"), 
    ("playing", "Global Thermonuclear War"), 
    ("listening", "White Noise")
]

TEXTS = [
    "System init complete.",
    "Grid stability at 100%.",
    "Welcome to the constructs."
]

THEMES = ['default', 'dark', 'retro', 'zen']

def seed():
    with app.app_context():
        db = get_db()
        print("🌱 Seeding Protocol Initiated...")

        # 0. CLEANUP (WIPE EVERYTHING)
        print("  🧹 Wiping existing data...")
        
        # Disable FKs temporarily to allow wiping
        db.execute("PRAGMA foreign_keys = OFF")
        
        db.execute("DELETE FROM messages")
        db.execute("DELETE FROM profile_posts")
        db.execute("DELETE FROM profiles")
        db.execute("DELETE FROM users")
        
        # Re-enable FKs
        db.execute("PRAGMA foreign_keys = ON")
        
        db.commit()
        print("  ✨ Data wiped.")

        # 1. Create Single User & Profile
        created_users = []
        for handle in HANDLES:
            try:
                # Create User
                # Default password for convenience, user can change later if implemented
                pwd = generate_password_hash("password") 
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (handle, pwd)
                )
                user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                print(f"  ✓ Created user {handle}")

                # Create Profile
                db.execute(
                    """INSERT INTO profiles 
                    (user_id, display_name, bio, status_message, status_emoji, 
                    now_activity, now_activity_type, theme_preset, is_public) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                    (user_id, 
                        handle.upper(), 
                        random.choice(BIOS),
                        random.choice(STATUSES),
                        "👑",
                        random.choice(ACTIVITIES)[1],
                        random.choice(ACTIVITIES)[0],
                        'dark') 
                )
                
                created_users.append({'id': user_id, 'name': handle})

            except Exception as e:
                print(f"  ❌ Error creating {handle}: {e}")

        # 2. Feed Posts (Just a few for the single user)
        # Get existing profiles to attach posts to
        profiles = db.execute("SELECT id FROM profiles").fetchall()
        
        if profiles:
            print(f"  📝 generating intro posts...")
            for i in range(3): # Just 3 intro posts
                p_id = profiles[0]['id']
                
                payload = {"text": TEXTS[i] if i < len(TEXTS) else "..."}
                
                db.execute(
                    """INSERT INTO profile_posts 
                    (profile_id, module_type, content_payload, display_order) 
                    VALUES (?, ?, ?, ?)""",
                    (p_id, 'text', json.dumps(payload), i)
                )

        # 3. Chat Messages (Clean slate, maybe 1 welcome message)
        rooms = db.execute("SELECT id, name FROM rooms").fetchall()
        if rooms and created_users:
            print("  💬 Generating Welcome Message...")
            # Post in the first available room (usually #general)
            room = rooms[0]
            user = created_users[0]
            msg = "Welcome to NeoSpace. User 1 initialized."
            
            ts = datetime.now().isoformat()

            db.execute(
                "INSERT INTO messages (room_id, user, content, created_at) VALUES (?, ?, ?, ?)",
                (room['id'], user['name'], msg, ts)
            )

        db.commit()
        print("✅ Seeding Complete! Single User 'antigravity' created.")

if __name__ == "__main__":
    seed()
