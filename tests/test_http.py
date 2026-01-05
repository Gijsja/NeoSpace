
def test_root_serves_ui(client):
    """Root endpoint serves the HTML UI."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"<!DOCTYPE html>" in res.data or b"<html" in res.data


def test_unread_endpoint(client):
    """Unread endpoint returns count."""
    res = client.get("/unread")
    assert res.status_code == 200
    data = res.get_json()
    assert "count" in data
    assert isinstance(data["count"], int)


def test_unread_count_increases_with_messages(client, app):
    """Unread count should increase as messages are added."""
    # Initial count
    res = client.get("/unread")
    initial_count = res.get_json()["count"]
    
    # Add messages
    client.post("/send", json={"content": "Message 1"}, headers={"X-User": "alice"})
    client.post("/send", json={"content": "Message 2"}, headers={"X-User": "bob"})
    
    # New count should be higher
    res = client.get("/unread")
    new_count = res.get_json()["count"]
    assert new_count == initial_count + 2


def test_unread_count_excludes_deleted(client, app):
    """Unread count should not include deleted messages."""
    # Add and delete a message
    res = client.post("/send", json={"content": "Delete me"}, headers={"X-User": "alice"})
    msg_id = res.get_json()["id"]
    
    res = client.get("/unread")
    count_before = res.get_json()["count"]
    
    client.post("/delete", json={"id": msg_id}, headers={"X-User": "alice"})
    
    res = client.get("/unread")
    count_after = res.get_json()["count"]
    
    assert count_after == count_before - 1


def test_static_css_served(client):
    """CSS files should be served correctly."""
    res = client.get("/ui/css/styles.css")
    assert res.status_code == 200
    assert b"--color-" in res.data  # CSS variables


def test_static_js_served(client):
    """JS files should be served correctly."""
    res = client.get("/ui/js/socket_glue.js")
    assert res.status_code == 200
    assert b"socket" in res.data


def test_backfill_endpoint(client, app):
    """HTTP backfill endpoint works."""
    client.post("/send", json={"content": "Test"}, headers={"X-User": "alice"})
    
    res = client.get("/backfill")
    assert res.status_code == 200
    data = res.get_json()
    assert "messages" in data
    assert len(data["messages"]) >= 1


def test_404_on_unknown_route(client):
    """Unknown routes return 404."""
    res = client.get("/unknown/route")
    assert res.status_code == 404
