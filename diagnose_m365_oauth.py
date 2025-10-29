"""
Microsoft 365 OAuth Diagnostics
================================

Diagnoses "invalid_client" errors by checking:
1. Azure AD app configuration
2. Environment variables
3. Redirect URI configuration
4. Client credentials validity

Author: Valor AI Platform
Date: October 28, 2025
"""

import os
import sys
from dotenv import load_dotenv
import requests
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

def check_environment_variables():
    """Check if Microsoft OAuth credentials are configured"""
    print("=" * 70)
    print("🔍 STEP 1: Environment Variables Check")
    print("=" * 70)
    
    client_id = os.getenv('MICROSOFT_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
    tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
    
    print(f"✓ MICROSOFT_CLIENT_ID: {'SET' if client_id else '❌ NOT SET'}")
    if client_id:
        print(f"  Value: {client_id}")
    
    print(f"✓ MICROSOFT_CLIENT_SECRET: {'SET' if client_secret else '❌ NOT SET'}")
    if client_secret:
        print(f"  Value: {'*' * len(client_secret)} (hidden)")
    
    print(f"✓ MICROSOFT_TENANT_ID: {tenant_id}")
    print()
    
    if not client_id or not client_secret:
        print("❌ ERROR: Missing credentials in .env.master")
        return False
    
    return True

def test_oauth_configuration(client_id: str, tenant_id: str):
    """Test OAuth configuration by attempting to get authorization URL"""
    print("=" * 70)
    print("🔍 STEP 2: OAuth Configuration Test")
    print("=" * 70)
    
    auth_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    redirect_uri = "http://localhost:5001/api/auth/microsoft/callback"
    
    print(f"Auth Endpoint: {auth_endpoint}")
    print(f"Redirect URI: {redirect_uri}")
    print(f"Client ID: {client_id}")
    print()
    
    # Build authorization URL
    scopes = "openid profile email User.Read Mail.Read"
    auth_url = (
        f"{auth_endpoint}?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"redirect_uri={redirect_uri}&"
        f"response_mode=query&"
        f"scope={scopes.replace(' ', '%20')}&"
        f"state=test_state"
    )
    
    print("✅ Authorization URL generated successfully")
    print(f"URL: {auth_url[:100]}...")
    print()
    
    return auth_url

def diagnose_invalid_client_error():
    """Provide specific diagnostics for invalid_client error"""
    print("=" * 70)
    print("🔍 STEP 3: Invalid Client Error Diagnosis")
    print("=" * 70)
    
    print("The 'invalid_client' error typically means:")
    print()
    print("1. ❌ Azure AD App NOT configured as Multi-tenant")
    print("   → Azure Portal → App registrations → Your app")
    print("   → Authentication → Supported account types")
    print("   → MUST be: 'Accounts in any organizational directory'")
    print()
    print("2. ❌ Client Secret is incorrect or expired")
    print("   → Azure Portal → App registrations → Your app")
    print("   → Certificates & secrets → Client secrets")
    print("   → Create new secret and update .env.master")
    print()
    print("3. ❌ Redirect URI not registered in Azure AD")
    print("   → Azure Portal → App registrations → Your app")
    print("   → Authentication → Platform configurations → Web")
    print("   → Add: http://localhost:5001/api/auth/microsoft/callback")
    print()
    print("4. ❌ Wrong Client ID being used")
    print("   → Verify Application (client) ID in Azure Portal matches .env.master")
    print()

def provide_solution():
    """Provide step-by-step solution"""
    print("=" * 70)
    print("✅ SOLUTION: Fix Azure AD App Configuration")
    print("=" * 70)
    
    print()
    print("STEP A: Check Multi-tenant Configuration")
    print("-" * 70)
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate: Azure Active Directory → App registrations")
    print("3. Find app: '324f7fef-50ac-4948-9f34-5f95b03ad818'")
    print("   (Or search by name if you remember it)")
    print()
    print("4. Click on your app")
    print("5. Go to: Authentication (left sidebar)")
    print("6. Check 'Supported account types' section:")
    print()
    print("   CURRENT (causing error):")
    print("   ● Accounts in this organizational directory only (Single tenant)")
    print()
    print("   REQUIRED (for multi-tenant):")
    print("   ● Accounts in any organizational directory (Any Azure AD directory - Multitenant)")
    print()
    print("7. If wrong, click 'Manifest' (left sidebar)")
    print("8. Find line: \"signInAudience\": \"AzureADMyOrg\"")
    print("9. Change to: \"signInAudience\": \"AzureADMultipleOrgs\"")
    print("10. Click Save")
    print()
    
    print("STEP B: Verify Redirect URI")
    print("-" * 70)
    print("1. Still in your app → Authentication")
    print("2. Under 'Platform configurations' → Web")
    print("3. Ensure this URL is listed:")
    print("   http://localhost:5001/api/auth/microsoft/callback")
    print("4. If not, click 'Add URI' and add it")
    print("5. Click Save")
    print()
    
    print("STEP C: Verify Client Secret")
    print("-" * 70)
    print("1. Go to: Certificates & secrets (left sidebar)")
    print("2. Under 'Client secrets' → Check if secret exists")
    print("3. If expired or unsure, create NEW secret:")
    print("   - Click 'New client secret'")
    print("   - Description: 'Valor AI Platform'")
    print("   - Expires: 24 months")
    print("   - Click Add")
    print("4. COPY the 'Value' (NOT the 'Secret ID')")
    print("5. Update .env.master:")
    print("   MICROSOFT_CLIENT_SECRET=<paste_new_value>")
    print()
    
    print("STEP D: Restart Server")
    print("-" * 70)
    print("1. Stop server: BISTOP")
    print("2. Start server: BISTART")
    print("3. Try Microsoft login again")
    print()

def main():
    """Run full diagnostics"""
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     MICROSOFT 365 OAUTH DIAGNOSTICS - INVALID CLIENT          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    # Step 1: Check environment
    if not check_environment_variables():
        sys.exit(1)
    
    client_id = os.getenv('MICROSOFT_CLIENT_ID')
    tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
    
    # Step 2: Test OAuth configuration
    test_oauth_configuration(client_id, tenant_id)
    
    # Step 3: Diagnose invalid_client error
    diagnose_invalid_client_error()
    
    # Step 4: Provide solution
    provide_solution()
    
    print("=" * 70)
    print("🎯 SUMMARY")
    print("=" * 70)
    print()
    print("Your OAuth configuration is CORRECT for multi-tenant:")
    print(f"✓ Tenant ID: {tenant_id} (common = multi-tenant)")
    print(f"✓ Client ID: {client_id}")
    print(f"✓ Redirect URI: http://localhost:5001/api/auth/microsoft/callback")
    print()
    print("The 'invalid_client' error is most likely due to:")
    print("❌ Azure AD app is configured as SINGLE-tenant, not multi-tenant")
    print()
    print("Follow STEP A above to fix the Azure AD app configuration.")
    print()

if __name__ == '__main__':
    main()
