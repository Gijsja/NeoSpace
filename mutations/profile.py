"""
Profile mutations for Sprint 6.
Handles profile creation, updates, and avatar uploads.
"""

import re
import os
import json
import uuid
import random
from flask import request, jsonify, g, current_app
from werkzeug.utils import secure_filename
from db import get_db
import html

# Validation constants
ALLOWED_THEMES = {"default", "dark", "retro", "cyber", "zen"}
ALLOWED_DM_POLICIES = {"everyone", "mutuals", "nobody"}
HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_DISPLAY_NAME_LENGTH = 50
MAX_BIO_LENGTH = 500


def validate_hex_color(color: str) -> str:
    """Validate and normalize hex color."""
    if not color:
        return "#3b82f6"  # Default accent
    if not HEX_COLOR_PATTERN.match(color):
        raise ValueError("Invalid color format. Use #RRGGBB")
    return color.upper()


def sanitize_display_name(name: str) -> str:
    """Remove control characters from display name."""
    if not name:
        return ""
    # Remove control chars and normalize whitespace
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name)
    return cleaned.strip()[:MAX_DISPLAY_NAME_LENGTH]


def sanitize_bio(bio: str) -> str:
    """Sanitize bio content, escaping HTML."""
    if not bio:
        return ""
    return html.escape(bio.strip()[:MAX_BIO_LENGTH])


def get_profile():
    """
    Get a user's profile.
    
    URL param: user_id (int)
    
    Returns:
        Profile data if public or own profile, 403 if private.
    """
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        if g.user:
            user_id = g.user["id"]
        else:
            return jsonify(error="user_id required"), 400
    
    db = get_db()
    
    # Get user and profile
    row = db.execute(
        """SELECT 
            u.id, u.username, u.created_at as member_since,
            p.id as profile_id, p.display_name, p.bio, p.avatar_path,
            p.theme_preset, p.accent_color,
            p.status_message, p.status_emoji,
            p.now_activity, p.now_activity_type,
            p.voice_intro_path, p.voice_waveform_json,
            p.anthem_url, p.anthem_autoplay,
            p.is_public, p.show_online_status, p.dm_policy
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.id = ?""",
        (user_id,)
    ).fetchone()
    
    if not row:
        return jsonify(error="User not found"), 404
    
    # Check privacy
    is_own = g.user and g.user["id"] == user_id
    is_public = row["is_public"] if row["is_public"] is not None else True
    
    if not is_public and not is_own:
        return jsonify(error="Profile is private"), 403
    
    # Get stickers
    stickers = []
    if row["profile_id"]:
        sticker_rows = db.execute(
            """SELECT s.id, s.sticker_type, s.image_path, s.x_pos, s.y_pos, s.rotation, s.scale, s.z_index, 
                      s.placed_by, u.username as placed_by_username
               FROM profile_stickers s
               LEFT JOIN users u ON s.placed_by = u.id
               WHERE s.profile_id = ?""",
            (row["profile_id"],)
        ).fetchall()
        stickers = [dict(r) for r in sticker_rows]
    
    # Get pinned scripts
    pinned_scripts = []
    if row["profile_id"]:
        script_rows = db.execute(
            """SELECT s.id, s.title, s.script_type, s.updated_at,
                      ps.display_order
               FROM profile_scripts ps
               JOIN scripts s ON ps.script_id = s.id
               WHERE ps.profile_id = ?
               ORDER BY ps.display_order ASC""",
            (row["profile_id"],)
        ).fetchall()
        pinned_scripts = [dict(r) for r in script_rows]
    
    return jsonify(
        user_id=row["id"],
        username=row["username"],
        display_name=row["display_name"] or row["username"],
        bio=row["bio"] or "",
        avatar_path=row["avatar_path"],
        theme_preset=row["theme_preset"] or "default",
        accent_color=row["accent_color"] or "#3b82f6",
        status_message=row["status_message"] or "",
        status_emoji=row["status_emoji"] or "",
        now_activity=row["now_activity"] or "",
        now_activity_type=row["now_activity_type"] or "thinking",
        member_since=row["member_since"],
        is_own=is_own,
        dm_policy=row["dm_policy"] if is_own else None,
        show_online_status=bool(row["show_online_status"]) if row["show_online_status"] is not None else True,
        voice_intro_path=row["voice_intro_path"],
        voice_waveform_json=row["voice_waveform_json"],
        anthem_url=row["anthem_url"] or "",
        anthem_autoplay=bool(row["anthem_autoplay"]) if row["anthem_autoplay"] is not None else True,
        stickers=stickers,
        pinned_scripts=pinned_scripts,
        viewer_id=g.user["id"] if g.user else None
    )



