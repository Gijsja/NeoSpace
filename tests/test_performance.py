
import pytest
from flask import session
from unittest.mock import MagicMock, patch

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

        # We need to simulate a file existing?
        # Actually we just want to check if load_user skips DB.
        # Even if the file doesn't exist (404), load_user runs before the route.
        # But wait, send_from_directory raises 404 if file not found.
        # But load_user runs BEFORE request dispatching? Yes, before_request.

        with patch('app.get_db') as mock_get_db:
            # We don't care if it returns 404, we care if load_user hit the DB.
            client.get('/files/some_shard/user_1/avatars/me.jpg')
            assert not mock_get_db.called, "get_db should NOT be called for /files/..."
