
import pytest
import tempfile
import os
from app import create_app
from db import init_db, get_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app(test_config={
        "TESTING": True,
        "DATABASE": db_path,
    })
    
    with app.app_context():
        # Ensure migration manually or init_db handles SCHEMA
        # db.py SCHEMA was updated, so init_db is sufficient
        init_db()

    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def register(self, username="coder", password="password"):
        return self._client.post(
            "/auth/register", json={"username": username, "password": password}
        )

    def login(self, username="coder", password="password"):
        return self._client.post(
            "/auth/login", json={"username": username, "password": password}
        )
    
    def logout(self):
        return self._client.get("/auth/logout")

@pytest.fixture
def auth(client):
    return AuthActions(client)

def test_script_lifecycle(client, auth):
    # 1. Register & Login
    auth.register()
    auth.login()
    
    # 2. Save new script
    res = client.post("/scripts/save", json={
        "title": "My Cool Sketch",
        "content": "function setup() { createCanvas(400, 400); }",
        "script_type": "p5"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    script_id = data["id"]
    
    # 3. List scripts
    res = client.get("/scripts/list")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["scripts"]) == 1
    assert data["scripts"][0]["title"] == "My Cool Sketch"
    
    # 4. Get specific script
    res = client.get(f"/scripts/get?id={script_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["script"]["content"] == "function setup() { createCanvas(400, 400); }"
    
    # 5. Update script
    res = client.post("/scripts/save", json={
        "id": script_id,
        "title": "My Cooler Sketch",
        "content": "function setup() { createCanvas(800, 800); }",
        "script_type": "p5"
    })
    assert res.status_code == 200
    
    # Verify update
    res = client.get(f"/scripts/get?id={script_id}")
    assert res.get_json()["script"]["title"] == "My Cooler Sketch"
    
    # 6. Delete script
    res = client.post("/scripts/delete", json={"id": script_id})
    assert res.status_code == 200
    
    # Verify gone
    res = client.get(f"/scripts/get?id={script_id}")
    assert res.status_code == 404
