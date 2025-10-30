#!/usr/bin/env python3
"""Test the /api/auth/profile endpoint to verify OAuth status is returned correctly"""

import requests
import json

print("="*80)
print("TESTING /api/auth/profile ENDPOINT - OAUTH STATUS CHECK")
print("="*80)

# Step 1: Login using dev mode (GET request for localhost auto-login)
print("\n[Step 1] Logging in via dev mode (localhost auto-login)...")
login_response = requests.get('http://localhost:5001/api/auth/login')

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    exit(1)

login_data = login_response.json()
if not login_data.get('success'):
    print(f"❌ Login unsuccessful: {login_data}")
    exit(1)

token = login_data.get('token')
print(f"✅ Login successful! Token: {token[:30]}...")

# Step 2: Get profile with OAuth status
print("\n[Step 2] Fetching user profile...")
headers = {'Authorization': f'Bearer {token}'}
profile_response = requests.get('http://localhost:5001/api/auth/profile', headers=headers)

if profile_response.status_code != 200:
    print(f"❌ Profile fetch failed: {profile_response.status_code}")
    print(f"Response: {profile_response.text}")
    exit(1)

profile_data = profile_response.json()
if not profile_data.get('success'):
    print(f"❌ Profile fetch unsuccessful: {profile_data}")
    exit(1)

print("✅ Profile fetched successfully!")

# Step 3: Check OAuth status in profile
print("\n" + "="*80)
print("PROFILE DATA:")
print("="*80)

profile = profile_data.get('profile', {})
print(f"Username: {profile.get('username')}")
print(f"Email: {profile.get('email')}")
print(f"Role: {profile.get('role')}")
print(f"Auth Platform: {profile.get('auth_platform')}")
print(f"\n🔑 OAUTH STATUS:")
print(f"   Google OAuth Connected: {profile.get('google_oauth_connected')}")
print(f"   Microsoft OAuth Connected: {profile.get('microsoft_oauth_connected')}")

# Step 4: Verify expected behavior
print("\n" + "="*80)
print("VERIFICATION:")
print("="*80)

google_connected = profile.get('google_oauth_connected')
if google_connected is True:
    print("✅ PASS: Google OAuth status shows as True (connected)")
    print("   Frontend UI should show '✅ Connected' for Google Workspace OAuth")
elif google_connected is False:
    print("❌ FAIL: Google OAuth status shows as False despite credentials existing")
    print("   This means the bug is NOT fixed yet!")
else:
    print(f"❌ FAIL: Google OAuth status is missing or invalid: {google_connected}")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
if google_connected is True:
    print("✅ OAuth detection is WORKING correctly!")
    print("   The frontend should now show Google Workspace as connected.")
    print("   Refresh your browser to see the updated status.")
else:
    print("❌ OAuth detection is STILL BROKEN!")
    print("   Need to investigate further...")
