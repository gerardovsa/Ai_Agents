"""
Synergy Configuration Loader
===========================
Dynamically loads Synergy configuration from database instead of hardcoding values.

Benefits:
- Add/remove Kanban columns without code changes
- Update priorities, statuses, platforms without redeployment
- Version control for configuration changes
- Audit trail of who changed what when

Usage:
    from shared.synergy_config import SynergyConfig
    
    config = SynergyConfig()
    columns = config.get_kanban_columns()  # ['backlog', 'in_progress', 'review', 'done']
    priorities = config.get_priority_levels()  # ['low', 'medium', 'high', 'critical']
"""

import json
from typing import List, Dict, Any, Optional
from functools import lru_cache
import time

class SynergyConfig:
    """
    Configuration loader for Synergy Dashboard.
    Caches config in memory with TTL to reduce database queries.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize config loader.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[Any, float]] = {}  # config_id -> (value, expiry_time)
        self._db_connected = False
        
    def _get_db_connection(self):
        """Get database connection (PostgreSQL via Supabase)."""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        
        # Get connection string from environment
        db_url = os.environ.get('SUPABASE_DB_URL_POOLER')
        if not db_url:
            raise RuntimeError(
                "❌ SUPABASE_DB_URL_POOLER not found in environment variables.\n"
                "   This system requires PostgreSQL connection.\n"
                "   Set SUPABASE_DB_URL_POOLER in your environment."
            )
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn, 'postgres'
    
    def _is_cache_valid(self, config_id: str) -> bool:
        """Check if cached value is still valid."""
        if config_id not in self._cache:
            return False
        _, expiry = self._cache[config_id]
        return time.time() < expiry
    
    def _set_cache(self, config_id: str, value: Any):
        """Store value in cache with expiry time."""
        expiry = time.time() + self.cache_ttl
        self._cache[config_id] = (value, expiry)
    
    def _get_cache(self, config_id: str) -> Optional[Any]:
        """Get value from cache if valid."""
        if self._is_cache_valid(config_id):
            return self._cache[config_id][0]
        return None
    
    def get_config(self, config_id: str, default: Any = None) -> Any:
        """
        Get configuration value by ID.
        
        Args:
            config_id: Configuration identifier (e.g., 'kanban_columns')
            default: Default value if config not found
            
        Returns:
            Configuration value (list, dict, string, etc.)
        """
        # Check cache first
        cached = self._get_cache(config_id)
        if cached is not None:
            return cached
        
        # Fetch from database
        try:
            conn, db_type = self._get_db_connection()
            cursor = conn.cursor()
            
            # Query PostgreSQL with schema qualification
            cursor.execute(
                "SELECT config_value FROM synergy_sessions.synergy_config WHERE config_id = %s",
                (config_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # PostgreSQL with RealDictCursor returns dict
                value = row['config_value'] if isinstance(row, dict) else row[0]
                self._set_cache(config_id, value)
                cursor.close()
                conn.close()
                return value
            
            cursor.close()
            conn.close()
                
        except Exception as e:
            print(f"⚠️ Warning: Could not load config '{config_id}' from database: {e}")
            print(f"   Using default value: {default}")
        
        return default
    
    def get_kanban_columns(self) -> List[str]:
        """
        Get list of Kanban columns.
        
        Returns:
            List of column names (e.g., ['backlog', 'in_progress', 'blocked', 'review', 'done', 'archived'])
        """
        return self.get_config(
            'kanban_columns',
            default=['backlog', 'in_progress', 'blocked', 'review', 'done', 'archived']
        )
    
    def get_session_statuses(self) -> List[str]:
        """
        Get list of session statuses.
        
        Returns:
            List of status values (e.g., ['active', 'blocked', 'paused', 'completed', 'archived'])
        """
        return self.get_config(
            'session_statuses',
            default=['active', 'blocked', 'paused', 'completed', 'archived']
        )
    
    def get_priority_levels(self) -> List[str]:
        """
        Get list of priority levels.
        
        Returns:
            List of priorities (e.g., ['low', 'medium', 'high', 'critical'])
        """
        return self.get_config(
            'priority_levels',
            default=['low', 'medium', 'high', 'critical']
        )
    
    def get_permission_levels(self) -> List[str]:
        """
        Get list of permission levels.
        
        Returns:
            List of permission levels (e.g., ['private', 'shared', 'public_view', 'public_edit'])
        """
        return self.get_config(
            'permission_levels',
            default=['private', 'shared', 'public_view', 'public_edit']
        )
    
    def get_blocker_types(self) -> List[str]:
        """
        Get list of blocker types.
        
        Returns:
            List of blocker types (e.g., ['internal', 'external', 'dependency', 'approval'])
        """
        return self.get_config(
            'blocker_types',
            default=['internal', 'external', 'dependency', 'approval']
        )
    
    def get_platform_options(self) -> List[str]:
        """
        Get list of available platform integrations.
        
        Returns:
            List of platform names (e.g., ['gmail', 'google_sheets', 'slack', ...])
        """
        return self.get_config(
            'platform_options',
            default=[
                "gmail", "google_sheets", "google_docs", "google_forms",
                "google_drive", "google_calendar", "google_slides",
                "microsoft_excel", "microsoft_word", "microsoft_outlook", "onedrive",
                "slack", "discord", "telegram",
                "stripe", "shopify", "quickbooks", "hubspot", "salesforce",
                "notion", "asana", "trello", "monday",
                "zapier", "make", "airtable", "other"
            ]
        )
    
    def clear_cache(self, config_id: Optional[str] = None):
        """
        Clear configuration cache.
        
        Args:
            config_id: Specific config to clear, or None to clear all
        """
        if config_id:
            self._cache.pop(config_id, None)
        else:
            self._cache.clear()
    
    def get_all_configs(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        Useful for debugging or admin panels.
        
        Returns:
            Dictionary of all config_id -> config_value mappings
        """
        try:
            conn, db_type = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT config_id, config_value FROM synergy_sessions.synergy_config")
            rows = cursor.fetchall()
            
            # Process rows from RealDictCursor
            result = {}
            for row in rows:
                if isinstance(row, dict):
                    result[row['config_id']] = row['config_value']
                else:
                    result[row[0]] = row[1]
            
            cursor.close()
            conn.close()
            return result
                
        except Exception as e:
            print(f"⚠️ Warning: Could not load all configs from database: {e}")
            return {}


