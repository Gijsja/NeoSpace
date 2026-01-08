"""
Rooms blueprint for Sprint 9.
"""

from flask import Blueprint
from queries.rooms import list_rooms, create_room

bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@bp.route('', methods=['GET'])
def get_rooms():
    """List all available rooms."""
    return list_rooms()

@bp.route('', methods=['POST'])
def post_room():
    """Create a new room."""
    return create_room()
