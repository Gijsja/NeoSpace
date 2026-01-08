"""
Tests for Sprint #15: Live Wire — Notifications
"""
import pytest


class TestNotificationsAPI:
    """Tests for /notifications/* endpoints."""
    
    def test_get_notifications_empty(self, auth_client):
        """Test getting notifications when there are none."""
        res = auth_client.get('/notifications/')
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
        assert 'notifications' in data
        assert len(data['notifications']) == 0
    
    def test_unread_count_zero(self, auth_client):
        """Test unread count is zero initially."""
        res = auth_client.get('/notifications/unread-count')
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['count'] == 0
    
    def test_follow_creates_notification(self, auth_client, app):
        """Test that following a user creates a notification."""
        # Create target user
        with app.app_context():
            from db import get_db
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("notify_target", "hash")
            )
            db.execute(
                "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
                (2, "Notify Target")
            )
            db.commit()
        
        # Follow them (as user 1)
        auth_client.post('/friends/follow', json={'user_id': 2})
        
        # Check user 2's notifications (need to login as user 2)
        # For now, just verify the endpoint works - full test would need second auth
        with app.app_context():
            from db import get_db
            db = get_db()
            row = db.execute(
                "SELECT * FROM notifications WHERE user_id = 2"
            ).fetchone()
            
            assert row is not None
            assert row['type'] == 'follow'
            assert 'testuser' in row['title']
    
    def test_mark_all_read(self, auth_client, app):
        """Test marking all notifications as read."""
        # Create some notifications
        with app.app_context():
            from db import get_db
            db = get_db()
            for i in range(3):
                db.execute(
                    """INSERT INTO notifications (user_id, type, title) 
                       VALUES (?, 'test', ?)""",
                    (1, f"Test notification {i}")
                )
            db.commit()
        
        # Mark all as read
        res = auth_client.post('/notifications/mark-all-read')
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
        assert data['marked'] == 3
    
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated users are redirected."""
        res = client.get('/notifications/')
        assert res.status_code == 302  # Redirect to login
