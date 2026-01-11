"""
Notification Service - Business logic for notifications.
"""

from typing import Optional
from db import get_db

def create_notification(
    user_id: int, 
    notif_type: str, 
    title: str, 
    message: Optional[str] = None, 
    link: Optional[str] = None, 
    actor_id: Optional[int] = None
) -> int:
    """
    Create a notification for a user.
    Returns: New notification ID.
    """
    db = get_db()
    cursor = db.execute(
        """INSERT INTO notifications (user_id, type, title, message, link, actor_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, notif_type, title, message, link, actor_id)
    )
    db.commit()
    return cursor.lastrowid

def mark_read(notification_id: int, user_id: int) -> bool:
    """Mark a notification as read."""
    db = get_db()
    result = db.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (notification_id, user_id)
    )
    db.commit()
    return result.rowcount > 0

def mark_all_read(user_id: int) -> int:
    """Mark all notifications as read."""
    db = get_db()
    result = db.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0",
        (user_id,)
    )
    db.commit()
    return result.rowcount

def delete_notification(notification_id: int, user_id: int) -> bool:
    """Delete a notification."""
    db = get_db()
    result = db.execute(
        "DELETE FROM notifications WHERE id = ? AND user_id = ?",
        (notification_id, user_id)
    )
    db.commit()
    return result.rowcount > 0
