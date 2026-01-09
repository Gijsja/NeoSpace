"""
Tests for Sprint #14: Social Graph (Friends + Top 8)
"""
import pytest


class TestFriendsAPI:
    """Tests for /friends/* endpoints."""
    
    def test_follow_user(self, auth_client, app):
        """Test following another user."""
        # Create second user to follow
        with app.app_context():
            from db import get_db
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("target_user", "hash")
            )
            db.execute(
                "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
                (2, "Target User")
            )
            db.commit()
        
        res = auth_client.post('/friends/follow', json={'user_id': 2})
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
    
    def test_cannot_follow_self(self, auth_client):
        """Test that users cannot follow themselves."""
        res = auth_client.post('/friends/follow', json={'user_id': 1})
        data = res.get_json()
        
        assert res.status_code == 400
        assert 'error' in data
    
    def test_unfollow_user(self, auth_client, app):
        """Test unfollowing a user."""
        # Setup: create user and follow
        with app.app_context():
            from db import get_db
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("unfollow_target", "hash")
            )
            db.execute(
                "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
                (2, "Unfollow Target")
            )
            db.commit()
        
        # Follow first
        auth_client.post('/friends/follow', json={'user_id': 2})
        
        # Then unfollow
        res = auth_client.post('/friends/unfollow', json={'user_id': 2})
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
    
    def test_get_top8(self, auth_client, app):
        """Test fetching Top 8."""
        with app.app_context():
            from db import get_db
            db = get_db()
            # Create users to follow
            for i in range(3):
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (f"friend_{i}", "hash")
                )
                db.execute(
                    "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
                    (i + 2, f"Friend {i}")
                )
            db.commit()
        
        # Follow them
        for i in range(3):
            auth_client.post('/friends/follow', json={'user_id': i + 2})
        
        # Set Top 8
        res = auth_client.post('/friends/top8', json={
            'friend_ids': [2, 3, 4]
        })
        assert res.status_code == 200
        
        # Get Top 8
        res = auth_client.get('/friends/top8/1')
        data = res.get_json()
        
        assert res.status_code == 200
        assert 'top8' in data
        assert len(data['top8']) == 3
    
    def test_max_top8_limit(self, auth_client):
        """Test that Top 8 is limited to 8 users."""
        res = auth_client.post('/friends/top8', json={
            'friend_ids': [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 9 users
        })
        data = res.get_json()
        
        assert res.status_code == 400
        assert 'Max 8' in data['error']
    
    def test_unauthenticated_follow(self, client):
        """Test that unauthenticated users cannot follow."""
        res = client.post('/friends/follow', json={'user_id': 2})
        assert res.status_code == 302  # Redirect to login
