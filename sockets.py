
from flask_socketio import SocketIO, emit
from flask import g
from db import get_db
from mutations.message_mutations import send_message

socketio = SocketIO(cors_allowed_origins="*")

def init_sockets(app):
    socketio.init_app(app)

    @socketio.on("connect")
    def connect():
        emit("connected", {"ok": True})

    @socketio.on("send_message")
    def handle_send(data):
        g.user = data.get("user", "anonymous")
        with app.test_request_context(json=data):
            resp = send_message()
            mid = resp.json["id"]

        db = get_db()
        row = db.execute("SELECT id,user,content FROM messages WHERE id=?", (mid,)).fetchone()

        emit("message", {
            "id": row["id"],
            "user": row["user"],
            "content": row["content"],
            "deleted": False,
            "edited": False
        }, broadcast=True)

    @socketio.on("request_backfill")
    def backfill(data):
        after = int(data.get("after_id", 0))
        db = get_db()
        rows = db.execute(
            "SELECT id,user,content,edited_at,deleted_at FROM messages WHERE id>? ORDER BY id",
            (after,)
        ).fetchall()

        msgs = []
        for r in rows:
            msgs.append({
                "id": r["id"],
                "user": r["user"],
                "content": None if r["deleted_at"] else r["content"],
                "deleted": bool(r["deleted_at"]),
                "edited": bool(r["edited_at"]),
            })
        emit("backfill", {"phase": "continuity", "messages": msgs})
