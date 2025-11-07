"""
Analyze Microsoft Authentication Status
========================================
Check all Microsoft tokens and authentication pathways
"""

import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def analyze_microsoft_tokens():
    """Analyze all Microsoft OAuth tokens"""
    print("\n" + "="*70)
    print("MICROSOFT AUTHENTICATION ANALYSIS")
    print("="*70)
    
    db_path = Path(__file__).parent.parent.parent / "data" / "ai_infrastructure.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check oauth_tokens table
    print("\n📊 OAuth Tokens Table:")
    cursor.execute("""
        SELECT 
            id,
            user_id,
            platform,
            account_identifier,
            account_name,
            expires_at,
            is_active,
            is_valid,
            created_at,
            updated_at,
            scope
        FROM oauth_tokens
        WHERE platform IN ('microsoft', 'microsoft365')
        ORDER BY updated_at DESC
    """)
    
    microsoft_tokens = cursor.fetchall()
    
    if not microsoft_tokens:
        print("   ⚠️  No Microsoft tokens found in oauth_tokens")
    else:
        print(f"   ✅ Found {len(microsoft_tokens)} Microsoft token(s)\n")
        
        for token in microsoft_tokens:
            print(f"   Token ID: {token['id']}")
            print(f"   User ID: {token['user_id']}")
            print(f"   Platform: {token['platform']} {'⚠️ OLD NAME' if token['platform'] == 'microsoft365' else '✅'}")
            print(f"   Account: {token['account_identifier'] or 'N/A'}")
            print(f"   Name: {token['account_name'] or 'N/A'}")
            print(f"   Expires: {token['expires_at'] or 'No expiry tracked'}")
            print(f"   Active: {token['is_active']}")
            print(f"   Valid: {token['is_valid']}")
            print(f"   Scopes: {token['scope'][:50] if token['scope'] else 'N/A'}...")
            print(f"   Created: {token['created_at']}")
            print(f"   Updated: {token['updated_at']}")
            print()
    
    # Check user_platform_credentials table (old)
    print("\n📊 User Platform Credentials Table (Legacy):")
    cursor.execute("""
        SELECT 
            id,
            user_id,
            platform,
            credential_key,
            is_active,
            created_at
        FROM user_platform_credentials
        WHERE platform IN ('microsoft', 'microsoft365', 'ms365')
        ORDER BY created_at DESC
    """)
    
    old_creds = cursor.fetchall()
    
    if not old_creds:
        print("   ✅ No Microsoft credentials in legacy table")
    else:
        print(f"   ⚠️  Found {len(old_creds)} legacy Microsoft credential(s)")
        for cred in old_creds:
            print(f"   - ID {cred['id']}: user {cred['user_id']}, platform='{cred['platform']}', key='{cred['credential_key']}'")
    
    # Check users table
    print("\n📊 Users Table - Microsoft OAuth Status:")
    cursor.execute("""
        SELECT 
            id,
            username,
            email,
            has_microsoft_oauth,
            is_active
        FROM users
        ORDER BY id
    """)
    
    users = cursor.fetchall()
    
    for user in users:
        ms_oauth = "✅ YES" if user['has_microsoft_oauth'] else "❌ NO"
        active = "✅" if user['is_active'] else "❌"
        print(f"   User {user['id']}: {user['username']} ({user['email']}) - Microsoft: {ms_oauth}, Active: {active}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


def check_microsoft_tool_implementations():
    """Check Microsoft tool implementations"""
    print("\n" + "="*70)
    print("MICROSOFT TOOL IMPLEMENTATIONS")
    print("="*70)
    
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        # Get all Microsoft tools
        microsoft_tools = [
            name for name in registry.tools.keys() 
            if any(keyword in name.lower() for keyword in ['microsoft', 'outlook', 'onedrive', 'teams', 'onenote', 'sharepoint', 'excel', 'word'])
        ]
        
        print(f"\n✅ Found {len(microsoft_tools)} Microsoft tools in registry")
        
        # Group by category
        categories = {
            'outlook': [],
            'onedrive': [],
            'teams': [],
            'calendar': [],
            'excel': [],
            'word': [],
            'onenote': [],
            'sharepoint': [],
            'forms': [],
            'todo': []
        }
        
        for tool in microsoft_tools:
            for category in categories.keys():
                if category in tool.lower():
                    categories[category].append(tool)
                    break
        
        print("\n📋 Tools by Category:")
        for category, tools in categories.items():
            if tools:
                print(f"\n   {category.upper()}: {len(tools)} tools")
                for tool in tools[:3]:  # Show first 3
                    print(f"      - {tool}")
                if len(tools) > 3:
                    print(f"      ... and {len(tools) - 3} more")
        
    except Exception as e:
        print(f"   ⚠️  Error loading tool registry: {e}")


def check_microsoft_routes():
    """Check Microsoft OAuth routes"""
    print("\n" + "="*70)
    print("MICROSOFT OAUTH ROUTES")
    print("="*70)
    
    routes_file = Path(__file__).parent.parent.parent / "AI_infrastructure" / "routes" / "microsoft_auth_routes_V2_FIXED.py"
    
    if routes_file.exists():
        print(f"   ✅ Microsoft OAuth routes file exists")
        print(f"   📄 {routes_file}")
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key functions
        checks = [
            ('microsoft_authorize', 'OAuth initiation'),
            ('microsoft_callback', 'OAuth callback'),
            ('oauth_tokens', 'Uses oauth_tokens table'),
            ("platform = 'microsoft'", 'Standardized platform name'),
        ]
        
        print("\n   📋 Route Checks:")
        for check, desc in checks:
            if check in content:
                print(f"      ✅ {desc}: {check}")
            else:
                print(f"      ❌ {desc}: {check} NOT FOUND")
    else:
        print(f"   ❌ Microsoft OAuth routes file NOT FOUND")
        print(f"   Expected: {routes_file}")


if __name__ == "__main__":
    analyze_microsoft_tokens()
    check_microsoft_tool_implementations()
    check_microsoft_routes()
