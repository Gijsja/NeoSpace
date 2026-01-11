"""
Unit tests for services/profile_service.py

Tests the profile service layer directly.
"""

import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.profile_service import (
    get_profile_by_user_id,
    update_profile_fields,
    save_avatar,
    create_default_profile,
    validate_hex_color,
    sanitize_display_name,
    sanitize_bio,
    ServiceResult,
    ALLOWED_THEMES,
    ALLOWED_DM_POLICIES,
    MAX_DISPLAY_NAME_LENGTH,
    MAX_BIO_LENGTH
)


class TestValidateHexColor:
    """Tests for validate_hex_color()"""

    def test_valid_color_lowercase(self):
        """Lowercase hex color is accepted and uppercased."""
        result = validate_hex_color("#aabbcc")
        assert result == "#AABBCC"

    def test_valid_color_uppercase(self):
        """Uppercase hex color is accepted."""
        result = validate_hex_color("#AABBCC")
        assert result == "#AABBCC"

    def test_valid_color_mixed(self):
        """Mixed case hex color is normalized."""
        result = validate_hex_color("#aAbBcC")
        assert result == "#AABBCC"

    def test_empty_returns_default(self):
        """Empty string returns default accent color."""
        result = validate_hex_color("")
        assert result == "#3b82f6"

    def test_none_returns_default(self):
        """None returns default accent color."""
        result = validate_hex_color(None)
        assert result == "#3b82f6"

    def test_invalid_format_raises(self):
        """Invalid format raises ValueError."""
        with pytest.raises(ValueError):
            validate_hex_color("red")

    def test_short_hex_raises(self):
        """Short hex (#RGB) raises ValueError."""
        with pytest.raises(ValueError):
            validate_hex_color("#abc")

    def test_no_hash_raises(self):
        """Missing hash raises ValueError."""
        with pytest.raises(ValueError):
            validate_hex_color("aabbcc")


class TestSanitizeDisplayName:
    """Tests for sanitize_display_name()"""

    def test_normal_name(self):
        """Normal name passes through."""
        result = sanitize_display_name("John Doe")
        assert result == "John Doe"

    def test_removes_control_chars(self):
        """Control characters are removed."""
        result = sanitize_display_name("Hello\x00World\x1f")
        assert result == "HelloWorld"

    def test_trims_whitespace(self):
        """Leading/trailing whitespace is trimmed."""
        result = sanitize_display_name("  Padded  ")
        assert result == "Padded"

    def test_truncates_long_name(self):
        """Long names are truncated to MAX_DISPLAY_NAME_LENGTH."""
        long_name = "x" * 100
        result = sanitize_display_name(long_name)
        assert len(result) == MAX_DISPLAY_NAME_LENGTH

    def test_empty_string(self):
        """Empty string returns empty."""
        result = sanitize_display_name("")
        assert result == ""

    def test_none_returns_empty(self):
        """None returns empty string."""
        result = sanitize_display_name(None)
        assert result == ""


