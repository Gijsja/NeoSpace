"""
Sprint #17: Search API Routes

Endpoint for searching users and content.
"""

from flask import Blueprint, jsonify, request, g
from auth import login_required
from queries.search import search_users, search_posts

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route("/")
@login_required
def search_index():
    """
    Search endpoint.
    Query Params:
        q: Search term (required)
        type: 'users' or 'posts' (default: users)
        limit: int (default 20)
    """
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "users").lower()
    limit = request.args.get("limit", 20, type=int)
    
    if limit > 50:
        limit = 50
        
    if not query:
        return jsonify(ok=True, results=[])
        
    if search_type == "posts":
        results = search_posts(query, limit=limit)
    else:
        # Default to users
        results = search_users(query, current_user_id=g.user["id"], limit=limit)
        
    return jsonify(ok=True, results=results)
