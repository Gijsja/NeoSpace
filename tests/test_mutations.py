
import pytest
from db import get_db


class TestSendMessage:
    """Tests for the /send endpoint."""

    def test_send_message_success(self, client, app):
        """Successfully send a message."""
        res = client.post("/send", 
            json={"content": "Hello, world!"},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_send_message_escapes_html(self, client, app):
        """Message content should be HTML-escaped."""
        client.post("/send",
            json={"content": "<script>alert('xss')</script>"},
            headers={"X-User": "alice"}
        )
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content FROM messages ORDER BY id DESC LIMIT 1").fetchone()
            assert "<script>" not in row["content"]
            assert "&lt;script&gt;" in row["content"]

    def test_send_message_anonymous_user(self, client):
        """Messages without X-User header use 'anonymous'."""
        res = client.post("/send", json={"content": "Anonymous message"})
        assert res.status_code == 200


class TestEditMessage:
    """Tests for the /edit endpoint."""

    def test_edit_message_success(self, client, app):
        """Successfully edit own message."""
        # Create message
        res = client.post("/send",
            json={"content": "Original"},
            headers={"X-User": "alice"}
        )
        msg_id = res.get_json()["id"]

        # Edit message
        res = client.post("/edit",
            json={"id": msg_id, "content": "Edited"},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

        # Verify in database
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content, edited_at FROM messages WHERE id=?", (msg_id,)).fetchone()
            assert row["content"] == "Edited"
            assert row["edited_at"] is not None

    def test_edit_message_not_owner(self, client):
        """Cannot edit another user's message."""
        # Create message as alice
        res = client.post("/send",
            json={"content": "Alice's message"},
            headers={"X-User": "alice"}
        )
        msg_id = res.get_json()["id"]

        # Try to edit as bob
        res = client.post("/edit",
            json={"id": msg_id, "content": "Hacked!"},
            headers={"X-User": "bob"}
        )
        assert res.status_code == 403
        assert res.get_json()["ok"] is False

    def test_edit_message_not_found(self, client):
        """Editing non-existent message returns 404."""
        res = client.post("/edit",
            json={"id": 999999, "content": "Ghost"},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 404

    def test_edit_message_missing_id(self, client):
        """Editing without message ID returns 400."""
        res = client.post("/edit",
            json={"content": "No ID"},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 400


class TestDeleteMessage:
    """Tests for the /delete endpoint."""

    def test_delete_message_success(self, client, app):
        """Successfully soft-delete own message."""
        # Create message
        res = client.post("/send",
            json={"content": "To be deleted"},
            headers={"X-User": "alice"}
        )
        msg_id = res.get_json()["id"]

        # Delete message
        res = client.post("/delete",
            json={"id": msg_id},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

        # Verify soft-delete in database
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT deleted_at FROM messages WHERE id=?", (msg_id,)).fetchone()
            assert row["deleted_at"] is not None

    def test_delete_message_not_owner(self, client):
        """Cannot delete another user's message."""
        # Create message as alice
        res = client.post("/send",
            json={"content": "Alice's message"},
            headers={"X-User": "alice"}
        )
        msg_id = res.get_json()["id"]

        # Try to delete as bob
        res = client.post("/delete",
            json={"id": msg_id},
            headers={"X-User": "bob"}
        )
        assert res.status_code == 403

    def test_delete_message_not_found(self, client):
        """Deleting non-existent message returns 404."""
        res = client.post("/delete",
            json={"id": 999999},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 404

    def test_delete_already_deleted(self, client):
        """Cannot delete an already deleted message."""
        # Create and delete message
        res = client.post("/send",
            json={"content": "Delete me twice"},
            headers={"X-User": "alice"}
        )
        msg_id = res.get_json()["id"]
        client.post("/delete", json={"id": msg_id}, headers={"X-User": "alice"})

        # Try to delete again
        res = client.post("/delete",
            json={"id": msg_id},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 404

    def test_cannot_edit_deleted_message(self, client):
        """Cannot edit a deleted message."""
        # Create and delete message
        res = client.post("/send",
            json={"content": "Delete then edit"},
            headers={"X-User": "alice"}
        )
        msg_id = res.get_json()["id"]
        client.post("/delete", json={"id": msg_id}, headers={"X-User": "alice"})

        # Try to edit deleted message
        res = client.post("/edit",
            json={"id": msg_id, "content": "Zombie"},
            headers={"X-User": "alice"}
        )
        assert res.status_code == 404
