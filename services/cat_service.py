"""
Cat Companion Service - services/cat_service.py

Handles cat companion AI logic, dialogue generation, and emotional state.
Cats can be actual user accounts with is_bot=True.
"""

import random
import json
import time
from typing import Optional, Dict, List, Any
from db import get_db, execute_with_retry

# =============================================================================
# Cat Personality Templates
# =============================================================================

BASE_CATS = [
    {
        "name": "beans",
        "priority": 10,
        "triggers": ["login_attempt", "login_success", "login_failure", "friend_added"],
        "global_observer": False,
        "silence_bias": 0.1,
        "traits": {"friendly": 0.9, "chaotic": 0.2, "lazy": 0.4}
    },
    {
        "name": "miso",
        "priority": 5,
        "triggers": ["timeout", "idle", "form_error", "message_sent"],
        "global_observer": True,
        "silence_bias": 0.5,
        "traits": {"friendly": 0.4, "chaotic": 0.1, "lazy": 0.8}
    },
    {
        "name": "tofu",
        "priority": 6,
        "triggers": ["page_load", "idle", "login_success", "post_created", "friend_added"],
        "global_observer": True,
        "silence_bias": 0.3,
        "traits": {"friendly": 0.7, "chaotic": 0.5, "lazy": 0.2}
    },
    {
        "name": "ash",
        "priority": 4,
        "triggers": ["idle", "timeout"],
        "global_observer": True,
        "silence_bias": 0.6,
        "traits": {"friendly": 0.3, "chaotic": 0.1, "lazy": 0.9}
    },
    {
        "name": "delta",
        "priority": 7,
        "triggers": ["post_created", "message_sent", "page_load"],
        "global_observer": False,
        "silence_bias": 0.3,
        "traits": {"friendly": 0.6, "chaotic": 0.8, "lazy": 0.1}
    },
    {
        "name": "patch",
        "priority": 3,
        "triggers": ["idle", "login_failure"],
        "global_observer": True,
        "silence_bias": 0.7,
        "traits": {"friendly": 0.2, "chaotic": 0.6, "lazy": 0.7}
    },
    {
        "name": "static",
        "priority": 8,
        "triggers": ["form_error", "system_error", "login_failure"],
        "global_observer": False,
        "silence_bias": 0.1,
        "traits": {"friendly": 0.1, "chaotic": 0.9, "lazy": 0.0}
    },
    {
        "name": "hex",
        "priority": 6,
        "triggers": ["page_load", "idle", "message_sent"],
        "global_observer": True,
        "silence_bias": 0.4,
        "traits": {"friendly": 0.5, "chaotic": 0.5, "lazy": 0.5}
    },
    {
        "name": "null",
        "priority": 2,
        "triggers": ["idle", "timeout"],
        "global_observer": True,
        "silence_bias": 0.9,
        "traits": {"friendly": 0.0, "chaotic": 0.0, "lazy": 1.0}
    },
    {
        "name": "root",
        "priority": 9,
        "triggers": ["page_load", "login_success", "login_failure"],
        "global_observer": False,
        "silence_bias": 0.2,
        "dominance_weight": 2.0,
        "traits": {"friendly": 0.1, "chaotic": 0.0, "lazy": 0.0}
    },
    {
        "name": "glitch",
        "priority": 7,
        "triggers": ["form_error", "system_error", "timeout"],
        "global_observer": True,
        "silence_bias": 0.2,
        "traits": {"friendly": 0.3, "chaotic": 1.0, "lazy": 0.1}
    },
    {
        "name": "neon",
        "priority": 6,
        "triggers": ["post_created", "friend_added"],
        "global_observer": False,
        "silence_bias": 0.3,
        "traits": {"friendly": 0.8, "chaotic": 0.7, "lazy": 0.1}
    }
]

