"""
VSA Supabase Connector
======================

Connects to the VSA (Veterinary Services Australia) Supabase database
for veterinary call transcripts and alerts.

Created: December 14, 2025
Purpose: Replace tools.Database_Data import with proper Supabase connection
"""

import os
import sys
import json
from typing import Optional, Dict, Any
from supabase import create_client, Client

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class VSASupabaseConnector:
    """
    Connector for VSA Veterinary Alerts Supabase database.
    
    Reads credentials from ai_infrastructure.user_platform_credentials table
    where platform='supabase' and metadata contains VSA-related info.
    
    Usage:
        connector = VSASupabaseConnector()
        client = connector.get_client()
        
        # Query veterinary calls
        result = client.table('call_full_transcript_and_full_analysis')\
            .select('*')\
            .eq('call_id', 'some_id')\
            .execute()
    """
    
    def __init__(self):
        """Initialize VSA Supabase connector with credentials from database."""
        self.client: Optional[Client] = None
        self._credentials: Optional[Dict[str, Any]] = None
        self._initialize_client()
    
    def _get_credentials_from_db(self) -> Optional[Dict[str, Any]]:
        """
        Fetch VSA Supabase credentials from user_platform_credentials table.
        
        Returns:
            Dict with url, service_key, etc. or None if not found
        """
        try:
            from shared.database_utils import get_database_connection
            
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            try:
                # Query for Supabase credentials with VSA metadata
                query = """
                    SELECT credentials, metadata
                    FROM ai_infrastructure.user_platform_credentials
                    WHERE platform = %s
                      AND is_active = true
                      AND (
                          metadata::text ILIKE %s
                          OR metadata::text ILIKE %s
                          OR credentials::text ILIKE %s
                      )
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                cursor.execute(query, ('supabase', '%veterinary%', '%VSA%', '%wuwmvtslltqhaycyukxk%'))
                
                rows = cursor.fetchall()
                
                if rows and len(rows) > 0:
                    row = rows[0]
                    credentials_json = row['credentials']
                    metadata_json = row['metadata']
                    
                    # Parse JSON if string
                    if isinstance(credentials_json, str):
                        credentials_json = json.loads(credentials_json)
                    if isinstance(metadata_json, str):
                        metadata_json = json.loads(metadata_json)
                    
                    return {
                        'url': credentials_json.get('url'),
                        'service_key': credentials_json.get('service_key'),
                        'anon_key': credentials_json.get('anon_key'),
                        'db_host': credentials_json.get('db_host'),
                        'db_name': credentials_json.get('db_name'),
                        'db_user': credentials_json.get('db_user'),
                        'db_password': credentials_json.get('db_password'),
                        'metadata': metadata_json
                    }
                
                return None
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"[VSA Connector] Error fetching credentials from DB: {e}", file=sys.stderr)
            return None
    
    def _get_credentials_from_env(self) -> Optional[Dict[str, Any]]:
        """
        Fallback: Get VSA credentials from environment variables.
        
        Returns:
            Dict with url, service_key, etc. or None if not found
        """
        url = os.getenv('VSA_SUPABASE_URL')
        service_key = os.getenv('VSA_SUPABASE_SERVICE_KEY')
        
        if url and service_key:
            return {
                'url': url,
                'service_key': service_key,
                'anon_key': os.getenv('VSA_SUPABASE_ANON_KEY', service_key)
            }
        
        return None
    
    def _initialize_client(self):
        """Initialize Supabase client with VSA credentials."""
        try:
            # Try database first, then environment variables
            self._credentials = self._get_credentials_from_db() or self._get_credentials_from_env()
            
            if not self._credentials:
                print("[VSA Connector] No VSA Supabase credentials found", file=sys.stderr)
                return
            
            url = self._credentials.get('url')
            # Use service_key for admin operations (service_role has full access)
            key = self._credentials.get('service_key') or self._credentials.get('anon_key')
            
            if not url or not key:
                print("[VSA Connector] Missing required credentials (url or key)", file=sys.stderr)
                return
            
            # Create Supabase client
            self.client = create_client(url, key)
            
            print(f"✅ [VSA Connector] Connected to VSA Supabase: {url}", file=sys.stderr)
            
        except Exception as e:
            print(f"[VSA Connector] Error initializing client: {e}", file=sys.stderr)
            self.client = None
    
    def get_client(self) -> Optional[Client]:
        """
        Get initialized Supabase client.
        
        Returns:
            Supabase Client instance or None if not initialized
        """
        return self.client
    
    def is_connected(self) -> bool:
        """Check if connector is successfully initialized."""
        return self.client is not None
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information (for debugging).
        
        Returns:
            Dict with connection status and metadata
        """
        if not self._credentials:
            return {'connected': False, 'error': 'No credentials'}
        
        return {
            'connected': self.is_connected(),
            'url': self._credentials.get('url'),
            'tables': self._credentials.get('metadata', {}).get('tables', []),
            'purpose': self._credentials.get('metadata', {}).get('purpose', 'Unknown')
        }


# Singleton instance
_vsa_connector: Optional[VSASupabaseConnector] = None


def get_vsa_connector() -> VSASupabaseConnector:
    """
    Get singleton VSA Supabase connector instance.
    
    Returns:
        VSASupabaseConnector instance
    
    Usage:
        connector = get_vsa_connector()
        client = connector.get_client()
    """
    global _vsa_connector
    
    if _vsa_connector is None:
        _vsa_connector = VSASupabaseConnector()
    
    return _vsa_connector


def get_vsa_supabase_client() -> Optional[Client]:
    """
    Get VSA Supabase client (convenience function).
    
    Returns:
        Supabase Client instance or None if not initialized
    
    Usage:
        client = get_vsa_supabase_client()
        if client:
            result = client.table('veterinary_calls').select('*').execute()
    """
    connector = get_vsa_connector()
    return connector.get_client()
