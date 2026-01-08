
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask import g, session, request
from db import get_db
from mutations.message_mutations import send_message
import os
import html

# Security: Restrict CORS to configured origins (default: localhost for dev)
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5000,http://127.0.0.1:5000"
).split(",")

socketio = SocketIO(cors_allowed_origins=ALLOWED_ORIGINS)

# Store authenticated socket connections
# Maps session ID to {user_id, username, room_id, room_name}
authenticated_sockets = {}


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


def init_sockets(app):
    socketio.init_app(app)

    @socketio.on("connect")
    def connect():
        """
        Validate authentication on WebSocket connect.
        Rejects unauthenticated connections.
        """
        # Get user from Flask session (set by HTTP login)
        user_id = session.get('user_id')
        username = session.get('username')
        
        if not user_id or not username:
            # Reject unauthenticated connections
            emit("error", {"message": "Authentication required"})
            disconnect()
            return False
        
        # Store authenticated connection (room set on join_room event)
        authenticated_sockets[request.sid] = {
            "user_id": user_id,
            "username": username,
            "room_id": 1,  # Default to general
            "room_name": "general"
        }
        
        emit("connected", {"ok": True, "username": username})
        return True

    @socketio.on("disconnect")
    def on_disconnect():
        """Clean up authenticated socket on disconnect."""
        auth_info = authenticated_sockets.get(request.sid)
        if auth_info:
            # Leave the room
            leave_room(auth_info["room_name"])
            del authenticated_sockets[request.sid]

    @socketio.on("join_room")
    def handle_join_room(data):
        """
        Join a specific room/channel.
        Client emits this after connect with {room: 'room_name'}.
        """
        auth_info = authenticated_sockets.get(request.sid)
        if not auth_info:
            emit("error", {"message": "Not authenticated"})
            return
        
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
        
        # Get authenticated user from our socket registry
        auth_info = authenticated_sockets.get(request.sid)
        if not auth_info:
            emit("error", {"message": "Not authenticated"})
            return
        
        username = auth_info["username"]
        room_id = auth_info.get("room_id", 1)
        room_name = auth_info.get("room_name", "general")
        content = data.get("content", "").strip()
        
        if not content:
            emit("error", {"message": "Empty message"})
            return
        
        # Sanitize content
        safe_content = html.escape(content)
        
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

        # Broadcast to room only
        emit("message", {
            "id": row["id"],
            "user": row["user"],
            "content": row["content"],
            "created_at": row["created_at"],
            "room_id": row["room_id"],
            "deleted": False,
            "edited": False
        }, room=room_name)

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

        msgs = []
        for r in rows:
            msgs.append({
                "id": r["id"],
                "user": r["user"],
                "content": r["content"],
                "created_at": r["created_at"],
                "room_id": r["room_id"],
                "deleted": False,
                "edited": bool(r["edited_at"]),
            })
        emit("backfill", {"phase": "continuity", "messages": msgs})

    @socketio.on("typing")
    def handle_typing(data):
        """Broadcast typing indicator to room."""
        auth_info = authenticated_sockets.get(request.sid)
        if auth_info:
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
