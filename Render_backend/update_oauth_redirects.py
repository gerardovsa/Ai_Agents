#!/usr/bin/env python3
"""
Update OAuth Redirects - Update OAuth redirect URLs for production

This script helps update OAuth redirect URLs in Microsoft Azure and Google Cloud
Console after deploying to Render.
"""

import os
import sys
from pathlib import Path

def print_microsoft_instructions(service_url):
    """Print instructions for updating Microsoft OAuth"""
    print("\n" + "=" * 70)
    print("🔵 Microsoft Azure AD - Update Redirect URIs")
    print("=" * 70)
    
    redirect_uri = f"{service_url}/api/auth/microsoft/callback"
    
    print(f"\n1️⃣  Open Azure Portal:")
    print("   https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps")
    
    print(f"\n2️⃣  Find your application:")
    print("   - Look for 'AI Agents Backend' or your app name")
    print("   - Click on the application")
    
    print(f"\n3️⃣  Add redirect URI:")
    print("   - Click 'Authentication' in left sidebar")
    print("   - Under 'Platform configurations' → 'Web'")
    print("   - Click 'Add URI'")
    print(f"   - Add: {redirect_uri}")
    print("   - Click 'Save'")
    
    print(f"\n4️⃣  Verify configuration:")
    print("   - Check 'ID tokens' is enabled")
    print("   - Check 'Access tokens' is enabled")
    print("   - Supported account types: 'Accounts in any organizational directory'")
    
    print(f"\n Microsoft redirect URI to add:")
    print(f"   {redirect_uri}")

def print_google_instructions(service_url):
    """Print instructions for updating Google OAuth"""
    print("\n" + "=" * 70)
    print("🔴 Google Cloud Console - Update Authorized Redirect URIs")
    print("=" * 70)
    
    redirect_uri = f"{service_url}/api/auth/google/callback"
    
    print(f"\n1️⃣  Open Google Cloud Console:")
    print("   https://console.cloud.google.com/apis/credentials")
    
    print(f"\n2️⃣  Select your project:")
    print("   - Click project dropdown at top")
    print("   - Select your AI Agents project")
    
    print(f"\n3️⃣  Find OAuth 2.0 Client:")
    print("   - Look for 'OAuth 2.0 Client IDs' section")
    print("   - Click on your client (e.g., 'AI Agents OAuth Client')")
    
    print(f"\n4️⃣  Add redirect URI:")
    print("   - Scroll to 'Authorized redirect URIs'")
    print("   - Click '+ ADD URI'")
    print(f"   - Add: {redirect_uri}")
    print("   - Click 'SAVE'")
    
    print(f"\n5️⃣  Verify configuration:")
    print("   - Check authorized JavaScript origins include your domain")
    print("   - Ensure OAuth consent screen is configured")
    
    print(f"\n Google redirect URI to add:")
    print(f"   {redirect_uri}")

def print_testing_instructions(service_url):
    """Print instructions for testing OAuth flows"""
    print("\n" + "=" * 70)
    print("🧪 Test OAuth Flows")
    print("=" * 70)
    
    print(f"\n1️⃣  Test Microsoft OAuth:")
    print(f"   curl -X GET {service_url}/api/auth/microsoft/login")
    print("   - Should redirect to Microsoft login")
    print("   - After login, should redirect to callback URL")
    print("   - Check for successful token exchange")
    
    print(f"\n2️⃣  Test Google OAuth:")
    print(f"   curl -X GET {service_url}/api/auth/google/login")
    print("   - Should redirect to Google login")
    print("   - After login, should redirect to callback URL")
    print("   - Check for successful token exchange")
    
    print(f"\n3️⃣  Verify in browser:")
    print(f"   - Open {service_url} in browser")
    print("   - Click 'Connect Microsoft Account' button")
    print("   - Complete OAuth flow")
    print("   - Check browser console for errors")
    
    print(f"\n4️⃣  Check database:")
    print("   - Verify user_platform_credentials table has entries")
    print("   - Check access_token and refresh_token are stored")

def print_environment_variables(service_url):
    """Print environment variables that might need updating"""
    print("\n" + "=" * 70)
    print("⚙️  Environment Variables to Verify")
    print("=" * 70)
    
    print("\n📋 Check these environment variables are set in Render:")
    
    vars_to_check = [
        ("MICROSOFT_CLIENT_ID", "Your Azure AD application ID"),
        ("MICROSOFT_CLIENT_SECRET", "Your Azure AD client secret"),
        ("MICROSOFT_TENANT_ID", "Usually 'common' for multi-tenant"),
        ("MICROSOFT_REDIRECT_URI", f"{service_url}/api/auth/microsoft/callback"),
        ("GOOGLE_CLIENT_ID", "Your Google OAuth client ID"),
        ("GOOGLE_CLIENT_SECRET", "Your Google OAuth client secret"),
        ("GOOGLE_REDIRECT_URI", f"{service_url}/api/auth/google/callback"),
    ]
    
    for var_name, description in vars_to_check:
        print(f"\n   {var_name}")
        print(f"   Description: {description}")
    
    print("\n💡 To update environment variables:")
    print("   1. Dashboard: https://dashboard.render.com/web/YOUR_SERVICE_ID")
    print("   2. Click 'Environment' tab")
    print("   3. Update values")
    print("   4. Click 'Save Changes' (will trigger redeploy)")

def main():
    print("=" * 70)
    print("🔗 Update OAuth Redirect URLs")
    print("=" * 70)
    
    # Get service URL from command line or use default
    if len(sys.argv) > 1:
        service_url = sys.argv[1]
    else:
        service_url = "https://ai-agents-backend-2oi8.onrender.com"
    
    print(f"\n🌐 Service URL: {service_url}")
    
    # Print instructions for each platform
    print_microsoft_instructions(service_url)
    print_google_instructions(service_url)
    print_environment_variables(service_url)
    print_testing_instructions(service_url)
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 Quick Summary")
    print("=" * 70)
    
    print("\n Redirect URIs to add:")
    print(f"   Microsoft: {service_url}/api/auth/microsoft/callback")
    print(f"   Google: {service_url}/api/auth/google/callback")
    
    print("\n🔗 Console Links:")
    print("   Microsoft: https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps")
    print("   Google: https://console.cloud.google.com/apis/credentials")
    
    print("\n📋 After updating, test OAuth flows:")
    print(f"   python Render_backend/test_deployment.py {service_url}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
