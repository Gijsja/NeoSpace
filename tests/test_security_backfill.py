
import pytest
import sqlite3
from flask import g, session

def test_backfill_security_critical(client, app):
    """
    CRITICAL SECURITY TEST:
    Verify that the /backfill endpoint is not open to the world.
    Currently it is dumping the entire database without auth.
    """

    # 1. Setup - Create some messages in different rooms
    with app.app_context():
        # We can use the app's db connection
        from db import get_db
        db = get_db()

        db.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES ('leak_victim', 'hash')")

        # Insert messages in room 1 (General) and room 999 (Secret)
        db.execute("INSERT INTO messages (user, content, room_id) VALUES ('leak_victim', 'SECRET_DATA_ROOM_999', 999)")
        db.execute("INSERT INTO messages (user, content, room_id) VALUES ('leak_victim', 'PUBLIC_DATA_ROOM_1', 1)")
        db.commit()

    # 2. Attack - Try to access /backfill without login
    response = client.get('/backfill')

    # Assert that it fails (It currently passes 200 and leaks data)
    assert response.status_code != 200, "Unauthenticated /backfill should NOT return 200 OK"

    if response.status_code == 302:
        assert '/auth/login' in response.headers['Location']
    elif response.status_code in [401, 403]:
        pass
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")

def test_backfill_limits_and_filtering(auth_client, app):
    """
    Verify that /backfill filters by room and respects limits when authenticated.
    """
    # auth_client is already logged in as 'testuser'

    # Insert 1000 messages in room 1
    with app.app_context():
        from db import get_db
        db = get_db()
        for i in range(550):
            db.execute(f"INSERT INTO messages (user, content, room_id) VALUES ('spammer', 'msg_{i}', 1)")
        db.commit()

    response = auth_client.get('/backfill?room_id=1')
    assert response.status_code == 200

    data = response.json
    messages = data['messages']

    # Should be limited to 500
    assert len(messages) <= 500, f"Backfill returned {len(messages)} messages, expected <= 500"

    # Insert a message in room 999
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO messages (user, content, room_id) VALUES ('victim', 'HIDDEN_ROOM_MSG', 999)")
        db.commit()

    response = auth_client.get('/backfill?room_id=1')
    data = response.json
    messages = data['messages']

    for msg in messages:
        # queries/backfill.py selects content.
        assert "HIDDEN_ROOM_MSG" not in str(msg), "Leaked message from another room!"
