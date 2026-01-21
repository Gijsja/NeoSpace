
import pytest
from sockets import socketio
from db import get_db

def test_socket_backfill_limit(app):
    """Verify backfill requests are limited to prevent N+1 issues."""

    # Create authenticated session context
    with app.test_client() as http_client:
        # Register and login
        http_client.post('/auth/register', json={'username': 'perf_user', 'password': 'pass'})

        # Connect socket with the authenticated http_client
        client = socketio.test_client(app, flask_test_client=http_client)

        # 1. Populate DB with 150 messages
        with app.app_context():
            db = get_db()
            for i in range(150):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    ("perf_user", f"Msg {i}", 1)
                )
            db.commit()

        # 2. Request backfill (initial load)
        client.emit('request_backfill', {'after_id': 0})

        # 3. Receive response
        received = client.get_received()

        # Find the 'backfill' event
        backfill_event = next((e for e in received if e['name'] == 'backfill'), None)
        assert backfill_event is not None

        messages = backfill_event['args'][0]['messages']

        print(f"Received {len(messages)} messages")

        # Expect latest 100 messages
        assert len(messages) == 100

        # Verify content (latest messages should be Msg 50 to Msg 149)
        # Since we sort by ID DESC and reverse, the last message should be "Msg 149"
        assert messages[-1]['content'] == "Msg 149"
        assert messages[0]['content'] == "Msg 50"

def test_socket_backfill_pagination(app):
    """Verify backfill returns correct messages for pagination (after_id > 0)."""

    with app.test_client() as http_client:
        http_client.post('/auth/register', json={'username': 'perf_user', 'password': 'pass'})
        client = socketio.test_client(app, flask_test_client=http_client)

        with app.app_context():
            db = get_db()
            for i in range(10):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    ("perf_user", f"Msg {i}", 1)
                )
            db.commit()

            # Get ID of 5th message (index 4)
            row = db.execute("SELECT id FROM messages WHERE content = 'Msg 4'").fetchone()
            msg_id_4 = row['id']

        # Request messages after Msg 4
        client.emit('request_backfill', {'after_id': msg_id_4})

        received = client.get_received()
        backfill_event = next((e for e in received if e['name'] == 'backfill'), None)
        messages = backfill_event['args'][0]['messages']

        # Should contain Msg 5, 6, 7, 8, 9 (5 messages)
        assert len(messages) == 5
        assert messages[0]['content'] == "Msg 5"
        assert messages[-1]['content'] == "Msg 9"
