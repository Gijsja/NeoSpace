import os
from flask import Blueprint, send_from_directory, current_app, session, abort
from auth import login_required

bp = Blueprint('files', __name__, url_prefix='/files')

@bp.route('/<shard>/user_<int:user_id>/<category>/<filename>')
def serve_user_file(shard, user_id, category, filename):
    """
    Serve user-specific files with access control.
    """
    viewer_id = session.get('user_id')

    # 1. Public Categories (e.g., avatars)
    if category == 'avatars':
        pass
    else:
        # 2. Private/Authenticated Categories
        if not viewer_id:
            abort(401)
        
        # For certain categories, we might want strict ownership
        # if category == 'private_vault' and user_id != viewer_id:
        #     abort(403)
        pass

    upload_root = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    if '..' in filename or '..' in category or '..' in shard:
        abort(400)

    directory = os.path.join(current_app.root_path, upload_root, shard, f"user_{user_id}", category)
    return send_from_directory(directory, filename)

@bp.route('/user_<int:user_id>/<category>/<filename>')
def serve_unsharded_user_file(user_id, category, filename):
    """
    Fallback for unsharded user files.
    """
    viewer_id = session.get('user_id')
    if category != 'avatars' and not viewer_id:
        abort(401)

    upload_root = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    directory = os.path.join(current_app.root_path, upload_root, f"user_{user_id}", category)
    return send_from_directory(directory, filename)

@bp.route('/<filename>')
def serve_legacy_file(filename):
    """
    Fallback for legacy files at the root of the upload folder.
    """
    # Legacy files are treated as authenticated-only for safety
    if not session.get('user_id'):
        abort(401)
        
    upload_root = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    directory = os.path.join(current_app.root_path, upload_root)
    return send_from_directory(directory, filename)
