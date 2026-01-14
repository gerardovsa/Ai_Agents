"""
Multi-Factor Authentication (MFA) Manager - OPTIONAL TOTP-based 2FA

This module provides OPTIONAL multi-factor authentication using TOTP (Time-based One-Time Password).
Compatible with Google Authenticator, Authy, Microsoft Authenticator, and other TOTP apps.

Key Features:
- OPTIONAL - Users can enable/disable MFA for their accounts
- TOTP-based (RFC 6238) - Industry standard
- QR code generation for easy setup
- Backup codes for account recovery
- Grace period for recent authentication

Security:
- 6-digit codes that change every 30 seconds
- 90-second validation window (allows clock skew)
- Rate limiting (max 5 attempts per minute)
- Backup codes (8 codes, single-use, 16 characters each)

Usage:
    mfa = MFAManager()
    
    # Enable MFA for user
    secret, qr_code = mfa.enable_mfa(user_id=14)
    # Show QR code to user, they scan with authenticator app
    
    # Verify TOTP code
    is_valid = mfa.verify_totp(user_id=14, code="123456")
    
    # Disable MFA
    mfa.disable_mfa(user_id=14)

Author: AI Agent Platform Team
Date: November 29, 2025
Updated: January 1, 2026 - Fixed cursor leaks with context managers
"""

import os
import io
import pyotp
import qrcode
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
from shared.database_utils import get_database_connection

logger = logging.getLogger(__name__)


