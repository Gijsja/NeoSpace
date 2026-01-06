
import pytest
from app import create_app
from db import init_db, get_db

import tempfile
import os

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app(test_config={
        "TESTING": True,
        "DATABASE": db_path,
    })
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def register(self, username, password="password"):
        return self._client.post(
            "/auth/register", json={"username": username, "password": password}
        )

    def login(self, username, password="password"):
        return self._client.post(
            "/auth/login", json={"username": username, "password": password}
        )
    
    def logout(self):
        return self._client.get("/auth/logout")

@pytest.fixture
def auth(client):
    return AuthActions(client)

def test_guestbook_flow(client, auth, app):
    # 1. Create Host (User A)
    auth.register("host_user")
    # Get host ID
    with app.app_context():
        db = get_db()
        host = db.execute("SELECT id FROM users WHERE username='host_user'").fetchone()
        host_id = host["id"]
        
    auth.logout()
    
    # 2. Create Guest (User B)
    res = auth.register("guest_user")
    assert res.status_code == 200, f"Register failed: {res.get_json()}"
    
    # Explicit login to be safe
    auth.login("guest_user")
    # Guest is logged in
    
    # 3. Guest adds sticker to Host's wall
    res = client.post("/profile/sticker/add", json={
        "sticker_type": "🎁",
        "x": 50,
        "y": 50,
        "target_user_id": host_id
    })
    assert res.status_code == 200, f"Error: {res.get_json()}"
    data = res.get_json()
    assert data["ok"] is True
    sticker_id = data["id"]
    
    # 4. Verify Sticker exists on Host's profile
    res = client.get(f"/profile?user_id={host_id}")
    assert res.status_code == 200
    profile = res.get_json()
    stickers = profile["stickers"]
    assert len(stickers) == 1
    s = stickers[0]
    assert s["sticker_type"] == "🎁"
    assert s["placed_by_username"] == "guest_user"
    
    # 5. Verify Guest cannot delete sticker if logic forbids? 
    # Current logic allows guest to delete THEIR OWN sticker.
    res = client.post("/profile/sticker/remove", json={"id": sticker_id})
    assert res.status_code == 200 # Should succeed
    
    # Re-add to test Host deletion
    res = client.post("/profile/sticker/add", json={
        "sticker_type": "🎁",
        "x": 50, 
        "y": 50,
        "target_user_id": host_id
    })
    sticker_id_2 = res.get_json()["id"]
    
    auth.logout()
    
    # 6. Host logs in and deletes Guest's sticker
    auth.login("host_user")
    res = client.post("/profile/sticker/remove", json={"id": sticker_id_2})
    assert res.status_code == 200
    
    # Verify empty
    res = client.get(f"/profile?user_id={host_id}")
    assert len(res.get_json()["stickers"]) == 0

