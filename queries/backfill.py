
from flask import jsonify, current_app
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch all chat messages using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.
    """
    rows = get_db().execute(
        "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL"
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
