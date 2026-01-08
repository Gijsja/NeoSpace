
import sqlite3
import time
import functools
import threading
import queue
from contextlib import contextmanager
from flask import g, current_app

DB_PATH = "app.db"

# =============================================================================
# Concurrency Settings
# =============================================================================
BUSY_TIMEOUT_MS = 30000  # 30 seconds - SQLite will retry internally
MAX_RETRIES = 5
RETRY_DELAY_BASE = 0.05  # 50ms base delay, exponential backoff

# Connection Pool Settings
POOL_SIZE = 10  # Number of connections to maintain
POOL_TIMEOUT = 30.0  # Seconds to wait for a connection


# =============================================================================
# Schema
# =============================================================================
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
    
    -- Profile Wall 2.0: Identity & Now
    status_message TEXT,
    status_emoji TEXT,
    now_activity TEXT,
    now_activity_type TEXT, -- 'listening', 'working', 'playing', 'reading', 'thinking'
    
    -- Avatar (stored locally, not user URLs)
    avatar_path TEXT,
    avatar_checksum TEXT,
    
    -- Sprint 9: Voice Identity
    voice_intro_path TEXT,
    voice_waveform_json TEXT,
    
    -- Sprint 11: Audio Anthem (MySpace-style profile music)
    anthem_url TEXT,
    anthem_autoplay INTEGER DEFAULT 1,
    
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
    id TEXT PRIMARY KEY, -- using UUID from frontend or backend
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    sticker_type TEXT, -- Emoji char or 'image'
    image_path TEXT,   -- Path to uploaded image (Sprint 11)
    x_pos REAL NOT NULL,
    y_pos REAL NOT NULL,
    rotation REAL DEFAULT 0,
    scale REAL DEFAULT 1,
    z_index INTEGER DEFAULT 0,
    placed_by INTEGER REFERENCES users(id),
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

-- Post Code on Profiles: Pinned Scripts
CREATE TABLE IF NOT EXISTS profile_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    script_id INTEGER NOT NULL REFERENCES scripts(id) ON DELETE CASCADE,
    display_order INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_id, script_id),
    CHECK(display_order IN (0, 1, 2))
);
CREATE INDEX IF NOT EXISTS idx_profile_scripts_profile ON profile_scripts(profile_id, display_order);

-- Sprint 12: Modular Wall (Unified Posts)
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
CREATE INDEX IF NOT EXISTS idx_posts_profile ON profile_posts(profile_id, display_order);

