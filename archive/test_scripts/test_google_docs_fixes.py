"""
Test Google Docs Tools Fixes
=============================

Verifies that both fixed tools can be imported and have correct dependencies.

Run this to verify fixes before restarting Flask.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_markdown_v2_imports():
    """Test that google_docs_smart_create_from_markdown_v2 has correct imports"""
    print("Testing google_docs_smart_create_from_markdown_v2 imports...")
    print("=" * 70)
    
    try:
        import inspect
        from google_workspace import google_docs
        
        # Get function source
        func = google_docs.google_docs_smart_create_from_markdown_v2
        source = inspect.getsource(func)
        
        # Check for broken import
        has_broken_import = 'from tools.implementations.microsoft_word_tools import _parse_markdown_to_docx' in source
        
        # Check for inline parser
        has_inline_parser = 'lines = markdown_content.strip().split' in source
        has_docx_imports = 'from docx.shared import' in source or 'from docx.enum.text import' in source
        
        print(f"\n{'Status':<30} {'Result':<15}")
        print("-" * 45)
        print(f"{'Broken import removed':<30} {'✅ YES' if not has_broken_import else '❌ NO':<15}")
        print(f"{'Inline parser added':<30} {'✅ YES' if has_inline_parser else '❌ NO':<15}")
        print(f"{'DOCX imports present':<30} {'✅ YES' if has_docx_imports else '❌ NO':<15}")
        
        if not has_broken_import and has_inline_parser and has_docx_imports:
            print(f"\n✅ google_docs_smart_create_from_markdown_v2 FIXED!")
            print("   - No broken imports")
            print("   - Inline markdown parser implemented")
            print("   - Uses python-docx directly")
            return True
        else:
            print(f"\n❌ google_docs_smart_create_from_markdown_v2 NOT FULLY FIXED")
            if has_broken_import:
                print("   ⚠️  Still has broken import from microsoft_word_tools")
            if not has_inline_parser:
                print("   ⚠️  Missing inline parser implementation")
            if not has_docx_imports:
                print("   ⚠️  Missing docx imports")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_generate_openai():
    """Test that google_docs_ai_smart_generate_document uses new OpenAI API"""
    print("\n\nTesting google_docs_ai_smart_generate_document OpenAI API...")
    print("=" * 70)
    
    try:
        import inspect
        from google_workspace import google_docs
        
        # Get function source
        func = google_docs.google_docs_ai_smart_generate_document
        source = inspect.getsource(func)
        
        # Check for old API
        has_old_import = 'import openai' in source and 'from openai import OpenAI' not in source
        has_old_api_key = 'openai.api_key =' in source
        has_old_completion = 'openai.ChatCompletion.create' in source
        
        # Check for new API
        has_new_import = 'from openai import OpenAI' in source
        has_new_client = 'client = OpenAI(' in source or 'OpenAI(api_key=' in source
        has_new_completion = 'client.chat.completions.create' in source
        
        print(f"\n{'Status':<35} {'Result':<15}")
        print("-" * 50)
        print(f"{'Old API removed:':<35}")
        print(f"  - import openai (old style){'  ':<13} {'✅ REMOVED' if not has_old_import else '❌ STILL PRESENT':<15}")
        print(f"  - openai.api_key = ...{'  ':<13} {'✅ REMOVED' if not has_old_api_key else '❌ STILL PRESENT':<15}")
        print(f"  - openai.ChatCompletion{'  ':<13} {'✅ REMOVED' if not has_old_completion else '❌ STILL PRESENT':<15}")
        print(f"\n{'New API added:':<35}")
        print(f"  - from openai import OpenAI{'  ':<8} {'✅ PRESENT' if has_new_import else '❌ MISSING':<15}")
        print(f"  - client = OpenAI(...){'  ':<13} {'✅ PRESENT' if has_new_client else '❌ MISSING':<15}")
        print(f"  - client.chat.completions{'  ':<11} {'✅ PRESENT' if has_new_completion else '❌ MISSING':<15}")
        
        old_api_removed = not (has_old_import or has_old_api_key or has_old_completion)
        new_api_added = has_new_import and has_new_client and has_new_completion
        
        if old_api_removed and new_api_added:
            print(f"\n✅ google_docs_ai_smart_generate_document FIXED!")
            print("   - Migrated to OpenAI v1.0+ API")
            print("   - Uses OpenAI client pattern")
            print("   - No deprecated syntax")
            return True
        else:
            print(f"\n❌ google_docs_ai_smart_generate_document NOT FULLY FIXED")
            if not old_api_removed:
                print("   ⚠️  Still has old OpenAI v0.28 syntax")
            if not new_api_added:
                print("   ⚠️  Missing new OpenAI v1.0+ client API")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_version():
    """Check installed OpenAI version"""
    print("\n\nChecking OpenAI library version...")
    print("=" * 70)
    
    try:
        import openai
        version = openai.__version__
        
        major_version = int(version.split('.')[0])
        
        print(f"\nInstalled OpenAI version: {version}")
        
        if major_version >= 1:
            print("✅ OpenAI v1.0+ detected (new client API required)")
            print("   - Old syntax: openai.ChatCompletion.create() ❌")
            print("   - New syntax: OpenAI().chat.completions.create() ✅")
            return True
        else:
            print("⚠️  OpenAI v0.28 detected (old API)")
            print("   Consider upgrading: pip install --upgrade openai")
            return False
    
    except Exception as e:
        print(f"⚠️  Could not check OpenAI version: {e}")
        return False


def main():
    """Run all tests"""
    print("Google Docs Tools Fix - Verification")
    print("=" * 70)
    print("Checking fixes for:")
    print("  1. google_docs_smart_create_from_markdown_v2 (ImportError)")
    print("  2. google_docs_ai_smart_generate_document (OpenAI API)")
    print("=" * 70)
    print()
    
    results = []
    
    # Test 1: Markdown V2 imports
    results.append(("Markdown V2 Fix", test_markdown_v2_imports()))
    
    # Test 2: AI Generate OpenAI API
    results.append(("AI Generate OpenAI Fix", test_ai_generate_openai()))
    
    # Test 3: OpenAI version check
    results.append(("OpenAI Version Check", test_openai_version()))
    
    # Final summary
    print("\n\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<35} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 SUCCESS! All fixes verified!")
        print("\nNext steps:")
        print("  1. Restart Flask server: BISTART")
        print("  2. Test markdown document creation")
        print("  3. Test AI document generation")
        print("  4. Verify no errors")
        return 0
    else:
        print("⚠️  ISSUES FOUND - Review output above")
        print("\nFailed tests need attention before deployment")
        return 1


if __name__ == '__main__':
    exit(main())
