from flask import Blueprint, request, jsonify
from mutations.scripts import save_script, list_scripts, get_script, delete_script
from auth import login_required

bp = Blueprint('scripts', __name__, url_prefix='/scripts')

bp.add_url_rule("/save", "save_script", login_required(save_script), methods=["POST"])
bp.add_url_rule("/list", "list_scripts", login_required(list_scripts), methods=["GET"])
bp.add_url_rule("/get", "get_script", get_script, methods=["GET"]) # Public read allowed
bp.add_url_rule("/delete", "delete_script", login_required(delete_script), methods=["POST"])
