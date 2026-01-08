"""
Unit tests for services/dm_service.py

Tests the encrypted direct messaging service layer directly.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.dm_service import (
    send_message,
    get_conversation_messages,
    mark_messages_read,
    delete_message,
    list_user_conversations,
    ServiceResult
)


class TestSendMessage:
    """Tests for send_message()"""

    def test_send_message_success(self, db_session, test_user, second_user):
        """Send message successfully."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Hello, world!"
        )
        
        assert result.success is True
        assert result.data is not None
        assert "id" in result.data
        assert "conversation_id" in result.data

    def test_send_message_empty_content(self, db_session, test_user, second_user):
        """Empty content is rejected."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="   "
        )
        
        assert result.success is False
        assert result.status == 400
        assert "content required" in result.error.lower()

    def test_send_message_too_long(self, db_session, test_user, second_user):
        """Message over 2000 chars is rejected."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="x" * 2001
        )
        
        assert result.success is False
        assert result.status == 400
        assert "too long" in result.error.lower()

    def test_send_message_recipient_not_found(self, db_session, test_user):
        """Sending to non-existent user fails."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=999999,
            content="Hello, nobody!"
        )
        
        assert result.success is False
        assert result.status == 404
        assert "not found" in result.error.lower()

    def test_send_message_dm_disabled(self, db_session, test_user, second_user):
        """Sending to user with DMs disabled fails."""
        db = db_session
        # Update second_user's DM policy to "nobody"
        db.execute(
            "UPDATE profiles SET dm_policy = 'nobody' WHERE user_id = ?",
            (second_user["user_id"],)
        )
        db.commit()
        
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Hello?"
        )
        
        assert result.success is False
        assert result.status == 403
        assert "disabled" in result.error.lower()

    def test_send_message_sanitization(self, db_session, test_user, second_user):
        """HTML in messages is escaped."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="<script>alert('xss')</script>"
        )
        
        assert result.success is True
        
        # Retrieve and check content is escaped
        conv = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"]
        )
        
        assert len(conv.data["messages"]) == 1
        msg_content = conv.data["messages"][0]["content"]
        assert "<script>" not in msg_content
        assert "&lt;script&gt;" in msg_content


class TestGetConversationMessages:
    """Tests for get_conversation_messages()"""

    def test_get_messages_empty(self, db_session, test_user, second_user):
        """No messages returns empty list."""
        result = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"]
        )
        
        assert result.success is True
        assert result.data["messages"] == []

    def test_get_messages_decrypts(self, db_session, test_user, second_user):
        """Messages are returned decrypted."""
        send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Secret message"
        )
        
        result = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"]
        )
        
        assert result.success is True
        assert len(result.data["messages"]) == 1
        # Content should be accessible (html-escaped version of original)
        assert "Secret message" in result.data["messages"][0]["content"]

    def test_get_messages_is_mine_flag(self, db_session, test_user, second_user):
        """Messages have correct is_mine flag."""
        send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="From test_user"
        )
        
        # From sender's perspective
        result1 = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"]
        )
        assert result1.data["messages"][0]["is_mine"] is True
        
        # From recipient's perspective
        result2 = get_conversation_messages(
            user_id=second_user["user_id"],
            other_user_id=test_user["user_id"]
        )
        assert result2.data["messages"][0]["is_mine"] is False

    def test_get_messages_pagination(self, db_session, test_user, second_user):
        """Pagination with before_id works."""
        # Send 5 messages
        msg_ids = []
        for i in range(5):
            result = send_message(
                sender_id=test_user["user_id"],
                recipient_id=second_user["user_id"],
                content=f"Message {i}"
            )
            msg_ids.append(result.data["id"])
        
        # Get messages before the 4th one (index 3)
        result = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"],
            before_id=msg_ids[3]
        )
        
        # Should only have messages 0, 1, 2
        assert len(result.data["messages"]) == 3

    def test_get_messages_limit(self, db_session, test_user, second_user):
        """Limit parameter is respected."""
        # Send 10 messages
        for i in range(10):
            send_message(
                sender_id=test_user["user_id"],
                recipient_id=second_user["user_id"],
                content=f"Message {i}"
            )
        
        result = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"],
            limit=5
        )
        
        assert len(result.data["messages"]) == 5

    def test_get_messages_max_limit(self, db_session, test_user, second_user):
        """Limit is capped at 100."""
        send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Test"
        )
        
        # Request with absurd limit
        result = get_conversation_messages(
            user_id=test_user["user_id"],
            other_user_id=second_user["user_id"],
            limit=9999
        )
        
        # Should succeed (capped internally)
        assert result.success is True


