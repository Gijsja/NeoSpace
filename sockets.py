
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask import g, session, request
from db import get_db
from mutations.message_mutations import send_message
from core.structs import Message, row_to_message
import msgspec
import os
import html

# Security: Restrict CORS to configured origins (default: localhost for dev)
# Moved to config.py, loaded in init_sockets

socketio = SocketIO()

# Store authenticated socket connections
# Maps session ID to {user_id, username, room_id, room_name}
authenticated_sockets = {}

# WebSocket Rate Limits (requests per window seconds)
WS_MSG_LIMIT = 60
WS_MSG_WINDOW = 60
WS_TYPING_LIMIT = 10
WS_TYPING_WINDOW = 10

# Rate Limiting Storage
from collections import defaultdict, deque
import time

# Map user_id -> default dict of actions -> deque of timestamps
rate_limits = defaultdict(lambda: defaultdict(deque))

def check_rate_limit(user_id, action="message", limit=60, window=60):
    """
    Check if user exceeded rate limit for action.
    Returns True if allowed, False if limited.
    """
    now = time.time()
    timestamps = rate_limits[user_id][action]
    
    # Remove old timestamps
    while timestamps and now - timestamps[0] > window:
        timestamps.popleft()
        
    if len(timestamps) >= limit:
        return False
        
    timestamps.append(now)
    return True


def get_room_id_by_name(db, room_name):
    """Get room ID from name, defaults to 'general' if not found."""
    row = db.execute(
        "SELECT id FROM rooms WHERE name = ?",
        (room_name,)
    ).fetchone()
    if row:
        return row["id"]
    # Fallback to general
    row = db.execute("SELECT id FROM rooms WHERE name = 'general'").fetchone()
    return row["id"] if row else 1


# Helper function for session re-validation
def validate_auth(sid, max_age=3600):  # Default 1 hour re-check
    auth = authenticated_sockets.get(sid)
    if not auth:
        return False
        
    # Check if re-validation is needed
    now = time.time()
    if now - auth.get("last_auth", 0) > max_age:
        # Re-query DB to ensure user still exists and isn't banned
        db = get_db()
        user = db.execute(
            "SELECT id, is_banned FROM users WHERE id = ? AND username = ?",
            (auth["user_id"], auth["username"])
        ).fetchone()
        
        if not user or user['is_banned']:
            return False
            
        # Update timestamp on success
        auth["last_auth"] = now
        
    return True


