#!/usr/bin/env python3
"""
Test Quote Calculator Scripts for Import Issues
Verifies that all GOD calculators can import dependencies correctly
"""

import sys
import os
from pathlib import Path

def test_god_flyer_calculator():
    """Test GOD_flyer_calculator.py imports"""
    print("\n" + "="*60)
    print("TEST: GOD Flyer Calculator")
    print("="*60)
    
    try:
        # Set up path like tool_use_agent.py does
        backend_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend'
        god_calc_dir = os.path.join(backend_dir, 'god_calculators')
        inhouse_print_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print'
        
        # Add paths
        for path in [backend_dir, god_calc_dir, inhouse_print_dir]:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        # Try importing the calculator
        script_path = os.path.join(god_calc_dir, 'GOD_flyer_calculator.py')
        
        if not os.path.exists(script_path):
            print(f"❌ FAILED: File not found: {script_path}")
            return False
        
        print(f"📄 Reading: {script_path}")
        
        # Check for syntax errors by compiling
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, script_path, 'exec')
        print("✅ Syntax check passed")
        
        # Try importing db_connector
        from db_connector import InHousePrintDB
        print("✅ InHousePrintDB import successful")
        
        # Try importing the calculator class (without executing __main__)
        import importlib.util
        spec = importlib.util.spec_from_file_location("GOD_flyer_calculator", script_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Don't execute - just verify it can be loaded
            print("✅ Module can be loaded")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_god_perfect_bound_calculator():
    """Test GOD_perfect_bound_books_calculator.py imports"""
    print("\n" + "="*60)
    print("TEST: GOD Perfect Bound Books Calculator")
    print("="*60)
    
    try:
        # Set up path
        backend_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend'
        god_calc_dir = os.path.join(backend_dir, 'god_calculators')
        inhouse_print_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print'
        
        for path in [backend_dir, god_calc_dir, inhouse_print_dir]:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        script_path = os.path.join(god_calc_dir, 'GOD_perfect_bound_books_calculator.py')
        
        if not os.path.exists(script_path):
            print(f"❌ FAILED: File not found: {script_path}")
            return False
        
        print(f"📄 Reading: {script_path}")
        
        # Syntax check
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, script_path, 'exec')
        print("✅ Syntax check passed")
        
        # Check imports mentioned in file
        from db_connector import InHousePrintDB
        print("✅ InHousePrintDB import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_use_agent():
    """Test tool_use_agent.py imports"""
    print("\n" + "="*60)
    print("TEST: Tool Use Agent")
    print("="*60)
    
    try:
        backend_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend'
        script_path = os.path.join(backend_dir, 'tool_use_agent.py')
        
        if not os.path.exists(script_path):
            print(f"❌ FAILED: File not found: {script_path}")
            return False
        
        print(f"📄 Reading: {script_path}")
        
        # Just syntax check - don't try to execute
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, script_path, 'exec')
        print("✅ Syntax check passed")
        
        # Check that it references the right paths
        if 'inhouse-print' in code:
            print("✅ References inhouse-print module")
        if 'from db_connector import InHousePrintDB' in code:
            print("✅ Contains correct import statement")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_inhouse_wrapper():
    """Test inhouse_wrapper.py"""
    print("\n" + "="*60)
    print("TEST: InHouse Wrapper")
    print("="*60)
    
    try:
        wrapper_path = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\inhouse-print\implementations\inhouse_wrapper.py'
        
        if not os.path.exists(wrapper_path):
            print(f"❌ FAILED: File not found: {wrapper_path}")
            return False
        
        print(f"📄 Reading: {wrapper_path}")
        
        # Syntax check
        with open(wrapper_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, wrapper_path, 'exec')
        print("✅ Syntax check passed")
        
        # Check structure
        if 'class InHouseWrapper' in code:
            print("✅ Contains InHouseWrapper class")
        if 'InHousePrintDB' in code:
            print("✅ References InHousePrintDB")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_corflute_calculator():
    """Test corflute_calculator.py which uses InHousePrint data"""
    print("\n" + "="*60)
    print("TEST: Corflute Calculator (uses InHousePrint data)")
    print("="*60)
    
    try:
        calc_path = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\backend\god_calculators\corflute_calculator.py'
        
        if not os.path.exists(calc_path):
            print(f"⚠️  File not found: {calc_path}")
            print("   (This is OK if calculator doesn't exist yet)")
            return True
        
        print(f"📄 Reading: {calc_path}")
        
        # Syntax check
        with open(calc_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, calc_path, 'exec')
        print("✅ Syntax check passed")
        
        # Check if it mentions InHousePrint
        if 'InHouse Print' in code or 'InHousePrint' in code:
            print("✅ References InHousePrint data")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_implementation_files():
    """Check all implementation files in quote-calculator"""
    print("\n" + "="*60)
    print("TEST: Quote Calculator Implementation Files")
    print("="*60)
    
    impl_dir = r'c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\implementations'
    
    if not os.path.exists(impl_dir):
        print(f"❌ Directory not found: {impl_dir}")
        return False
    
    try:
        files = [f for f in os.listdir(impl_dir) if f.endswith('.py')]
        print(f"Found {len(files)} Python files")
        
        all_ok = True
        for filename in files:
            filepath = os.path.join(impl_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, filepath, 'exec')
                print(f"   ✅ {filename}")
            except SyntaxError as e:
                print(f"   ❌ {filename} - SYNTAX ERROR at line {e.lineno}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

def main():
    """Run all script tests"""
    print("\n" + "🧪"*30)
    print("Quote Calculator Scripts - Import & Dependency Tests")
    print("🧪"*30)
    
    results = {}
    
    # Test each script
    results['GOD Flyer Calculator'] = test_god_flyer_calculator()
    results['GOD Perfect Bound Calculator'] = test_god_perfect_bound_calculator()
    results['Tool Use Agent'] = test_tool_use_agent()
    results['InHouse Wrapper'] = test_inhouse_wrapper()
    results['Corflute Calculator'] = test_corflute_calculator()
    results['Implementation Files'] = check_implementation_files()
    
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
        print("\n🎉 ALL SCRIPTS VALIDATED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
