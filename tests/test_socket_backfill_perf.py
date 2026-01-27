
import pytest
from flask import session
from sockets import socketio
from db import get_db

def test_backfill_pagination_limit(app):
    """
    Test that backfill requests are limited to avoid fetching too many messages.
    """
    # 1. Setup: Create 200 messages in the DB
    with app.app_context():
        db = get_db()
        # Create a user
        db.execute("INSERT INTO users (username, password_hash) VALUES ('tester', 'hash')")
        user_id = db.execute("SELECT id FROM users WHERE username = 'tester'").fetchone()['id']

        # Insert 200 messages
        for i in range(200):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ('tester', f'msg-{i}', 1)
            )
        db.commit()

    # 2. Connect via SocketIO
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'tester'

        socket_client = socketio.test_client(app, flask_test_client=client)

        socket_client.emit('join_room', {'room': 'general'})
        socket_client.get_received()

        # 3. Request Backfill (Initial Load)
        socket_client.emit('request_backfill', {'after_id': 0})

        received = socket_client.get_received()
        backfill_event = next(e for e in received if e['name'] == 'backfill')
        messages = backfill_event['args'][0]['messages']

        # 4. Assertions
        # Expect limit of 100
        assert len(messages) == 100, f"Expected 100 messages, got {len(messages)}"

        # Expect latest messages (199 down to 100, but sorted ASC)
        # msg-199 is the last one inserted
        assert messages[-1]['content'] == 'msg-199'
        assert messages[0]['content'] == 'msg-100'

def test_backfill_sync_limit(app):
    """
    Test that sync requests (after_id > 0) are also limited.
    """
    # 1. Setup: Create 600 messages
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('tester', 'hash')")

        # Insert 600 messages
        # Use executemany for speed? No, simple loop is fine for test DB
        for i in range(600):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ('tester', f'msg-{i}', 1)
            )
        db.commit()

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'tester'

        socket_client = socketio.test_client(app, flask_test_client=client)
        socket_client.emit('join_room', {'room': 'general'})
        socket_client.get_received()

        # 3. Request Sync (from ID 0) - This is technically same as initial load if after_id=0
        # But if we ask for after_id=1, we should get limited batch

        socket_client.emit('request_backfill', {'after_id': 1})

        received = socket_client.get_received()
        backfill_event = next(e for e in received if e['name'] == 'backfill')
        messages = backfill_event['args'][0]['messages']

        # Expect limit of 500
        assert len(messages) == 500, f"Expected 500 messages, got {len(messages)}"

        # Should start from msg-1 (ID 2)
        assert messages[0]['content'] == 'msg-1'
