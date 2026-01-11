
"""
Room Service - services/room_service.py

Business logic for managing chat rooms.
"""
from typing import List, Optional, Dict, Any
from db import get_db, execute_with_retry
from core.types import ServiceResult

def create_room_logic(user_id: int, name: str, description: str = "") -> ServiceResult:
    """
    Create a new chat room.
    """
    # 1. Validation
    name_clean = name.lower().strip().replace(" ", "-")
    
    if len(name_clean) < 2 or len(name_clean) > 32:
        return ServiceResult(success=False, error="Room name must be 2-32 characters", status=400)
    
    if not name_clean.replace("-", "").replace("_", "").isalnum():
        return ServiceResult(success=False, error="Room name can only contain letters, numbers, hyphens, underscores", status=400)
    
    # 2. DB Interaction
    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO rooms (name, description, room_type, is_default, created_by) 
               VALUES (?, ?, 'text', 1, ?)""",
            (name_clean, description, user_id)
        )
        db.commit()
        room_id = cursor.lastrowid
        
        return ServiceResult(success=True, data={
            "room": {
                "id": room_id,
                "name": name_clean,
                "description": description,
                "room_type": "text"
            }
        })
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            return ServiceResult(success=False, error="Room already exists", status=409)
        # Log error here in a real app
        return ServiceResult(success=False, error="Failed to create room", status=500)

def list_all_rooms() -> List[Dict[str, Any]]:
    """
    List all default rooms.
    """
    query = """
        SELECT id, name, description, room_type, is_default
        FROM rooms
        WHERE is_default = 1
        ORDER BY 
            CASE WHEN name = 'general' THEN 0
                 WHEN name = 'announcements' THEN 1
                 ELSE 2 END,
            name
    """
    rows = execute_with_retry(query, fetchall=True)
    
    return [dict(row) for row in rows] if rows else []

def get_room_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a room by name.
    """
    query = "SELECT id, name, description, room_type FROM rooms WHERE name = ?"
    row = execute_with_retry(query, (name,), fetchone=True)
    return dict(row) if row else None
