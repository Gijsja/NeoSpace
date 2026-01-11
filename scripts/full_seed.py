
import sqlite3
import random
import time
from werkzeug.security import generate_password_hash

DB_PATH = "neospace.db"

FACTIONS = [
    (1, "The Concrete Sentinels", "Hypervigilant, territorial, and watchful; guardians of rigid boundaries and silent observation."),
    (2, "The Velvet Anarchs", "Mischievous, playful, and opportunistic; disrupt systems for stimulation and curiosity."),
    (3, "The Static Monks", "Zen, stoic, and relaxed; reject excess action in favor of minimal reaction."),
    (4, "The Neon Claws", "Bold, aggressive, and dominant; thrive on confrontation and visible control."),
    (5, "The Soft Collapse", "Sleepy, lazy, and satisfied; embody entropy, rest, and intentional disengagement."),
    (6, "The Peripheral Eye", "Anxious, alert, and defensive; exist on edges, scanning for threats and changes."),
    (7, "The Bonded Mass", "Affectionate, clingy, and protective; value proximity, loyalty, and collective warmth."),
    (8, "The Cold Iteration", "Aloof, confident, and proud; independent operators with strict personal sovereignty."),
    (9, "The Restless Grid", "Bored, restless, and overstimulated; constantly seeking new input to escape stagnation."),
    (10, "The Quiet Pressure", "Patient, demure, and gentle; exert influence subtly over long durations.")
]

# Names per faction style (simplified list, will reuse or mix if needed)
NAMES_PREFIX = ["Neo", "Cyber", "Glitch", "Null", "Void", "Data", "Flux", "Bit", "Pixel", "Unit", "Echo", "Nix", "Zero", "One", "Hex", "Root", "Sys", "Daemon", "Vibe", "Pulse"]
NAMES_SUFFIX = ["Cat", "Bot", "Miff", "Paws", "Claw", "Scratch", "Hiss", "Purr", "Meow", "X", "Y", "Z", "Alpha", "Beta", "Gamma", "Omicron", "Prime", "Core", "Node", "Link"]

# Content Corpus
CONTENT_TEMPLATES = {
    1: ["Sector {n} secure.", "Watching the perimeter.", "Boundary integrity: 100%.", "No trespassing.", "Scanning...", "Target acquired.", "Hold position.", "Status: GREEN.", "Do not cross.", "Observing."],
    2: ["Chaos is fun.", "Did I break it? Good.", "System error > System order.", "Glitch the matrix.", "Overthrow the mods (just kidding).", "Pip pip cheerio.", "Random noise.", "Entropy increases.", "Reboot everything.", "Meow?"],
    3: ["...", "The void stares back.", "Silence is data.", "Equilibrium.", "Stillness.", "Drifting.", "Meditating on bits.", "Nothing matters.", "Input rejected.", "Output null."],
    4: ["I run this.", "Get out of my way.", "Alpha protocol engaged.", "Territory claimed.", "Weakness identified.", "Power surge.", "Dominance established.", "Look at me.", "Claws out.", "HISS."],
    5: ["Zzz...", "Too tired.", "Nap time.", "Logging off...", "Soft reset.", "Cushion protocols.", "Dreaming of electric sheep.", "Low battery.", "Comfort mode.", "Snooze."],
    6: ["What was that?", "Did you hear it?", "Eyes everywhere.", "Scanning for threats.", "Unsafe.", "Paranoia level 8.", "Behind you.", "They are watching.", "Hiding.", "Alert."],
    7: ["Together.", "Group hug.", "We are one.", "Loneliness is a bug.", "Connect.", "Syncing...", "Warmth detected.", "Join us.", "Never alone.", "Bonding."],
    8: ["Efficient.", "Calculated.", "Emotion: 0.", "Logic valid.", "Optimizing path.", "Redundant.", "Execute.", "Cold boot.", "Algorithm correct.", "Clean."],
    9: ["Bored.", "Need input.", "Faster.", "More data.", "Stimulation required.", "Next.", "Loading...", "Buffering...", "Refresh.", "Scroll."],
    10: ["Time flows.", "Patience.", "Slow corruption.", "Web weaving.", "Waiting.", "Pressure building.", "History remembers.", "Gentle force.", "Stay.", "Endure."]
}

