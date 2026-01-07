
import json
import uuid
from flask import request, jsonify, g
from db import get_db

# Validator helpers
ALLOWED_TYPES = {'text', 'image', 'link', 'script', 'audio'}

def get_wall_posts(profile_id):
    """
    Fetch all wall posts for a profile, ordered by display_order.
    Returns list of dicts with parsed JSON payloads.
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
        # Parse JSON fields safe
        try:
            post["content"] = json.loads(post["content_payload"])
        except:
            post["content"] = {}
            
        try:
            post["style"] = json.loads(post["style_payload"]) if post["style_payload"] else {}
        except:
            post["style"] = {}
            
        # Remove raw strings to clean up response
        del post["content_payload"]
        del post["style_payload"]
        
        posts.append(post)
        
    return posts

def add_wall_post():
    if g.user is None:
        return jsonify(error="Auth required"), 401
        
    data = request.get_json()
    module_type = data.get("module_type")
    content = data.get("content", {})
    style = data.get("style", {})
    
    if module_type not in ALLOWED_TYPES:
        return jsonify(error=f"Invalid type. {ALLOWED_TYPES}"), 400
        
    display_order = data.get("display_order", 0)
    
    db = get_db()
    user_id = g.user["id"]
    
    # Verify profile exists for user
    profile = db.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    if not profile:
        return jsonify(error="Profile not found"), 404
        
    profile_id = profile["id"]
    
    try:
        content_json = json.dumps(content)
        style_json = json.dumps(style)
    except:
        return jsonify(error="Invalid JSON content/style"), 400
        
    # Insert
    cursor = db.execute(
        """INSERT INTO profile_posts (profile_id, module_type, content_payload, style_payload, display_order)
           VALUES (?, ?, ?, ?, ?)""",
        (profile_id, module_type, content_json, style_json, display_order)
    )
    new_id = cursor.lastrowid
    db.commit()
    
    return jsonify(ok=True, id=new_id)

def update_wall_post():
    if g.user is None: return jsonify(error="Auth required"), 401
    data = request.get_json()
    post_id = data.get("id")
    if not post_id: return jsonify(error="ID required"), 400
    
    db = get_db()
    
    # Ownership check
    # Join profiles to check user_id
    row = db.execute(
        """SELECT p.id FROM profile_posts p
           JOIN profiles pr ON p.profile_id = pr.id
           WHERE p.id = ? AND pr.user_id = ?""",
        (post_id, g.user["id"])
    ).fetchone()
    
    if not row:
        return jsonify(error="Post not found or owned"), 403
        
    updates = []
    values = []
    
    if "content" in data:
        updates.append("content_payload = ?")
        values.append(json.dumps(data["content"]))
        
    if "style" in data:
        updates.append("style_payload = ?")
        values.append(json.dumps(data["style"]))
        
    if "module_type" in data:
        if data["module_type"] in ALLOWED_TYPES:
            updates.append("module_type = ?")
            values.append(data["module_type"])
            
    if not updates:
        return jsonify(ok=True)
        
    values.append(post_id)
    sql = f"UPDATE profile_posts SET {', '.join(updates)}, updated_at = datetime('now') WHERE id = ?"
    
    db.execute(sql, values)
    db.commit()
    
    return jsonify(ok=True)

def delete_wall_post():
    if g.user is None: return jsonify(error="Auth required"), 401
    data = request.get_json()
    post_id = data.get("id")
    
    db = get_db()
    # Owner check + Delete
    db.execute(
        """DELETE FROM profile_posts 
           WHERE id = ? AND profile_id IN (SELECT id FROM profiles WHERE user_id = ?)""",
        (post_id, g.user["id"])
    )
    db.commit()
    return jsonify(ok=True)

def reorder_wall_posts():
    """
    Accepts { "order": [id1, id2, id3] }
    Updates display_order for each.
    """
    if g.user is None: return jsonify(error="Auth required"), 401
    data = request.get_json()
    order_ids = data.get("order", [])
    
    if not order_ids:
        return jsonify(ok=True)
        
    db = get_db()
    user_id = g.user["id"]
    
    # Get profile id
    profile = db.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    if not profile: return jsonify(error="No profile"), 404
    pid = profile["id"]
    
    # Verify all IDs belong to this profile to prevent tampering
    # Actually just update with WHERE profile_id = ? constraint
    
    for idx, post_id in enumerate(order_ids):
        db.execute(
            "UPDATE profile_posts SET display_order = ? WHERE id = ? AND profile_id = ?",
            (idx, post_id, pid)
        )
        
    db.commit()
    return jsonify(ok=True)
