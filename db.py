
import sqlite3
from flask import g, current_app

DB_PATH = "app.db"


SCHEMA = '''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    content TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    edited_at TEXT,
    deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    avatar_color TEXT
);

-- Sprint 6: User Profiles
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Display info (sanitized on input)
    display_name TEXT,
    bio TEXT,
    
    -- Avatar (stored locally, not user URLs)
    avatar_path TEXT,
    avatar_checksum TEXT,
    
    -- Sprint 9: Voice Identity
    voice_intro_path TEXT,
    voice_waveform_json TEXT,
    
    -- Theming (presets only, no raw CSS for security)
    theme_preset TEXT DEFAULT 'default',
    accent_color TEXT DEFAULT '#3b82f6',
    
    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    
    -- Privacy controls
    is_public INTEGER DEFAULT 1,
    show_online_status INTEGER DEFAULT 1,
    dm_policy TEXT DEFAULT 'everyone'
);

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- Sprint 6: Encrypted Direct Messages
CREATE TABLE IF NOT EXISTS direct_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    
    -- AES-256-GCM encrypted content
    content_encrypted BLOB NOT NULL,
    content_iv BLOB NOT NULL,
    content_tag BLOB NOT NULL,
    
    -- Metadata (unencrypted for queries)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    read_at TEXT,
    
    -- Per-user soft delete
    deleted_by_sender INTEGER DEFAULT 0,
    deleted_by_recipient INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_dm_conversation ON direct_messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_dm_recipient ON direct_messages(recipient_id, read_at);
CREATE INDEX IF NOT EXISTS idx_dm_sender ON direct_messages(sender_id);

-- Sprint 7: Wall Stickers
CREATE TABLE IF NOT EXISTS profile_stickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    sticker_type TEXT NOT NULL, -- Emoji char or image path
    x_pos REAL NOT NULL,
    y_pos REAL NOT NULL,
    rotation REAL DEFAULT 0,
    scale REAL DEFAULT 1,
    z_index INTEGER DEFAULT 0,
    placed_by INTEGER REFERENCES users(id), -- Nullable for now (backward compat), or NULL means owner? Let's say explicit.
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_stickers_profile ON profile_stickers(profile_id);

-- Sprint 8: Creative Sandbox Scripts
CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'Untitled',
    content TEXT NOT NULL,
    script_type TEXT DEFAULT 'p5', -- 'p5', 'three', 'vanilla'
    is_public INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_scripts_user ON scripts(user_id);
'''

def get_db():
    if "db" not in g:
        path = current_app.config.get("DATABASE", DB_PATH)
        db = sqlite3.connect(path, check_same_thread=False)
        db.row_factory = sqlite3.Row
        
        # WAL mode might not be supported in :memory: or limited environments
        if path != ":memory:":
             db.execute("PRAGMA journal_mode=WAL;")
             
        g.db = db
    return g.db

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()

def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()
