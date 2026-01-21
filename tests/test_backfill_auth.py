
import pytest
import os
import tempfile
from app import create_app
from db import init_db

@pytest.fixture
def client():
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True, "DATABASE": db_path})

    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

def test_backfill_unauthorized_access(client):
    """
    Vulnerability Verification:
    /backfill should require authentication.
    """
    response = client.get("/backfill")
    # NEW BEHAVIOR: Returns 302 Redirect to login or 401
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

def test_unread_unauthorized_access(client):
    """
    Vulnerability Verification:
    /unread should require authentication.
    """
    response = client.get("/unread")
    # NEW BEHAVIOR: Returns 302 Redirect to login or 401
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
