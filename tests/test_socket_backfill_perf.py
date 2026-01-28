
import pytest
from flask_socketio import SocketIO
from db import get_db

class TestSocketBackfillPerformance:
    """Test performance optimizations for socket backfill."""

    def test_backfill_limit_initial_load(self, auth_client, app):
        """
        Verify that initial backfill (after_id=0) is limited to 100 messages.
        This prevents fetching the entire history on join.
        """
        # Create 200 messages
        with app.app_context():
            db = get_db()
            # We need to manually insert to ensure timestamps are ordered if needed,
            # but AUTOINCREMENT id is enough for the sort.
            for i in range(200):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    (f"user{i}", f"Message {i}", 1)
                )
            db.commit()

        # Connect with auth_client which has the session
        socketio = app.extensions['socketio']
        socket_client = socketio.test_client(app, flask_test_client=auth_client)

        socket_client.connect()
        socket_client.emit('join_room', {'room': 'general'})

        # Clear any events from join
        socket_client.get_received()

        # Request backfill
        socket_client.emit('request_backfill', {'after_id': 0})

        received = socket_client.get_received()
        backfill_event = next((e for e in received if e['name'] == 'backfill'), None)

        assert backfill_event is not None
        messages = backfill_event['args'][0]['messages']

        # Should be limited to 100
        assert len(messages) == 100

        # Should be the LATEST 100 messages (ids 101 to 200)
        # And they should be in chronological order (ascending ID)
        assert messages[0]['content'] == "Message 100"
        assert messages[-1]['content'] == "Message 199"

    def test_backfill_limit_sync_clean(self, auth_client, app):
        """
        Verify that sync backfill (after_id > 0) is limited to 500 messages.
        """
        # Create 600 messages
        with app.app_context():
            db = get_db()
            for i in range(600):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    (f"user{i}", f"Message {i}", 1)
                )
            db.commit()

        socketio = app.extensions['socketio']
        socket_client = socketio.test_client(app, flask_test_client=auth_client)
        socket_client.connect()
        socket_client.emit('join_room', {'room': 'general'})
        socket_client.get_received()

        # Request backfill from ID 10. There are 590 messages after ID 10.
        # The limit should be 500.
        socket_client.emit('request_backfill', {'after_id': 10})

        received = socket_client.get_received()
        backfill_event = next((e for e in received if e['name'] == 'backfill'), None)

        assert backfill_event is not None
        messages = backfill_event['args'][0]['messages']

        assert len(messages) == 500
        # Should be ordered ASC
        assert messages[0]['id'] == 11
        assert messages[-1]['id'] == 510
