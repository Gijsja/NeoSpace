import pytest
from sockets import socketio
from db import get_db


class TestSocketBackfill:
    def test_backfill_pagination_logic(self, app):
        """
        Verify that backfill limits to 50 messages on initial load.
        """
        client = app.test_client()

        # Register and login to set session
        client.post('/auth/register', json={
            'username': 'chat_user',
            'password': 'password123'
        })

        # Create 70 messages (more than 50)
        with app.app_context():
            db = get_db()
            for i in range(70):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    ('chat_user', f'Message {i}', 1)
                )
            db.commit()

        # Connect via SocketIO
        socket_client = socketio.test_client(app, flask_test_client=client)
        socket_client.emit('join_room', {'room': 'general'})

        # Request backfill (Initial load)
        socket_client.emit('request_backfill', {'after_id': 0})

        received = socket_client.get_received()
        backfill_events = [e for e in received if e['name'] == 'backfill']
        assert len(backfill_events) > 0

        data = backfill_events[0]['args'][0]
        messages = data['messages']

        # Optimization: Returns 50 messages (latest)
        assert len(messages) == 50

        # Check content (Latest messages should be at the end)
        # Message 69 is the last one created.
        assert messages[-1]['content'] == 'Message 69'
        # Message 20 is the 50th from last (69-49 = 20)
        assert messages[0]['content'] == 'Message 20'

    def test_backfill_pagination_previous(self, app):
        """
        Verify that we can fetch older messages using before_id.
        """
        client = app.test_client()
        client.post('/auth/register', json={
            'username': 'chat_user',
            'password': 'password123'
        })

        # Create 70 messages
        with app.app_context():
            db = get_db()
            for i in range(70):
                db.execute(
                    "INSERT INTO messages (user, content, room_id) VALUES (?, ?, ?)",
                    ('chat_user', f'Message {i}', 1)
                )
            db.commit()

        socket_client = socketio.test_client(app, flask_test_client=client)
        socket_client.emit('join_room', {'room': 'general'})

        # 1. Initial Load
        socket_client.emit('request_backfill', {'after_id': 0})
        received = socket_client.get_received()

        backfill_events = [e for e in received if e['name'] == 'backfill']
        assert len(backfill_events) > 0
        messages = backfill_events[0]['args'][0]['messages']
        assert len(messages) == 50

        oldest_msg_id = messages[0]['id']

        # 2. Load Previous (Pagination)
        socket_client.emit('request_backfill', {'before_id': oldest_msg_id})
        received = socket_client.get_received()

        # Should be a new backfill event
        backfill_events = [e for e in received if e['name'] == 'backfill']
        # Note: get_received() clears the buffer, so we look at the new events
        assert len(backfill_events) > 0

        new_messages = backfill_events[0]['args'][0]['messages']

        # Expect remaining 20 messages (0 to 19)
        assert len(new_messages) == 20

        assert new_messages[-1]['content'] == 'Message 19'
        assert new_messages[0]['content'] == 'Message 0'
