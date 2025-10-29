"""
Test Microsoft 365 Authentication and Store Credentials
========================================================

This script tests the Microsoft OAuth flow with the test account:
gerardo@minivetguide.onmicrosoft.com

It will:
1. Initiate OAuth flow via the Flask API
2. Store the resulting tokens in the database
3. Verify the credentials work with Microsoft Graph API
"""

import requests
import webbrowser
import time
import sys
import sqlite3
import json
from datetime import datetime

# Configuration
FLASK_BASE_URL = "http://localhost:5001"
TEST_EMAIL = "gerardo@minivetguide.onmicrosoft.com"
TEST_PASSWORD = "Vetsuccess11!"
DB_PATH = "AI_infrastructure/ai_infrastructure.db"

def check_flask_running():
    """Check if Flask server is running"""
    try:
        response = requests.get(f"{FLASK_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_user_id(email):
    """Get user ID from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        user = cursor.execute(
            "SELECT id, username, email FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        
        if user:
            print(f"✅ Found user: ID {user[0]}, Username: {user[1]}, Email: {user[2]}")
            conn.close()
            return user[0]
        else:
            print(f"⚠️ User not found with email: {email}")
            print(f"   Creating new user...")
            
            # Extract username from email
            username = email.split('@')[0]
            
            # Create user
            cursor.execute(
                "INSERT INTO users (username, email, created_at) VALUES (?, ?, ?)",
                (username, email, datetime.now().isoformat())
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            print(f"✅ Created user: ID {user_id}, Username: {username}, Email: {email}")
            conn.close()
            return user_id
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def check_existing_credentials(user_id):
    """Check if Microsoft credentials already exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        creds = cursor.execute(
            "SELECT credential_key, created_at FROM user_platform_credentials WHERE user_id = ? AND platform = 'microsoft365'",
            (user_id,)
        ).fetchall()
        
        conn.close()
        
        if creds:
            print(f"\n📋 Existing Microsoft credentials found:")
            for cred in creds:
                print(f"   - {cred[0]} (created: {cred[1]})")
            return True
        else:
            print(f"\n⚠️ No existing Microsoft credentials found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False

def initiate_oauth_flow(user_id):
    """Initiate Microsoft OAuth flow"""
    print(f"\n🔐 Initiating Microsoft OAuth flow...")
    print(f"   User ID: {user_id}")
    print(f"   Email: {TEST_EMAIL}")
    
    # Generate auth URL
    auth_url = f"{FLASK_BASE_URL}/api/auth/microsoft/login"
    
    print(f"\n📌 Opening browser to authenticate...")
    print(f"   URL: {auth_url}")
    print(f"\n   ⚠️ MANUAL STEPS REQUIRED:")
    print(f"   1. Browser will open to Microsoft login")
    print(f"   2. Sign in with: {TEST_EMAIL}")
    print(f"   3. Password: {TEST_PASSWORD}")
    print(f"   4. Accept permissions")
    print(f"   5. Wait for redirect to callback")
    print(f"\n   Press ENTER to open browser...")
    
    input()
    
    # Open browser
    webbrowser.open(auth_url)
    
    print(f"\n⏳ Waiting for OAuth callback...")
    print(f"   (This may take 30-60 seconds)")
    print(f"\n   Press ENTER once you see 'Authentication successful' in browser...")
    
    input()
    
    # Check if credentials were stored
    time.sleep(2)
    return check_existing_credentials(user_id)

def test_credentials(user_id):
    """Test if the stored credentials work"""
    print(f"\n🧪 Testing Microsoft credentials...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get access token
        result = cursor.execute(
            "SELECT credential_value FROM user_platform_credentials WHERE user_id = ? AND platform = 'microsoft365' AND credential_key = 'access_token'",
            (user_id,)
        ).fetchone()
        
        conn.close()
        
        if not result:
            print(f"❌ No access token found")
            return False
        
        access_token = result[0]
        print(f"✅ Access token retrieved (length: {len(access_token)})")
        
        # Test with Microsoft Graph API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"\n✅ Microsoft Graph API test successful!")
            print(f"   Display Name: {user_data.get('displayName')}")
            print(f"   Email: {user_data.get('mail') or user_data.get('userPrincipalName')}")
            print(f"   ID: {user_data.get('id')}")
            return True
        else:
            print(f"❌ Microsoft Graph API test failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("MICROSOFT 365 AUTHENTICATION TEST")
    print("=" * 60)
    
    # Check Flask is running
    if not check_flask_running():
        print(f"\n❌ Flask server is not running on {FLASK_BASE_URL}")
        print(f"   Start with: BISTART")
        sys.exit(1)
    
    print(f"✅ Flask server is running")
    
    # Get or create user
    user_id = get_user_id(TEST_EMAIL)
    if not user_id:
        print(f"❌ Failed to get/create user")
        sys.exit(1)
    
    # Check existing credentials
    has_creds = check_existing_credentials(user_id)
    
    if has_creds:
        print(f"\n❓ Credentials already exist. Test them? (y/n): ", end='')
        choice = input().strip().lower()
        if choice == 'y':
            success = test_credentials(user_id)
        else:
            print(f"   Skipping test")
            success = True
    else:
        # Initiate OAuth flow
        success = initiate_oauth_flow(user_id)
        
        if success:
            # Test the new credentials
            test_credentials(user_id)
    
    print(f"\n" + "=" * 60)
    if success:
        print(f"✅ SETUP COMPLETE")
        print(f"\n   Microsoft 365 account is ready for AI agent use!")
        print(f"\n   Test with CHAT command:")
        print(f'   CHAT "List my Outlook emails"')
        print(f'   CHAT "Show my OneDrive files"')
    else:
        print(f"❌ SETUP FAILED")
        print(f"\n   Please try manual authentication:")
        print(f"   1. Open: http://localhost:5001")
        print(f"   2. Go to Settings")
        print(f"   3. Click 'Sign in with Microsoft'")
    print(f"=" * 60)

if __name__ == '__main__':
    main()
