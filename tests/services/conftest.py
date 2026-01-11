"""
Service layer test fixtures.
Provides isolated database and test users for fast, focused unit tests.

Uses a minimal Flask app context to satisfy db.get_db() requirements.
"""

import os
import sys
import tempfile
import pytest
from flask import Flask

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import db as db_module
from db import get_db, init_db


@pytest.fixture
def db_session():
    """
    Create an isolated test database with Flask app context.
    Uses a temp file to allow multiple connections if needed.
    """
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Override module-level DB path
    original_path = db_module.DB_PATH
    db_module.DB_PATH = db_path
    
    # Create minimal Flask app for context
    app = Flask(__name__)
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    # Required for DM encryption (core.crypto derives key from this)
    app.secret_key = "dev_secret_key_DO_NOT_USE_IN_PROD"
    
    with app.app_context():
        # Initialize schema
        init_db()
        
        yield get_db()
    
    # Cleanup
    db_module.DB_PATH = original_path
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def test_user(db_session):
    """
    Create a test user with profile.
    Returns dict with user_id, profile_id, username.
    """
    db = db_session
    
    # Create user
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("testuser", "fakehash123")
    )
    user_id = cursor.lastrowid
    
    # Create profile
    cursor = db.execute(
        "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
        (user_id, "Test User")
    )
    profile_id = cursor.lastrowid
    
    db.commit()
    
    return {
        "user_id": user_id,
        "profile_id": profile_id,
        "username": "testuser"
    }


@pytest.fixture
def second_user(db_session):
    """
    Create a second user for permission/ownership tests.
    """
    db = db_session
    
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("otheruser", "fakehash456")
    )
    user_id = cursor.lastrowid
    
    cursor = db.execute(
        "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
        (user_id, "Other User")
    )
    profile_id = cursor.lastrowid
    
    db.commit()
    
    return {
        "user_id": user_id,
        "profile_id": profile_id,
        "username": "otheruser"
    }
