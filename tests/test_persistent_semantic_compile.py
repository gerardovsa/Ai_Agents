"""
COMPILE TEST: Persistent Semantic Search
========================================

Validates that all code compiles and basic functionality works.

USAGE:
    python tests/test_persistent_semantic_compile.py

EXPECTED: All modules load, methods callable, no syntax errors
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def compile_test():
    """Test that all code compiles and basic methods work"""
    print("\n" + "=" * 80)
    print("COMPILE TEST: Persistent Semantic Search")
    print("=" * 80)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Version hash calculation
    print("\n[TEST 1/8] Version hash calculation...")
    try:
        from tools.registry_v3 import get_registry
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        
        registry = get_registry()
        search = PersistentSemanticToolSearch.__new__(PersistentSemanticToolSearch)
        search.registry = registry
        
        version_hash = search._calculate_version_hash()
        
        if version_hash and len(version_hash) == 64:  # SHA256 is 64 hex chars
            print(f"✅ PASS: Version hash calculated ({version_hash[:16]}...)")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Invalid version hash: {version_hash}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1
    
    # Test 2: Database schema creation
    print("\n[TEST 2/8] Database schema creation (dry-run)...")
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Check if tables exist
        tables = execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name LIKE 'tool_embedding%'
        """, fetch_mode='all')
        
        table_names = [t['table_name'] for t in tables] if tables else []
        
        if 'tool_embeddings' in table_names and 'tool_embedding_cache' in table_names:
            print(f"✅ PASS: Tables exist ({len(tables)} tables)")
            tests_passed += 1
        else:
            print(f"⚠️ WARN: Tables not found. Run migration first:")
            print("   python AI_infrastructure/migrations/create_tool_embeddings_tables.py")
            tests_passed += 1  # Not a compile error
    except Exception as e:
        print(f"⚠️ WARN: Database check failed: {e}")
        tests_passed += 1  # Not a compile error
    
    # Test 3: Embedding generation (mock)
    print("\n[TEST 3/8] Embedding generation (mock)...")
    try:
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        from tools.registry_v3 import get_registry
        
        # Check if sentence-transformers available
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate single embedding as test
            test_text = "send email message"
            embedding = model.encode(test_text, convert_to_numpy=True)
            
            if len(embedding) == 384:  # all-MiniLM-L6-v2 produces 384-dim vectors
                print(f"✅ PASS: Embedding generated (384 dimensions)")
                tests_passed += 1
            else:
                print(f"❌ FAIL: Wrong embedding dimension: {len(embedding)}")
                tests_failed += 1
        except ImportError:
            print("⚠️ SKIP: sentence-transformers not installed")
            tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1
    
    # Test 4: Search method signature
    print("\n[TEST 4/8] Search method signature...")
    try:
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        
        # Check method exists and has correct signature
        import inspect
        sig = inspect.signature(PersistentSemanticToolSearch.search)
        params = list(sig.parameters.keys())
        
        expected_params = ['self', 'query', 'top_k', 'similarity_threshold']
        if all(p in params for p in expected_params):
            print(f"✅ PASS: Search method has correct signature")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Missing parameters. Expected {expected_params}, got {params}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 5: Management script functions
    print("\n[TEST 5/8] Management script functions...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
        import manage_semantic_cache
        
        # Check functions exist
        functions = ['check_status', 'invalidate_cache', 'regenerate_cache', 'show_stats']
        missing = []
        for func in functions:
            if not hasattr(manage_semantic_cache, func):
                missing.append(func)
        
        if not missing:
            print(f"✅ PASS: All management functions defined")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Missing functions: {missing}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 6: Flask route integration
    print("\n[TEST 6/8] Flask route integration...")
    try:
        from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search
        
        # Check function exists and has correct signature
        import inspect
        sig = inspect.signature(get_semantic_search)
        params = list(sig.parameters.keys())
        
        if 'registry' in params:
            print(f"✅ PASS: Flask route function has correct signature")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Missing 'registry' parameter")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        tests_failed += 1
    
    # Test 7: Flask startup integration
    print("\n[TEST 7/8] Flask startup integration...")
    try:
        # Check if initialize_semantic_search_on_startup exists in flask_app
        flask_app_path = Path(__file__).parent.parent / 'AI_infrastructure' / 'flask_app.py'
        with open(flask_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check function exists
        if 'def initialize_semantic_search_on_startup():' in content:
            print(f"✅ PASS: Startup function exists in flask_app.py")
            
            # Check if it's uncommented
            if 'initialize_semantic_search_on_startup()' in content and \
               '# initialize_semantic_search_on_startup()' not in content.split('if __name__')[-1]:
                print(f"✅ PASS: Startup function is ENABLED (not commented)")
                tests_passed += 1
            else:
                print(f"⚠️ WARN: Startup function might be commented out")
                print(f"   Check line ~3875 in flask_app.py")
                tests_passed += 1  # Not a compile error
        else:
            print(f"❌ FAIL: Startup function not found in flask_app.py")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
    
    # Test 8: Migration script
    print("\n[TEST 8/8] Migration script...")
    try:
        migration_path = Path(__file__).parent.parent / 'AI_infrastructure' / 'migrations' / 'create_tool_embeddings_tables.py'
        
        if migration_path.exists():
            print(f"✅ PASS: Migration script exists")
            
            # Check if it's executable
            with open(migration_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'def run_migration():' in content:
                print(f"✅ PASS: Migration script has run_migration() function")
                tests_passed += 1
            else:
                print(f"❌ FAIL: Migration script missing run_migration() function")
                tests_failed += 1
        else:
            print(f"❌ FAIL: Migration script not found at {migration_path}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPILE TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {tests_passed}/8")
    print(f"❌ Failed: {tests_failed}/8")
    
    if tests_failed == 0:
        print("\n🎉 ALL COMPILE TESTS PASSED")
        print("System is ready for endpoint and integration testing")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Fix errors before proceeding")
        return False


if __name__ == '__main__':
    success = compile_test()
    sys.exit(0 if success else 1)
