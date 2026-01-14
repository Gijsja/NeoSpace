
import os
import tempfile
import pytest
from app import create_app
import db as db_module

@pytest.fixture
def app():
    """Create app with isolated test database."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Override database path
    # We must pass this to create_app so it overrides the config.py default
    test_config = {
        'DATABASE': db_path,
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False
    }
    
    app = create_app(test_config)
    
    yield app
    
    # Cleanup
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()

@pytest.fixture
def auth_client(app):
    """Test client with authenticated session."""
    client = app.test_client()
    
    # Register and login a test user
    with client:
        client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Session is now set
        yield client
