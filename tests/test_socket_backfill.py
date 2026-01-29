
import pytest
from sockets import socketio
from db import get_db

class TestSocketBackfill:
    def test_backfill_limit_initial_load(self, app, auth_client):
        """
        Verify that initial backfill (after_id=0) is limited to 100 messages.
        """
        # 1. Seed 150 messages
        with app.app_context():
            db = get_db()
            for i in range(150):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    ('testuser', f'msg-{i}', 1)
                )
            db.commit()

        # 2. Connect via Socket
        # auth_client is already logged in (from conftest fixture)
        socket_client = socketio.test_client(app, flask_test_client=auth_client)
        assert socket_client.is_connected()

        # 3. Join room (triggers request_backfill in frontend, but here we emit manually to be sure)
        socket_client.emit('join_room', {'room': 'general'})

        # 4. Request backfill
        socket_client.emit('request_backfill', {'after_id': 0})

        # 5. Receive backfill response
        received = socket_client.get_received()

        # Search for 'backfill' event
        backfill_event = None
        for event in received:
            if event['name'] == 'backfill':
                backfill_event = event
                break

        assert backfill_event is not None
        payload = backfill_event['args'][0]
        messages = payload['messages']

        # 6. Assert limit (Should be 100)
        # CURRENT BEHAVIOR: This will fail because it returns 150
        print(f"Received {len(messages)} messages")
        assert len(messages) == 100

        # 7. Assert we got the LATEST messages (msg-50 to msg-149)
        # Since we inserted 0 to 149.
        # msg-0 is the oldest. msg-149 is the newest.
        # We expect msg-50 ... msg-149.
        assert messages[0]['content'] == 'msg-50'
        assert messages[-1]['content'] == 'msg-149'

    def test_backfill_limit_sync(self, app, auth_client):
        """
        Verify that sync backfill (after_id > 0) is limited to 500 messages.
        """
        # 1. Seed 600 messages
        with app.app_context():
            db = get_db()
            # Clear previous messages
            db.execute("DELETE FROM messages")
            for i in range(600):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    ('testuser', f'msg-{i}', 1)
                )
            db.commit()

        socket_client = socketio.test_client(app, flask_test_client=auth_client)
        socket_client.emit('join_room', {'room': 'general'})

        # 4. Request backfill from 0 (simulating catch up from beginning, but using > 0 logic?)
        # Wait, the logic handles after_id=0 specifically.
        # Let's request from ID 10.
        socket_client.emit('request_backfill', {'after_id': 10})

        received = socket_client.get_received()
        backfill_event = next(e for e in received if e['name'] == 'backfill')
        messages = backfill_event['args'][0]['messages']

        # Should be limited to 500
        # If we asked for > 10. We have IDs roughly 1 to 600.
        # So we expect ~590 messages. Limit is 500.
        assert len(messages) == 500
        # Should start from the one after 10.
        # Note: IDs might not be perfectly 1-600 due to autoincrement and previous tests.
        # But they are sequential.