class TestSanitizeBio:
    """Tests for sanitize_bio()"""

    def test_normal_bio(self):
        """Normal bio passes through."""
        result = sanitize_bio("I like coding")
        assert "I like coding" in result

    def test_strips_script_tags(self):
        """Script tags are removed."""
        result = sanitize_bio("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_truncates_long_bio(self):
        """Long bios are truncated before sanitization."""
        long_bio = "x" * 1000
        result = sanitize_bio(long_bio)
        assert len(result) <= MAX_BIO_LENGTH

    def test_empty_returns_empty(self):
        """Empty string returns empty."""
        result = sanitize_bio("")
        assert result == ""

    def test_none_returns_empty(self):
        """None returns empty string."""
        result = sanitize_bio(None)
        assert result == ""


class TestUpdateProfileFields:
    """Tests for update_profile_fields()"""

    def test_update_display_name(self, db_session, test_user):
        """Update display_name successfully."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"display_name": "New Name"}
        )
        
        assert result.success is True
        
        # Verify in DB
        db = db_session
        row = db.execute(
            "SELECT display_name FROM profiles WHERE user_id = ?",
            (test_user["user_id"],)
        ).fetchone()
        assert row["display_name"] == "New Name"

    def test_update_bio(self, db_session, test_user):
        """Update bio successfully."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"bio": "My new bio"}
        )
        
        assert result.success is True

    def test_update_theme_valid(self, db_session, test_user):
        """Valid theme is accepted."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"theme_preset": "dark"}
        )
        
        assert result.success is True

    def test_update_theme_invalid(self, db_session, test_user):
        """Invalid theme is rejected."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"theme_preset": "neon_rainbow"}
        )
        
        assert result.success is False
        assert result.status == 400
        assert "Invalid theme" in result.error

    def test_update_accent_color_valid(self, db_session, test_user):
        """Valid accent color is accepted."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"accent_color": "#ff5500"}
        )
        
        assert result.success is True

    def test_update_accent_color_invalid(self, db_session, test_user):
        """Invalid accent color is rejected."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"accent_color": "not-a-color"}
        )
        
        assert result.success is False
        assert result.status == 400

    def test_update_dm_policy_valid(self, db_session, test_user):
        """Valid DM policy is accepted."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"dm_policy": "mutuals"}
        )
        
        assert result.success is True

    def test_update_dm_policy_invalid(self, db_session, test_user):
        """Invalid DM policy is rejected."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"dm_policy": "friends_only"}
        )
        
        assert result.success is False
        assert result.status == 400

    def test_update_anthem_url_valid(self, db_session, test_user):
        """Valid anthem URL is accepted."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"anthem_url": "https://example.com/song.mp3"}
        )
        
        assert result.success is True

    def test_update_anthem_url_invalid(self, db_session, test_user):
        """Invalid anthem URL (not http/https) is rejected."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={"anthem_url": "ftp://example.com/song.mp3"}
        )
        
        assert result.success is False
        assert result.status == 400

    def test_update_empty_data(self, db_session, test_user):
        """Empty update data is rejected."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={}
        )
        
        assert result.success is False
        assert result.status == 400

    def test_update_multiple_fields(self, db_session, test_user):
        """Multiple fields can be updated at once."""
        result = update_profile_fields(
            user_id=test_user["user_id"],
            data={
                "display_name": "Multi Update",
                "bio": "New bio",
                "theme_preset": "retro"
            }
        )
        
        assert result.success is True

    def test_update_creates_profile_if_missing(self, db_session):
        """Updates create profile if user doesn't have one."""
        db = db_session
        
        # Create user without profile
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("noprofile", "hash")
        )
        user_id = cursor.lastrowid
        db.commit()
        
        result = update_profile_fields(
            user_id=user_id,
            data={"display_name": "Created Profile"}
        )
        
        assert result.success is True
        
        # Verify profile was created
        row = db.execute(
            "SELECT display_name FROM profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        assert row["display_name"] == "Created Profile"


class TestSaveAvatar:
    """Tests for save_avatar()"""

    def test_save_avatar_valid(self, db_session, test_user):
        """Valid avatar is saved."""
        with tempfile.TemporaryDirectory() as app_root:
            fake_image = b"\x89PNG\r\n\x1a\n" + b"x" * 100
            
            result = save_avatar(
                user_id=test_user["user_id"],
                file_data=fake_image,
                extension="png",
                app_root=app_root
            )
            
            assert result.success is True
            assert "avatar_path" in result.data
            assert result.data["avatar_path"].startswith("/files/")

    def test_save_avatar_invalid_extension(self, db_session, test_user):
        """Invalid file extension is rejected."""
        with tempfile.TemporaryDirectory() as app_root:
            result = save_avatar(
                user_id=test_user["user_id"],
                file_data=b"test",
                extension="exe",
                app_root=app_root
            )
            
            assert result.success is False
            assert result.status == 400
            assert "Invalid file type" in result.error

    def test_save_avatar_too_large(self, db_session, test_user):
        """File over 2MB is rejected."""
        with tempfile.TemporaryDirectory() as app_root:
            large_file = b"x" * (3 * 1024 * 1024)  # 3MB
            
            result = save_avatar(
                user_id=test_user["user_id"],
                file_data=large_file,
                extension="png",
                app_root=app_root
            )
            
            assert result.success is False
            assert result.status == 400
            assert "too large" in result.error.lower()


class TestCreateDefaultProfile:
    """Tests for create_default_profile()"""

    def test_create_default_profile(self, db_session):
        """Default profile is created for new user."""
        db = db_session
        
        # Create user without profile
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("newuser", "hash")
        )
        user_id = cursor.lastrowid
        db.commit()
        
        result = create_default_profile(user_id, "newuser")
        
        assert result.success is True
        
        # Verify profile exists
        row = db.execute(
            "SELECT display_name FROM profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        assert row["display_name"] == "newuser"


class TestGetProfileByUserId:
    """Tests for get_profile_by_user_id()"""

    def test_get_profile_success(self, db_session, test_user):
        """Get profile returns data."""
        result = get_profile_by_user_id(
            user_id=test_user["user_id"],
            viewer_id=test_user["user_id"]
        )
        
        assert result.success is True
        assert result.data["username"] == "testuser"
        assert result.data["is_own"] is True

    def test_get_profile_not_found(self, db_session):
        """Non-existent user returns 404."""
        result = get_profile_by_user_id(user_id=999999)
        
        assert result.success is False
        assert result.status == 404

    def test_get_profile_private_blocked(self, db_session, test_user, second_user):
        """Private profile is blocked for non-owner."""
        db = db_session
        
        # Make test_user's profile private
        db.execute(
            "UPDATE profiles SET is_public = 0 WHERE user_id = ?",
            (test_user["user_id"],)
        )
        db.commit()
        
        result = get_profile_by_user_id(
            user_id=test_user["user_id"],
            viewer_id=second_user["user_id"]
        )
        
        assert result.success is False
        assert result.status == 403

    def test_get_profile_own_private_allowed(self, db_session, test_user):
        """Owner can view their own private profile."""
        db = db_session
        
        db.execute(
            "UPDATE profiles SET is_public = 0 WHERE user_id = ?",
            (test_user["user_id"],)
        )
        db.commit()
        
        result = get_profile_by_user_id(
            user_id=test_user["user_id"],
            viewer_id=test_user["user_id"]
        )
        
        assert result.success is True
