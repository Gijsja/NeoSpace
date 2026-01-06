import pytest
import sqlite3
import json

def test_anthem_columns_exist(app):
    """Verify schema migration."""
    with app.app_context():
        from db import get_db
        db = get_db()
        # Check columns in profiles table
        cursor = db.execute("PRAGMA table_info(profiles)")
        columns = {row['name'] for row in cursor.fetchall()}
        assert 'anthem_url' in columns
        assert 'anthem_autoplay' in columns

def test_get_profile_includes_anthem(auth_client, app):
    """Verify default anthem fields."""
    # Auth client auto-login
    # Create profile first
    auth_client.post('/profile/update', json={'display_name': 'Anthem User'})
    
    res = auth_client.get('/profile')
    assert res.status_code == 200
    data = res.get_json()
    assert 'anthem_url' in data
    assert 'anthem_autoplay' in data
    assert data['anthem_autoplay'] is True # Default

def test_update_anthem_success(auth_client, app):
    """Test updating anthem fields."""
    
    url = "https://example.com/music.mp3"
    
    res = auth_client.post('/profile/update', json={
        'anthem_url': url,
        'anthem_autoplay': False
    })
    assert res.status_code == 200
    assert res.get_json()['ok'] is True
    
    # Verify persistence
    res = auth_client.get('/profile')
    data = res.get_json()
    assert data['anthem_url'] == url
    assert data['anthem_autoplay'] is False

def test_anthem_url_validation(auth_client, app):
    """Test invalid URLs are rejected."""
    
    # Invalid protocol
    res = auth_client.post('/profile/update', json={
        'anthem_url': 'ftp://bad-url.com'
    })
    assert res.status_code == 400
    assert "http:// or https://" in res.get_json()['error']
    
    # Empty Allowed (clearing)
    res = auth_client.post('/profile/update', json={
        'anthem_url': ''
    })
    assert res.status_code == 200
