"""
Xero Tools Test Report Generator
Generates comprehensive test report with tool validations and results
"""

import sys
from datetime import datetime
from tools.implementations.xero import (
    xero_get_contacts, 
    xero_get_contact_by_id,
    xero_get_invoices,
    xero_get_payments,
    xero_get_accounts
)
from tools.implementations.xero_quotes import (
    xero_list_quotes,
    xero_get_quote_by_id,
    xero_get_branding_themes
)

# Output file
OUTPUT_FILE = r"C:\Users\gpoli\GIT\AI_agents\UI\modules_external\xero\test_results\test_report.txt"

class TestReport:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def run_test(self, name, func, *args, **kwargs):
        """Run a test and record results"""
        self.tests_run += 1
        result = {
            'name': name,
            'status': 'PENDING',
            'error': None,
            'data': None,
            'params': kwargs
        }
        
        try:
            data = func(*args, **kwargs)
            if data.get('success'):
                result['status'] = 'PASS'
                result['data'] = data
                self.tests_passed += 1
            else:
                result['status'] = 'FAIL'
                result['error'] = data.get('error', 'Unknown error')
                self.tests_failed += 1
        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)
            self.tests_failed += 1
        
        self.results.append(result)
        return result

def write_header(f, report):
    """Write report header"""
    f.write("╔" + "═"*98 + "╗\n")
    f.write("║" + " "*98 + "║\n")
    f.write("║" + "XERO TOOLS TEST REPORT".center(98) + "║\n")
    f.write("║" + " "*98 + "║\n")
    f.write("╚" + "═"*98 + "╝\n\n")
    
    f.write(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"🐍 Python: {sys.version.split()[0]}\n")
    f.write(f"📦 Business: InHouse Print (ID: 1)\n")
    f.write("\n" + "─"*100 + "\n\n")

def write_summary(f, report):
    """Write test summary"""
    f.write("╔" + "═"*98 + "╗\n")
    f.write("║" + "TEST EXECUTION SUMMARY".center(98) + "║\n")
    f.write("╚" + "═"*98 + "╝\n\n")
    
    total = report.tests_run
    passed = report.tests_passed
    failed = report.tests_failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    f.write(f"  📊 Tests Run:    {total:>3}\n")
    f.write(f"  ✅ Passed:       {passed:>3}\n")
    f.write(f"  ❌ Failed:       {failed:>3}\n")
    f.write(f"  📈 Pass Rate:    {pass_rate:.1f}%\n\n")
    f.write("─"*100 + "\n\n")

