
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages using msgspec for high-performance serialization.
    Supports cursor-based pagination (limit, before_id, after_id).
    Defaults to latest 50 messages.
    """
    limit = request.args.get("limit", 50, type=int)
    before_id = request.args.get("before_id", type=int)
    after_id = request.args.get("after_id", type=int)
    room_id = request.args.get("room_id", 1, type=int)

    # Cap limit to prevent abuse (max 100)
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 50

    query = "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL AND room_id = ?"
    params = [room_id]

    # Pagination logic
    if after_id:
        # Fetch newer messages (oldest to newest)
        query += " AND id > ? ORDER BY id ASC"
        params.append(after_id)
        reverse_output = False
    elif before_id:
        # Fetch older messages (newest to oldest)
        query += " AND id < ? ORDER BY id DESC"
        params.append(before_id)
        reverse_output = True
    else:
        # Default: Fetch latest messages (newest to oldest)
        query += " ORDER BY id DESC"
        reverse_output = True

    query += " LIMIT ?"
    params.append(limit)

    rows = get_db().execute(query, params).fetchall()
    
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
    
    # Ensure chronological order for the client
    if reverse_output:
        messages.reverse()

    response = BackfillResponse(messages=messages)
    
    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
