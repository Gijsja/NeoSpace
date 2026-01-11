"""
NeoSpace msgspec Structs — Sprint #13: Speed Demon

High-performance struct definitions for hot-path JSON serialization.
msgspec provides 10-80x faster encoding/decoding than stdlib json.

Usage:
    from core.structs import Message, WallPost, encode_json, decode_json
"""

import msgspec
from typing import Optional


# =============================================================================
# Message Struct (Chat / Socket payloads)
# =============================================================================
class Message(msgspec.Struct):
    """Real-time chat message structure."""
    id: int
    user: str
    content: str
    created_at: str
    room_id: int = 1
    deleted: bool = False
    edited: bool = False


# =============================================================================
# Wall Post Struct (Profile modules)
# =============================================================================
class WallPost(msgspec.Struct):
    """Profile wall module structure."""
    id: int
    module_type: str
    content: dict
    style: dict
    display_order: int
    created_at: str
    updated_at: Optional[str] = None


# =============================================================================
# Profile Sticker Struct
# =============================================================================
class Sticker(msgspec.Struct):
    """Profile wall sticker."""
    id: str
    sticker_type: str
    x_pos: float
    y_pos: float
    rotation: float = 0.0
    scale: float = 1.0
    z_index: int = 0
    image_path: Optional[str] = None


# =============================================================================
# Encoder/Decoder Instances (reuse for performance)
# =============================================================================
_encoder = msgspec.json.Encoder()
_decoder = msgspec.json.Decoder()


def encode_json(obj) -> bytes:
    """Fast JSON encoding. Returns bytes."""
    return _encoder.encode(obj)


def decode_json(data: bytes, type=None):
    """Fast JSON decoding. Optionally validates against type."""
    if type:
        return msgspec.json.decode(data, type=type)
    return _decoder.decode(data)


# =============================================================================
# Convenience: Convert DB row to Message struct
# =============================================================================
def row_to_message(row) -> Message:
    """Convert sqlite3.Row to Message struct."""
    return Message(
        id=row["id"],
        user=row["user"],
        content=row["content"],
        created_at=row["created_at"],
        room_id=row.get("room_id", 1) if hasattr(row, "get") else row["room_id"] if "room_id" in row.keys() else 1,
        deleted=bool(row["deleted_at"]) if "deleted_at" in row.keys() else False,
        edited=bool(row["edited_at"]) if "edited_at" in row.keys() else False,
    )
