
import pytest
from db import get_db


class TestSendMessage:
    """Tests for the /send endpoint (now requires authentication)."""

    def test_send_message_success(self, auth_client, app):
        """Successfully send a message when authenticated."""
        res = auth_client.post("/send", 
            json={"content": "Hello, world!"}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_send_message_requires_auth(self, client):
        """Unauthenticated requests are rejected."""
        res = client.post("/send", json={"content": "Unauthorized"})
        assert res.status_code == 302  # Redirect to login

    def test_send_message_escapes_html(self, auth_client, app):
        """Message content should be HTML-escaped."""
        auth_client.post("/send",
            json={"content": "<script>alert('xss')</script>"}
        )
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content FROM messages ORDER BY id DESC LIMIT 1").fetchone()
            # Bleach removes script tags entirely
            assert "<script>" not in row["content"]
            assert "alert('xss')" in row["content"]


class TestEditMessage:
    """Tests for the /edit endpoint."""

    def test_edit_message_success(self, auth_client, app):
        """Successfully edit own message."""
        # Create message
        res = auth_client.post("/send", json={"content": "Original"})
        msg_id = res.get_json()["id"]

        # Edit message
        res = auth_client.post("/edit",
            json={"id": msg_id, "content": "Edited"}
        )
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

        # Verify in database
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content, edited_at FROM messages WHERE id=?", (msg_id,)).fetchone()
            assert row["content"] == "Edited"
            assert row["edited_at"] is not None

    def test_edit_message_not_owner(self, app):
        """Cannot edit another user's message."""
        client = app.test_client()
        
        # Create user1 (alice) and send message
        client.post('/auth/register', json={'username': 'alice', 'password': 'pass123'})
        res = client.post("/send", json={"content": "Alice's message"})
        msg_id = res.get_json()["id"]
        client.get('/auth/logout')
        
        # Login as user2 (bob) and try to edit
        client.post('/auth/register', json={'username': 'bob', 'password': 'pass123'})
        res = client.post("/edit", json={"id": msg_id, "content": "Hacked!"})
        assert res.status_code == 403
        assert res.get_json()["ok"] is False

    def test_edit_message_not_found(self, auth_client):
        """Editing non-existent message returns 404."""
        res = auth_client.post("/edit",
            json={"id": 999999, "content": "Ghost"}
        )
        assert res.status_code == 404

    def test_edit_message_missing_id(self, auth_client):
        """Editing without message ID returns 400."""
        res = auth_client.post("/edit", json={"content": "No ID"})
        assert res.status_code == 400

    def test_edit_requires_auth(self, client):
        """Edit requires authentication."""
        res = client.post("/edit", json={"id": 1, "content": "Nope"})
        assert res.status_code == 302


class TestDeleteMessage:
    """Tests for the /delete endpoint."""

    def test_delete_message_success(self, auth_client, app):
        """Successfully soft-delete own message."""
        # Create message
        res = auth_client.post("/send", json={"content": "To be deleted"})
        msg_id = res.get_json()["id"]

        # Delete message
        res = auth_client.post("/delete", json={"id": msg_id})
        assert res.status_code == 200
        assert res.get_json()["ok"] is True

        # Verify soft-delete in database
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT deleted_at FROM messages WHERE id=?", (msg_id,)).fetchone()
            assert row["deleted_at"] is not None

    def test_delete_message_not_owner(self, app):
        """Cannot delete another user's message."""
        client = app.test_client()
        
        # Create user1 (alice) and send message
        client.post('/auth/register', json={'username': 'alice2', 'password': 'pass123'})
        res = client.post("/send", json={"content": "Alice's message"})
        msg_id = res.get_json()["id"]
        client.get('/auth/logout')
        
        # Login as user2 (bob) and try to delete
        client.post('/auth/register', json={'username': 'bob2', 'password': 'pass123'})
        res = client.post("/delete", json={"id": msg_id})
        assert res.status_code == 403

    def test_delete_message_not_found(self, auth_client):
        """Deleting non-existent message returns 404."""
        res = auth_client.post("/delete", json={"id": 999999})
        assert res.status_code == 404

    def test_delete_already_deleted(self, auth_client):
        """Cannot delete an already deleted message."""
        # Create and delete message
        res = auth_client.post("/send", json={"content": "Delete me twice"})
        msg_id = res.get_json()["id"]
        auth_client.post("/delete", json={"id": msg_id})

        # Try to delete again
        res = auth_client.post("/delete", json={"id": msg_id})
        assert res.status_code == 404

    def test_cannot_edit_deleted_message(self, auth_client):
        """Cannot edit a deleted message."""
        # Create and delete message
        res = auth_client.post("/send", json={"content": "Delete then edit"})
        msg_id = res.get_json()["id"]
        auth_client.post("/delete", json={"id": msg_id})

        # Try to edit deleted message
        res = auth_client.post("/edit", json={"id": msg_id, "content": "Zombie"})
        assert res.status_code == 404

    def test_delete_requires_auth(self, client):
        """Delete requires authentication."""
        res = client.post("/delete", json={"id": 1})
        assert res.status_code == 302
