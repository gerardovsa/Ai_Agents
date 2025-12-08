"""Test Aged Reports with proper parameters"""
from UI.modules_external.xero.xero_routes import XeroAPIClient
from datetime import datetime

client = XeroAPIClient(1)

# Test Aged Receivables with date parameter
print("Testing Aged Receivables with date parameter...")
try:
    # Try with current date
    today = datetime.now().strftime('%Y-%m-%d')
    result = client.make_request('GET', f'Reports/AgedReceivablesByContact', params={'date': today})
    
    if result and 'Reports' in result:
        report = result['Reports'][0]
        print(f'✅ SUCCESS - Aged Receivables accessible!')
        print(f'   Report ID: {report.get("ReportID")}')
        print(f'   Report Name: {report.get("ReportName")}')
        print(f'   Report Date: {report.get("ReportDate")}')
        print(f'   Rows: {len(report.get("Rows", []))}')
        
        # Show structure
        rows = report.get('Rows', [])
        if rows:
            print(f'\n   Row Structure:')
            for i, row in enumerate(rows[:3]):
                print(f'   Row {i}: Type={row.get("RowType")}, Cells={len(row.get("Cells", []))}')
    else:
        print(f'❌ No data')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')

print("\n" + "="*60)
print("Testing Aged Payables with date parameter...")
try:
    result = client.make_request('GET', f'Reports/AgedPayablesByContact', params={'date': today})
    
    if result and 'Reports' in result:
        report = result['Reports'][0]
        print(f'✅ SUCCESS - Aged Payables accessible!')
        print(f'   Report ID: {report.get("ReportID")}')
        print(f'   Report Name: {report.get("ReportName")}')
        print(f'   Report Date: {report.get("ReportDate")}')
        print(f'   Rows: {len(report.get("Rows", []))}')
    else:
        print(f'❌ No data')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')
