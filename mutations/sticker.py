"""
Sticker mutations.
Delegates to sticker_service.
"""

from flask import request, jsonify, g
from services import sticker_service

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
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    profile_id = request.form.get('profile_id')
    x_pos = request.form.get('x_pos', 0)
    y_pos = request.form.get('y_pos', 0)
    sticker_type = request.form.get('sticker_type', 'image')
    text_content = request.form.get('text_content')
    
    image_file = None
    if 'image' in request.files:
        image_file = request.files['image']

    try:
        x_pos = float(x_pos)
        y_pos = float(y_pos)
    except (ValueError, TypeError):
        return jsonify(error="Invalid coordinates"), 400

    result = sticker_service.add_sticker(
        user_id=g.user['id'],
        profile_id=profile_id,
        sticker_type=sticker_type,
        x_pos=x_pos,
        y_pos=y_pos,
        text_content=text_content,
        image_file=image_file
    )
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(success=True, sticker=result.data)


def update_sticker():
    """
    POST /wall/sticker/update
    JSON: { id, x, y, rotation, scale, z_index }
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401

    try:
        import msgspec
        from core.schemas import UpdateStickerRequest
        req = msgspec.json.decode(request.get_data(), type=UpdateStickerRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    updates = {}
    if req.x is not None: updates['x_pos'] = req.x
    if req.y is not None: updates['y_pos'] = req.y
    if req.rotation is not None: updates['rotation'] = req.rotation
    if req.scale is not None: updates['scale'] = req.scale
    if req.z_index is not None: updates['z_index'] = req.z_index
    
    result = sticker_service.update_sticker(g.user['id'], req.id, updates)
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(success=True)


def delete_sticker():
    """
    POST /wall/sticker/delete
    JSON: { id }
    """
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
         
    return jsonify(success=True)

