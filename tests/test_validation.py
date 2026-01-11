import pytest
from core.validators import validate_username, validate_display_name, validate_bio

def test_validate_username():
    assert validate_username("valid_user") is None
    assert validate_username("a") == "Username must be at least 2 characters."
    assert validate_username("a" * 21) == "Username must be at most 20 characters."
    assert validate_username("invalid user") == "Username can only contain letters, numbers, underscores, and hyphens."
    assert validate_username("user!") == "Username can only contain letters, numbers, underscores, and hyphens."
    assert validate_username("") == "Username is required."

def test_validate_display_name():
    assert validate_display_name("Cool User") is None
    assert validate_display_name("a" * 51) == "Display name must be at most 50 characters."

def test_validate_bio():
    assert validate_bio("This is a bio.") is None
    assert validate_bio("a" * 161) == "Bio must be at most 160 characters."

def test_registration_validation(client):
    """Test that registration endpoint enforces username rules."""
    # Too short
    rv = client.post("/auth/register", json={"username": "a", "password": "password"})
    assert rv.status_code == 400
    assert "Username must be at least 2 characters" in rv.get_json()["error"]
    
    # Invalid chars
    rv = client.post("/auth/register", json={"username": "bad user", "password": "password"})
    assert rv.status_code == 400
    assert "can only contain letters" in rv.get_json()["error"]

def test_profile_validation(auth_client):
    """Test that profile update enforces length limits."""
    # Long bio
    rv = auth_client.post("/profile/update", json={"bio": "a" * 200})
    assert rv.status_code == 400
    assert "Bio must be at most 160 characters" in rv.get_json()["error"]
    
    # Long status
    rv = auth_client.post("/profile/update", json={"status_message": "a" * 101})
    assert rv.status_code == 400
    assert "Status message exceeds maximum length" in rv.get_json()["error"]
