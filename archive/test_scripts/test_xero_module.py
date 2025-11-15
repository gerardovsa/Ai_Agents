"""
Test Xero Module Integration
=============================

Tests the complete Xero module:
1. Module files exist
2. Backend routes are registered
3. API endpoints respond
4. AI tools are loaded

Run this after restarting BISTART to verify Xero integration.
"""

import os
import sys
import requests
from pathlib import Path

print("=" * 70)
print("XERO MODULE INTEGRATION TEST")
print("=" * 70)

# Test 1: Check module files exist
print("\n1. Checking Xero module files...")
module_path = Path(__file__).parent / 'UI' / 'external' / 'modules' / 'xero'
files_to_check = [
    'manifest.json',
    'xero.js',
    'xero.css',
    'xero_routes.py',
    'README.md'
]

all_files_exist = True
for file in files_to_check:
    file_path = module_path / file
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"   ✅ {file} ({size:,} bytes)")
    else:
        print(f"   ❌ {file} - NOT FOUND")
        all_files_exist = False

if all_files_exist:
    print("   🎉 All module files present!")
else:
    print("   ⚠️  Some files are missing")

# Test 2: Check if module is in manifest
print("\n2. Checking module registration in manifest...")
manifest_path = module_path.parent / 'manifest.json'
try:
    import json
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    xero_module = next((m for m in manifest['modules'] if m['id'] == 'xero'), None)
    if xero_module:
        print(f"   ✅ Xero module registered")
        print(f"      Name: {xero_module['name']}")
        print(f"      Icon: {xero_module['icon']}")
        print(f"      Color: {xero_module['color']}")
    else:
        print(f"   ❌ Xero module NOT in manifest")
except Exception as e:
    print(f"   ❌ Error reading manifest: {e}")

# Test 3: Check environment variables
print("\n3. Checking Xero credentials in .env.master...")
env_path = Path(__file__).parent / '.env.master'
if env_path.exists():
    print(f"   ✅ .env.master exists")
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    credentials = [
        'XERO_PRINT_CLIENT_ID',
        'XERO_PRINT_CLIENT_SECRET',
        'XERO_PUB_CLIENT_ID',
        'XERO_PUB_CLIENT_SECRET',
        'XERO_SIGNS_CLIENT_ID',
        'XERO_SIGNS_CLIENT_SECRET'
    ]
    
    for cred in credentials:
        if cred in content:
            # Check if it has a value (not just the key)
            line = [l for l in content.split('\n') if cred in l and '=' in l]
            if line and len(line[0].split('=')[1].strip()) > 0:
                print(f"   ✅ {cred} = [SET]")
            else:
                print(f"   ⚠️  {cred} = [EMPTY]")
        else:
            print(f"   ❌ {cred} - NOT FOUND")
else:
    print(f"   ❌ .env.master not found at {env_path}")

# Test 4: Test backend API endpoints (if server is running)
print("\n4. Testing backend API endpoints...")
print("   ⓘ  Make sure Flask server is running (BISTART)")

base_url = 'http://localhost:5001'
endpoints_to_test = [
    '/api/xero/dashboard?business_id=1',
    '/api/xero/invoices?business_id=1',
    '/api/xero/contacts?business_id=1',
    '/api/xero/payments?business_id=1',
    '/api/xero/accounts?business_id=1'
]

for endpoint in endpoints_to_test:
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ {endpoint}")
            else:
                print(f"   ⚠️  {endpoint} - API error: {data.get('error', 'Unknown')}")
        else:
            print(f"   ❌ {endpoint} - HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  {endpoint} - Server not running")
        break
    except Exception as e:
        print(f"   ❌ {endpoint} - Error: {e}")

# Test 5: Check tool registry
print("\n5. Checking Xero tools in registry...")
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    xero_tools = [name for name in registry.tools.keys() if 'xero' in name]
    
    if xero_tools:
        print(f"   ✅ Found {len(xero_tools)} Xero tools:")
        for tool in xero_tools:
            print(f"      • {tool}")
    else:
        print(f"   ❌ No Xero tools found in registry")
        print(f"   ⓘ  Total tools loaded: {len(registry.tools)}")
except Exception as e:
    print(f"   ❌ Error loading registry: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("""
Next Steps:
1. If server not running: Run 'BISTART' to start Flask server
2. If credentials empty: Update .env.master with Xero API credentials
3. If tools not loaded: Restart BISTART to reload tools
4. Test UI: Open browser → AI_agents → Click 'Xero Accounting'
5. Test AI: Run 'CHAT "Show me Xero invoices from InHouse Print"'

Module Location:
UI/external/modules/xero/

API Documentation:
http://localhost:5001/api/xero/dashboard?business_id=1

AI Commands:
CHAT "Show Xero invoices"
CHAT "Get Xero contacts for InHouse Publishing"
CHAT "What's the outstanding balance in Xero?"
""")
print("=" * 70)
