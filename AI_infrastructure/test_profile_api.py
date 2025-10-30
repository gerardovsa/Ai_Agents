import requests
import json

# First, login to get a token
print("🔐 Logging in as Gerardo...")
login_response = requests.post('http://localhost:5001/api/auth/login', json={
    'username': 'Gerardo',
    'password': 'admin123'  # Replace with actual password if different
})

print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    login_data = login_response.json()
    if login_data.get('success'):
        token = login_data.get('token')
        print(f"✅ Got token: {token[:50]}...")
        
        # Now fetch profile
        print("\n📡 Fetching profile...")
        profile_response = requests.get('http://localhost:5001/api/auth/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        
        print(f"Profile status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print("\n=== Profile Response ===")
            print(json.dumps(profile_data, indent=2))
            
            if profile_data.get('success'):
                profile = profile_data.get('profile', {})
                print(f"\n🔑 Auth Platform: {profile.get('auth_platform')}")
                print(f"🔑 Google OAuth Connected: {profile.get('google_oauth_connected')}")
                print(f"🔑 Microsoft OAuth Connected: {profile.get('microsoft_oauth_connected')}")
        else:
            print(f"❌ Error: {profile_response.text}")
    else:
        print(f"❌ Login failed: {login_data.get('error')}")
else:
    print(f"❌ Login request failed: {login_response.text}")
