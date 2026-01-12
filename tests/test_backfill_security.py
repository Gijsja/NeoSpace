
import pytest
from flask import json
from db import get_db

def test_backfill_leak_repro(auth_client, app):
    """
    Reproduction of Information Disclosure Vulnerability in /backfill.
    Messages from ALL rooms are currently returned by the HTTP endpoint.
    """
    with app.app_context():
        db = get_db()

        # Ensure we have two distinct rooms
        db.execute("INSERT OR IGNORE INTO rooms (name) VALUES ('general')")
        general_room_id = db.execute("SELECT id FROM rooms WHERE name = 'general'").fetchone()['id']

        db.execute("INSERT OR IGNORE INTO rooms (name) VALUES ('secret_room')")
        secret_room_id = db.execute("SELECT id FROM rooms WHERE name = 'secret_room'").fetchone()['id']

        # Ensure they are different
        assert general_room_id != secret_room_id

        # Insert a message into the general room
        db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                   ('user1', 'Public Message', general_room_id))

        # Insert a message into the secret room
        db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                   ('user1', 'Secret Message', secret_room_id))

        db.commit()

    # Authenticated user requests backfill for general room (default)
    # The default in backfill.py is 1. But here general_room_id might not be 1 if other tests ran.
    # However, for the reproduction to work robustly, we should request the specific room we expect public msg in.
    # OR rely on the fact that we test the *leak* into the default view.

    # Let's request explicit room 1 (assuming general gets 1, or forcing it).
    # But wait, the vulnerability was that it returned ALL messages regardless of room.
    # Now the fix filters by room_id=1 by default.
    # So if I request without params, it searches room 1.

    # If general_room_id is 1, it should show Public, hide Secret (if Secret is 2).
    # If general_room_id is 2, and Secret is 3... requesting default (1) should show nothing?

    # To properly test the fix, we should query specifically for the general room
    # AND verify the secret room message is NOT present.

    res = auth_client.get(f"/backfill?room_id={general_room_id}")
    assert res.status_code == 200

    data = res.json
    messages = data['messages']

    # Check if Secret Message is leaked
    leaked_msg = next((m for m in messages if m['content'] == 'Secret Message'), None)

    # This assertion CONFIRMS the fix if it passes (i.e., message is NOT found)
    assert leaked_msg is None, "Vulnerability Persists: Secret message was returned."

    # Check if Public Message is returned
    public_msg = next((m for m in messages if m['content'] == 'Public Message'), None)
    assert public_msg is not None, "Regression: Public message missing from correct room"

def test_backfill_limit(auth_client, app):
    """
    Verify DoS protection (limit 500).
    """
    with app.app_context():
        db = get_db()
        # Create room 1 if not exists (likely created above but scope might differ)
        db.execute("INSERT OR IGNORE INTO rooms (id, name) VALUES (1, 'general')")

        # Insert 600 messages
        for i in range(600):
             db.execute("INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                   ('bot', f'Msg {i}', 1))
        db.commit()

    res = auth_client.get("/backfill?room_id=1")
    assert res.status_code == 200
    messages = res.json['messages']

    assert len(messages) == 500
    # Should be the *latest* 500. So Msg 599 should be present.
    # Since we order by ID DESC (newest first) then reverse, the last element in list is the newest.
    assert messages[-1]['content'] == 'Msg 599'