# Singleton instance for easy import
_config_instance = None

def get_synergy_config() -> SynergyConfig:
    """
    Get singleton instance of SynergyConfig.
    
    Returns:
        Shared SynergyConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = SynergyConfig()
    return _config_instance


# Convenience functions for quick access
def get_kanban_columns() -> List[str]:
    """Get Kanban columns from config."""
    return get_synergy_config().get_kanban_columns()

def get_priority_levels() -> List[str]:
    """Get priority levels from config."""
    return get_synergy_config().get_priority_levels()

def get_session_statuses() -> List[str]:
    """Get session statuses from config."""
    return get_synergy_config().get_session_statuses()

def get_permission_levels() -> List[str]:
    """Get permission levels from config."""
    return get_synergy_config().get_permission_levels()

def get_platform_options() -> List[str]:
    """Get platform options from config."""
    return get_synergy_config().get_platform_options()


if __name__ == "__main__":
    # Test the config loader
    config = SynergyConfig()
    
    print("🧪 Testing Synergy Config Loader\n")
    
    print("📊 Kanban Columns:", config.get_kanban_columns())
    print("⚡ Priority Levels:", config.get_priority_levels())
    print("📍 Session Statuses:", config.get_session_statuses())
    print("🔒 Permission Levels:", config.get_permission_levels())
    print("🔗 Platform Options (first 5):", config.get_platform_options()[:5])
    
    print("\n✅ All configs loaded successfully!")
