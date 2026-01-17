
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.
    Includes pagination limit to prevent fetching entire history.
    """
    # Default to 50 messages, allow client override up to 100
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
    except (ValueError, TypeError):
        limit = 50

    # Fetch latest messages using DESC order
    rows = get_db().execute(
        "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    
    # Reverse to return in chronological order (oldest -> newest)
    rows = list(reversed(rows))

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
