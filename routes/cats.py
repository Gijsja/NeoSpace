from flask import Blueprint, jsonify, request, g
from auth import login_required
from services.cats import (
    get_all_cats,
    trigger_event,
    seed_db
)

cats_bp = Blueprint("cats", __name__, url_prefix="/cats")


@cats_bp.route("/", methods=["GET"])
def list_cats():
    """Get all cat personalities."""
    cats = get_all_cats()
    return jsonify({"cats": cats})


@cats_bp.route("/speak", methods=["POST"])
@login_required
def speak():
    """
    Trigger a cat response for an event.
    
    POST body: {"event": "login_success"}
    Returns: {"cat": "beans", "state": "Playful", "sound": "purr.wav", "line": "..."}
    """
    data = request.get_json() or {}
    event = data.get("event", "idle")
    cat_name = data.get("cat", "beans") # Default
    
    # Optional: Authentication check (TODO)
    
    response = trigger_event(cat_name, event, user_id=g.user['id'] if g.user else None)
    return jsonify(response)


@cats_bp.route("/seed", methods=["POST"])
@login_required
def seed():
    """
    Seed cat personalities (internal use).
    """
    # seed_db() needs implementation in __init__ or store if we want to call it here
    # For now, we rely on the manual scripts run earlier
    return jsonify({"status": "ok", "message": "Seeding handled manually via scripts."})
