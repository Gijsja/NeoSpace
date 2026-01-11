"""
Sprint #14: Social Graph — Friend Mutations
Delegates to friends_service.
"""

from flask import g, jsonify, request
from services import friends_service
from core.security import limiter

@limiter.limit("20/minute")
def follow():
    """Follow a user."""
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import FollowRequest
        req = msgspec.json.decode(request.get_data(), type=FollowRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    result = friends_service.follow_user(g.user["id"], req.user_id)
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(ok=True, **(result.data or {}))


@limiter.limit("20/minute")
def unfollow():
    """Unfollow a user."""
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import UnfollowRequest
        req = msgspec.json.decode(request.get_data(), type=UnfollowRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    result = friends_service.unfollow_user(g.user["id"], req.user_id)
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(ok=True)


@limiter.limit("10/minute")
def set_top8():
    """
    Set Top 8 order.
    Expects: { "friend_ids": [user_id_1, user_id_2, ...] }
    """
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import UpdateTop8Request
        req = msgspec.json.decode(request.get_data(), type=UpdateTop8Request)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    result = friends_service.set_top8(g.user["id"], req.friend_ids)
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(ok=True)

