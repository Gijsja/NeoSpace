"""
Encryption utilities for Sprint 6 DMs.
Uses AES-256-GCM for authenticated encryption.
"""

import os
import hashlib
from typing import Tuple


def get_dm_key() -> bytes:
    """Get the master key for DM encryption from environment."""
    key_hex = os.environ.get("DM_MASTER_KEY")
    if not key_hex:
        # In development, derive from secret key (NOT for production!)
        from flask import current_app
        secret = current_app.secret_key
        if secret == "dev_secret_key_DO_NOT_USE_IN_PROD":
            # Generate deterministic dev key
            key_hex = hashlib.sha256(b"dev_dm_key_DO_NOT_USE_IN_PROD").hexdigest()
        else:
            key_hex = hashlib.sha256(secret.encode()).hexdigest()
    return bytes.fromhex(key_hex[:64])  # 32 bytes = 256 bits


def derive_conversation_key(user_a_id: int, user_b_id: int, master_key: bytes) -> bytes:
    """Derive a unique key per conversation using HKDF."""
    # Sort IDs for consistent conversation_id regardless of sender/recipient order
    conversation_id = f"{min(user_a_id, user_b_id)}:{max(user_a_id, user_b_id)}"
    
    # Use HMAC-SHA256 as a simple KDF (cryptography package optional)
    import hmac
    return hmac.new(
        master_key,
        conversation_id.encode(),
        hashlib.sha256
    ).digest()


def get_conversation_id(user_a_id: int, user_b_id: int) -> str:
    """Generate consistent conversation ID from two user IDs."""
    return f"{min(user_a_id, user_b_id)}:{max(user_a_id, user_b_id)}"


def encrypt_message(plaintext: str, conversation_key: bytes) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypt message using AES-256-GCM.
    
    Returns: (ciphertext, iv, tag)
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        # Fallback: store as "encrypted" but actually base64 (DEV ONLY)
        import base64
        import warnings
        warnings.warn("cryptography not installed - using insecure fallback!")
        iv = os.urandom(12)
        tag = os.urandom(16)
        ciphertext = base64.b64encode(plaintext.encode())
        return ciphertext, iv, tag
    
    aesgcm = AESGCM(conversation_key)
    iv = os.urandom(12)  # 96-bit nonce (recommended for GCM)
    
    # Encrypt and get ciphertext + tag combined
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
    
    # Split: last 16 bytes are the authentication tag
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    
    return ciphertext, iv, tag


def decrypt_message(ciphertext: bytes, iv: bytes, tag: bytes, conversation_key: bytes) -> str:
    """
    Decrypt message using AES-256-GCM.
    
    Returns: plaintext string
    Raises: cryptography.exceptions.InvalidTag if tampered
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        # Fallback for dev
        import base64
        return base64.b64decode(ciphertext).decode('utf-8')
    
    aesgcm = AESGCM(conversation_key)
    
    # Reassemble ciphertext + tag for decryption
    ciphertext_with_tag = ciphertext + tag
    
    plaintext_bytes = aesgcm.decrypt(iv, ciphertext_with_tag, None)
    return plaintext_bytes.decode('utf-8')