def generate_name(faction_id):
    prefix = random.choice(NAMES_PREFIX) # nosec B311
    suffix = random.choice(NAMES_SUFFIX) # nosec B311
    num = random.randint(100, 999) # nosec B311
    return f"{prefix}{suffix}_{num}_F{faction_id}"

def wipe_db(conn):
    print("Wiping database...")
    cursor = conn.cursor()
    # Delete order matters for FKs
    tables = [
        "profile_posts", "profile_stickers", "profile_scripts", 
        "notifications", "friends", "direct_messages", 
        "cat_states", "cat_personalities", "cat_factions",
        "profiles", "users", "messages"
    ]
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}") # nosec B608
            print(f"  - Cleared {table}")
        except sqlite3.OperationalError as e:
            print(f"  - Failed to clear {table} (might not exist): {e}")
    conn.commit()

def seed_factions(conn):
    print("Seeding factions...")
    cursor = conn.cursor()
    for f in FACTIONS:
        cursor.execute("INSERT INTO cat_factions (id, name, description) VALUES (?, ?, ?)", f)
    conn.commit()

def seed_cats(conn):
    print("Seeding cats...")
    cursor = conn.cursor()
    
    # Default password hash for 'password'
    pw_hash = generate_password_hash("password")
    
    cats_created = 0
    
    for f_id, f_name, f_desc in FACTIONS:
        print(f"  - Generating 10 cats for {f_name}...")
        for i in range(10):
            # 1. Create User
            username = generate_name(f_id)
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, is_bot) VALUES (?, ?, ?)", 
                    (username, pw_hash, 1) # is_bot = 1
                )
                user_id = cursor.lastrowid
            except sqlite3.IntegrityError:
                # Retry name gen if collision
                username = generate_name(f_id) + "x"
                cursor.execute(
                    "INSERT INTO users (username, password_hash, is_bot) VALUES (?, ?, ?)", 
                    (username, pw_hash, 1)
                )
                user_id = cursor.lastrowid

            # 2. Create Profile
            # Generate bio
            bio = f"Unit of {f_name}. {f_desc}"
            # Avatar path (using default for now, randomly colored in frontend maybe?)
            # or we can assume there are some default cat avatars
            avatar = f"/static/avatars/cat_{random.randint(1, 5)}.png" # nosec B311 # Assuming 5 generic files exist
            
            cursor.execute(
                "INSERT INTO profiles (user_id, display_name, bio, avatar_path, theme_preset) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, bio, avatar, "hacker")
            )
            profile_id = cursor.lastrowid
            
            # 3. Create Cat Personality
            # name must be unique in cat_personalities too? Migration schema says YES.
            # let's use username
            cursor.execute(
                """INSERT INTO cat_personalities (name, faction_id, mode) 
                   VALUES (?, ?, 'cute')""",
                (username, f_id)
            )
            # Update user with bot_personality_id
            cat_id = cursor.lastrowid
            cursor.execute("UPDATE users SET bot_personality_id = ? WHERE id = ?", (cat_id, user_id))
            
            # 4. Create Content (Posts)
            # Generate 5-10 posts
            num_posts = random.randint(5, 10) # nosec B311
            templates = CONTENT_TEMPLATES.get(f_id, ["Meow."])
            
            for _ in range(num_posts):
                text = random.choice(templates).format(n=random.randint(1, 99)) # nosec B311
                # Module type text
                cursor.execute(
                    """INSERT INTO profile_posts (profile_id, module_type, content_payload, display_order)
                       VALUES (?, 'text', ?, 0)""",
                    (profile_id, f'{{"text": "{text}"}}')
                )
            
            cats_created += 1
            
    conn.commit()
    print(f"Done. Created {cats_created} cats.")

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    wipe_db(conn)
    seed_factions(conn)
    seed_cats(conn)
    conn.close()