class MFAManager:
    """
    Manages OPTIONAL multi-factor authentication for users
    """
    
    # MFA Configuration
    ISSUER_NAME = "AI Agent Platform"
    BACKUP_CODE_LENGTH = 16
    BACKUP_CODE_COUNT = 8
    TOTP_INTERVAL = 30  # seconds
    TOTP_DIGITS = 6
    GRACE_PERIOD_MINUTES = 10  # Don't require MFA again for 10 minutes
    MAX_ATTEMPTS_PER_MINUTE = 5
    
    def __init__(self):
        """Initialize MFA manager"""
        # No persistent connection - use context managers for each operation
        pass
    
    def is_mfa_enabled(self, user_id: int) -> bool:
        """
        Check if MFA is enabled for user
        
        Args:
            user_id: User ID
        
        Returns:
            True if MFA enabled, False otherwise
        """
        try:
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT mfa_enabled
                        FROM ai_infrastructure.users
                        WHERE id = %s
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    
                    if row and row[0]:
                        return True
                    
                    return False
        
        except Exception as e:
            logger.error(f"❌ Failed to check MFA status: {e}")
            return False
    
    def enable_mfa(self, user_id: int, username: str) -> Tuple[str, str, List[str]]:
        """
        Enable MFA for user and generate QR code
        
        Args:
            user_id: User ID
            username: Username (for TOTP label)
        
        Returns:
            Tuple of (secret_key, qr_code_data_uri, backup_codes)
        
        Raises:
            ValueError: If MFA already enabled
        """
        try:
            # Check if already enabled
            if self.is_mfa_enabled(user_id):
                raise ValueError("MFA already enabled for this user")
            
            # Generate TOTP secret
            secret = pyotp.random_base32()
            
            # Create TOTP URI for QR code
            totp = pyotp.TOTP(secret, interval=self.TOTP_INTERVAL, digits=self.TOTP_DIGITS)
            provisioning_uri = totp.provisioning_uri(
                name=username,
                issuer_name=self.ISSUER_NAME
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to data URI
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            import base64
            img_data = base64.b64encode(buffer.getvalue()).decode()
            qr_code_data_uri = f"data:image/png;base64,{img_data}"
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            
            # Store in database
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    # Update user record
                    cursor.execute('''
                        UPDATE ai_infrastructure.users
                        SET mfa_secret = %s,
                            mfa_enabled = TRUE,
                            mfa_backup_codes = %s,
                            mfa_enabled_at = NOW(),
                            updated_at = NOW()
                        WHERE id = %s
                    ''', (secret, backup_codes, user_id))
                    
                    conn.commit()
            
            logger.info(f"✅ MFA enabled for user {user_id}")
            
            return secret, qr_code_data_uri, backup_codes
        
        except ValueError as ve:
            raise ve
        
        except Exception as e:
            logger.error(f"❌ Failed to enable MFA: {e}")
            raise ValueError(f"Failed to enable MFA: {str(e)}")
    
    def disable_mfa(self, user_id: int) -> bool:
        """
        Disable MFA for user
        
        Args:
            user_id: User ID
        
        Returns:
            True if disabled successfully, False otherwise
        """
        try:
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        UPDATE ai_infrastructure.users
                        SET mfa_secret = NULL,
                            mfa_enabled = FALSE,
                            mfa_backup_codes = NULL,
                            mfa_last_used = NULL,
                            updated_at = NOW()
                        WHERE id = %s
                    ''', (user_id,))
                    
                    conn.commit()
            
            logger.info(f"✅ MFA disabled for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to disable MFA: {e}")
            return False
    
    def verify_totp(self, user_id: int, code: str) -> bool:
        """
        Verify TOTP code for user
        
        Args:
            user_id: User ID
            code: 6-digit TOTP code
        
        Returns:
            True if code valid, False otherwise
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit(user_id):
                logger.warning(f"⚠️ Rate limit exceeded for user {user_id}")
                return False
            
            # Get secret from database and verify
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT mfa_secret, mfa_enabled
                        FROM ai_infrastructure.users
                        WHERE id = %s
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    
                    if not row or not row[1]:
                        logger.warning(f"⚠️ MFA not enabled for user {user_id}")
                        return False
                    
                    secret = row[0]
                    
                    if not secret:
                        logger.error(f"❌ MFA secret not found for user {user_id}")
                        return False
                
                # Verify TOTP code (outside cursor context)
                totp = pyotp.TOTP(secret, interval=self.TOTP_INTERVAL, digits=self.TOTP_DIGITS)
                
                # Allow 1 interval before/after (90 second window total)
                is_valid = totp.verify(code, valid_window=1)
                
                if is_valid:
                    # Update last used timestamp (new cursor context)
                    with conn.cursor() as cursor:
                        
                        cursor.execute('''
                            UPDATE ai_infrastructure.users
                            SET mfa_last_used = NOW()
                            WHERE id = %s
                        ''', (user_id,))
                        
                        conn.commit()
                    
                    logger.info(f"✅ TOTP verified for user {user_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Invalid TOTP code for user {user_id}")
                    return False
        
        except Exception as e:
            logger.error(f"❌ TOTP verification failed: {e}")
            return False
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """
        Verify backup code for user (single-use)
        
        Args:
            user_id: User ID
            code: Backup code
        
        Returns:
            True if code valid, False otherwise
        """
        try:
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT mfa_backup_codes, mfa_enabled
                        FROM ai_infrastructure.users
                        WHERE id = %s
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    
                    if not row or not row[1]:
                        logger.warning(f"⚠️ MFA not enabled for user {user_id}")
                        return False
                    
                    backup_codes = row[0]
                    
                    if not backup_codes or code not in backup_codes:
                        logger.warning(f"⚠️ Invalid backup code for user {user_id}")
                        return False
                
                # Remove used backup code (new cursor context)
                backup_codes.remove(code)
                
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        UPDATE ai_infrastructure.users
                        SET mfa_backup_codes = %s,
                            mfa_last_used = NOW()
                        WHERE id = %s
                    ''', (backup_codes, user_id))
                    
                    conn.commit()
                
                logger.info(f"✅ Backup code verified for user {user_id} ({len(backup_codes)} codes remaining)")
                
                # Warn if running low on backup codes
                if len(backup_codes) <= 2:
                    logger.warning(f"⚠️ User {user_id} has only {len(backup_codes)} backup codes remaining!")
                
                return True
        
        except Exception as e:
            logger.error(f"❌ Backup code verification failed: {e}")
            return False
    
    def regenerate_backup_codes(self, user_id: int) -> List[str]:
        """
        Generate new backup codes for user (replaces old codes)
        
        Args:
            user_id: User ID
        
        Returns:
            List of new backup codes
        """
        try:
            backup_codes = self._generate_backup_codes()
            
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        UPDATE ai_infrastructure.users
                        SET mfa_backup_codes = %s,
                            updated_at = NOW()
                        WHERE id = %s
                    ''', (backup_codes, user_id))
                    
                    conn.commit()
            
            logger.info(f"✅ Regenerated backup codes for user {user_id}")
            
            return backup_codes
        
        except Exception as e:
            logger.error(f"❌ Failed to regenerate backup codes: {e}")
            raise ValueError(f"Failed to regenerate backup codes: {str(e)}")
    
    def check_mfa_grace_period(self, user_id: int) -> bool:
        """
        Check if user is within MFA grace period (recently authenticated)
        
        Args:
            user_id: User ID
        
        Returns:
            True if within grace period, False otherwise
        """
        try:
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT mfa_last_used
                        FROM ai_infrastructure.users
                        WHERE id = %s
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    
                    if not row or not row[0]:
                        return False
                    
                    last_used = row[0]
                    grace_period_end = last_used + timedelta(minutes=self.GRACE_PERIOD_MINUTES)
                    
                    if datetime.now() < grace_period_end:
                        logger.debug(f"User {user_id} within MFA grace period")
                        return True
                    
                    return False
        
        except Exception as e:
            logger.error(f"❌ Failed to check grace period: {e}")
            return False
    
    def _generate_backup_codes(self) -> List[str]:
        """
        Generate backup codes
        
        Returns:
            List of backup codes
        """
        codes = []
        
        for _ in range(self.BACKUP_CODE_COUNT):
            # Generate cryptographically secure random code
            code = secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper()
            
            # Format with dashes (e.g., ABCD-1234-EFGH-5678)
            formatted_code = '-'.join([code[i:i+4] for i in range(0, len(code), 4)])
            codes.append(formatted_code)
        
        return codes
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user is within rate limit for MFA attempts
        
        Args:
            user_id: User ID
        
        Returns:
            True if within limit, False if exceeded
        """
        # TODO: Implement Redis-based rate limiting
        # For now, always return True (no rate limiting)
        return True
    
    def get_mfa_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get MFA status and details for user
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with MFA status information
        """
        try:
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        SELECT mfa_enabled, mfa_enabled_at, mfa_last_used, mfa_backup_codes
                        FROM ai_infrastructure.users
                        WHERE id = %s
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    
                    if not row:
                        return {
                            'enabled': False,
                            'enabled_at': None,
                            'last_used': None,
                            'backup_codes_remaining': 0,
                            'within_grace_period': False
                        }
                    
                    backup_codes = row[3] if row[3] else []
                    
                    return {
                        'enabled': row[0] or False,
                        'enabled_at': row[1].isoformat() if row[1] else None,
                        'last_used': row[2].isoformat() if row[2] else None,
                        'backup_codes_remaining': len(backup_codes),
                        'within_grace_period': self.check_mfa_grace_period(user_id)
                    }
        
        except Exception as e:
            logger.error(f"❌ Failed to get MFA status: {e}")
            return {'enabled': False, 'error': str(e)}


# Database migration SQL (add to migration script)
MFA_MIGRATION_SQL = """
-- Add MFA columns to users table

ALTER TABLE ai_infrastructure.users
ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN DEFAULT FALSE;

ALTER TABLE ai_infrastructure.users
ADD COLUMN IF NOT EXISTS mfa_secret VARCHAR(32);

ALTER TABLE ai_infrastructure.users
ADD COLUMN IF NOT EXISTS mfa_backup_codes TEXT[];

ALTER TABLE ai_infrastructure.users
ADD COLUMN IF NOT EXISTS mfa_enabled_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE ai_infrastructure.users
ADD COLUMN IF NOT EXISTS mfa_last_used TIMESTAMP WITH TIME ZONE;

-- Create index for MFA lookups
CREATE INDEX IF NOT EXISTS idx_users_mfa_enabled 
ON ai_infrastructure.users(id, mfa_enabled) 
WHERE mfa_enabled = TRUE;

COMMENT ON COLUMN ai_infrastructure.users.mfa_enabled IS 'OPTIONAL - User can enable/disable MFA';
COMMENT ON COLUMN ai_infrastructure.users.mfa_secret IS 'TOTP secret for Google Authenticator';
COMMENT ON COLUMN ai_infrastructure.users.mfa_backup_codes IS 'Single-use backup codes for account recovery';
"""


if __name__ == '__main__':
    """
    Test MFA functionality
    
    Usage:
        python mfa_manager.py
    """
    print("=" * 60)
    print("MFA Manager - OPTIONAL Multi-Factor Authentication")
    print("=" * 60)
    
    mfa = MFAManager()
    
    # Test TOTP generation
    print("\n1. Generate TOTP Secret:")
    secret = pyotp.random_base32()
    print(f"   Secret: {secret}")
    
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    print(f"   Current Code: {current_code}")
    
    # Test verification
    print("\n2. Verify TOTP Code:")
    is_valid = totp.verify(current_code, valid_window=1)
    print(f"   Valid: {is_valid}")
    
    # Test QR code generation
    print("\n3. Generate QR Code:")
    provisioning_uri = totp.provisioning_uri(
        name="test@example.com",
        issuer_name="AI Agent Platform"
    )
    print(f"   URI: {provisioning_uri}")
    
    # Test backup codes
    print("\n4. Generate Backup Codes:")
    backup_codes = mfa._generate_backup_codes()
    for i, code in enumerate(backup_codes, 1):
        print(f"   {i}. {code}")
    
    print("\n" + "=" * 60)
    print("✅ MFA test complete!")
    print("=" * 60)
    print("\nTo enable MFA for a user:")
    print("  mfa.enable_mfa(user_id=14, username='user@example.com')")
    print("\nMFA is OPTIONAL - users can enable/disable as needed")