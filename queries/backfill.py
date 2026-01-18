
from flask import current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages with pagination using msgspec.
    10-80x faster than standard jsonify.

    Query Params:
      - limit: Number of messages to return (default 50, max 100)
      - before_id: Fetch messages older than this ID
      - after_id: Fetch messages newer than this ID
    """
    try:
        limit = int(request.args.get('limit', 50))
        if limit < 1:
            limit = 50
        if limit > 100:
            limit = 100
    except ValueError:
        limit = 50

    before_id = request.args.get('before_id')
    after_id = request.args.get('after_id')

    query = (
        "SELECT id, user, content, created_at, edited_at, deleted_at "
        "FROM messages WHERE deleted_at IS NULL"
    )
    params = []

    # Pagination logic
    if after_id is not None:
        # Fetch newer messages (Chronological)
        query += " AND id > ?"
        params.append(after_id)
        query += " ORDER BY id ASC LIMIT ?"
        params.append(limit)
        reverse = False
    elif before_id is not None:
        # Fetch older messages (Reverse Chronological, then flipped)
        query += " AND id < ?"
        params.append(before_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        reverse = True
    else:
        # Default: Fetch latest messages
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        reverse = True

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

    if reverse:
        messages.reverse()

    response = BackfillResponse(messages=messages)

    # Use msgspec for ultra-fast JSON encoding
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
