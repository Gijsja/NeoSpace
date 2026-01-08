"""
Sprint #15: Live Wire — Notification Queries

Read operations for user notifications.
"""

from db import get_db


def get_unread(user_id: int) -> list:
    """Get unread notifications for a user."""
    db = get_db()
    rows = db.execute(
        """SELECT n.id, n.type, n.title, n.message, n.link, n.created_at,
                  u.username as actor_username, u.id as actor_id
           FROM notifications n
           LEFT JOIN users u ON n.actor_id = u.id
           WHERE n.user_id = ? AND n.is_read = 0
           ORDER BY n.created_at DESC
           LIMIT 50""",
        (user_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_unread_count(user_id: int) -> int:
    """Get count of unread notifications."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND is_read = 0",
        (user_id,)
    ).fetchone()
    return row["cnt"] if row else 0


def get_all(user_id: int, limit: int = 50) -> list:
    """Get all notifications for a user."""
    db = get_db()
    rows = db.execute(
        """SELECT n.id, n.type, n.title, n.message, n.link, n.is_read, n.created_at,
                  u.username as actor_username, u.id as actor_id
           FROM notifications n
           LEFT JOIN users u ON n.actor_id = u.id
           WHERE n.user_id = ?
           ORDER BY n.created_at DESC
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    return [dict(r) for r in rows]
