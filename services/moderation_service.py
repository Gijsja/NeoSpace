"""
Moderation Service - Business logic for reporting and resolution.
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

def submit_report(reporter_id: int, content_type: str, content_id: str, reason: str) -> ServiceResult:
    """
    Submit a moderation report.
    """
    if content_type not in ('post', 'script', 'user'):
        return ServiceResult(success=False, error="Invalid content type", status=400)
        
    db = get_db()
    try:
        db.execute(
            "INSERT INTO reports (reporter_id, content_type, content_id, reason) VALUES (?, ?, ?, ?)",
            (reporter_id, content_type, content_id, reason)
        )
        db.commit()
    except Exception as e:
        return ServiceResult(success=False, error=str(e), status=500)
        
    return ServiceResult(success=True)


def resolve_report(
    staff_id: int, 
    report_id: int, 
    action: str, 
    note: str = ""
) -> ServiceResult:
    """
    Resolve a report (Admin/Staff only).
    """
    db = get_db()
    
    # Check if report exists
    report = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not report:
        return ServiceResult(success=False, error="Report not found", status=404)
        
    status = 'resolved'
    resolution_note = note
    
    if action == 'dismiss':
        status = 'dismissed'
    elif action in ('delete_content', 'ban_user'):
        status = 'resolved'
        
        # --- EXECUTE ACTION ---
        if action == 'delete_content':
            if report['content_type'] == 'post':
                try:
                    pid = int(report['content_id'])
                    # Admin force delete
                    db.execute("DELETE FROM profile_posts WHERE id = ?", (pid,))
                except ValueError:
                    pass
            elif report['content_type'] == 'script':
                try:
                    sid = int(report['content_id'])
                    db.execute("DELETE FROM scripts WHERE id = ?", (sid,))
                    db.execute("DELETE FROM profile_scripts WHERE script_id = ?", (sid,))
                except ValueError:
                    pass
                    
        elif action == 'ban_user':
            target_user_id = None
            if report['content_type'] == 'user':
                try:
                    target_user_id = int(report['content_id'])
                except ValueError:
                    pass
            elif report['content_type'] == 'post':
                # Try to find author via profile
                post_row = db.execute(
                    "SELECT user_id FROM profiles WHERE id = (SELECT profile_id FROM profile_posts WHERE id = ?)", 
                    (report['content_id'],)
                ).fetchone()
                if post_row:
                    target_user_id = post_row['user_id']
            elif report['content_type'] == 'script':
                script_row = db.execute("SELECT user_id FROM scripts WHERE id = ?", (report['content_id'],)).fetchone()
                if script_row:
                    target_user_id = script_row['user_id']
            
            if target_user_id:
                db.execute("UPDATE users SET is_banned = 1 WHERE id = ?", (target_user_id,))
                resolution_note += f" [Action: User {target_user_id} Banned]"
    else:
        return ServiceResult(success=False, error="Invalid action", status=400)
        
    # Update report status
    try:
        db.execute(
            """UPDATE reports 
               SET status = ?, resolution_note = ?, resolved_by = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?""",
            (status, resolution_note, staff_id, report_id)
        )
        db.commit()
    except Exception as e:
        return ServiceResult(success=False, error=str(e), status=500)
        
    return ServiceResult(success=True)
