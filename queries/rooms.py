"""
Room queries for Sprint 9.
Handles room listing and management.
"""

from flask import request, g, jsonify
from db import get_db


def list_rooms():
    """
    List all available rooms.
    Returns rooms marked as default, plus any the user has access to.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    db = get_db()
    
    rows = db.execute("""
        SELECT id, name, description, room_type, is_default
        FROM rooms
        WHERE is_default = 1
        ORDER BY 
            CASE WHEN name = 'general' THEN 0
                 WHEN name = 'announcements' THEN 1
                 ELSE 2 END,
            name
    """).fetchall()
    
    rooms = []
    for row in rows:
        rooms.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "room_type": row["room_type"],
            "is_default": bool(row["is_default"])
        })
    
    return jsonify(rooms=rooms)


def get_room_by_name(name):
    """
    Get a room by its name.
    Returns None if not found.
    """
    db = get_db()
    row = db.execute(
        "SELECT id, name, description, room_type FROM rooms WHERE name = ?",
        (name,)
    ).fetchone()
    
    if not row:
        return None
    
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "room_type": row["room_type"]
    }


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
    
    name = req.name.lower().strip().replace(" ", "-")
    description = req.description or ""
    room_type = "text"  # Default
    
    # Validate name
    if len(name) < 2 or len(name) > 32:
        return jsonify(error="Room name must be 2-32 characters"), 400
    
    if not name.replace("-", "").replace("_", "").isalnum():
        return jsonify(error="Room name can only contain letters, numbers, hyphens, underscores"), 400
    
    db = get_db()
    
    try:
        cursor = db.execute(
            """INSERT INTO rooms (name, description, room_type, is_default, created_by) 
               VALUES (?, ?, ?, 1, ?)""",
            (name, description, room_type, g.user["id"])
        )
        room_id = cursor.lastrowid
        
        return jsonify(
            ok=True,
            room={
                "id": room_id,
                "name": name,
                "description": description,
                "room_type": room_type
            }
        )
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            return jsonify(error="Room already exists"), 409
        return jsonify(error="Failed to create room"), 500
