import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_from_directory, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=('POST',))
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify(error="Username and password required"), 400
        
    db = get_db()
    
    # Deterministic color (simplified from frontend logic)
    hash_val = 0
    for char in username:
        hash_val = ord(char) + ((hash_val << 5) - hash_val)
    color_class = f"user-color-{abs(hash_val) % 8}"

    try:
        db.execute(
            "INSERT INTO users (username, password_hash, avatar_color) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), color_class),
        )
        db.commit()
    except db.IntegrityError:
        return jsonify(error=f"User {username} is already registered."), 400

    # Auto login
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    # Create default profile for new user
    db.execute(
        "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
        (user['id'], username)
    )
    db.commit()
    
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    return jsonify(ok=True, redirect=url_for('index'))

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            return jsonify(error="Incorrect username."), 401
        elif not check_password_hash(user['password_hash'], password):
            return jsonify(error="Incorrect password."), 401

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify(ok=True, redirect=url_for('index'))

    return send_from_directory("ui/views", "login.html")

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/me')
def me():
    if g.user:
        return jsonify(
            logged_in=True, 
            username=g.user['username'],
            avatar_color=g.user['avatar_color']
        )
    return jsonify(logged_in=False)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
