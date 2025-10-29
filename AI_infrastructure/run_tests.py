r"""
Test Runner for AI Infrastructure

Quick command to run all tests and show results

Usage:
    cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
    python run_tests.py
"""

import subprocess
import sys


def run_tests():
    """Run all tests with pytest"""
    
    print("=" * 60)
    print("AI INFRASTRUCTURE TEST SUITE")
    print("=" * 60)
    print()
    
    # Add parent directory to path for imports
    import os
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Run pytest with verbose output
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
        capture_output=False
    )
    
    print()
    print("=" * 60)
    
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review docs/MIGRATION_GUIDE.md")
        print("2. Test side-by-side (see README.md)")
        print("3. Migrate when ready")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print()
        print("Please fix failing tests before migration.")
        return 1


def run_tests_with_coverage():
    """Run tests with coverage report"""
    
    print("=" * 60)
    print("AI INFRASTRUCTURE TEST SUITE (WITH COVERAGE)")
    print("=" * 60)
    print()
    
    result = subprocess.run(
        [
            sys.executable, '-m', 'pytest',
            'tests/', '-v',
            '--cov=core',
            '--cov-report=term-missing',
            '--tb=short'
        ],
        capture_output=False
    )
    
    print()
    print("=" * 60)
    
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AI Infrastructure tests')
    parser.add_argument('--coverage', action='store_true', help='Include coverage report')
    
    args = parser.parse_args()
    
    if args.coverage:
        sys.exit(run_tests_with_coverage())
    else:
        sys.exit(run_tests())
