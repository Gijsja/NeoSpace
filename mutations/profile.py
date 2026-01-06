"""
Profile mutations for Sprint 6.
Handles profile creation, updates, and avatar uploads.
"""

import re
import os
import hashlib
from flask import request, g, jsonify, current_app
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
            p.voice_intro_path, p.voice_waveform_json,
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
            """SELECT s.id, s.sticker_type, s.x_pos, s.y_pos, s.rotation, s.scale, s.z_index, 
                      s.placed_by, u.username as placed_by_username
               FROM profile_stickers s
               LEFT JOIN users u ON s.placed_by = u.id
               WHERE s.profile_id = ?""",
            (row["profile_id"],)
        ).fetchall()
        stickers = [dict(r) for r in sticker_rows]
    
    return jsonify(
        user_id=row["id"],
        username=row["username"],
        display_name=row["display_name"] or row["username"],
        bio=row["bio"] or "",
        avatar_path=row["avatar_path"],
        theme_preset=row["theme_preset"] or "default",
        accent_color=row["accent_color"] or "#3b82f6",
        member_since=row["member_since"],
        is_own=is_own,
        dm_policy=row["dm_policy"] if is_own else None,
        show_online_status=bool(row["show_online_status"]) if row["show_online_status"] is not None else True,
        voice_intro_path=row["voice_intro_path"],
        voice_waveform_json=row["voice_waveform_json"],
        stickers=stickers,
        viewer_id=g.user["id"] if g.user else None
    )



def update_profile():
    """
    Update the current user's profile.
    
    Request JSON (all optional):
        display_name: str
        bio: str
        theme_preset: str (one of ALLOWED_THEMES)
        accent_color: str (#RRGGBB)
        is_public: bool
        show_online_status: bool
        dm_policy: str (one of ALLOWED_DM_POLICIES)
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
    """Add a sticker to a user's profile (Guestbook)."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    data = request.get_json()
    sticker_type = data.get("sticker_type")
    target_user_id = data.get("target_user_id") # Operations on other walls
    
    if not sticker_type:
        return jsonify(error="sticker_type required"), 400
        
    # Basic position validation
    try:
        x = float(data.get("x", 0))
        y = float(data.get("y", 0))
    except (ValueError, TypeError):
        return jsonify(error="Invalid coordinates"), 400
        
    db = get_db()
    current_user_id = g.user["id"]
    
    # Determine target profile
    target_uid = target_user_id if target_user_id else current_user_id
    
    # Ensure profile exists and get ID
    profile = db.execute("SELECT id FROM profiles WHERE user_id = ?", (target_uid,)).fetchone()
    if not profile:
        return jsonify(error="Profile not found"), 404
        
    profile_id = profile["id"]
    
    db.execute(
        """INSERT INTO profile_stickers (profile_id, sticker_type, x_pos, y_pos, placed_by)
           VALUES (?, ?, ?, ?, ?)""",
        (profile_id, sticker_type, x, y, current_user_id)
    )
    db.commit()
    
    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    return jsonify(ok=True, id=new_id, placed_by=current_user_id, placed_by_username=g.user["username"])


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
