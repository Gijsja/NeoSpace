from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages using msgspec for high-performance serialization.
    Supports cursor-based pagination (before_id, after_id) and limits.
    """
    # Parse pagination params
    try:
        limit = int(request.args.get('limit', 50))
        limit = max(1, min(limit, 100)) # Clamp between 1 and 100
    except (ValueError, TypeError):
        limit = 50

    try:
        room_id = int(request.args.get('room_id', 1))
    except (ValueError, TypeError):
        room_id = 1

    before_id = request.args.get('before_id')
    after_id = request.args.get('after_id')

    # Base query
    query_parts = [
        "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL AND room_id = ?"
    ]
    params = [room_id]

    should_reverse = False

    if after_id:
        try:
            aid = int(after_id)
            query_parts.append("AND id > ?")
            params.append(aid)
            # Syncing forward: get next messages in chronological order
            query_parts.append("ORDER BY id ASC")
        except ValueError:
            # Fallback if invalid ID
            query_parts.append("ORDER BY id DESC")
            should_reverse = True
    elif before_id:
        try:
            bid = int(before_id)
            query_parts.append("AND id < ?")
            params.append(bid)
            # Paging backward: get previous messages (descending), then reverse
            query_parts.append("ORDER BY id DESC")
            should_reverse = True
        except ValueError:
            # Fallback
            query_parts.append("ORDER BY id DESC")
            should_reverse = True
    else:
        # Default: get latest messages (descending), then reverse
        query_parts.append("ORDER BY id DESC")
        should_reverse = True

    query_parts.append("LIMIT ?")
    params.append(limit)

    sql = " ".join(query_parts)

    rows = get_db().execute(sql, tuple(params)).fetchall()
    
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

    # Ensure chronological order (oldest -> newest)
    if should_reverse:
        messages.reverse()
    
    response = BackfillResponse(messages=messages)
    
    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
