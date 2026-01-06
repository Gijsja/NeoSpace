import tempfile
import pytest
import io
import os
from app import create_app
from db import get_db, SCHEMA

@pytest.fixture
def auth_client():
    # specific db file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path
    })
    
    with app.app_context():
        db = get_db()
        # Initialize schema directly to ensure it runs
        for statement in SCHEMA.split(';'):
            if statement.strip():
                db.execute(statement)
        
        # Create user
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ('tester', 'hash'))
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Create profile
        db.execute("INSERT INTO profiles (user_id, display_name) VALUES (?, ?)", (user_id, 'Tester'))
        db.commit()
        
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "tester"
        
    yield client
    
    os.close(db_fd)
    os.unlink(db_path)

def test_image_sticker_upload(auth_client):
    # Mock image file
    data = {
        'image': (io.BytesIO(b"fakeimagebytes"), 'test.jpg'),
        'x': 100,
        'y': 200,
        'target_user_id': 1
    }
    
    response = auth_client.post(
        '/profile/sticker/add',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['ok'] is True
    assert 'image_path' in json_data
    assert json_data['image_path'].startswith('/static/uploads/stickers/')
    
    # Verify DB persistence
    with auth_client.application.app_context():
        db = get_db()
        sticker = db.execute("SELECT * FROM profile_stickers WHERE id = ?", (json_data['id'],)).fetchone()
        assert sticker is not None
        assert sticker['sticker_type'] == 'image'
        assert sticker['image_path'] == json_data['image_path']
