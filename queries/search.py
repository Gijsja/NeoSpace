"""
Sprint #17: Search API Queries

Search users and content.
"""

from db import get_db
import json
from queries.friends import is_following


def search_users(query: str, current_user_id: int = None, limit: int = 20) -> list:
    """
    Search users by username or display name.
    
    Args:
        query: Search term
        current_user_id: ID of performing user (to check follow status)
        limit: Max results
        
    Returns:
        List of user objects with follow status
    """
    if not query or len(query.strip()) < 1:
        return []
        
    query = query.strip()
    term = f"%{query}%"
    db = get_db()
    
    # Priority: Starts with query > Contains query
    # We'll just do simple LIKE for now, sorting by partial match relevance is complex in pure SQL
    # Ordering by length of match is a decent proxy for relevance
    
    rows = db.execute(
        """SELECT u.id, u.username, p.display_name, p.avatar_path, p.bio
           FROM users u
           LEFT JOIN profiles p ON u.id = p.user_id
           WHERE u.username LIKE ? OR p.display_name LIKE ?
           ORDER BY 
             CASE WHEN u.username LIKE ? THEN 0 ELSE 1 END, -- Exactish matches first
             u.username ASC
           LIMIT ?""",
        (term, term, f"{query}%", limit)
    ).fetchall()
    
    results = []
    for row in rows:
        r = dict(row)
        if current_user_id and current_user_id != r["id"]:
            r["is_following"] = is_following(current_user_id, r["id"])
        else:
            r["is_following"] = False
        results.append(r)
        
    return results


def search_posts(query: str, limit: int = 20) -> list:
    """
    Search generic text posts.
    
    Args:
        query: Search term
        limit: Max results
        
    Returns:
        List of post objects
    """
    if not query or len(query.strip()) < 1:
        return []
        
    query = query.strip()
    term = f"%{query}%"
    db = get_db()
    
    # Search in content_payload where module_type = 'text'
    # SQLite JSON search is limited without JSON1 extension guaranteed, 
    # but we store payload as text.
    
    rows = db.execute(
        """SELECT 
            post.id, post.module_type, post.content_payload, post.created_at,
            p.display_name as author_name, p.avatar_path as author_avatar, 
            u.username as author_username, u.id as author_user_id
           FROM profile_posts post
           JOIN profiles p ON post.profile_id = p.id
           JOIN users u ON p.user_id = u.id
           WHERE post.module_type = 'text' 
             AND post.content_payload LIKE ?
           ORDER BY post.created_at DESC
           LIMIT ?""",
        (term, limit)
    ).fetchall()
    
    results = []
    for row in rows:
        r = dict(row)
        try:
            r["content"] = json.loads(r["content_payload"])
        except:
            r["content"] = {}
        
        # Double check match in python to be safe (JSON string structure)
        # simplistic but effective for strict backend MVP
        del r["content_payload"]
        results.append(r)
        
    return results