def update_profile():
    """
    Update the current user's profile.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    data = request.get_json()
    user_id = g.user["id"]
    db = get_db()
    
    # Validate and sanitize inputs
    updates = {}
    
    if "display_name" in data:
        updates["display_name"] = sanitize_display_name(data["display_name"])
    
    if "bio" in data:
        updates["bio"] = sanitize_bio(data["bio"])
    
    # Hero Identity & Now Fields
    if "status_message" in data:
        updates["status_message"] = html.escape(data["status_message"].strip()[:100]) # 100 char limit
    
    if "status_emoji" in data:
        updates["status_emoji"] = data["status_emoji"][:4] # Max 4 chars (1-2 emojis)
    
    if "now_activity" in data:
        updates["now_activity"] = html.escape(data["now_activity"].strip()[:50]) # 50 char limit for "Now"
        
    if "now_activity_type" in data:
        updates["now_activity_type"] = data["now_activity_type"]
    
    if "theme_preset" in data:
        theme = data["theme_preset"]
        if theme not in ALLOWED_THEMES:
            return jsonify(error=f"Invalid theme. Choose from: {ALLOWED_THEMES}"), 400
        updates["theme_preset"] = theme
    
    if "accent_color" in data:
        try:
            updates["accent_color"] = validate_hex_color(data["accent_color"])
        except ValueError as e:
            return jsonify(error=str(e)), 400
    
    if "is_public" in data:
        updates["is_public"] = 1 if data["is_public"] else 0
    
    if "show_online_status" in data:
        updates["show_online_status"] = 1 if data["show_online_status"] else 0
    
    if "dm_policy" in data:
        policy = data["dm_policy"]
        if policy not in ALLOWED_DM_POLICIES:
            return jsonify(error=f"Invalid DM policy. Choose from: {ALLOWED_DM_POLICIES}"), 400
        updates["dm_policy"] = policy
    
    # Sprint 11: Audio Anthem
    if "anthem_url" in data:
        url = data["anthem_url"].strip() if data["anthem_url"] else ""
        # Basic URL validation (allow empty to clear)
        if url and not (url.startswith("http://") or url.startswith("https://")):
            return jsonify(error="Anthem URL must be http:// or https://"), 400
        updates["anthem_url"] = url[:500]  # Limit length
    
    if "anthem_autoplay" in data:
        updates["anthem_autoplay"] = 1 if data["anthem_autoplay"] else 0
    
    if not updates:
        return jsonify(error="No valid fields to update"), 400
    
    # Check if profile exists
    existing = db.execute(
        "SELECT id FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    
    updates["updated_at"] = "datetime('now')"
    
    if existing:
        # Update existing profile
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys() if k != "updated_at")
        set_clause += ", updated_at = datetime('now')"
        values = [v for k, v in updates.items() if k != "updated_at"]
        values.append(user_id)
        
        db.execute(
            f"UPDATE profiles SET {set_clause} WHERE user_id = ?",
            values
        )
    else:
        # Create new profile
        updates["user_id"] = user_id
        columns = ", ".join(updates.keys())
        placeholders = ", ".join("?" if k != "updated_at" else "datetime('now')" for k in updates.keys())
        values = [v for k, v in updates.items() if k != "updated_at"]
        
        db.execute(
            f"INSERT INTO profiles ({columns}) VALUES ({placeholders})",
            values
        )
    
    db.commit()
    return jsonify(ok=True)


def upload_avatar():
    """
    Upload a new avatar image.
    
    Request: multipart/form-data with 'avatar' file
    
    Returns:
        JSON with avatar_path on success
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    if 'avatar' not in request.files:
        return jsonify(error="No avatar file provided"), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify(error="No file selected"), 400
    
    # Validate extension
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        return jsonify(error=f"Invalid file type. Allowed: {ALLOWED_AVATAR_EXTENSIONS}"), 400
    
    # Read file and compute checksum
    file_data = file.read()
    if len(file_data) > 2 * 1024 * 1024:  # 2MB limit
        return jsonify(error="File too large (max 2MB)"), 400
    
    checksum = hashlib.sha256(file_data).hexdigest()
    
    # Generate unique filename
    user_id = g.user["id"]
    filename = f"avatar_{user_id}_{checksum[:16]}.{ext}"
    
    # Save to avatars directory
    avatar_dir = os.path.join(current_app.root_path, 'static/avatars')
    os.makedirs(avatar_dir, exist_ok=True)
    
    filepath = os.path.join(avatar_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(file_data)
    
    # Update profile
    avatar_path = f"/static/avatars/{filename}"
    db = get_db()
    
    existing = db.execute(
        "SELECT id FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    
    if existing:
        db.execute(
            "UPDATE profiles SET avatar_path = ?, avatar_checksum = ?, updated_at = datetime('now') WHERE user_id = ?",
            (avatar_path, checksum, user_id)
        )
    else:
        db.execute(
            "INSERT INTO profiles (user_id, avatar_path, avatar_checksum) VALUES (?, ?, ?)",
            (user_id, avatar_path, checksum)
        )
    
    db.commit()
    
    return jsonify(ok=True, avatar_path=avatar_path)


def upload_voice_intro():
    """
    Upload a voice intro (audio/webm).
    Expects multipart/form-data:
      - voice: Blob/File
      - waveform: JSON string of peaks (optional, or we generate placeholder)
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
        
    if 'voice' not in request.files:
        return jsonify(error="No audio file"), 400
        
    file = request.files['voice']
    waveform_json = request.form.get('waveform', '[]')
    
    # Save file
    user_id = g.user["id"]
    filename = f"voice_{user_id}.webm" # Single file per user, overwrite
    
    voice_dir = os.path.join(current_app.root_path, 'static/voice_intros')
    os.makedirs(voice_dir, exist_ok=True)
    
    filepath = os.path.join(voice_dir, filename)
    file.save(filepath)
    
    path_url = f"/static/voice_intros/{filename}"
    
    # Update DB
    db = get_db()
    existing = db.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    
    if existing:
        db.execute(
            """UPDATE profiles 
               SET voice_intro_path = ?, voice_waveform_json = ?, updated_at = datetime('now') 
               WHERE user_id = ?""",
            (path_url, waveform_json, user_id)
        )
        db.commit()
        return jsonify(ok=True, voice_path=path_url)
    
    return jsonify(error="Profile not found"), 404


def create_default_profile(user_id: int, username: str):
    """
    Create a default profile for a new user.
    Called from auth.py after registration.
    """
    db = get_db()
    db.execute(
        """INSERT INTO profiles (user_id, display_name) 
           VALUES (?, ?)""",
        (user_id, username)
    )
    db.commit()


# =============================================
# STICKER MUTATIONS
# =============================================

def add_sticker():
    """Add a sticker to a user's profile (Guestbook or Image Collage)."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    # Handle both JSON and FormData
    if request.content_type.startswith('multipart/form-data'):
        # Image Upload
        sticker_type = 'image'
        target_user_id = request.form.get("target_user_id")
        x = request.form.get("x", 0)
        y = request.form.get("y", 0)
        
        file = request.files.get('image')
        if not file:
            return jsonify(error="No image file provided"), 400
            
        # Validate Image
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
             return jsonify(error="Invalid file type"), 400
             
        # Save Image
        filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        upload_dir = os.path.join(current_app.root_path, 'static/uploads/stickers')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Security check: ensure target user exists (implicitly checked by db insert constraint but safer to check profile)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        image_path = f"/static/uploads/stickers/{filename}"
        
    else:
        # Standard Emoji Sticker
        data = request.get_json()
        sticker_type = data.get("sticker_type")
        target_user_id = data.get("target_user_id")
        x = data.get("x", 0)
        y = data.get("y", 0)
        image_path = None
        
        if not sticker_type:
            return jsonify(error="sticker_type required"), 400

    # Basic position validation
    try:
        x = float(x)
        y = float(y)
    except (ValueError, TypeError):
        return jsonify(error="Invalid coordinates"), 400
        
    db = get_db()
    
    # Find profile ID of target
    # If target_user_id not provided, assume own profile (or fail?)
    # Usually we want to post on SOMEONE's wall.
    if not target_user_id:
         target_user_id = g.user["id"]
         
    profile = db.execute("SELECT id FROM profiles WHERE user_id = ?", (target_user_id,)).fetchone()
    if not profile:
        return jsonify(error="Target profile not found"), 404
        
    # Create Sticker
    # Generate UUID for ID
    sid = str(uuid.uuid4())
    
    # Random default rotation
    rotation = float(data.get("rotation", 0)) if request.is_json else random.uniform(-10, 10)
    
    db.execute(
        """INSERT INTO profile_stickers (
            id, profile_id, sticker_type, image_path, x_pos, y_pos, rotation, placed_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, profile['id'], sticker_type, image_path, x, y, rotation, g.user['id'])
    )
    db.commit()
    
    # Get username for response
    # We return the new sticker object so frontend can update the temp one
    return jsonify(
        ok=True, 
        id=sid, 
        placed_by_username=g.user['username'],
        image_path=image_path
    )


def update_sticker():
    """Update sticker position/rotation/scale."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
        
    data = request.get_json()
    sticker_id = data.get("id")
    
    if not sticker_id:
        return jsonify(error="sticker id required"), 400
        
    db = get_db()
    user_id = g.user["id"]
    
    # Verify ownership
    row = db.execute(
        """SELECT s.id 
           FROM profile_stickers s
           JOIN profiles p ON s.profile_id = p.id
           WHERE s.id = ? AND p.user_id = ?""",
        (sticker_id, user_id)
    ).fetchone()
    
    if not row:
        return jsonify(error="Sticker not found or not owned"), 404
        
    updates = {}
    if "x" in data: updates["x_pos"] = float(data["x"])
    if "y" in data: updates["y_pos"] = float(data["y"])
    if "rotation" in data: updates["rotation"] = float(data["rotation"])
    if "scale" in data: updates["scale"] = float(data["scale"])
    if "z_index" in data: updates["z_index"] = int(data["z_index"])
    
    if not updates:
        return jsonify(ok=True) # Nothing to do
        
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values())
    values.append(sticker_id)
    
    db.execute(f"UPDATE profile_stickers SET {set_clause} WHERE id = ?", values)
    db.commit()
    
    return jsonify(ok=True)


def remove_sticker():
    """Remove a sticker."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
        
    data = request.get_json()
    sticker_id = data.get("id")
    
    if not sticker_id:
        return jsonify(error="sticker id required"), 400
        
    db = get_db()
    user_id = g.user["id"]
    
    # Verify ownership (Profile Owner OR Sticker Placer)
    # Subquery based deletion
    result = db.execute(
        """DELETE FROM profile_stickers 
           WHERE id = ? AND (
                profile_id IN (SELECT id FROM profiles WHERE user_id = ?) 
                OR placed_by = ?
           )""",
        (sticker_id, user_id, user_id)
    )
    db.commit()
    
    if result.rowcount == 0:
        return jsonify(error="Sticker not found or not owned"), 404
        
    return jsonify(ok=True)
