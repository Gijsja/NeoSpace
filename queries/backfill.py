from flask import current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.

    Optimized: Limits to last 50 messages to prevent performance degradation.
    Supports 'before_id' for pagination.
    """
    before_id = request.args.get('before_id', type=int)

    query = """
        SELECT id, user, content, created_at, edited_at, deleted_at
        FROM messages
        WHERE deleted_at IS NULL
    """
    params = []

    if before_id is not None:
        query += " AND id < ?"
        params.append(before_id)

    query += " ORDER BY id DESC LIMIT 50"

    # Fetch messages
    rows = get_db().execute(query, params).fetchall()

    # Convert SQLite rows to msgspec Message structs
    # Reverse rows to maintain chronological order (oldest -> newest)
    messages = [
        Message(
            id=r['id'],
            user=r['user'],
            content=r['content'],
            created_at=r['created_at'],
            edited_at=r['edited_at'],
            deleted_at=r['deleted_at']
        ) for r in reversed(rows)
    ]

    response = BackfillResponse(messages=messages)

    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
