
from flask import jsonify, current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch all chat messages using msgspec for high-performance serialization.
    10-80x faster than standard jsonify.
    Supports limit (max 50) and before_id pagination.
    """
    limit = request.args.get('limit', 50, type=int)
    before_id = request.args.get('before_id', type=int)

    # Hard limit
    if limit > 50: limit = 50

    query = "SELECT id, user, content, created_at, edited_at, deleted_at FROM messages WHERE deleted_at IS NULL"
    params = []

    if before_id:
        query += " AND id < ?"
        params.append(before_id)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    rows = get_db().execute(query, params).fetchall()

    # Restore chronological order for the client
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
