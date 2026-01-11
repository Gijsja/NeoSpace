"""
Tests for Sprint #16: Feed API
"""
import pytest
import json

class TestFeedAPI:
    """Tests for /feed/* endpoints."""
    
    def test_unauthenticated_feed(self, client):
        """Test unauthenticated access returns 401/302."""
        res = client.get('/feed/')
        assert res.status_code == 302 # Redirect to login
        
    def test_empty_feed(self, auth_client):
        """Test feed is empty when following no one."""
        res = auth_client.get('/feed/')
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
        assert isinstance(data['posts'], list)
        assert len(data['posts']) == 0
        
    def test_feed_content(self, auth_client, app):
        """Test feed contains posts from followed users."""
        
        # Setup: Create a friend and some posts
        with app.app_context():
            from db import get_db
            db = get_db()
            
            # Create Friend User (ID 2)
            db.execute("INSERT INTO users (id, username, password_hash) VALUES (2, 'friend', 'hash')")
            db.execute("INSERT INTO profiles (user_id, display_name) VALUES (2, 'Friend')")
            
            # Current user (ID 1) follows Friend (ID 2)
            db.execute("INSERT INTO friends (follower_id, following_id) VALUES (1, 2)")
            
            # Add posts for Friend
            # Note: profile_posts links to profile_id, not user_id directly. 
            # Profile ID usually matches rowid if inserted sequentially, but let's be safe.
            profile = db.execute("SELECT id FROM profiles WHERE user_id = 2").fetchone()
            pid = profile['id']
            
            # Post 1 (Old)
            db.execute("""
                INSERT INTO profile_posts (profile_id, module_type, content_payload, created_at)
                VALUES (?, 'text', ?, datetime('now', '-1 hour'))
            """, (pid, json.dumps({"text": "Old post"})))
            
            # Post 2 (New)
            db.execute("""
                INSERT INTO profile_posts (profile_id, module_type, content_payload, created_at)
                VALUES (?, 'text', ?, datetime('now'))
            """, (pid, json.dumps({"text": "New post"})))
            
            db.commit()
            
        # Fetch Feed
        res = auth_client.get('/feed/')
        data = res.get_json()
        
        assert res.status_code == 200
        assert len(data['posts']) == 2
        
        # Verify specific fields from query
        post = data['posts'][0] # Should be "New post" (ORDER BY created_at DESC)
        assert post['content']['text'] == "New post"
        assert post['author_username'] == 'friend'
        
    def test_pagination(self, auth_client, app):
        """Test feed pagination with before_id."""
        
         # Setup: Create a friend and 3 posts
        with app.app_context():
            from db import get_db
            db = get_db()
            # Assuming user 2 exists from previous test potentially, but tests should be isolated by pytest-flask usually if properly configured fixture-wise.
            # But here we are using same DB file likely if not using in-memory for tests. 
            # Let's check our conftest structure or just use unique IDs/fresh setup.
            # Standard NeoSpace test setup uses fresh DB per session or function depending on fixture scope.
            # Assuming logging in as fresh user 1 for isolated test or reused DB. 
            # Safe bet: Insert new data.
            
            db.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (10, 'pagination_friend', 'hash')")
            db.execute("INSERT OR IGNORE INTO profiles (user_id, display_name) VALUES (10, 'Pagination Friend')")
            db.execute("INSERT OR IGNORE INTO friends (follower_id, following_id) VALUES (1, 10)") # User 1 follows 10
            
            pid = db.execute("SELECT id FROM profiles WHERE user_id = 10").fetchone()['id']
            
            # 3 Posts
            for i in range(1, 4):
                 db.execute("""
                    INSERT INTO profile_posts (id, profile_id, module_type, content_payload)
                    VALUES (?, ?, 'text', ?)
                """, (100+i, pid, json.dumps({"text": f"Post {i}"})))
            db.commit()
            
        # Get Limit 2
        res = auth_client.get('/feed/?limit=2')
        data = res.get_json()
        assert len(data['posts']) == 2
        last_id = data['posts'][-1]['id'] # Should be 102 (103, 102)
        
        # Get Next Page
        res = auth_client.get(f'/feed/?limit=2&before_id={last_id}')
        data = res.get_json()
        assert len(data['posts']) == 1
        assert data['posts'][0]['id'] == 101
