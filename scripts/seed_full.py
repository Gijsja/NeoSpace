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

HANDLES = [
    "ZeroCool", "AcidBurn", "CerealKiller", "Neo", "Trinity", "Morpheus",
    "Tank", "Dozer", "Switch", "Apoc", "Mouse", "Cypher", "AgentSmith",
    "TheOracle", "Keymaker", "Merovingian", "Persephone", "Niobe", "Ghost",
    "Sparks", "Link", "Zee", "Bane", "Seraph", "Sati", "RamaKandra",
    "Kamala", "Trainman", "Architect", "DeusEx", "SpoonBoy", "Ice",
    "Taser", "Razor", "Blade", "Laser", "Phazer", "Glitch", "Pixel",
    "Vector", "Voxel", "Sprite", "Polygon", "Shader", "Render", "Frame",
    "Buffer", "Cache", "Stack", "Heap"
]

BIOS = [
    "Hacking the Gibson.", "Follow the white rabbit.", "There is no spoon.",
    "Living in the matrix.", "Wake up.", "Digital nomad.", "Crypto enthusiast.",
    "System administrator.", "Netrunner.", "Console cowboy.", "Data pirate.",
    "Construct architect.", "Signal tracer.", "Node operator.", "Grid warrior.",
    "Byte code breaker.", "Synthwave addict.", "Retro futurist.", "Neon dreamer."
]

STATUSES = [
    "Compiling...", "Uploading...", "Downloading...", "In the mainframe",
    "Jacked in", "Offline", "Away", "Busy", "Thinking", "Listening to synth"
]

ACTIVITIES = [
    ("working", "Coding"), ("playing", "Cyberpunk 2077"), ("listening", "Daft Punk"),
    ("reading", "Neuromancer"), ("thinking", "About chaos"), ("watching", "The Matrix")
]

TEXTS = [
    "System check complete. Grid is stable.",
    "Found a new exploit in the mainframe. Patching now.",
    "Anyone want to join the raid tonight?",
    "Just upgraded my cyberdeck. It flies.",
    "The sky above the port was the color of television, tuned to a dead channel.",
    "High tech, low life.",
    "Construct loading...",
    "Check out this new shader I wrote.",
    "Running low on caffeine and RAM.",
    "Who is watching the watchers?",
    "Encryption keys rotate in 5 minutes.",
    "Signal strength is low in sector 7.",
    "Recompiling the kernel...",
    "Why does it always rain in this city?",
    "Need backup on the north bridge.",
    "Proxy server is down again.",
    "Deploying to production. Fingers crossed.",
    "404 Identity Not Found.",
    "Ping.",
    "Pong."
]

THEMES = ['default', 'dark', 'retro', 'zen']

IMAGES = [
    "https://picsum.photos/seed/neo/400/300",
    "https://picsum.photos/seed/cyber/300/500",
    "https://picsum.photos/seed/punk/500/300",
    "https://picsum.photos/seed/grid/400/400",
    "https://picsum.photos/seed/matrix/600/400"
]

LINKS = [
    {"url": "https://github.com", "title": "GitHub Repo"},
    {"url": "https://news.ycombinator.com", "title": "Hacker News"},
    {"url": "https://example.com", "title": "Encrypted Uplink"}
]

CODE_SNIPPETS = [
    "```python\\ndef hack():\\n    return 'Access Granted'\\n```",
    "```js\\nconst matrix = new Matrix();\\nmatrix.enter();\\n```",
    "```sql\\n-- DROPPING TABLES...\\n```"
]

def seed():
    with app.app_context():
        db = get_db()
        print("🌱 Seeding Database Protocol Initiated...")

        # 1. Create Users & Profiles
        created_users = []
        for handle in HANDLES:
            try:
                # Check if exists
                existing = db.execute("SELECT id FROM users WHERE username = ?", (handle,)).fetchone()
                if existing:
                    user_id = existing['id']
                    # print(f"  ⚠ User {handle} exists.")
                else:
                    # Create User
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
                         random.choice(BIOS), # nosec B311
                         random.choice(STATUSES), # nosec B311
                         "👋",
                         random.choice(ACTIVITIES)[1], # nosec B311
                         random.choice(ACTIVITIES)[0], # nosec B311
                         random.choice(THEMES)) # nosec B311
                    )
                
                created_users.append({'id': user_id, 'name': handle})

            except Exception as e:
                print(f"  ❌ Error creating {handle}: {e}")

        # 2. Rooms
        rooms = db.execute("SELECT id, name FROM rooms").fetchall()
        
        # 3. Mixed Content Posts
        # Get existing profiles to attach posts to
        profiles = db.execute("SELECT id FROM profiles").fetchall()
        
        if profiles:
            print(f"  📝 generating 50 mixed posts...")
            for i in range(50):
                p_id = random.choice(profiles)['id'] # nosec B311
                type_choice = random.choice(['text', 'image', 'link', 'code']) # nosec B311
                
                payload = {}
                if type_choice == 'text':
                    payload = {"text": random.choice(TEXTS)} # nosec B311
                elif type_choice == 'image':
                    url = f"{random.choice(IMAGES)}?r={i}" # nosec B311
                    payload = {"url": url}
                elif type_choice == 'link':
                    link = random.choice(LINKS) # nosec B311
                    payload = {"url": link['url'], "title": link['title']}
                elif type_choice == 'code':
                    type_choice = 'text' 
                    payload = {"text": f"Found this snippet:\n\n{random.choice(CODE_SNIPPETS)}"} # nosec B311

                db.execute(
                    """INSERT INTO profile_posts 
                    (profile_id, module_type, content_payload, display_order) 
                    VALUES (?, ?, ?, ?)""",
                    (p_id, type_choice, json.dumps(payload), i)
                )

        # 4. Chat Messages
        if rooms and created_users:
            print("  💬 Generating Chat Messages...")
            for _ in range(100):
                room = random.choice(rooms) # nosec B311
                user = random.choice(created_users) # nosec B311
                msg = random.choice(TEXTS) # nosec B311
                
                delta = timedelta(minutes=random.randint(1, 10000)) # nosec B311
                ts = (datetime.now() - delta).isoformat()

                db.execute(
                    "INSERT INTO messages (room_id, user, content, created_at) VALUES (?, ?, ?, ?)",
                    (room['id'], user['name'], msg, ts)
                )

        db.commit()
        print("✅ Seeding Complete!")

if __name__ == "__main__":
    seed()
