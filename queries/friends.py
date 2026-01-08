"""
Sprint #14: Social Graph — Friend Queries

Read operations for followers, following, and Top 8.
"""

from db import get_db


def get_followers(user_id: int) -> list:
    """Get list of users following this user."""
    db = get_db()
    rows = db.execute(
        """SELECT u.id, u.username, p.display_name, p.avatar_path
           FROM friends f
           JOIN users u ON f.follower_id = u.id
           LEFT JOIN profiles p ON p.user_id = u.id
           WHERE f.following_id = ?
           ORDER BY f.created_at DESC""",
        (user_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_following(user_id: int) -> list:
    """Get list of users this user follows."""
    db = get_db()
    rows = db.execute(
        """SELECT u.id, u.username, p.display_name, p.avatar_path, f.top8_position
           FROM friends f
           JOIN users u ON f.following_id = u.id
           LEFT JOIN profiles p ON p.user_id = u.id
           WHERE f.follower_id = ?
           ORDER BY f.created_at DESC""",
        (user_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_top8(user_id: int) -> list:
    """Get Top 8 friends for a user."""
    db = get_db()
    rows = db.execute(
        """SELECT u.id, u.username, p.display_name, p.avatar_path, f.top8_position
           FROM friends f
           JOIN users u ON f.following_id = u.id
           LEFT JOIN profiles p ON p.user_id = u.id
           WHERE f.follower_id = ? AND f.top8_position IS NOT NULL
           ORDER BY f.top8_position ASC
           LIMIT 8""",
        (user_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def is_following(follower_id: int, following_id: int) -> bool:
    """Check if follower_id follows following_id."""
    db = get_db()
    row = db.execute(
        "SELECT 1 FROM friends WHERE follower_id = ? AND following_id = ?",
        (follower_id, following_id)
    ).fetchone()
    return row is not None


def is_mutual(user_a: int, user_b: int) -> bool:
    """Check if two users follow each other (mutual friends)."""
    return is_following(user_a, user_b) and is_following(user_b, user_a)


def get_follower_count(user_id: int) -> int:
    """Get number of followers."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM friends WHERE following_id = ?",
        (user_id,)
    ).fetchone()
    return row["cnt"] if row else 0


def get_following_count(user_id: int) -> int:
    """Get number of users this user follows."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM friends WHERE follower_id = ?",
        (user_id,)
    ).fetchone()
    return row["cnt"] if row else 0
