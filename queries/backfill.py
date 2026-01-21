
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.
    Includes pagination to prevent DoS (LIMIT 100).
    """
    after_id = request.args.get('after_id', 0, type=int)
    db = get_db()

    if after_id == 0:
        # Initial load: Get last 100 messages
        rows = db.execute(
            "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL ORDER BY id DESC LIMIT 100"
        ).fetchall()
        rows = list(reversed(rows))
    else:
        # Sync: Get messages after ID (limit 100)
        rows = db.execute(
            "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE id > ? AND deleted_at IS NULL ORDER BY id ASC LIMIT 100",
            (after_id,)
        ).fetchall()
    
    # Convert SQLite rows to msgspec Message structs
    messages = [
        Message(
            id=r['id'],
            user=r['user'],
            content=r['content'],
            created_at=r['created_at'],
            edited_at=r['edited_at'],
            deleted_at=r['deleted_at']
        ) for r in rows
    ]
    
    response = BackfillResponse(messages=messages)
    
    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
