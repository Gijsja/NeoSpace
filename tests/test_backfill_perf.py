
import pytest
from db import get_db

def test_backfill_filters_by_room(auth_client, app):
    """
    Verify that backfill now correctly filters messages by room_id.
    """
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM messages")

        # Insert message in Room 1 (General)
        db.execute(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            ("user1", "Message in Room 1", 1)
        )

        # Insert message in Room 2 (Secret)
        db.execute(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            ("user2", "Message in Room 2", 2)
        )
        db.commit()

    # Request backfill (default room_id=1)
    res = auth_client.get("/backfill")
    assert res.status_code == 200
    data = res.json

    # Verify we ONLY got message from Room 1
    content_list = [m['content'] for m in data['messages']]
    assert "Message in Room 1" in content_list
    assert "Message in Room 2" not in content_list

def test_backfill_filters_by_room_param(auth_client, app):
    """
    Verify that we can request a specific room.
    """
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM messages")
        db.execute(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            ("user2", "Message in Room 2", 2)
        )
        db.commit()

    # Request backfill for room 2
    res = auth_client.get("/backfill?room_id=2")
    assert res.status_code == 200
    data = res.json

    content_list = [m['content'] for m in data['messages']]
    assert "Message in Room 2" in content_list

def test_backfill_limit(auth_client, app):
    """
    Verify the limit works.
    """
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM messages")
        for i in range(10):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ("user1", f"Message {i}", 1)
            )
        db.commit()

    # Request limit 5
    res = auth_client.get("/backfill?limit=5")
    assert res.status_code == 200
    data = res.json

    assert len(data['messages']) == 5
    # Should be first 5 since we order by ID ASC (oldest first after 'after_id')
    # If we requested default (after_id=0), we get the oldest messages first.
    # Wait, if I insert 10 messages, IDs will be 1..10.
    # ORDER BY ID ASC LIMIT 5 -> IDs 1, 2, 3, 4, 5.
    assert data['messages'][0]['content'] == "Message 0"
    assert data['messages'][4]['content'] == "Message 4"

def test_backfill_after_id(auth_client, app):
    """
    Verify after_id pagination.
    """
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM messages")
        # Insert 10 messages
        for i in range(10):
            db.execute(
                "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                ("user1", f"Message {i}", 1)
            )
        db.commit()

        # Get ID of the 5th message
        rows = db.execute("SELECT id FROM messages ORDER BY id ASC").fetchall()
        fifth_id = rows[4]['id'] # 0-indexed, so 5th item

    # Request messages after 5th message
    res = auth_client.get(f"/backfill?after_id={fifth_id}")
    assert res.status_code == 200
    data = res.json

    # Should get messages 6, 7, 8, 9, 10 (indices 5..9)
    assert len(data['messages']) == 5
    assert data['messages'][0]['content'] == "Message 5"
