
import pytest
from db import get_db

def test_backfill_access_protected(client, auth_client, app):
    """
    Verification:
    1. Test that unauthenticated access is BLOCKED (redirects to login).
    2. Test that authenticated access is ALLOWED.
    """
    # 1. Setup: Create a message
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO messages (user, content) VALUES ('victim', 'Secret Message')"
        )
        db.commit()

    # 2. Test Unauthenticated Access
    res = client.get('/backfill')
    assert res.status_code == 302, "Unauthenticated access should be redirected"
    assert "/auth/login" in res.headers["Location"], "Should redirect to login page"

    # 3. Test Authenticated Access
    # auth_client is a fixture that logs in a user 'testuser'
    res_auth = auth_client.get('/backfill')
    assert res_auth.status_code == 200, "Authenticated user should access backfill"
    assert b"Secret Message" in res_auth.data, "Authenticated user should see messages"
