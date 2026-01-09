
import pytest
from app import create_app

class TestFullSiteSmoke:
    """Smoke tests for all major application routes."""

    @pytest.fixture
    def client(self):
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def auth_client(self, client):
        """Authenticated client."""
        client.post('/auth/register', data={'username': 'smokeuser', 'password': 'password'})
        client.post('/auth/login', data={'username': 'smokeuser', 'password': 'password'})
        return client

    def test_public_routes(self, client):
        """Test routes accessible without login (or redirect to login)."""
        routes = [
            '/',
            '/auth/login',
        ]
        for route in routes:
            res = client.get(route, follow_redirects=True)
            assert res.status_code == 200, f"Route {route} failed with {res.status_code}"

    def test_protected_routes(self, auth_client):
        """Test routes requiring login."""
        routes = [
            '/app',      # Main App (Chat/Dashboard)
            '/feed/',
            '/wall/',    # Profile View
            '/codeground', 
            '/directory',
            '/components'
        ]
        for route in routes:
            res = auth_client.get(route, follow_redirects=True)
            assert res.status_code == 200, f"Protected route {route} failed with {res.status_code}"

    def test_api_routes(self, auth_client):
        """Smoke test key API endpoints."""
        # Search
        res = auth_client.get('/search/?q=test', follow_redirects=True)
        assert res.status_code == 200, f"Search failed: {res.status_code}"
        
        # Feed API
        res = auth_client.get('/feed/?page=1', follow_redirects=True) 
        assert res.status_code == 200
