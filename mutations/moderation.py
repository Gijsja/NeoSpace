from flask import g, jsonify
import msgspec
from db import get_db

class SubmitReportRequest(msgspec.Struct):
    content_type: str
    content_id: str
    reason: str

class ResolveReportRequest(msgspec.Struct):
    report_id: int
    action: str  # 'dismiss', 'delete_content', 'ban_user'
    note: str = ""

def submit_report():
    if not g.user:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        data = msgspec.json.decode(g.request.get_data(), type=SubmitReportRequest)
    except msgspec.ValidationError as e:
        return jsonify({"error": str(e)}), 400
        
    if data.content_type not in ('post', 'script', 'user'):
        return jsonify({"error": "Invalid content type"}), 400
        
    db = get_db()
    db.execute(
        "INSERT INTO reports (reporter_id, content_type, content_id, reason) VALUES (?, ?, ?, ?)",
        (g.user['id'], data.content_type, data.content_id, data.reason)
    )
    db.commit()
    
    return jsonify({"success": True})

def resolve_report():
    if not g.user:
        return jsonify({"error": "Unauthorized"}), 401
        
    # Check if user is staff
    # Note: g.user is a row factory or dict-like, assuming is_staff is available
    if not g.user.get('is_staff'):
        return jsonify({"error": "Forbidden"}), 403
        
    try:
        data = msgspec.json.decode(g.request.get_data(), type=ResolveReportRequest)
    except msgspec.ValidationError as e:
        return jsonify({"error": str(e)}), 400
        
    db = get_db()
    
    # Get report
    report = db.execute("SELECT * FROM reports WHERE id = ?", (data.report_id,)).fetchone()
    if not report:
        return jsonify({"error": "Report not found"}), 404
        
    if data.action == 'dismiss':
        status = 'dismissed'
    elif data.action in ('delete_content', 'ban_user'):
        status = 'resolved'
        
        if data.action == 'delete_content':
            if report['content_type'] == 'post':
                from services.wall_service import delete_post
                # content_id is strings in DB but int in service, cast it
                try:
                    pid = int(report['content_id'])
                    # We don't have the post owner ID easily here to pass to delete_post
                    # which expects (user_id, post_id) for auth check.
                    # We should probably bypass check for admin or use a force_delete service method.
                    # For now, let's just do direct SQL for admin power.
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
                    
        elif data.action == 'ban_user':
            target_user_id = None
            if report['content_type'] == 'user':
                target_user_id = int(report['content_id'])
            elif report['content_type'] == 'post':
                # content_id for post is profile_post.id
                # Post doesn't store author directly if it's a profile post!
                # Wait, profile_posts are on a profile. 
                # If it's a "wall post", who is the author? 
                # Currently profile_posts doesn't track "author" distinct from "profile owner" usually?
                # Actually, `mutations/wall.py` uses `g.user['id']` to verify, but `profile_posts` table ONLY has `profile_id`.
                # Limitation: We assume the profile owner wrote the post unless it's a sticker (which has `placed_by`).
                # Wall posts (modules) are content of the *profile*.
                # So we ban the profile owner.
                post = db.execute("SELECT user_id FROM profiles WHERE id = (SELECT profile_id FROM profile_posts WHERE id = ?)", (report['content_id'],)).fetchone()
                if post:
                    target_user_id = post['user_id']
            elif report['content_type'] == 'script':
                script = db.execute("SELECT user_id FROM scripts WHERE id = ?", (report['content_id'],)).fetchone()
                if script:
                    target_user_id = script['user_id']
            
            if target_user_id:
                db.execute("UPDATE users SET is_banned = 1 WHERE id = ?", (target_user_id,))
                data.note += f" [Action: User {target_user_id} Banned]"
    
    else:
        return jsonify({"error": "Invalid action"}), 400
        
    db.execute(
        "UPDATE reports SET status = ?, resolution_note = ?, resolved_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, data.note, g.user['id'], data.report_id)
    )
    db.commit()
    
    return jsonify({"success": True})
