"""
Moderation mutations.
Delegates to moderation_service.
"""

from flask import g, jsonify, request
import msgspec
from services import moderation_service

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
        data = msgspec.json.decode(request.get_data(), type=SubmitReportRequest)
    except msgspec.ValidationError as e:
        return jsonify({"error": str(e)}), 400
        
    result = moderation_service.submit_report(g.user['id'], data.content_type, data.content_id, data.reason)
    
    if not result.success:
        return jsonify({"error": result.error}), result.status
    
    return jsonify({"success": True})

def resolve_report():
    if not g.user:
        return jsonify({"error": "Unauthorized"}), 401
        
    # Check if user is staff
    if not g.user.get('is_staff'):
        return jsonify({"error": "Forbidden"}), 403
        
    try:
        data = msgspec.json.decode(request.get_data(), type=ResolveReportRequest)
    except msgspec.ValidationError as e:
        return jsonify({"error": str(e)}), 400
        
    result = moderation_service.resolve_report(g.user['id'], data.report_id, data.action, data.note)
    
    if not result.success:
        return jsonify({"error": result.error}), result.status
        
    return jsonify({"success": True})

