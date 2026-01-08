import os
import secrets
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'webm', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
        
    if file and allowed_file(file.filename):
        # Secure the filename but keep it recognizable? 
        # Better: use a random ID + ext to prevent overwrites/traversal
        ext = file.filename.rsplit('.', 1)[1].lower()
        random_name = secrets.token_urlsafe(8)
        filename = f"{random_name}.{ext}"
        
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file.save(os.path.join(upload_folder, filename))
        
        return jsonify(
            ok=True,
            url=f"/static/uploads/{filename}",
            filename=filename
        )
    
    return jsonify(error="File type not allowed"), 400
