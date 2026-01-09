
import pytest
from db import get_db

class TestLinkStyles:
    """Detailed tests for Link Module styles."""

    def test_create_button_style_link(self, auth_client):
        """Test creating a Button style link."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'link',
            'content': {
                'url': 'https://example.com/button', 
                'title': 'My Button'
            },
            'style': {
                'link_style': 'button'
            },
            'display_order': 0
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['ok'] == True
        post_id = data['id']

        # Verify DB content
        db = get_db()
        row = db.execute("SELECT style_payload FROM profile_posts WHERE id = ?", (post_id,)).fetchone()
        assert 'button' in row['style_payload']

    def test_create_card_style_link(self, auth_client):
        """Test creating a Card style link with thumbnail."""
        res = auth_client.post('/wall/post/add', json={
            'module_type': 'link',
            'content': {
                'url': 'https://example.com/card', 
                'title': 'My Card',
                'thumbnail': 'https://example.com/thumb.jpg'
            },
            'style': {
                'link_style': 'card'
            },
            'display_order': 1
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['ok'] == True
        post_id = data['id']

        # Verify DB content
        db = get_db()
        row = db.execute("SELECT content_payload, style_payload FROM profile_posts WHERE id = ?", (post_id,)).fetchone()
        assert 'card' in row['style_payload']
        assert 'thumb.jpg' in row['content_payload']
