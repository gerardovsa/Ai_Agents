"""
Comprehensive API Endpoint Testing Script
Tests all major endpoints after database syntax fixes
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5001"
TEST_USER_ID = 14  # User from the error logs

# Test results tracking
results = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_endpoint(name, method, endpoint, data=None, params=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, params=params, timeout=10)
        
        if response.status_code == expected_status:
            results['passed'].append(name)
            print(f"{Fore.GREEN}✅ PASS{Style.RESET_ALL} | {name}")
            print(f"   Status: {response.status_code}")
            if response.text:
                try:
                    json_data = response.json()
                    if 'error' in json_data:
                        print(f"   {Fore.YELLOW}Warning: {json_data['error']}{Style.RESET_ALL}")
                    elif isinstance(json_data, dict) and len(json_data) > 0:
                        print(f"   Response keys: {list(json_data.keys())[:5]}")
                except:
                    print(f"   Response: {response.text[:100]}")
            return True
        else:
            results['failed'].append(name)
            print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} | {name}")
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        results['failed'].append(name)
        print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} | {name}")
        print(f"   Error: Cannot connect to {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        results['failed'].append(name)
        print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} | {name}")
        print(f"   Error: Request timeout")
        return False
    except Exception as e:
        results['failed'].append(name)
        print(f"{Fore.RED}❌ FAIL{Style.RESET_ALL} | {name}")
        print(f"   Error: {e}")
        return False


def main():
    print("=" * 80)
    print(f"{Fore.CYAN}API ENDPOINT TESTING - Database Syntax Fix Verification{Style.RESET_ALL}")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # ============================================================================
    # CRITICAL FIXES - Thread & Message Operations
    # ============================================================================
    print(f"\n{Fore.YELLOW}[CRITICAL FIXES]{Style.RESET_ALL} Thread & Message Operations")
    print("-" * 80)
    
    test_endpoint(
        "Thread List (PRIMARY FIX)",
        "GET", 
        "/api/threads/list",
        params={'user_id': TEST_USER_ID}
    )
    
    test_endpoint(
        "Thread Create",
        "POST",
        "/api/threads/create",
        data={'user_id': TEST_USER_ID, 'title': 'API Test Thread'}
    )
    
    test_endpoint(
        "Thread Search",
        "GET",
        "/api/threads/search",
        params={'user_id': TEST_USER_ID, 'query': 'test'}
    )
    
    # ============================================================================
    # CORE INFRASTRUCTURE
    # ============================================================================
    print(f"\n{Fore.YELLOW}[CORE INFRASTRUCTURE]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "Health Check",
        "GET",
        "/health"
    )
    
    test_endpoint(
        "Database Status",
        "GET",
        "/api/database/status"
    )
    
    # ============================================================================
    # USER & AUTHENTICATION
    # ============================================================================
    print(f"\n{Fore.YELLOW}[USER & AUTHENTICATION]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "User Profile",
        "GET",
        "/api/users/profile",
        params={'user_id': TEST_USER_ID}
    )
    
    test_endpoint(
        "User Sessions",
        "GET",
        "/api/users/sessions",
        params={'user_id': TEST_USER_ID}
    )
    
    # ============================================================================
    # AGENT OPERATIONS
    # ============================================================================
    print(f"\n{Fore.YELLOW}[AGENT OPERATIONS]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "Agent List",
        "GET",
        "/api/agents/list"
    )
    
    test_endpoint(
        "Agent Status",
        "GET",
        "/api/agents/status"
    )
    
    # ============================================================================
    # PROMPT LIBRARY (AUTOINCREMENT FIX)
    # ============================================================================
    print(f"\n{Fore.YELLOW}[PROMPT LIBRARY - AUTOINCREMENT FIX]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "Prompt Library List",
        "GET",
        "/api/prompts/list",
        params={'user_id': TEST_USER_ID}
    )
    
    test_endpoint(
        "Prompt Library Create",
        "POST",
        "/api/prompts/create",
        data={
            'user_id': TEST_USER_ID,
            'name': 'API Test Prompt',
            'category': 'test',
            'prompt_text': 'Test prompt text',
            'type': 'quick_action'
        }
    )
    
    # ============================================================================
    # MODULE ENDPOINTS
    # ============================================================================
    print(f"\n{Fore.YELLOW}[MODULE ENDPOINTS]{Style.RESET_ALL}")
    print("-" * 80)
    
    # Stock Management
    test_endpoint(
        "Stock Management - Usage Analytics",
        "GET",
        "/api/stock-management/usage-analytics",
        params={'days': 30}
    )
    
    test_endpoint(
        "Stock Management - Hierarchy",
        "GET",
        "/api/stock-management/hierarchy"
    )
    
    # Shopify
    test_endpoint(
        "Shopify - Dashboard Metrics",
        "GET",
        "/api/shopify/dashboard/metrics"
    )
    
    # Kanban
    test_endpoint(
        "Kanban - Jobs List",
        "GET",
        "/api/kanban/jobs"
    )
    
    # Quote Calculator
    test_endpoint(
        "Quote Calculator - Stock List",
        "GET",
        "/api/quote-calculator/stocks"
    )
    
    # ============================================================================
    # SYNERGY FEATURES
    # ============================================================================
    print(f"\n{Fore.YELLOW}[SYNERGY FEATURES]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "Synergy Cards List",
        "GET",
        "/api/synergy/cards",
        params={'user_id': TEST_USER_ID}
    )
    
    test_endpoint(
        "Synergy Sessions List",
        "GET",
        "/api/synergy/sessions",
        params={'user_id': TEST_USER_ID}
    )
    
    # ============================================================================
    # AUTOMATION & WORKFLOWS
    # ============================================================================
    print(f"\n{Fore.YELLOW}[AUTOMATION & WORKFLOWS]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "Automation List",
        "GET",
        "/api/automation/list",
        params={'user_id': TEST_USER_ID}
    )
    
    test_endpoint(
        "Workflow Templates",
        "GET",
        "/api/automation/templates"
    )
    
    # ============================================================================
    # DEVICE & SECURITY
    # ============================================================================
    print(f"\n{Fore.YELLOW}[DEVICE & SECURITY]{Style.RESET_ALL}")
    print("-" * 80)
    
    test_endpoint(
        "Device Lock Status",
        "GET",
        "/api/device-lock/status",
        params={'user_id': TEST_USER_ID}
    )
    
    # ============================================================================
    # RESULTS SUMMARY
    # ============================================================================
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}TEST RESULTS SUMMARY{Style.RESET_ALL}")
    print("=" * 80)
    
    total = len(results['passed']) + len(results['failed']) + len(results['skipped'])
    pass_rate = (len(results['passed']) / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tests: {total}")
    print(f"{Fore.GREEN}Passed: {len(results['passed'])} ({pass_rate:.1f}%){Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {len(results['failed'])}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Skipped: {len(results['skipped'])}{Style.RESET_ALL}")
    
    if results['failed']:
        print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
        for test in results['failed']:
            print(f"  ❌ {test}")
    
    print("\n" + "=" * 80)
    
    # Success criteria
    critical_tests = [
        "Thread List (PRIMARY FIX)",
        "Prompt Library List",
        "Health Check"
    ]
    
    critical_passed = all(test in results['passed'] for test in critical_tests)
    
    if critical_passed and pass_rate >= 70:
        print(f"{Fore.GREEN}✅ SUCCESS: Critical fixes verified!{Style.RESET_ALL}")
        print(f"   Thread loading: WORKING")
        print(f"   Prompt library: WORKING")
        print(f"   Overall health: GOOD")
    elif critical_passed:
        print(f"{Fore.YELLOW}⚠️  PARTIAL SUCCESS: Critical fixes work, but some endpoints failed{Style.RESET_ALL}")
        print(f"   Thread loading: WORKING")
        print(f"   Prompt library: WORKING")
        print(f"   Some modules may need attention")
    else:
        print(f"{Fore.RED}❌ FAILURE: Critical tests failed{Style.RESET_ALL}")
        print(f"   Please check Flask logs for errors")
    
    print("=" * 80)
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"api_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'base_url': BASE_URL,
            'test_user_id': TEST_USER_ID,
            'results': results,
            'summary': {
                'total': total,
                'passed': len(results['passed']),
                'failed': len(results['failed']),
                'skipped': len(results['skipped']),
                'pass_rate': pass_rate
            }
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")


if __name__ == '__main__':
    main()
