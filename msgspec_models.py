"""
msgspec Struct Definitions for High-Performance JSON Serialization.

These structs are used in hot paths (WebSocket events, API responses)
to achieve 10-80x faster JSON encoding/decoding compared to standard Python json.
"""

import msgspec
from typing import Optional


class Message(msgspec.Struct):
    """Chat message struct for serialization."""
    id: int
    user: str
    content: Optional[str]
    created_at: str
    edited_at: Optional[str] = None
    deleted_at: Optional[str] = None


class BackfillResponse(msgspec.Struct):
    """Response structure for backfill endpoint."""
    messages: list[Message]


class SendMessageRequest(msgspec.Struct):
    """Request payload for sending a message."""
    content: str


class AddWallPostRequest(msgspec.Struct):
    """Request to add a wall post."""
    module_type: str
    content: dict
    style: dict = {}
    display_order: int = 0


class UpdateWallPostRequest(msgspec.Struct):
    """Request to update a wall post."""
    id: int
    content: Optional[dict] = None
    style: Optional[dict] = None
    module_type: Optional[str] = None


class DeleteWallPostRequest(msgspec.Struct):
    """Request to delete a wall post."""
    id: int


class ReorderWallPostsRequest(msgspec.Struct):
    """Request to reorder wall posts."""
    order: list[int]


class WallPostResponse(msgspec.Struct):
    """Single wall post in response."""
    id: int
    module_type: str
    content: dict
    style: dict
    display_order: int
    created_at: str
    updated_at: Optional[str] = None


# Auth Requests
class RegisterRequest(msgspec.Struct):
    """Request to register a new user."""
    username: str
    password: str


class LoginRequest(msgspec.Struct):
    """Request to login."""
    username: str
    password: str


# Profile Mutations
class UpdateProfileRequest(msgspec.Struct):
    """Request to update profile."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    status_message: Optional[str] = None
    status_emoji: Optional[str] = None
    now_activity: Optional[str] = None
    now_activity_type: Optional[str] = None
    theme_preset: Optional[str] = None
    accent_color: Optional[str] = None
    is_public: Optional[bool] = None
    show_online_status: Optional[bool] = None
    dm_policy: Optional[str] = None
    anthem_url: Optional[str] = None
    anthem_autoplay: Optional[bool] = None


class UpdateStickerRequest(msgspec.Struct):
    """Request to update sticker position/rotation/scale."""
    id: str
    x: Optional[float] = None
    y: Optional[float] = None
    rotation: Optional[float] = None
    scale: Optional[float] = None
    z_index: Optional[int] = None


class RemoveStickerRequest(msgspec.Struct):
    """Request to remove a sticker."""
    id: str


# DM Mutations
class SendDMRequest(msgspec.Struct):
    """Request to send a direct message."""
    recipient_id: int
    content: str


class MarkDMReadRequest(msgspec.Struct):
    """Request to mark DM as read."""
    message_id: int


class DeleteDMRequest(msgspec.Struct):
    """Request to delete a DM."""
    message_id: int


# Friend Mutations  
class FollowRequest(msgspec.Struct):
    """Request to follow a user."""
    user_id: int


class UnfollowRequest(msgspec.Struct):
    """Request to unfollow a user."""
    user_id: int


class UpdateTop8Request(msgspec.Struct):
    """Request to update top 8 friends."""
    friend_ids: list[int]


# Notification Mutations
class MarkNotificationReadRequest(msgspec.Struct):
    """Request to mark notification as read."""
    notification_id: int


class DeleteNotificationRequest(msgspec.Struct):
    """Request to delete a notification."""
    notification_id: int


# Room Mutations
class CreateRoomRequest(msgspec.Struct):
    """Request to create a new room."""
    name: str
    description: Optional[str] = None


# Script Mutations
class PinScriptRequest(msgspec.Struct):
    """Request to pin a script to profile."""
    script_id: int


class UnpinScriptRequest(msgspec.Struct):
    """Request to unpin a script from profile."""
    script_id: int


class ReorderScriptsRequest(msgspec.Struct):
    """Request to reorder pinned scripts."""
    script_ids: list[int]


# Sticker Mutations  
class AddStickerRequest(msgspec.Struct):
    """Request to add a sticker."""
    sticker_type: str
    target_user_id: int
    x: int = 0
    y: int = 0
