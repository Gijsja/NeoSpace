import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, Integer, Text, Float, LargeBinary, ForeignKey, UniqueConstraint, CheckConstraint, Index

metadata = MetaData()

# Users Table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", Text, unique=True, nullable=False),
    Column("password_hash", Text, nullable=False),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("avatar_color", Text),
    Column("is_staff", Integer, server_default="0"),
    Column("is_banned", Integer, server_default="0"),
    Column("is_bot", Integer, server_default="0"),
    Column("bot_personality_id", Integer),
)

# Reports Table
reports = Table(
    "reports",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reporter_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("content_type", Text, nullable=False),  # 'post', 'script', 'user'
    Column("content_id", Text, nullable=False),
    Column("reason", Text),
    Column("status", Text, server_default="pending"),  # pending, resolved, dismissed
    Column("resolution_note", Text),
    Column("resolved_by", Integer, ForeignKey("users.id")),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("updated_at", Text),
)
Index("idx_reports_reporter", reports.c.reporter_id)
Index("idx_reports_reporter", reports.c.reporter_id)
Index("idx_reports_status", reports.c.status)

# Admin Operations Audit Log
admin_ops = Table(
    "admin_ops",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("admin_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("action", Text, nullable=False), # e.g. "ban_user", "update_config"
    Column("target", Text),                 # e.g. "user:123", "config:maintenance_mode"
    Column("details", Text),                # JSON or details string
    Column("ip_address", Text),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
)
Index("idx_admin_ops_created", admin_ops.c.created_at)
Index("idx_admin_ops_admin", admin_ops.c.admin_id)

# Messages Table
# Messages Table
messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user", Text, nullable=False),
    Column("content", Text),
    Column("room_id", Integer, server_default="1"),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("edited_at", Text),
    Column("deleted_at", Text),
)
Index("idx_messages_created", messages.c.created_at)
Index("idx_messages_user", messages.c.user)
Index("idx_messages_room", messages.c.room_id, messages.c.created_at)

# Messages Archive Table (Cold Storage)
messages_archive = Table(
    "messages_archive",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=False), # Keep original ID
    Column("user", Text, nullable=False),
    Column("content", Text),
    Column("room_id", Integer),
    Column("created_at", Text),
    Column("archived_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
)
Index("idx_archive_created", messages_archive.c.created_at)
Index("idx_archive_room", messages_archive.c.room_id)

# Profiles Table
profiles = Table(
    "profiles",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
    Column("display_name", Text),
    Column("bio", Text),
    Column("status_message", Text),
    Column("status_emoji", Text),
    Column("now_activity", Text),
    Column("now_activity_type", Text),
    Column("avatar_path", Text),
    Column("avatar_checksum", Text),
    Column("voice_intro_path", Text),
    Column("voice_waveform_json", Text),
    Column("anthem_url", Text),
    Column("anthem_autoplay", Integer, server_default="1"),
    Column("theme_preset", Text, server_default="default"),
    Column("accent_color", Text, server_default="#3b82f6"),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("updated_at", Text),
    Column("is_public", Integer, server_default="1"),
    Column("show_online_status", Integer, server_default="1"),
    Column("dm_policy", Text, server_default="everyone"),
)
Index("idx_profiles_user_id", profiles.c.user_id)

