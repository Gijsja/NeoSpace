"""
Song Service - Business logic for song projects.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from db import get_db

@dataclass
class ServiceResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: int = 200

def save_song(
    user_id: int,
    title: str,
    data_json: str,
    is_public: bool,
    song_id: Optional[int] = None
) -> ServiceResult:
    """
    Save (create or update) a song.
    """
    db = get_db()
    
    if song_id:
        # Update
        row = db.execute("SELECT user_id FROM songs WHERE id=?", (song_id,)).fetchone()
        if not row:
            return ServiceResult(success=False, error="Song not found", status=404)
        if row['user_id'] != user_id:
            return ServiceResult(success=False, error="Not authorized", status=403)
            
        try:
            db.execute(
                """UPDATE songs 
                   SET title=?, data_json=?, is_public=?, updated_at=datetime('now') 
                   WHERE id=?""",
                (title, data_json, is_public, song_id)
            )
            db.commit()
        except Exception as e:
             return ServiceResult(success=False, error=str(e), status=500)
             
        return ServiceResult(success=True, data={"id": song_id, "message": "Saved"})
    else:
        # Create
        try:
            cur = db.execute(
                """INSERT INTO songs (user_id, title, data_json, is_public) 
                   VALUES (?, ?, ?, ?) 
                   RETURNING id""",
                (user_id, title, data_json, is_public)
            )
            row = cur.fetchone()
            db.commit()
            return ServiceResult(success=True, data={"id": row['id'], "message": "Created"})
        except Exception as e:
            return ServiceResult(success=False, error=str(e), status=500)

def delete_song(user_id: int, song_id: int) -> ServiceResult:
    """
    Delete a song.
    """
    db = get_db()
    
    row = db.execute("SELECT user_id FROM songs WHERE id=?", (song_id,)).fetchone()
    if not row:
        return ServiceResult(success=False, error="Not found", status=404)
    if row['user_id'] != user_id:
        return ServiceResult(success=False, error="Not authorized", status=403)
        
    db.execute("DELETE FROM songs WHERE id=?", (song_id,))
    db.commit()
    return ServiceResult(success=True, data={"deleted": song_id})
