"""
Test CORS with Streamlit Render URL as Origin
"""

import requests

FLASK_URL = "https://inhouseprint-flask.onrender.com"
STREAMLIT_URL = "https://inhouseprint-streamlit.onrender.com"

print("=" * 80)
print("TESTING CORS WITH RENDER STREAMLIT ORIGIN")
print("=" * 80)

# Test with Streamlit Render URL as origin
headers = {
    'Origin': STREAMLIT_URL,
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'Content-Type'
}

print(f"\n🔍 Testing CORS with Origin: {STREAMLIT_URL}")
print(f"   Target: {FLASK_URL}/api/stock/master")

try:
    # First, OPTIONS preflight request
    print("\n1️⃣ OPTIONS Preflight Request:")
    response = requests.options(f"{FLASK_URL}/api/stock/master", headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"      {key}: {value}")
    
    # Then, actual GET request
    print("\n2️⃣ GET Request with Origin Header:")
    response = requests.get(f"{FLASK_URL}/api/stock/master", headers={'Origin': STREAMLIT_URL}, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"      {key}: {value}")
    
    # Check if Streamlit origin is allowed
    allow_origin = response.headers.get('access-control-allow-origin', 'NOT SET')
    print(f"\n📊 RESULT:")
    if allow_origin == STREAMLIT_URL:
        print(f"   ✅ SUCCESS! Flask allows Streamlit Render origin")
        print(f"   ✅ Streamlit on Render CAN connect to Flask")
    elif allow_origin == '*':
        print(f"   ✅ SUCCESS! Flask allows all origins")
    else:
        print(f"   ❌ FAILED! Flask returned: {allow_origin}")
        print(f"   ❌ Expected: {STREAMLIT_URL}")
        print(f"\n🔍 Possible Issues:")
        print(f"      1. Deploy didn't pick up CORS changes")
        print(f"      2. Flask is still using old cached code")
        print(f"      3. CORS configuration error")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 80)
