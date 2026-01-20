import pytest

class TestBackfillSecurity:
    """Test security of chat endpoints."""

    def test_backfill_unauthenticated(self, client):
        """Test that /backfill requires authentication."""
        # Ensure we are logged out
        client.get('/auth/logout')

        # Access /backfill
        res = client.get('/backfill')

        # Should redirect to login (302) or return Unauthorized (401)
        # Currently this will likely return 200 (Fail)
        assert res.status_code in [302, 401], f"Expected 302/401, got {res.status_code}"

    def test_unread_unauthenticated(self, client):
        """Test that /unread requires authentication."""
        client.get('/auth/logout')

        res = client.get('/unread')

        assert res.status_code in [302, 401], f"Expected 302/401, got {res.status_code}"
