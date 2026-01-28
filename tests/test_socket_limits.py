
import pytest
from app import create_app
from sockets import socketio
import msgspec
import tempfile
import os

def test_socket_backfill_limit_initial():
    # Create temp db
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        # Setup app and db
        test_config = {
            'DATABASE': db_path,
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'RATELIMIT_ENABLED': False,
            'RATELIMIT_STORAGE_URI': 'memory://'
        }
        app = create_app(test_config)

        # Create test client
        client = app.test_client()

        # Register and login
        client.post('/auth/register', json={'username': 'tester', 'password': 'password'})
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'tester'

        # Create many messages
        with app.app_context():
            from db import get_db
            db = get_db()
            for i in range(150):
                db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                          ('tester', f'msg {i}', 1))
            db.commit()

        # Connect socket
        socket_client = socketio.test_client(app, flask_test_client=client)

        # Request backfill (initial load)
        socket_client.emit('request_backfill', {'after_id': 0})

        # Get response
        received = socket_client.get_received()

        backfill_event = next((e for e in received if e['name'] == 'backfill'), None)
        assert backfill_event is not None

        data = backfill_event['args'][0]
        messages = data['messages']

        print(f"Initial load received {len(messages)} messages")
        assert len(messages) <= 100, f"Expected <= 100 messages, got {len(messages)}"

        # Verify it got the LATEST messages
        assert messages[-1]['content'] == 'msg 149'

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_socket_backfill_limit_sync():
    # Create temp db
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        # Setup app and db
        test_config = {
            'DATABASE': db_path,
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'RATELIMIT_ENABLED': False,
            'RATELIMIT_STORAGE_URI': 'memory://'
        }
        app = create_app(test_config)

        # Create test client
        client = app.test_client()

        # Register and login
        client.post('/auth/register', json={'username': 'tester', 'password': 'password'})
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'tester'

        # Create massive amount of messages (e.g. 600)
        with app.app_context():
            from db import get_db
            db = get_db()
            # Batch insert for speed
            db.execute("BEGIN TRANSACTION")
            for i in range(600):
                db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                          ('tester', f'msg {i}', 1))
            db.execute("COMMIT")

        # Connect socket
        socket_client = socketio.test_client(app, flask_test_client=client)

        # Request backfill (sync from id 10)
        socket_client.emit('request_backfill', {'after_id': 10})

        # Get response
        received = socket_client.get_received()
        backfill_event = next((e for e in received if e['name'] == 'backfill'), None)
        messages = backfill_event['args'][0]['messages']

        print(f"Sync load received {len(messages)} messages")
        assert len(messages) <= 500, f"Expected <= 500 messages, got {len(messages)}"

        # Verify it got the NEXT messages starting after 10
        # id 11 should be first (if auto-increment works as expected starting at 1)
        # Note: ids might not be contiguous if deletions/failures, but here they should be.
        # First message content should correspond to id 11 (msg 10)
        # Wait, if id starts at 1, msg 0 is id 1. msg 10 is id 11.

        assert messages[0]['content'] == 'msg 10' # id 11

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