# Direct Messages Table
direct_messages = Table(
    "direct_messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("conversation_id", Text, nullable=False),
    Column("sender_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("recipient_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("content_encrypted", LargeBinary, nullable=False),
    Column("content_iv", LargeBinary, nullable=False),
    Column("content_tag", LargeBinary, nullable=False),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("read_at", Text),
    Column("deleted_by_sender", Integer, server_default="0"),
    Column("deleted_by_recipient", Integer, server_default="0"),
)
Index("idx_dm_conversation", direct_messages.c.conversation_id, direct_messages.c.created_at)
Index("idx_dm_recipient", direct_messages.c.recipient_id, direct_messages.c.read_at)
Index("idx_dm_sender", direct_messages.c.sender_id)

# Profile Stickers Table
profile_stickers = Table(
    "profile_stickers",
    metadata,
    Column("id", Text, primary_key=True),
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
    Column("sticker_type", Text),
    Column("image_path", Text),
    Column("text_content", Text),
    Column("x_pos", Float, nullable=False),
    Column("y_pos", Float, nullable=False),
    Column("rotation", Float, server_default="0"),
    Column("scale", Float, server_default="1"),
    Column("z_index", Integer, server_default="0"),
    Column("placed_by", Integer, ForeignKey("users.id")),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
)
Index("idx_stickers_profile", profile_stickers.c.profile_id)

# Scripts Table
scripts = Table(
    "scripts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("title", Text, nullable=False, server_default="Untitled"),
    Column("content", Text, nullable=False),
    Column("script_type", Text, server_default="p5"),
    Column("is_public", Integer, server_default="1"),
    Column("parent_id", Integer, ForeignKey("scripts.id"), nullable=True),
    Column("root_id", Integer, ForeignKey("scripts.id"), nullable=True),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("updated_at", Text),
)
Index("idx_scripts_user", scripts.c.user_id)
Index("idx_scripts_parent", scripts.c.parent_id)
Index("idx_scripts_root", scripts.c.root_id)

# Profile Scripts Table
profile_scripts = Table(
    "profile_scripts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
    Column("script_id", Integer, ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False),
    Column("display_order", Integer, nullable=False),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    UniqueConstraint("profile_id", "script_id"),
    CheckConstraint("display_order IN (0, 1, 2)"),
)
Index("idx_profile_scripts_profile", profile_scripts.c.profile_id, profile_scripts.c.display_order)

# Profile Posts Table
profile_posts = Table(
    "profile_posts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
    Column("module_type", Text, nullable=False),
    Column("content_payload", Text),
    Column("style_payload", Text),
    Column("display_order", Integer, nullable=False, server_default="0"),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("updated_at", Text),
)
Index("idx_posts_profile", profile_posts.c.profile_id, profile_posts.c.display_order)

# Friends Table
friends = Table(
    "friends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("follower_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("following_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("top8_position", Integer),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    UniqueConstraint("follower_id", "following_id"),
)
Index("idx_friends_follower", friends.c.follower_id)
Index("idx_friends_following", friends.c.following_id)

# Notifications Table
notifications = Table(
    "notifications",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("type", Text, nullable=False),
    Column("title", Text, nullable=False),
    Column("message", Text),
    Column("link", Text),
    Column("actor_id", Integer, ForeignKey("users.id")),
    Column("is_read", Integer, server_default="0"),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
)
Index("idx_notif_user", notifications.c.user_id, notifications.c.is_read)

# Rooms Table
rooms = Table(
    "rooms",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", Text, unique=True, nullable=False),
    Column("description", Text),
    Column("room_type", Text, server_default="text"),
    Column("is_default", Integer, server_default="0"),
    Column("created_by", Integer, ForeignKey("users.id")),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
)

# Songs Table (The Studio)
songs = Table(
    "songs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("title", Text, nullable=False, server_default="Untitled Track"),
    Column("data_json", Text, nullable=False),  # Full sequencer state (patterns, songs, effects)
    Column("version", Integer, server_default="1"),
    Column("is_public", Integer, server_default="0"),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("updated_at", Text),
)
Index("idx_songs_user", songs.c.user_id)

# Cat Factions
cat_factions = Table(
    "cat_factions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("description", Text),
    Column("traits", Text),
)

# Cat Personalities
cat_personalities = Table(
    "cat_personalities",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, unique=True, nullable=False),
    Column("priority", Integer, server_default="5"),
    Column("triggers", Text),
    Column("mode", Text, server_default="'cute'"),
    Column("silence_bias", Float, server_default="0.5"),
    Column("global_observer", Integer, server_default="0"),
    Column("pleasure_weight", Float, server_default="1.0"),
    Column("arousal_weight", Float, server_default="0.5"),
    Column("dominance_weight", Float, server_default="1.0"),
    Column("dialogues", Text),
    Column("avatar_url", Text),
    Column("created_at", Text, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("faction_id", Integer, ForeignKey("cat_factions.id")),
)
Index("idx_cat_personalities_faction", cat_personalities.c.faction_id)

# Cat Relationships
cat_relationships = Table(
    "cat_relationships",
    metadata,
    Column("source_cat_id", Integer, ForeignKey("cat_personalities.id"), primary_key=True),
    Column("target_user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("affinity", Float, server_default="0.0"),
    Column("compatibility", Float, server_default="0.0"),
    Column("last_updated", sa.TIMESTAMP, server_default=sa.text("CURRENT_TIMESTAMP")),
)

# Cat Memories
cat_memories = Table(
    "cat_memories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("source_cat_id", Integer, ForeignKey("cat_personalities.id"), nullable=False),
    Column("target_user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("memory_type", Text, nullable=False),
    Column("opinion_modifier", Float, server_default="0.0"),
    Column("created_at", sa.TIMESTAMP, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("expires_at", sa.TIMESTAMP),
)

# Cat States
cat_states = Table(
    "cat_states",
    metadata,
    Column("cat_id", Integer, ForeignKey("cat_personalities.id"), primary_key=True),
    Column("pleasure", Float, server_default="0"),
    Column("arousal", Float, server_default="0"),
    Column("dominance", Float, server_default="0"),
    Column("last_updated", sa.TIMESTAMP, server_default=sa.text("CURRENT_TIMESTAMP")),
    Column("last_deed_id", Integer),
)
