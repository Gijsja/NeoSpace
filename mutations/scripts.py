"""
Script mutations.
Delegates to script_service.
"""

from flask import request, g, jsonify
import msgspec
from services import script_service

def save_script():
    """
    Create or update a script.
    """
    if g.user is None:
        return jsonify(ok=False, error="Auth required"), 401

    try:
        from core.schemas import SaveScriptRequest
        req = msgspec.json.decode(request.get_data(), type=SaveScriptRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    result = script_service.save_script(
        user_id=g.user['id'],
        title=req.title,
        content=req.content,
        script_type=req.script_type,
        is_public=req.is_public,
        script_id=req.id,
        parent_id=req.parent_id
    )
    
    if not result.success:
        return jsonify(ok=False, error=result.error), result.status
        
    return jsonify(ok=True, **(result.data or {}))

def list_scripts():
    """List scripts for the current user."""
    if g.user is None:
        return jsonify(ok=False, error="Auth required"), 401
    
    result = script_service.list_user_scripts(g.user['id'])
    
    if not result.success:
        return jsonify(ok=False, error=result.error), result.status
        
    return jsonify(ok=True, **result.data)

def get_script():
    """Get a single script by ID."""
    script_id = request.args.get('id')
    
    if not script_id:
        return jsonify(ok=False, error="Missing ID"), 400
        
    try:
        script_id = int(script_id)
    except ValueError:
        return jsonify(ok=False, error="Invalid ID"), 400
        
    user_id = g.user['id'] if g.user else None
    
    result = script_service.get_script_by_id(script_id, user_id)
    
    if not result.success:
        return jsonify(ok=False, error=result.error), result.status
        
    return jsonify(ok=True, **result.data)

def delete_script():
    """Delete a script."""
    if g.user is None:
        return jsonify(ok=False, error="Auth required"), 401

    try:
        from core.schemas import DeleteScriptRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteScriptRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    result = script_service.delete_script(g.user['id'], req.id)
    
    if not result.success:
        return jsonify(ok=False, error=result.error), result.status
        
    return jsonify(ok=True, **(result.data or {}))

