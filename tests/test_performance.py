
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
    """
    with app.test_client() as client:
        client.post('/auth/register', json={
            'username': 'perf_user_3',
            'password': 'password123'
        })

        with patch('app.get_db') as mock_get_db:
            client.get('/files/some_shard/user_1/avatars/me.jpg')
            assert not mock_get_db.called, "get_db should NOT be called for /files/..."

def test_backfill_limit(auth_client, app):
    """
    Test that backfill endpoint limits the number of messages returned.
    """
    with app.app_context():
        db = get_db()
        messages = [
            ("testuser", f"Message {i}", 1) for i in range(600)
        ]
        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            messages
        )
        db.commit()

    res = auth_client.get("/backfill")
    assert res.status_code == 200
    data = res.get_json()

    assert len(data["messages"]) == 500, "Backfill should be limited to 500 messages"
    last_msg = data["messages"][-1]
    assert last_msg["content"] == "Message 599"

def test_feed_index_exists(app):
    """
    Test that the performance index idx_posts_created exists in the database schema.
    This ensures that queries sorting profile_posts by created_at are optimized.
    """
    with app.app_context():
        db = get_db()
        # Query SQLite system table
        row = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='index' AND name='idx_posts_created'"
        ).fetchone()

        assert row is not None, "Performance index 'idx_posts_created' is missing!"
