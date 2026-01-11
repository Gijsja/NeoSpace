import pytest
from flask import Flask, g, request
from app import create_app
from db import get_db, init_db
from utils.decorators import log_admin_action

import tempfile
import os

@pytest.fixture
def app():
    # Use a file-based DB so it persists across request contexts
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({'TESTING': True, 'DATABASE': db_path})
    
    with app.app_context():
        init_db()
        
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_metrics_endpoint(client):
    """Test that /metrics returns 200 and prometheus format."""
    # Hit random page to increment counter
    client.get('/favicon.ico')
    
    res = client.get('/metrics')
    assert res.status_code == 200
    assert b'neospace_requests_total' in res.data
    # Counter should be at least 1 (favicon + maybe others)
    assert b'neospace_requests_total 1' in res.data or b'neospace_requests_total 2' in res.data 
    assert b'neospace_info' in res.data

def test_audit_log_decorator(app):
    """Test that @log_admin_action inserts into admin_ops."""
    
    @log_admin_action("test_action")
    def dummy_action():
        return "success"

    with app.test_request_context('/admin/dashboard', method='POST', data={'target': 'user:99'}):
        db = get_db()
        # Seed user for FK constraint
        db.execute("INSERT INTO users (id, username, password_hash, is_staff) VALUES (1, 'admin', 'hash', 1)")
        db.execute("INSERT INTO users (id, username, password_hash, is_staff) VALUES (2, 'user', 'hash', 0)")
        db.commit()

        # 1. No user logged in -> No log
        g.user = None
        dummy_action()
        count = db.execute("SELECT COUNT(*) FROM admin_ops").fetchone()[0]
        assert count == 0
        
        # 2. Regular user -> No log
        g.user = {'id': 2, 'is_staff': 0}
        dummy_action()
        count = db.execute("SELECT COUNT(*) FROM admin_ops").fetchone()[0]
        assert count == 0
        
        # 3. Staff user -> Log!
        g.user = {'id': 1, 'is_staff': 1}
        dummy_action()
        row = db.execute("SELECT * FROM admin_ops").fetchone()
        assert row is not None
        assert row['action'] == 'test_action'
        assert row['target'] == 'user:99'
        assert row['admin_id'] == 1
