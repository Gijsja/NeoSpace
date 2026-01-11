"""
Friends Service - Business logic for social graph operations.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from db import get_db

@dataclass
class ServiceResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: int = 200

def follow_user(follower_id: int, target_id: int) -> ServiceResult:
    """
    Follow a user.
    """
    if follower_id == target_id:
        return ServiceResult(success=False, error="Cannot follow yourself", status=400)
    
    db = get_db()
    
    # Check target exists
    target = db.execute("SELECT id, username FROM users WHERE id = ?", (target_id,)).fetchone()
    if not target:
        return ServiceResult(success=False, error="User not found", status=404)
        
    # Check if already following
    existing = db.execute(
        "SELECT id FROM friends WHERE follower_id = ? AND following_id = ?",
        (follower_id, target_id)
    ).fetchone()
    
    if existing:
        return ServiceResult(success=True, data={"already_following": True})
        
    try:
        db.execute(
            "INSERT INTO friends (follower_id, following_id) VALUES (?, ?)",
            (follower_id, target_id)
        )
        db.commit()
        
        # Trigger notification
        # We can implement this via a callback or importing notification service?
        # Better to keep services decoupled? 
        # Typically one service calling another is fine.
        # Ideally, we return success and let the caller (mutation) handle notifications or use an event system.
        # But for this refactor, let's include it here to centralize logic.
        from services.notification_service import create_notification
        
        # Get follower username for notification
        follower = db.execute("SELECT username FROM users WHERE id = ?", (follower_id,)).fetchone()
        
        create_notification(
            user_id=target_id,
            notif_type="follow",
            title=f"{follower['username']} started following you",
            link=f"/wall?user_id={follower_id}",
            actor_id=follower_id
        )
        
    except Exception as e:
        return ServiceResult(success=False, error=str(e), status=500)
        
    return ServiceResult(success=True, data={"already_following": False})


def unfollow_user(follower_id: int, target_id: int) -> ServiceResult:
    """
    Unfollow a user.
    """
    db = get_db()
    db.execute(
        "DELETE FROM friends WHERE follower_id = ? AND following_id = ?",
        (follower_id, target_id)
    )
    db.commit()
    return ServiceResult(success=True)


def set_top8(user_id: int, friend_ids: List[int]) -> ServiceResult:
    """
    Set Top 8 friends.
    """
    if len(friend_ids) > 8:
        return ServiceResult(success=False, error="Max 8 users", status=400)
        
    db = get_db()
    
    try:
        # Clear existing
        db.execute(
            "UPDATE friends SET top8_position = NULL WHERE follower_id = ?",
            (user_id,)
        )
        
        # Set new
        for idx, fid in enumerate(friend_ids, start=1):
            db.execute(
                """UPDATE friends 
                   SET top8_position = ? 
                   WHERE follower_id = ? AND following_id = ?""",
                (idx, user_id, fid)
            )
        db.commit()
    except Exception as e:
         return ServiceResult(success=False, error=str(e), status=500)
         
    return ServiceResult(success=True)
