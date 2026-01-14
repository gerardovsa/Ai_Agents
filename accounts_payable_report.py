"""
Accounts Payable Analysis - All Unpaid Invoices
Shows all outstanding invoices with aging breakdown
"""
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from tools.implementations.xero import xero_get_invoices
import json

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env.master'
if env_path.exists():
    load_dotenv(env_path)

def parse_xero_date(date_str):
    """
    Parse Xero's weird date format: /Date(1748476800000+0000)/
    Returns datetime object or None
    """
    if not date_str:
        return None
    
    try:
        # Extract timestamp from /Date(timestamp+0000)/
        match = re.search(r'/Date\((\d+)', date_str)
        if match:
            timestamp_ms = int(match.group(1))
            # Convert milliseconds to seconds
            timestamp_sec = timestamp_ms / 1000
            return datetime.fromtimestamp(timestamp_sec)
        
        # Try ISO format as fallback
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception as e:
        return None

print('\n' + '='*80)
print('XERO - ACCOUNTS PAYABLE ANALYSIS (ALL UNPAID)')
print('='*80 + '\n')

# Get all unpaid invoices
print('Fetching unpaid invoices from Xero...')
result = xero_get_invoices(business_id=1, status='AUTHORISED')

if not result.get('success'):
    print(f'❌ Error: {result.get("error")}')
    exit(1)

invoices = result.get('invoices', [])
print(f'✅ Retrieved {len(invoices)} unpaid invoices\n')

# Analyze all invoices
total_due = 0.0
current = []      # Not yet due
overdue_1_30 = [] # 1-30 days overdue
overdue_30_60 = [] # 30-60 days overdue
overdue_60_90 = [] # 60-90 days overdue
overdue_90_plus = [] # 90+ days overdue

now = datetime.now()

for inv in invoices:
    due_date_str = inv.get('due_date')
    amount_due = inv.get('amount_due', 0)
    total_due += amount_due
    
    # Parse dates
    invoice_date = parse_xero_date(inv.get('date'))
    due_date = parse_xero_date(due_date_str)
    
    inv_data = {
        'invoice_number': inv.get('invoice_number'),
        'contact_name': inv.get('contact_name'),
        'date': invoice_date.strftime('%Y-%m-%d') if invoice_date else None,
        'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
        'amount_due': amount_due,
        'total': inv.get('total', 0),
        'currency': inv.get('currency', 'AUD')
    }
    
    if not due_date:
        current.append(inv_data)
        continue
    
    try:
        days_overdue = (now - due_date).days
        inv_data['days_overdue'] = days_overdue
        
        if days_overdue < 0:
            current.append(inv_data)
        elif days_overdue <= 30:
            overdue_1_30.append(inv_data)
        elif days_overdue <= 60:
            overdue_30_60.append(inv_data)
        elif days_overdue <= 90:
            overdue_60_90.append(inv_data)
        else:
            overdue_90_plus.append(inv_data)
    except Exception as e:
        current.append(inv_data)

print('='*80)
print('ACCOUNTS PAYABLE AGING SUMMARY')
print('='*80)
print(f"{'Category':<20} {'Count':<10} {'Total Amount':<20}")
print('-'*80)

categories = [
    ('Current (Not Due)', current),
    ('1-30 Days Overdue', overdue_1_30),
    ('30-60 Days Overdue', overdue_30_60),
    ('60-90 Days Overdue', overdue_60_90),
    ('90+ Days Overdue', overdue_90_plus)
]

for category_name, category_list in categories:
    count = len(category_list)
    amount = sum(inv['amount_due'] for inv in category_list)
    print(f"{category_name:<20} {count:<10} ${amount:>18,.2f}")

print('-'*80)
print(f"{'TOTAL':<20} {len(invoices):<10} ${total_due:>18,.2f}")
print('='*80 + '\n')

