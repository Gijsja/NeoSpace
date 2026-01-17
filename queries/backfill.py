
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch recent chat messages (default 50) using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.
    Supports pagination via 'limit' and 'before_id'.
    """
    try:
        limit = int(request.args.get('limit', 50))
        limit = max(1, min(limit, 100)) # Clamp between 1 and 100
    except ValueError:
        limit = 50

    before_id = request.args.get('before_id')

    query = "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL"
    params = []

    if before_id:
        try:
            before_id_int = int(before_id)
            query += " AND id < ?"
            params.append(before_id_int)
        except ValueError:
            pass # Ignore invalid ID

    # Optimization: Fetch only latest N messages
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    rows = get_db().execute(query, tuple(params)).fetchall()

    # Reverse to return in chronological order (oldest to newest)
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
