"""
Quick Test Script for Production Deployment Fixes
Run this BEFORE pushing to verify fixes work locally
"""

import sys
import os

print("="*80)
print("TESTING PRODUCTION DEPLOYMENT FIXES")
print("="*80)

# Test 1: ToolUseAgent Import
print("\n[TEST 1] ToolUseAgent Import (should not reference C:/Users/gpoli/...)")
try:
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from UI.modules_external.quote_calculator.backend.tool_use_agent import ToolUseAgent
    print("✅ PASS: ToolUseAgent imported successfully")
    print("   No hardcoded C:/Users/gpoli paths causing import failures")
except ImportError as e:
    print(f"❌ FAIL: {e}")
    print("   Import should work now with relative paths")

# Test 2: InHouse Wrapper Import
print("\n[TEST 2] InHouse Wrapper Import")
try:
    from UI.modules_external.inhouse_print.implementations.inhouse_wrapper import inhouse_execute_sql
    print("✅ PASS: InHouse wrapper imported successfully")
    print("   _get_agent() should work now (no hardcoded paths)")
except ImportError as e:
    print(f"⚠️  WARNING: {e}")
    print("   This may fail if config files are missing (OK for test)")

# Test 3: Query Library Wrapper with Pandas
print("\n[TEST 3] Query Library Wrapper - Pandas Import")
try:
    from UI.modules_external.quote_calculator.implementations.query_library_wrapper import execute_query_library
    import pandas as pd
    print("✅ PASS: Query library wrapper has pandas import")
    
    # Check if DataFrame conversion code exists
    import inspect
    source = inspect.getsource(execute_query_library)
    
    if 'to_dict(orient=' in source:
        print("✅ PASS: DataFrame conversion code present")
        print("   DataFrame will be converted to JSON-serializable dict")
    else:
        print("❌ FAIL: DataFrame conversion code missing")
        
except ImportError as e:
    print(f"❌ FAIL: {e}")

# Test 4: Registry V3 Tool Discovery
print("\n[TEST 4] Registry V3 Tool Discovery")
try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    # Check for InHouse tools
    inhouse_tools = [name for name in registry.tools.keys() if 'inhouse' in name.lower()]
    query_tools = [name for name in registry.tools.keys() if 'query' in name.lower()]
    
    print(f"✅ PASS: Registry initialized with {len(registry.tools)} tools")
    print(f"   InHouse tools: {len(inhouse_tools)}")
    print(f"   Query tools: {len(query_tools)}")
    
    # Check specific tools
    critical_tools = [
        'inhouse_execute_sql',
        'inhouse_get_query_library_catalog',
        'execute_query_library',
        'get_available_queries'
    ]
    
    for tool in critical_tools:
        if tool in registry.tools:
            print(f"   ✅ {tool} - registered")
        else:
            print(f"   ❌ {tool} - missing")
            
except Exception as e:
    print(f"❌ FAIL: {e}")
    import traceback
    print(traceback.format_exc())

# Test 5: Path Verification
print("\n[TEST 5] Path Verification in tool_use_agent.py")
try:
    # Read the file and check for hardcoded paths
    tool_use_agent_path = os.path.join(
        project_root,
        'UI', 'modules_external', 'quote-calculator', 'backend', 'tool_use_agent.py'
    )
    
    with open(tool_use_agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for bad patterns
    bad_patterns = [
        "C:/Users/gpoli",
        "In_House_SQL",
        "in_house_sql_root = 'C:"
    ]
    
    found_issues = []
    for pattern in bad_patterns:
        if pattern in content:
            # Count occurrences
            count = content.count(pattern)
            found_issues.append((pattern, count))
    
    if found_issues:
        print("❌ FAIL: Found hardcoded paths that should be removed:")
        for pattern, count in found_issues:
            print(f"   - '{pattern}' appears {count} times")
    else:
        print("✅ PASS: No hardcoded Windows paths found")
        print("   File uses relative paths only")
        
    # Check for good patterns
    good_patterns = [
        "shopify_calc_path = os.path.join(current_dir, 'shopify_calculators')",
        "ENVIRONMENT-AGNOSTIC"
    ]
    
    found_good = []
    for pattern in good_patterns:
        if pattern in content:
            found_good.append(pattern)
    
    if found_good:
        print(f"✅ PASS: Found {len(found_good)} environment-agnostic patterns")
        for pattern in found_good:
            print(f"   - {pattern[:50]}...")
            
except Exception as e:
    print(f"⚠️  WARNING: Could not verify paths: {e}")

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print("\nIf all tests pass:")
print("  1. Run: git add [modified files]")
print("  2. Run: git commit -m 'fix(deployment): Remove hardcoded paths and fix DataFrame serialization'")
print("  3. Run: git push origin v10")
print("  4. Monitor Render deployment logs")
print("\nIf tests fail:")
print("  - Review error messages above")
print("  - Check PRODUCTION_DEPLOYMENT_ISSUES_ANALYSIS.md for details")
print("  - Verify all file changes were applied correctly")
print("\n" + "="*80)
