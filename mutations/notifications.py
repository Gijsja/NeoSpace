"""
Sprint #15: Live Wire — Notification Mutations

Create and manage notifications for user events.
"""

from db import get_db


def create_notification(user_id: int, notif_type: str, title: str, 
                       message: str = None, link: str = None, actor_id: int = None) -> int:
    """
    Create a notification for a user.
    
    Args:
        user_id: User to notify
        notif_type: 'sticker', 'dm', 'follow', 'mention'
        title: Short title
        message: Optional longer message
        link: Optional URL to navigate on click
        actor_id: User who triggered the notification
    
    Returns:
        New notification ID
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
    """Mark a notification as read. Returns True if successful."""
    db = get_db()
    result = db.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (notification_id, user_id)
    )
    db.commit()
    return result.rowcount > 0


def mark_all_read(user_id: int) -> int:
    """Mark all notifications as read. Returns count updated."""
    db = get_db()
    result = db.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0",
        (user_id,)
    )
    db.commit()
    return result.rowcount


def delete_notification(notification_id: int, user_id: int) -> bool:
    """Delete a notification. Returns True if successful."""
    db = get_db()
    result = db.execute(
        "DELETE FROM notifications WHERE id = ? AND user_id = ?",
        (notification_id, user_id)
    )
    db.commit()
    return result.rowcount > 0