def init_sockets(app):
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("ALLOWED_ORIGINS"),
        async_mode=app.config.get("SOCKETIO_ASYNC_MODE")
    )

    @socketio.on("connect")
    def connect(auth=None):
        """
        Validate authentication on WebSocket connect.
        Rejects unauthenticated connections and banned users.
        """
        # Get user from Flask session (set by HTTP login)
        user_id = session.get('user_id')
        username = session.get('username')
        
        if not user_id or not username:
            # Reject unauthenticated connections
            emit("error", {"message": "Authentication required"})
            disconnect()
            return False
        
        # Verify user exists and is not banned
        db = get_db()
        user = db.execute("SELECT is_banned FROM users WHERE id = ?", (user_id,)).fetchone()
        
        if not user or user['is_banned']:
             session.clear()
             emit("error", {"message": "Connection rejected: Account banned or invalid"})
             disconnect()
             return False

        # Store authenticated connection (room set on join_room event)
        authenticated_sockets[request.sid] = {
            "user_id": user_id,
            "username": username,
            "room_id": 1,  # Default to general
            "room_name": "general",
            "last_auth": time.time()  # Track auth time
        }
        
        emit("connected", {"ok": True, "username": username})
        
        # Broadcast presence
        emit("user_online", {"user_id": user_id}, broadcast=True)
        
        return True

    @socketio.on("disconnect")
    def on_disconnect():
        """Clean up authenticated socket on disconnect."""
        auth_info = authenticated_sockets.get(request.sid)
        if auth_info:
            # Leave the room
            leave_room(auth_info["room_name"])
            
            user_id = auth_info["user_id"]
            del authenticated_sockets[request.sid]
            
            # Broadcast offline (check if user has other sockets open first?)
            # For simplicity, broadcast offline. Frontend can debounce.
            emit("user_offline", {"user_id": user_id}, broadcast=True)
            
            # Optional: Clean up rate limits if memory is concern, 
            # but getting user_id here might be tricky if cleaned up too early.
            # Leaving in memory for now as they are small deques.

    @socketio.on("get_online_users")
    def handle_get_online_users():
        """Return list of currently online user IDs."""
        # Set comprehension for unique user IDs
        online_ids = list({s["user_id"] for s in authenticated_sockets.values()})
        return {"online_ids": online_ids}

    @socketio.on("join_room")
    def handle_join_room(data):
        """
        Join a specific room/channel.
        Client emits this after connect with {room: 'room_name'}.
        """
        if not validate_auth(request.sid):
            emit("error", {"message": "Session expired or invalid"})
            disconnect()
            return
            
        auth_info = authenticated_sockets[request.sid]
        
        room_name = data.get("room", "general").lower().strip()
        
        # Leave previous room if any
        old_room = auth_info.get("room_name")
        if old_room and old_room != room_name:
            leave_room(old_room)
        
        # Get room ID from database
        db = get_db()
        room_id = get_room_id_by_name(db, room_name)
        
        # Update socket state
        auth_info["room_id"] = room_id
        auth_info["room_name"] = room_name
        
        # Join Socket.IO room
        join_room(room_name)
        
        emit("room_joined", {
            "room": room_name,
            "room_id": room_id
        })

    @socketio.on("send_message")
    def handle_send(data):
        """
        Handle message sending via WebSocket.
        Uses server-authenticated username, ignoring any client-provided user.
        Messages are scoped to the user's current room.
        """
        import time
        import sqlite3
        
        if not validate_auth(request.sid):
            emit("error", {"message": "Session expired or invalid"})
            disconnect()
            return

        # Get authenticated user from our socket registry
        auth_info = authenticated_sockets[request.sid]
        
        username = auth_info["username"]
        user_id = auth_info["user_id"]
        room_id = auth_info.get("room_id", 1)
        room_name = auth_info.get("room_name", "general")
        content = data.get("content", "").strip()

        config_limit = WS_MSG_LIMIT
        config_window = WS_MSG_WINDOW

        # Rate Limiting (60 messages per 60 seconds)
        if not check_rate_limit(user_id, action="message", limit=config_limit, window=config_window):
            emit("error", {"message": "Rate limit exceeded. Slow down!"})
            return
        
        if not content:
            emit("error", {"message": "Empty message"})
            return
        
        # Sanitize content
        from utils.sanitize import clean_html
        safe_content = clean_html(content)
        
        # Insert with retry logic for high concurrency
        MAX_RETRIES = 5
        RETRY_DELAY_BASE = 0.05
        
        db = get_db()
        row = None
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                row = db.execute(
                    "INSERT INTO messages(user, content, room_id) VALUES (?, ?, ?) RETURNING id, user, content, created_at, room_id",
                    (username, safe_content, room_id)
                ).fetchone()
                db.commit()
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() or "busy" in str(e).lower():
                    last_error = e
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    time.sleep(delay)
                else:
                    print(f"Error inserting message: {e}")
                    emit("error", {"message": "Database error"})
                    return
            except Exception as e:
                db.rollback()
                print(f"Error inserting message: {e}")
                emit("error", {"message": "Database error"})
                return
        
        if row is None:
            print(f"Message insert failed after {MAX_RETRIES} retries: {last_error}")
            emit("error", {"message": "Database busy, please retry"})
            return

        # Broadcast to room only (msgspec struct for speed)
        msg = Message(
            id=row["id"],
            user=row["user"],
            content=row["content"],
            created_at=row["created_at"],
            room_id=row["room_id"],
            deleted=False,
            edited=False
        )
        emit("message", msgspec.to_builtins(msg), room=room_name)

    @socketio.on("request_backfill")
    def backfill(data):
        """Fetch message history for current room."""
        auth_info = authenticated_sockets.get(request.sid)
        room_id = auth_info.get("room_id", 1) if auth_info else 1
        
        after = int(data.get("after_id", 0))
        db = get_db()
        rows = db.execute(
            """SELECT id, user, content, created_at, edited_at, deleted_at, room_id
               FROM messages 
               WHERE id > ? AND deleted_at IS NULL AND room_id = ?
               ORDER BY id""",
            (after, room_id)
        ).fetchall()

        # Use msgspec structs for fast serialization
        msgs = []
        for r in rows:
            msg = Message(
                id=r["id"],
                user=r["user"],
                content=r["content"],
                created_at=r["created_at"],
                room_id=r["room_id"],
                deleted=False,
                edited=bool(r["edited_at"]),
            )
            msgs.append(msgspec.to_builtins(msg))
        emit("backfill", {"phase": "continuity", "messages": msgs})

    @socketio.on("typing")
    def handle_typing(data):
        """Broadcast typing indicator to room."""
        if not validate_auth(request.sid):
            return

        auth_info = authenticated_sockets[request.sid]
        
        # Rate limit typing events (prevent spam)
        if not check_rate_limit(auth_info["user_id"], action="typing", limit=WS_TYPING_LIMIT, window=WS_TYPING_WINDOW):
            return

        room_name = auth_info.get("room_name", "general")
        emit("typing", {"user": auth_info["username"]}, room=room_name, include_self=False)

    @socketio.on("stop_typing")
    def handle_stop_typing(data):
        """Broadcast stop typing indicator to room."""
        auth_info = authenticated_sockets.get(request.sid)
        if auth_info:
            room_name = auth_info.get("room_name", "general")
            emit("stop_typing", {"user": auth_info["username"]}, room=room_name, include_self=False)

    @socketio.on("latency_check")
    def latency_check(data=None):
        """
        Simple pong for client-side latency measurement.
        Returns the same data back, basically an Ack.
        """
        return {"ts": data.get("ts") if data else None}
