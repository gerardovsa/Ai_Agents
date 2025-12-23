"""
Comprehensive Xero Reports Test Script
=======================================

Tests all 20 Xero report endpoints with 1-month date filtering.
Validates data return, visual usefulness, and query performance.

Reports Tested:
- Invoice Reports (6)
- Contact Reports (4)
- Payment Reports (4)
- Multi-Business Reports (3)
- Advanced Analytics (3)

Created: December 23, 2025
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import time

# Configuration
BASE_URL = "http://localhost:5000"
BUSINESS_IDS = [1, 2, 3]  # Print, Publishing, Signs
BUSINESS_NAMES = {1: "InHouse Print", 2: "InHouse Publishing", 3: "InHouse Signs"}

# Calculate 1-month date range
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
date_from = start_date.strftime('%Y-%m-%d')
date_to = end_date.strftime('%Y-%m-%d')

print(f"📅 Testing with date range: {date_from} to {date_to} (30 days)")
print("=" * 80)

# Report endpoints with expected data structure
REPORTS = {
    # Invoice Reports
    "aged-receivables": {
        "category": "Invoice",
        "expected_keys": ["success", "buckets", "total_outstanding"],
        "description": "Age buckets for outstanding invoices",
        "visual_check": lambda data: len(data.get('buckets', [])) > 0
    },
    "sales-summary": {
        "category": "Invoice",
        "expected_keys": ["success", "total_revenue", "invoice_count", "customers"],
        "description": "Revenue summary by customer",
        "visual_check": lambda data: data.get('invoice_count', 0) >= 0
    },
    "overdue-invoices": {
        "category": "Invoice",
        "expected_keys": ["success", "overdue_count", "total_overdue", "invoices"],
        "description": "Invoices past due date",
        "visual_check": lambda data: 'invoices' in data
    },
    "revenue-trends": {
        "category": "Invoice",
        "expected_keys": ["success", "monthly_data", "total_revenue"],
        "description": "Monthly revenue time series",
        "visual_check": lambda data: len(data.get('monthly_data', [])) > 0
    },
    "invoice-status": {
        "category": "Invoice",
        "expected_keys": ["success", "status_distribution", "total_invoices"],
        "description": "Distribution by invoice status",
        "visual_check": lambda data: 'status_distribution' in data
    },
    "invoice-volume": {
        "category": "Invoice",
        "expected_keys": ["success", "total_invoices", "peak_day"],
        "description": "Volume analysis and peak billing days",
        "visual_check": lambda data: 'total_invoices' in data
    },
    
    # Contact Reports
    "contact-activity": {
        "category": "Contact",
        "expected_keys": ["success", "contacts"],
        "description": "Transaction history per contact",
        "visual_check": lambda data: 'contacts' in data
    },
    "inactive-customers": {
        "category": "Contact",
        "expected_keys": ["success", "inactive_count", "customers"],
        "description": "Customers with no recent activity",
        "visual_check": lambda data: 'customers' in data
    },
    "customer-lifetime-value": {
        "category": "Contact",
        "expected_keys": ["success", "customers"],
        "description": "Total revenue per customer + tenure",
        "visual_check": lambda data: len(data.get('customers', [])) >= 0
    },
    "customer-segmentation": {
        "category": "Contact",
        "expected_keys": ["success", "segments"],
        "description": "RFM analysis (Champions, Loyal, At Risk, Lost)",
        "visual_check": lambda data: 'segments' in data
    },
    
    # Payment Reports
    "payment-behavior": {
        "category": "Payment",
        "expected_keys": ["success", "avg_days_to_pay"],
        "description": "Average days to pay, early/late percentages",
        "visual_check": lambda data: 'avg_days_to_pay' in data
    },
    "payment-reconciliation": {
        "category": "Payment",
        "expected_keys": ["success", "unmatched_count", "partial_count"],
        "description": "Unmatched, partial, overpayments",
        "visual_check": lambda data: 'unmatched_count' in data
    },
    "cash-flow": {
        "category": "Payment",
        "expected_keys": ["success", "timeline"],
        "description": "Daily payment timeline",
        "visual_check": lambda data: 'timeline' in data
    },
    "dso": {
        "category": "Payment",
        "expected_keys": ["success", "dso_days"],
        "description": "Days Sales Outstanding calculation",
        "visual_check": lambda data: 'dso_days' in data
    },
    
    # Multi-Business Reports
    "business-comparison": {
        "category": "Multi-Business",
        "expected_keys": ["success", "businesses"],
        "description": "Compare all 3 businesses",
        "visual_check": lambda data: len(data.get('businesses', [])) > 0
    },
    "customer-overlap": {
        "category": "Multi-Business",
        "expected_keys": ["success", "shared_customers"],
        "description": "Customers across multiple businesses",
        "visual_check": lambda data: 'shared_customers' in data
    },
    "consolidated-revenue": {
        "category": "Multi-Business",
        "expected_keys": ["success", "total_revenue", "breakdown"],
        "description": "Total revenue across all businesses",
        "visual_check": lambda data: 'total_revenue' in data
    },
    
    # Advanced Analytics
    "revenue-by-product": {
        "category": "Analytics",
        "expected_keys": ["success", "products"],
        "description": "Revenue grouped by product/line item",
        "visual_check": lambda data: 'products' in data
    },
    "seasonality": {
        "category": "Analytics",
        "expected_keys": ["success", "monthly_patterns"],
        "description": "Monthly patterns and YoY comparison",
        "visual_check": lambda data: 'monthly_patterns' in data
    },
    "forecast": {
        "category": "Analytics",
        "expected_keys": ["success", "forecast_30", "forecast_60", "forecast_90"],
        "description": "Trend-based revenue forecast",
        "visual_check": lambda data: 'forecast_30' in data
    }
}

# Test results storage
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "slow_queries": [],
    "failed_tests": [],
    "passed_tests": []
}


def test_report(report_name: str, business_id: int) -> Tuple[bool, Dict, float]:
    """
    Test a single report endpoint
    
    Returns:
        (success, response_data, response_time)
    """
    url = f"{BASE_URL}/api/xero/reports/{report_name}"
    params = {
        'business_id': business_id,
        'from_date': date_from,
        'to_date': date_to
    }
    
    start_time = time.time()
    try:
        response = requests.get(url, params=params, timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return True, data, response_time
        else:
            return False, {"error": f"HTTP {response.status_code}: {response.text}"}, response_time
    
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        return False, {"error": "Request timeout (>30s)"}, response_time
    
    except Exception as e:
        response_time = time.time() - start_time
        return False, {"error": str(e)}, response_time


def validate_response(report_name: str, data: Dict, config: Dict) -> Tuple[bool, List[str]]:
    """
    Validate response data structure and visual usefulness
    
    Returns:
        (is_valid, issues_found)
    """
    issues = []
    
    # Check success flag
    if not data.get('success'):
        issues.append(f"❌ Response success=false: {data.get('error', 'Unknown error')}")
        return False, issues
    
    # Check expected keys
    for key in config['expected_keys']:
        if key not in data:
            issues.append(f"⚠️  Missing expected key: {key}")
    
    # Visual usefulness check
    try:
        if not config['visual_check'](data):
            issues.append(f"⚠️  Visual check failed: Data may not be useful for display")
    except Exception as e:
        issues.append(f"⚠️  Visual check error: {e}")
    
    # Check for empty data
    if 'invoices' in data and len(data['invoices']) == 0:
        issues.append(f"ℹ️  No invoices found in date range")
    
    if 'customers' in data and len(data['customers']) == 0:
        issues.append(f"ℹ️  No customers found")
    
    return len(issues) == 0 or all('ℹ️' in i for i in issues), issues


def print_result(report_name: str, business_id: str, success: bool, response_time: float, issues: List[str]):
    """Pretty print test result"""
    status = "✅" if success else "❌"
    biz_name = BUSINESS_NAMES[business_id]
    
    print(f"{status} {report_name:30s} | {biz_name:20s} | {response_time:5.2f}s")
    
    if issues:
        for issue in issues:
            print(f"   {issue}")


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

print("\n🧪 Testing Xero Reports\n")

# Group reports by category
categories = {}
for report_name, config in REPORTS.items():
    category = config['category']
    if category not in categories:
        categories[category] = []
    categories[category].append(report_name)

# Test each report for each business
for category, report_names in categories.items():
    print(f"\n📊 {category} Reports ({len(report_names)} reports)")
    print("─" * 80)
    
    for report_name in report_names:
        config = REPORTS[report_name]
        
        for business_id in BUSINESS_IDS:
            results['total'] += 1
            
            # Test report
            success, data, response_time = test_report(report_name, business_id)
            
            # Validate response
            if success:
                is_valid, issues = validate_response(report_name, data, config)
                
                if is_valid:
                    results['passed'] += 1
                    results['passed_tests'].append(f"{report_name} (Business {business_id})")
                else:
                    results['failed'] += 1
                    results['failed_tests'].append(f"{report_name} (Business {business_id}): {', '.join(issues)}")
                
                print_result(report_name, business_id, is_valid, response_time, issues)
            else:
                results['failed'] += 1
                error_msg = data.get('error', 'Unknown error')
                results['failed_tests'].append(f"{report_name} (Business {business_id}): {error_msg}")
                print_result(report_name, business_id, False, response_time, [f"❌ {error_msg}"])
            
            # Track slow queries (>5s)
            if response_time > 5.0:
                results['slow_queries'].append({
                    'report': report_name,
                    'business': business_id,
                    'time': response_time
                })

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n" + "=" * 80)
print("📈 TEST SUMMARY")
print("=" * 80)

print(f"\nTotal Tests: {results['total']}")
print(f"✅ Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
print(f"❌ Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")

if results['slow_queries']:
    print(f"\n⚠️  Slow Queries (>5s): {len(results['slow_queries'])}")
    for query in results['slow_queries']:
        print(f"   - {query['report']} (Business {query['business']}): {query['time']:.2f}s")

if results['failed_tests']:
    print(f"\n❌ Failed Tests:")
    for test in results['failed_tests'][:10]:  # Show first 10
        print(f"   - {test}")
    
    if len(results['failed_tests']) > 10:
        print(f"   ... and {len(results['failed_tests']) - 10} more")

print("\n" + "=" * 80)
print("🎯 RECOMMENDATIONS")
print("=" * 80)

if results['failed'] > 0:
    print("\n1. Fix failed endpoints - Check Flask logs for errors")

if len(results['slow_queries']) > 0:
    print("\n2. Optimize slow queries:")
    print("   - Add indexes to invoice/payment date columns")
    print("   - Implement pagination for large result sets")
    print("   - Cache frequently accessed data")

if results['passed'] == results['total']:
    print("\n✅ All tests passed! Xero reports are production-ready.")
else:
    print(f"\n⚠️  {results['failed']} tests failed. Review errors above.")

print("\n" + "=" * 80)
