
from flask import current_app, request
from db import get_db
import msgspec
from core.schemas import Message, BackfillResponse


def backfill_messages():
    """
    Fetch chat messages with pagination.
    Default: latest 50 messages.
    """
    # 1. Parse pagination params
    try:
        limit = int(request.args.get('limit', 50))
    except (ValueError, TypeError):
        limit = 50

    # Security: Hard cap on limit to prevent DoS
    if limit > 50:
        limit = 50
    if limit < 1:
        limit = 1

    before_id = request.args.get('before_id', type=int)
    after_id = request.args.get('after_id', type=int)

    # 2. Build Query
    query = (
        "SELECT id, user, content, created_at, edited_at, deleted_at "
        "FROM messages WHERE deleted_at IS NULL"
    )
    params = []

    if before_id:
        query += " AND id < ?"
        params.append(before_id)

    if after_id:
        query += " AND id > ?"
        params.append(after_id)

    # Optimization: Always fetch latest first (DESC), then reverse in app
    # This ensures we get the *closest* messages to the cursor or HEAD
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    rows = get_db().execute(query, tuple(params)).fetchall()

    # 3. Convert to Structs
    # Reverse to ensure chronological order (oldest -> newest) for client
    rows = reversed(rows)

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

    # 4. Serialize
    return current_app.response_class(
        msgspec.json.encode(response),
        mimetype='application/json'
    )
