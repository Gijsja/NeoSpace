
import pytest
from services import dm_service
from db import get_db

@pytest.fixture
def users(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES ('alice', 'hash')")
        db.execute("INSERT INTO users (username, password_hash) VALUES ('bob', 'hash')")
        alice_id = db.execute("SELECT id FROM users WHERE username = 'alice'").fetchone()[0]
        bob_id = db.execute("SELECT id FROM users WHERE username = 'bob'").fetchone()[0]
        
        db.execute("INSERT INTO profiles (user_id, display_name) VALUES (?, 'Alice')", (alice_id,))
        db.execute("INSERT INTO profiles (user_id, display_name) VALUES (?, 'Bob')", (bob_id,))
        db.commit()
        return {'alice': alice_id, 'bob': bob_id}

def test_send_message_success(app, users):
    with app.app_context():
        res = dm_service.send_message(users['alice'], users['bob'], "Hello Bob!")
        assert res.success is True
        assert "id" in res.data
        assert res.data["conversation_id"] == f"{min(users['alice'], users['bob'])}:{max(users['alice'], users['bob'])}"

def test_send_message_empty_content(app, users):
    with app.app_context():
        res = dm_service.send_message(users['alice'], users['bob'], "   ")
        assert res.success is False
        assert res.status == 400

def test_send_message_recipient_not_found(app, users):
    with app.app_context():
        res = dm_service.send_message(users['alice'], 9999, "Hello?")
        assert res.success is False
        assert res.status == 404

def test_dm_policy_nobody(app, users):
    with app.app_context():
        db = get_db()
        db.execute("UPDATE profiles SET dm_policy = 'nobody' WHERE user_id = ?", (users['bob'],))
        db.commit()
        
        res = dm_service.send_message(users['alice'], users['bob'], "Private?")
        assert res.success is False
        assert res.status == 403

def test_get_conversation_messages(app, users):
    with app.app_context():
        dm_service.send_message(users['alice'], users['bob'], "Msg 1")
        dm_service.send_message(users['bob'], users['alice'], "Msg 2")
        
        res = dm_service.get_conversation_messages(users['alice'], users['bob'])
        assert res.success is True
        assert len(res.data["messages"]) == 2
        assert res.data["messages"][0]["content"] == "Msg 1"
        assert res.data["messages"][1]["content"] == "Msg 2"
        assert res.data["messages"][1]["is_mine"] is False

def test_mark_messages_read(app, users):
    with app.app_context():
        res = dm_service.send_message(users['alice'], users['bob'], "Unread")
        msg_id = res.data["id"]
        
        dm_service.mark_messages_read(users['bob'], msg_id)
        
        db = get_db()
        row = db.execute("SELECT read_at FROM direct_messages WHERE id = ?", (msg_id,)).fetchone()
        assert row["read_at"] is not None

def test_delete_message(app, users):
    with app.app_context():
        res = dm_service.send_message(users['alice'], users['bob'], "Regret")
        msg_id = res.data["id"]
        
        # Unauthorized delete
        res_fail = dm_service.delete_message(999, msg_id)
        assert res_fail.success is False
        
        # Sender delete
        res_ok = dm_service.delete_message(users['alice'], msg_id)
        assert res_ok.success is True
        
        db = get_db()
        row = db.execute("SELECT deleted_by_sender FROM direct_messages WHERE id = ?", (msg_id,)).fetchone()
        assert row["deleted_by_sender"] == 1

def test_list_conversations(app, users):
    with app.app_context():
        dm_service.send_message(users['alice'], users['bob'], "Hey")
        
        res = dm_service.list_user_conversations(users['alice'])
        assert res.success is True
        assert len(res.data["conversations"]) == 1
        assert res.data["conversations"][0]["other_user_id"] == users['bob']
        assert res.data["conversations"][0]["unread_count"] == 0
        
        res_bob = dm_service.list_user_conversations(users['bob'])
        assert res_bob.data["conversations"][0]["unread_count"] == 1
