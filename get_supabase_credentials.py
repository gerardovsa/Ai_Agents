#!/usr/bin/env python3
"""
get_supabase_credentials.py - Retrieve Supabase credentials from user_platform_credentials

Purpose: Fetch Supabase API credentials for a specific user from the database
Usage: Can be called by Flask endpoints to provide credentials to frontend modules

Date: November 30, 2025
Project: AI_agents - VSA Veterinary Alerts Module
"""

import sys
import os
import json
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI_infrastructure'))

from shared.database_utils import get_database_connection


def get_supabase_credentials(user_id: int = 1, platform: str = 'supabase') -> Optional[Dict]:
    """
    Retrieve Supabase credentials from user_platform_credentials table
    
    Args:
        user_id: User ID (default: 1 for admin)
        platform: Platform name (default: 'supabase')
    
    Returns:
        Dictionary with Supabase credentials or None if not found
        
    Example Response:
        {
            'url': 'https://wuwmvtslltqhaycyukxk.supabase.co',
            'anon_key': 'eyJhbGciOiJ...',
            'service_key': 'eyJhbGciOiJ...',
            'db_host': 'db.wuwmvtslltqhaycyukxk.supabase.co',
            'db_port': '5432',
            'db_name': 'postgres',
            'db_user': 'postgres',
            'db_password': 'phonetranscriptions11!',
            'project_id': 'wuwmvtslltqhaycyukxk',
            'region': 'ap-southeast-2'
        }
    """
    try:
        # Get database connection
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query credentials
        query = """
            SELECT 
                credentials,
                credential_value,
                metadata,
                is_active
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
            print(f"❌ No credentials found for user_id={user_id}, platform={platform}")
            cursor.close()
            conn.close()
            return None
        
        # Access row as dictionary (RealDictRow from psycopg2)
        credentials_json = row['credentials']
        credential_value = row['credential_value']
        metadata_json = row['metadata']
        is_active = row['is_active']
        
        # PostgreSQL JSONB columns are already parsed as dicts
        if isinstance(credentials_json, dict):
            credentials = credentials_json
        elif isinstance(credentials_json, str) and credentials_json:
            credentials = json.loads(credentials_json)
        else:
            credentials = {}
        
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully retrieved Supabase credentials for user_id={user_id}")
        print(f"   URL: {credentials.get('url', 'N/A')}")
        print(f"   Project ID: {credentials.get('project_id', 'N/A')}")
        print(f"   Active: {is_active}")
        
        return credentials
        
    except Exception as e:
        print(f"❌ Error retrieving credentials: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_supabase_credentials_for_frontend(user_id: int = 1) -> Dict:
    """
    Get Supabase credentials formatted for frontend use
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with only the credentials safe to send to frontend (no service_key)
    """
    credentials = get_supabase_credentials(user_id)
    
    if not credentials:
        return {
            'success': False,
            'error': 'Credentials not found'
        }
    
    # Return only safe credentials for frontend (exclude service_key)
    return {
        'success': True,
        'credentials': {
            'url': credentials.get('url'),
            'anon_key': credentials.get('anon_key'),
            'project_id': credentials.get('project_id'),
            'region': credentials.get('region')
        }
    }


def get_supabase_credentials_for_backend(user_id: int = 1) -> Dict:
    """
    Get Supabase credentials formatted for backend use (includes service_key)
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with all credentials including service_key
    """
    credentials = get_supabase_credentials(user_id)
    
    if not credentials:
        return {
            'success': False,
            'error': 'Credentials not found'
        }
    
    return {
        'success': True,
        'credentials': credentials
    }


def print_credentials_summary(user_id: int = 1):
    """Print a formatted summary of credentials"""
    print(f"\n{'='*60}")
    print(f"SUPABASE CREDENTIALS SUMMARY")
    print(f"{'='*60}\n")
    
    credentials = get_supabase_credentials(user_id)
    
    if not credentials:
        print("❌ No credentials found")
        return
    
    print(f"✅ Credentials found for user_id={user_id}\n")
    print(f"Project Details:")
    print(f"  URL:        {credentials.get('url', 'N/A')}")
    print(f"  Project ID: {credentials.get('project_id', 'N/A')}")
    print(f"  Region:     {credentials.get('region', 'N/A')}\n")
    
    print(f"Database Connection:")
    print(f"  Host:     {credentials.get('db_host', 'N/A')}")
    print(f"  Port:     {credentials.get('db_port', 'N/A')}")
    print(f"  Database: {credentials.get('db_name', 'N/A')}")
    print(f"  User:     {credentials.get('db_user', 'N/A')}\n")
    
    print(f"API Keys:")
    anon_key = credentials.get('anon_key', '')
    service_key = credentials.get('service_key', '')
    print(f"  Anon Key:    {anon_key[:40]}... (length: {len(anon_key)})")
    print(f"  Service Key: {service_key[:40]}... (length: {len(service_key)})\n")
    
    print(f"{'='*60}\n")


# ==================== CLI USAGE ====================

if __name__ == '__main__':
    """
    CLI Usage:
        python get_supabase_credentials.py              # Get credentials for user_id=1
        python get_supabase_credentials.py 2            # Get credentials for user_id=2
        python get_supabase_credentials.py --json       # Output as JSON
        python get_supabase_credentials.py --summary    # Print formatted summary
    """
    
    import sys
    
    # Parse command line arguments
    user_id = 1
    output_format = 'summary'
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--json':
            output_format = 'json'
        elif arg == '--summary':
            output_format = 'summary'
        elif arg.isdigit():
            user_id = int(arg)
            if len(sys.argv) > 2 and sys.argv[2] == '--json':
                output_format = 'json'
    
    if output_format == 'json':
        # Output as JSON for programmatic use
        result = get_supabase_credentials_for_backend(user_id)
        print(json.dumps(result, indent=2))
    else:
        # Output formatted summary
        print_credentials_summary(user_id)
        
        # Test both frontend and backend functions
        print("\n" + "="*60)
        print("TESTING CREDENTIAL RETRIEVAL FUNCTIONS")
        print("="*60 + "\n")
        
        print("1. Frontend credentials (safe for browser):")
        frontend = get_supabase_credentials_for_frontend(user_id)
        print(json.dumps(frontend, indent=2))
        
        print("\n2. Backend credentials (includes service_key):")
        backend = get_supabase_credentials_for_backend(user_id)
        if backend['success']:
            # Don't print full service_key in logs
            backend_safe = backend.copy()
            if 'credentials' in backend_safe:
                creds = backend_safe['credentials'].copy()
                if 'service_key' in creds:
                    creds['service_key'] = creds['service_key'][:40] + '...'
                backend_safe['credentials'] = creds
            print(json.dumps(backend_safe, indent=2))
        else:
            print(json.dumps(backend, indent=2))
        
        print("\n" + "="*60)
        print("✅ Credential retrieval test complete")
        print("="*60 + "\n")
