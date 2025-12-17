"""
Quick test: Verify dev-tools route is accessible
"""
import requests
import time

print('=' * 80)
print('DEV-TOOLS ROUTE VERIFICATION TEST')
print('=' * 80)
print()

# Wait for Flask to start
print('⏳ Waiting 3 seconds for Flask to start...')
time.sleep(3)

base_url = 'http://localhost:5001'

tests = [
    {
        'name': 'Module Creator HTML',
        'url': f'{base_url}/dev-tools/module-creator-enhanced.html',
        'expected_content': 'Module Creator & Verifier'
    },
    {
        'name': 'Module Creator JavaScript',
        'url': f'{base_url}/dev-tools/module-creator-enhanced.js',
        'expected_content': 'ModuleCreatorEnhanced'
    },
    {
        'name': 'Module Creator CSS',
        'url': f'{base_url}/dev-tools/module-creator.css',
        'expected_content': 'Module Creator & Verifier'
    },
    {
        'name': 'Credential Testing Guide',
        'url': f'{base_url}/dev-tools/CREDENTIAL_TESTING_GUIDE.md',
        'expected_content': 'Credential Testing Guide'
    }
]

passed = 0
failed = 0

for test in tests:
    try:
        response = requests.get(test['url'], timeout=5)
        
        if response.status_code == 200:
            if test['expected_content'] in response.text:
                print(f"✅ {test['name']}")
                print(f"   URL: {test['url']}")
                print(f"   Size: {len(response.content):,} bytes")
                passed += 1
            else:
                print(f"❌ {test['name']} - Content mismatch")
                print(f"   Expected: '{test['expected_content']}'")
                failed += 1
        else:
            print(f"❌ {test['name']} - HTTP {response.status_code}")
            print(f"   URL: {test['url']}")
            print(f"   Response: {response.text[:200]}...")
            failed += 1
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {test['name']} - Connection Error")
        print(f"   Error: {e}")
        failed += 1

print()
print('=' * 80)
print(f'RESULTS: {passed}/{len(tests)} tests passed')
print('=' * 80)

if passed == len(tests):
    print()
    print('✅ ALL TESTS PASSED!')
    print()
    print('📍 Open Module Creator:')
    print('   http://localhost:5001/dev-tools/module-creator-enhanced.html')
    print()
else:
    print()
    print('⚠️  Some tests failed - check Flask is running (BISTART)')
    print()
