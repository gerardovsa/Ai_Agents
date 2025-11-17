"""
Test all database connections across the entire application
Verifies:
1. Supabase connection to all schemas
2. All critical tables exist
3. Sample queries work
4. No SQLite placeholders remain
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection
import re
from pathlib import Path

def test_schema_connection(schema_name, expected_tables):
    """Test connection to a specific schema"""
    print(f"\n{'='*80}")
    print(f"Testing {schema_name} schema")
    print('='*80)
    
    try:
        conn = get_database_connection(schema_name)
        cursor = conn.cursor()
        
        # Get all tables in schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name
        """, (schema_name,))
        
        tables = [row[0] if isinstance(row, tuple) else row['table_name'] for row in cursor.fetchall()]
        
        print(f"Found {len(tables)} tables")
        
        # Check for expected tables
        missing_tables = []
        for expected in expected_tables:
            if expected in tables:
                print(f"  ✅ {expected}")
            else:
                print(f"  ❌ MISSING: {expected}")
                missing_tables.append(expected)
        
        # Test a simple query on the first table
        if tables:
            test_table = tables[0]
            cursor.execute(f"""
                SELECT COUNT(*) FROM {schema_name}.{test_table}
            """)
            count_result = cursor.fetchone()
            count = count_result[0] if isinstance(count_result, tuple) else count_result['count']
            print(f"\n  Sample query: {test_table} has {count} rows")
        
        conn.close()
        
        if missing_tables:
            print(f"\n  ⚠️  WARNING: Missing {len(missing_tables)} expected tables")
            return False
        else:
            print(f"\n  ✅ All expected tables present")
            return True
            
    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def scan_for_remaining_sqlite_placeholders():
    """Scan codebase for any remaining SQLite placeholders"""
    print(f"\n{'='*80}")
    print("Scanning for remaining SQLite placeholders (?)")
    print('='*80)
    
    base_dir = Path('AI_infrastructure')
    python_files = list(base_dir.glob('**/*.py'))
    python_files = [f for f in python_files if '__pycache__' not in str(f)]
    
    issues_found = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for SQL queries with ? placeholders
            sql_keywords = ['WHERE', 'SET', 'VALUES', 'AND', 'OR', 'LIKE', 'IN']
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                # Check if line has SQL keywords and ?
                if any(keyword in line.upper() for keyword in sql_keywords):
                    if '?' in line and '# ?' not in line:
                        # Check if ? is in a SQL context (in a string)
                        if ("'" in line or '"' in line) and any(kw in line.upper() for kw in sql_keywords):
                            issues_found.append((file_path, line_num, line.strip()))
        
        except Exception as e:
            pass
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} potential SQLite placeholders:\n")
        for file_path, line_num, line in issues_found[:20]:  # Show first 20
            rel_path = str(file_path).replace('AI_infrastructure\\\\', '')
            print(f"  {rel_path}:{line_num}")
            print(f"    {line[:100]}")
        
        if len(issues_found) > 20:
            print(f"\n  ... and {len(issues_found) - 20} more")
        
        return False
    else:
        print("\n✅ No SQLite placeholders found - all queries use PostgreSQL syntax")
        return True

def main():
    print("="*80)
    print("COMPREHENSIVE DATABASE CONNECTION TEST")
    print("="*80)
    
    schemas_to_test = {
        'ai_infrastructure': [
            'users',
            'user_sessions',
            'oauth_tokens',
            'workspaces',
            'scheduled_tasks',
            'user_preferences'
        ],
        'sessions': [
            'threads',
            'messages',
            'api_sessions'
        ],
        'synergy_sessions': [
            'synergy_sessions',
            'synergy_internal_docs'
        ],
        'kanban_analytics': [
            'job_tickets',
            'clients',
            'production_log'
        ]
    }
    
    results = {}
    
    # Test each schema
    for schema_name, expected_tables in schemas_to_test.items():
        results[schema_name] = test_schema_connection(schema_name, expected_tables)
    
    # Scan for remaining issues
    no_sqlite_placeholders = scan_for_remaining_sqlite_placeholders()
    
    # Summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print('='*80)
    
    all_passed = all(results.values()) and no_sqlite_placeholders
    
    for schema, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {schema}")
    
    placeholder_status = "✅ PASS" if no_sqlite_placeholders else "❌ FAIL"
    print(f"{placeholder_status}: No SQLite placeholders")
    
    print('='*80)
    
    if all_passed:
        print("\n✅✅✅ ALL TESTS PASSED ✅✅✅")
        print("\nAll database connections are working correctly!")
        print("All queries use PostgreSQL syntax!")
        print("\nYour application is ready for Supabase!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review errors above")
        print("\nAction items:")
        if not all(results.values()):
            print("  1. Check Supabase schema migrations")
        if not no_sqlite_placeholders:
            print("  2. Fix remaining SQLite placeholders")
    
    print('='*80)

if __name__ == '__main__':
    main()
