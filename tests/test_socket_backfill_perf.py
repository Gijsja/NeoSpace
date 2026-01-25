
import pytest
from app import create_app
from db import get_db, init_db
from sockets import socketio
import tempfile
import os

@pytest.fixture
def app_with_db():
    fd, db_path = tempfile.mkstemp()
    os.close(fd)

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'WTF_CSRF_ENABLED': False
    })

    # Setup DB
    with app.app_context():
        init_db()

    yield app, db_path

    if os.path.exists(db_path):
        os.unlink(db_path)

def test_backfill_initial_limit(app_with_db):
    app, _ = app_with_db

    with app.app_context():
        db = get_db()
        # Create user
        db.execute("INSERT INTO users (username, password_hash) VALUES ('test', 'hash')")

        # Create 150 messages (ID 1 to 150)
        for i in range(150):
            db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                       ('test', f'msg {i+1}', 1))
        db.commit()

    flask_client = app.test_client()
    with flask_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test'

    client = socketio.test_client(app, flask_test_client=flask_client)
    client.emit('join_room', {'room': 'general'})
    client.get_received() # clear events

    # Request backfill (initial load)
    client.emit('request_backfill', {'after_id': 0})

    received = client.get_received()
    backfill_event = next((e for e in received if e['name'] == 'backfill'), None)

    assert backfill_event is not None
    messages = backfill_event['args'][0]['messages']

    # Expect limit of 100
    print(f"Received {len(messages)} messages (Initial Load)")
    assert len(messages) == 100

    # Expect latest messages (ID 51 to 150)
    # Check first and last message IDs
    first_msg = messages[0]
    last_msg = messages[-1]

    assert first_msg['id'] == 51
    assert last_msg['id'] == 150

def test_backfill_sync_limit(app_with_db):
    app, _ = app_with_db

    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('test', 'hash')")

        # Create 600 messages
        for i in range(600):
            db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                       ('test', f'msg {i+1}', 1))
        db.commit()

    flask_client = app.test_client()
    with flask_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test'

    client = socketio.test_client(app, flask_test_client=flask_client)
    client.emit('join_room', {'room': 'general'})
    client.get_received()

    # Request sync backfill (after_id=10)
    # Should get messages 11 to 600 (total 590), but capped at 500
    client.emit('request_backfill', {'after_id': 10})

    received = client.get_received()
    backfill_event = next((e for e in received if e['name'] == 'backfill'), None)

    assert backfill_event is not None
    messages = backfill_event['args'][0]['messages']

    print(f"Received {len(messages)} messages (Sync Load)")
    assert len(messages) == 500

    # Check range (11 to 510)
    assert messages[0]['id'] == 11
    assert messages[-1]['id'] == 510
