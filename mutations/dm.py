"""
Direct Message mutations for Sprint 6.
Handles sending, reading, and deleting encrypted DMs.
"""

from flask import request, g, jsonify
from db import get_db
from crypto_utils import (
    get_dm_key, 
    derive_conversation_key, 
    get_conversation_id,
    encrypt_message, 
    decrypt_message
)
import html


def send_dm():
    """
    Send an encrypted direct message.
    
    Request JSON:
        recipient_id: int - ID of the recipient user
        content: str - Message content (will be encrypted)
    
    Returns:
        JSON with message ID on success
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from msgspec_models import SendDMRequest
        req = msgspec.json.decode(request.get_data(), type=SendDMRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    recipient_id = req.recipient_id
    content = req.content.strip()
    
    if not content:
        return jsonify(error="Message content required"), 400
    if len(content) > 2000:
        return jsonify(error="Message too long (max 2000 chars)"), 400
    
    db = get_db()
    sender_id = g.user["id"]
    
    # Check recipient exists
    recipient = db.execute(
        "SELECT id, username FROM users WHERE id = ?", 
        (recipient_id,)
    ).fetchone()
    if not recipient:
        return jsonify(error="Recipient not found"), 404
    
    # Check DM policy
    profile = db.execute(
        "SELECT dm_policy FROM profiles WHERE user_id = ?",
        (recipient_id,)
    ).fetchone()
    
    if profile and profile["dm_policy"] == "nobody":
        return jsonify(error="User has disabled direct messages"), 403
    
    # Check "mutuals" policy (Sprint cleanup)
    if profile and profile["dm_policy"] == "mutuals":
        # Check if both users follow each other
        sender_follows = db.execute(
            "SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?",
            (sender_id, recipient_id)
        ).fetchone()
        recipient_follows = db.execute(
            "SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?",
            (recipient_id, sender_id)
        ).fetchone()
        
        if not (sender_follows and recipient_follows):
            return jsonify(error="User only accepts DMs from mutual follows"), 403
    
    # Encrypt the message
    master_key = get_dm_key()
    conversation_key = derive_conversation_key(sender_id, recipient_id, master_key)
    conversation_id = get_conversation_id(sender_id, recipient_id)
    
    # Sanitize before encryption (defense in depth)
    safe_content = html.escape(content)
    ciphertext, iv, tag = encrypt_message(safe_content, conversation_key)
    
    # Store encrypted message
    db.execute(
        """INSERT INTO direct_messages 
           (conversation_id, sender_id, recipient_id, content_encrypted, content_iv, content_tag)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (conversation_id, sender_id, recipient_id, ciphertext, iv, tag)
    )
    db.commit()
    
    msg_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    return jsonify(ok=True, id=msg_id, conversation_id=conversation_id)


