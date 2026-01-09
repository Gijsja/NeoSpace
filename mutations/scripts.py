
from flask import request, g, jsonify
from db import get_db

def save_script():
    """
    Create or update a script (Strict Validation).
    """
    db = get_db()
    user_id = g.user['id']
    
    try:
        import msgspec
        from msgspec_models import SaveScriptRequest
        req = msgspec.json.decode(request.get_data(), type=SaveScriptRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    if req.id:
        # Update existing
        row = db.execute("SELECT user_id FROM scripts WHERE id=?", (req.id,)).fetchone()
        if not row:
            return jsonify(ok=False, error="Script not found"), 404
        if row['user_id'] != user_id:
            return jsonify(ok=False, error="Not authorized"), 403
            
        db.execute(
            """UPDATE scripts 
               SET title=?, content=?, script_type=?, is_public=?, updated_at=datetime('now') 
               WHERE id=?""",
            (req.title, req.content, req.script_type, req.is_public, req.id)
        )
        db.commit()
        return jsonify(ok=True, id=req.id, message="Updated")
    else:
        # Create new
        try:
            row = db.execute(
                """INSERT INTO scripts (user_id, title, content, script_type, is_public) 
                   VALUES (?, ?, ?, ?, ?) 
                   RETURNING id""",
                (user_id, req.title, req.content, req.script_type, req.is_public)
            ).fetchone()
            db.commit()
            return jsonify(ok=True, id=row['id'], message="Created")
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 500

def list_scripts():
    """List scripts for the current user."""
    db = get_db()
    user_id = g.user['id']
    
    rows = db.execute(
        "SELECT id, title, script_type, updated_at, created_at FROM scripts WHERE user_id=? ORDER BY updated_at DESC, created_at DESC",
        (user_id,)
    ).fetchall()
    
    scripts = [dict(
        id=r['id'], 
        title=r['title'], 
        script_type=r['script_type'],
        last_modified=r['updated_at'] or r['created_at']
    ) for r in rows]
    
    return jsonify(ok=True, scripts=scripts)

def get_script():
    """Get a single script by ID."""
    db = get_db()
    script_id = request.args.get('id')
    
    if not script_id:
        return jsonify(ok=False, error="Missing ID"), 400
        
    row = db.execute("SELECT * FROM scripts WHERE id=?", (script_id,)).fetchone()
    
    if not row:
        return jsonify(ok=False, error="Script not found"), 404
        
    is_owner = g.user and row['user_id'] == g.user['id']
    if not row['is_public'] and not is_owner:
         return jsonify(ok=False, error="Private script"), 403

    return jsonify(ok=True, script=dict(row))

def delete_script():
    """Delete a script (Strict Validation)."""
    db = get_db()
    user_id = g.user['id']
    
    try:
        import msgspec
        from msgspec_models import DeleteScriptRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteScriptRequest)
    except msgspec.ValidationError as e:
        return jsonify(ok=False, error=str(e)), 400

    # Check ownership
    row = db.execute("SELECT user_id FROM scripts WHERE id=?", (req.id,)).fetchone()
    if not row:
        return jsonify(ok=False, error="Not found"), 404
    if row['user_id'] != user_id:
        return jsonify(ok=False, error="Not authorized"), 403
        
    db.execute("DELETE FROM scripts WHERE id=?", (req.id,))
    db.commit()
    return jsonify(ok=True, deleted=req.id)
