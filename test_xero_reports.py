"""Test Xero Reports API access without account endpoints"""
from UI.modules_external.xero.xero_routes import XeroAPIClient
import json

def test_report(client, report_name, endpoint):
    """Test a specific report endpoint"""
    try:
        print(f'\n{"="*60}')
        print(f'Testing: {report_name}')
        print(f'Endpoint: {endpoint}')
        print(f'{"="*60}')
        
        result = client.make_request('GET', endpoint)
        
        if result and 'Reports' in result:
            reports = result.get('Reports', [])
            if reports:
                report = reports[0]
                print(f'✅ SUCCESS - {report_name} accessible!')
                print(f'   Report ID: {report.get("ReportID")}')
                print(f'   Report Name: {report.get("ReportName")}')
                print(f'   Report Date: {report.get("ReportDate")}')
                
                rows = report.get('Rows', [])
                print(f'   Data Rows: {len(rows)}')
                
                # Show first row structure
                if rows:
                    first_row = rows[0]
                    print(f'   Row Type: {first_row.get("RowType")}')
                    if 'Cells' in first_row:
                        print(f'   Cells: {len(first_row["Cells"])}')
                
                return True
        else:
            print(f'❌ FAILED - No data returned')
            print(f'   Response: {result}')
            return False
            
    except Exception as e:
        error_msg = str(e)
        if '401' in error_msg:
            print(f'❌ FAILED - 401 Unauthorized (OAuth scope missing)')
        elif '403' in error_msg:
            print(f'❌ FAILED - 403 Forbidden (No permission)')
        elif '404' in error_msg:
            print(f'❌ FAILED - 404 Not Found (Endpoint doesn\'t exist)')
        else:
            print(f'❌ ERROR: {error_msg}')
        return False


# Test with InHouse Print (business_id=1)
print('Initializing Xero API Client for InHouse Print...')
client = XeroAPIClient(1)
print(f'✅ Client initialized: {client.config["name"]}')

# Test all report endpoints
reports_to_test = [
    ('Aged Receivables by Contact', 'Reports/AgedReceivablesByContact'),
    ('Aged Payables by Contact', 'Reports/AgedPayablesByContact'),
    ('Profit and Loss', 'Reports/ProfitAndLoss'),
    ('Balance Sheet', 'Reports/BalanceSheet'),
    ('Executive Summary', 'Reports/ExecutiveSummary'),
    ('Budget Summary', 'Reports/BudgetSummary'),
    ('Trial Balance', 'Reports/TrialBalance'),
]

results = {}
for name, endpoint in reports_to_test:
    results[name] = test_report(client, name, endpoint)

# Summary
print('\n' + '='*60)
print('TEST SUMMARY')
print('='*60)
success_count = sum(1 for v in results.values() if v)
total_count = len(results)
print(f'Success: {success_count}/{total_count} reports accessible')
print()
for name, success in results.items():
    status = '✅' if success else '❌'
    print(f'{status} {name}')
print('='*60)
