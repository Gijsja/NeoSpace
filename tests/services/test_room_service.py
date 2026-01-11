
import pytest
from services.room_service import create_room_logic, list_all_rooms, get_room_by_name

class TestRoomService:
    def setup_method(self):
        """Run before each test method to create a user."""
        from db import get_db
        db = get_db()
        db.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'testuser', 'pass')")
        db.commit()

    def test_create_room_logic_success(self, app):
        with app.app_context():
            self.setup_method()
            result = create_room_logic(user_id=1, name="test-room", description="A test room")
            assert result.success is True, f"Failed: {result.error}"
            assert result.data["room"]["name"] == "test-room"

    def test_create_room_invalid_name(self, app):
        with app.app_context():
            # No user needed for validation failure, but good practice
            self.setup_method()
            result = create_room_logic(user_id=1, name="a") # Too short
            assert result.success is False
            assert "2-32 characters" in result.error

    def test_create_room_duplicate(self, app):
        with app.app_context():
            self.setup_method()
            create_room_logic(user_id=1, name="dup-room")
            result = create_room_logic(user_id=1, name="dup-room")
            assert result.success is False
            assert result.status == 409

    def test_list_and_get_rooms(self, app):
        with app.app_context():
            self.setup_method()
            create_room_logic(user_id=1, name="room-a")
            rooms = list_all_rooms()
            assert len(rooms) >= 1
            
            room = get_room_by_name("room-a")
            assert room is not None
            assert room["name"] == "room-a"
