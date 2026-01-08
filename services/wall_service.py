"""
Wall Service - Business logic for wall post operations.
Extracted from mutations/wall.py for testability.
"""

import json
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from db import get_db


# =============================================
# CONSTANTS
# =============================================

ALLOWED_TYPES = {'text', 'image', 'link', 'script', 'audio', 'voice_note'}


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
# WALL POST OPERATIONS
# =============================================

def get_posts_for_profile(profile_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all wall posts for a profile, ordered by display_order.
    
    Args:
        profile_id: Profile ID to fetch posts for
    
    Returns:
        List of post dictionaries with parsed JSON payloads
    """
    db = get_db()
    rows = db.execute(
        """SELECT id, module_type, content_payload, style_payload, display_order, created_at
           FROM profile_posts
           WHERE profile_id = ?
           ORDER BY display_order ASC, created_at DESC""",
        (profile_id,)
    ).fetchall()
    
    posts = []
    for r in rows:
        post = dict(r)
        try:
            post["content"] = json.loads(post["content_payload"])
        except Exception:
            post["content"] = {}
            
        try:
            post["style"] = json.loads(post["style_payload"]) if post["style_payload"] else {}
        except Exception:
            post["style"] = {}
            
        del post["content_payload"]
        del post["style_payload"]
        
        posts.append(post)
        
    return posts


def add_post(
    user_id: int, 
    module_type: str, 
    content: Dict[str, Any], 
    style: Dict[str, Any],
    display_order: int = 0
) -> ServiceResult:
    """
    Add a new wall post.
    
    Args:
        user_id: Owner's user ID
        module_type: Post type (text, image, link, script, audio)
        content: Content payload dictionary
        style: Style payload dictionary
        display_order: Position in wall
    
    Returns:
        ServiceResult with new post ID on success
    """
    if module_type not in ALLOWED_TYPES:
        return ServiceResult(success=False, error=f"Invalid type. Allowed: {ALLOWED_TYPES}", status=400)
    
    db = get_db()
    
    # Verify profile exists for user
    profile = db.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    if not profile:
        return ServiceResult(success=False, error="Profile not found", status=404)
        
    profile_id = profile["id"]
    
    try:
        content_json = json.dumps(content)
        style_json = json.dumps(style)
    except:
        return ServiceResult(success=False, error="Invalid JSON content/style", status=400)
        
    cursor = db.execute(
        """INSERT INTO profile_posts (profile_id, module_type, content_payload, style_payload, display_order)
           VALUES (?, ?, ?, ?, ?)""",
        (profile_id, module_type, content_json, style_json, display_order)
    )
    new_id = cursor.lastrowid
    db.commit()
    
    return ServiceResult(success=True, data={"id": new_id})


def update_post(
    user_id: int,
    post_id: int,
    content: Optional[Dict[str, Any]] = None,
    style: Optional[Dict[str, Any]] = None,
    module_type: Optional[str] = None
) -> ServiceResult:
    """
    Update an existing wall post.
    
    Args:
        user_id: Owner's user ID (for ownership check)
        post_id: Post ID to update
        content: Optional new content payload
        style: Optional new style payload
        module_type: Optional new module type
    
    Returns:
        ServiceResult indicating success
    """
    db = get_db()
    
    # Ownership check
    row = db.execute(
        """SELECT p.id FROM profile_posts p
           JOIN profiles pr ON p.profile_id = pr.id
           WHERE p.id = ? AND pr.user_id = ?""",
        (post_id, user_id)
    ).fetchone()
    
    if not row:
        return ServiceResult(success=False, error="Post not found or not owned", status=403)
        
    updates = []
    values = []
    
    if content is not None:
        updates.append("content_payload = ?")
        values.append(json.dumps(content))
        
    if style is not None:
        updates.append("style_payload = ?")
        values.append(json.dumps(style))
        
    if module_type is not None:
        if module_type in ALLOWED_TYPES:
            updates.append("module_type = ?")
            values.append(module_type)
            
    if not updates:
        return ServiceResult(success=True)
        
    values.append(post_id)
    sql = f"UPDATE profile_posts SET {', '.join(updates)}, updated_at = datetime('now') WHERE id = ?"
    
    db.execute(sql, values)
    db.commit()
    
    return ServiceResult(success=True)


def delete_post(user_id: int, post_id: int) -> ServiceResult:
    """
    Delete a wall post.
    
    Args:
        user_id: Owner's user ID (for ownership check)
        post_id: Post ID to delete
    
    Returns:
        ServiceResult indicating success
    """
    db = get_db()
    
    db.execute(
        """DELETE FROM profile_posts 
           WHERE id = ? AND profile_id IN (SELECT id FROM profiles WHERE user_id = ?)""",
        (post_id, user_id)
    )
    db.commit()
    return ServiceResult(success=True)


def reorder_posts(user_id: int, order: List[int]) -> ServiceResult:
    """
    Reorder wall posts.
    
    Args:
        user_id: Owner's user ID
        order: List of post IDs in new order
    
    Returns:
        ServiceResult indicating success
    """
    if not order:
        return ServiceResult(success=True)
        
    db = get_db()
    
    # Get profile id
    profile = db.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    if not profile:
        return ServiceResult(success=False, error="No profile", status=404)
    pid = profile["id"]
    
    for idx, post_id in enumerate(order):
        db.execute(
            "UPDATE profile_posts SET display_order = ? WHERE id = ? AND profile_id = ?",
            (idx, post_id, pid)
        )
        
    db.commit()
    return ServiceResult(success=True)
