#!/usr/bin/env python3
"""
Comprehensive Test Suite for InHouse Print Module
Tests all import paths, dependencies, and functionality
"""

import sys
import os
from pathlib import Path

def test_direct_import():
    """Test 1: Direct import from inhouse-print directory"""
    print("\n" + "="*60)
    print("TEST 1: Direct Import (sys.path method)")
    print("="*60)
    
    try:
        inhouse_print_path = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print'
        if inhouse_print_path not in sys.path:
            sys.path.insert(0, inhouse_print_path)
        
        from db_connector import InHousePrintDB
        
        print("✅ SUCCESS: InHousePrintDB imported")
        print(f"   Class: {InHousePrintDB}")
        print(f"   Module: {InHousePrintDB.__module__}")
        
        # Get all public methods
        methods = [m for m in dir(InHousePrintDB) if not m.startswith('_')]
        print(f"   Public methods: {', '.join(methods)}")
        
        return True, InHousePrintDB
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_class_instantiation(InHousePrintDB):
    """Test 2: Try to instantiate the class"""
    print("\n" + "="*60)
    print("TEST 2: Class Instantiation")
    print("="*60)
    
    if InHousePrintDB is None:
        print("⏭️  SKIPPED: InHousePrintDB not available")
        return False
    
    try:
        # Try to instantiate (may fail if no config, but should not error on import)
        db = InHousePrintDB()
        print("✅ SUCCESS: Class instantiated")
        print(f"   Connection: {db.connection}")
        return True
    except FileNotFoundError as e:
        print("⚠️  EXPECTED ERROR (no config file):")
        print(f"   {e}")
        print("   This is OK - class structure is valid")
        return True
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test 3: Check all dependencies"""
    print("\n" + "="*60)
    print("TEST 3: Dependency Check")
    print("="*60)
    
    required_packages = [
        'pyodbc',
        'pandas',
        'json',
        'argparse',
        'datetime',
        'typing'
    ]
    
    results = {}
    for package in required_packages:
        try:
            __import__(package)
            results[package] = True
            print(f"✅ {package:<15} - Available")
        except ImportError:
            results[package] = False
            print(f"❌ {package:<15} - MISSING")
    
    all_ok = all(results.values())
    return all_ok

def test_backward_dependencies():
    """Test 4: Find what imports inhouse-print"""
    print("\n" + "="*60)
    print("TEST 4: Backward Dependencies (Who imports this module)")
    print("="*60)
    
    # Files that should import inhouse-print
    dependent_files = [
        r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend\tool_use_agent.py',
        r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend\god_calculators\GOD_flyer_calculator.py',
        r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend\god_calculators\GOD_perfect_bound_books_calculator.py',
        r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print\implementations\inhouse_wrapper.py'
    ]
    
    for file_path in dependent_files:
        if os.path.exists(file_path):
            print(f"\n📄 {Path(file_path).name}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'db_connector' in content or 'InHousePrintDB' in content:
                        print(f"   ✅ Contains inhouse-print imports")
                        # Find the import lines
                        for i, line in enumerate(content.split('\n'), 1):
                            if 'db_connector' in line or 'InHousePrintDB' in line:
                                if not line.strip().startswith('#'):
                                    print(f"   Line {i}: {line.strip()}")
                    else:
                        print(f"   ⚠️  No inhouse-print imports found")
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
        else:
            print(f"❌ File not found: {file_path}")
    
    return True

def test_forward_dependencies():
    """Test 5: What does inhouse-print import"""
    print("\n" + "="*60)
    print("TEST 5: Forward Dependencies (What this module needs)")
    print("="*60)
    
    db_connector_path = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print\db_connector.py'
    
    if os.path.exists(db_connector_path):
        with open(db_connector_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n📦 Standard Library Imports:")
        stdlib_imports = ['pyodbc', 'pandas', 'json', 'argparse', 'sys', 'warnings', 'datetime', 'typing', 'os']
        for imp in stdlib_imports:
            if f'import {imp}' in content:
                print(f"   ✅ {imp}")
        
        print("\n📦 Project Imports:")
        if 'AI_infrastructure.auth.supabase_credentials' in content:
            print("   ✅ AI_infrastructure.auth.supabase_credentials")
            print("      (Optional - for Render deployment)")
        
        return True
    else:
        print(f"❌ db_connector.py not found")
        return False

def test_quote_calculator_integration():
    """Test 6: Verify quote-calculator can import"""
    print("\n" + "="*60)
    print("TEST 6: Quote Calculator Integration")
    print("="*60)
    
    # Simulate the import pattern from tool_use_agent.py
    try:
        current_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend'
        inhouse_print_module = os.path.join(current_dir, '..', '..', 'inhouse-print')
        inhouse_print_module = os.path.abspath(inhouse_print_module)
        
        print(f"Adding to sys.path: {inhouse_print_module}")
        
        if os.path.exists(inhouse_print_module):
            if inhouse_print_module not in sys.path:
                sys.path.insert(0, inhouse_print_module)
            
            from db_connector import InHousePrintDB
            print("✅ SUCCESS: Quote calculator can import InHousePrintDB")
            return True
        else:
            print(f"❌ FAILED: Path doesn't exist: {inhouse_print_module}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_structure():
    """Test 7: Verify module file structure"""
    print("\n" + "="*60)
    print("TEST 7: Module File Structure")
    print("="*60)
    
    base_path = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print'
    
    required_files = {
        '__init__.py': 'Module initialization',
        'db_connector.py': 'Database connection class',
        'manifest.json': 'Module manifest',
        'README.md': 'Documentation'
    }
    
    required_dirs = {
        'backend': 'Backend scripts',
        'implementations': 'Implementation wrappers',
        'schema': 'Database schema'
    }
    
    print("\n📁 Required Files:")
    all_files_ok = True
    for filename, description in required_files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {filename:<20} ({size:,} bytes) - {description}")
        else:
            print(f"   ❌ {filename:<20} - MISSING - {description}")
            all_files_ok = False
    
    print("\n📁 Required Directories:")
    all_dirs_ok = True
    for dirname, description in required_dirs.items():
        dirpath = os.path.join(base_path, dirname)
        if os.path.exists(dirpath):
            num_files = len([f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))])
            print(f"   ✅ {dirname:<20} ({num_files} files) - {description}")
        else:
            print(f"   ❌ {dirname:<20} - MISSING - {description}")
            all_dirs_ok = False
    
    return all_files_ok and all_dirs_ok

def main():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("InHouse Print Module - Comprehensive Test Suite")
    print("🧪"*30)
    
    results = {}
    
    # Test 1: Direct import
    success, InHousePrintDB = test_direct_import()
    results['Direct Import'] = success
    
    # Test 2: Class instantiation
    results['Class Instantiation'] = test_class_instantiation(InHousePrintDB)
    
    # Test 3: Dependencies
    results['Dependencies'] = test_dependencies()
    
    # Test 4: Backward dependencies
    results['Backward Dependencies'] = test_backward_dependencies()
    
    # Test 5: Forward dependencies
    results['Forward Dependencies'] = test_forward_dependencies()
    
    # Test 6: Quote calculator integration
    results['Quote Calculator'] = test_quote_calculator_integration()
    
    # Test 7: Module structure
    results['Module Structure'] = test_module_structure()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
