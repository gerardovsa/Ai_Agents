"""
Supabase Credentials Manager for InHouse Print Tools

PURPOSE: Fetch SQL Server and API credentials from Supabase for Render deployment
REPLACES: Reading database-config.json from filesystem
USED BY: inhouse_wrapper.py, calculator_wrapper.py, query_library_wrapper.py

ENVIRONMENT DETECTION:
- Local: Reads from database-config.json (C:\Users\gpoli\GIT\In_House_SQL\config\)
- Render: Reads from Supabase (ai_infrastructure.user_platform_credentials)

DATE: November 26, 2025
"""

import os
import json
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class SupabaseCredentialsManager:
    """
    Manages credentials retrieval from Supabase PostgreSQL
    
    Fetches credentials from ai_infrastructure.user_platform_credentials table
    based on platform name (inhouse_print, anthropic, xero_print, shopify)
    """
    
    def __init__(self):
        """Initialize with Supabase connection details from environment"""
        self.db_url = os.environ.get('SUPABASE_DB_URL_POOLER')
        self.is_render = self.db_url is not None
        
        if not self.is_render:
            # Local development - no Supabase connection needed
            print("🔧 Local development mode - will use database-config.json")
        else:
            print(f"🔧 Render deployment mode - using Supabase credentials")
    
    def get_connection(self):
        """Get database connection (Supabase PostgreSQL)"""
        if not self.is_render:
            raise RuntimeError("Supabase connection only available on Render deployment")
        
        return psycopg2.connect(
            self.db_url,
            cursor_factory=RealDictCursor
        )
    
    def get_credentials(self, platform: str, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Fetch credentials for a specific platform
        
        Args:
            platform: Platform identifier (inhouse_print, anthropic, xero_print, shopify)
            user_id: User ID (default: 1 for system/default user)
        
        Returns:
            Dict with credentials data from JSONB 'credentials' column
            None if not found
        
        Example:
            manager = SupabaseCredentialsManager()
            creds = manager.get_credentials('inhouse_print')
            connection_string = creds['connection_string']
        """
        if not self.is_render:
            raise RuntimeError("Cannot fetch from Supabase in local development mode")
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id,
                    platform,
                    credential_type,
                    credential_key,
                    credential_value,
                    credentials,
                    metadata,
                    is_active,
                    created_at,
                    updated_at
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s 
                  AND platform = %s
                  AND is_active = true
                ORDER BY updated_at DESC
                LIMIT 1
            """
            
            cursor.execute(query, (user_id, platform))
            row = cursor.fetchone()
            
            if not row:
                print(f"⚠️  No credentials found for platform: {platform}")
                return None
            
            # Return the JSONB 'credentials' column (contains all secrets)
            return dict(row['credentials']) if row['credentials'] else None
            
        finally:
            conn.close()
    
    def get_inhouse_print_config(self) -> Dict[str, Any]:
        """
        Get InHouse Print SQL Server configuration
        
        Returns:
            Dict with structure matching database-config.json format:
            {
                'DatabaseConnections': {
                    'Primary': {
                        'ConnectionString': '...',
                        'Provider': 'SqlServer',
                        'DatabaseName': 'InHousePrint',
                        'Server': '3.25.76.138\\INHPSQLSERVER',
                        'Port': 1433,
                        'Timeout': 30
                    }
                },
                'AI': {
                    'AnthropicAPIKey': '...',
                    'Model': '...',
                    'MaxTokens': 30000
                }
            }
        """
        # Fetch SQL Server credentials
        sql_creds = self.get_credentials('inhouse_print')
        if not sql_creds:
            raise ValueError("InHouse Print SQL Server credentials not found in Supabase")
        
        # Fetch Anthropic API key
        anthropic_creds = self.get_credentials('anthropic')
        if not anthropic_creds:
            raise ValueError("Anthropic API credentials not found in Supabase")
        
        # Build config matching database-config.json structure
        config = {
            'DatabaseConnections': {
                'Primary': {
                    'ConnectionString': sql_creds['connection_string'],
                    'Provider': sql_creds.get('provider', 'SqlServer'),
                    'DatabaseName': sql_creds['database'],
                    'Server': sql_creds['server'],
                    'Port': sql_creds['port'],
                    'Timeout': sql_creds.get('timeout', 30)
                }
            },
            'AI': {
                'AnthropicAPIKey': anthropic_creds['api_key'],
                'Model': anthropic_creds.get('model', 'claude-sonnet-4-5-20250929'),
                'MaxTokens': anthropic_creds.get('max_tokens', 30000)
            }
        }
        
        return config
    
    def test_connection(self) -> bool:
        """Test if Supabase connection works"""
        if not self.is_render:
            print("✅ Local mode - no Supabase connection to test")
            return True
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            print("✅ Supabase connection successful")
            return result is not None
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return False


def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration (environment-aware)
    
    - Render deployment: Fetches from Supabase
    - Local development: Reads from database-config.json
    
    Returns:
        Dict with database configuration matching database-config.json structure
    
    Usage:
        from supabase_credentials import get_database_config
        
        config = get_database_config()
        connection_string = config['DatabaseConnections']['Primary']['ConnectionString']
        api_key = config['AI']['AnthropicAPIKey']
    """
    manager = SupabaseCredentialsManager()
    
    if manager.is_render:
        # Render deployment - fetch from Supabase
        print("🔍 Fetching credentials from Supabase...")
        config = manager.get_inhouse_print_config()
        print("✅ Credentials loaded from Supabase")
        return config
    else:
        # Local development - read from database-config.json
        print("🔍 Loading credentials from database-config.json...")
        
        # Try multiple possible paths
        possible_paths = [
            # AI_agents project root
            os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database-config.json'),
            # In_House_SQL project
            r'C:\Users\gpoli\GIT\In_House_SQL\config\database-config.json',
            # InHousePrint subfolder
            r'C:\Users\gpoli\GIT\In_House_SQL\InHousePrint\config\database-config.json'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found config at: {path}")
                with open(path, 'r') as f:
                    return json.load(f)
        
        raise FileNotFoundError(
            f"database-config.json not found in any of these locations:\n" +
            "\n".join(f"  - {p}" for p in possible_paths)
        )


# Test code
if __name__ == '__main__':
    print("=" * 60)
    print("Testing Supabase Credentials Manager")
    print("=" * 60)
    
    manager = SupabaseCredentialsManager()
    
    # Test connection
    print("\n1. Testing Supabase connection...")
    manager.test_connection()
    
    # Test credentials fetch
    if manager.is_render:
        print("\n2. Fetching InHouse Print credentials...")
        try:
            config = manager.get_inhouse_print_config()
            print("✅ Config structure:")
            print(f"   - SQL Server: {config['DatabaseConnections']['Primary']['Server']}")
            print(f"   - Database: {config['DatabaseConnections']['Primary']['DatabaseName']}")
            print(f"   - AI Model: {config['AI']['Model']}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    else:
        print("\n2. Testing local config loading...")
        try:
            config = get_database_config()
            print("✅ Config loaded:")
            print(f"   - SQL Server: {config['DatabaseConnections']['Primary']['Server']}")
            print(f"   - Database: {config['DatabaseConnections']['Primary']['DatabaseName']}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 60)
