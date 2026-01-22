import time

import pytest


class TestSocketsV2:
    """
    Test suite specifically for the new socket logic:
    - Pagination for backfill (100 latest, then sync)
    - Retry logic for messaging (hard to test without mocking lock)
    """

    @pytest.fixture
    def socket_client(self, app, client):
        """Authenticated socket client."""
        from db import get_db
        from sockets import socketio

        username = "socket_tester"
        with app.app_context():
            database = get_db()
            cursor = database.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, "hash"),
            )
            user_id = cursor.lastrowid
            database.commit()

        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = username

        socket_client = socketio.test_client(app, flask_test_client=client)
        return socket_client

    def test_backfill_initial_load_limit(self, app, socket_client):
        """
        Verify that requesting backfill with after_id=0 returns
        only the latest 100 messages.
        """
        from db import get_db

        # Seed 150 messages
        with app.app_context():
            database = get_db()
            for i in range(150):
                database.execute(
                    "INSERT INTO messages "
                    "(user, content, room_id, created_at) VALUES (?, ?, ?, ?)",
                    ("seed_user", f"msg_{i}", 1, time.time() + i),
                )
            database.commit()

        # Emit join room (required to set room context)
        socket_client.emit("join_room", {"room": "general"})

        # Request backfill
        socket_client.emit("request_backfill", {"after_id": 0})

        received = socket_client.get_received()
        backfill_event = next(
            (e for e in received if e["name"] == "backfill"), None
        )
        assert backfill_event, "Backfill event not received"

        data = backfill_event["args"][0]
        messages = data["messages"]

        # Should be capped at 100
        assert len(messages) == 100
        # Should be the latest (msg_50 to msg_149)
        # Check first and last content
        assert messages[0]["content"] == "msg_50"
        assert messages[-1]["content"] == "msg_149"

    def test_backfill_sync_limit(self, app, socket_client):
        """
        Verify that requesting backfill with after_id > 0 returns messages
        and respects limit.
        """
        from db import get_db

        # Seed 1200 messages
        with app.app_context():
            database = get_db()
            for i in range(1200):
                database.execute(
                    "INSERT INTO messages "
                    "(user, content, room_id, created_at) VALUES (?, ?, ?, ?)",
                    ("seed_user", f"msg_{i}", 1, time.time() + i),
                )
            database.commit()

        socket_client.emit("join_room", {"room": "general"})

        # Request sync from message 0
        socket_client.emit("request_backfill", {"after_id": 0})

        # Clear the queue so we don't mix up events
        socket_client.get_received()

        # Wait, after_id=0 is initial load (limit 100).
        # We want sync, so after_id must be > 0.
        # But we need to know an ID. IDs are auto-increment.
        # Let's get the first ID.

        with app.app_context():
            database = get_db()
            first_id = database.execute(
                "SELECT id FROM messages LIMIT 1"
            ).fetchone()["id"]
            # So if we request after first_id, we should get next 1000.

        socket_client.emit("request_backfill", {"after_id": first_id})

        received = socket_client.get_received()
        backfill_event = next(
            (e for e in received if e["name"] == "backfill"), None
        )

        data = backfill_event["args"][0]
        messages = data["messages"]

        # Should be capped at 1000
        assert len(messages) == 1000
        # Should start from first_id + 1
        assert messages[0]["id"] > first_id

    def test_send_message_success(self, socket_client):
        """Test sending a message works."""
        socket_client.emit("join_room", {"room": "general"})
        socket_client.emit("send_message", {"content": "Hello World"})

        received = socket_client.get_received()
        msg_event = next((e for e in received if e["name"] == "message"), None)
        assert msg_event

        # Args is a dict (msgspec struct converted to dict) in this test
        # environment context. Check if it's a list or dict to be safe.
        args = msg_event["args"]
        if isinstance(args, list):
            content = args[0]["content"]
        else:
            content = args["content"]

        assert content == "Hello World"
