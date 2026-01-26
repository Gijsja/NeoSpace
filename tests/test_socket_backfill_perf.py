
import pytest
from db import get_db
from sockets import socketio

def test_socket_backfill_pagination(app, client):
    """
    Test that socket backfill respects pagination limits.
    - Initial load (after_id=0): Max 100 messages
    - Sync load (after_id>0): Max 500 messages
    """
    with app.app_context():
        # Create user manually
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('testuser', 'hash')")
        user_row = db.execute("SELECT id FROM users WHERE username = 'testuser'").fetchone()
        user_id = user_row['id']

        # Create 200 messages
        for i in range(200):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ('testuser', f'Message {i}', 1)
            )
        db.commit()

    # Authenticate session
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['username'] = 'testuser'

    # Connect socket
    socket_client = socketio.test_client(app, flask_test_client=client)
    assert socket_client.is_connected()

    # Join room
    socket_client.emit('join_room', {'room': 'general'})
    socket_client.get_received() # Clear events

    # 1. Test Initial Load Pagination
    socket_client.emit('request_backfill', {'after_id': 0})

    received = socket_client.get_received()
    backfill_event = next(e for e in received if e['name'] == 'backfill')
    # msgspec structs are converted to builtins, check structure
    messages = backfill_event['args'][0]['messages']

    assert len(messages) == 100, f"Initial load expected 100 messages, got {len(messages)}"

    # Verify we got the LATEST messages (ids 101-200, sorted ASC)
    # ids are 1-based usually. 200 messages.
    # The optimization is: SELECT ... ORDER BY id DESC LIMIT 100 -> ORDER BY id ASC.
    # So we expect ids 101 to 200.
    assert messages[0]['id'] == 101
    assert messages[-1]['id'] == 200

    # 2. Test Sync Pagination (limit 500)
    # Create 600 more messages
    with app.app_context():
        db = get_db()
        for i in range(600):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ('testuser', f'Sync Message {i}', 1)
            )
        db.commit()
        # Total messages now: 200 + 600 = 800. IDs 1 to 800.

    # Request backfill after id 200 (so we have 600 new messages waiting: 201-800)
    socket_client.emit('request_backfill', {'after_id': 200})

    received = socket_client.get_received()
    backfill_event = next(e for e in received if e['name'] == 'backfill')
    messages = backfill_event['args'][0]['messages']

    assert len(messages) == 500, f"Sync load expected 500 messages, got {len(messages)}"

    # Verify IDs (should be 201 to 700)
    assert messages[0]['id'] == 201
    assert messages[-1]['id'] == 700
