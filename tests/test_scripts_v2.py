
import pytest
from db import get_db

class TestScriptsV2:
    """Tests for Script persistence used in Codeground v2."""

    def test_save_and_list_scripts(self, auth_client):
        """Test saving a new script and listing it."""
        # 1. Save New
        res = auth_client.post('/scripts/save', json={
            'title': 'V2 Test Script',
            'content': 'console.log("Hello")',
            'script_type': 'p5'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['ok'] == True
        script_id = data['id']
        
        # 2. List
        res = auth_client.get('/scripts/list')
        assert res.status_code == 200
        data = res.get_json()
        scripts = data['scripts']
        assert len(scripts) >= 1
        assert scripts[0]['id'] == script_id
        assert scripts[0]['title'] == 'V2 Test Script'

    def test_update_script(self, auth_client):
        """Test updating an existing script."""
        # Create
        res = auth_client.post('/scripts/save', json={'title': 'Original'})
        sid = res.get_json()['id']
        
        # Update
        res = auth_client.post('/scripts/save', json={
            'id': sid,
            'title': 'Updated Title',
            'content': 'New Content'
        })
        assert res.status_code == 200
        
        # Verify
        res = auth_client.get(f'/scripts/get?id={sid}')
        data = res.get_json()
        assert data['script']['title'] == 'Updated Title'
        assert data['script']['content'] == 'New Content'
