
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

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def register(self, username="testuser", password="password"):
            return self._client.post(
                "/auth/register", json={"username": username, "password": password}
            )

        def login(self, username="testuser", password="password"):
            return self._client.post(
                "/auth/login", json={"username": username, "password": password}
            )

    return AuthActions(client)

def test_sticker_workflow(client, auth, app):
    # 1. Register and Login
    auth.register()
    auth.login()
    
    # 2. Add Sticker
    res = client.post("/profile/sticker/add", json={
        "sticker_type": "🔥",
        "x": 100,
        "y": 200
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    sticker_id = data["id"]
    
    # 3. Verify Sticker in Profile
    res = client.get("/profile")
    assert res.status_code == 200
    profile = res.get_json()
    assert "stickers" in profile
    assert len(profile["stickers"]) == 1
    s = profile["stickers"][0]
    assert s["id"] == sticker_id
    assert s["sticker_type"] == "🔥"
    assert s["x_pos"] == 100
    
    # 4. Update Sticker
    res = client.post("/profile/sticker/update", json={
        "id": sticker_id,
        "x": 150,
        "scale": 1.5,
        "rotation": 45
    })
    assert res.status_code == 200
    
    # Verify Update
    res = client.get("/profile")
    s = res.get_json()["stickers"][0]
    assert s["x_pos"] == 150
    assert s["scale"] == 1.5
    
    # 5. Remove Sticker
    res = client.post("/profile/sticker/remove", json={"id": sticker_id})
    assert res.status_code == 200
    
    # Verify Removal
    res = client.get("/profile")
    assert len(res.get_json()["stickers"]) == 0

if __name__ == "__main__":
    # Quick run without pytest
    # But imports might fail if not running as module
    pass
