
from flask import request, g, jsonify
from db import get_db, db_retry
import html
import sqlite3



from security import limiter

@limiter.limit("60/minute")
def send_message():
    db = get_db()
    content = html.escape(request.json.get("content", ""))
    username = g.user['username'] if g.user else 'anonymous'
    
    def do_insert():
        row = db.execute(
            "INSERT INTO messages(user,content) VALUES (?,?) RETURNING id", 
            (username, content)
        ).fetchone()
        db.commit()
        return row
    
    try:
        row = db_retry(do_insert)
        return jsonify(id=row['id'])
    except sqlite3.OperationalError:
        return jsonify(error="Database busy, please retry"), 503


def edit_message():
    """Edit message content. Requires 'id' and 'content' in JSON body."""
    db = get_db()
    msg_id = request.json.get("id")
    content = html.escape(request.json.get("content", ""))
    
    if not msg_id:
        return jsonify(ok=False, error="Missing message id"), 400
    
    # Verify message exists and belongs to user
    row = db.execute("SELECT user FROM messages WHERE id=? AND deleted_at IS NULL", (msg_id,)).fetchone()
    if not row:
        return jsonify(ok=False, error="Message not found"), 404
    username = g.user['username'] if g.user else None
    if row["user"] != username:
        return jsonify(ok=False, error="Not authorized"), 403
    
    def do_update():
        db.execute(
            "UPDATE messages SET content=?, edited_at=datetime('now') WHERE id=?",
            (content, msg_id)
        )
        db.commit()
    
    try:
        db_retry(do_update)
        return jsonify(ok=True, id=msg_id)
    except sqlite3.OperationalError:
        return jsonify(ok=False, error="Database busy, please retry"), 503


def delete_message():
    """Soft-delete a message. Requires 'id' in JSON body."""
    db = get_db()
    msg_id = request.json.get("id")
    
    if not msg_id:
        return jsonify(ok=False, error="Missing message id"), 400
    
    # Verify message exists and belongs to user
    row = db.execute("SELECT user FROM messages WHERE id=? AND deleted_at IS NULL", (msg_id,)).fetchone()
    if not row:
        return jsonify(ok=False, error="Message not found"), 404
    username = g.user['username'] if g.user else None
    if row["user"] != username:
        return jsonify(ok=False, error="Not authorized"), 403
    
    def do_delete():
        db.execute(
            "UPDATE messages SET deleted_at=datetime('now') WHERE id=?",
            (msg_id,)
        )
        db.commit()
    
    try:
        db_retry(do_delete)
        return jsonify(ok=True, id=msg_id)
    except sqlite3.OperationalError:
        return jsonify(ok=False, error="Database busy, please retry"), 503

