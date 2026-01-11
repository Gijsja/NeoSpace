
import pytest
from services import script_service
from db import get_db

@pytest.fixture
def user_id(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('coder', 'hash')")
        u_id = db.execute("SELECT id FROM users WHERE username = 'coder'").fetchone()[0]
        db.commit()
        return u_id

def test_save_script_create(app, user_id):
    with app.app_context():
        res = script_service.save_script(user_id, "Cool Script", "console.log('hi')", "p5", True)
        assert res.success is True
        assert res.data["message"] == "Created"
        assert res.data["id"] is not None

def test_save_script_update(app, user_id):
    with app.app_context():
        res = script_service.save_script(user_id, "Old", "old content", "p5", True)
        sid = res.data["id"]
        
        res_upd = script_service.save_script(user_id, "New", "new content", "p5", True, script_id=sid)
        assert res_upd.success is True
        assert res_upd.data["message"] == "Updated"
        
        # Verify
        db = get_db()
        row = db.execute("SELECT title, content FROM scripts WHERE id=?", (sid,)).fetchone()
        assert row["title"] == "New"
        assert row["content"] == "new content"

def test_save_script_fork(app, user_id):
    with app.app_context():
        res = script_service.save_script(user_id, "Parent", "parent content", "p5", True)
        pid = res.data["id"]
        
        res_fork = script_service.save_script(user_id, "Fork", "forked content", "p5", True, parent_id=pid)
        assert res_fork.success is True
        assert res_fork.data["parent_id"] == pid
        assert res_fork.data["root_id"] == pid

def test_list_user_scripts(app, user_id):
    with app.app_context():
        script_service.save_script(user_id, "s1", "c1", "p5", True)
        script_service.save_script(user_id, "s2", "c2", "p5", True)
        
        res = script_service.list_user_scripts(user_id)
        assert res.success is True
        assert len(res.data["scripts"]) == 2

def test_get_script_by_id(app, user_id):
    with app.app_context():
        res = script_service.save_script(user_id, "Public", "...", "p5", True)
        pub_id = res.data["id"]
        
        res_priv = script_service.save_script(user_id, "Private", "...", "p5", False)
        priv_id = res_priv.data["id"]
        
        # Public
        assert script_service.get_script_by_id(pub_id).success is True
        
        # Private (as owner)
        assert script_service.get_script_by_id(priv_id, user_id).success is True
        
        # Private (as guest)
        assert script_service.get_script_by_id(priv_id).success is False
        assert script_service.get_script_by_id(priv_id).status == 403

def test_delete_script(app, user_id):
    with app.app_context():
        res = script_service.save_script(user_id, "Short Lived", "...", "p5", True)
        sid = res.data["id"]
        
        # Unauthorized
        assert script_service.delete_script(999, sid).success is False
        
        # Authorized
        assert script_service.delete_script(user_id, sid).success is True
        
        # Verify
        db = get_db()
        assert db.execute("SELECT 1 FROM scripts WHERE id=?", (sid,)).fetchone() is None
