import os
import uuid
import msgspec
from flask import request, jsonify, g
from db import get_db
from werkzeug.utils import secure_filename
from msgspec_models import UpdateStickerRequest, RemoveStickerRequest

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_sticker():
    """
    POST /wall/sticker/add
    Form Data:
        profile_id: int
        x_pos: float
        y_pos: float
        sticker_type: 'image' | 'text'
        image: file (if type='image')
        text_content: str (if type='text')
    """
    profile_id = request.form.get('profile_id')
    x_pos = request.form.get('x_pos', 0)
    y_pos = request.form.get('y_pos', 0)
    sticker_type = request.form.get('sticker_type', 'image')
    
    if not profile_id:
        return jsonify({"error": "Profile ID required"}), 400

    sticker_id = str(uuid.uuid4())
    image_path = None
    text_content = None

    if sticker_type == 'text':
        text_content = request.form.get('text_content')
        if not text_content:
             return jsonify({"error": "Text content required"}), 400
    else:
        # Image handling
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Save file
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"sticker_{uuid.uuid4().hex}.{ext}"
        
        # Ensure upload directory exists
        upload_folder = os.path.join("static", "uploads", "stickers")
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        image_path = f"/static/uploads/stickers/{filename}"
    
    db = get_db()
    
    db.execute(
        """INSERT INTO profile_stickers 
           (id, profile_id, sticker_type, image_path, text_content, x_pos, y_pos, rotation, scale, z_index, placed_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sticker_id, profile_id, sticker_type, image_path, text_content, x_pos, y_pos, 0, 1, 10, g.user['id'])
    )
    db.commit()
    
    return jsonify({
        "success": True, 
        "sticker": {
            "id": sticker_id,
            "sticker_type": sticker_type,
            "image_path": image_path,
            "text_content": text_content,
            "x_pos": float(x_pos),
            "y_pos": float(y_pos),
            "rotation": 0,
            "scale": 1,
            "z_index": 10,
            "placed_by": g.user['id']
        }
    })

def update_sticker():
    """
    POST /wall/sticker/update
    JSON: { id, x, y, rotation, scale, z_index }
    """
    try:
        req = msgspec.json.decode(request.get_data(), type=UpdateStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400
    
    sticker_id = req.id
        
    db = get_db()
    
    # Permission check: Only permit OWNER of profile or AUTHOR of sticker to move it?
    # For MVP: Let's allow the Profile Owner to manage all stickers, and maybe the author to move their own.
    # Getting sticker info first
    sticker = db.execute(
        "SELECT s.*, p.user_id as profile_owner_id FROM profile_stickers s JOIN profiles p ON s.profile_id = p.id WHERE s.id = ?", 
        (sticker_id,)
    ).fetchone()
    
    if not sticker:
        return jsonify({"error": "Sticker not found"}), 404
        
    if g.user['id'] != sticker['profile_owner_id'] and g.user['id'] != sticker['placed_by']:
         return jsonify({"error": "Unauthorized"}), 403

    updates = []
    values = []
    
    if req.x is not None:
        updates.append("x_pos = ?")
        values.append(req.x)
    if req.y is not None:
        updates.append("y_pos = ?")
        values.append(req.y)
    if req.rotation is not None:
        updates.append("rotation = ?")
        values.append(req.rotation)
    if req.scale is not None:
        updates.append("scale = ?")
        values.append(req.scale)
    if req.z_index is not None:
        updates.append("z_index = ?")
        values.append(req.z_index)
        
    if not updates:
        return jsonify({"success": True}) # Nothing to update
        
    values.append(sticker_id)
    
    db.execute(f"UPDATE profile_stickers SET {', '.join(updates)} WHERE id = ?", values)
    db.commit()
    
    return jsonify({"success": True})

def delete_sticker():
    """
    POST /wall/sticker/delete
    JSON: { id }
    """
    try:
        req = msgspec.json.decode(request.get_data(), type=RemoveStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400
    
    sticker_id = req.id
    
    db = get_db()
    
    # Permission check
    sticker = db.execute(
        "SELECT s.*, p.user_id as profile_owner_id FROM profile_stickers s JOIN profiles p ON s.profile_id = p.id WHERE s.id = ?", 
        (sticker_id,)
    ).fetchone()
    
    if not sticker:
        return jsonify({"error": "Sticker not found"}), 404

    if g.user['id'] != sticker['profile_owner_id'] and g.user['id'] != sticker['placed_by']:
         return jsonify({"error": "Unauthorized"}), 403

    db.execute("DELETE FROM profile_stickers WHERE id = ?", (sticker_id,))
    db.commit()
    
    return jsonify({"success": True})