INTENTS = {
    "login_attempt": "ack",
    "login_success": "welcome",
    "login_failure": "mock",
    "friend_added": "approval",
    "timeout": "sleepy",
    "idle": "observe",
    "form_error": "mock",
    "message_sent": "chat",
    "post_created": "praise",
    "page_load": "greet",
    "system_error": "glitch"
}

DIALOGUE_TEMPLATES = {
    "cute": {
        "ack": ["hi there!", "logging in?", "meow?"],
        "welcome": ["yay! you made it!", "welcome back friend!", "meow~ hi!"],
        "mock": ["oopsie!", "try again maybe?", "silly human."],
        "approval": ["new friends! yay!", "so popular!", "friendship is magic."],
        "sleepy": ["zzz...", "boring...", "*yawns*"],
        "observe": ["watching you.", "i see everything.", "nice cursor."],
        "chat": ["good point.", "really?", "tell me more!"],
        "praise": ["wow! love this.", "cool post!", "amazing!"],
        "greet": ["hi hi!", "meowdy!", "hello there."],
        "glitch": ["uh oh.", "system fuzzy.", "whoops."]
    },
    "pirate": {
        "ack": ["ahoy matey!", "state yer business.", "halt!"],
        "welcome": ["arrr! welcome aboard!", "yo ho! access granted.", "ay, good to see ye."],
        "mock": ["walk the plank!", "blimey, fail!", "scallywag."],
        "approval": ["more crew!", "a fine addition.", "arrr, mates!"],
        "sleepy": ["driftin'...", "calm seas...", "zzarrrr..."],
        "observe": ["spyin' on ye.", "keepin' watch.", "dead men tell no tales."],
        "chat": ["aye?", "speak up!", "is that so?"],
        "praise": ["fine booty!", "treasure!", "gold star!"],
        "greet": ["ahoy!", "arrr!", "greetings scum."],
        "glitch": ["shiver me timbers!", "leak in the hull!", "abandon ship!"]
    },
    "formal": {
        "ack": ["identifying...", "please wait.", "scanning."],
        "welcome": ["access granted.", "welcome, user.", "identity verified."],
        "mock": ["access denied.", "incompetence detected.", "error."],
        "approval": ["network expanded.", "connection established.", "optimal."],
        "sleepy": ["standby mode.", "power saving.", "idling."],
        "observe": ["monitoring.", "observing behavior.", "data collection."],
        "chat": ["noted.", "input received.", "interesting hypothesis."],
        "praise": ["quality content.", "contribution accepted.", "adequate."],
        "greet": ["system online.", "greetings.", "initializing."],
        "glitch": ["malfunction.", "error 404.", "anomaly detected."]
    },
    "chaotic": {
         "ack": ["WHO GOES THERE", "KEYS???", "CLICK CLACK"],
         "welcome": ["YOU MADE IT AHHH", "YAYAYAYAY", "IM SO HAPPY"],
         "mock": ["LOL FAIL", "NOPE NOPE NOPE", "TRY HARDER LOL"],
         "approval": ["MORE PPL!!", "CROWD SURFING", "YES YES YES"],
         "sleepy": ["BORED NOW", "ZZZzzZZz", "WAKE UP"],
         "observe": ["I SEE U", "👀", "IM IN UR WALLS"],
         "chat": ["LOUD NOISES", "WHAT???", "SDKJFHSKDJF"],
         "praise": ["THIS ROCKS", "SO COOL", "FIRE FIRE FIRE"],
         "greet": ["HI HI HI", "WHATS UP", "IM HERE"],
         "glitch": ["AJSKDLJAKS", "HELP", "REALITY BREAKING"]
    }
}


# =============================================================================
# In-Memory State (per-session familiarity tracking)
# =============================================================================

_cat_state = {
    "familiarity": {},  # cat_name -> int
    "mood": {},         # cat_name -> float (-1 to 1) 
    "energy": {},       # cat_name -> float (0 to 1)
    "last_speaker": None,
    "last_speak_time": 0
}

