
import pytest
import json
from flask import Flask

def test_backfill_pagination(app):
    """
    Verify that backfill supports pagination.
    """
    with app.test_client() as client:
        # Register a user
        client.post('/auth/register', json={'username': 'perf_test', 'password': 'password'})

        # Create 60 messages
        ids = []
        for i in range(60):
            res = client.post('/send', json={'content': f'Message {i}'})
            assert res.status_code == 200
            ids.append(res.get_json()['id'])

        # Request backfill (default limit 50)
        res = client.get('/backfill')
        assert res.status_code == 200
        messages = res.get_json()['messages']

        assert len(messages) == 50
        # Should be messages 10 to 59 (the latest 50)
        # Message 0 is oldest, Message 59 is newest.
        # So we expect [Message 10, ..., Message 59]
        assert messages[0]['content'] == 'Message 10'
        assert messages[-1]['content'] == 'Message 59'

        # Get the ID of the first message returned (oldest in this batch) to use as cursor
        oldest_msg_id = messages[0]['id']

        # Fetch older messages
        res = client.get(f'/backfill?before_id={oldest_msg_id}')
        assert res.status_code == 200
        older_messages = res.get_json()['messages']

        # Should return remaining 10 messages [Message 0, ..., Message 9]
        assert len(older_messages) == 10
        assert older_messages[0]['content'] == 'Message 0'
        assert older_messages[-1]['content'] == 'Message 9'
