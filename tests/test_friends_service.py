
import pytest
from services import friends_service
from db import get_db

@pytest.fixture
def users(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('f1', 'h')")
        db.execute("INSERT INTO users (username, password_hash) VALUES ('f2', 'h')")
        db.execute("INSERT INTO users (username, password_hash) VALUES ('f3', 'h')")
        u1 = db.execute("SELECT id FROM users WHERE username = 'f1'").fetchone()[0]
        u2 = db.execute("SELECT id FROM users WHERE username = 'f2'").fetchone()[0]
        u3 = db.execute("SELECT id FROM users WHERE username = 'f3'").fetchone()[0]
        db.commit()
        return [u1, u2, u3]

def test_follow_unfollow(app, users):
    u1, u2, _ = users
    with app.app_context():
        # Follow
        res = friends_service.follow_user(u1, u2)
        assert res.success is True
        assert res.data["already_following"] is False
        
        # Already following
        res_dup = friends_service.follow_user(u1, u2)
        assert res_dup.success is True
        assert res_dup.data["already_following"] is True
        
        # Unfollow
        res_un = friends_service.unfollow_user(u1, u2)
        assert res_un.success is True
        
        db = get_db()
        assert db.execute("SELECT 1 FROM friends WHERE follower_id = ? AND following_id = ?", (u1, u2)).fetchone() is None

def test_follow_self(app, users):
    u1, _, _ = users
    with app.app_context():
        res = friends_service.follow_user(u1, u1)
        assert res.success is False
        assert res.status == 400

def test_follow_not_found(app, users):
    u1, _, _ = users
    with app.app_context():
        res = friends_service.follow_user(u1, 9999)
        assert res.success is False
        assert res.status == 404

def test_set_top8(app, users):
    u1, u2, u3 = users
    with app.app_context():
        # Must follow first to be in Top 8 (due to friends table structure)
        friends_service.follow_user(u1, u2)
        friends_service.follow_user(u1, u3)
        
        res = friends_service.set_top8(u1, [u2, u3])
        assert res.success is True
        
        db = get_db()
        row2 = db.execute("SELECT top8_position FROM friends WHERE follower_id = ? AND following_id = ?", (u1, u2)).fetchone()
        row3 = db.execute("SELECT top8_position FROM friends WHERE follower_id = ? AND following_id = ?", (u1, u3)).fetchone()
        assert row2["top8_position"] == 1
        assert row3["top8_position"] == 2
        
        # Clear/Reset
        friends_service.set_top8(u1, [u3])
        row2_cleared = db.execute("SELECT top8_position FROM friends WHERE follower_id = ? AND following_id = ?", (u1, u2)).fetchone()
        assert row2_cleared["top8_position"] is None

def test_set_top8_too_many(app, users):
    with app.app_context():
        res = friends_service.set_top8(1, [1,2,3,4,5,6,7,8,9])
        assert res.success is False
        assert res.status == 400
