"""
Script Service - Business logic for Codeground scripts.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from db import get_db

@dataclass
class ServiceResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: int = 200

def save_script(
    user_id: int,
    title: str,
    content: str,
    script_type: str,
    is_public: bool,
    script_id: Optional[int] = None,
    parent_id: Optional[int] = None
) -> ServiceResult:
    """
    Create or update a script.
    """
    db = get_db()
    
    if script_id:
        # Update
        row = db.execute("SELECT user_id FROM scripts WHERE id=?", (script_id,)).fetchone()
        if not row:
            return ServiceResult(success=False, error="Script not found", status=404)
        if row['user_id'] != user_id:
            return ServiceResult(success=False, error="Not authorized", status=403)
            
        try:
            db.execute(
                """UPDATE scripts 
                   SET title=?, content=?, script_type=?, is_public=?, updated_at=datetime('now') 
                   WHERE id=?""",
                (title, content, script_type, is_public, script_id)
            )
            db.commit()
        except Exception as e:
            return ServiceResult(success=False, error=str(e), status=500)
            
        return ServiceResult(success=True, data={"id": script_id, "message": "Updated"})
        
    else:
        # Create
        root_id = None
        if parent_id:
            parent = db.execute("SELECT id, root_id FROM scripts WHERE id=?", (parent_id,)).fetchone()
            if parent:
                root_id = parent['root_id'] if parent['root_id'] else parent['id']
            else:
                parent_id = None # Ignore invalid parent

        try:
            row = db.execute(
                """INSERT INTO scripts (user_id, title, content, script_type, is_public, parent_id, root_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?) 
                   RETURNING id""",
                (user_id, title, content, script_type, is_public, parent_id, root_id)
            ).fetchone()
            db.commit()
            return ServiceResult(success=True, data={
                "id": row['id'], 
                "message": "Created",
                "parent_id": parent_id,
                "root_id": root_id
            })
        except Exception as e:
            return ServiceResult(success=False, error=str(e), status=500)

def list_user_scripts(user_id: int) -> ServiceResult:
    """
    List all scripts for a user.
    """
    db = get_db()
    rows = db.execute(
        """SELECT id, title, script_type, updated_at, created_at, parent_id, root_id 
           FROM scripts 
           WHERE user_id=? 
           ORDER BY updated_at DESC, created_at DESC""",
        (user_id,)
    ).fetchall()
    
    scripts = [dict(
        id=r['id'], 
        title=r['title'], 
        script_type=r['script_type'],
        last_modified=r['updated_at'] or r['created_at'],
        parent_id=r['parent_id'],
        root_id=r['root_id']
    ) for r in rows]
    
    return ServiceResult(success=True, data={"scripts": scripts})

def get_script_by_id(script_id: int, user_id: Optional[int] = None) -> ServiceResult:
    """
    Get a script.
    """
    db = get_db()
    row = db.execute("SELECT * FROM scripts WHERE id=?", (script_id,)).fetchone()
    
    if not row:
        return ServiceResult(success=False, error="Script not found", status=404)
        
    is_owner = (user_id is not None) and (row['user_id'] == user_id)
    
    if not row['is_public'] and not is_owner:
         return ServiceResult(success=False, error="Private script", status=403)

    return ServiceResult(success=True, data={"script": dict(row)})

def delete_script(user_id: int, script_id: int) -> ServiceResult:
    """
    Delete a script.
    """
    db = get_db()
    
    row = db.execute("SELECT user_id FROM scripts WHERE id=?", (script_id,)).fetchone()
    if not row:
        return ServiceResult(success=False, error="Not found", status=404)
    if row['user_id'] != user_id:
        return ServiceResult(success=False, error="Not authorized", status=403)
        
    db.execute("DELETE FROM scripts WHERE id=?", (script_id,))
    db.commit()
    return ServiceResult(success=True, data={"deleted": script_id})