def write_test_details(f, report):
    """Write detailed test results"""
    f.write("╔" + "═"*98 + "╗\n")
    f.write("║" + "DETAILED TEST RESULTS".center(98) + "║\n")
    f.write("╚" + "═"*98 + "╝\n\n")
    
    for i, result in enumerate(report.results, 1):
        # Test header
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'ERROR': '⚠️',
            'PENDING': '⏳'
        }.get(result['status'], '❓')
        
        f.write(f"\n┌─ Test #{i}: {result['name']}\n")
        f.write(f"│  Status: {status_icon} {result['status']}\n")
        
        # Parameters
        if result['params']:
            f.write(f"│  Parameters:\n")
            for key, value in result['params'].items():
                if len(str(value)) > 60:
                    f.write(f"│    • {key}: {str(value)[:60]}...\n")
                else:
                    f.write(f"│    • {key}: {value}\n")
        
        # Results or errors
        if result['status'] == 'PASS' and result['data']:
            data = result['data']
            f.write(f"│  Results:\n")
            
            # Common fields
            if 'business_name' in data:
                f.write(f"│    • Business: {data['business_name']}\n")
            
            # Contact-specific
            if 'contact_count' in data:
                f.write(f"│    • Contact Count: {data['contact_count']}\n")
                if data.get('contacts'):
                    f.write(f"│    • Sample Contact: {data['contacts'][0].get('name', 'N/A')}\n")
            
            if 'contact' in data:
                contact = data['contact']
                f.write(f"│    • Contact Name: {contact.get('name', 'N/A')}\n")
                f.write(f"│    • Status: {contact.get('status', 'N/A')}\n")
                f.write(f"│    • Addresses: {len(contact.get('addresses', []))}\n")
                f.write(f"│    • Phones: {len(contact.get('phones', []))}\n")
            
            # Quote-specific
            if 'pagination' in data:
                pagination = data['pagination']
                f.write(f"│    • Total Count: {pagination.get('total_count', 0)}\n")
                f.write(f"│    • Returned: {pagination.get('returned_count', 0)}\n")
            
            if 'quotes' in data:
                quotes = data['quotes']
                if quotes:
                    f.write(f"│    • Sample Quote: {quotes[0].get('quote_number', 'N/A')}\n")
                    f.write(f"│    • Quote Status: {quotes[0].get('status', 'N/A')}\n")
                    total = quotes[0].get('total')
                    if total:
                        f.write(f"│    • Quote Total: ${total:.2f}\n")
            
            # Invoice-specific
            if 'invoice_count' in data:
                f.write(f"│    • Invoice Count: {data['invoice_count']}\n")
            
            if 'invoice' in data:
                invoice = data['invoice']
                f.write(f"│    • Invoice Number: {invoice.get('invoice_number', 'N/A')}\n")
                f.write(f"│    • Status: {invoice.get('status', 'N/A')}\n")
                total = invoice.get('total')
                if total:
                    f.write(f"│    • Total: ${total:.2f}\n")
            
            # Payment-specific
            if 'payment_count' in data:
                f.write(f"│    • Payment Count: {data['payment_count']}\n")
            
            # Account-specific
            if 'account_count' in data:
                f.write(f"│    • Account Count: {data['account_count']}\n")
            
            # Branding themes
            if 'themes' in data:
                f.write(f"│    • Theme Count: {len(data['themes'])}\n")
                if data['themes']:
                    f.write(f"│    • Sample Theme: {data['themes'][0].get('name', 'N/A')}\n")
        
        elif result['error']:
            f.write(f"│  Error:\n")
            f.write(f"│    • {result['error']}\n")
        
        f.write(f"└{'─'*98}\n")
    
    f.write("\n" + "─"*100 + "\n\n")

def write_workflow_guide(f):
    """Write workflow guide"""
    f.write("╔" + "═"*98 + "╗\n")
    f.write("║" + "COMPLETE WORKFLOW GUIDE".center(98) + "║\n")
    f.write("╚" + "═"*98 + "╝\n\n")
    
    f.write("🔄 Contact + Quotes Workflow:\n\n")
    f.write("  Step 1: Find Contact\n")
    f.write("    Tool: xero_get_contacts\n")
    f.write("    Purpose: Search or list contacts to get contact_id\n")
    f.write("    Returns: List of contacts with IDs\n\n")
    
    f.write("  Step 2: Get Contact Details\n")
    f.write("    Tool: xero_get_contact_by_id\n")
    f.write("    Purpose: Retrieve full contact profile\n")
    f.write("    Returns: Addresses, phones, contact persons, account details\n\n")
    
    f.write("  Step 3: Get Contact's Quotes\n")
    f.write("    Tool: xero_list_quotes\n")
    f.write("    Purpose: List all quotes for specific contact\n")
    f.write("    Returns: Quote list with numbers, status, totals\n\n")
    
    f.write("  Step 4: Get Quote Details (Optional)\n")
    f.write("    Tool: xero_get_quote_by_id\n")
    f.write("    Purpose: Get full quote with line items\n")
    f.write("    Returns: Complete quote breakdown\n\n")
    
    f.write("─"*100 + "\n\n")
    
    f.write("📊 Other Available Workflows:\n\n")
    
    f.write("  • Invoice Management:\n")
    f.write("    - xero_get_invoices: List invoices\n")
    f.write("    - xero_get_invoice_by_id: Get invoice details\n\n")
    
    f.write("  • Payment Tracking:\n")
    f.write("    - xero_get_payments: List payments\n\n")
    
    f.write("  • Account Management:\n")
    f.write("    - xero_get_accounts: Chart of accounts\n\n")
    
    f.write("  • Quote Templates:\n")
    f.write("    - xero_get_branding_themes: Available templates\n\n")
    
    f.write("─"*100 + "\n\n")

