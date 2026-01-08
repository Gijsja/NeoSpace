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


def user_cards_html():
    """
    Return HTML fragment of user cards for HTMX.
    Uses same query logic as list_users but returns HTML instead of JSON.
    """
    if g.user is None:
        return '<div class="text-red-400">Authentication required</div>', 401
    
    cursor = request.args.get("cursor", "0")
    try:
        cursor_id = int(cursor) if cursor else 0
    except ValueError:
        cursor_id = 0
    
    limit = min(request.args.get("limit", 20, type=int), 50)
    search = request.args.get("search", "").strip()
    
    db = get_db()
    
    if search:
        query = """
            SELECT u.id, u.username, p.display_name, p.avatar_path
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            WHERE (p.is_public = 1 OR p.is_public IS NULL)
              AND u.id > ?
              AND (u.username LIKE ? OR p.display_name LIKE ?)
            ORDER BY u.id LIMIT ?
        """
        search_pattern = f"%{search}%"
        rows = db.execute(query, (cursor_id, search_pattern, search_pattern, limit)).fetchall()
    else:
        query = """
            SELECT u.id, u.username, p.display_name, p.avatar_path
            FROM users u
            LEFT JOIN profiles p ON u.id = p.user_id
            WHERE (p.is_public = 1 OR p.is_public IS NULL)
              AND u.id > ?
            ORDER BY u.id LIMIT ?
        """
        rows = db.execute(query, (cursor_id, limit)).fetchall()
    
    if not rows:
        return '<div class="col-span-full nb-card p-8 text-center font-mono uppercase">No users found.</div>'
    
    html_parts = []
    for row in rows:
        user_id = row["id"]
        username = row["username"]
        display_name = row["display_name"] or username
        avatar_path = row["avatar_path"]
        initial = username[0].upper() if username else "?"
        
        # Avatar HTML - Neubrutalist Square Style
        if avatar_path:
            avatar_html = f'<div class="w-14 h-14 bg-black bg-cover bg-center border-2 border-black shadow-[2px_2px_0_0_#000]" style="background-image: url(\'{avatar_path}\')"></div>'
        else:
            avatar_html = f'<div class="w-14 h-14 bg-black flex items-center justify-center text-xl font-bold text-white border-2 border-black shadow-[2px_2px_0_0_#000]">{initial}</div>'
        
        card_html = f'''
        <div class="bg-white border-2 border-black p-4 shadow-[4px_4px_0_0_#000] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[6px_6px_0_0_#000] transition-all">
            <div class="flex items-start gap-4">
                {avatar_html}
                <div class="flex-1 min-w-0">
                    <h3 class="text-lg font-black text-black uppercase truncate">{display_name}</h3>
                    <p class="text-xs font-mono text-gray-500 mb-3">@{username}</p>
                    <div class="flex items-center gap-2">
                        <a href="/wall?user_id={user_id}" class="px-3 py-1.5 bg-white border-2 border-black text-black font-bold text-xs uppercase hover:bg-acid-green transition-colors shadow-[2px_2px_0_0_#000]">Wall</a>
                        <a href="/ui/views/messages.html?with={user_id}" class="px-3 py-1.5 bg-black border-2 border-black text-white font-bold text-xs uppercase hover:bg-hot-pink transition-colors shadow-[2px_2px_0_0_#000]">DM</a>
                    </div>
                </div>
            </div>
        </div>
        '''
        html_parts.append(card_html)
    
    # Add load more button if there might be more results
    next_cursor = str(rows[-1]["id"]) if len(rows) == limit else ""
    if next_cursor:
        load_more = f'''
        <div class="col-span-full flex justify-center mt-4">
            <button hx-get="/users/cards?cursor={next_cursor}" hx-target="#user-grid" hx-swap="beforeend" 
                    class="px-6 py-3 bg-white border-2 border-black font-black uppercase text-black shadow-[4px_4px_0_0_#000] hover:bg-acid-green transition-colors">
                Load More
            </button>
        </div>
        '''
        html_parts.append(load_more)
    
    return "\n".join(html_parts)

