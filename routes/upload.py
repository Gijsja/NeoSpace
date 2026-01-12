from flask import Blueprint, request, jsonify, g
from auth import login_required
from mutations.file_mutations import upload_file

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('', methods=['POST'])
@login_required
def upload_endpoint():
    # Use existing mutation (reads request.files directly)
    return upload_file()
