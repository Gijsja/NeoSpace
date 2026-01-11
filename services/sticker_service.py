"""
Sticker Service - Business logic for sticker operations.
Consolidates logic from mutations/sticker.py and mutations/profile.py.
"""

import os
import uuid
import random
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from db import get_db

# =============================================
# CONSTANTS
# =============================================

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

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
# HELPERS
# =============================================

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =============================================
# STICKER OPERATIONS
# =============================================

def add_sticker(
    user_id: int,
    profile_id: int,
    sticker_type: str,
    x_pos: float = 0.0,
    y_pos: float = 0.0,
    rotation: float = 0.0,
    scale: float = 1.0,
    z_index: int = 10,
    text_content: Optional[str] = None,
    image_file: Optional[FileStorage] = None,
    image_path: Optional[str] = None # For pre-uploaded or existing images
) -> ServiceResult:
    """
    Add a sticker to a profile.
    
    Args:
        user_id: User adding the sticker (placed_by)
        profile_id: Profile to add sticker to
        sticker_type: 'image' or 'text'
        x_pos, y_pos: Coordinates
        rotation: Rotation in degrees
        scale: Scale factor
        z_index: Z-index
        text_content: Content for text stickers
        image_file: FileStorage object for new uploads
        image_path: Direct path if not uploading
    
    Returns:
        ServiceResult with sticker data
    """
    db = get_db()
    
    # Verify profile exists
    profile = db.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    if not profile:
        return ServiceResult(success=False, error="Target profile not found", status=404)

    final_image_path = image_path

    if sticker_type == 'image':
        if image_file:
            if not allowed_file(image_file.filename):
                return ServiceResult(success=False, error="Invalid file type", status=400)
            
            # Save file
            ext = image_file.filename.rsplit('.', 1)[1].lower()
            filename = f"sticker_{uuid.uuid4().hex}.{ext}"
            
            upload_folder = os.path.join(current_app.root_path, "static", "uploads", "stickers")
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            
            final_image_path = f"/static/uploads/stickers/{filename}"
            
        elif not final_image_path and not text_content: 
            # If no file and no path, and it is an image type, maybe it is a "standard emoji sticker" 
            # which might be treated as image-less or handled differently?
            # mutations/profile.py handled "Standard Emoji Sticker" via JSON request but `image_path` was reused?
            # Actually, `mutations/profile.py` logic for emojis seemed to use `sticker_type` from request but 
            # didn't explicitly save an image for emojis.
            # If it's pure text/emoji rendered effectively as text, then type should be 'text'.
            # If it's a pre-defined asset path, image_path should be provided.
            if not text_content and not image_path:
                 return ServiceResult(success=False, error="Image file or path required for image stickers", status=400)

    elif sticker_type == 'text':
        if not text_content:
            return ServiceResult(success=False, error="Text content required for text stickers", status=400)

    sticker_id = str(uuid.uuid4())
    
    # If rotation not specified (or 0), and we want randomness for "organic" feel like in profile.py
    # But service should be deterministic generally. Let caller handle randomness or explicit default.
    # We'll use passed values.

    try:
        db.execute(
            """INSERT INTO profile_stickers 
               (id, profile_id, sticker_type, image_path, text_content, x_pos, y_pos, rotation, scale, z_index, placed_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sticker_id, profile_id, sticker_type, final_image_path, text_content, x_pos, y_pos, rotation, scale, z_index, user_id)
        )
        db.commit()
    except Exception as e:
        return ServiceResult(success=False, error=str(e), status=500)
    
    # Fetch username for response convenience (used by frontend)
    placer = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    username = placer['username'] if placer else "Unknown"

    return ServiceResult(success=True, data={
        "id": sticker_id,
        "sticker_type": sticker_type,
        "image_path": final_image_path,
        "text_content": text_content,
        "x_pos": x_pos,
        "y_pos": y_pos,
        "rotation": rotation,
        "scale": scale,
        "z_index": z_index,
        "placed_by": user_id,
        "placed_by_username": username
    })


def update_sticker(
    user_id: int,
    sticker_id: str,
    updates: Dict[str, Any]
) -> ServiceResult:
    """
    Update a sticker's properties.
    
    Args:
        user_id: User requesting update (must be owner or placer)
        sticker_id: ID of sticker
        updates: Dictionary of fields to update (x, y, rotation, scale, z_index)
        
    Returns:
        ServiceResult
    """
    db = get_db()
    
    # Get sticker and check permissions
    sticker = db.execute(
        """SELECT s.*, p.user_id as profile_owner_id 
           FROM profile_stickers s 
           JOIN profiles p ON s.profile_id = p.id 
           WHERE s.id = ?""", 
        (sticker_id,)
    ).fetchone()
    
    if not sticker:
        return ServiceResult(success=False, error="Sticker not found", status=404)
        
    # Permission: Profile Owner OR Sticker Placer
    if user_id != sticker['profile_owner_id'] and user_id != sticker['placed_by']:
         return ServiceResult(success=False, error="Unauthorized", status=403)

    # Map generic update keys to DB columns
    db_updates = []
    values = []
    
    # Mapping support for both 'x'/'y' (common api) and 'x_pos'/'y_pos' (db)
    key_map = {
        'x': 'x_pos', 'x_pos': 'x_pos',
        'y': 'y_pos', 'y_pos': 'y_pos',
        'rotation': 'rotation',
        'scale': 'scale',
        'z_index': 'z_index'
    }

    for key, value in updates.items():
        if key in key_map and value is not None:
             db_updates.append(f"{key_map[key]} = ?")
             values.append(value)
             
    if not db_updates:
        return ServiceResult(success=True) # Check if this counts as success? Yes.
        
    values.append(sticker_id)
    
    try:
        db.execute(f"UPDATE profile_stickers SET {', '.join(db_updates)} WHERE id = ?", values)
        db.commit()
    except Exception as e:
        return ServiceResult(success=False, error=str(e), status=500)
        
    return ServiceResult(success=True)


def delete_sticker(user_id: int, sticker_id: str) -> ServiceResult:
    """
    Delete a sticker.
    
    Args:
        user_id: User requesting delete
        sticker_id: ID of sticker
        
    Returns:
        ServiceResult
    """
    db = get_db()
    
    # Check permissions (Owner of Profile OR Placer of Sticker)
    # Optimized single query delete
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
        # Check if it existed but was unauthorized, or just didn't exist?
        # For simplicity return Not Found / Unauthorized generic error or just 404
        # Querying to check existence first would be more verbose but precise.
        # But looking at mutation logic, if rowcount=0 it returns 404/Error.
        return ServiceResult(success=False, error="Sticker not found or not authorized", status=404)
        
    return ServiceResult(success=True)
