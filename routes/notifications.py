"""
Sprint #15: Live Wire — Notification Routes

API endpoints for fetching and managing notifications.
"""

from flask import Blueprint, jsonify, g, request, render_template
from auth import login_required
from queries.notifications import get_unread, get_unread_count, get_all
from mutations.notifications import mark_read, mark_all_read, delete_notification

bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@bp.route("/center")
@login_required
def notification_center():
    return render_template("notifications.html")


@bp.route("/")
@login_required
def get_notifications():
    """Get user's notifications."""
    include_read = request.args.get("include_read", "false").lower() == "true"
    
    if include_read:
        notifications = get_all(g.user["id"])
    else:
        notifications = get_unread(g.user["id"])
    
    return jsonify(ok=True, notifications=notifications)


@bp.route("/unread-count")
@login_required
def get_count():
    """Get unread notification count for badge."""
    count = get_unread_count(g.user["id"])
    return jsonify(ok=True, count=count)


@bp.route("/mark-read", methods=["POST"])
@login_required
def mark_one_read():
    """Mark a notification as read."""
    try:
        import msgspec
        from msgspec_models import MarkNotificationReadRequest
        req = msgspec.json.decode(request.get_data(), type=MarkNotificationReadRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    success = mark_read(req.notification_id, g.user["id"])
    return jsonify(ok=success)


@bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all():
    """Mark all notifications as read."""
    count = mark_all_read(g.user["id"])
    return jsonify(ok=True, marked=count)


@bp.route("/delete", methods=["POST"])
@login_required
def delete():
    """Delete a notification."""
    try:
        import msgspec
        from msgspec_models import DeleteNotificationRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteNotificationRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    success = delete_notification(req.notification_id, g.user["id"])
    return jsonify(ok=success)
