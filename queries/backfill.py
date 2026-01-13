
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages for a specific room with limits.
    """
    # Get room_id from query params, default to 1 (general)
    room_id = request.args.get('room_id', 1, type=int)

    # Filter by room_id and limit to 500 messages
    rows = get_db().execute(
        """
        SELECT id, user, content, created_at, edited_at, deleted_at
        FROM messages
        WHERE deleted_at IS NULL AND room_id = ?
        ORDER BY id DESC LIMIT 500
        """,
        (room_id,)
    ).fetchall()
    
    # Reverse to maintain chronological order
    rows = rows[::-1]

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
