
import os
import shutil
import pytest
from flask import Flask
from routes.files import bp as files_bp

@pytest.fixture
def app_with_files():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    app.config['UPLOAD_FOLDER'] = 'uploads_test_traversal'
    app.register_blueprint(files_bp)

    # Create temp upload folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    app.root_path = root_dir

    upload_dir = os.path.join(root_dir, 'uploads_test_traversal')
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir)

    # Create a dummy user folder
    user_dir = os.path.join(upload_dir, 'user_1')
    os.makedirs(user_dir)

    # Create a secret file in uploads root (parent of user_1)
    with open(os.path.join(upload_dir, 'secret.txt'), 'w') as f:
        f.write('SECRET_CONTENT')

    yield app

    # Cleanup
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)

def test_path_traversal_uploads_root(app_with_files):
    """Test that traversing to uploads root via '..' in category is blocked."""
    client = app_with_files.test_client()

    # Mock login
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Try to access ../secret.txt via user_1 category traversal
    # URL: /files/user_1/../secret.txt
    res = client.get('/files/user_1/../secret.txt')

    # It should fail (400 or 404 depending on implementation of checks)
    # Before fix: 200 (Vulnerable)
    # After fix: 400 (Bad Request)

    if res.status_code == 200 and b'SECRET_CONTENT' in res.data:
        pytest.fail("Path traversal vulnerability detected: Accessed file in uploads root via '..'")

    # Ideally we expect 400 after fix
    assert res.status_code == 400
