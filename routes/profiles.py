from flask import Blueprint
from auth import login_required
from mutations.profile import get_profile, update_profile, upload_avatar, upload_voice_intro
from mutations.profile import add_sticker, update_sticker, remove_sticker
from mutations.profile_scripts import pin_script_view, unpin_script_view, reorder_pins_view

bp = Blueprint('profiles', __name__, url_prefix='/profile')

# Profile Management
bp.add_url_rule("/", "get_profile", get_profile, methods=["GET"])
bp.add_url_rule("/update", "update_profile", login_required(update_profile), methods=["POST"])
bp.add_url_rule("/avatar", "upload_avatar", login_required(upload_avatar), methods=["POST"])
bp.add_url_rule("/voice/upload", "upload_voice_intro", login_required(upload_voice_intro), methods=["POST"])

# Stickers
bp.add_url_rule("/sticker/add", "add_sticker", login_required(add_sticker), methods=["POST"])
bp.add_url_rule("/sticker/update", "update_sticker", login_required(update_sticker), methods=["POST"])
bp.add_url_rule("/sticker/remove", "remove_sticker", login_required(remove_sticker), methods=["POST"])

# Pinned Scripts
bp.add_url_rule("/scripts/pin", "pin_script", login_required(pin_script_view), methods=["POST"])
bp.add_url_rule("/scripts/unpin", "unpin_script", login_required(unpin_script_view), methods=["POST"])
bp.add_url_rule("/scripts/reorder", "reorder_pins", login_required(reorder_pins_view), methods=["POST"])
