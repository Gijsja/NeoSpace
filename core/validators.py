from typing import Optional
import re

def validate_username(username: str) -> Optional[str]:
    """Validate username format and length."""
    if not username:
        return "Username is required."
    if len(username) < 2:
        return "Username must be at least 2 characters."
    if len(username) > 20:
        return "Username must be at most 20 characters."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return "Username can only contain letters, numbers, underscores, and hyphens."
    return None

def validate_display_name(name: str) -> Optional[str]:
    """Validate display name length."""
    if name and len(name) > 50:
        return "Display name must be at most 50 characters."
    return None

def validate_bio(bio: str) -> Optional[str]:
    """Validate bio length."""
    if bio and len(bio) > 160:
        return "Bio must be at most 160 characters."
    return None

def validate_content_length(content: str, max_len: int = 5000, label: str = "Content") -> Optional[str]:
    """Generic length validation."""
    if content and len(content) > max_len:
        return f"{label} exceeds maximum length of {max_len} characters."
    return None

def validate_sticker_text(text: str) -> Optional[str]:
    """Validate sticker emoji/text length."""
    if text and len(text) > 32:
        return "Sticker text too long."
    return None

