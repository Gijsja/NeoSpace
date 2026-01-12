from flask import current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages for a specific room using msgspec.
    10-80x faster than standard jsonify.

    Security:
    - Filters by room_id (default=1) to prevent information leakage
    - Limits to 500 messages to prevent DoS
    """
    # Get room_id from query params, default to 1 (general)
    # Validate it's an integer
    try:
        room_id = int(request.args.get('room_id', 1))
    except (ValueError, TypeError):
        room_id = 1

    # Fetch last 500 messages for the room
    # Order by ID DESC to get NEWEST 500, then reverse for chronological
    db = get_db()
    rows = db.execute(
        """
        SELECT id, user, content, created_at, edited_at, deleted_at
        FROM messages
        WHERE deleted_at IS NULL AND room_id = ?
        ORDER BY id DESC
        LIMIT 500
        """,
        (room_id,)
    ).fetchall()

    # Reverse to restore chronological order
    rows.reverse()

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
