"""
Sprint #14: Social Graph — Friends Routes

API endpoints for following/unfollowing and Top 8 management.
"""

from flask import Blueprint, jsonify, request, g
from auth import login_required
from mutations.friends import follow, unfollow, set_top8
from queries.friends import get_top8, get_followers, get_following, get_follower_count, get_following_count, is_following

bp = Blueprint('friends', __name__, url_prefix='/friends')


# Follow/Unfollow
bp.add_url_rule("/follow", "follow", login_required(follow), methods=["POST"])
bp.add_url_rule("/unfollow", "unfollow", login_required(unfollow), methods=["POST"])
bp.add_url_rule("/top8", "set_top8", login_required(set_top8), methods=["POST"])


@bp.route("/top8/<int:user_id>")
def get_user_top8(user_id):
    """Get a user's Top 8."""
    top8 = get_top8(user_id)
    return jsonify(ok=True, top8=top8)


@bp.route("/followers/<int:user_id>")
def get_user_followers(user_id):
    """Get a user's followers."""
    followers = get_followers(user_id)
    count = get_follower_count(user_id)
    return jsonify(ok=True, followers=followers, count=count)


@bp.route("/following/<int:user_id>")
def get_user_following(user_id):
    """Get who a user follows."""
    following = get_following(user_id)
    count = get_following_count(user_id)
    return jsonify(ok=True, following=following, count=count)


@bp.route("/status/<int:user_id>")
@login_required
def check_follow_status(user_id):
    """Check if current user follows target user."""
    if g.user is None:
        return jsonify(is_following=False)
    
    following = is_following(g.user["id"], user_id)
    return jsonify(is_following=following)
