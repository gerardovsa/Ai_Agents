"""
Check OAuth Status for Communication Hub
=========================================

Quick diagnostic script to check if a user has valid OAuth credentials
for Gmail and/or Outlook.

Usage:
    python check_oauth_status.py [user_id]
    
Example:
    python check_oauth_status.py 12
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from auth.user_auth import UserAuthManager


def check_oauth_status(user_id=None):
    """Check OAuth status for a user"""
    
    # Default to user_id=12 if not provided
    if user_id is None:
        user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    
    print(f"\n{'='*60}")
    print(f"OAuth Status Check for User ID: {user_id}")
    print(f"{'='*60}\n")
    
    auth_manager = UserAuthManager()
    
    # Check Google OAuth
    print("🔍 Checking Google OAuth...")
    try:
        google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
        if google_creds:
            print("✅ Google OAuth: CONNECTED")
            print(f"   Email: {google_creds.get('email', google_creds.get('client_id', 'N/A'))}")
            print(f"   Token Type: {google_creds.get('token_type', 'N/A')}")
            if 'expires_in' in google_creds:
                print(f"   Expires In: {google_creds['expires_in']} seconds")
        else:
            print("❌ Google OAuth: NOT CONNECTED")
            print("   Action: Navigate to OAuth page and connect Gmail account")
    except Exception as e:
        print(f"❌ Google OAuth: ERROR - {str(e)}")
    
    print()
    
    # Check Microsoft OAuth
    print("🔍 Checking Microsoft OAuth...")
    try:
        microsoft_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
        if microsoft_creds:
            print("✅ Microsoft OAuth: CONNECTED")
            print(f"   Email: {microsoft_creds.get('email', microsoft_creds.get('microsoft_email', 'N/A'))}")
            print(f"   Token Type: {microsoft_creds.get('token_type', 'N/A')}")
            if 'expires_in' in microsoft_creds:
                print(f"   Expires In: {microsoft_creds['expires_in']} seconds")
        else:
            print("❌ Microsoft OAuth: NOT CONNECTED")
            print("   Action: Navigate to OAuth page and connect Outlook account")
    except Exception as e:
        print(f"❌ Microsoft OAuth: ERROR - {str(e)}")
    
    print(f"\n{'='*60}")
    
    # Summary
    has_google = google_creds is not None if 'google_creds' in locals() else False
    has_microsoft = microsoft_creds is not None if 'microsoft_creds' in locals() else False
    
    if has_google or has_microsoft:
        print("✅ Status: User can access Communication Hub")
        connected_accounts = []
        if has_google:
            connected_accounts.append("Gmail")
        if has_microsoft:
            connected_accounts.append("Outlook")
        print(f"   Connected: {', '.join(connected_accounts)}")
    else:
        print("⚠️  Status: No email accounts connected")
        print("   Action: Connect at least one account to use Communication Hub")
    
    print(f"{'='*60}\n")


if __name__ == '__main__':
    try:
        check_oauth_status()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
