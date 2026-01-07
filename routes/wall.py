from flask import Blueprint
from auth import login_required
from mutations.wall import add_wall_post, update_wall_post, delete_wall_post, reorder_wall_posts

bp = Blueprint('wall', __name__, url_prefix='/wall')

# Wall Post CRUD
bp.add_url_rule("/post/add", "add_wall_post", login_required(add_wall_post), methods=["POST"])
bp.add_url_rule("/post/update", "update_wall_post", login_required(update_wall_post), methods=["POST"])
bp.add_url_rule("/post/delete", "delete_wall_post", login_required(delete_wall_post), methods=["POST"])
bp.add_url_rule("/reorder", "reorder_wall_posts", login_required(reorder_wall_posts), methods=["POST"])
