"""Initial schema

Revision ID: 1b811fd21d41
Revises: 
Create Date: 2026-01-09 00:07:36.595398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b811fd21d41'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables
    op.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        content TEXT,
        room_id INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        edited_at TEXT,
        deleted_at TEXT
    )''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        avatar_color TEXT
    )''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        display_name TEXT,
        bio TEXT,
        status_message TEXT,
        status_emoji TEXT,
        now_activity TEXT,
        now_activity_type TEXT,
        avatar_path TEXT,
        avatar_checksum TEXT,
        voice_intro_path TEXT,
        voice_waveform_json TEXT,
        anthem_url TEXT,
        anthem_autoplay INTEGER DEFAULT 1,
        theme_preset TEXT DEFAULT 'default',
        accent_color TEXT DEFAULT '#3b82f6',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT,
        is_public INTEGER DEFAULT 1,
        show_online_status INTEGER DEFAULT 1,
        dm_policy TEXT DEFAULT 'everyone'
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS direct_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        sender_id INTEGER NOT NULL REFERENCES users(id),
        recipient_id INTEGER NOT NULL REFERENCES users(id),
        content_encrypted BLOB NOT NULL,
        content_iv BLOB NOT NULL,
        content_tag BLOB NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        read_at TEXT,
        deleted_by_sender INTEGER DEFAULT 0,
        deleted_by_recipient INTEGER DEFAULT 0
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_dm_conversation ON direct_messages(conversation_id, created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dm_recipient ON direct_messages(recipient_id, read_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_dm_sender ON direct_messages(sender_id)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS profile_stickers (
        id TEXT PRIMARY KEY,
        profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        sticker_type TEXT,
        image_path TEXT,
        x_pos REAL NOT NULL,
        y_pos REAL NOT NULL,
        rotation REAL DEFAULT 0,
        scale REAL DEFAULT 1,
        z_index INTEGER DEFAULT 0,
        placed_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_stickers_profile ON profile_stickers(profile_id)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL DEFAULT 'Untitled',
        content TEXT NOT NULL,
        script_type TEXT DEFAULT 'p5',
        is_public INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_scripts_user ON scripts(user_id)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS profile_scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        script_id INTEGER NOT NULL REFERENCES scripts(id) ON DELETE CASCADE,
        display_order INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(profile_id, script_id),
        CHECK(display_order IN (0, 1, 2))
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_profile_scripts_profile ON profile_scripts(profile_id, display_order)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS profile_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        module_type TEXT NOT NULL,
        content_payload TEXT,
        style_payload TEXT,
        display_order INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_posts_profile ON profile_posts(profile_id, display_order)")

    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        top8_position INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(follower_id, following_id)
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_friends_follower ON friends(follower_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_friends_following ON friends(following_id)")

    op.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT,
        link TEXT,
        actor_id INTEGER REFERENCES users(id),
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id, is_read)")

    # Sprint 9: Rooms
    op.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        room_type TEXT DEFAULT 'text',
        is_default INTEGER DEFAULT 0,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room_id, created_at)")


def downgrade() -> None:
    # Quick drop of all tables in reverse dependency order
    op.execute("DROP TABLE IF EXISTS rooms")
    op.execute("DROP TABLE IF EXISTS notifications")
    op.execute("DROP TABLE IF EXISTS friends")
    op.execute("DROP TABLE IF EXISTS profile_posts")
    op.execute("DROP TABLE IF EXISTS profile_scripts")
    op.execute("DROP TABLE IF EXISTS scripts")
    op.execute("DROP TABLE IF EXISTS profile_stickers")
    op.execute("DROP TABLE IF EXISTS direct_messages")
    op.execute("DROP TABLE IF EXISTS profiles")
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS messages")
