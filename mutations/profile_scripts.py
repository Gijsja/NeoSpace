"""
Profile Scripts Mutations
Pin/unpin scripts to user profile walls.
"""

import sqlite3
from db import execute_with_retry
from flask import request, g, jsonify


def pin_script(user_id, script_id, display_order):
    """
    Pin a script to the user's profile wall.
    
    Args:
        user_id: ID of the user pinning the script
        script_id: ID of the script to pin
        display_order: Position (0, 1, or 2)
    
    Returns:
        dict with 'ok' boolean and optional 'error' message
    """
    # Validate display_order
    if display_order not in (0, 1, 2):
        return {"ok": False, "error": "Invalid display order"}
    
    # Get profile_id for user
    profile = execute_with_retry(
        "SELECT id FROM profiles WHERE user_id = ?",
        (user_id,),
        fetchone=True
    )
    
    if not profile:
        return {"ok": False, "error": "Profile not found"}
    
    profile_id = profile['id']
    
    # Verify user owns the script
    script = execute_with_retry(
        "SELECT user_id FROM scripts WHERE id = ?",
        (script_id,),
        fetchone=True
    )
    
    if not script:
        return {"ok": False, "error": "Script not found"}
    
    if script['user_id'] != user_id:
        return {"ok": False, "error": "Cannot pin other users' scripts"}
    
    # Check if already at max (3 pins)
    count = execute_with_retry(
        "SELECT COUNT(*) as count FROM profile_scripts WHERE profile_id = ?",
        (profile_id,),
        fetchone=True
    )
    
    if count['count'] >= 3:
        return {"ok": False, "error": "Maximum 3 scripts can be pinned"}
    
    # Insert pin
    try:
        execute_with_retry(
            """INSERT INTO profile_scripts (profile_id, script_id, display_order)
               VALUES (?, ?, ?)""",
            (profile_id, script_id, display_order)
        )
        return {"ok": True}
    except sqlite3.IntegrityError:
        return {"ok": False, "error": "Script already pinned"}


def unpin_script(user_id, script_id):
    """
    Remove a pinned script from the user's profile.
    
    Args:
        user_id: ID of the user
        script_id: ID of the script to unpin
    
    Returns:
        dict with 'ok' boolean
    """
    # Get profile_id
    profile = execute_with_retry(
        "SELECT id FROM profiles WHERE user_id = ?",
        (user_id,),
        fetchone=True
    )
    
    if not profile:
        return {"ok": False, "error": "Profile not found"}
    
    profile_id = profile['id']
    
    # Delete pin
    execute_with_retry(
        "DELETE FROM profile_scripts WHERE profile_id = ? AND script_id = ?",
        (profile_id, script_id)
    )
    
    return {"ok": True}


def reorder_pins(user_id, script_ids):
    """
    Reorder pinned scripts.
    
    Args:
        user_id: ID of the user
        script_ids: List of script IDs in desired order (max 3)
    
    Returns:
        dict with 'ok' boolean
    """
    if len(script_ids) > 3:
        return {"ok": False, "error": "Maximum 3 scripts"}
    
    # Get profile_id
    profile = execute_with_retry(
        "SELECT id FROM profiles WHERE user_id = ?",
        (user_id,),
        fetchone=True
    )
    
    if not profile:
        return {"ok": False, "error": "Profile not found"}
    
    profile_id = profile['id']
    
    # Update display orders
    try:
        for idx, script_id in enumerate(script_ids):
            execute_with_retry(
                """UPDATE profile_scripts 
                   SET display_order = ? 
                   WHERE profile_id = ? AND script_id = ?""",
                (idx, profile_id, script_id)
            )
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_pinned_scripts(profile_id):
    """
    Fetch all pinned scripts for a profile.
    
    Args:
        profile_id: ID of the profile
    
    Returns:
        List of script dicts with metadata
    """
    rows = execute_with_retry(
        """SELECT s.id, s.title, s.script_type, s.updated_at,
                  ps.display_order
           FROM profile_scripts ps
           JOIN scripts s ON ps.script_id = s.id
           WHERE ps.profile_id = ?
           ORDER BY ps.display_order ASC""",
        (profile_id,),
        fetchall=True
    )
    
    return [dict(row) for row in rows] if rows else []


# =============================================================================
# View Handlers (Flask)
# =============================================================================

def pin_script_view():
    data = request.get_json()
    script_id = data.get("script_id")
    display_order = data.get("display_order", 0)
    
    if not script_id:
        return jsonify(error="script_id required"), 400
        
    result = pin_script(g.user["id"], script_id, display_order)
    if result["ok"]:
        return jsonify(ok=True)
    return jsonify(error=result.get("error")), 400


def unpin_script_view():
    data = request.get_json()
    script_id = data.get("script_id")
    
    if not script_id:
        return jsonify(error="script_id required"), 400
        
    result = unpin_script(g.user["id"], script_id)
    if result["ok"]:
        return jsonify(ok=True)
    return jsonify(error=result.get("error")), 400


def reorder_pins_view():
    data = request.get_json()
    script_ids = data.get("script_ids", [])
    
    result = reorder_pins(g.user["id"], script_ids)
    if result["ok"]:
        return jsonify(ok=True)
    return jsonify(error=result.get("error")), 400

