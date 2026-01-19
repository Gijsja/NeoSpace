
import pytest
from db import get_db

def test_backfill_limit_default(auth_client, app):
    """
    Verify that backfill defaults to 50 messages limit.
    """
    # Create 60 messages
    with app.app_context():
        db = get_db()
        params = []
        for i in range(60):
            params.append((f"user_{i}", f"content_{i}", 1))

        db.executemany(
            "INSERT INTO messages(user, content, room_id) VALUES (?, ?, ?)",
            params
        )
        db.commit()

    # Fetch backfill
    res = auth_client.get("/backfill")
    assert res.status_code == 200
    data = res.get_json()
    messages = data["messages"]

    # Should be capped at 50
    assert len(messages) == 50

    # And should be the LATEST 50 messages (chronological order)
    # The last message inserted was content_59
    # So messages[-1] should be content_59
    assert messages[-1]["content"] == "content_59"
    # The first message in the list should be content_10 (60-50=10)
    assert messages[0]["content"] == "content_10"

def test_backfill_custom_limit(auth_client, app):
    """Verify custom limit works."""
    # Create 15 messages
    with app.app_context():
        db = get_db()
        params = []
        for i in range(15):
            params.append((f"user_{i}", f"content_{i}", 1))
        db.executemany(
            "INSERT INTO messages(user, content, room_id) VALUES (?, ?, ?)",
            params
        )
        db.commit()

    res = auth_client.get("/backfill?limit=10")
    data = res.get_json()
    assert len(data["messages"]) == 10
    # Should be latest 10 (content_5 to content_14)
    assert data["messages"][-1]["content"] == "content_14"
    assert data["messages"][0]["content"] == "content_5"

def test_backfill_room_filter(auth_client, app):
    """Verify room filtering."""
    with app.app_context():
        db = get_db()
        # Room 1: 5 msgs
        for i in range(5):
             db.execute("INSERT INTO messages(user, content, room_id) VALUES (?, ?, ?)", ("u", f"r1_{i}", 1))
        # Room 2: 5 msgs
        for i in range(5):
             db.execute("INSERT INTO messages(user, content, room_id) VALUES (?, ?, ?)", ("u", f"r2_{i}", 2))
        db.commit()

    # Default room_id=1
    res = auth_client.get("/backfill")
    data = res.get_json()
    assert len(data["messages"]) == 5
    assert all("r1_" in m["content"] for m in data["messages"])

    # room_id=2
    res = auth_client.get("/backfill?room_id=2")
    data = res.get_json()
    assert len(data["messages"]) == 5
    assert all("r2_" in m["content"] for m in data["messages"])