-- Additional performance indexes
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Sprint 14: Social Graph (Friends + Top 8)
CREATE TABLE IF NOT EXISTS friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    top8_position INTEGER,  -- NULL = not in Top 8, 1-8 = position
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_id, following_id)
);
CREATE INDEX IF NOT EXISTS idx_friends_follower ON friends(follower_id);
CREATE INDEX IF NOT EXISTS idx_friends_following ON friends(following_id);
'''


# =============================================================================
# Connection Pool
# =============================================================================
class ConnectionPool:
    """
    Thread-safe SQLite connection pool.
    Maintains a pool of pre-configured connections for reuse.
    """
    
    def __init__(self, db_path, pool_size=POOL_SIZE):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialized = False
        
    def _create_connection(self):
        """Create and configure a new database connection."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0,
            isolation_level=None  # Autocommit mode
        )
        conn.row_factory = sqlite3.Row
        
        # Skip PRAGMAs for in-memory databases
        if self.db_path != ":memory:":
            # Busy timeout
            conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS};")
            # WAL mode for concurrent reads
            conn.execute("PRAGMA journal_mode = WAL;")
            # Balanced synchronization
            conn.execute("PRAGMA synchronous = NORMAL;")
            # Memory-mapped I/O (256MB)
            conn.execute("PRAGMA mmap_size = 268435456;")
            # Large page cache (64MB)
            conn.execute("PRAGMA cache_size = -64000;")
            # Temp store in memory
            conn.execute("PRAGMA temp_store = MEMORY;")
            # Foreign keys
            conn.execute("PRAGMA foreign_keys = ON;")
            # Read uncommitted for non-blocking reads (optional, for high-read scenarios)
            conn.execute("PRAGMA read_uncommitted = ON;")
            
        return conn
    
    def initialize(self):
        """Pre-populate the connection pool."""
        with self._lock:
            if self._initialized:
                return
            for _ in range(self.pool_size):
                try:
                    conn = self._create_connection()
                    self._pool.put_nowait(conn)
                except queue.Full:
                    break
            self._initialized = True
    
    def get_connection(self, timeout=POOL_TIMEOUT):
        """Get a connection from the pool."""
        try:
            return self._pool.get(timeout=timeout)
        except queue.Empty:
            # Pool exhausted, create a new connection
            return self._create_connection()
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close the connection
            conn.close()
    
    def close_all(self):
        """Close all pooled connections."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
        self._initialized = False


# Global connection pool (lazy initialized)
_connection_pool = None
_pool_lock = threading.Lock()


def _get_pool():
    """Get or create the global connection pool."""
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                # Determine path from Flask context if available
                try:
                    path = current_app.config.get("DATABASE", DB_PATH)
                except RuntimeError:
                    path = DB_PATH
                _connection_pool = ConnectionPool(path)
                _connection_pool.initialize()
    return _connection_pool


@contextmanager
def get_pooled_connection():
    """Context manager for using a pooled connection."""
    pool = _get_pool()
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.return_connection(conn)


# =============================================================================
# Retry Decorator
# =============================================================================
def with_retry(func):
    """
    Decorator that retries database operations on lock errors.
    Uses exponential backoff to avoid thundering herd.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    last_error = e
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise
        raise last_error
    return wrapper


def db_retry(operation):
    """
    Execute a database operation with retry on lock.
    For inline usage - wraps an operation callable.
    
    Usage:
        db_retry(lambda: db.execute(...))
    """
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return operation()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() or "busy" in str(e).lower():
                last_error = e
                time.sleep(RETRY_DELAY_BASE * (2 ** attempt))
            else:
                raise
    raise last_error


# =============================================================================
# Flask Integration (per-request connections)
# =============================================================================
def _configure_connection(db, path):
    """Apply optimal SQLite settings for high concurrency."""
    db.row_factory = sqlite3.Row
    
    if path == ":memory:":
        return
    
    db.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS};")
    db.execute("PRAGMA journal_mode = WAL;")
    db.execute("PRAGMA synchronous = NORMAL;")
    # JUICED: 2GB memory-mapped I/O (zero-copy reads)
    db.execute("PRAGMA mmap_size = 2147483648;")
    # JUICED: 512MB RAM cache (negative = kilobytes)
    db.execute("PRAGMA cache_size = -512000;")
    db.execute("PRAGMA temp_store = MEMORY;")
    db.execute("PRAGMA foreign_keys = ON;")


def get_db():
    """Get database connection for current request context."""
    if "db" not in g:
        path = current_app.config.get("DATABASE", DB_PATH)
        db = sqlite3.connect(
            path, 
            check_same_thread=False,
            timeout=15.0,  # JUICED: 15s allows client retry rather than indefinite hang
            isolation_level=None
        )
        _configure_connection(db, path)
        g.db = db
    return g.db


def execute_with_retry(sql, params=(), fetchone=False, fetchall=False):
    """
    Execute SQL with automatic retry on lock.
    """
    db = get_db()
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            cursor = db.execute(sql, params)
            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
            return cursor
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() or "busy" in str(e).lower():
                last_error = e
                delay = RETRY_DELAY_BASE * (2 ** attempt)
                time.sleep(delay)
            else:
                raise
    
    raise last_error


def init_db():
    """Initialize database schema."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    
    # Initialize connection pool
    _get_pool()


def close_db(e=None):
    """Close database connection."""
    db = g.pop("db", None)
    if db:
        db.close()


def shutdown_pool():
    """Shutdown the connection pool (for graceful termination)."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.close_all()
        _connection_pool = None
