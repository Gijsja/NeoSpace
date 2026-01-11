"""
Wall mutations for profile posts.
Delegates to wall_service.
"""

from flask import request, jsonify, g
from core.security import limiter

def get_wall_posts(profile_id, limit=20, offset=0):
    """
    Fetch wall posts for a profile, ordered by display_order.
    Delegates to wall_service.
    """
    from services import wall_service
    return wall_service.get_posts_for_profile(profile_id, limit, offset)

@limiter.limit("10/minute")
def add_wall_post():
    if g.user is None:
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import AddWallPostRequest
        req = msgspec.json.decode(request.get_data(), type=AddWallPostRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import wall_service
    result = wall_service.add_post(
        g.user["id"], 
        req.module_type, 
        req.content, 
        req.style, 
        req.display_order
    )
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(ok=True, **result.data)


def update_wall_post():
    if g.user is None: 
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import UpdateWallPostRequest
        req = msgspec.json.decode(request.get_data(), type=UpdateWallPostRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import wall_service
    result = wall_service.update_post(
        g.user["id"],
        req.id,
        req.content,
        req.style,
        req.module_type
    )
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(ok=True)


def delete_wall_post():
    if g.user is None: 
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import DeleteWallPostRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteWallPostRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import wall_service
    result = wall_service.delete_post(g.user["id"], req.id)
    return jsonify(ok=True)


def reorder_wall_posts():
    """Reorder wall posts."""
    if g.user is None: 
        return jsonify(error="Auth required"), 401
    
    try:
        import msgspec
        from core.schemas import ReorderWallPostsRequest
        req = msgspec.json.decode(request.get_data(), type=ReorderWallPostsRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import wall_service
    result = wall_service.reorder_posts(g.user["id"], req.order)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(ok=True)