def _init_cat_state(name: str):
    """Initialize state for a cat."""
    if name not in _cat_state["familiarity"]:
        _cat_state["familiarity"][name] = 0
        _cat_state["mood"][name] = 0.5  # Neutral-positive start
        _cat_state["energy"][name] = 1.0 # Full energy

def _update_state(name: str, event: str):
    """Update cat internal state based on event."""
    # Familiarity caps at 50
    _cat_state["familiarity"][name] = min(_cat_state["familiarity"].get(name, 0) + 1, 50)
    
    # Mood/Energy Effects
    mood_delta = 0
    energy_delta = -0.05 # Speaking costs energy
    
    if event in ["login_success", "post_created", "friend_added"]:
        mood_delta = 0.2
    elif event in ["login_failure", "form_error", "system_error"]:
        mood_delta = -0.3
    elif event in ["idle", "timeout"]:
        energy_delta = 0.3 # Rest
        
    current_mood = _cat_state["mood"].get(name, 0.5)
    current_energy = _cat_state["energy"].get(name, 1.0)
    
    _cat_state["mood"][name] = max(-1.0, min(1.0, current_mood + mood_delta))
    _cat_state["energy"][name] = max(0.0, min(1.0, current_energy + energy_delta))
    _cat_state["last_speaker"] = name
    _cat_state["last_speak_time"] = time.time()


# =============================================================================
# Public API
# =============================================================================

def get_cat_personalities() -> List[Dict]:
    """Get all cat personalities from database."""
    try:
        rows = execute_with_retry(
            "SELECT * FROM cat_personalities ORDER BY priority DESC",
            fetchall=True
        )
        return [dict(row) for row in rows] if rows else BASE_CATS
    except Exception:
        return BASE_CATS


def get_cat_by_name(name: str) -> Optional[Dict]:
    """Get a specific cat personality."""
    try:
        row = execute_with_retry(
            "SELECT * FROM cat_personalities WHERE name = ?",
            (name,),
            fetchone=True
        )
        return dict(row) if row else None
    except Exception:
        return next((c for c in BASE_CATS if c["name"] == name), None)


def get_responding_cat(event: str, exclude_last: bool = True) -> Optional[Dict]:
    """
    Select the best cat to respond to an event.
    """
    cats = get_cat_personalities()
    eligible = []
    
    for cat in cats:
        # Check triggers
        triggers = json.loads(cat.get("triggers", "[]")) if isinstance(cat.get("triggers"), str) else cat.get("triggers", [])
        if event in triggers or cat.get("global_observer"):
            eligible.append(cat)
    
    if not eligible:
        return None
    
    # Calculate scores
    scored = []
    current_time = time.time()
    
    for cat in eligible:
        name = cat["name"]
        _init_cat_state(name)
        
        # Base Score
        score = cat.get("priority", 5) * 10
        
        # Variability
        score += random.uniform(-15, 15)
        
        # State Modifiers
        fam = _cat_state["familiarity"].get(name, 0)
        mood = _cat_state["mood"].get(name, 0)
        energy = _cat_state["energy"].get(name, 1.0)
        
        # Traits
        traits = cat.get("traits", {}) if isinstance(cat.get("traits"), dict) else json.loads(cat.get("traits", "{}"))
        friendly = traits.get("friendly", 0.5)
        
        # Modifiers
        if event in ["login_failure", "system_error"] and mood < 0:
            score += 20 # Grumpy cats like errors
        if event in ["post_created"] and friendly > 0.7:
            score += 15 # Friendly cats like posts
            
        if energy < 0.2:
            score -= 50 # Too tired
            
        # Anti-spam: punish if spoke recently
        if _cat_state["last_speaker"] == name:
             score -= 100
             
        scored.append((score, cat))
    
    # Filter out negative scores
    viable = [s for s in scored if s[0] > 0]
    
    if not viable:
        return None
        
    viable.sort(key=lambda x: x[0], reverse=True)
    return viable[0][1]


