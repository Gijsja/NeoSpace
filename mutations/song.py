
from flask import request, g, jsonify
from db import get_db
import msgspec
from msgspec_models import SaveSongRequest, DeleteSongRequest

def save_song():
    """
    Create or update a song project.
    """
    db = get_db()
    user_id = g.user['id']
    
    try:
        req = msgspec.json.decode(request.get_data(), type=SaveSongRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    # Encode data dict to JSON string for storage
    try:
        data_json = msgspec.json.encode(req.data).decode('utf-8')
    except Exception as e:
        return jsonify(ok=False, error="Invalid song data"), 400

    if req.id:
        # Update existing
        row = db.execute("SELECT user_id FROM songs WHERE id=?", (req.id,)).fetchone()
        if not row:
            return jsonify(ok=False, error="Song not found"), 404
        if row['user_id'] != user_id:
            return jsonify(ok=False, error="Not authorized"), 403
            
        db.execute(
            """UPDATE songs 
               SET title=?, data_json=?, is_public=?, updated_at=datetime('now') 
               WHERE id=?""",
            (req.title, data_json, req.is_public, req.id)
        )
        db.commit()
        return jsonify(ok=True, id=req.id, message="Saved")
    else:
        # Create new
        try:
            cur = db.execute(
                """INSERT INTO songs (user_id, title, data_json, is_public) 
                   VALUES (?, ?, ?, ?) 
                   RETURNING id""",
                (user_id, req.title, data_json, req.is_public)
            )
            row = cur.fetchone()
            db.commit()
            return jsonify(ok=True, id=row['id'], message="Created")
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 500

def delete_song():
    """Delete a song project."""
    db = get_db()
    user_id = g.user['id']
    
    try:
        req = msgspec.json.decode(request.get_data(), type=DeleteSongRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    row = db.execute("SELECT user_id FROM songs WHERE id=?", (req.id,)).fetchone()
    if not row:
        return jsonify(ok=False, error="Not found"), 404
    if row['user_id'] != user_id:
        return jsonify(ok=False, error="Not authorized"), 403
        
    db.execute("DELETE FROM songs WHERE id=?", (req.id,))
    db.commit()
    return jsonify(ok=True, deleted=req.id)
