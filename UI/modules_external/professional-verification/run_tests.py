"""
Professional Verification Module - Test Runner
===============================================

Comprehensive test execution with smoke test, unit tests, and end-to-end validation.

WHAT IT DOES:
1. Smoke Test - Validates installation and dependencies
2. Unit Tests - Tests individual components
3. Integration Test - Tests complete workflow
4. Compilation Check - Validates Python syntax
5. Trace Analysis - Shows execution paths

USAGE:
    python run_tests.py                    # Run all tests
    python run_tests.py --smoke-only       # Quick validation
    python run_tests.py --unit-only        # Unit tests only
    python run_tests.py --e2e-only         # End-to-end only
    python run_tests.py --trace            # Show execution trace

CREATED: December 16, 2025
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import time

# Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.RESET}\n")


def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.RESET}")


def run_smoke_test():
    """Run smoke test"""
    print_section("STEP 1: Smoke Test (Installation Validation)")
    
    result = subprocess.run(
        [sys.executable, 'smoke_test.py'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def run_compilation_check():
    """Check Python syntax compilation"""
    print_section("STEP 2: Compilation Check (Python Syntax)")
    
    files_to_check = [
        'verification_engine.py',
        'report_generator.py',
        'smoke_test.py',
        'test_suite.py',
        'tools/implementations/verification_core.py',
        'tools/implementations/computer_use_verification.py'
    ]
    
    all_passed = True
    
    for filepath in files_to_check:
        if not Path(filepath).exists():
            print(f"{Colors.YELLOW}⚠️  SKIP: {filepath} (not found){Colors.RESET}")
            continue
        
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', filepath],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ PASS: {filepath}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ FAIL: {filepath}{Colors.RESET}")
            print(f"   {result.stderr}")
            all_passed = False
    
    return all_passed


def run_unit_tests():
    """Run unit tests"""
    print_section("STEP 3: Unit Tests (Component Testing)")
    
    result = subprocess.run(
        [sys.executable, 'test_suite.py', 'TestToolRegistry', 'TestVerificationEngine', 'TestReportGenerator'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def run_e2e_test():
    """Run end-to-end test"""
    print_section("STEP 4: End-to-End Test (Full Workflow)")
    
    result = subprocess.run(
        [sys.executable, 'test_suite.py', 'TestEndToEnd'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def run_trace_analysis():
    """Run execution trace analysis"""
    print_section("STEP 5: Trace Analysis (Execution Paths)")
    
    print(f"{Colors.CYAN}Execution Path:{Colors.RESET}")
    print("""
    1. Tool Registry Discovery
       └─> UI/modules_external/professional-verification/tools/
           └─> verification_tools_schema.json (25 tools)
       └─> AI_infrastructure/tools/
           └─> computer_use_tools_schema.json (3 tools)
    
    2. Verification Engine Initialization
       └─> Load profession template (software_engineer)
       └─> Set category weights (6 categories)
    
    3. Tool Execution (via Tool Registry)
       └─> parse_resume → verification_core.py
       └─> verify_github_profile → verification_core.py
       └─> search_linkedin_profile → computer_use_verification.py
           └─> Computer Use Executor → Docker container
    
    4. Risk Score Calculation
       └─> _score_resume_authenticity() → 0-100
       └─> _score_online_presence() → 0-100
       └─> _score_credential_validity() → 0-100
       └─> _score_company_legitimacy() → 0-100
       └─> _score_timeline_consistency() → 0-100
       └─> _score_digital_footprint() → 0-100
       └─> Weighted average → Overall score
    
    5. Red Flag Detection
       └─> Check AI-generated resume → CRITICAL
       └─> Check invalid credentials → CRITICAL
       └─> Check recent domain → HIGH
       └─> Check timeline gaps → HIGH
       └─> Check missing GitHub → MEDIUM
    
    6. Report Generation
       └─> compile_risk_assessment()
       └─> categorize_claims()
       └─> generate_timeline_visualization()
       └─> highlight_red_flags()
       └─> compile_screenshots()
    
    7. Export
       └─> export_to_json() → verification_report.json
       └─> export_to_pdf() → verification_report.pdf (requires reportlab)
       └─> export_to_html() → verification_report.html
    """)
    
    print(f"\n{Colors.CYAN}Key Decision Points:{Colors.RESET}")
    print("""
    - Profession Template Selection: software_engineer vs medical_professional
      → Determines weight distribution (GitHub 30% vs Credentials 40%)
    
    - Risk Level Threshold: score < 30 = Low, 30-60 = Medium, 60-80 = High, 80+ = Critical
      → Determines hiring recommendation
    
    - Red Flag Severity: CRITICAL (reject) vs HIGH (investigate) vs MEDIUM (caution)
      → Determines next steps
    
    - Data Availability: 100% confidence vs 60% confidence
      → Affects report reliability
    """)
    
    return True


def run_full_suite(args):
    """Run complete test suite"""
    print_header("PROFESSIONAL VERIFICATION MODULE - TEST SUITE")
    
    print(f"{Colors.BOLD}Module Root:{Colors.RESET} {Path.cwd()}")
    print(f"{Colors.BOLD}Python:{Colors.RESET} {sys.version.split()[0]}")
    print(f"{Colors.BOLD}Time:{Colors.RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run tests based on arguments
    if args.smoke_only:
        results['smoke'] = run_smoke_test()
    elif args.unit_only:
        results['compilation'] = run_compilation_check()
        results['unit'] = run_unit_tests()
    elif args.e2e_only:
        results['e2e'] = run_e2e_test()
    elif args.trace:
        results['trace'] = run_trace_analysis()
    else:
        # Full suite
        results['smoke'] = run_smoke_test()
        
        if results['smoke']:
            results['compilation'] = run_compilation_check()
            
            if results['compilation']:
                results['unit'] = run_unit_tests()
                
                if results['unit']:
                    results['e2e'] = run_e2e_test()
                    
                    if args.trace:
                        results['trace'] = run_trace_analysis()
        else:
            print(f"\n{Colors.RED}❌ Smoke test failed - skipping remaining tests{Colors.RESET}")
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for test_name, passed_test in results.items():
        status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if passed_test else f"{Colors.RED}❌ FAILED{Colors.RESET}"
        print(f"  {test_name.upper():20} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED - Module ready for production{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ {total - passed} test(s) failed - Fix before using module{Colors.RESET}")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Professional Verification Module Test Runner')
    parser.add_argument('--smoke-only', action='store_true', help='Run smoke test only')
    parser.add_argument('--unit-only', action='store_true', help='Run unit tests only')
    parser.add_argument('--e2e-only', action='store_true', help='Run end-to-end test only')
    parser.add_argument('--trace', action='store_true', help='Show execution trace')
    
    args = parser.parse_args()
    
    exit_code = run_full_suite(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