class TestMarkMessagesRead:
    """Tests for mark_messages_read()"""

    def test_mark_read_success(self, db_session, test_user, second_user):
        """Marking messages as read works."""
        # Send a message from test_user to second_user
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Read me!"
        )
        msg_id = result.data["id"]
        
        # second_user marks as read
        result = mark_messages_read(
            user_id=second_user["user_id"],
            message_id=msg_id
        )
        
        assert result.success is True
        
        # Verify read_at is set
        db = db_session
        row = db.execute(
            "SELECT read_at FROM direct_messages WHERE id = ?",
            (msg_id,)
        ).fetchone()
        assert row["read_at"] is not None

    def test_mark_read_idempotent(self, db_session, test_user, second_user):
        """Marking read multiple times is safe."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Read me twice!"
        )
        msg_id = result.data["id"]
        
        # Mark twice
        mark_messages_read(user_id=second_user["user_id"], message_id=msg_id)
        result = mark_messages_read(user_id=second_user["user_id"], message_id=msg_id)
        
        assert result.success is True


class TestDeleteMessage:
    """Tests for delete_message()"""

    def test_delete_message_sender(self, db_session, test_user, second_user):
        """Sender can soft-delete their message."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Delete me"
        )
        msg_id = result.data["id"]
        
        result = delete_message(
            user_id=test_user["user_id"],
            message_id=msg_id
        )
        
        assert result.success is True
        
        # Verify flag is set
        db = db_session
        row = db.execute(
            "SELECT deleted_by_sender FROM direct_messages WHERE id = ?",
            (msg_id,)
        ).fetchone()
        assert row["deleted_by_sender"] == 1

    def test_delete_message_recipient(self, db_session, test_user, second_user):
        """Recipient can soft-delete from their view."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Delete for recipient"
        )
        msg_id = result.data["id"]
        
        result = delete_message(
            user_id=second_user["user_id"],
            message_id=msg_id
        )
        
        assert result.success is True
        
        # Verify flag is set
        db = db_session
        row = db.execute(
            "SELECT deleted_by_recipient FROM direct_messages WHERE id = ?",
            (msg_id,)
        ).fetchone()
        assert row["deleted_by_recipient"] == 1

    def test_delete_message_other_still_sees(self, db_session, test_user, second_user):
        """Soft delete doesn't affect other participant's view."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Visible to recipient"
        )
        msg_id = result.data["id"]
        
        # Sender deletes
        delete_message(user_id=test_user["user_id"], message_id=msg_id)
        
        # Recipient should still see it
        conv = get_conversation_messages(
            user_id=second_user["user_id"],
            other_user_id=test_user["user_id"]
        )
        
        assert len(conv.data["messages"]) == 1

    def test_delete_message_not_found(self, db_session, test_user):
        """Deleting non-existent message fails."""
        result = delete_message(
            user_id=test_user["user_id"],
            message_id=999999
        )
        
        assert result.success is False
        assert result.status == 404

    def test_delete_message_unauthorized(self, db_session, test_user, second_user):
        """Non-participant cannot delete message."""
        result = send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Protected"
        )
        msg_id = result.data["id"]
        
        # Create third user
        db = db_session
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("thirduser", "hash")
        )
        third_user_id = cursor.lastrowid
        db.commit()
        
        result = delete_message(
            user_id=third_user_id,
            message_id=msg_id
        )
        
        assert result.success is False
        assert result.status == 403


class TestListUserConversations:
    """Tests for list_user_conversations()"""

    def test_list_conversations_empty(self, db_session, test_user):
        """User with no conversations gets empty list."""
        result = list_user_conversations(user_id=test_user["user_id"])
        
        assert result.success is True
        assert result.data["conversations"] == []

    def test_list_conversations_single(self, db_session, test_user, second_user):
        """Single conversation is listed."""
        send_message(
            sender_id=test_user["user_id"],
            recipient_id=second_user["user_id"],
            content="Hello!"
        )
        
        result = list_user_conversations(user_id=test_user["user_id"])
        
        assert result.success is True
        assert len(result.data["conversations"]) == 1
        assert result.data["conversations"][0]["other_user_id"] == second_user["user_id"]

    def test_list_conversations_multiple(self, db_session, test_user, second_user):
        """Multiple conversations are listed."""
        # Create third user
        db = db_session
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("thirduser", "hash")
        )
        third_id = cursor.lastrowid
        cursor = db.execute(
            "INSERT INTO profiles (user_id, display_name) VALUES (?, ?)",
            (third_id, "Third")
        )
        db.commit()
        
        # Send messages to both
        send_message(sender_id=test_user["user_id"], recipient_id=second_user["user_id"], content="Hi 2")
        send_message(sender_id=test_user["user_id"], recipient_id=third_id, content="Hi 3")
        
        result = list_user_conversations(user_id=test_user["user_id"])
        
        assert result.success is True
        assert len(result.data["conversations"]) == 2

    def test_list_conversations_unread_count(self, db_session, test_user, second_user):
        """Unread count is accurate."""
        # Send 3 messages from second_user to test_user
        for i in range(3):
            send_message(
                sender_id=second_user["user_id"],
                recipient_id=test_user["user_id"],
                content=f"Unread {i}"
            )
        
        result = list_user_conversations(user_id=test_user["user_id"])
        
        assert result.success is True
        assert result.data["conversations"][0]["unread_count"] == 3
