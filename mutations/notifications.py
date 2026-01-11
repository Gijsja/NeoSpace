"""
Sprint #15: Live Wire — Notification Mutations
Delegates to notification_service.
"""

from services import notification_service

def create_notification(user_id: int, notif_type: str, title: str, 
                       message: str = None, link: str = None, actor_id: int = None) -> int:
    """
    Create a notification for a user.
    Note: This might be called directly by other Python code if legacy imports exist.
    Preferred: Use services.notification_service directly.
    """
    return notification_service.create_notification(user_id, notif_type, title, message, link, actor_id)


def mark_read(notification_id: int, user_id: int) -> bool:
    """Mark a notification as read."""
    return notification_service.mark_read(notification_id, user_id)


def mark_all_read(user_id: int) -> int:
    """Mark all notifications as read."""
    return notification_service.mark_all_read(user_id)


def delete_notification(notification_id: int, user_id: int) -> bool:
    """Delete a notification."""
    return notification_service.delete_notification(notification_id, user_id)