# Show overdue invoices (1+ months)
all_overdue = overdue_30_60 + overdue_60_90 + overdue_90_plus
if all_overdue:
    # Sort by days overdue
    all_overdue.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
    
    overdue_total = sum(inv['amount_due'] for inv in all_overdue)
    
    print('='*80)
    print(f'OVERDUE 30+ DAYS ({len(all_overdue)} invoices)')
    print('='*80)
    print(f"Total Amount: ${overdue_total:,.2f}\n")
    print(f"{'Invoice #':<15} {'Customer':<30} {'Due Date':<12} {'Days':<8} {'Amount':<15}")
    print('-'*80)
    
    for inv in all_overdue[:30]:  # Show top 30
        inv_num = inv['invoice_number'] or 'N/A'
        customer = inv['contact_name'] or 'Unknown'
        due_date = inv.get('due_date', 'N/A')
        if due_date != 'N/A':
            due_date = due_date[:10]  # Just date part
        days = inv.get('days_overdue', 0)
        amount = inv['amount_due']
        
        if len(customer) > 28:
            customer = customer[:25] + '...'
        
        print(f"{inv_num:<15} {customer:<30} {due_date:<12} {days:<8} ${amount:>12,.2f}")
    
    if len(all_overdue) > 30:
        remaining = len(all_overdue) - 30
        remaining_amount = sum(inv['amount_due'] for inv in all_overdue[30:])
        print(f"\n... and {remaining} more overdue invoices (${remaining_amount:,.2f})")
    
    print('\n' + '='*80 + '\n')
else:
    print('✅ No invoices overdue by 30+ days\n')

# Show recently overdue (1-30 days)
if overdue_1_30:
    overdue_1_30.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
    recent_total = sum(inv['amount_due'] for inv in overdue_1_30)
    
    print('='*80)
    print(f'RECENTLY OVERDUE 1-30 DAYS ({len(overdue_1_30)} invoices)')
    print('='*80)
    print(f"Total Amount: ${recent_total:,.2f}\n")
    print(f"{'Invoice #':<15} {'Customer':<30} {'Due Date':<12} {'Days':<8} {'Amount':<15}")
    print('-'*80)
    
    for inv in overdue_1_30[:20]:  # Show top 20
        inv_num = inv['invoice_number'] or 'N/A'
        customer = inv['contact_name'] or 'Unknown'
        due_date = inv.get('due_date', 'N/A')
        if due_date != 'N/A':
            due_date = due_date[:10]
        days = inv.get('days_overdue', 0)
        amount = inv['amount_due']
        
        if len(customer) > 28:
            customer = customer[:25] + '...'
        
        print(f"{inv_num:<15} {customer:<30} {due_date:<12} {days:<8} ${amount:>12,.2f}")
    
    if len(overdue_1_30) > 20:
        print(f"\n... and {len(overdue_1_30) - 20} more")
    
    print('\n' + '='*80 + '\n')

# Export to JSON
export_file = 'xero_accounts_payable.json'
with open(export_file, 'w') as f:
    json.dump({
        'report_date': datetime.now().isoformat(),
        'total_unpaid_invoices': len(invoices),
        'total_amount_due': total_due,
        'aging_summary': {
            'current': {'count': len(current), 'amount': sum(inv['amount_due'] for inv in current)},
            '1_30_days': {'count': len(overdue_1_30), 'amount': sum(inv['amount_due'] for inv in overdue_1_30)},
            '30_60_days': {'count': len(overdue_30_60), 'amount': sum(inv['amount_due'] for inv in overdue_30_60)},
            '60_90_days': {'count': len(overdue_60_90), 'amount': sum(inv['amount_due'] for inv in overdue_60_90)},
            '90_plus_days': {'count': len(overdue_90_plus), 'amount': sum(inv['amount_due'] for inv in overdue_90_plus)}
        },
        'current_invoices': current,
        'overdue_1_30_days': overdue_1_30,
        'overdue_30_60_days': overdue_30_60,
        'overdue_60_90_days': overdue_60_90,
        'overdue_90_plus_days': overdue_90_plus
    }, f, indent=2)

print(f'✅ Full report exported to: {export_file}')
print('='*80 + '\n')
