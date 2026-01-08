"""
Unit tests for services/wall_service.py

Tests the wall post service layer directly without HTTP overhead.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.wall_service import (
    add_post,
    update_post,
    delete_post,
    get_posts_for_profile,
    reorder_posts,
    ALLOWED_TYPES,
    ServiceResult
)


class TestAddPost:
    """Tests for add_post()"""

    def test_add_post_text(self, db_session, test_user):
        """Add a text post successfully."""
        result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "Hello world!"},
            style={"color": "#ff0000"},
            display_order=0
        )
        
        assert result.success is True
        assert result.data is not None
        assert "id" in result.data
        assert isinstance(result.data["id"], int)

    def test_add_post_all_types(self, db_session, test_user):
        """All allowed module types can be created."""
        for idx, module_type in enumerate(ALLOWED_TYPES):
            result = add_post(
                user_id=test_user["user_id"],
                module_type=module_type,
                content={"test": f"content for {module_type}"},
                style={},
                display_order=idx
            )
            assert result.success is True, f"Failed for type: {module_type}"

    def test_add_post_invalid_type(self, db_session, test_user):
        """Invalid module type is rejected."""
        result = add_post(
            user_id=test_user["user_id"],
            module_type="invalid_type",
            content={"text": "test"},
            style={},
            display_order=0
        )
        
        assert result.success is False
        assert result.status == 400
        assert "Invalid type" in result.error

    def test_add_post_no_profile(self, db_session):
        """User without profile gets 404."""
        # Create user without profile
        db = db_session
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("noprofile", "hash")
        )
        user_id = cursor.lastrowid
        db.commit()
        
        result = add_post(
            user_id=user_id,
            module_type="text",
            content={"text": "test"},
            style={},
            display_order=0
        )
        
        assert result.success is False
        assert result.status == 404
        assert "Profile not found" in result.error


class TestUpdatePost:
    """Tests for update_post()"""

    def test_update_post_content(self, db_session, test_user):
        """Update content payload."""
        # Create post first
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "Original"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        # Update content
        result = update_post(
            user_id=test_user["user_id"],
            post_id=post_id,
            content={"text": "Updated"}
        )
        
        assert result.success is True

    def test_update_post_style(self, db_session, test_user):
        """Update style payload."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "test"},
            style={"color": "#000"},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        result = update_post(
            user_id=test_user["user_id"],
            post_id=post_id,
            style={"color": "#fff", "bold": True}
        )
        
        assert result.success is True

    def test_update_post_module_type(self, db_session, test_user):
        """Update module type."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "test"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        result = update_post(
            user_id=test_user["user_id"],
            post_id=post_id,
            module_type="link"
        )
        
        assert result.success is True

    def test_update_post_not_owner(self, db_session, test_user, second_user):
        """Non-owner cannot update post."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "test"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        result = update_post(
            user_id=second_user["user_id"],
            post_id=post_id,
            content={"text": "Hacked!"}
        )
        
        assert result.success is False
        assert result.status == 403

    def test_update_post_not_found(self, db_session, test_user):
        """Updating non-existent post fails."""
        result = update_post(
            user_id=test_user["user_id"],
            post_id=999999,
            content={"text": "Ghost"}
        )
        
        assert result.success is False
        assert result.status == 403

    def test_update_post_empty_update(self, db_session, test_user):
        """Empty update is a no-op success."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "test"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        result = update_post(
            user_id=test_user["user_id"],
            post_id=post_id
            # No content, style, or module_type
        )
        
        assert result.success is True


class TestDeletePost:
    """Tests for delete_post()"""

    def test_delete_post_success(self, db_session, test_user):
        """Delete own post successfully."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "To be deleted"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        result = delete_post(
            user_id=test_user["user_id"],
            post_id=post_id
        )
        
        assert result.success is True
        
        # Verify it's gone
        posts = get_posts_for_profile(test_user["profile_id"])
        assert len(posts) == 0

    def test_delete_post_idempotent(self, db_session, test_user):
        """Deleting already-deleted post is safe."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "Double delete"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        # Delete twice
        delete_post(user_id=test_user["user_id"], post_id=post_id)
        result = delete_post(user_id=test_user["user_id"], post_id=post_id)
        
        # Should still succeed (no error on missing)
        assert result.success is True

    def test_delete_post_other_user(self, db_session, test_user, second_user):
        """Cannot delete another user's post (silently fails)."""
        create_result = add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "Protected"},
            style={},
            display_order=0
        )
        post_id = create_result.data["id"]
        
        # Second user tries to delete
        delete_post(user_id=second_user["user_id"], post_id=post_id)
        
        # Post should still exist
        posts = get_posts_for_profile(test_user["profile_id"])
        assert len(posts) == 1


