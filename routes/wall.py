from flask import Blueprint, render_template
from auth import login_required
from mutations.wall import add_wall_post, update_wall_post, delete_wall_post, reorder_wall_posts
from mutations.sticker import add_sticker, update_sticker, delete_sticker
from mutations.file_mutations import upload_file

bp = Blueprint('wall', __name__, url_prefix='/wall')

@bp.route("/")
@login_required
def index():
    return render_template("wall.html")

# Wall Post CRUD
bp.add_url_rule("/post/add", "add_wall_post", login_required(add_wall_post), methods=["POST"])
bp.add_url_rule("/post/update", "update_wall_post", login_required(update_wall_post), methods=["POST"])
bp.add_url_rule("/post/delete", "delete_wall_post", login_required(delete_wall_post), methods=["POST"])
bp.add_url_rule("/post/upload", "upload_file", login_required(upload_file), methods=["POST"])
bp.add_url_rule("/reorder", "reorder_wall_posts", login_required(reorder_wall_posts), methods=["POST"])

# Sticker CRUD
bp.add_url_rule("/sticker/add", "add_sticker", login_required(add_sticker), methods=["POST"])
bp.add_url_rule("/sticker/update", "update_sticker", login_required(update_sticker), methods=["POST"])
bp.add_url_rule("/sticker/delete", "delete_sticker", login_required(delete_sticker), methods=["POST"])

@bp.route("/posts/<int:profile_id>")
def get_profile_posts(profile_id):
    from flask import request, jsonify
    from mutations.wall import get_wall_posts
    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    offset = (page - 1) * limit
    
    posts = get_wall_posts(profile_id, limit=limit, offset=offset)
    return jsonify(posts=posts, page=page, has_more=len(posts) == limit)
