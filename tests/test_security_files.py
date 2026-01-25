
import pytest
import os
from app import create_app
from db import get_db, init_db

@pytest.fixture
def app():
    # Use a temporary database for testing
    app = create_app({'TESTING': True, 'DATABASE': ':memory:', 'WTF_CSRF_ENABLED': False})

    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_path_traversal_blocked(client, app):
    """
    Verify that path traversal attempts in file serving routes are blocked.
    """
    # 1. Register and Login
    auth_response = client.post('/auth/register', json={
        'username': 'attacker',
        'password': 'password123'
    })
    assert auth_response.status_code == 200

    # 2. Setup Files
    upload_root = app.config.get('UPLOAD_FOLDER', 'uploads')
    user_dir = os.path.join(app.root_path, upload_root, 'user_1', 'docs')
    os.makedirs(user_dir, exist_ok=True)

    with open(os.path.join(user_dir, 'test.txt'), 'w') as f:
        f.write("I am legitimate")

    with open(os.path.join(app.root_path, upload_root, 'secret_in_uploads.txt'), 'w') as f:
        f.write("I am secret")

    # 3. Test Legitimate Access
    resp = client.get('/files/user_1/docs/test.txt')
    assert resp.status_code == 200
    assert "I am legitimate" in resp.get_data(as_text=True)

    # 4. Attempt Path Traversal via serve_unsharded_user_file
    # Try to access secret_in_uploads.txt via user_1/../secret_in_uploads.txt
    response = client.get('/files/user_1/%2e%2e/secret_in_uploads.txt')

    # Assert that the request is blocked with 400 Bad Request
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    # 5. Attempt Path Traversal via serve_legacy_file (if applicable)
    # The legacy route is /files/<filename>.
    # If we request /files/..%2fsecret.txt, it might be normalized or blocked.
    # But serve_legacy_file now explicitly checks for '..' in filename.
    response_legacy = client.get('/files/%2e%2e%2fsecret.txt')
    # Depending on how Werkzeug handles %2f in path, this might be 404 (no route) or hit the view.
    # If it hits the view, it should be 400.
    if response_legacy.status_code != 404:
        assert response_legacy.status_code == 400 or response_legacy.status_code == 403
