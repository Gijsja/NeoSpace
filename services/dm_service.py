"""
DM Service - Business logic for direct message operations.
Extracted from mutations/dm.py for testability.
"""

import html
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from db import get_db
from crypto_utils import (
    get_dm_key, 
    derive_conversation_key, 
    get_conversation_id,
    encrypt_message, 
    decrypt_message
)


# =============================================
# RESULT CLASSES
# =============================================

@dataclass
class ServiceResult:
    """Standard result object for service operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: int = 200


# =============================================
# DM OPERATIONS
# =============================================

def send_message(sender_id: int, recipient_id: int, content: str) -> ServiceResult:
    """
    Send an encrypted direct message.
    
    Args:
        sender_id: ID of the sender
        recipient_id: ID of the recipient
        content: Message content (will be sanitized and encrypted)
    
    Returns:
        ServiceResult with message ID and conversation_id on success
    """
    content = content.strip()
    
    if not content:
        return ServiceResult(success=False, error="Message content required", status=400)
    if len(content) > 2000:
        return ServiceResult(success=False, error="Message too long (max 2000 chars)", status=400)
    
    db = get_db()
    
    # Check recipient exists
    recipient = db.execute(
        "SELECT id, username FROM users WHERE id = ?", 
        (recipient_id,)
    ).fetchone()
    if not recipient:
        return ServiceResult(success=False, error="Recipient not found", status=404)
    
    # Check DM policy
    profile = db.execute(
        "SELECT dm_policy FROM profiles WHERE user_id = ?",
        (recipient_id,)
    ).fetchone()
    
    if profile and profile["dm_policy"] == "nobody":
        return ServiceResult(success=False, error="User has disabled direct messages", status=403)
    
    # Check "mutuals" policy
    if profile and profile["dm_policy"] == "mutuals":
        sender_follows = db.execute(
            "SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?",
            (sender_id, recipient_id)
        ).fetchone()
        recipient_follows = db.execute(
            "SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?",
            (recipient_id, sender_id)
        ).fetchone()
        
        if not (sender_follows and recipient_follows):
            return ServiceResult(success=False, error="User only accepts DMs from mutual follows", status=403)
    
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
    
    return ServiceResult(success=True, data={
        "id": msg_id, 
        "conversation_id": conversation_id
    })


def get_conversation_messages(
    user_id: int, 
    other_user_id: int, 
    limit: int = 50, 
    before_id: Optional[int] = None
) -> ServiceResult:
    """
    Get decrypted messages for a conversation.
    
    Args:
        user_id: Current user ID
        other_user_id: Other participant ID
        limit: Max messages to return
        before_id: Pagination cursor
    
    Returns:
        ServiceResult with list of decrypted messages
    """
    db = get_db()
    conversation_id = get_conversation_id(user_id, other_user_id)
    limit = min(limit, 100)
    
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
    
    return ServiceResult(success=True, data={
        "messages": messages, 
        "conversation_id": conversation_id
    })


def mark_messages_read(user_id: int, message_id: int) -> ServiceResult:
    """
    Mark messages as read up to a given message ID.
    
    Args:
        user_id: Current user ID (must be recipient)
        message_id: Mark all messages up to this ID as read
    
    Returns:
        ServiceResult indicating success
    """
    db = get_db()
    
    db.execute(
        """UPDATE direct_messages 
           SET read_at = datetime('now')
           WHERE id <= ? AND recipient_id = ? AND read_at IS NULL""",
        (message_id, user_id)
    )
    db.commit()
    
    return ServiceResult(success=True)


def delete_message(user_id: int, message_id: int) -> ServiceResult:
    """
    Soft-delete a DM for the current user.
    The other participant can still see it.
    
    Args:
        user_id: Current user ID
        message_id: Message to delete
    
    Returns:
        ServiceResult indicating success
    """
    db = get_db()
    
    # Check message exists and user is participant
    row = db.execute(
        "SELECT sender_id, recipient_id FROM direct_messages WHERE id = ?",
        (message_id,)
    ).fetchone()
    
    if not row:
        return ServiceResult(success=False, error="Message not found", status=404)
    
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
        return ServiceResult(success=False, error="Not authorized", status=403)
    
    db.commit()
    return ServiceResult(success=True)


def list_user_conversations(user_id: int) -> ServiceResult:
    """
    List all conversations for a user.
    
    Args:
        user_id: Current user ID
    
    Returns:
        ServiceResult with list of conversations and metadata
    """
    db = get_db()
    
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
    
    return ServiceResult(success=True, data={"conversations": conversations})
