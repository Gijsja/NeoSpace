from sockets import socketio
from db import get_db


def test_backfill_pagination(app, client):
    """Verify that backfill requests are paginated."""
    # 1. Register and Authenticate
    client.post(
        "/auth/register",
        json={"username": "limit_tester", "password": "password"},
    )

    # 2. Seed Database with 150 messages
    with app.app_context():
        db = get_db()
        # Ensure room 1 exists (it should by default or be created)
        db.execute("INSERT OR IGNORE INTO rooms (id, name) VALUES (1, 'general')")

        messages = []
        for i in range(150):
            # i=0 -> Message 0
            messages.append(("limit_tester", f"Message {i}", 1))

        db.executemany(
            "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
            messages,
        )
        db.commit()

        # Verify IDs are sequential starting from 1 (or whatever next is)
        rows = db.execute("SELECT id, content FROM messages ORDER BY id").fetchall()
        first_id = rows[0]["id"]
        assert len(rows) == 150

    # 3. Connect Socket
    # Must use client that has the session cookie from login
    sio = socketio.test_client(app, flask_test_client=client)
    assert sio.is_connected()

    # 4. Request Initial Backfill (after_id=0)
    sio.emit("request_backfill", {"after_id": 0})

    received = sio.get_received()
    backfill_events = [e for e in received if e["name"] == "backfill"]
    assert len(backfill_events) > 0
    data = backfill_events[0]["args"][0]
    messages = data["messages"]

    # 5. Verify Limits (Initial Load)
    # Should only get 100 messages
    assert len(messages) == 100

    # Should be the LATEST 100 messages, in chronological order
    # If we have 150 messages, we expect messages 50 to 149
    # (Assuming we started empty and IDs are 1..150)

    # content of the first returned message should be "Message 50"
    assert messages[0]["content"] == "Message 50"
    # content of the last returned message should be "Message 149"
    assert messages[-1]["content"] == "Message 149"

    # 6. Verify Sync Limit
    # Need to insert more messages to test sync limit (>500)
    # But checking that it returns correct data for small sync is good too

    # Request sync after the 50th message (ID = first_id + 49)
    sync_after_id = first_id + 49
    sio.emit("request_backfill", {"after_id": sync_after_id})

    received = sio.get_received()
    backfill_events = [e for e in received if e["name"] == "backfill"]
    data = backfill_events[0]["args"][0]
    messages = data["messages"]

    # Should return messages 51..149 (Total 100)
    assert len(messages) == 100
    # Wait. ID > 50 (if first_id=1). ID 51 is Message 50. Correct.
    assert messages[0]["content"] == "Message 50"

    sio.disconnect()
