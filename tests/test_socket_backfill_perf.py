from app import socketio
import db as db_module


def test_backfill_limit(client, app):
    """
    Test that backfill is limited to 100 messages for initial load.
    """
    # 1. Setup User and DB
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    # Insert 200 messages
    with app.app_context():
        db = db_module.get_db()

        # Create user first to satisfy foreign keys
        db.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash) "
            "VALUES (1, 'testuser', 'hash')"
        )
        db.execute(
            "INSERT OR IGNORE INTO rooms (id, name) VALUES (1, 'general')"
        )

        # Insert 200 messages
        params = []
        for i in range(200):
            params.append(('testuser', f'msg {i}', 1))

        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            params
        )
        db.commit()

    # 2. Connect Socket
    socket_client = socketio.test_client(app, flask_test_client=client)

    # 3. Join Room
    socket_client.emit('join_room', {'room': 'general'})

    # Clear received events (connection messages etc)
    socket_client.get_received()

    # 4. Request Backfill (Initial Load)
    socket_client.emit('request_backfill', {'after_id': 0})

    received = socket_client.get_received()

    # Find backfill event
    backfill_event = next(
        (e for e in received if e['name'] == 'backfill'), None
    )
    assert backfill_event is not None

    # msgspec structs are converted to builtins (dicts)
    payload = backfill_event['args'][0]
    messages = payload['messages']

    # Assertions
    # Should now return 100 messages (latest)
    assert len(messages) == 100, f"Expected 100 messages, got {len(messages)}"
    assert messages[0]['content'] == 'msg 100'
    assert messages[-1]['content'] == 'msg 199'
