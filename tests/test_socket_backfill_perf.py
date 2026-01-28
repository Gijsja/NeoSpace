
import pytest
from app import socketio
from db import get_db


@pytest.fixture
def auth_socket_client(app, client):
    """
    Create an authenticated socket client.
    """
    # Create user and login via HTTP to set session
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ('perf_user', 'hash')
        )
        user = db.execute(
            "SELECT id FROM users WHERE username = 'perf_user'"
        ).fetchone()
        user_id = user['id']
        db.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['username'] = 'perf_user'

    # Connect socket client using the authenticated flask client
    socket_client = socketio.test_client(app, flask_test_client=client)
    return socket_client


def test_backfill_pagination_initial_load(app, auth_socket_client):
    """
    Verify backfill limits initial load to 100 messages.
    """
    # Populate DB with 200 messages
    with app.app_context():
        db = get_db()
        # Ensure room exists
        db.execute("INSERT OR IGNORE INTO rooms (name) VALUES ('general')")
        room = db.execute(
            "SELECT id FROM rooms WHERE name = 'general'"
        ).fetchone()
        room_id = room['id'] if room else 1

        for i in range(200):
            db.execute(
                "INSERT INTO messages (user, content, room_id) "
                "VALUES (?, ?, ?)",
                ('perf_user', f'Msg {i}', room_id)
            )
        db.commit()

    # Request backfill (initial load)
    auth_socket_client.emit('request_backfill', {'after_id': 0})

    received = auth_socket_client.get_received()

    backfill_event = None
    for event in received:
        if event['name'] == 'backfill':
            backfill_event = event
            break

    assert backfill_event is not None
    data = backfill_event['args'][0]

    # Assert we got ONLY 100 messages (Optimization verified)
    assert len(data['messages']) == 100

    # Check that we got the LATEST messages (reversed chronological order)
    # The last message in the list should be Msg 199
    # (since we inserted 0 to 199)
    # The list contains the *last* 100 messages.
    # So it should be Msg 100 to Msg 199.

    messages = data['messages']
    # msgspec structs are converted to builtins (dicts)
    assert messages[-1]['content'] == 'Msg 199'
    assert messages[0]['content'] == 'Msg 100'


def test_backfill_pagination_sync_limit(app, auth_socket_client):
    """
    Verify backfill sync (after_id > 0) is capped at 500 messages.
    """
    # Populate DB with 600 messages
    with app.app_context():
        db = get_db()
        # Ensure room exists
        db.execute("INSERT OR IGNORE INTO rooms (name) VALUES ('general')")
        room = db.execute(
            "SELECT id FROM rooms WHERE name = 'general'"
        ).fetchone()
        room_id = room['id'] if room else 1

        # We need to distinguish from previous test run if DB persists.
        # Tests usually share DB in this setup unless teardown clears it.
        # But let's assume cleaner setup or just insert new ones.
        # Ideally we should clear messages first.
        db.execute("DELETE FROM messages")

        for i in range(600):
            db.execute(
                "INSERT INTO messages (user, content, room_id) "
                "VALUES (?, ?, ?)",
                ('perf_user', f'SyncMsg {i}', room_id)
            )
        db.commit()

    # Request backfill starting from 0
    # (but we are simulating sync so let's say after_id=1)
    # Actually, if we want to test the limit of 500,
    # we just need enough messages > after_id.
    # Let's request after_id=0 but via the "else" branch?
    # No, if after_id=0 it goes to first branch.
    # So we must provide after_id > 0.

    # Get the ID of the first message
    with app.app_context():
        db = get_db()
        first_msg = db.execute(
            "SELECT id FROM messages ORDER BY id ASC LIMIT 1"
        ).fetchone()
        first_id = first_msg['id']

    # Request backfill after the first message
    # There should be 599 messages remaining.
    auth_socket_client.emit('request_backfill', {'after_id': first_id})

    received = auth_socket_client.get_received()
    backfill_event = next(e for e in received if e['name'] == 'backfill')
    data = backfill_event['args'][0]

    # Assert limit of 500
    assert len(data['messages']) == 500
