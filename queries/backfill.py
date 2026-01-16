
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages with pagination using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.

    Query Params:
        limit (int): Number of messages to return (default 50, max 100).
        before_id (int): Return messages older than this ID (cursor).
    """
    db = get_db()

    try:
        limit = int(request.args.get('limit', 50))
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
    except ValueError:
        limit = 50

    before_id = request.args.get('before_id')

    query = "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL"
    params = []

    if before_id:
        try:
            bid = int(before_id)
            query += " AND id < ?"
            params.append(bid)
        except ValueError:
            pass

    # Fetch latest messages first (DESC) so we get the most recent ones
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    rows = db.execute(query, params).fetchall()
    
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
    
    # Reverse to return chronological order (oldest -> newest) for the UI
    messages.reverse()

    response = BackfillResponse(messages=messages)
    
    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
