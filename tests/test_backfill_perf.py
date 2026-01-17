
import pytest
from flask import json
from db import get_db

def test_backfill_defaults_to_50_messages(app):
    """
    Verify that backfill now defaults to 50 recent messages.
    """
    with app.app_context():
        db = get_db()
        # Create 60 messages
        for i in range(60):
            db.execute("INSERT INTO messages (user, content) VALUES (?, ?)", (f"user{i}", f"msg{i}"))
        db.commit()

    with app.test_client() as client:
        res = client.get("/backfill")
        data = res.get_json()

        # Expect only 50 messages
        assert len(data["messages"]) == 50

        # Verify it's the *latest* 50 messages, but in ascending order
        # So we expect msg10 to msg59
        assert data["messages"][0]["content"] == "msg10"
        assert data["messages"][-1]["content"] == "msg59"

def test_backfill_respects_limit(app):
    """
    Verify that backfill respects the limit parameter.
    """
    with app.app_context():
        db = get_db()
        # Create 20 messages
        for i in range(20):
            db.execute("INSERT INTO messages (user, content) VALUES (?, ?)", (f"user{i}", f"msg{i}"))
        db.commit()

    with app.test_client() as client:
        # Request limit=5
        res = client.get("/backfill?limit=5")
        data = res.get_json()

        assert len(data["messages"]) == 5
        # Should be msg15 to msg19
        assert data["messages"][0]["content"] == "msg15"
        assert data["messages"][-1]["content"] == "msg19"

def test_backfill_limit_clamping(app):
    """
    Verify limit is clamped between 1 and 100.
    """
    with app.app_context():
        db = get_db()
        # Create 110 messages
        for i in range(110):
            db.execute("INSERT INTO messages (user, content) VALUES (?, ?)", (f"user{i}", f"msg{i}"))
        db.commit()

    with app.test_client() as client:
        # Request limit=200 -> clamped to 100
        res = client.get("/backfill?limit=200")
        data = res.get_json()
        assert len(data["messages"]) == 100

        # Request limit=0 -> clamped to 1
        res = client.get("/backfill?limit=0")
        data = res.get_json()
        assert len(data["messages"]) == 1

def test_backfill_pagination(app):
    """
    Verify that backfill supports pagination via before_id.
    """
    with app.app_context():
        db = get_db()
        # Create 20 messages. IDs will be 1 to 20.
        for i in range(20):
            db.execute("INSERT INTO messages (user, content) VALUES (?, ?)", (f"user{i}", f"msg{i}"))
        db.commit()

    with app.test_client() as client:
        # 1. Fetch latest 5 messages (msg15-msg19)
        # IDs: 16, 17, 18, 19, 20
        res = client.get("/backfill?limit=5")
        data = res.get_json()
        messages = data["messages"]
        assert len(messages) == 5
        assert messages[-1]["id"] == 20
        assert messages[0]["id"] == 16

        # 2. Fetch 5 messages before ID 16
        # Should be IDs 11, 12, 13, 14, 15
        oldest_id = messages[0]["id"]
        res = client.get(f"/backfill?limit=5&before_id={oldest_id}")
        data = res.get_json()
        prev_messages = data["messages"]

        assert len(prev_messages) == 5
        assert prev_messages[-1]["id"] == 15
        assert prev_messages[0]["id"] == 11
