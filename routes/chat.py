from flask import Blueprint
from mutations.message_mutations import send_message, edit_message, delete_message
from mutations.file_mutations import upload_file
from queries.backfill import backfill_messages
from queries.unread import unread_count
from auth import login_required

bp = Blueprint('chat', __name__)

bp.add_url_rule("/send", "send", login_required(send_message), methods=["POST"])
bp.add_url_rule("/edit", "edit", login_required(edit_message), methods=["POST"])
bp.add_url_rule("/delete", "delete", login_required(delete_message), methods=["POST"])
bp.add_url_rule("/upload", "upload", login_required(upload_file), methods=["POST"])
bp.add_url_rule("/backfill", "backfill", login_required(backfill_messages))
bp.add_url_rule("/unread", "unread", unread_count)
