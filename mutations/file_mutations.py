import os
import secrets
from flask import request, jsonify, current_app, g
from werkzeug.utils import secure_filename
from services.storage_service import StorageService

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'webm', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    if not g.user:
        return jsonify(error="Authentication required"), 401

    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
        
    if file and allowed_file(file.filename):
        # Determine category based on extension or context (defaulting to 'uploads')
        ext = file.filename.rsplit('.', 1)[1].lower()
        category = "audio" if ext in ('mp3', 'wav', 'webm') else "images"
        
        try:
            url = StorageService.save_file(file, g.user['id'], category)
            return jsonify(
                ok=True,
                url=url,
                filename=os.path.basename(url)
            )
        except Exception as e:
            return jsonify(error=str(e)), 500
    
    return jsonify(error="File type not allowed"), 400
