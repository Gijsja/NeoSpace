import pytest
from app import create_app, init_db
from sockets import socketio
from flask_socketio import SocketIOTestClient
import msgspec
import tempfile
import os

@pytest.fixture
def app():
    """Create app with isolated test database."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    test_config = {
        'DATABASE': db_path,
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    }

    app = create_app(test_config)

    with app.app_context():
        init_db()

    yield app

    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def socket_client(app, client):
    # Authenticate first
    client.post('/auth/register', json={'username': 'testuser', 'password': 'password'})
    client.post('/auth/login', json={'username': 'testuser', 'password': 'password'})

    # Connect socket
    return socketio.test_client(app, flask_test_client=client)

def test_backfill_initial_load_limit(app, client, socket_client):
    """Test that initial backfill is limited to 100 messages."""
    from db import get_db

    # Create 150 messages
    with app.app_context():
        db = get_db()
        # Use executemany for speed
        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            [('testuser', f'msg {i}', 1) for i in range(150)]
        )
        db.commit()

    # Request backfill with after_id=0
    socket_client.emit('request_backfill', {'after_id': 0})

    received = socket_client.get_received()
    backfill_event = next(e for e in received if e['name'] == 'backfill')

    payload = backfill_event['args'][0]
    messages = payload['messages']

    # Should be 100 messages (the last 100)
    assert len(messages) == 100

    # Verify we got the LATEST messages (msg 50 to msg 149)
    # messages are sorted by ID ASC in the response
    assert messages[0]['content'] == 'msg 50'
    assert messages[-1]['content'] == 'msg 149'

def test_backfill_sync_limit(app, client, socket_client):
    """Test that sync backfill is limited to 500 messages."""
    from db import get_db

    # Create 600 messages
    with app.app_context():
        db = get_db()
        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            [('testuser', f'msg {i}', 1) for i in range(600)]
        )
        db.commit()

    # Request backfill starting from message 10 (id > 10, but id is auto increment so roughly matches index if we started at 1)
    # Wait, IDs start at 1. msg 0 is ID 1. msg 10 is ID 11.
    # If we ask for after_id = 10 (which is msg 9), we get msg 10 (ID 11) onwards.

    # To be safe, let's just use what we inserted.
    # IDs will be 1 to 600.
    # Request after_id=10.

    socket_client.emit('request_backfill', {'after_id': 10})

    received = socket_client.get_received()
    backfill_event = next(e for e in received if e['name'] == 'backfill')
    messages = backfill_event['args'][0]['messages']

    # Should be 500 messages
    assert len(messages) == 500

    # First message should be ID 11 (msg 10)
    assert messages[0]['content'] == 'msg 10'
    # Last message should be ID 510 (msg 509)
    assert messages[-1]['content'] == 'msg 509'
