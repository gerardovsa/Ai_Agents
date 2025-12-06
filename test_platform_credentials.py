"""
Test Platform Credentials Loader
================================

Tests loading credentials from user_platform_credentials table.

Run with: python test_platform_credentials.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from AI_infrastructure.shared.platform_credentials_loader import (
    get_user_credentials,
    get_assemblyai_key,
    get_openai_key,
    get_xero_credentials,
    list_user_platforms,
    has_assemblyai,
    has_openai,
    has_xero
)


def test_user_1():
    """Test credentials for user_id=1"""
    print("\n" + "="*60)
    print("Testing user_id=1")
    print("="*60 + "\n")
    
    user_id = 1
    
    # Test listing platforms
    print("1. List all platforms for user")
    platforms = list_user_platforms(user_id)
    print(f"   Found {len(platforms)} platforms:")
    for platform in platforms:
        print(f"   - {platform}")
    
    # Test Xero Print
    print("\n2. Test Xero Print credentials")
    xero_creds = get_xero_credentials(user_id, 'print')
    if xero_creds:
        print(f"   ✅ Xero Print credentials loaded")
        print(f"   Client ID: {xero_creds['client_id'][:20]}...")
        print(f"   Client Secret: {xero_creds['client_secret'][:20]}...")
        print(f"   Base URL: {xero_creds['base_url']}")
        print(f"   Business: {xero_creds['business']}")
    else:
        print(f"   ❌ No Xero Print credentials found")
    
    # Test AssemblyAI
    print("\n3. Test AssemblyAI credentials")
    if has_assemblyai(user_id):
        api_key = get_assemblyai_key(user_id)
        print(f"   ✅ AssemblyAI API key: {api_key[:20]}...")
    else:
        print(f"   ❌ No AssemblyAI credentials found")
    
    # Test OpenAI
    print("\n4. Test OpenAI credentials")
    if has_openai(user_id):
        api_key = get_openai_key(user_id)
        print(f"   ✅ OpenAI API key: {api_key[:20]}...")
    else:
        print(f"   ❌ No OpenAI credentials found")
    
    # Test raw credential fetching
    print("\n5. Test raw credential fetching (Xero Print)")
    raw_creds = get_user_credentials(user_id, 'xero_print')
    if raw_creds:
        print(f"   ✅ Raw credentials loaded:")
        print(f"   Platform: {raw_creds['platform']}")
        print(f"   Credential Type: {raw_creds['credential_type']}")
        print(f"   Credential Key: {raw_creds['credential_key']}")
        print(f"   Credential Value: {raw_creds['credential_value'][:20]}...")
        if 'credentials' in raw_creds:
            print(f"   Credentials JSON: {list(raw_creds['credentials'].keys())}")
        if 'metadata' in raw_creds:
            print(f"   Metadata JSON: {list(raw_creds['metadata'].keys())}")
    else:
        print(f"   ❌ Could not load raw credentials")
    
    print("\n" + "="*60 + "\n")


def test_tool_integration():
    """Test tool integration with credentials"""
    print("\n" + "="*60)
    print("Testing Tool Integration")
    print("="*60 + "\n")
    
    user_id = 1
    
    # Test AssemblyAI tool
    print("1. Test AssemblyAI tool integration")
    try:
        from tools.implementations.assemblyai import _get_assemblyai_client
        client = _get_assemblyai_client(user_id)
        if client:
            print(f"   ✅ AssemblyAI client initialized")
        else:
            print(f"   ⚠️  AssemblyAI client not available")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test OpenAI tool
    print("\n2. Test OpenAI client integration")
    try:
        from tools.implementations.veterinary_soap_notes import _get_openai_client
        client = _get_openai_client(user_id)
        if client:
            print(f"   ✅ OpenAI client initialized")
        else:
            print(f"   ⚠️  OpenAI client not available")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " PLATFORM CREDENTIALS LOADER TEST ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    test_user_1()
    test_tool_integration()
    
    print("╔" + "="*58 + "╗")
    print("║" + " TEST COMPLETE ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    print("\n")


if __name__ == '__main__':
    main()
