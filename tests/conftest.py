
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
    db_module.DB_PATH = db_path
    
    app = create_app()
    app.config["TESTING"] = True
    
    yield app
    
    # Cleanup
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()

