"""
Profile mutations for Sprint 6.
Handles profile creation, updates, and avatar uploads.
"""

import re
import os
import json
import uuid
import random
import hashlib
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
    from services import profile_service
    
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        if g.user:
            user_id = g.user["id"]
        else:
            return jsonify(error="user_id required"), 400
    
    viewer_id = g.user["id"] if g.user else None
    result = profile_service.get_profile_by_user_id(user_id, viewer_id)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(**result.data)



def update_profile():
    """
    Update the current user's profile.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    from services import profile_service
    
    try:
        import msgspec
        from msgspec_models import UpdateProfileRequest
        req = msgspec.json.decode(request.get_data(), type=UpdateProfileRequest)
        data = msgspec.to_builtins(req)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    result = profile_service.update_profile_fields(g.user["id"], data)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
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
        try:
            import msgspec
            from msgspec_models import AddStickerRequest
            req = msgspec.json.decode(request.get_data(), type=AddStickerRequest)
        except msgspec.ValidationError as e:
            return jsonify(error=f"Invalid request: {e}"), 400
        
        sticker_type = req.sticker_type
        target_user_id = req.target_user_id
        x = req.x
        y = req.y
        image_path = None

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
    
    try:
        import msgspec
        from msgspec_models import UpdateStickerRequest
        req = msgspec.json.decode(request.get_data(), type=UpdateStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    db = get_db()
    user_id = g.user["id"]
    
    # Verify ownership
    row = db.execute(
        """SELECT s.id 
           FROM profile_stickers s
           JOIN profiles p ON s.profile_id = p.id
           WHERE s.id = ? AND p.user_id = ?""",
        (req.id, user_id)
    ).fetchone()
    
    if not row:
        return jsonify(error="Sticker not found or not owned"), 404
        
    updates = {}
    if req.x is not None: updates["x_pos"] = req.x
    if req.y is not None: updates["y_pos"] = req.y
    if req.rotation is not None: updates["rotation"] = req.rotation
    if req.scale is not None: updates["scale"] = req.scale  
    if req.z_index is not None: updates["z_index"] = req.z_index
    
    if not updates:
        return jsonify(ok=True) # Nothing to do
        
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values())
    values.append(req.id)
    
    db.execute(f"UPDATE profile_stickers SET {set_clause} WHERE id = ?", values)
    db.commit()
    
    return jsonify(ok=True)


def remove_sticker():
    """Remove a sticker."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from msgspec_models import RemoveStickerRequest
        req = msgspec.json.decode(request.get_data(), type=RemoveStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
        
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
        (req.id, user_id, user_id)
    )
    db.commit()
    
    if result.rowcount == 0:
        return jsonify(error="Sticker not found or not owned"), 404
        
    return jsonify(ok=True)
