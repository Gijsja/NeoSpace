
"""
Room queries/handlers for Sprint 9.
Delegates to services/room_service.py.
"""

from flask import request, g, jsonify
from services import room_service

def list_rooms():
    """
    List all available rooms.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    rooms = room_service.list_all_rooms()
    return jsonify(rooms=rooms)


def get_room_by_name(name):
    """
    Get a room by its name.
    """
    return room_service.get_room_by_name(name)


def create_room():
    """
    Create a new room.
    Requires authentication.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import CreateRoomRequest
        req = msgspec.json.decode(request.get_data(), type=CreateRoomRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    result = room_service.create_room_logic(
        user_id=g.user["id"],
        name=req.name,
        description=req.description or ""
    )
    
    if not result.success:
        return jsonify(error=result.error), result.status
        
    return jsonify(ok=True, **result.data)

