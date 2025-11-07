r"""
AI Infrastructure - Quick Verification Script

Verifies all files exist and basic imports work

Run:
    cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
    python verify_setup.py
"""

import os
import sys


def verify_setup():
    """Verify all required files exist"""
    
    print("=" * 60)
    print("AI INFRASTRUCTURE - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    # Required files
    required_files = [
        'core/__init__.py',
        'core/unified_session_manager.py',
        'core/unified_anthropic_client.py',
        'tests/__init__.py',
        'tests/test_session_manager.py',
        'tests/test_anthropic_client.py',
        'tests/test_integration.py',
        'docs/MIGRATION_GUIDE.md',
        'docs/API_REFERENCE.md',
        'docs/IMPLEMENTATION_SUMMARY.md',
        'flask_integration.py',
        'requirements.txt',
        'run_tests.py',
        'README.md'
    ]
    
    print("Checking files...")
    all_exist = True
    
    for filepath in required_files:
        exists = os.path.exists(filepath)
        status = "" if exists else ""
        print(f"{status} {filepath}")
        
        if not exists:
            all_exist = False
    
    print()
    
    if not all_exist:
        print(" FAILED - Some files are missing!")
        print("Please ensure all files were created correctly.")
        return False
    
    print(" All files exist!")
    print()
    
    # Verify imports
    print("Checking imports...")
    
    try:
        from core.unified_session_manager import UnifiedSessionManager, session_manager
        print(" UnifiedSessionManager imported")
    except ImportError as e:
        print(f" Failed to import UnifiedSessionManager: {e}")
        return False
    
    try:
        from core.unified_anthropic_client import UnifiedAnthropicClient
        print(" UnifiedAnthropicClient imported")
    except ImportError as e:
        print(f" Failed to import UnifiedAnthropicClient: {e}")
        return False
    
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    
    try:
        import anthropic
        print(" anthropic installed")
    except ImportError:
        print("⚠️  anthropic not installed - run: pip install anthropic")
    
    try:
        import pytest
        print(" pytest installed")
    except ImportError:
        print("⚠️  pytest not installed - run: pip install pytest pytest-asyncio")
    
    print()
    print("=" * 60)
    print(" SETUP VERIFICATION COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run tests: python run_tests.py")
    print("3. Review README.md for usage examples")
    print("4. Review docs/MIGRATION_GUIDE.md for migration steps")
    print()
    
    return True


if __name__ == '__main__':
    success = verify_setup()
    sys.exit(0 if success else 1)
