
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages with filtering and limits.
    10-80x faster than standard jsonify.

    Args (query params):
        room_id: Room to fetch messages for (default: 1)
        after_id: Fetch messages after this ID (default: 0)
        limit: Max messages to return (default: 500, max: 500)
    """
    try:
        room_id = int(request.args.get('room_id', 1))
        after_id = int(request.args.get('after_id', 0))
        limit = int(request.args.get('limit', 500))
    except (ValueError, TypeError):
        # Fallback to safe defaults on invalid input
        room_id = 1
        after_id = 0
        limit = 500

    # Enforce strict upper bound to prevent DoS
    if limit > 500:
        limit = 500
    if limit < 1:
        limit = 500

    # Performance: Filter by room_id and limit to prevent full table scans
    # We use ORDER BY id ASC because we want the chronological list of messages
    # appearing after 'after_id'.
    query = """
        SELECT id, user, content, created_at, edited_at, deleted_at
        FROM messages
        WHERE deleted_at IS NULL
        AND room_id = ?
        AND id > ?
        ORDER BY id ASC
        LIMIT ?
    """

    rows = get_db().execute(query, (room_id, after_id, limit)).fetchall()
    
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
