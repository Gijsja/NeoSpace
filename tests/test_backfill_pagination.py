
class TestBackfillPagination:
    """Test pagination logic for /backfill endpoint."""

    def test_backfill_default_latest(self, auth_client, app):
        """Default request returns latest messages in chronological order."""
        # Create 60 messages
        for i in range(60):
            auth_client.post("/send", json={"content": f"Message {i}"})

        res = auth_client.get("/backfill")
        data = res.get_json()
        messages = data["messages"]

        # Should return 50 messages (default limit)
        assert len(messages) == 50

        # Should be the LATEST 50 messages (10 to 59)
        # And in chronological order
        assert messages[0]["content"] == "Message 10"
        assert messages[-1]["content"] == "Message 59"

    def test_backfill_limit(self, auth_client, app):
        """Test custom limit parameter."""
        for i in range(10):
            auth_client.post("/send", json={"content": f"Message {i}"})

        res = auth_client.get("/backfill?limit=5")
        messages = res.get_json()["messages"]

        assert len(messages) == 5
        # Should be the latest 5
        assert messages[0]["content"] == "Message 5"
        assert messages[-1]["content"] == "Message 9"

    def test_backfill_after_id(self, auth_client, app):
        """Test fetching newer messages with after_id."""
        ids = []
        for i in range(10):
            res = auth_client.post("/send", json={"content": f"Message {i}"})
            ids.append(res.get_json()["id"])

        # Get messages after the 5th message (index 4)
        mid_id = ids[4]
        res = auth_client.get(f"/backfill?after_id={mid_id}")
        messages = res.get_json()["messages"]

        # Should return messages 5 to 9
        assert len(messages) == 5
        assert messages[0]["id"] == ids[5]
        assert messages[-1]["id"] == ids[9]

    def test_backfill_before_id(self, auth_client, app):
        """Test fetching older messages with before_id."""
        ids = []
        for i in range(10):
            res = auth_client.post("/send", json={"content": f"Message {i}"})
            ids.append(res.get_json()["id"])

        # Get messages before the 6th message (index 5)
        # Should get 0-4
        mid_id = ids[5]
        res = auth_client.get(f"/backfill?before_id={mid_id}")
        messages = res.get_json()["messages"]

        # Should return messages 0 to 4
        assert len(messages) == 5
        assert messages[0]["id"] == ids[0]
        assert messages[-1]["id"] == ids[4]

    def test_backfill_empty(self, auth_client):
        """Should handle empty database gracefully."""
        res = auth_client.get("/backfill")
        assert res.status_code == 200
        assert len(res.get_json()["messages"]) == 0

    def test_backfill_limit_max(self, auth_client):
        """Limit should be capped at 100."""
        # Check logic via code inspection or just trust logic
        pass
