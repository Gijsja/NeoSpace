"""
Sprint #16: Feed API Queries

Fetch time-ordered feed of posts from followed users.
"""

from db import get_db
import json


def get_feed(user_id: int, limit: int = 20, before_id: int = None) -> list:
    """
    Get feed of posts from everyone the user follows.
    
    Args:
        user_id: Current user ID
        limit: Max posts to return
        before_id: Pagination cursor (post_id)
        
    Returns:
        List of dicts mixed with post content + author profile info
    """
    db = get_db()
    
    query = """
        SELECT 
            post.id, post.module_type, post.content_payload, post.style_payload, 
            post.created_at, post.profile_id,
            p.display_name as author_name, p.avatar_path as author_avatar, 
            u.username as author_username, u.id as author_user_id
        FROM profile_posts post
        JOIN profiles p ON post.profile_id = p.id
        JOIN users u ON p.user_id = u.id
        JOIN friends f ON f.following_id = u.id
        WHERE f.follower_id = ?
    """
    params = [user_id]
    
    if before_id:
        query += " AND post.id < ?"
        params.append(before_id)
        
    query += " ORDER BY post.created_at DESC LIMIT ?"
    params.append(limit)
    
    rows = db.execute(query, params).fetchall()
    
    posts = []
    for row in rows:
        r = dict(row)
        # Parse JSON payloads
        try:
            r["content"] = json.loads(r["content_payload"]) if r["content_payload"] else {}
        except Exception:
            r["content"] = {}
            
        try:
            r["style"] = json.loads(r["style_payload"]) if r["style_payload"] else {}
        except Exception:
            r["style"] = {}
            
        # Cleanup raw JSON fields
        del r["content_payload"]
        del r["style_payload"]
        
        posts.append(r)
        
    return posts
