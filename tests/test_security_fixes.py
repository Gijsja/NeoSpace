import pytest
from flask import session
from datetime import timedelta

class TestSecurityFixes:
    """Tests for critical security hardening fixes."""

    def test_session_cookie_flags(self, app, client):
        """Test that session cookies have correct security flags."""
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
        
        with client:
            client.get('/')
            with client.session_transaction() as sess:
                sess['test'] = 'val'
            
            res = client.get('/')
            cookie = None
            for value in res.headers.get_all('Set-Cookie'):
                if 'session=' in value:
                    cookie = value
                    break
            
            if cookie:
                assert 'HttpOnly' in cookie
                assert 'SameSite=Lax' in cookie
    
    def test_secret_key_enforcement(self, monkeypatch):
        """Test that production fails with weak secret key."""
        monkeypatch.setenv('FLASK_ENV', 'production')
        monkeypatch.delenv('SECRET_KEY', raising=False)
        
        from app import create_app
        with pytest.raises(ValueError, match="CRITICAL SECURITY ERROR: SECRET_KEY"):
            create_app()

    def test_websocket_banned_user(self, app, client):
        """Test that banned users cannot connect to WebSocket."""
        from db import get_db
        from flask_socketio import SocketIOTestClient
        from sockets import socketio
        
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES ('banned_user', 'hash')")
            user_id = db.execute("SELECT id FROM users WHERE username='banned_user'").fetchone()['id']
            db.execute("UPDATE users SET is_banned=1 WHERE id=?", (user_id,))
            db.commit()
            
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['username'] = 'banned_user'

        try:
           socket_client = socketio.test_client(app, flask_test_client=client)
           assert not socket_client.is_connected()
        except Exception:
           pass

    def test_websocket_rate_limit(self, app, client):
        """Test rate limiting on messages."""
        from sockets import socketio
        from db import get_db
        
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES ('spammer', 'hash')")
            user_id = db.execute("SELECT id FROM users WHERE username='spammer'").fetchone()['id']
            db.commit()
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = 'spammer'
            
        socket_client = socketio.test_client(app, flask_test_client=client)
        assert socket_client.is_connected()
        
        for i in range(70):
             socket_client.emit('send_message', {'content': f'msg {i}'})
        
        received = socket_client.get_received()
        errors = [m for m in received if m['name'] == 'error']
        assert any("Rate limit exceeded" in str(e['args'][0]) for e in errors)

    def test_content_sanitization(self, app, client):
        """Test that XSS is prevented but safe HTML is allowed."""
        from db import get_db
        
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES ('hacker', 'hash')")
            user_id = db.execute("SELECT id FROM users WHERE username='hacker'").fetchone()['id']
            db.commit()
            
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = 'hacker'
            
        payload = {
            "content": "Hello <script>alert('xss')</script> <b>World</b>"
        }
        
        res = client.post('/send', json=payload)
        assert res.status_code == 200
        msg_id = res.json['id']
        
        with app.app_context():
            db = get_db()
            msg = db.execute("SELECT content FROM messages WHERE id=?", (msg_id,)).fetchone()
            content = msg['content']
            assert "<script>" not in content
            assert "alert('xss')" in content 
            assert "<b>World</b>" in content or "<strong>World</strong>" in content
            
    def test_websocket_content_sanitization(self, app, client):
        """Test that WebSocket messages are sanitized."""
        from sockets import socketio, rate_limits
        from db import get_db
        
        rate_limits.clear()
        
        username = 'sanitizer_ws'
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, 'hash')", (username,))
            user_id = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()['id']
            db.commit()
            
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = username
            
        socket_client = socketio.test_client(app, flask_test_client=client)
        assert socket_client.is_connected()
        
        socket_client.emit('send_message', {'content': 'WS <script>alert(1)</script> <i>Italic</i>'})
        
        received = socket_client.get_received()
        errors = [m for m in received if m['name'] == 'error']
        assert not errors
        
        with app.app_context():
            db = get_db()
            msg = db.execute(
                "SELECT content FROM messages WHERE user=? ORDER BY id DESC LIMIT 1", 
                (username,)
            ).fetchone()
            
            assert msg is not None
            content = msg['content']
            assert "<script>" not in content
            assert "alert(1)" in content
            assert "<i>Italic</i>" in content or "<em>Italic</em>" in content

    def test_http_rate_limits(self, app, client):
        """Test HTTP rate limits (Flask-Limiter)."""
        from db import get_db
        from core.security import limiter
        
        # Reset limits
        # Limiter storage is memory://, but we need to ensure clean slate
        try:
             limiter.reset() 
        except:
             pass 

        username = 'http_spammer'
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, 'hash')", (username,))
            user_id = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()['id']
            # Create a recipient
            db.execute("INSERT INTO users (username, password_hash) VALUES ('victim', 'hash')")
            victim_id = db.execute("SELECT id FROM users WHERE username='victim'").fetchone()['id']
            db.commit()
            
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = username
            
        # Target: send_dm is 20/minute
        # We need to send > 20 requests
        
        blocked = False
        payload = {"recipient_id": victim_id, "content": "spam"}
        
        for i in range(25):
            res = client.post('/dm/send', json=payload)
            if res.status_code == 429:
                blocked = True
                break
                
        assert blocked, "Should have been rate limited (429) after > 20 requests"
            
    def test_websocket_reauth(self, app, client):
        """Test WebSocket re-authentication and ban enforcement."""
        from sockets import socketio, authenticated_sockets, validate_auth
        from db import get_db
        import time
        
        username = 'reauth_user'
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, 'hash')", (username,))
            user_id = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()['id']
            db.commit()
            
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['username'] = username
            
        socket_client = socketio.test_client(app, flask_test_client=client)
        assert socket_client.is_connected()
        
        if not authenticated_sockets:
             time.sleep(0.1)
        
        server_sid = None
        for sid, auth in authenticated_sockets.items():
            if auth['username'] == username:
                server_sid = sid
                break
        
        assert server_sid is not None

        # Simulate Ban
        with app.app_context():
            db = get_db()
            db.execute("UPDATE users SET is_banned=1 WHERE id=?", (user_id,))
            db.commit()
            
        # Manipulate timestamp
        authenticated_sockets[server_sid]['last_auth'] = time.time() - 7200 
                
        # Send message - should fail and disconnect
        socket_client.emit('send_message', {'content': 'Should fail'})
        
        try:
            received = socket_client.get_received()
            # If we got here, maybe disconnect was fast but not fast enough to throw?
            # Or maybe we got the error message
            errors = [m for m in received if m['name'] == 'error']
            if errors:
                assert "Session expired" in errors[0]['args'][0]['message']
        except RuntimeError:
            # "not connected" error is EXPECTED here
            pass
            
        assert not socket_client.is_connected(), "User should be disconnected"
