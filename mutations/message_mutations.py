
from flask import request, g, jsonify
from db import get_db, db_retry
from utils.sanitize import clean_html
import sqlite3



from core.security import limiter
from core.permissions import check_ownership
from core.responses import success_response, error_response
from core.validators import validate_content_length
import msgspec
from core.schemas import SendMessageRequest, UpdateMessageRequest, DeleteMessageRequest

@limiter.limit("60/minute")
def send_message():
    """
    Send a chat message with msgspec-based parsing.
    Automatic validation + 10-80x faster than request.json.
    """
    db = get_db()
    
    try:
        # Fast msgspec decoding with automatic validation
        req = msgspec.json.decode(request.get_data(), type=SendMessageRequest)
        
        # Semantic validation
        v_err = validate_content_length(req.content, 10000)
        if v_err: return error_response(v_err)
        
        content = clean_html(req.content)
    except msgspec.ValidationError as e:
        return error_response(f"Invalid request: {e}")
    
    username = g.user['username'] if g.user else 'anonymous'
    
    def do_insert():
        row = db.execute(
            "INSERT INTO messages(user,content) VALUES (?,?) RETURNING id", 
            (username, content)
        ).fetchone()
        db.commit()
        return row
    
    try:
        row = db_retry(do_insert)
        return success_response(id=row['id'])
    except sqlite3.OperationalError:
        return error_response("Database busy, please retry", 503)


@limiter.limit("20/minute")
def edit_message():
    """Edit message content."""
    db = get_db()
    
    try:
        req = msgspec.json.decode(request.get_data(), type=UpdateMessageRequest)
        
        # Semantic validation
        v_err = validate_content_length(req.content, 2000)
        if v_err: return error_response(v_err)
        
        content = clean_html(req.content)
    except msgspec.ValidationError as e:
        return error_response(f"Invalid request: {e}")
    
    # Verify message exists and belongs to user
    row = db.execute("SELECT user FROM messages WHERE id=? AND deleted_at IS NULL", (req.id,)).fetchone()
    if not row:
        return error_response("Message not found", 404)
        
    username = g.user['username'] if g.user else None
    
    if not check_ownership(row["user"], username):
        return error_response("Not authorized", 403)
    
    def do_update():
        db.execute(
            "UPDATE messages SET content=?, edited_at=datetime('now') WHERE id=?",
            (content, req.id)
        )
        db.commit()
    
    try:
        db_retry(do_update)
        return success_response(id=req.id)
    except sqlite3.OperationalError:
        return error_response("Database busy, please retry", 503)


@limiter.limit("20/minute")
def delete_message():
    """Soft-delete a message."""
    db = get_db()
    
    try:
        req = msgspec.json.decode(request.get_data(), type=DeleteMessageRequest)
    except msgspec.ValidationError as e:
        return error_response(f"Invalid request: {e}")
    
    # Verify message exists and belongs to user
    row = db.execute("SELECT user FROM messages WHERE id=? AND deleted_at IS NULL", (req.id,)).fetchone()
    if not row:
        return error_response("Message not found", 404)
        
    username = g.user['username'] if g.user else None
    
    if not check_ownership(row["user"], username):
        return error_response("Not authorized", 403)
    
    def do_delete():
        db.execute(
            "UPDATE messages SET deleted_at=datetime('now') WHERE id=?",
            (req.id,)
        )
        db.commit()
    
    try:
        db_retry(do_delete)
        return success_response(id=req.id)
    except sqlite3.OperationalError:
        return error_response("Database busy, please retry", 503)

