
from flask_socketio import SocketIO, emit, disconnect
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
# Maps session ID to username for quick lookup
authenticated_sockets = {}


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
        
        # Store authenticated connection
        authenticated_sockets[request.sid] = {
            "user_id": user_id,
            "username": username
        }
        
        emit("connected", {"ok": True, "username": username})
        return True

    @socketio.on("disconnect")
    def on_disconnect():
        """Clean up authenticated socket on disconnect."""
        if request.sid in authenticated_sockets:
            del authenticated_sockets[request.sid]

    @socketio.on("send_message")
    def handle_send(data):
        """
        Handle message sending via WebSocket.
        Uses server-authenticated username, ignoring any client-provided user.
        """
        # Get authenticated user from our socket registry
        auth_info = authenticated_sockets.get(request.sid)
        if not auth_info:
            emit("error", {"message": "Not authenticated"})
            return
        
        username = auth_info["username"]
        content = data.get("content", "").strip()
        
        if not content:
            emit("error", {"message": "Empty message"})
            return
        
        # Sanitize content
        safe_content = html.escape(content)
        
        # Insert directly (avoiding test_request_context complexity)
        db = get_db()
        db.execute(
            "INSERT INTO messages(user, content) VALUES (?, ?)",
            (username, safe_content)
        )
        db.commit()
        mid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        row = db.execute(
            "SELECT id, user, content, created_at FROM messages WHERE id=?",
            (mid,)
        ).fetchone()

        emit("message", {
            "id": row["id"],
            "user": row["user"],
            "content": row["content"],
            "created_at": row["created_at"],
            "deleted": False,
            "edited": False
        }, broadcast=True)

    @socketio.on("request_backfill")
    def backfill(data):
        """Fetch message history."""
        # Allow even if not in authenticated_sockets (for initial load)
        after = int(data.get("after_id", 0))
        db = get_db()
        rows = db.execute(
            """SELECT id, user, content, created_at, edited_at, deleted_at 
               FROM messages 
               WHERE id > ? AND deleted_at IS NULL
               ORDER BY id""",
            (after,)
        ).fetchall()

        msgs = []
        for r in rows:
            msgs.append({
                "id": r["id"],
                "user": r["user"],
                "content": r["content"],
                "created_at": r["created_at"],
                "deleted": False,
                "edited": bool(r["edited_at"]),
            })
        emit("backfill", {"phase": "continuity", "messages": msgs})

    @socketio.on("typing")
    def handle_typing(data):
        """Broadcast typing indicator (use authenticated username)."""
        auth_info = authenticated_sockets.get(request.sid)
        if auth_info:
            emit("typing", {"user": auth_info["username"]}, broadcast=True, include_self=False)

    @socketio.on("stop_typing")
    def handle_stop_typing(data):
        """Broadcast stop typing indicator."""
        auth_info = authenticated_sockets.get(request.sid)
        if auth_info:
            emit("stop_typing", {"user": auth_info["username"]}, broadcast=True, include_self=False)
