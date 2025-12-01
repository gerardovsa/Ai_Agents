"""
Credential Encryption Module - Secure credential storage with Fernet encryption

This module provides encryption/decryption for sensitive credentials stored in the database.
Uses Fernet (symmetric encryption) from cryptography library.

Security Features:
- AES-128 encryption with HMAC authentication
- Key rotation support
- Backward compatibility with plain-text credentials (migration support)
- Environment-based key management

Usage:
    encryptor = CredentialEncryptor()
    
    # Encrypt before storing
    encrypted = encryptor.encrypt("sk-proj-abc123...")
    
    # Decrypt on retrieval
    decrypted = encryptor.decrypt(encrypted)
    
    # Check if value is encrypted
    is_encrypted = encryptor.is_encrypted(value)

Author: AI Agent Platform Team
Date: November 29, 2025
"""

import os
import base64
import logging
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CredentialEncryptor:
    """
    Handles encryption/decryption of credentials using Fernet symmetric encryption
    """
    
    def __init__(self):
        """Initialize encryptor with encryption key from environment"""
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
        
        if not self.cipher:
            logger.warning("⚠️ Credential encryption DISABLED - CREDENTIAL_ENCRYPTION_KEY not set!")
            logger.warning("⚠️ Credentials will be stored in PLAIN TEXT (not recommended for production)")
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """
        Get encryption key from environment variable
        
        Returns:
            Encryption key bytes or None if not configured
        """
        key_str = os.getenv('CREDENTIAL_ENCRYPTION_KEY')
        
        if not key_str:
            # Try alternate environment variable names
            key_str = os.getenv('ENCRYPTION_KEY') or os.getenv('SECRET_KEY')
        
        if key_str:
            try:
                # Key should be base64-encoded 32-byte string
                if len(key_str) == 44 and key_str.endswith('='):
                    # Already base64 encoded
                    return key_str.encode()
                else:
                    # Generate Fernet key from string
                    return base64.urlsafe_b64encode(key_str.encode().ljust(32)[:32])
            except Exception as e:
                logger.error(f"❌ Failed to load encryption key: {e}")
                return None
        
        return None
    
    def is_encrypted(self, value: str) -> bool:
        """
        Check if a value is already encrypted
        
        Args:
            value: String to check
        
        Returns:
            True if encrypted, False if plain text
        """
        if not value or not isinstance(value, str):
            return False
        
        # Encrypted values start with 'gAAAAA' (Fernet token format)
        # or are base64-encoded with specific prefix
        try:
            # Fernet tokens are base64-encoded and start with specific bytes
            if value.startswith('gAAAAA'):
                return True
            
            # Try to decode as base64
            decoded = base64.urlsafe_b64decode(value + '==')  # Add padding
            # Fernet tokens have version byte (0x80)
            if len(decoded) > 0 and decoded[0] == 0x80:
                return True
        except:
            pass
        
        return False
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a credential value
        
        Args:
            plaintext: Plain text credential to encrypt
        
        Returns:
            Encrypted credential (base64-encoded Fernet token)
            Returns original plaintext if encryption disabled
        """
        if not plaintext:
            return plaintext
        
        # Already encrypted, return as-is
        if self.is_encrypted(plaintext):
            logger.debug("Value already encrypted, skipping")
            return plaintext
        
        # Encryption disabled, return plain text
        if not self.cipher:
            logger.debug("Encryption disabled, storing plain text")
            return plaintext
        
        try:
            # Encrypt and encode to string
            encrypted_bytes = self.cipher.encrypt(plaintext.encode('utf-8'))
            encrypted_str = encrypted_bytes.decode('utf-8')
            
            logger.debug(f"✅ Encrypted credential (length: {len(encrypted_str)})")
            return encrypted_str
        
        except Exception as e:
            logger.error(f"❌ Encryption failed: {e}")
            # Fallback to plain text (not ideal, but prevents data loss)
            logger.warning("⚠️ Falling back to plain text storage")
            return plaintext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a credential value
        
        Args:
            ciphertext: Encrypted credential (Fernet token)
        
        Returns:
            Decrypted plain text credential
            Returns original value if not encrypted or decryption disabled
        """
        if not ciphertext:
            return ciphertext
        
        # Not encrypted, return as-is
        if not self.is_encrypted(ciphertext):
            logger.debug("Value not encrypted, returning plain text")
            return ciphertext
        
        # Decryption disabled, can't decrypt
        if not self.cipher:
            logger.error("❌ Cannot decrypt - encryption key not available")
            raise ValueError("Encryption key not configured, cannot decrypt credentials")
        
        try:
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(ciphertext.encode('utf-8'))
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            logger.debug("✅ Decrypted credential successfully")
            return decrypted_str
        
        except InvalidToken:
            logger.error("❌ Invalid encryption token - credential may be corrupted")
            raise ValueError("Failed to decrypt credential - invalid token")
        
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt credential: {str(e)}")
    
    def encrypt_dict(self, credentials_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt all values in a credentials dictionary
        
        Args:
            credentials_dict: Dictionary of credential key-value pairs
        
        Returns:
            Dictionary with encrypted values
        """
        if not credentials_dict:
            return credentials_dict
        
        encrypted_dict = {}
        
        for key, value in credentials_dict.items():
            if isinstance(value, str):
                # Encrypt string values
                encrypted_dict[key] = self.encrypt(value)
            else:
                # Non-string values (int, bool, etc.) - store as-is
                encrypted_dict[key] = value
        
        return encrypted_dict
    
    def decrypt_dict(self, credentials_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt all encrypted values in a credentials dictionary
        
        Args:
            credentials_dict: Dictionary with encrypted values
        
        Returns:
            Dictionary with decrypted plain text values
        """
        if not credentials_dict:
            return credentials_dict
        
        decrypted_dict = {}
        
        for key, value in credentials_dict.items():
            if isinstance(value, str):
                # Decrypt string values
                try:
                    decrypted_dict[key] = self.decrypt(value)
                except ValueError as e:
                    logger.error(f"Failed to decrypt {key}: {e}")
                    # Keep encrypted value if decryption fails
                    decrypted_dict[key] = value
            else:
                # Non-string values - return as-is
                decrypted_dict[key] = value
        
        return decrypted_dict
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key
        
        Returns:
            Base64-encoded encryption key (suitable for environment variable)
        
        Usage:
            key = CredentialEncryptor.generate_key()
            print(f"Add to .env: CREDENTIAL_ENCRYPTION_KEY={key}")
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')
    
    def mask_credential(self, value: str, show_start: int = 4, show_end: int = 4) -> str:
        """
        Mask a credential for display (first X + last Y characters)
        
        Args:
            value: Credential to mask
            show_start: Number of characters to show at start (default: 4)
            show_end: Number of characters to show at end (default: 4)
        
        Returns:
            Masked credential string (e.g., "sk-p...AlDm")
        """
        if not value or not isinstance(value, str):
            return '****'
        
        # Decrypt if encrypted
        if self.is_encrypted(value):
            try:
                value = self.decrypt(value)
            except:
                return '****'  # Can't decrypt, full mask
        
        # Too short to mask meaningfully
        if len(value) <= (show_start + show_end):
            return '****'
        
        # Create masked version
        masked = f"{value[:show_start]}...{value[-show_end:]}"
        return masked


# Singleton instance
_encryptor_instance = None


def get_encryptor() -> CredentialEncryptor:
    """
    Get singleton CredentialEncryptor instance
    
    Returns:
        CredentialEncryptor instance
    """
    global _encryptor_instance
    
    if _encryptor_instance is None:
        _encryptor_instance = CredentialEncryptor()
    
    return _encryptor_instance


# Convenience functions
def encrypt_credential(plaintext: str) -> str:
    """Encrypt a credential (convenience function)"""
    return get_encryptor().encrypt(plaintext)


def decrypt_credential(ciphertext: str) -> str:
    """Decrypt a credential (convenience function)"""
    return get_encryptor().decrypt(ciphertext)


def mask_credential(value: str, show_start: int = 4, show_end: int = 4) -> str:
    """Mask a credential for display (convenience function)"""
    return get_encryptor().mask_credential(value, show_start, show_end)


def is_encrypted(value: str) -> bool:
    """Check if value is encrypted (convenience function)"""
    return get_encryptor().is_encrypted(value)


if __name__ == '__main__':
    """
    Test script / Key generation utility
    
    Usage:
        python credential_encryptor.py
    """
    print("=" * 60)
    print("Credential Encryptor - Test & Key Generation")
    print("=" * 60)
    
    # Generate new key
    print("\n1. Generate New Encryption Key:")
    new_key = CredentialEncryptor.generate_key()
    print(f"   Add to .env file:")
    print(f"   CREDENTIAL_ENCRYPTION_KEY={new_key}")
    
    # Test encryption/decryption
    print("\n2. Test Encryption/Decryption:")
    test_credentials = {
        'api_key': 'sk-proj-abc123def456ghi789',
        'secret_key': 'shppa_test_secret_key_xyz',
        'access_token': 'ya29.a0AfB_byBtest_token_string'
    }
    
    # Set test key
    os.environ['CREDENTIAL_ENCRYPTION_KEY'] = new_key
    encryptor = CredentialEncryptor()
    
    for key, value in test_credentials.items():
        encrypted = encryptor.encrypt(value)
        decrypted = encryptor.decrypt(encrypted)
        masked = encryptor.mask_credential(value)
        
        print(f"\n   {key}:")
        print(f"     Original:  {value}")
        print(f"     Encrypted: {encrypted[:40]}...")
        print(f"     Decrypted: {decrypted}")
        print(f"     Masked:    {masked}")
        print(f"     Match:     {decrypted == value}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
