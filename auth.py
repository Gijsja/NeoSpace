import functools
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_from_directory, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db, db_retry

from core.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')



@auth_bp.route('/register', methods=('POST',))
def register():
    try:
        import msgspec
        from core.schemas import RegisterRequest
        req = msgspec.json.decode(request.get_data(), type=RegisterRequest)
    except msgspec.ValidationError as e:
        return error_response(f"Invalid request: {e}")
    
    from core.validators import validate_username
    v_err = validate_username(req.username)
    if v_err: return error_response(v_err)
    
    username = req.username
    password = req.password
        
    db = get_db()
    
    # Deterministic color (simplified from frontend logic)
    hash_val = 0
    for char in username:
        hash_val = ord(char) + ((hash_val << 5) - hash_val)
    color_class = f"user-color-{abs(hash_val) % 8}"

    def do_register():
        db.execute(
            "INSERT INTO users (username, password_hash, avatar_color) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), color_class),
        )
        db.commit()

    try:
        db_retry(do_register)
    except sqlite3.IntegrityError:
        return error_response(f"User {username} is already registered.")
    except sqlite3.OperationalError:
        return error_response("Database busy, please retry", 503)

    # Auto login
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    # Create default profile for new user
    def do_create_profile():
        db.execute(
            "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
            (user['id'], username)
        )
        db.commit()
    
    try:
        db_retry(do_create_profile)
    except sqlite3.OperationalError:
        pass  # Profile creation failure is non-critical
    
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    return success_response(redirect=url_for('views.index'))

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        try:
            import msgspec
            from core.schemas import LoginRequest
            req = msgspec.json.decode(request.get_data(), type=LoginRequest)
        except msgspec.ValidationError as e:
            return error_response(f"Invalid request: {e}")
        
        username = req.username
        password = req.password
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            return error_response("Incorrect username.", 401)
        elif not check_password_hash(user['password_hash'], password):
            return error_response("Incorrect password.", 401)

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return success_response(redirect=url_for('views.index'))

    return render_template("login.html")

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/me')
def me():
    if g.user:
        return success_response(
            logged_in=True, 
            username=g.user['username'],
            avatar_color=g.user['avatar_color']
        )
    return success_response(logged_in=False)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
