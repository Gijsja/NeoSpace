"""
Profile Service - Business logic for profile operations.
Extracted from mutations/profile.py for testability.
"""

import re
import os
import json
import uuid
import random
import hashlib
import html
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from db import get_db

# =============================================
# CONSTANTS
# =============================================

ALLOWED_THEMES = {"default", "dark", "retro", "cyber", "zen"}
ALLOWED_DM_POLICIES = {"everyone", "mutuals", "nobody"}
HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_DISPLAY_NAME_LENGTH = 50
MAX_BIO_LENGTH = 500


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
# VALIDATION HELPERS
# =============================================

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
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name)
    return cleaned.strip()[:MAX_DISPLAY_NAME_LENGTH]


def sanitize_bio(bio: str) -> str:
    """Sanitize bio content using bleach."""
    if not bio:
        return ""
    from utils.sanitize import clean_html
    return clean_html(bio.strip()[:MAX_BIO_LENGTH])


# =============================================
# PROFILE OPERATIONS
# =============================================

def get_profile_by_user_id(user_id: int, viewer_id: Optional[int] = None, wall_page: int = 1, wall_limit: int = 20) -> ServiceResult:
    """
    Fetch a user's profile with all related data.
    
    Args:
        user_id: ID of the profile owner
        viewer_id: ID of the viewing user (for privacy checks)
        wall_page: Pagination page (1-indexed)
        wall_limit: Items per page
    
    Returns:
        ServiceResult with profile data or error
    """
    db = get_db()
    
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
        return ServiceResult(success=False, error="User not found", status=404)
    
    # Check privacy
    is_own = viewer_id == user_id if viewer_id else False
    is_public = row["is_public"] if row["is_public"] is not None else True
    
    if not is_public and not is_own:
        return ServiceResult(success=False, error="Profile is private", status=403)
    
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
    
    # Get Modular Wall Posts
    wall_modules = []
    has_more_wall = False
    
    if row["profile_id"]:
        from mutations.wall import get_wall_posts
        offset = (wall_page - 1) * wall_limit
        # Fetch one extra to check if more exist
        fetched_modules = get_wall_posts(row["profile_id"], limit=wall_limit + 1, offset=offset)
        
        if len(fetched_modules) > wall_limit:
            has_more_wall = True
            wall_modules = fetched_modules[:wall_limit]
        else:
            wall_modules = fetched_modules
        
        # Enrich script modules with details
        script_ids = [m["content"].get("script_id") for m in wall_modules 
                      if m["module_type"] == 'script' and m["content"].get("script_id")]
        
        if script_ids:
            placeholders = ",".join("?" * len(script_ids))
            script_details = db.execute(
                f"SELECT id, title, script_type FROM scripts WHERE id IN ({placeholders})",
                script_ids
            ).fetchall()
            script_map = {s["id"]: dict(s) for s in script_details}
            
            for m in wall_modules:
                if m["module_type"] == 'script':
                    sid = m["content"].get("script_id")
                    if sid and sid in script_map:
                        m["script_details"] = script_map[sid]
    
    # Social Graph
    from queries.friends import get_top8, get_follower_count, get_following_count, is_following as check_following
    
    top8 = get_top8(user_id)
    follower_count = get_follower_count(user_id)
    following_count = get_following_count(user_id)
    viewer_is_following = check_following(viewer_id, user_id) if viewer_id and not is_own else False

    profile_data = {
        "user_id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"] or row["username"],
        "bio": row["bio"] or "",
        "avatar_path": row["avatar_path"],
        "theme_preset": row["theme_preset"] or "default",
        "accent_color": row["accent_color"] or "#3b82f6",
        "status_message": row["status_message"] or "",
        "status_emoji": row["status_emoji"] or "",
        "now_activity": row["now_activity"] or "",
        "now_activity_type": row["now_activity_type"] or "thinking",
        "member_since": row["member_since"],
        "is_own": is_own,
        "dm_policy": row["dm_policy"] if is_own else None,
        "show_online_status": bool(row["show_online_status"]) if row["show_online_status"] is not None else True,
        "voice_intro_path": row["voice_intro_path"],
        "voice_waveform_json": row["voice_waveform_json"],
        "anthem_url": row["anthem_url"] or "",
        "anthem_autoplay": bool(row["anthem_autoplay"]) if row["anthem_autoplay"] is not None else True,
        "stickers": stickers,
        "wall_modules": wall_modules,
        "wall_pagination": {
            "page": wall_page,
            "has_more": has_more_wall
        },
        "top8": top8,
        "follower_count": follower_count,
        "following_count": following_count,
        "viewer_is_following": viewer_is_following,
        "pinned_scripts": [],  # Deprecated
        "viewer_id": viewer_id
    }
    
    return ServiceResult(success=True, data=profile_data)


