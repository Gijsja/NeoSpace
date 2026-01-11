"""
Direct Message mutations for Sprint 6.
Handles sending, reading, and deleting encrypted DMs.
"""

from flask import request, g, jsonify


def send_dm():
    """
    Send an encrypted direct message.
    
    Request JSON:
        recipient_id: int - ID of the recipient user
        content: str - Message content (will be encrypted)
    
    Returns:
        JSON with message ID on success
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import SendDMRequest
        req = msgspec.json.decode(request.get_data(), type=SendDMRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import dm_service
    result = dm_service.send_message(g.user["id"], req.recipient_id, req.content)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(ok=True, **result.data)


def get_conversation():
    """
    Get decrypted messages for a conversation.
    
    Query params:
        with_user: int - ID of the other user in conversation
        limit: int - Max messages to return (default 50)
        before_id: int - Pagination cursor
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    other_user_id = request.args.get("with_user", type=int)
    limit = min(request.args.get("limit", 50, type=int), 100)
    before_id = request.args.get("before_id", type=int)
    
    if not other_user_id:
        return jsonify(error="with_user parameter required"), 400
    
    from services import dm_service
    result = dm_service.get_conversation_messages(g.user["id"], other_user_id, limit, before_id)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(**result.data)


def mark_dm_read():
    """
    Mark messages as read up to a given message ID.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import MarkDMReadRequest
        req = msgspec.json.decode(request.get_data(), type=MarkDMReadRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import dm_service
    result = dm_service.mark_messages_read(g.user["id"], req.message_id)
    
    return jsonify(ok=True)


def delete_dm():
    """
    Soft-delete a DM for the current user.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    try:
        import msgspec
        from core.schemas import DeleteDMRequest
        req = msgspec.json.decode(request.get_data(), type=DeleteDMRequest)
    except msgspec.ValidationError as e:
        return jsonify(error=f"Invalid request: {e}"), 400
    
    from services import dm_service
    result = dm_service.delete_message(g.user["id"], req.message_id)
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(ok=True)


def list_conversations():
    """
    List all conversations for the current user.
    """
    if g.user is None:
        return jsonify(error="Authentication required"), 401
    
    from services import dm_service
    result = dm_service.list_user_conversations(g.user["id"])
    
    if not result.success:
        return jsonify(error=result.error), result.status
    
    return jsonify(**result.data)