def get_dialogue(cat: Dict, event: str, mode: str = "cute") -> Optional[str]:
    """Generate a dialogue line for a cat responding to an event."""
    intent = INTENTS.get(event)
    if not intent:
        return None
    
    # Check for chaotic override in traits
    traits = cat.get("traits", {})
    if isinstance(traits, str):
        try:
            traits = json.loads(traits)
        except:
            traits = {}
            
    # Determine effective mode
    effective_mode = mode
    if traits.get("chaotic", 0) > 0.8:
        effective_mode = "chaotic"
    elif traits.get("friendly", 0) < 0.2:
        effective_mode = "pirate" # Mocking tone
        
    templates = DIALOGUE_TEMPLATES.get(effective_mode, DIALOGUE_TEMPLATES["cute"])
    
    # Fallback to cute if mode missing
    if intent not in templates:
        templates = DIALOGUE_TEMPLATES["cute"]
        
    pool = templates.get(intent, [])
    
    if not pool:
        return "..."
    
    return random.choice(pool)


def trigger_cat_response(event: str, mode: str = "cute") -> Dict[str, Any]:
    """
    Main entry point: trigger a cat response for an event.
    """
    # Global Rate Limit check (optional, let's keep it spammy for now but maybe 1s)
    if time.time() - _cat_state["last_speak_time"] < 1.5:
         return {"cat": None}

    cat = get_responding_cat(event)
    if not cat:
        return {"cat": None, "avatar": None, "line": None}
    
    line = get_dialogue(cat, event, mode)
    if not line:
        return {"cat": None, "avatar": None, "line": None}
    
    # Update state
    _update_state(cat["name"], event)
    
    return {
        "cat": cat["name"],
        "avatar": cat.get("avatar_url", f"/static/images/cats/{cat['name']}.png"),
        "line": line
    }


# =============================================================================
# Seeding Functions
# =============================================================================

def seed_cat_personalities():
    """Insert default cat personalities into the database."""
    db = get_db()
    
    for cat in BASE_CATS:
        db.execute('''
            INSERT OR IGNORE INTO cat_personalities 
            (name, priority, triggers, mode, silence_bias, global_observer, 
             pleasure_weight, arousal_weight, dominance_weight, avatar_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cat["name"],
            cat["priority"],
            json.dumps(cat["triggers"]),
            "cute",
            cat["silence_bias"],
            1 if cat.get("global_observer") else 0,
            1.0, 0.5, 1.0, # Defaults for legacy columns
            f"/static/images/cats/{cat['name']}.png"
        ))
    
    db.commit()


def seed_cat_bot_users():
    """
    Create actual user accounts for each cat.
    """
    from werkzeug.security import generate_password_hash
    import secrets
    
    db = get_db()
    
    for cat in BASE_CATS:
        # Check if user already exists
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?",
            (cat["name"],)
        ).fetchone()
        
        if existing:
            # Mark as bot if not already
            db.execute(
                "UPDATE users SET is_bot = 1 WHERE username = ?",
                (cat["name"],)
            )
            continue
        
        # Create new bot user
        password_hash = generate_password_hash(secrets.token_hex(32))
        
        cursor = db.execute('''
            INSERT INTO users (username, password_hash, is_bot, avatar_color, created_at)
            VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
        ''', (cat["name"], password_hash, "#" + secrets.token_hex(3)[:6]))
        
        user_id = cursor.lastrowid
        
        # Update bot_personality_id
        personality = db.execute(
            "SELECT id FROM cat_personalities WHERE name = ?",
            (cat["name"],)
        ).fetchone()
        
        if personality:
            db.execute(
                "UPDATE users SET bot_personality_id = ? WHERE id = ?",
                (personality["id"], user_id)
            )
        
        # Create profile
        db.execute('''
            INSERT OR IGNORE INTO profiles (user_id, display_name, bio, theme_preset)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            cat["name"].upper(),
            f"🐱 SYSTEM BIT: {cat['name'].upper()}",
            "term"
        ))
    
    db.commit()
