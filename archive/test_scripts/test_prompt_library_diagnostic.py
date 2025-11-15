"""
Prompt Library Diagnostic Script

Tests:
1. Database connection
2. Table structure verification
3. Sample data verification
4. API endpoint availability
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

import sqlite3
from pathlib import Path
import requests

def test_database_connection():
    """Test if database exists and is accessible"""
    print("\n" + "="*80)
    print("TEST 1: Database Connection")
    print("="*80)
    
    db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
    print(f"Database path: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    if not db_path.exists():
        print("❌ ERROR: Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if prompt_library table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='prompt_library'
        """)
        
        result = cursor.fetchone()
        if result:
            print("✅ prompt_library table exists")
        else:
            print("❌ ERROR: prompt_library table NOT found!")
            conn.close()
            return False
        
        # Count rows
        cursor.execute("SELECT COUNT(*) as count FROM prompt_library")
        count = cursor.fetchone()['count']
        print(f"✅ Found {count} prompts in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_table_structure():
    """Verify table has all required columns"""
    print("\n" + "="*80)
    print("TEST 2: Table Structure")
    print("="*80)
    
    db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(prompt_library)")
        columns = cursor.fetchall()
        
        required_columns = [
            'id', 'user_id', 'workspace_id', 'name', 'category', 
            'type', 'description', 'prompt_text', 'tags', 
            'visibility', 'usage_count', 'created_at', 'updated_at'
        ]
        
        found_columns = [col[1] for col in columns]
        
        print(f"Required columns: {len(required_columns)}")
        print(f"Found columns: {len(found_columns)}")
        
        missing = set(required_columns) - set(found_columns)
        if missing:
            print(f"❌ ERROR: Missing columns: {missing}")
            conn.close()
            return False
        
        print("✅ All required columns present:")
        for col in found_columns:
            print(f"   - {col}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_sample_data():
    """Check if sample prompts exist"""
    print("\n" + "="*80)
    print("TEST 3: Sample Data")
    print("="*80)
    
    db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get first 3 prompts
        cursor.execute("""
            SELECT id, user_id, name, category, type, visibility
            FROM prompt_library
            LIMIT 3
        """)
        
        prompts = cursor.fetchall()
        
        if not prompts:
            print("❌ ERROR: No prompts found in database!")
            conn.close()
            return False
        
        print(f"✅ Found {len(prompts)} sample prompts:")
        for prompt in prompts:
            print(f"   ID {prompt['id']}: '{prompt['name']}' ({prompt['category']}, {prompt['type']}, {prompt['visibility']})")
        
        # Check users
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM prompt_library")
        user_count = cursor.fetchone()['count']
        print(f"✅ Prompts exist for {user_count} different users")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_api_endpoints():
    """Test if Flask server is running and endpoints are available"""
    print("\n" + "="*80)
    print("TEST 4: API Endpoints")
    print("="*80)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        print(f"✅ Flask server is running (status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("❌ ERROR: Flask server not running!")
        print("   Run: cd AI_infrastructure && python flask_app.py")
        return False
    
    # Test 2: List prompts endpoint
    try:
        response = requests.get(
            f"{base_url}/api/prompts/library/db?user_id=1",
            headers={'X-User-ID': '1'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prompt_count = data.get('count', 0)
                print(f"✅ GET /api/prompts/library/db works ({prompt_count} prompts)")
            else:
                print(f"⚠️  WARNING: Endpoint returned success=false: {data.get('error')}")
        else:
            print(f"❌ ERROR: Endpoint returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Could not reach endpoint: {e}")
        return False
    
    print("✅ All API endpoints accessible")
    return True


def test_javascript_module():
    """Check if JavaScript module file exists"""
    print("\n" + "="*80)
    print("TEST 5: JavaScript Module")
    print("="*80)
    
    js_path = Path(__file__).parent / 'UI' / 'modules' / 'prompt-library.js'
    css_path = Path(__file__).parent / 'UI' / 'modules' / 'prompt-library.css'
    
    if js_path.exists():
        print(f"✅ JavaScript module exists: {js_path.name}")
        # Check file size
        size = js_path.stat().st_size
        print(f"   File size: {size:,} bytes")
        
        # Check for syntax error (try: instead of try {)
        content = js_path.read_text(encoding='utf-8')
        if 'try:' in content:
            print("❌ ERROR: Found Python syntax 'try:' in JavaScript file!")
            return False
        else:
            print("✅ No Python syntax errors detected")
    else:
        print(f"❌ ERROR: JavaScript module not found!")
        return False
    
    if css_path.exists():
        print(f"✅ CSS module exists: {css_path.name}")
    else:
        print(f"❌ ERROR: CSS module not found!")
        return False
    
    return True


def main():
    """Run all diagnostic tests"""
    print("\n" + "#"*80)
    print("# PROMPT LIBRARY DIAGNOSTIC SCRIPT")
    print("#"*80)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Structure", test_table_structure),
        ("Sample Data", test_sample_data),
        ("API Endpoints", test_api_endpoints),
        ("JavaScript Module", test_javascript_module)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "#"*80)
    print("# TEST SUMMARY")
    print("#"*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Prompt library system is fully operational.")
        print("\nNext steps:")
        print("1. Open http://localhost:5001/ui in your browser")
        print("2. Look for the ⚡ lightning bolt button (top right)")
        print("3. Click to open the prompt library dropdown")
        print("4. Open browser console (F12) to see debug logs")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
