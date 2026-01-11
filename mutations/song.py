"""
Song mutations.
Delegates to song_service.
"""

from flask import request, g, jsonify
import msgspec
from services import song_service

def save_song():
    """
    Create or update a song project.
    """
    if g.user is None:
        return jsonify(ok=False, error="Auth required"), 401

    try:
        from core.schemas import SaveSongRequest
        req = msgspec.json.decode(request.get_data(), type=SaveSongRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    # Encode data dict to JSON string for storage
    # Service expects the JSON string for data_json
    try:
        data_json = msgspec.json.encode(req.data).decode('utf-8')
    except Exception as e:
        return jsonify(ok=False, error="Invalid song data"), 400

    result = song_service.save_song(
        user_id=g.user['id'],
        title=req.title,
        data_json=data_json,
        is_public=req.is_public,
        song_id=req.id
    )
    
    if not result.success:
        return jsonify(ok=False, error=result.error), result.status
        
    return jsonify(ok=True, **(result.data or {}))

def delete_song():
    """Delete a song project."""
    if g.user is None:
        return jsonify(ok=False, error="Auth required"), 401

    try:
        from core.schemas import DeleteSongRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteSongRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    result = song_service.delete_song(g.user['id'], req.id)
    
    if not result.success:
        return jsonify(ok=False, error=result.error), result.status
        
    return jsonify(ok=True, **(result.data or {}))