def get_conversation():
    """
    Get decrypted messages for a conversation.
    
    Query params:
        with_user: int - ID of the other user in conversation
        limit: int - Max messages to return (default 50)
        before_id: int - Pagination cursor
    
    Returns:
        JSON with list of decrypted messages
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    other_user_id = request.args.get("with_user", type=int)
    limit = min(request.args.get("limit", 50, type=int), 100)
    before_id = request.args.get("before_id", type=int)
    
    if not other_user_id:
        return jsonify(error="with_user parameter required"), 400
    
    db = get_db()
    user_id = g.user["id"]
    conversation_id = get_conversation_id(user_id, other_user_id)
    
    # Build query with optional pagination
    query = """
        SELECT 
            id, sender_id, recipient_id, 
            content_encrypted, content_iv, content_tag,
            created_at, read_at
        FROM direct_messages
        WHERE conversation_id = ?
          AND ((sender_id = ? AND deleted_by_sender = 0)
               OR (recipient_id = ? AND deleted_by_recipient = 0))
    """
    params = [conversation_id, user_id, user_id]
    
    if before_id:
        query += " AND id < ?"
        params.append(before_id)
    
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    rows = db.execute(query, params).fetchall()
    
    # Decrypt messages
    master_key = get_dm_key()
    conversation_key = derive_conversation_key(user_id, other_user_id, master_key)
    
    messages = []
    for row in rows:
        try:
            content = decrypt_message(
                row["content_encrypted"],
                row["content_iv"],
                row["content_tag"],
                conversation_key
            )
        except Exception:
            content = "[Decryption failed]"
        
        messages.append({
            "id": row["id"],
            "sender_id": row["sender_id"],
            "is_mine": row["sender_id"] == user_id,
            "content": content,
            "created_at": row["created_at"],
            "read_at": row["read_at"]
        })
    
    # Reverse to chronological order
    messages.reverse()
    
    return jsonify(messages=messages, conversation_id=conversation_id)


def mark_dm_read():
    """
    Mark messages as read up to a given message ID.
    
    Request JSON:
        message_id: int - Mark all messages up to this ID as read
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from msgspec_models import MarkDMReadRequest
        req = msgspec.json.decode(request.get_data(), type=MarkDMReadRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    message_id = req.message_id
    
    db = get_db()
    user_id = g.user["id"]
    
    # Only mark messages where current user is recipient
    db.execute(
        """UPDATE direct_messages 
           SET read_at = datetime('now')
           WHERE id <= ? AND recipient_id = ? AND read_at IS NULL""",
        (message_id, user_id)
    )
    db.commit()
    
    return jsonify(ok=True)


def delete_dm():
    """
    Soft-delete a DM for the current user.
    The other participant can still see it.
    
    Request JSON:
        message_id: int - Message to delete
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from msgspec_models import DeleteDMRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteDMRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    message_id = req.message_id
    
    db = get_db()
    user_id = g.user["id"]
    
    # Check message exists and user is participant
    row = db.execute(
        "SELECT sender_id, recipient_id FROM direct_messages WHERE id = ?",
        (message_id,)
    ).fetchone()
    
    if not row:
        return jsonify(error="Message not found"), 404
    
    if row["sender_id"] == user_id:
        db.execute(
            "UPDATE direct_messages SET deleted_by_sender = 1 WHERE id = ?",
            (message_id,)
        )
    elif row["recipient_id"] == user_id:
        db.execute(
            "UPDATE direct_messages SET deleted_by_recipient = 1 WHERE id = ?",
            (message_id,)
        )
    else:
        return jsonify(error="Not authorized"), 403
    
    db.commit()
    return jsonify(ok=True)


def list_conversations():
    """
    List all conversations for the current user.
    
    Returns:
        JSON with list of conversations and last message preview
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    db = get_db()
    user_id = g.user["id"]
    
    # Get distinct conversations with latest message
    query = """
        SELECT 
            dm.conversation_id,
            dm.id as last_message_id,
            dm.sender_id,
            dm.recipient_id,
            dm.created_at,
            dm.read_at,
            CASE 
                WHEN dm.sender_id = ? THEN dm.recipient_id 
                ELSE dm.sender_id 
            END as other_user_id
        FROM direct_messages dm
        INNER JOIN (
            SELECT conversation_id, MAX(id) as max_id
            FROM direct_messages
            WHERE (sender_id = ? AND deleted_by_sender = 0)
               OR (recipient_id = ? AND deleted_by_recipient = 0)
            GROUP BY conversation_id
        ) latest ON dm.id = latest.max_id
        ORDER BY dm.created_at DESC
    """
    
    rows = db.execute(query, (user_id, user_id, user_id)).fetchall()
    
    conversations = []
    for row in rows:
        # Get other user info
        other = db.execute(
            """SELECT u.username, p.display_name, p.avatar_path
               FROM users u
               LEFT JOIN profiles p ON u.id = p.user_id
               WHERE u.id = ?""",
            (row["other_user_id"],)
        ).fetchone()
        
        # Count unread
        unread = db.execute(
            """SELECT COUNT(*) as c FROM direct_messages
               WHERE conversation_id = ? AND recipient_id = ? AND read_at IS NULL""",
            (row["conversation_id"], user_id)
        ).fetchone()["c"]
        
        conversations.append({
            "conversation_id": row["conversation_id"],
            "other_user_id": row["other_user_id"],
            "other_username": other["username"] if other else "Unknown",
            "other_display_name": other["display_name"] if other else None,
            "last_message_at": row["created_at"],
            "unread_count": unread
        })
    
    return jsonify(conversations=conversations)
