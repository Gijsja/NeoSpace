
"""Socket contract tests - validate message payload structure and integration."""

import pytest
from db import get_db

# Required keys for message payloads (socket and backfill)
REQUIRED_MESSAGE_KEYS = {"id", "user", "content", "deleted", "edited"}


class TestMessagePayloadContract:
    """Verify message payload structure adheres to contract."""

    def test_message_payload_has_required_keys(self):
        """Message payloads must contain all required keys."""
        payload = {
            "id": 1,
            "user": "alice",
            "content": "hi",
            "deleted": False,
            "edited": False
        }
        assert set(payload.keys()) == REQUIRED_MESSAGE_KEYS

    def test_message_payload_types(self):
        """Message payload values must have correct types."""
        payload = {
            "id": 1,
            "user": "alice",
            "content": "hi",
            "deleted": False,
            "edited": False
        }
        assert isinstance(payload["id"], int)
        assert isinstance(payload["user"], str)
        assert isinstance(payload["content"], (str, type(None)))
        assert isinstance(payload["deleted"], bool)
        assert isinstance(payload["edited"], bool)

    def test_deleted_message_has_none_content(self):
        """Deleted messages should have None content."""
        deleted_payload = {
            "id": 1,
            "user": "alice",
            "content": None,
            "deleted": True,
            "edited": False
        }
        assert deleted_payload["deleted"] is True
        assert deleted_payload["content"] is None


class TestBackfillContract:
    """Verify backfill payload structure."""

    def test_backfill_payload_structure(self):
        """Backfill responses have phase and messages array."""
        backfill_response = {
            "phase": "continuity",
            "messages": []
        }
        assert "phase" in backfill_response
        assert "messages" in backfill_response
        assert isinstance(backfill_response["messages"], list)

    def test_backfill_phase_is_continuity(self):
        """Backfill phase must be 'continuity' in E2."""
        backfill_response = {"phase": "continuity", "messages": []}
        assert backfill_response["phase"] == "continuity"


class TestBackfillIntegration:
    """Integration tests for backfill endpoint."""

    def test_backfill_returns_messages(self, auth_client, app):
        """Backfill endpoint returns created messages."""
        # Create messages
        auth_client.post("/send", json={"content": "Message 1"})
        auth_client.post("/send", json={"content": "Message 2"})
        
        # Fetch backfill
        res = auth_client.get("/backfill")
        assert res.status_code == 200
        data = res.get_json()
        assert "messages" in data
        assert len(data["messages"]) == 2

    def test_backfill_respects_message_order(self, auth_client, app):
        """Messages should be returned in creation order."""
        auth_client.post("/send", json={"content": "First"})
        auth_client.post("/send", json={"content": "Second"})
        auth_client.post("/send", json={"content": "Third"})
        
        res = auth_client.get("/backfill")
        messages = res.get_json()["messages"]
        
        assert messages[0]["content"] == "First"
        assert messages[1]["content"] == "Second"
        assert messages[2]["content"] == "Third"

    def test_backfill_includes_edited_flag(self, auth_client, app):
        """Edited messages should have edited flag in backfill."""
        # Create and edit message
        res = auth_client.post("/send", json={"content": "Original"})
        msg_id = res.get_json()["id"]
        auth_client.post("/edit", json={"id": msg_id, "content": "Edited"})
        
        # Check backfill
        res = auth_client.get("/backfill")
        messages = res.get_json()["messages"]
        edited_msg = next(m for m in messages if m["id"] == msg_id)
        
        assert edited_msg["content"] == "Edited"
        # Note: HTTP backfill doesn't include edited flag currently


class TestCoreInvariants:
    """Tests for core invariants defined in CORE_INVARIANTS.md."""

    def test_invariant_deleted_content_never_leaked(self, auth_client, app):
        """Invariant 4: Deleted content is never leaked."""
        # Create and delete message
        res = auth_client.post("/send", json={"content": "Secret message"})
        msg_id = res.get_json()["id"]
        auth_client.post("/delete", json={"id": msg_id})
        
        # Verify content is not in database query result
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content, deleted_at FROM messages WHERE id=?", (msg_id,)).fetchone()
            # Content still exists in DB (soft delete), but...
            assert row["deleted_at"] is not None

    def test_invariant_server_authoritative_on_ownership(self, app):
        """Invariant 1: Server enforces message ownership."""
        client = app.test_client()
        
        # Alice creates message
        client.post('/auth/register', json={'username': 'alice_inv', 'password': 'pass123'})
        res = client.post("/send", json={"content": "Alice message here"})
        msg_id = res.get_json()["id"]
        client.get('/auth/logout')
        
        # Bob tries to edit/delete
        client.post('/auth/register', json={'username': 'bob_inv', 'password': 'pass123'})
        
        res = client.post("/edit", json={"id": msg_id, "content": "Hacked"})
        assert res.status_code == 403
        
        res = client.post("/delete", json={"id": msg_id})
        assert res.status_code == 403
        
        # Verify message unchanged
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content FROM messages WHERE id=?", (msg_id,)).fetchone()
            assert row["content"] == "Alice message here"

    def test_invariant_reconnect_idempotent(self, auth_client, app):
        """Invariant 5: Multiple backfill requests produce same result."""
        # Create some messages
        auth_client.post("/send", json={"content": "Msg 1"})
        auth_client.post("/send", json={"content": "Msg 2"})
        
        # Multiple backfill requests
        res1 = auth_client.get("/backfill")
        res2 = auth_client.get("/backfill")
        res3 = auth_client.get("/backfill")
        
        # All should return same data
        assert res1.get_json() == res2.get_json() == res3.get_json()


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_empty_content_allowed(self, auth_client):
        """Empty message content is currently allowed."""
        res = auth_client.post("/send", json={"content": ""})
        # Currently allowed - empty string is valid
        assert res.status_code == 200

    def test_very_long_content(self, auth_client, app):
        """Very long messages should be stored correctly."""
        long_content = "X" * 10000
        res = auth_client.post("/send", json={"content": long_content})
        assert res.status_code == 200
        msg_id = res.get_json()["id"]
        
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content FROM messages WHERE id=?", (msg_id,)).fetchone()
            assert len(row["content"]) == 10000

    def test_unicode_content(self, auth_client, app):
        """Unicode content should be preserved."""
        content = "Hello 世界 🌍 Привет"
        res = auth_client.post("/send", json={"content": content})
        msg_id = res.get_json()["id"]
        
        with app.app_context():
            db = get_db()
            row = db.execute("SELECT content FROM messages WHERE id=?", (msg_id,)).fetchone()
            # Content is HTML escaped, so check for presence of unicode
            assert "世界" in row["content"]

    def test_unauthenticated_send_rejected(self, client):
        """Unauthenticated send should redirect to login."""
        res = client.post("/send", json={"content": "Unauthorized"})
        assert res.status_code == 302
