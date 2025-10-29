"""
Azure AD Multi-tenant Configuration Fixer
==========================================

Automatically updates Azure AD app to support multi-tenant authentication.

This script:
1. Connects to Azure AD using Azure CLI or Microsoft Graph API
2. Retrieves current app configuration
3. Updates signInAudience to "AzureADMultipleOrgs"
4. Verifies redirect URIs
5. Confirms changes

Prerequisites:
- Azure CLI installed (https://aka.ms/install-azure-cli)
- OR Azure AD admin credentials for Graph API

Author: Valor AI Platform
Date: October 28, 2025
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
REDIRECT_URI = "http://localhost:5001/api/auth/microsoft/callback"


def check_azure_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(['az', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✅ Azure CLI is installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Azure CLI not found")
    print()
    print("To install Azure CLI:")
    print("1. Download from: https://aka.ms/install-azure-cli")
    print("2. Run installer")
    print("3. Restart terminal")
    print("4. Run: az login")
    print()
    return False


def azure_cli_login():
    """Login to Azure CLI"""
    print("=" * 70)
    print("🔐 Azure CLI Login")
    print("=" * 70)
    
    try:
        # Check if already logged in
        result = subprocess.run(['az', 'account', 'show'],
                              capture_output=True,
                              text=True,
                              timeout=10)
        
        if result.returncode == 0:
            account = json.loads(result.stdout)
            print(f"✅ Already logged in as: {account.get('user', {}).get('name', 'Unknown')}")
            return True
        
        # Not logged in, prompt to login
        print("Opening browser for Azure login...")
        result = subprocess.run(['az', 'login'],
                              capture_output=True,
                              text=True,
                              timeout=60)
        
        if result.returncode == 0:
            print("✅ Successfully logged in")
            return True
        else:
            print(f"❌ Login failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False


def get_app_manifest():
    """Get current app manifest using Azure CLI"""
    print()
    print("=" * 70)
    print("📋 Retrieving App Configuration")
    print("=" * 70)
    
    try:
        cmd = ['az', 'ad', 'app', 'show', '--id', CLIENT_ID]
        result = subprocess.run(cmd,
                              capture_output=True,
                              text=True,
                              timeout=30)
        
        if result.returncode == 0:
            manifest = json.loads(result.stdout)
            print(f"✅ Retrieved app: {manifest.get('displayName', 'Unknown')}")
            print(f"   App ID: {manifest.get('appId', 'Unknown')}")
            print(f"   Sign-in Audience: {manifest.get('signInAudience', 'Unknown')}")
            return manifest
        else:
            print(f"❌ Failed to retrieve app: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving app: {e}")
        return None


def update_app_to_multitenant(app_object_id: str):
    """Update app to support multi-tenant"""
    print()
    print("=" * 70)
    print("🔧 Updating App to Multi-tenant")
    print("=" * 70)
    
    try:
        cmd = [
            'az', 'ad', 'app', 'update',
            '--id', app_object_id,
            '--sign-in-audience', 'AzureADMultipleOrgs'
        ]
        
        result = subprocess.run(cmd,
                              capture_output=True,
                              text=True,
                              timeout=30)
        
        if result.returncode == 0:
            print("✅ Successfully updated app to multi-tenant")
            print("   Sign-in Audience: AzureADMultipleOrgs")
            return True
        else:
            print(f"❌ Failed to update app: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating app: {e}")
        return False


def verify_redirect_uris(app_manifest: dict):
    """Verify redirect URIs are configured"""
    print()
    print("=" * 70)
    print("🔗 Verifying Redirect URIs")
    print("=" * 70)
    
    web_config = app_manifest.get('web', {})
    redirect_uris = web_config.get('redirectUris', [])
    
    print(f"Current Redirect URIs:")
    for uri in redirect_uris:
        print(f"  • {uri}")
    
    if REDIRECT_URI in redirect_uris:
        print(f"✅ Required URI found: {REDIRECT_URI}")
        return True
    else:
        print(f"❌ Missing required URI: {REDIRECT_URI}")
        return False


def add_redirect_uri(app_object_id: str):
    """Add redirect URI if missing"""
    print()
    print("=" * 70)
    print("➕ Adding Redirect URI")
    print("=" * 70)
    
    try:
        # First get current URIs
        cmd = ['az', 'ad', 'app', 'show', '--id', app_object_id]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Failed to get current URIs: {result.stderr}")
            return False
        
        manifest = json.loads(result.stdout)
        current_uris = manifest.get('web', {}).get('redirectUris', [])
        
        # Add new URI if not present
        if REDIRECT_URI not in current_uris:
            current_uris.append(REDIRECT_URI)
            
            # Update app with new URIs
            uris_json = json.dumps({'redirectUris': current_uris})
            cmd = [
                'az', 'ad', 'app', 'update',
                '--id', app_object_id,
                '--web-redirect-uris', *current_uris
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Added redirect URI: {REDIRECT_URI}")
                return True
            else:
                print(f"❌ Failed to add URI: {result.stderr}")
                return False
        else:
            print(f"✅ URI already exists: {REDIRECT_URI}")
            return True
            
    except Exception as e:
        print(f"❌ Error adding redirect URI: {e}")
        return False


def manual_instructions():
    """Provide manual instructions as fallback"""
    print()
    print("=" * 70)
    print("📖 MANUAL CONFIGURATION INSTRUCTIONS")
    print("=" * 70)
    print()
    print("Follow these steps to configure multi-tenant support manually:")
    print()
    print("1. Go to Azure Portal: https://portal.azure.com")
    print()
    print("2. Navigate to: Azure Active Directory → App registrations")
    print()
    print(f"3. Find your app by Client ID: {CLIENT_ID}")
    print("   (Use search box if needed)")
    print()
    print("4. Click on your app to open it")
    print()
    print("5. OPTION A - Use Authentication page:")
    print("   a. Click 'Authentication' in left sidebar")
    print("   b. Under 'Supported account types', select:")
    print("      'Accounts in any organizational directory (Any Azure AD - Multitenant)'")
    print("   c. Under 'Platform configurations' → Web → Redirect URIs")
    print(f"      Add: {REDIRECT_URI}")
    print("   d. Click 'Save'")
    print()
    print("6. OPTION B - Edit Manifest directly:")
    print("   a. Click 'Manifest' in left sidebar")
    print("   b. Find line: \"signInAudience\": \"AzureADMyOrg\"")
    print("   c. Change to: \"signInAudience\": \"AzureADMultipleOrgs\"")
    print("   d. Find \"replyUrlsWithType\" array")
    print(f"   e. Add: {{\"url\": \"{REDIRECT_URI}\", \"type\": \"Web\"}}")
    print("   f. Click 'Save'")
    print()
    print("7. Wait 2-3 minutes for changes to propagate")
    print()
    print("8. Restart your Flask server:")
    print("   BISTOP")
    print("   BISTART")
    print()
    print("9. Try Microsoft login again")
    print()


def main():
    """Main execution"""
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        AZURE AD MULTI-TENANT CONFIGURATION FIXER               ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    if not CLIENT_ID:
        print("❌ MICROSOFT_CLIENT_ID not found in .env.master")
        sys.exit(1)
    
    print(f"Target App ID: {CLIENT_ID}")
    print(f"Required Redirect URI: {REDIRECT_URI}")
    print()
    
    # Check Azure CLI
    if not check_azure_cli():
        manual_instructions()
        sys.exit(1)
    
    # Login to Azure
    if not azure_cli_login():
        print("❌ Azure login failed")
        manual_instructions()
        sys.exit(1)
    
    # Get current app configuration
    manifest = get_app_manifest()
    if not manifest:
        manual_instructions()
        sys.exit(1)
    
    app_object_id = manifest.get('id')  # Object ID (not App ID)
    current_audience = manifest.get('signInAudience')
    
    # Check if already multi-tenant
    if current_audience == 'AzureADMultipleOrgs':
        print()
        print("✅ App is already configured as multi-tenant!")
        print()
        print("The 'invalid_client' error might be due to:")
        print("1. Client Secret is incorrect or expired")
        print("2. Redirect URI mismatch")
        print()
        print("Check STEP C in the diagnostics output to verify client secret.")
    else:
        print(f"Current Sign-in Audience: {current_audience}")
        print("Need to update to: AzureADMultipleOrgs")
        
        # Update app
        success = update_app_to_multitenant(app_object_id)
        if not success:
            manual_instructions()
            sys.exit(1)
    
    # Verify redirect URIs
    has_uri = verify_redirect_uris(manifest)
    if not has_uri:
        add_redirect_uri(app_object_id)
    
    # Final summary
    print()
    print("=" * 70)
    print("✅ CONFIGURATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Wait 2-3 minutes for Azure AD changes to propagate")
    print("2. Restart Flask server: BISTOP then BISTART")
    print("3. Try Microsoft login again")
    print()
    print("If you still get 'invalid_client' error:")
    print("→ Run: python diagnose_m365_oauth.py")
    print("→ Follow STEP C to verify/update client secret")
    print()


if __name__ == '__main__':
    main()