def update_profile_fields(user_id: int, data: Dict[str, Any]) -> ServiceResult:
    """
    Update profile fields for a user.
    
    Args:
        user_id: ID of the profile owner
        data: Dictionary of fields to update
    
    Returns:
        ServiceResult indicating success or error
    """
    db = get_db()
    updates = {}
    
    # Validate and sanitize each field
    if "display_name" in data:
        updates["display_name"] = sanitize_display_name(data["display_name"])
    
    if "bio" in data:
        updates["bio"] = sanitize_bio(data["bio"])
    
    if "status_message" in data:
        updates["status_message"] = html.escape(data["status_message"].strip()[:100])
    
    if "status_emoji" in data:
        updates["status_emoji"] = data["status_emoji"][:4]
    
    if "now_activity" in data:
        updates["now_activity"] = html.escape(data["now_activity"].strip()[:50])
        
    if "now_activity_type" in data:
        updates["now_activity_type"] = data["now_activity_type"]
    
    if "theme_preset" in data:
        theme = data["theme_preset"]
        if theme not in ALLOWED_THEMES:
            return ServiceResult(success=False, error=f"Invalid theme. Choose from: {ALLOWED_THEMES}", status=400)
        updates["theme_preset"] = theme
    
    if "accent_color" in data:
        try:
            updates["accent_color"] = validate_hex_color(data["accent_color"])
        except ValueError as e:
            return ServiceResult(success=False, error=str(e), status=400)
    
    if "is_public" in data:
        updates["is_public"] = 1 if data["is_public"] else 0
    
    if "show_online_status" in data:
        updates["show_online_status"] = 1 if data["show_online_status"] else 0
    
    if "dm_policy" in data:
        policy = data["dm_policy"]
        if policy not in ALLOWED_DM_POLICIES:
            return ServiceResult(success=False, error=f"Invalid DM policy. Choose from: {ALLOWED_DM_POLICIES}", status=400)
        updates["dm_policy"] = policy
    
    if "anthem_url" in data:
        url = data["anthem_url"].strip() if data["anthem_url"] else ""
        if url and not (url.startswith("http://") or url.startswith("https://")):
            return ServiceResult(success=False, error="Anthem URL must be http:// or https://", status=400)
        updates["anthem_url"] = url[:500]
    
    if "anthem_autoplay" in data:
        updates["anthem_autoplay"] = 1 if data["anthem_autoplay"] else 0
    
    if not updates:
        return ServiceResult(success=False, error="No valid fields to update", status=400)
    
    # Check if profile exists
    existing = db.execute(
        "SELECT id FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    
    if existing:
        # Update existing profile
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        set_clause += ", updated_at = datetime('now')"
        values = list(updates.values())
        values.append(user_id)
        
        db.execute(
            f"UPDATE profiles SET {set_clause} WHERE user_id = ?",
            values
        )
    else:
        # Create new profile
        updates["user_id"] = user_id
        columns = ", ".join(updates.keys())
        placeholders = ", ".join("?" for _ in updates.values())
        values = list(updates.values())
        
        db.execute(
            f"INSERT INTO profiles ({columns}) VALUES ({placeholders})",
            values
        )
    
    db.commit()
    return ServiceResult(success=True)


def save_avatar(user_id: int, file_data: bytes, extension: str, app_root: str) -> ServiceResult:
    """
    Save avatar file and update profile.
    
    Args:
        user_id: Profile owner ID
        file_data: Raw file bytes
        extension: File extension (png, jpg, etc.)
        app_root: Application root path for file storage
    
    Returns:
        ServiceResult with avatar_path on success
    """
    if extension not in ALLOWED_AVATAR_EXTENSIONS:
        return ServiceResult(success=False, error=f"Invalid file type. Allowed: {ALLOWED_AVATAR_EXTENSIONS}", status=400)
    
    if len(file_data) > 2 * 1024 * 1024:
        return ServiceResult(success=False, error="File too large (max 2MB)", status=400)
    
    checksum = hashlib.sha256(file_data).hexdigest()
    filename = f"avatar_{user_id}_{checksum[:16]}.{extension}"
    
    avatar_dir = os.path.join(app_root, 'static/avatars')
    os.makedirs(avatar_dir, exist_ok=True)
    
    filepath = os.path.join(avatar_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(file_data)
    
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
    return ServiceResult(success=True, data={"avatar_path": avatar_path})


def create_default_profile(user_id: int, username: str) -> ServiceResult:
    """
    Create a default profile for a new user.
    
    Args:
        user_id: New user's ID
        username: Username for display_name default
    
    Returns:
        ServiceResult indicating success
    """
    db = get_db()
    db.execute(
        """INSERT INTO profiles (user_id, display_name) 
           VALUES (?, ?)""",
        (user_id, username)
    )
    db.commit()
    return ServiceResult(success=True)
