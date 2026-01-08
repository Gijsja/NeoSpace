"""
Sprint #14: Social Graph — Friend Mutations

CRUD operations for follow/unfollow and Top 8 management.
"""

from flask import g, jsonify, request
from db import get_db


from security import limiter

@limiter.limit("20/minute")
def follow():
    """Follow a user."""
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from msgspec_models import FollowRequest
        req = msgspec.json.decode(request.get_data(), type=FollowRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    target_user_id = req.user_id
    
    if target_user_id == g.user["id"]:
        return jsonify(error="Cannot follow yourself"), 400
    
    db = get_db()
    
    # Check target exists
    target = db.execute("SELECT id FROM users WHERE id = ?", (target_user_id,)).fetchone()
    if not target:
        return jsonify(error="User not found"), 404
    
    # Check if already following
    existing = db.execute(
        "SELECT id FROM friends WHERE follower_id = ? AND following_id = ?",
        (g.user["id"], target_user_id)
    ).fetchone()
    
    if existing:
        return jsonify(ok=True, already_following=True)
    
    # Insert follow
    try:
        db.execute(
            "INSERT INTO friends (follower_id, following_id) VALUES (?, ?)",
            (g.user["id"], target_user_id)
        )
        db.commit()
        
        # Sprint 15: Create notification for followed user
        from mutations.notifications import create_notification
        create_notification(
            user_id=target_user_id,
            notif_type="follow",
            title=f"{g.user['username']} started following you",
            link=f"/wall?user_id={g.user['id']}",
            actor_id=g.user["id"]
        )
    except Exception as e:
        return jsonify(error=str(e)), 500
    
    return jsonify(ok=True)


def unfollow():
    """Unfollow a user."""
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from msgspec_models import UnfollowRequest
        req = msgspec.json.decode(request.get_data(), type=UnfollowRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    target_user_id = req.user_id
    
    db = get_db()
    db.execute(
        "DELETE FROM friends WHERE follower_id = ? AND following_id = ?",
        (g.user["id"], target_user_id)
    )
    db.commit()
    
    return jsonify(ok=True)


def set_top8():
    """
    Set Top 8 order.
    Expects: { "order": [user_id_1, user_id_2, ...] }
    Max 8 users.
    """
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from msgspec_models import UpdateTop8Request
        req = msgspec.json.decode(request.get_data(), type=UpdateTop8Request)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    order = req.friend_ids
    
    if len(order) > 8:
        return jsonify(error="Max 8 users"), 400
    
    db = get_db()
    my_id = g.user["id"]
    
    # Clear all existing Top 8 positions
    db.execute(
        "UPDATE friends SET top8_position = NULL WHERE follower_id = ?",
        (my_id,)
    )
    
    # Set new positions (only for users we follow)
    for idx, user_id in enumerate(order, start=1):
        db.execute(
            """UPDATE friends 
               SET top8_position = ? 
               WHERE follower_id = ? AND following_id = ?""",
            (idx, my_id, user_id)
        )
    
    db.commit()
    return jsonify(ok=True)
