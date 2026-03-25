"""
FILE: AI_infrastructure/shared/credential_crypto.py

PURPOSE:
    Symmetric encryption/decryption of credential values at rest (GAP-L7).
    Uses Fernet (AES-128-CBC + HMAC-SHA256) from the `cryptography` package.

CONFIGURATION:
    Set CREDENTIAL_ENCRYPTION_KEY in your .env file.
    Generate a key with:
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    If the env var is absent the module operates in PASSTHROUGH mode (no encryption).
    This ensures backward compatibility when the key is not yet deployed.

USAGE:
    from AI_infrastructure.shared.credential_crypto import encrypt_credential, decrypt_credential

    stored  = encrypt_credential("sk-ant-abc123")   # store this in DB
    plaintext = decrypt_credential(stored)           # retrieve original
"""

import os
import logging

logger = logging.getLogger(__name__)

# Sentinel prefix that marks an already-encrypted value
_ENC_PREFIX = "enc:v1:"


def _get_fernet():
    """Return a Fernet instance or None if the key is not configured."""
    key = os.getenv('CREDENTIAL_ENCRYPTION_KEY', '').strip()
    if not key:
        return None
    try:
        from cryptography.fernet import Fernet
        return Fernet(key.encode('utf-8') if isinstance(key, str) else key)
    except Exception as exc:
        logger.error(f"[CRED_CRYPTO] Failed to initialise Fernet: {exc} — running in passthrough mode")
        return None


def encrypt_credential(plaintext: str) -> str:
    """
    Encrypt *plaintext* and return a string safe to store in the database.
    If encryption is not configured, returns the value unchanged (passthrough).
    Already-encrypted values are returned as-is (idempotent).
    """
    if not plaintext:
        return plaintext
    if plaintext.startswith(_ENC_PREFIX):
        return plaintext  # already encrypted

    fernet = _get_fernet()
    if fernet is None:
        return plaintext  # passthrough — no key configured

    try:
        token = fernet.encrypt(plaintext.encode('utf-8'))
        return _ENC_PREFIX + token.decode('utf-8')
    except Exception as exc:
        logger.error(f"[CRED_CRYPTO] Encryption failed: {exc} — storing plaintext")
        return plaintext


def decrypt_credential(stored: str) -> str:
    """
    Decrypt a value previously encrypted by *encrypt_credential*.
    If the value is not encrypted (no prefix) it is returned unchanged.
    """
    if not stored:
        return stored
    if not stored.startswith(_ENC_PREFIX):
        return stored  # plaintext / legacy value

    fernet = _get_fernet()
    if fernet is None:
        logger.warning("[CRED_CRYPTO] Cannot decrypt — CREDENTIAL_ENCRYPTION_KEY not set")
        return stored  # return raw token rather than crashing

    try:
        token = stored[len(_ENC_PREFIX):].encode('utf-8')
        return fernet.decrypt(token).decode('utf-8')
    except Exception as exc:
        logger.error(f"[CRED_CRYPTO] Decryption failed: {exc}")
        return ''


def is_encryption_enabled() -> bool:
    """Return True if CREDENTIAL_ENCRYPTION_KEY is configured and Fernet loads."""
    return _get_fernet() is not None
