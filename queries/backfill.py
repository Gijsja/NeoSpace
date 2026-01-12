
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages with pagination support.

    Query Params:
        before_id (int): Cursor for pagination (fetch messages older than this ID)

    Optimization:
    - Limited to 500 messages to prevent unbounded growth.
    - Uses msgspec for high-performance serialization (10-80x faster).
    """
    before_id = request.args.get("before_id", type=int)

    query = "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL"
    params = []

    if before_id:
        query += " AND id < ?"
        params.append(before_id)

    # ⚡ Bolt: Added LIMIT 500 and ORDER BY to prevent loading entire history
    query += " ORDER BY created_at DESC LIMIT 500"

    rows = get_db().execute(query, params).fetchall()

    # We want chronological order (oldest -> newest), but we fetched newest first
    # So we reverse the list.
    rows = list(rows)
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
