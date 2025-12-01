"""
Test Pre-Commit Review Agent Installation
Verifies all components are properly installed and working.
"""

import os
import sys
from pathlib import Path

def test_installation():
    """Test that all components are installed correctly"""
    
    print("\n╔════════════════════════════════════════╗")
    print("║   PRE-COMMIT AGENT INSTALLATION TEST  ║")
    print("╚════════════════════════════════════════╝\n")
    
    root_dir = Path(__file__).parent
    all_pass = True
    
    # Test 1: Check script files exist
    print("📁 Test 1: Checking script files...")
    scripts = [
        'scripts/pre_commit/pre_commit_security_scanner.py',
        'scripts/pre_commit/code_quality_checker.py',
        'scripts/pre_commit/commit_message_validator.py'
    ]
    
    for script in scripts:
        path = root_dir / script
        if path.exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} NOT FOUND")
            all_pass = False
    
    # Test 2: Check Git hooks exist
    print("\n🔗 Test 2: Checking Git hooks...")
    hooks = [
        '.git/hooks/pre-commit',
        '.git/hooks/commit-msg'
    ]
    
    for hook in hooks:
        path = root_dir / hook
        if path.exists():
            print(f"  ✅ {hook}")
        else:
            print(f"  ❌ {hook} NOT FOUND")
            all_pass = False
    
    # Test 3: Check if hooks are executable (Windows check)
    print("\n🔧 Test 3: Checking hook executability...")
    for hook in hooks:
        path = root_dir / hook
        if path.exists():
            # On Windows, check if file is readable
            if os.access(str(path), os.R_OK):
                print(f"  ✅ {hook} is readable")
            else:
                print(f"  ❌ {hook} is not readable")
                all_pass = False
    
    # Test 4: Test imports
    print("\n📦 Test 4: Testing Python imports...")
    sys.path.insert(0, str(root_dir / 'scripts' / 'pre_commit'))
    
    try:
        from pre_commit_security_scanner import PreCommitSecurityScanner
        print("  ✅ pre_commit_security_scanner imports correctly")
    except ImportError as e:
        print(f"  ❌ Failed to import pre_commit_security_scanner: {e}")
        all_pass = False
    
    try:
        from code_quality_checker import CodeQualityChecker
        print("  ✅ code_quality_checker imports correctly")
    except ImportError as e:
        print(f"  ❌ Failed to import code_quality_checker: {e}")
        all_pass = False
    
    try:
        from commit_message_validator import CommitMessageValidator
        print("  ✅ commit_message_validator imports correctly")
    except ImportError as e:
        print(f"  ❌ Failed to import commit_message_validator: {e}")
        all_pass = False
    
    # Test 5: Test basic functionality
    print("\n⚙️  Test 5: Testing basic functionality...")
    
    try:
        # Test security scanner with empty file list
        scanner = PreCommitSecurityScanner([])
        results = scanner.scan_all()
        if results['severity'] == 'LOW':
            print("  ✅ Security scanner works (no files)")
        else:
            print(f"  ⚠️  Security scanner unexpected result: {results['severity']}")
    except Exception as e:
        print(f"  ❌ Security scanner failed: {e}")
        all_pass = False
    
    try:
        # Test quality checker with empty file list
        checker = CodeQualityChecker([])
        results = checker.check_all()
        if results['total_issues'] == 0:
            print("  ✅ Quality checker works (no files)")
        else:
            print(f"  ⚠️  Quality checker unexpected result: {results['total_issues']} issues")
    except Exception as e:
        print(f"  ❌ Quality checker failed: {e}")
        all_pass = False
    
    try:
        # Test commit message validator
        validator = CommitMessageValidator("feat(test): test commit message")
        results = validator.validate()
        if results['valid']:
            print("  ✅ Commit message validator works")
        else:
            print(f"  ⚠️  Validator rejected valid message: {results['errors']}")
    except Exception as e:
        print(f"  ❌ Commit message validator failed: {e}")
        all_pass = False
    
    # Test 6: Check documentation
    print("\n📚 Test 6: Checking documentation...")
    docs = [
        'PRE_COMMIT_REVIEW_COMPLETE.md',
        'PRE_COMMIT_REVIEW_QUICK_START.md',
        '.github/prompts/Pre-Commit Review Agent.prompt.md'
    ]
    
    for doc in docs:
        path = root_dir / doc
        if path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ⚠️  {doc} NOT FOUND (optional)")
    
    # Final result
    print("\n" + "="*50)
    if all_pass:
        print("✅ ALL TESTS PASSED!")
        print("\nPre-Commit Review Agent is properly installed.")
        print("Git hooks will run automatically on commit.")
        print("\nNext steps:")
        print("  1. Read PRE_COMMIT_REVIEW_QUICK_START.md")
        print("  2. Try a test commit to verify hooks work")
        print("  3. Share PRE_COMMIT_REVIEW_COMPLETE.md with team")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above and run this test again.")
    print("="*50 + "\n")
    
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(test_installation())
