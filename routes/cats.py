"""
Cat Companion Routes - routes/cats.py

API endpoints for cat companion system.
"""

from flask import Blueprint, jsonify, request
from services.cat_service import (
    get_cat_personalities,
    trigger_cat_response,
    seed_cat_personalities,
    seed_cat_bot_users
)

cats_bp = Blueprint("cats", __name__, url_prefix="/cats")


@cats_bp.route("/", methods=["GET"])
def list_cats():
    """Get all cat personalities."""
    cats = get_cat_personalities()
    return jsonify({"cats": cats})


@cats_bp.route("/speak", methods=["POST"])
def speak():
    """
    Trigger a cat response for an event.
    
    POST body: {"event": "login_success", "mode": "cute"}
    Returns: {"cat": "beans", "avatar": "/static/...", "line": "yay! welcome."}
    """
    data = request.get_json() or {}
    event = data.get("event", "idle")
    mode = data.get("mode", "cute")
    
    response = trigger_cat_response(event, mode)
    return jsonify(response)


@cats_bp.route("/seed", methods=["POST"])
def seed():
    """
    Seed cat personalities and bot users (admin only in production).
    """
    seed_cat_personalities()
    seed_cat_bot_users()
    return jsonify({"status": "ok", "message": "10 cats seeded successfully"})
