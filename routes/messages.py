from flask import Blueprint
from mutations.dm import send_dm, mark_dm_read, delete_dm, get_conversation, list_conversations
from auth import login_required

bp = Blueprint('messages', __name__, url_prefix='/dm')

bp.add_url_rule("/send", "send_dm", login_required(send_dm), methods=["POST"])
bp.add_url_rule("/conversation", "get_conversation", login_required(get_conversation), methods=["GET"])
bp.add_url_rule("/read", "mark_dm_read", login_required(mark_dm_read), methods=["POST"])
bp.add_url_rule("/delete", "delete_dm", login_required(delete_dm), methods=["POST"])
bp.add_url_rule("/list", "list_conversations", login_required(list_conversations), methods=["GET"])
