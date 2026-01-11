
import pytest
from flask import json
from services.cats import seed_db

class TestCatRoutes:
    """Test suite for /cats endpoints."""

    @pytest.fixture(autouse=True)
    def seed_cats(self, app):
        """Seed the database with cats before each test in this class."""
        with app.app_context():
            seed_db()

    def test_list_cats(self, client):
        """Verify we can list cats."""
        res = client.get("/cats/")
        assert res.status_code == 200
        data = res.get_json()
        assert "cats" in data
        assert isinstance(data["cats"], list)
        # Assuming at least one cat exists (seeded or default)
        if len(data["cats"]) > 0:
            assert "name" in data["cats"][0]

    def test_speak_requires_login(self, client):
        """Verify /cats/speak requires login."""
        res = client.post("/cats/speak", json={"event": "test"})
        # Should redirect to login (302) or return 401 depending on config, 
        # but standard auth returns 302 for redirects.
        assert res.status_code == 302 or res.status_code == 401

    def test_speak_success(self, auth_client):
        """Verify an authenticated user can trigger a cat event."""
        res = auth_client.post("/cats/speak", json={
            "event": "login_success",
            "cat": "beans"
        })
        assert res.status_code == 200
        data = res.get_json()
        
        # Structure check based on docstring return value
        # Returns: {"cat": "beans", "state": "Playful", "sound": "purr.wav", "line": "..."}
        assert "cat" in data
        assert "state" in data
        assert "line" in data
        assert data["cat"] == "beans"
