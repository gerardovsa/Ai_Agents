"""
Quick Database Visualizer Test
Simple test to verify the module is working
"""

import requests

BASE_URL = "http://localhost:5001"

def test_health():
    """Test if server is running"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f" Server running: {r.status_code}")
        return True
    except:
        print(" Server not running")
        return False

def test_list_databases():
    """Test list databases endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/database-visualizer/list-databases", timeout=5)
        print(f"\n📊 List Databases: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Databases found: {len(data.get('databases', []))}")
            if data.get('databases'):
                print(f"   First DB: {data['databases'][0]['name']}")
            return True
        else:
            print(f"   Error: {r.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_schema():
    """Test schema endpoint"""
    try:
        # Get first database
        r = requests.get(f"{BASE_URL}/api/database-visualizer/list-databases", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('databases'):
                db_path = data['databases'][0]['path']
                
                # Get schema
                r2 = requests.get(
                    f"{BASE_URL}/api/database-visualizer/schema",
                    params={'db_path': db_path},
                    timeout=5
                )
                print(f"\n📋 Get Schema: {r2.status_code}")
                if r2.status_code == 200:
                    schema_data = r2.json()
                    print(f"   Success: {schema_data.get('success', False)}")
                    print(f"   Tables: {schema_data.get('table_count', 0)}")
                    if schema_data.get('schema'):
                        first_table = list(schema_data['schema'].keys())[0]
                        print(f"   First table: {first_table}")
                    return True
                else:
                    print(f"   Error: {r2.text}")
                    return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Visualizer - Quick Test")
    print("=" * 60)
    
    if not test_health():
        print("\n Server not running. Please start with:")
        print("   cd AI_infrastructure")
        print("   python flask_app.py")
        exit(1)
    
    test_list_databases()
    test_schema()
    
    print("\n" + "=" * 60)
    print(" Database Visualizer module is working!")
    print("=" * 60)
    print("\n📌 Next steps:")
    print("   1. Open browser: http://localhost:5001")
    print("   2. Navigate to Database Visualizer module")
    print("   3. Explore the 3 tabs:")
    print("      - Databases: View all .db files")
    print("      - Schema Explorer: Examine table structures")
    print("      - Data Viewer: Browse table data")
