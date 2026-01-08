"""
Sprint #16: Feed API Routes

Endpoint for the main activity feed.
"""

from flask import Blueprint, jsonify, request, g, render_template
from auth import login_required
from queries.feed import get_feed

bp = Blueprint('feed', __name__, url_prefix='/feed')


@bp.route("/home")
@login_required
def feed_home():
    return render_template("feed.html")


@bp.route("/")
@login_required
def feed_index():
    """
    Get the user's home feed.
    Query Params: limit (int), before_id (int)
    """
    limit = request.args.get("limit", 20, type=int)
    before_id = request.args.get("before_id", type=int)
    
    # Hard cap limit for safety
    if limit > 50:
        limit = 50
        
    posts = get_feed(g.user["id"], limit=limit, before_id=before_id)
    
    return jsonify(ok=True, posts=posts)
