
import pytest

def test_backfill_public_access(client):
    """
    Verify that /backfill is NO LONGER accessible without authentication.
    """
    response = client.get('/backfill')
    # Should redirect to login page (302)
    assert response.status_code == 302
    # Verify it redirects to login
    assert '/auth/login' in response.headers['Location']
