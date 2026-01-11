
import pytest
from flask import session
from unittest.mock import MagicMock, patch
from db import get_db

def test_static_file_skips_db(app):
    """
    Test that requesting a static file does NOT trigger load_user DB query.
    """
    with app.test_client() as client:
        client.post('/auth/register', json={
            'username': 'perf_user',
            'password': 'password123'
        })

        with patch('app.get_db') as mock_get_db:
            # Request a file that IS in /static/
            resp = client.get('/static/favicon.ico')
            assert not mock_get_db.called, "get_db should NOT be called for /static/favicon.ico"

def test_favicon_route_skips_db(app):
    """
    Test that requesting /favicon.ico (root route) also skips DB if optimized.
    """
    with app.test_client() as client:
        client.post('/auth/register', json={
            'username': 'perf_user_2',
            'password': 'password123'
        })

        with patch('app.get_db') as mock_get_db:
            resp = client.get('/favicon.ico')
            assert not mock_get_db.called, "get_db should NOT be called for /favicon.ico"

def test_files_route_skips_db(app):
    """
    Test that requesting a file from /files/ also skips DB query in load_user.
    Note: files.py handles auth via session, not g.user.
    """
    with app.test_client() as client:
        # Register/Login
        client.post('/auth/register', json={
            'username': 'perf_user_3',
            'password': 'password123'
        })

        with patch('app.get_db') as mock_get_db:
            # We don't care if it returns 404, we care if load_user hit the DB.
            client.get('/files/some_shard/user_1/avatars/me.jpg')
            assert not mock_get_db.called, "get_db should NOT be called for /files/..."

def test_backfill_limit(auth_client, app):
    """
    Test that backfill endpoint limits the number of messages returned.
    This prevents loading the entire message history into memory.
    """
    # 1. Seed database with 600 messages
    # We do this directly via DB to be fast
    with app.app_context():
        db = get_db()
        # Create a user first (testuser is created by auth_client fixture)
        # But we need their ID or just use any username

        # Use executemany for speed
        messages = [
            ("testuser", f"Message {i}", 1) for i in range(600)
        ]
        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            messages
        )
        db.commit()

    # 2. Fetch backfill
    res = auth_client.get("/backfill")
    assert res.status_code == 200
    data = res.get_json()

    # 3. Assert count
    # Optimization: Should be capped at 500
    assert len(data["messages"]) == 500, "Backfill should be limited to 500 messages"

    # Verify we got the LATEST messages (Message 599 should be present)
    # Since we inserted them in order, the last one is Message 599.
    # The returned list is chronological, so the last element should be Message 599.
    last_msg = data["messages"][-1]
    assert last_msg["content"] == "Message 599"
