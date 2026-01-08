"""
Tests for Sprint #17: Search API
"""
import pytest
import json

class TestSearchAPI:
    """Tests for /search/ endpoint."""
    
    def test_search_users(self, auth_client, app):
        """Test searching for users by username and display name."""
        with app.app_context():
            from db import get_db
            db = get_db()
            
            # Create users
            db.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (20, 'search_target', 'hash')")
            db.execute("INSERT OR IGNORE INTO profiles (user_id, display_name) VALUES (20, 'Target Person')")
            
            db.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (21, 'other_user', 'hash')")
            db.execute("INSERT OR IGNORE INTO profiles (user_id, display_name) VALUES (21, 'Other One')")
            db.commit()
            
        # Search by username partial
        res = auth_client.get('/search/?q=search_tar&type=users')
        data = res.get_json()
        assert res.status_code == 200
        assert len(data['results']) == 1
        assert data['results'][0]['username'] == 'search_target'
        
        # Search by display name
        res = auth_client.get('/search/?q=Target&type=users')
        data = res.get_json()
        assert len(data['results']) == 1
        assert data['results'][0]['display_name'] == 'Target Person'
        
    def test_search_posts(self, auth_client, app):
        """Test searching for posts."""
        with app.app_context():
            from db import get_db
            db = get_db()
            pid = db.execute("SELECT id FROM profiles WHERE user_id = 1").fetchone()['id']
            
            db.execute("""
                INSERT INTO profile_posts (profile_id, module_type, content_payload)
                VALUES (?, 'text', ?)
            """, (pid, json.dumps({"text": "The magic keyword is pineapple"})))
            db.commit()
            
        res = auth_client.get('/search/?q=pineapple&type=posts')
        data = res.get_json()
        
        assert res.status_code == 200
        assert len(data['results']) == 1
        assert "pineapple" in data['results'][0]['content']['text']
        
    def test_empty_query(self, auth_client):
        """Test empty query returns empty list."""
        res = auth_client.get('/search/?q=')
        data = res.get_json()
        assert res.status_code == 200
        assert data['results'] == []
        
    def test_unauthenticated(self, client):
        """Test unauthenticated access."""
        res = client.get('/search/?q=test')
        assert res.status_code == 302
