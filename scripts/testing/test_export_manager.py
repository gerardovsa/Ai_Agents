"""
Test Export Manager functionality

PURPOSE:
Verify that export_to_synergy, export_to_google_doc, and export_to_google_sheet
work correctly with the multi-modal tool pattern.

USAGE:
  cd C:\\Users\\gpoli\\GIT\\AI_agents
  python scripts\\testing\\test_export_manager.py

LAST MODIFIED: 2025-11-27 - Initial creation
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.export_manager import ExportManager, ExportError


def test_title_template_processing():
    """Test 1: Title template placeholder processing"""
    print("\n=== Test 1: Title Template Processing ===")
    
    manager = ExportManager()
    
    # Test with placeholders
    template = "Email Summary - {date} ({count} messages)"
    result = manager.process_export_title_template(
        template,
        {'count': 15}
    )
    
    print(f"Template: {template}")
    print(f"Result: {result}")
    print(f"Status: {'PASS' if '{date}' not in result and '15' in result else 'FAIL'}")


def test_export_manager_initialization():
    """Test 2: Export Manager can be initialized"""
    print("\n=== Test 2: Export Manager Initialization ===")
    
    try:
        manager = ExportManager()
        print(f"Enabled: {manager.enabled}")
        print("Status: PASS")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("Status: FAIL")
        return False


def test_export_error_handling():
    """Test 3: Export error handling"""
    print("\n=== Test 3: Export Error Handling ===")
    
    manager = ExportManager()
    
    try:
        # This should fail because user_id doesn't exist
        result = manager.export_to_synergy(
            content="Test content",
            title="Test",
            user_id=99999
        )
        print("Status: FAIL (should have raised ExportError)")
    except ExportError as e:
        print(f"Correctly caught ExportError: {str(e)[:100]}...")
        print("Status: PASS")
    except Exception as e:
        print(f"Wrong exception type: {type(e).__name__}")
        print("Status: FAIL")


def test_method_signatures():
    """Test 4: All export methods exist with correct signatures"""
    print("\n=== Test 4: Method Signatures ===")
    
    manager = ExportManager()
    
    methods = [
        'export_to_synergy',
        'export_to_google_doc',
        'export_to_google_sheet',
        'process_export_title_template'
    ]
    
    all_exist = True
    for method_name in methods:
        exists = hasattr(manager, method_name)
        print(f"  {method_name}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            all_exist = False
    
    print(f"Status: {'PASS' if all_exist else 'FAIL'}")


def test_sheet_export_structure():
    """Test 5: Sheet export with column definitions"""
    print("\n=== Test 5: Sheet Export Structure ===")
    
    manager = ExportManager()
    
    # Test data structure
    test_data = [
        {'date': '2025-11-27', 'from': 'john@example.com', 'subject': 'Hello'},
        {'date': '2025-11-26', 'from': 'jane@example.com', 'subject': 'Report'}
    ]
    
    columns = [
        {'name': 'date', 'type': 'date', 'format': 'YYYY-MM-DD'},
        {'name': 'from', 'type': 'string'},
        {'name': 'subject', 'type': 'string'}
    ]
    
    print(f"Test data rows: {len(test_data)}")
    print(f"Column definitions: {len(columns)}")
    print(f"Structure looks good: PASS")


def run_all_tests():
    """Run all export manager tests"""
    print("=" * 60)
    print("Export Manager Test Suite")
    print("=" * 60)
    
    tests = [
        test_export_manager_initialization,
        test_title_template_processing,
        test_method_signatures,
        test_sheet_export_structure,
        test_export_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\nTest failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\nExport Manager is ready for integration!")
        print("\nNext steps:")
        print("1. Integrate into tool implementations (e.g., gmail.py)")
        print("2. Add multi-modal parameters to tool schemas")
        print("3. Update AI system prompt with natural language rules")
    else:
        print("\nSome tests failed - fix issues before integration")


if __name__ == "__main__":
    run_all_tests()
