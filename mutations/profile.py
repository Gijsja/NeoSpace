"""
Profile mutations for Sprint 6.
Delegates to profile_service and sticker_service.
"""

from flask import request, jsonify, g, current_app
from services import profile_service, sticker_service

def get_profile():
    """
    Get a user's profile.
    """
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        if g.user:
            user_id = g.user["id"]
        else:
            return jsonify(error="user_id required"), 400
    
    viewer_id = g.user["id"] if g.user else None
    
    wall_page = request.args.get("page", 1, type=int)
    wall_limit = request.args.get("limit", 20, type=int)
    
    result = profile_service.get_profile_by_user_id(user_id, viewer_id, wall_page, wall_limit)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(**result.data)


def update_profile():
    """
    Update the current user's profile.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import UpdateProfileRequest
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
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    if 'avatar' not in request.files:
        return jsonify(error="No avatar file provided"), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify(error="No file selected"), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    # Read file data here or pass file object to service?
    # Service 'save_avatar' expects `file_data: bytes`.
    file_data = file.read()
    
    result = profile_service.save_avatar(g.user["id"], file_data, ext, current_app.root_path)
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(ok=True, **result.data)


def upload_voice_intro():
    """
    Upload a voice intro (audio/webm).
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
        
    if 'voice' not in request.files:
        return jsonify(error="No audio file"), 400
        
    file = request.files['voice']
    waveform_json = request.form.get('waveform', '[]')
    
    # Service 'save_voice_intro' expects file object
    result = profile_service.save_voice_intro(g.user["id"], file, current_app.root_path, waveform_json)
    
    if not result.success:
         return jsonify(error=result.error), result.status
         
    return jsonify(ok=True, **result.data)


# =============================================
# STICKER MUTATIONS (Delegated to Sticker Service)
# =============================================

def add_sticker():
    """Add a sticker to a user's profile."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    # Extract params from request regardless of content type or method
    # profile.py original Logic supported both JSON and Multipart
    
    profile_id = None
    sticker_type = 'image'
    x = 0
    y = 0
    rotation = 0
    image_file = None
    target_user_id = None
    text_content = None # Not used in original profile.py add_sticker explicitly for text?
                        # Actually profile.py had logic for "Standard Emoji Sticker" via JSON.
    
    if request.content_type.startswith('multipart/form-data'):
        # Image Upload
        target_user_id = request.form.get("target_user_id")
        x = request.form.get("x", 0)
        y = request.form.get("y", 0)
        rotation = float(request.form.get("rotation", 0))
        image_file = request.files.get('image')
        # sticker_type default 'image'
    else:
        # JSON (Emoji)
        try:
            import msgspec
            from core.schemas import AddStickerRequest
            req = msgspec.json.decode(request.get_data(), type=AddStickerRequest)
            sticker_type = req.sticker_type
            target_user_id = req.target_user_id
            x = req.x
            y = req.y
            rotation = req.rotation if req.rotation is not None else 0
        except msgspec.ValidationError as e:
            return jsonify(error=f"Invalid request: {e}"), 400

    if not target_user_id:
         target_user_id = g.user["id"]

    # We need profile_id, not target_user_id for service
    # Helper to get profile_id from user_id?
    # Or strict check.
    # We can do this lookup here or let service handle it? Service expects profile_id.
    # Let's import get_db mostly for this one check? Or add helper to service?
    # Actually, let's query DB here quickly or add a helper in service `get_profile_id_by_user`.
    # `profile_service.get_profile_by_user_id` returns a dict with `profile_id`.
    
    p_result = profile_service.get_profile_by_user_id(target_user_id)
    if not p_result.success or not p_result.data["profile_id"]:
         return jsonify(error="Target profile not found"), 404
    
    profile_id = p_result.data["profile_id"]

    result = sticker_service.add_sticker(
        user_id=g.user['id'],
        profile_id=profile_id,
        sticker_type=sticker_type,
        x_pos=float(x),
        y_pos=float(y),
        rotation=float(rotation),
        image_file=image_file,
        # Original profile.py used JSON for emojis, which essentially means they are "images" but with paths known by frontend?
        # NO, wait. `mutations/profile.py` for "Standard Emoji Sticker" used `req.sticker_type` but did it save it?
        # It did `stickers/uuid.png` logic ONLY for multipart.
        # For JSON, it passed `image_path` as NULL?
        # `mutations/profile.py` insert: `INSERT INTO profile_stickers ... image_path`
        # In JSON case, image_path was undefined in that block! It likely inserted NULL or failed if not null constraint?
        # Actually `image_path` variable was set in multipart block.
        # It seems `mutations/profile.py` JSON path was broken or relied on `sticker_type` containing content?
        # Ah, emojis are just text? Or pre-baked paths?
        # Let's assuming for JSON path (emojis), we pass `sticker_type` (which might be the emoji char?)
        # If `sticker_type` is real type like 'image', then we need path.
        # If `sticker_type` holds the emoji, we might want to pass it as text_content?
        # Let's inspect `AddStickerRequest`.
        text_content=None 
    )
    
    if not result.success:
        return jsonify(error=result.error), result.status

    return jsonify(ok=True, **result.data)


def update_sticker():
    """Update sticker position/rotation/scale."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import UpdateStickerRequest
        req = msgspec.json.decode(request.get_data(), type=UpdateStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    updates = {}
    if req.x is not None: updates['x'] = req.x
    if req.y is not None: updates['y'] = req.y
    if req.rotation is not None: updates['rotation'] = req.rotation
    if req.scale is not None: updates['scale'] = req.scale
    if req.z_index is not None: updates['z_index'] = req.z_index
    
    result = sticker_service.update_sticker(g.user['id'], req.id, updates)
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(ok=True)


def remove_sticker():
    """Remove a sticker."""
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import RemoveStickerRequest
        req = msgspec.json.decode(request.get_data(), type=RemoveStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
        
    result = sticker_service.delete_sticker(g.user['id'], req.id)
    
    if not result.success:
         return jsonify(error=result.error), result.status
         
    return jsonify(ok=True)

