"""
Credential Fetcher - Fetch OAuth credentials from database
Part of V4 Modular Architecture

Responsibilities:
- Query OAuth credentials from user_platform_credentials table
- Format credentials for tool executor injection
- Handle credential expiration and refresh
- Support multiple platforms (Google, Microsoft)
"""

from typing import Dict, Any, Optional
import sqlite3  # Keep for type hints
from shared.db_connection_wrapper import get_connection
from datetime import datetime
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from AI_infrastructure.utils.logger import get_logger
from AI_infrastructure.config.constants import DB_PATH

logger = get_logger(__name__)


class CredentialFetcher:
    """
    Fetches OAuth credentials from database for tool execution.
    
    Features:
    - Query credentials by user_id and platform
    - Format for tool executor injection
    - Check credential validity
    - Support Google and Microsoft OAuth
    
    Usage:
        fetcher = CredentialFetcher()
        
        # Get Google credentials
        google_creds = fetcher.get_credentials(
            user_id=1, 
            platform='google'
        )
        
        # Get all user credentials
        all_creds = fetcher.get_all_credentials(user_id=1)
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize credential fetcher.
        
        Args:
            db_path: Optional database path (defaults to constants.DB_PATH)
        """
        self.db_path = db_path or DB_PATH
        logger.info(f"🔐 CredentialFetcher initialized (db: {Path(self.db_path).name})")

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = get_connection('ai_infrastructure')
        conn.row_factory = sqlite3.Row
        return conn

    def get_credentials(self, user_id: int, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get credentials for specific platform.
        
        Args:
            user_id: User ID
            platform: Platform name ('google', 'microsoft', etc.)
            
        Returns:
            Credential dict or None if not found:
            {
                "access_token": str,
                "refresh_token": str,
                "token_uri": str,
                "client_id": str,
                "client_secret": str,
                "expires_at": str,
                "is_valid": bool
            }
            
        Example:
            creds = fetcher.get_credentials(user_id=1, platform='google')
            if creds and creds['is_valid']:
                print("Valid credentials found")
        """
        logger.debug(f"🔍 Fetching {platform} credentials for user_id={user_id}")
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Normalize platform name for query
            platform_pattern = f"%{platform}%"
            
            # Query NEW oauth_tokens table (simplified column structure)
            cursor.execute("""
                SELECT platform, access_token, refresh_token, 
                       token_type, expires_at, scope, metadata,
                       created_at, updated_at, last_refreshed_at
                FROM oauth_tokens
                WHERE user_id = ? AND platform LIKE ?
                ORDER BY updated_at DESC
                LIMIT 1
            """, (user_id, platform_pattern))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"⚠️ No credentials found for {platform}")
                return None
            
            # Build credential dict from columns (not key-value pairs!)
            creds = {
                'platform': row['platform'],
                'access_token': row['access_token'],
                'refresh_token': row['refresh_token'],
                'token_type': row['token_type'] or 'Bearer',
                'expires_at': row['expires_at'],
                'scope': row['scope'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'last_refreshed_at': row['last_refreshed_at']
            }
            
            # Parse metadata JSON if exists
            if row['metadata']:
                import json
                try:
                    creds['metadata'] = json.loads(row['metadata'])
                except:
                    pass
            
            # Check if expired
            if creds['expires_at']:
                try:
                    expires = datetime.fromisoformat(creds['expires_at'])
                    creds['is_valid'] = expires > datetime.utcnow()
                except:
                    creds['is_valid'] = True  # Assume valid if can't parse
            else:
                creds['is_valid'] = True
            
            status = "valid" if creds['is_valid'] else "⚠️ expired"
            logger.info(f"Credentials found for {platform}: {status}")
            
            return creds
            
        except sqlite3.Error as e:
            logger.error(f" Database error: {e}")
            return None

    def get_all_credentials(self, user_id: int) -> Dict[str, Any]:
        """
        Get all credentials for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with credentials by platform:
            {
                "google": {...} or None,
                "microsoft": {...} or None
            }
            
        Example:
            all_creds = fetcher.get_all_credentials(user_id=1)
            if all_creds['google']:
                print("Google connected")
        """
        logger.debug(f"🔍 Fetching all credentials for user_id={user_id}")
        
        credentials = {
            'google': self.get_credentials(user_id, 'google'),
            'microsoft': self.get_credentials(user_id, 'microsoft')
        }
        
        connected_count = sum(1 for creds in credentials.values() if creds)
        logger.info(f"Found credentials for {connected_count} platforms")
        
        return credentials

    def format_for_injection(self, credentials: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format credentials for tool executor injection.
        
        Args:
            credentials: Credential dict from get_credentials()
            
        Returns:
            Formatted dict for injection:
            {
                "access_token": str,
                "refresh_token": str,
                "token_uri": str,
                "client_id": str,
                "client_secret": str
            }
            
        Example:
            creds = fetcher.get_credentials(user_id=1, platform='google')
            injected = fetcher.format_for_injection(creds)
            # Pass to tool executor
        """
        if not credentials:
            logger.debug("⚠️ No credentials to format")
            return {}
        
        # Extract only fields needed for injection
        injected = {
            'access_token': credentials.get('access_token'),
            'refresh_token': credentials.get('refresh_token'),
            'token_uri': credentials.get('token_uri'),
            'client_id': credentials.get('client_id'),
            'client_secret': credentials.get('client_secret')
        }
        
        # Remove None values
        injected = {k: v for k, v in injected.items() if v is not None}
        
        logger.debug(f"Formatted {len(injected)} credential fields for injection")
        
        return injected

    def get_credentials_for_injection(self, user_id: int, 
                                     platform: str) -> Dict[str, Any]:
        """
        Get credentials and format for injection in one call.
        
        Args:
            user_id: User ID
            platform: Platform name
            
        Returns:
            Formatted credentials dict
            
        Example:
            injected = fetcher.get_credentials_for_injection(
                user_id=1, 
                platform='google'
            )
            # Ready to pass to tool executor
        """
        logger.debug(f"🔍 Getting {platform} credentials for injection")
        
        creds = self.get_credentials(user_id, platform)
        
        if not creds:
            logger.warning(f"⚠️ No credentials available for {platform}")
            return {}
        
        if not creds.get('is_valid', True):
            logger.warning(f"⚠️ Credentials expired for {platform}")
            # Still return them - tool might auto-refresh
        
        return self.format_for_injection(creds)

    def check_platform_availability(self, user_id: int, 
                                   platform: str) -> bool:
        """
        Check if user has valid credentials for platform.
        
        Args:
            user_id: User ID
            platform: Platform name
            
        Returns:
            True if valid credentials exist
            
        Example:
            if fetcher.check_platform_availability(user_id=1, platform='google'):
                print("User can use Google tools")
        """
        logger.debug(f"🔍 Checking {platform} availability for user_id={user_id}")
        
        creds = self.get_credentials(user_id, platform)
        
        if not creds:
            logger.debug(f" Platform unavailable: {platform} (no credentials)")
            return False
        
        if not creds.get('is_valid', True):
            logger.debug(f"⚠️ Platform unavailable: {platform} (expired credentials)")
            return False
        
        logger.debug(f"Platform available: {platform}")
        return True


# Export
__all__ = ['CredentialFetcher']
