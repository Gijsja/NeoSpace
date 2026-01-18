from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages with pagination using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.

    Optimized to use pagination and limits to avoid full table scans.
    """
    try:
        limit = int(request.args.get('limit', 50))
        limit = max(1, min(100, limit))
    except (ValueError, TypeError):
        limit = 50

    try:
        room_id = int(request.args.get('room_id', 1))
    except (ValueError, TypeError):
        room_id = 1

    query = "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL AND room_id = ?"
    params = [room_id]

    # Cursor Logic
    # after_id -> Fetch newer messages (ASC)
    # before_id -> Fetch older messages (DESC)
    # Default -> Fetch latest messages (DESC)

    is_fetching_newer = False

    try:
        if request.args.get('after_id'):
            after_id = int(request.args.get('after_id'))
            query += " AND id > ?"
            params.append(after_id)
            is_fetching_newer = True

        if request.args.get('before_id'):
            before_id = int(request.args.get('before_id'))
            query += " AND id < ?"
            params.append(before_id)
    except (ValueError, TypeError):
        pass

    if is_fetching_newer:
        query += " ORDER BY id ASC"
    else:
        query += " ORDER BY id DESC"

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
    
    # If we fetched latest/older (DESC), reverse to return in chronological order
    if not is_fetching_newer:
        messages.reverse()

    response = BackfillResponse(messages=messages)
    
    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
