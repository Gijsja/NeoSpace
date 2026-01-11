
import pytest
import os
import hashlib
from core import crypto

def test_get_dm_key_env(monkeypatch):
    monkeypatch.setenv("DM_MASTER_KEY", "f" * 64)
    key = crypto.get_dm_key()
    assert key == bytes.fromhex("f" * 64)

def test_get_dm_key_fallback(app):
    with app.app_context():
        # current_app.secret_key is set in create_app
        key = crypto.get_dm_key()
        assert len(key) == 32

def test_derive_conversation_key():
    master_key = b"master_key_32_bytes_long_exactly_"[:32]
    key1 = crypto.derive_conversation_key(1, 2, master_key)
    key2 = crypto.derive_conversation_key(2, 1, master_key)
    assert key1 == key2
    assert len(key1) == 32

def test_encrypt_decrypt_roundtrip():
    conversation_key = os.urandom(32)
    plaintext = "Hello, NeoSpace!"
    
    ciphertext, iv, tag = crypto.encrypt_message(plaintext, conversation_key)
    decrypted = crypto.decrypt_message(ciphertext, iv, tag, conversation_key)
    
    assert decrypted == plaintext

def test_decrypt_tampered_tag():
    conversation_key = os.urandom(32)
    plaintext = "Secure Message"
    
    ciphertext, iv, tag = crypto.encrypt_message(plaintext, conversation_key)
    
    # Tamper with tag
    tampered_tag = bytearray(tag)
    tampered_tag[0] ^= 0xFF
    
    from cryptography.exceptions import InvalidTag
    with pytest.raises(InvalidTag):
        crypto.decrypt_message(ciphertext, iv, bytes(tampered_tag), conversation_key)

def test_get_conversation_id():
    assert crypto.get_conversation_id(1, 2) == "1:2"
    assert crypto.get_conversation_id(2, 1) == "1:2"
