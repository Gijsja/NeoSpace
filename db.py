
import sqlite3
from flask import g

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
'''

def get_db():
    if "db" not in g:
        db = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
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
