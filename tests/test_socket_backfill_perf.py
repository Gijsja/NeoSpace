
import pytest
import tempfile
import os
from flask_socketio import SocketIO
from app import create_app
from db import get_db

@pytest.fixture
def app():
    # Use a temporary file for the database to ensure persistence across contexts
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": db_path, "WTF_CSRF_ENABLED": False})

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_socket_backfill_limit(app, client):
    """
    Verify that socket backfill returns ALL messages without limit (current behavior),
    proving the need for optimization.
    """
    # Create a user and log in to get session
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("testuser", "password"))
        db.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'

    # Initialize SocketIO client
    # We need to import socketio from where it's defined
    from sockets import socketio

    # Create 200 messages
    with app.app_context():
        db = get_db()
        for i in range(200):
            db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)", ("testuser", f"msg {i}", 1))
        db.commit()

    socket_client = socketio.test_client(app, flask_test_client=client)

    # Connect
    socket_client.connect()

    # Request backfill with after_id=0
    socket_client.emit('request_backfill', {'after_id': 0})

    received = socket_client.get_received()

    backfill_event = next((e for e in received if e['name'] == 'backfill'), None)
    assert backfill_event is not None

    messages = backfill_event['args'][0]['messages']

    # If optimized, it should return 100 messages (latest)
    print(f"Received {len(messages)} messages")
    assert len(messages) == 100, f"Expected 100 messages, got {len(messages)}"

    # Verify we got the LATEST messages
    # We inserted 0..199. Latest 100 should be 100..199.
    # Note: messages are reversed in backfill(after=0) to be chronological
    first_msg_content = messages[0]['content']
    last_msg_content = messages[-1]['content']

    assert first_msg_content == "msg 100", f"Expected 'msg 100', got '{first_msg_content}'"
    assert last_msg_content == "msg 199", f"Expected 'msg 199', got '{last_msg_content}'"

if __name__ == "__main__":
    # Manually run the test if executed as script
    pass