def write_footer(f, report):
    """Write report footer"""
    f.write("╔" + "═"*98 + "╗\n")
    f.write("║" + "END OF TEST REPORT".center(98) + "║\n")
    f.write("╚" + "═"*98 + "╝\n\n")
    
    status = "ALL TESTS PASSED ✅" if report.tests_failed == 0 else f"{report.tests_failed} TEST(S) FAILED ❌"
    f.write(f"Status: {status}\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("\n" + "═"*100 + "\n")

print(f"\n🧪 Running Xero Tools Test Suite...\n")

report = TestReport()

# Run tests
print("  [1/8] Testing xero_get_contacts...")
report.run_test(
    "xero_get_contacts - List contacts",
    xero_get_contacts,
    business_id=1,
    limit=5
)

print("  [2/8] Testing xero_get_contact_by_id...")
# Get a contact ID from first test
if report.results[0]['status'] == 'PASS':
    contacts = report.results[0]['data'].get('contacts', [])
    if contacts:
        test_contact_id = contacts[0]['contact_id']
        report.run_test(
            "xero_get_contact_by_id - Get contact details",
            xero_get_contact_by_id,
            business_id=1,
            contact_id=test_contact_id
        )

print("  [3/8] Testing xero_list_quotes...")
if len(report.results) > 1 and report.results[1]['status'] == 'PASS':
    report.run_test(
        "xero_list_quotes - Get quotes for contact",
        xero_list_quotes,
        business_id=1,
        contact_id=test_contact_id,
        page_size=10
    )

print("  [4/8] Testing xero_get_quote_by_id...")
if len(report.results) > 2 and report.results[2]['status'] == 'PASS':
    quotes = report.results[2]['data'].get('quotes', [])
    if quotes:
        test_quote_id = quotes[0]['quote_id']
        report.run_test(
            "xero_get_quote_by_id - Get quote details",
            xero_get_quote_by_id,
            business_id=1,
            quote_id=test_quote_id
        )

print("  [5/8] Testing xero_get_invoices...")
report.run_test(
    "xero_get_invoices - List invoices",
    xero_get_invoices,
    business_id=1,
    status="AUTHORISED"
)

print("  [6/8] Testing xero_get_payments...")
report.run_test(
    "xero_get_payments - List payments",
    xero_get_payments,
    business_id=1
)

print("  [7/8] Testing xero_get_accounts...")
report.run_test(
    "xero_get_accounts - Get chart of accounts",
    xero_get_accounts,
    business_id=1,
    limit=10
)

print("  [8/8] Testing xero_get_branding_themes...")
report.run_test(
    "xero_get_branding_themes - Get quote templates",
    xero_get_branding_themes,
    business_id=1
)

print(f"\n✅ Test suite complete: {report.tests_passed}/{report.tests_run} passed\n")

# Write report
print(f"📝 Generating test report...\n")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    write_header(f, report)
    write_summary(f, report)
    write_test_details(f, report)
    write_workflow_guide(f)
    write_footer(f, report)

print(f"✅ Test report saved to:\n   {OUTPUT_FILE}\n")
print(f"📊 Results: {report.tests_passed} passed, {report.tests_failed} failed")
print(f"📈 Pass Rate: {(report.tests_passed/report.tests_run*100):.1f}%\n")
