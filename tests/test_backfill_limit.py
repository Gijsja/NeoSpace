
def test_backfill_pagination(auth_client):
    """
    Verify that backfill endpoint limits response and supports pagination.
    """
    # 1. Post 70 messages
    total_messages = 70
    for i in range(total_messages):
        auth_client.post("/send", json={"content": f"Message {i}"})

    # 2. Request first page (last 50)
    res = auth_client.get("/backfill")
    assert res.status_code == 200
    data = res.get_json()
    messages = data["messages"]
    assert len(messages) == 50

    # The messages are ordered chronologically (oldest -> newest).
    # To paginate backwards, we take the ID of the oldest message (index 0).
    oldest_id = messages[0]["id"]
    oldest_content = messages[0]["content"]

    # Verify content of the cutoff point
    # Message 69 is last. Message 20 is the 50th from last (indices 20..69 = 50 items).
    assert messages[-1]["content"] == f"Message {total_messages - 1}"
    assert oldest_content == f"Message {total_messages - 50}"

    # 3. Request second page (older than oldest_id)
    res_page2 = auth_client.get(f"/backfill?before_id={oldest_id}")
    assert res_page2.status_code == 200
    data_page2 = res_page2.get_json()
    messages_page2 = data_page2["messages"]

    # Should get remaining 20 messages (indices 0..19)
    assert len(messages_page2) == 20

    # Check content
    # Last message of page 2 should be the one just before the oldest of page 1
    assert messages_page2[-1]["content"] == f"Message {total_messages - 51}"
    assert messages_page2[0]["content"] == "Message 0"
