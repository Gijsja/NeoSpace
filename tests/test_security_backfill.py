
import pytest
import json
from db import get_db

def test_backfill_unauthorized(client):
    """Ensure /backfill is not accessible without login."""
    res = client.get('/backfill')
    assert res.status_code == 302  # Redirects to login
    assert '/auth/login' in res.headers['Location']

def test_backfill_room_isolation(auth_client, app):
    """Ensure /backfill filters by room_id."""
    with app.app_context():
        db = get_db()
        # 'testuser' is created by auth_client fixture (id=1)

        # Insert messages
        db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                   ("testuser", "general msg", 1))
        db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                   ("testuser", "secret msg", 2))

    # Test Room 1 (Default)
    res = auth_client.get('/backfill')
    assert res.status_code == 200
    # Response is application/json, client.get_json() should work
    data = res.get_json()
    messages = data['messages']

    assert any(m['content'] == 'general msg' for m in messages)
    assert not any(m['content'] == 'secret msg' for m in messages)

    # Test Room 2
    res = auth_client.get('/backfill?room_id=2')
    assert res.status_code == 200
    data = res.get_json()
    messages = data['messages']

    assert any(m['content'] == 'secret msg' for m in messages)
    assert not any(m['content'] == 'general msg' for m in messages)

def test_backfill_invalid_room(auth_client):
    """Ensure invalid room_id is handled gracefully (empty list)."""
    res = auth_client.get('/backfill?room_id=999')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['messages']) == 0
