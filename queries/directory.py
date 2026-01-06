"""
User directory queries for Sprint 6.
Provides secure, paginated user listing with privacy controls.
"""

from flask import request, g, jsonify
from db import get_db


def list_users():
    """
    List public user profiles for directory.
    
    Query params:
        cursor: str - Pagination cursor (encoded user ID)
        limit: int - Max results (default 20, max 50)
        search: str - Optional search term for display_name/username
    
    Returns:
        JSON with users list and next_cursor
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    # Parse pagination params
    cursor = request.args.get("cursor", "0")
    try:
        cursor_id = int(cursor) if cursor else 0
    except ValueError:
        cursor_id = 0
    
    limit = min(request.args.get("limit", 20, type=int), 50)
    search = request.args.get("search", "").strip()
    
    db = get_db()
    
    # Build query - only public profiles
    if search:
        # Search by username or display_name (case-insensitive)
        query = """
            SELECT 
                u.id,
                u.username,
                p.display_name,
                p.avatar_path,
                p.theme_preset,
                p.show_online_status
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            WHERE (p.is_public = 1 OR p.is_public IS NULL)
              AND u.id > ?
              AND (u.username LIKE ? OR p.display_name LIKE ?)
            ORDER BY u.id
            LIMIT ?
        """
        search_pattern = f"%{search}%"
        rows = db.execute(query, (cursor_id, search_pattern, search_pattern, limit)).fetchall()
    else:
        query = """
            SELECT 
                u.id,
                u.username,
                p.display_name,
                p.avatar_path,
                p.theme_preset,
                p.show_online_status
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            WHERE (p.is_public = 1 OR p.is_public IS NULL)
              AND u.id > ?
            ORDER BY u.id
            LIMIT ?
        """
        rows = db.execute(query, (cursor_id, limit)).fetchall()
    
    users = []
    for row in rows:
        users.append({
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"] or row["username"],
            "avatar_path": row["avatar_path"],
            "theme_preset": row["theme_preset"] or "default"
            # Note: NOT exposing show_online_status value, just using it server-side
        })
    
    # Compute next cursor
    next_cursor = str(rows[-1]["id"]) if rows and len(rows) == limit else None
    
    return jsonify(
        users=users,
        next_cursor=next_cursor,
        total_shown=len(users)
    )


def get_user_by_username():
    """
    Look up a single user by username.
    
    Query params:
        username: str - Exact username to find
    
    Returns:
        Basic user info if found and public
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify(error="username parameter required"), 400
    
    db = get_db()
    
    row = db.execute(
        """SELECT 
            u.id,
            u.username,
            p.display_name,
            p.avatar_path,
            p.bio,
            p.status_message,
            p.status_emoji,
            p.now_activity,
            p.now_activity_type,
            p.voice_intro_path,
            p.anthem_url,
            p.is_public
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.username = ?""",
        (username,)
    ).fetchone()
    
    if not row:
        return jsonify(error="User not found"), 404
    
    is_public = row["is_public"] if row["is_public"] is not None else True
    is_own = g.user["id"] == row["id"]
    
    if not is_public and not is_own:
        return jsonify(error="User profile is private"), 403
    
    return jsonify(
        id=row["id"],
        username=row["username"],
        display_name=row["display_name"] or row["username"],
        avatar_path=row["avatar_path"],
        bio=row["bio"] or "",
        status_message=row["status_message"],
        status_emoji=row["status_emoji"],
        now_activity=row["now_activity"],
        now_activity_type=row["now_activity_type"],
        voice_intro_path=row["voice_intro_path"],
        anthem_url=row["anthem_url"]
    )
