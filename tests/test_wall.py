"""
Tests for Sprint 12: Modular Wall API
"""
import pytest


class TestWallAPI:
    """Tests for /wall/post/* endpoints."""
    
    def test_add_text_module(self, auth_client):
        """Test adding a text module to the wall."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'text',
            'content': {'text': '# Hello World\n\nThis is a test.'},
            'display_order': 0
        })
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
        assert 'id' in data
    
    def test_add_image_module(self, auth_client):
        """Test adding an image module."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'image',
            'content': {'url': 'https://example.com/image.png'},
            'display_order': 1
        })
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
    
    def test_add_link_module(self, auth_client):
        """Test adding a link module."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'link',
            'content': {'url': 'https://example.com', 'title': 'Example'},
            'display_order': 2
        })
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
    
    def test_add_audio_module(self, auth_client):
        """Test adding an audio module."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'audio',
            'content': {'url': 'https://example.com/song.mp3', 'title': 'My Song'},
            'display_order': 3
        })
        data = res.get_json()
        
        assert res.status_code == 200
        assert data['ok'] == True
    
    def test_add_invalid_type(self, auth_client):
        """Test that invalid module types are rejected."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'invalid_type',
            'content': {'text': 'test'}
        })
        data = res.get_json()
        
        assert res.status_code == 400
        assert 'error' in data
    
    def test_update_module(self, auth_client):
        """Test updating an existing module."""
        # First, create a module
        create_res = auth_client.post('/wall/post/add', json={
            'module_type': 'text',
            'content': {'text': 'Original content'}
        })
        post_id = create_res.get_json()['id']
        
        # Update it
        update_res = auth_client.post('/wall/post/update', json={
            'id': post_id,
            'content': {'text': 'Updated content'}
        })
        data = update_res.get_json()
        
        assert update_res.status_code == 200
        assert data['ok'] == True
    
    def test_delete_module(self, auth_client):
        """Test deleting a module."""
        # First, create a module
        create_res = auth_client.post('/wall/post/add', json={
            'module_type': 'text',
            'content': {'text': 'To be deleted'}
        })
        post_id = create_res.get_json()['id']
        
        # Delete it
        delete_res = auth_client.post('/wall/post/delete', json={
            'id': post_id
        })
        data = delete_res.get_json()
        
        assert delete_res.status_code == 200
        assert data['ok'] == True
    
    def test_reorder_modules(self, auth_client):
        """Test reordering modules."""
        # Create 3 modules
        ids = []
        for i in range(3):
            res = auth_client.post('/wall/post/add', json={
                'module_type': 'text',
                'content': {'text': f'Module {i}'},
                'display_order': i
            })
            ids.append(res.get_json()['id'])
        
        # Reorder: reverse the list
        reorder_res = auth_client.post('/wall/reorder', json={
            'order': list(reversed(ids))
        })
        data = reorder_res.get_json()
        
        assert reorder_res.status_code == 200
        assert data['ok'] == True
    
    def test_unauthenticated_add(self, client):
        """Test that unauthenticated users are redirected to login."""
        res = client.post('/wall/post/add', json={
            'module_type': 'text',
            'content': {'text': 'Unauthorized'}
        })
        
        # login_required decorator redirects to login page
        assert res.status_code == 302
    
    def test_unauthenticated_delete(self, client):
        """Test that unauthenticated users are redirected to login."""
        res = client.post('/wall/post/delete', json={
            'id': 1
        })
        
        # login_required decorator redirects to login page
        assert res.status_code == 302
