
import pytest
from services import wall_service
from db import get_db

@pytest.fixture
def user_with_profile(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('wallowner', 'hash')")
        u_id = db.execute("SELECT id FROM users WHERE username = 'wallowner'").fetchone()[0]
        db.execute("INSERT INTO profiles (user_id, display_name) VALUES (?, 'Wall Owner')", (u_id,))
        db.commit()
        
        p_id = db.execute("SELECT id FROM profiles WHERE user_id = ?", (u_id,)).fetchone()[0]
        return {'user_id': u_id, 'profile_id': p_id}

def test_add_post_success(app, user_with_profile):
    with app.app_context():
        res = wall_service.add_post(
            user_with_profile['user_id'], 
            'text', 
            {'text': 'Hello world'}, 
            {'color': 'red'}
        )
        assert res.success is True
        assert res.data["id"] is not None

def test_add_post_invalid_type(app, user_with_profile):
    with app.app_context():
        res = wall_service.add_post(
            user_with_profile['user_id'], 
            'invalid_type', 
            {}, 
            {}
        )
        assert res.success is False
        assert res.status == 400

def test_get_posts_for_profile(app, user_with_profile):
    with app.app_context():
        wall_service.add_post(user_with_profile['user_id'], 'text', {'text': 'P1'}, {})
        wall_service.add_post(user_with_profile['user_id'], 'text', {'text': 'P2'}, {})
        
        posts = wall_service.get_posts_for_profile(user_with_profile['profile_id'])
        assert len(posts) == 2
        texts = [p["content"]["text"] for p in posts]
        assert "P1" in texts
        assert "P2" in texts

def test_update_post(app, user_with_profile):
    with app.app_context():
        res = wall_service.add_post(user_with_profile['user_id'], 'text', {'text': 'Old'}, {})
        pid = res.data["id"]
        
        # Unauthorized update
        res_fail = wall_service.update_post(999, pid, content={'text': 'New'})
        assert res_fail.success is False
        assert res_fail.status == 403
        
        # Authorized update
        res_ok = wall_service.update_post(user_with_profile['user_id'], pid, content={'text': 'New'})
        assert res_ok.success is True
        
        # Verify
        posts = wall_service.get_posts_for_profile(user_with_profile['profile_id'])
        assert posts[0]["content"]["text"] == "New"

def test_delete_post(app, user_with_profile):
    with app.app_context():
        res = wall_service.add_post(user_with_profile['user_id'], 'text', {'text': 'Gone'}, {})
        pid = res.data["id"]
        
        wall_service.delete_post(user_with_profile['user_id'], pid)
        
        posts = wall_service.get_posts_for_profile(user_with_profile['profile_id'])
        assert len(posts) == 0

def test_reorder_posts(app, user_with_profile):
    with app.app_context():
        p1 = wall_service.add_post(user_with_profile['user_id'], 'text', {'text': 'First'}, {}).data["id"]
        p2 = wall_service.add_post(user_with_profile['user_id'], 'text', {'text': 'Second'}, {}).data["id"]
        
        # Initial order (DESC created_at): P2, P1
        # Reorder to P1, P2
        wall_service.reorder_posts(user_with_profile['user_id'], [p1, p2])
        
        posts = wall_service.get_posts_for_profile(user_with_profile['profile_id'])
        assert posts[0]["id"] == p1
        assert posts[1]["id"] == p2
