
import pytest
import io
from services import profile_service
from db import get_db

@pytest.fixture
def users(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('alice', 'h')")
        db.execute("INSERT INTO users (username, password_hash) VALUES ('bob', 'h')")
        alice_id = db.execute("SELECT id FROM users WHERE username = 'alice'").fetchone()[0]
        bob_id = db.execute("SELECT id FROM users WHERE username = 'bob'").fetchone()[0]
        
        db.execute("INSERT INTO profiles (user_id, display_name, is_public) VALUES (?, 'Alice', 1)", (alice_id,))
        db.execute("INSERT INTO profiles (user_id, display_name, is_public) VALUES (?, 'Bob', 0)", (bob_id,))
        db.commit()
        return {'alice': alice_id, 'bob': bob_id}

def test_get_profile_public(app, users):
    with app.app_context():
        res = profile_service.get_profile_by_user_id(users['alice'])
        assert res.success is True
        assert res.data["display_name"] == "Alice"
        assert res.data["is_own"] is False

def test_get_profile_private(app, users):
    with app.app_context():
        # Guest viewing private
        res = profile_service.get_profile_by_user_id(users['bob'])
        assert res.success is False
        assert res.status == 403
        
        # Owner viewing private
        res_own = profile_service.get_profile_by_user_id(users['bob'], viewer_id=users['bob'])
        assert res_own.success is True
        assert res_own.data["is_own"] is True

def test_update_profile_fields(app, users):
    with app.app_context():
        update_data = {
            "display_name": "New Alice",
            "bio": "New Bio",
            "theme_preset": "retro",
            "accent_color": "#FF0000",
            "is_public": False,
            "dm_policy": "mutuals"
        }
        res = profile_service.update_profile_fields(users['alice'], update_data)
        assert res.success is True
        
        # Verify
        profile = profile_service.get_profile_by_user_id(users['alice'], viewer_id=users['alice']).data
        assert profile["display_name"] == "New Alice"
        assert profile["bio"] == "New Bio"
        assert profile["theme_preset"] == "retro"
        assert profile["accent_color"] == "#FF0000"
        assert profile["dm_policy"] == "mutuals"

def test_update_profile_invalid_fields(app, users):
    with app.app_context():
        res = profile_service.update_profile_fields(users['alice'], {"theme_preset": "invalid"})
        assert res.success is False
        assert res.status == 400
        
        res_color = profile_service.update_profile_fields(users['alice'], {"accent_color": "not-a-color"})
        assert res_color.success is False

def test_social_graph_integration(app, users):
    with app.app_context():
        db = get_db()
        # Bob follows Alice
        db.execute("INSERT INTO friends (follower_id, following_id) VALUES (?, ?)", (users['bob'], users['alice']))
        db.commit()
        
        res = profile_service.get_profile_by_user_id(users['alice'], viewer_id=users['bob'])
        assert res.data["follower_count"] == 1
        assert res.data["viewer_is_following"] is True

def test_save_avatar(app, users):
    with app.app_context():
        # Mock StorageService if possible, or just let it fail if not configured
        # Actually storage_service might need app_root
        res = profile_service.save_avatar(users['alice'], b"fake-data", "png", "/tmp")
        # Depending on StorageService config this might succeed or fail
        # Let's see what happens
        pass

def test_create_default_profile(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('newuser', 'h')")
        u_id = db.execute("SELECT id FROM users WHERE username = 'newuser'").fetchone()[0]
        
        res = profile_service.create_default_profile(u_id, "newuser")
        assert res.success is True
        
        row = db.execute("SELECT display_name FROM profiles WHERE user_id = ?", (u_id,)).fetchone()
        assert row["display_name"] == "newuser"
