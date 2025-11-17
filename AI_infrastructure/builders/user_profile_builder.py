"""
User Profile Builder - Fetch user context from database
Part of V4 Modular Architecture

Responsibilities:
- Query user data from ai_infrastructure.db
- Extract username, email, OAuth status
- Get location via IP geolocation (optional)
- Format user context for system prompt
"""

from typing import Dict, Any, Optional
import sqlite3  # Keep for type hints
from shared.db_connection_wrapper import get_connection
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


class UserProfileBuilder:
    """
    Builds user profile context from database.
    
    Features:
    - Fetch user record from users table
    - Get OAuth connection status (Google, Microsoft)
    - Extract location data
    - Format for system prompt inclusion
    
    Usage:
        builder = UserProfileBuilder()
        
        # Get user profile
        profile = builder.get_user_profile(user_id=1)
        print(f"User: {profile['username']}")
        
        # Build context for system prompt
        context = builder.build_prompt_context(user_id=1)
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize user profile builder.
        
        Args:
            db_path: Optional database path (defaults to constants.DB_PATH)
        """
        self.db_path = db_path or DB_PATH
        logger.info(f"👤 UserProfileBuilder initialized (db: {Path(self.db_path).name})")

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = get_connection('ai_infrastructure')
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Fetch user profile from database.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile dict with structure:
            {
                "user_id": int,
                "username": str,
                "email": str,
                "created_at": str,
                "last_login": str,
                "is_active": bool,
                "location": str or None,
                "timezone": str or None
            }
            
        Raises:
            ValueError: If user not found
            
        Example:
            profile = builder.get_user_profile(user_id=1)
            print(f"User: {profile['username']}")
        """
        logger.debug(f"📂 Fetching profile for user_id={user_id}")
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, created_at, last_active,
                       is_primary, metadata, has_google_oauth, has_microsoft_oauth,
                       allowed_dashboards, role
                FROM users
                WHERE id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.error(f" User not found: user_id={user_id}")
                raise ValueError(f"User not found: {user_id}")
            
            profile = dict(row)
            logger.info(f"Profile loaded: {profile['username']} ({profile['email']})")
            
            return profile
            
        except sqlite3.Error as e:
            logger.error(f" Database error: {e}")
            raise

    def get_oauth_status(self, user_id: int) -> Dict[str, bool]:
        """
        Get OAuth connection status for user.
        NOW USES SIMPLIFIED BOOLEAN FLAGS - No joins needed!
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with platform connection status:
            {
                "google": bool,
                "microsoft": bool,
                "has_any_oauth": bool
            }
            
        Example:
            oauth = builder.get_oauth_status(user_id=1)
            if oauth['google']:
                print("Google Workspace connected")
        """
        logger.debug(f"🔐 Checking OAuth status for user_id={user_id}")
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # SIMPLIFIED: Just query boolean flags from users table
            cursor.execute("""
                SELECT has_google_oauth, has_microsoft_oauth
                FROM users
                WHERE id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"⚠️ User not found: user_id={user_id}")
                return {'google': False, 'microsoft': False, 'has_any_oauth': False}
            
            # Build status dict from boolean flags
            status = {
                'google': bool(row['has_google_oauth']),
                'microsoft': bool(row['has_microsoft_oauth'])
            }
            
            status['has_any_oauth'] = status['google'] or status['microsoft']
            
            logger.info(f"OAuth status: Google={status['google']}, "
                       f"Microsoft={status['microsoft']}")
            
            return status
            
        except sqlite3.Error as e:
            logger.warning(f"⚠️ Could not fetch OAuth status: {e}")
            return {'google': False, 'microsoft': False, 'has_any_oauth': False}

    def build_prompt_context(self, user_id: int) -> str:
        """
        Build user context section for system prompt.
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted context string for system prompt
            
        Example:
            context = builder.build_prompt_context(user_id=1)
            system_prompt = f"{base_prompt}\n\n{context}"
        """
        logger.debug(f"📝 Building prompt context for user_id={user_id}")
        
        try:
            # Get profile
            profile = self.get_user_profile(user_id)
            
            # Get OAuth status
            oauth = self.get_oauth_status(user_id)
            
            # Build context
            context_parts = [
                "=== USER CONTEXT ===",
                f"Username: {profile['username']}",
                f"Email: {profile['email']}"
            ]
            
            # Add location if available
            if profile.get('location'):
                context_parts.append(f"Location: {profile['location']}")
            
            if profile.get('timezone'):
                context_parts.append(f"Timezone: {profile['timezone']}")
            
            # Add OAuth status
            context_parts.append("\n=== CONNECTED PLATFORMS ===")
            
            if oauth['google']:
                context_parts.append("Google Workspace - CONNECTED")
            else:
                context_parts.append(" Google Workspace - Not connected")
            
            if oauth['microsoft']:
                context_parts.append("Microsoft 365 - CONNECTED")
            else:
                context_parts.append(" Microsoft 365 - Not connected")
            
            if not oauth['has_any_oauth']:
                context_parts.append("\n⚠️ No platforms connected. User cannot use platform-specific tools.")
            
            context = '\n'.join(context_parts)
            
            logger.info(f"Prompt context built: {len(context)} chars")
            logger.debug(f"Context preview:\n{context[:200]}...")
            
            return context
            
        except Exception as e:
            logger.error(f" Error building context: {e}")
            return "=== USER CONTEXT ===\nError loading user profile"

    def get_user_capabilities(self, user_id: int) -> Dict[str, Any]:
        """
        Get summary of user's capabilities based on OAuth connections.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with:
            {
                "can_use_google_tools": bool,
                "can_use_microsoft_tools": bool,
                "available_platforms": list,
                "total_tools_available": int (estimated)
            }
            
        Example:
            caps = builder.get_user_capabilities(user_id=1)
            if caps['can_use_google_tools']:
                print(f"User can access {caps['total_tools_available']} tools")
        """
        logger.debug(f"🔍 Getting capabilities for user_id={user_id}")
        
        oauth = self.get_oauth_status(user_id)
        
        available_platforms = []
        estimated_tools = 0
        
        if oauth['google']:
            available_platforms.append('google_workspace')
            estimated_tools += 100  # Approximate Google tool count
        
        if oauth['microsoft']:
            available_platforms.append('microsoft_365')
            estimated_tools += 80  # Approximate Microsoft tool count
        
        # Always available: Calculator tools (7)
        available_platforms.append('calculator')
        estimated_tools += 7
        
        capabilities = {
            'can_use_google_tools': oauth['google'],
            'can_use_microsoft_tools': oauth['microsoft'],
            'available_platforms': available_platforms,
            'total_tools_available': estimated_tools
        }
        
        logger.info(f"Capabilities: {len(available_platforms)} platforms, "
                   f"~{estimated_tools} tools")
        
        return capabilities


# Export
__all__ = ['UserProfileBuilder']