class TestGetPostsForProfile:
    """Tests for get_posts_for_profile()"""

    def test_get_posts_empty(self, db_session, test_user):
        """Profile with no posts returns empty list."""
        posts = get_posts_for_profile(test_user["profile_id"])
        assert posts == []

    def test_get_posts_ordering(self, db_session, test_user):
        """Posts returned in display_order."""
        # Create posts in reverse order
        for i in [3, 1, 2]:
            add_post(
                user_id=test_user["user_id"],
                module_type="text",
                content={"text": f"Post {i}"},
                style={},
                display_order=i
            )
        
        posts = get_posts_for_profile(test_user["profile_id"])
        
        assert len(posts) == 3
        # Should be sorted by display_order ASC
        assert posts[0]["content"]["text"] == "Post 1"
        assert posts[1]["content"]["text"] == "Post 2"
        assert posts[2]["content"]["text"] == "Post 3"

    def test_get_posts_parses_json(self, db_session, test_user):
        """Content and style are parsed from JSON."""
        add_post(
            user_id=test_user["user_id"],
            module_type="text",
            content={"text": "Hello", "nested": {"key": "value"}},
            style={"color": "#fff"},
            display_order=0
        )
        
        posts = get_posts_for_profile(test_user["profile_id"])
        
        assert len(posts) == 1
        assert posts[0]["content"]["text"] == "Hello"
        assert posts[0]["content"]["nested"]["key"] == "value"
        assert posts[0]["style"]["color"] == "#fff"

    def test_get_posts_invalid_profile(self, db_session):
        """Non-existent profile returns empty list."""
        posts = get_posts_for_profile(999999)
        assert posts == []


class TestReorderPosts:
    """Tests for reorder_posts()"""

    def test_reorder_posts_success(self, db_session, test_user):
        """Reorder posts successfully."""
        # Create 3 posts
        ids = []
        for i in range(3):
            result = add_post(
                user_id=test_user["user_id"],
                module_type="text",
                content={"text": f"Post {i}"},
                style={},
                display_order=i
            )
            ids.append(result.data["id"])
        
        # Reverse order
        result = reorder_posts(
            user_id=test_user["user_id"],
            order=list(reversed(ids))
        )
        
        assert result.success is True
        
        # Verify new order
        posts = get_posts_for_profile(test_user["profile_id"])
        assert posts[0]["id"] == ids[2]
        assert posts[1]["id"] == ids[1]
        assert posts[2]["id"] == ids[0]

    def test_reorder_posts_empty(self, db_session, test_user):
        """Empty order list is no-op."""
        result = reorder_posts(
            user_id=test_user["user_id"],
            order=[]
        )
        
        assert result.success is True

    def test_reorder_posts_no_profile(self, db_session):
        """User without profile gets 404."""
        db = db_session
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("noprofile2", "hash")
        )
        user_id = cursor.lastrowid
        db.commit()
        
        result = reorder_posts(
            user_id=user_id,
            order=[1, 2, 3]
        )
        
        assert result.success is False
        assert result.status == 404

    def test_reorder_posts_partial(self, db_session, test_user):
        """Partial order only updates specified posts."""
        # Create 3 posts
        ids = []
        for i in range(3):
            result = add_post(
                user_id=test_user["user_id"],
                module_type="text",
                content={"text": f"Post {i}"},
                style={},
                display_order=i
            )
            ids.append(result.data["id"])
        
        # Only reorder first two (swap them)
        result = reorder_posts(
            user_id=test_user["user_id"],
            order=[ids[1], ids[0]]
        )
        
        assert result.success is True
