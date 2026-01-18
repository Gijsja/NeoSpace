
import pytest
from core.schemas import Message

def test_backfill_pagination_limit(auth_client):
    """Test that limit parameter works."""
    # Seed 5 messages
    for i in range(5):
        auth_client.post("/send", json={"content": f"Message {i}"})

    # Request limit=2
    res = auth_client.get("/backfill?limit=2")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["messages"]) == 2

    # Verify we got the latest 2 (chronological order)
    # Message 3 and 4 (if 0-indexed)
    assert "Message 3" in data["messages"][0]["content"]
    assert "Message 4" in data["messages"][1]["content"]

def test_backfill_pagination_after_id(auth_client):
    """Test using after_id to fetch newer messages."""
    # Seed 3 messages
    ids = []
    for i in range(3):
        res = auth_client.post("/send", json={"content": f"Message {i}"})
        ids.append(res.get_json()["id"])

    # Ask for messages after the first one
    res = auth_client.get(f"/backfill?after_id={ids[0]}")
    data = res.get_json()

    # Should get messages 2 and 3 (indices 1 and 2)
    assert len(data["messages"]) == 2
    assert data["messages"][0]["id"] == ids[1]
    assert data["messages"][1]["id"] == ids[2]

def test_backfill_pagination_before_id(auth_client):
    """Test using before_id to fetch older messages."""
    # Seed 5 messages
    ids = []
    for i in range(5):
        res = auth_client.post("/send", json={"content": f"Message {i}"})
        ids.append(res.get_json()["id"])

    # Ask for messages before the last one (limit 2)
    # This should return the 2 messages immediately preceding the last one
    target_id = ids[4]
    res = auth_client.get(f"/backfill?before_id={target_id}&limit=2")
    data = res.get_json()

    assert len(data["messages"]) == 2
    # Should be Message 2 and Message 3
    assert data["messages"][0]["id"] == ids[2]
    assert data["messages"][1]["id"] == ids[3]
