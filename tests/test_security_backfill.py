
import pytest
import msgspec
from db import get_db


def test_backfill_unauthorized_access(client):
    """
    VULNERABILITY CHECK:
    The /backfill endpoint should be protected by login.
    """
    res = client.get('/backfill')

    # 302 Redirect (to login) or 401 Unauthorized is expected if secure
    if res.status_code == 200:
        print("VULNERABILITY CONFIRMED: /backfill accessible without auth")
        pytest.fail("Endpoint is accessible without auth")
    else:
        print(f"Secure: Endpoint returned {res.status_code}")


def test_backfill_pagination_dos(auth_client, app):
    """
    VULNERABILITY CHECK:
    The /backfill endpoint should verify pagination limits.
    Currently it dumps the whole DB.
    """
    # Create 100 messages
    with app.app_context():
        db = get_db()
        for i in range(100):
            db.execute(
                "INSERT INTO messages (user, content) VALUES (?, ?)",
                (f"user{i}", f"msg{i}")
            )

    # Call backfill (authenticated)
    res = auth_client.get('/backfill')
    assert res.status_code == 200

    # Decode response using msgspec
    data = msgspec.json.decode(res.data)
    messages = data['messages']

    print(f"Backfill returned {len(messages)} messages")

    # If vulnerability exists, it returns all 100 messages
    if len(messages) == 100:
        print("VULNERABILITY CONFIRMED: /backfill returned all messages")
    else:
        print(f"Good: /backfill returned {len(messages)} messages")
        assert len(messages) <= 50, "Should return max 50 messages"
