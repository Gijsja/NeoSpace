from flask import Blueprint
from queries.directory import list_users, get_user_by_username, user_cards_html
from auth import login_required

bp = Blueprint('directory', __name__, url_prefix='/users')

bp.add_url_rule("/", "list_users", login_required(list_users), methods=["GET"])
bp.add_url_rule("/lookup", "get_user_by_username", login_required(get_user_by_username), methods=["GET"])
bp.add_url_rule("/cards", "user_cards_html", login_required(user_cards_html), methods=["GET"])

