"""
Get Accounts Payable - Overdue Invoices (Last Month)
Query Xero for invoices that are overdue by at least 1 month
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from tools.implementations.xero import xero_get_invoices
import json

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env.master'
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"⚠ Warning: .env.master not found at {env_path}")

print('\n' + '='*80)
print('XERO - ACCOUNTS PAYABLE REPORT (OVERDUE 1+ MONTH)')
print('='*80 + '\n')

# Calculate date 1 month ago
one_month_ago = datetime.now() - timedelta(days=30)
print(f'Searching for invoices overdue since: {one_month_ago.strftime("%Y-%m-%d")}')
print(f'Today: {datetime.now().strftime("%Y-%m-%d")}\n')

# Get all unpaid invoices (AUTHORISED = unpaid in Xero)
print('Fetching unpaid invoices from Xero...')
result = xero_get_invoices(business_id=1, status='AUTHORISED')

if not result.get('success'):
    print(f'❌ Error: {result.get("error")}')
    exit(1)

invoices = result.get('invoices', [])
print(f'✅ Retrieved {len(invoices)} unpaid invoices\n')

# Filter for overdue by 1+ month
overdue_invoices = []
total_overdue = 0.0

for inv in invoices:
    due_date_str = inv.get('due_date')
    if not due_date_str:
        continue
    
    # Parse due date
    try:
        # Xero returns ISO format: 2025-11-16T00:00:00
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        
        # Check if overdue by 1+ month
        days_overdue = (datetime.now() - due_date).days
        
        if days_overdue >= 30:  # 1 month = 30 days
            amount_due = inv.get('amount_due', 0)
            overdue_invoices.append({
                'invoice_number': inv.get('invoice_number'),
                'contact_name': inv.get('contact_name'),
                'due_date': due_date_str,
                'days_overdue': days_overdue,
                'amount_due': amount_due,
                'total': inv.get('total', 0),
                'currency': inv.get('currency', 'AUD')
            })
            total_overdue += amount_due
    except Exception as e:
        continue

# Sort by days overdue (most overdue first)
overdue_invoices.sort(key=lambda x: x['days_overdue'], reverse=True)

print('='*80)
print(f'OVERDUE INVOICES (1+ MONTH OLD)')
print('='*80)
print(f'Total overdue invoices: {len(overdue_invoices)}')
print(f'Total amount overdue: ${total_overdue:,.2f} AUD')
print('='*80 + '\n')

if overdue_invoices:
    # Group by age brackets
    age_brackets = {
        '30-60 days': {'count': 0, 'amount': 0},
        '60-90 days': {'count': 0, 'amount': 0},
        '90+ days': {'count': 0, 'amount': 0}
    }
    
    for inv in overdue_invoices:
        days = inv['days_overdue']
        amount = inv['amount_due']
        
        if 30 <= days < 60:
            age_brackets['30-60 days']['count'] += 1
            age_brackets['30-60 days']['amount'] += amount
        elif 60 <= days < 90:
            age_brackets['60-90 days']['count'] += 1
            age_brackets['60-90 days']['amount'] += amount
        else:
            age_brackets['90+ days']['count'] += 1
            age_brackets['90+ days']['amount'] += amount
    
    print('AGING SUMMARY:')
    print('-'*80)
    for bracket, data in age_brackets.items():
        if data['count'] > 0:
            print(f"{bracket:15} {data['count']:>5} invoices  ${data['amount']:>12,.2f}")
    print('-'*80 + '\n')
    
    # Show top 20 most overdue
    print('TOP 20 MOST OVERDUE INVOICES:')
    print('-'*80)
    print(f"{'Invoice #':<15} {'Customer':<30} {'Days':<8} {'Amount Due':<15}")
    print('-'*80)
    
    for inv in overdue_invoices[:20]:
        inv_num = inv['invoice_number'] or 'N/A'
        customer = inv['contact_name'] or 'Unknown'
        days = inv['days_overdue']
        amount = inv['amount_due']
        
        # Truncate long names
        if len(customer) > 28:
            customer = customer[:25] + '...'
        
        print(f"{inv_num:<15} {customer:<30} {days:<8} ${amount:>12,.2f}")
    
    if len(overdue_invoices) > 20:
        print(f"\n... and {len(overdue_invoices) - 20} more overdue invoices")
    
    print('\n' + '='*80)
    
    # Export to JSON
    export_file = 'xero_overdue_report.json'
    with open(export_file, 'w') as f:
        json.dump({
            'report_date': datetime.now().isoformat(),
            'total_overdue_invoices': len(overdue_invoices),
            'total_amount_overdue': total_overdue,
            'aging_summary': age_brackets,
            'invoices': overdue_invoices
        }, f, indent=2)
    
    print(f'\n✅ Full report exported to: {export_file}')
    print('='*80 + '\n')
else:
    print('✅ No invoices overdue by 1+ month\n')
