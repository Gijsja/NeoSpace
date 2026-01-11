
import pytest
import io
from services import sticker_service
from db import get_db

@pytest.fixture
def setup_data(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('owner', 'h')")
        db.execute("INSERT INTO users (username, password_hash) VALUES ('placer', 'h')")
        owner_id = db.execute("SELECT id FROM users WHERE username = 'owner'").fetchone()[0]
        placer_id = db.execute("SELECT id FROM users WHERE username = 'placer'").fetchone()[0]
        
        db.execute("INSERT INTO profiles (user_id, display_name) VALUES (?, 'Owner')", (owner_id,))
        p_id = db.execute("SELECT id FROM profiles WHERE user_id = ?", (owner_id,)).fetchone()[0]
        db.commit()
        return {'owner_id': owner_id, 'placer_id': placer_id, 'profile_id': p_id}

def test_add_text_sticker(app, setup_data):
    with app.app_context():
        res = sticker_service.add_sticker(
            setup_data['placer_id'],
            setup_data['profile_id'],
            'text',
            text_content="Nice wall!"
        )
        assert res.success is True
        assert res.data["text_content"] == "Nice wall!"

def test_add_image_sticker_invalid_file(app, setup_data):
    with app.app_context():
        from werkzeug.datastructures import FileStorage
        file = FileStorage(io.BytesIO(b"data"), filename="test.exe")
        res = sticker_service.add_sticker(
            setup_data['placer_id'],
            setup_data['profile_id'],
            'image',
            image_file=file
        )
        assert res.success is False
        assert res.status == 400

def test_update_sticker_success(app, setup_data):
    with app.app_context():
        res = sticker_service.add_sticker(
            setup_data['placer_id'],
            setup_data['profile_id'],
            'text',
            text_content="Move me"
        )
        sid = res.data["id"]
        
        res_upd = sticker_service.update_sticker(
            setup_data['placer_id'],
            sid,
            {'x': 100, 'y': 200, 'rotation': 45}
        )
        assert res_upd.success is True
        
        # Verify
        db = get_db()
        row = db.execute("SELECT x_pos, y_pos, rotation FROM profile_stickers WHERE id=?", (sid,)).fetchone()
        assert row["x_pos"] == 100
        assert row["y_pos"] == 200
        assert row["rotation"] == 45

def test_update_sticker_unauthorized(app, setup_data):
    with app.app_context():
        res = sticker_service.add_sticker(
            setup_data['placer_id'],
            setup_data['profile_id'],
            'text',
            text_content="Private"
        )
        sid = res.data["id"]
        
        # Someone else tries to update
        res_fail = sticker_service.update_sticker(999, sid, {'x': 0})
        assert res_fail.success is False
        assert res_fail.status == 403

def test_delete_sticker_success(app, setup_data):
    with app.app_context():
        res = sticker_service.add_sticker(
            setup_data['placer_id'],
            setup_data['profile_id'],
            'text',
            text_content="Delete me"
        )
        sid = res.data["id"]
        
        # Delete as profile owner
        res_del = sticker_service.delete_sticker(setup_data['owner_id'], sid)
        assert res_del.success is True
        
        db = get_db()
        assert db.execute("SELECT 1 FROM profile_stickers WHERE id=?", (sid,)).fetchone() is None

def test_delete_sticker_not_found(app):
    with app.app_context():
        res = sticker_service.delete_sticker(1, "non-existent")
        assert res.success is False
        assert res.status == 404
