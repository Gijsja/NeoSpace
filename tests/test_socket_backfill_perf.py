
import pytest
from db import get_db
from sockets import socketio

def test_socket_backfill_pagination(app):
    """
    Test that backfill requests are paginated to prevent performance issues.
    """
    # 1. Setup: Create user and seed 1000 messages
    with app.app_context():
        db = get_db()
        db.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (1, 'perf_tester', 'hash')")

        # Ensure we start fresh or know the IDs?
        # The test fixture usually resets the DB.

        # Use a transaction for speed
        db.execute("BEGIN")
        for i in range(1000):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ("perf_bot", f"Message {i}", 1)
            )
        db.execute("COMMIT")

        # Get the ID range to be safe
        first_id = db.execute("SELECT MIN(id) FROM messages").fetchone()[0]
        last_id = db.execute("SELECT MAX(id) FROM messages").fetchone()[0]

    # 2. Authenticate
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'perf_tester'

    # 3. Connect SocketIO
    socket_client = socketio.test_client(app, flask_test_client=client)
    socket_client.get_received() # Clear 'connected' events

    # 4. Request Backfill (Initial Load)
    socket_client.emit('request_backfill', {'after_id': 0})

    received = socket_client.get_received()
    assert len(received) > 0
    backfill_event = received[0]
    data = backfill_event['args'][0]
    messages = data['messages']

    # 5. Assert Initial Load Limits
    print(f"Initial load returned {len(messages)} messages")
    assert len(messages) == 100, f"Expected 100 messages (optimized), got {len(messages)}"

    # Check it returned the LATEST messages
    # messages are sorted by ID ASC.
    # So the last message in the list should be the last message in DB.
    assert messages[-1]['id'] == last_id
    # The first message in the list should be last_id - 99
    assert messages[0]['id'] == last_id - 99

    # 6. Test Sync Pagination (limit 500)
    socket_client.get_received() # clear

    # Request messages after the very first ID
    # This should return the next 500 messages (limit)
    socket_client.emit('request_backfill', {'after_id': first_id})

    received = socket_client.get_received()
    data = received[0]['args'][0]
    sync_messages = data['messages']

    print(f"Sync load returned {len(sync_messages)} messages")
    assert len(sync_messages) == 500, f"Expected 500 sync messages, got {len(sync_messages)}"

    # Verify content
    # Should start from first_id + 1
    assert sync_messages[0]['id'] == first_id + 1

    socket_client.disconnect()
