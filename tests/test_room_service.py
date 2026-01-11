
import pytest
from services import room_service
from db import get_db

@pytest.fixture
def user_id(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('testuser', 'hash')")
        u_id = db.execute("SELECT id FROM users WHERE username = 'testuser'").fetchone()[0]
        db.commit()
        return u_id

def test_create_room_success(app, user_id):
    with app.app_context():
        res = room_service.create_room_logic(user_id, "Neo Room", "A cool room")
        assert res.success is True
        assert res.data["room"]["name"] == "neo-room"
        
        # Verify in DB
        db = get_db()
        row = db.execute("SELECT * FROM rooms WHERE name = 'neo-room'").fetchone()
        assert row is not None

def test_create_room_invalid_name(app, user_id):
    with app.app_context():
        res = room_service.create_room_logic(user_id, "a") # Too short
        assert res.success is False
        assert res.status == 400
        
        res = room_service.create_room_logic(user_id, "invalid@name")
        assert res.success is False

def test_create_room_duplicate(app, user_id):
    with app.app_context():
        room_service.create_room_logic(user_id, "general")
        res = room_service.create_room_logic(user_id, "general")
        assert res.success is False
        assert res.status == 409

def test_list_all_rooms(app, user_id):
    with app.app_context():
        room_service.create_room_logic(user_id, "general")
        room_service.create_room_logic(user_id, "announcements")
        room_service.create_room_logic(user_id, "chat")
        
        rooms = room_service.list_all_rooms()
        # 'general' and 'announcements' should be first
        assert rooms[0]["name"] == "general"
        assert rooms[1]["name"] == "announcements"
        assert len(rooms) >= 3

def test_get_room_by_name(app, user_id):
    with app.app_context():
        room_service.create_room_logic(user_id, "find-me")
        room = room_service.get_room_by_name("find-me")
        assert room is not None
        assert room["name"] == "find-me"
        
        assert room_service.get_room_by_name("non-existent") is None
