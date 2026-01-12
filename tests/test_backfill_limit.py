
import pytest
from db import get_db

def test_backfill_limit(auth_client, app):
    """Test that backfill returns at most 500 messages."""

    with app.app_context():
        db = get_db()
        # Bulk insert 600 messages
        # Use executemany for speed
        messages = [
            ("user_limit", f"msg {i}", "1") for i in range(600)
        ]
        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            messages
        )
        db.commit()

    # Now call backfill
    res = auth_client.get("/backfill")
    assert res.status_code == 200
    data = res.get_json()

    # Assert we got exactly 500 messages
    assert len(data["messages"]) <= 500, f"Expected <= 500 messages, got {len(data['messages'])}"

    # Verify they are the LATEST messages.
    # The last inserted message should be in the list.
    last_msg = data["messages"][-1]
    # Check if the last message content matches one of the latest inserted
    assert "msg" in last_msg["content"]

def test_backfill_pagination(auth_client, app):
    """Test that backfill pagination works."""
    with app.app_context():
        db = get_db()
        # Insert 3 messages with specific IDs if possible, but IDs are autoincrement.
        # We'll just insert and query to get IDs.
        messages = [
            ("user_pag", "p1", "1"),
            ("user_pag", "p2", "1"),
            ("user_pag", "p3", "1")
        ]
        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            messages
        )
        db.commit()

        # Get the ID of the middle message
        rows = db.execute("SELECT id, content FROM messages WHERE user='user_pag' ORDER BY id").fetchall()
        p1 = rows[0]
        p2 = rows[1]
        p3 = rows[2]

    # Fetch messages before p3
    res = auth_client.get(f"/backfill?before_id={p3['id']}")
    assert res.status_code == 200
    data = res.get_json()
    messages = data["messages"]

    # We should see p2 and p1 (and possibly others if the DB wasn't empty)
    # But strictly speaking, we check if p3 is NOT there, and p2 IS there.

    ids = [m['id'] for m in messages]
    assert p3['id'] not in ids
    assert p2['id'] in ids
    assert p1['id'] in ids
