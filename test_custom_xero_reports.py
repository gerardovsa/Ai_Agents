"""
Test Custom Xero Reports - Derived from Invoice/Contact/Payment Data
This tests the reports WE calculate (not Xero's built-in reports)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add modules to path
root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(root_path / 'UI' / 'modules_external' / 'xero'))

from xero_routes import XeroAPIClient, parse_xero_date

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_basic_data_fetch():
    """Test 1: Verify we can fetch basic Xero data"""
    print_header("TEST 1: Basic Data Fetching")
    
    try:
        client = XeroAPIClient(business_id=1)
        print(f"✅ Client initialized for: {client.config['name']}")
        
        # Test invoices
        print("\n📄 Fetching invoices...")
        inv_data = client.make_request('GET', 'Invoices', params={'page': '1'})
        invoices = inv_data.get('Invoices', [])
        print(f"   ✅ {len(invoices)} invoices fetched")
        
        # Test contacts  
        print("\n👥 Fetching contacts...")
        con_data = client.make_request('GET', 'Contacts', params={'page': '1'})
        contacts = con_data.get('Contacts', [])
        print(f"   ✅ {len(contacts)} contacts fetched")
        
        # Test payments
        print("\n💰 Fetching payments...")
        pay_data = client.make_request('GET', 'Payments', params={'page': '1'})
        payments = pay_data.get('Payments', [])
        print(f"   ✅ {len(payments)} payments fetched")
        
        return True, {'invoices': invoices, 'contacts': contacts, 'payments': payments}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_contact_activity_report(data):
    """Test 2: Contact Activity Report (JOIN contacts with invoices)"""
    print_header("TEST 2: Contact Activity Report")
    
    try:
        invoices = data['invoices']
        contacts = data['contacts']
        
        print(f"Analyzing {len(invoices)} invoices across {len(contacts)} contacts...")
        
        # Build activity map
        activity_map = {}
        
        for inv in invoices:
            contact_id = inv.get('Contact', {}).get('ContactID')
            contact_name = inv.get('Contact', {}).get('Name', 'Unknown')
            
            if contact_id not in activity_map:
                activity_map[contact_id] = {
                    'name': contact_name,
                    'invoice_count': 0,
                    'total_invoiced': 0,
                    'total_paid': 0,
                    'outstanding': 0
                }
            
            activity_map[contact_id]['invoice_count'] += 1
            activity_map[contact_id]['total_invoiced'] += float(inv.get('Total', 0))
            activity_map[contact_id]['total_paid'] += float(inv.get('AmountPaid', 0))
            activity_map[contact_id]['outstanding'] += float(inv.get('AmountDue', 0))
        
        # Sort by revenue
        sorted_activities = sorted(
            activity_map.values(),
            key=lambda x: x['total_invoiced'],
            reverse=True
        )
        
        # Display top 10
        print(f"\n📊 TOP 10 CUSTOMERS BY REVENUE:\n")
        print(f"{'#':<4}{'Customer':<35}{'Invoices':<10}{'Revenue':<15}{'Outstanding'}")
        print("-" * 75)
        
        for i, activity in enumerate(sorted_activities[:10], 1):
            print(f"{i:<4}{activity['name'][:33]:<35}{activity['invoice_count']:<10}${activity['total_invoiced']:>12,.2f}  ${activity['outstanding']:>10,.2f}")
        
        print(f"\n✅ Report generated successfully!")
        print(f"   Total contacts with activity: {len(activity_map)}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_aged_receivables_report(data):
    """Test 3: Aged Receivables Report (overdue invoices in buckets)"""
    print_header("TEST 3: Aged Receivables Report")
    
    try:
        invoices = data['invoices']
        
        # Filter unpaid invoices
        unpaid = [inv for inv in invoices if inv.get('Status') not in ['PAID', 'VOIDED']]
        print(f"Analyzing {len(unpaid)} unpaid invoices...")
        
        # Age buckets
        buckets = {
            'Current (not due)': {'count': 0, 'amount': 0},
            '1-30 days': {'count': 0, 'amount': 0},
            '31-60 days': {'count': 0, 'amount': 0},
            '61-90 days': {'count': 0, 'amount': 0},
            '90+ days': {'count': 0, 'amount': 0}
        }
        
        today = datetime.now().date()
        
        for inv in unpaid:
            due_date_str = inv.get('DueDate')
            if not due_date_str:
                continue
            
            try:
                due_date = parse_xero_date(due_date_str)
                if due_date:
                    due_date = due_date.date()
                    days_overdue = (today - due_date).days
                    amount_due = float(inv.get('AmountDue', 0))
                    
                    if days_overdue <= 0:
                        bucket = 'Current (not due)'
                    elif days_overdue <= 30:
                        bucket = '1-30 days'
                    elif days_overdue <= 60:
                        bucket = '31-60 days'
                    elif days_overdue <= 90:
                        bucket = '61-90 days'
                    else:
                        bucket = '90+ days'
                    
                    buckets[bucket]['count'] += 1
                    buckets[bucket]['amount'] += amount_due
            except:
                continue
        
        # Display results
        print(f"\n📊 AGED RECEIVABLES:\n")
        print(f"{'Age Bucket':<20}{'Count':<10}{'Total Amount'}")
        print("-" * 50)
        
        for bucket_name, bucket_data in buckets.items():
            print(f"{bucket_name:<20}{bucket_data['count']:<10}${bucket_data['amount']:>12,.2f}")
        
        total_outstanding = sum(b['amount'] for b in buckets.values())
        print("-" * 50)
        print(f"{'TOTAL':<20}{len(unpaid):<10}${total_outstanding:>12,.2f}")
        
        print(f"\n✅ Report generated successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sales_summary_report(data):
    """Test 4: Sales Summary Report (revenue by customer)"""
    print_header("TEST 4: Sales Summary Report")
    
    try:
        invoices = data['invoices']
        
        # Filter to last 90 days
        cutoff = datetime.now() - timedelta(days=90)
        recent_invoices = []
        
        for inv in invoices:
            inv_date_str = inv.get('Date')
            if inv_date_str:
                try:
                    inv_date = parse_xero_date(inv_date_str)
                    if inv_date and inv_date >= cutoff:
                        recent_invoices.append(inv)
                except:
                    continue
        
        print(f"Analyzing {len(recent_invoices)} invoices from last 90 days...")
        
        # Group by customer
        customer_sales = {}
        
        for inv in recent_invoices:
            contact_name = inv.get('Contact', {}).get('Name', 'Unknown')
            
            if contact_name not in customer_sales:
                customer_sales[contact_name] = {
                    'invoice_count': 0,
                    'total_invoiced': 0,
                    'total_paid': 0,
                    'outstanding': 0
                }
            
            customer_sales[contact_name]['invoice_count'] += 1
            customer_sales[contact_name]['total_invoiced'] += float(inv.get('Total', 0))
            customer_sales[contact_name]['total_paid'] += float(inv.get('AmountPaid', 0))
            customer_sales[contact_name]['outstanding'] += float(inv.get('AmountDue', 0))
        
        # Calculate totals
        total_revenue = sum(s['total_invoiced'] for s in customer_sales.values())
        total_paid = sum(s['total_paid'] for s in customer_sales.values())
        total_outstanding = sum(s['outstanding'] for s in customer_sales.values())
        
        print(f"\n📊 SALES SUMMARY (Last 90 Days):\n")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Paid: ${total_paid:,.2f}")
        print(f"Outstanding: ${total_outstanding:,.2f}")
        print(f"Active Customers: {len(customer_sales)}")
        
        # Top 10
        sorted_sales = sorted(
            customer_sales.items(),
            key=lambda x: x[1]['total_invoiced'],
            reverse=True
        )
        
        print(f"\n{'Customer':<35}{'Invoices':<10}{'Revenue':<15}{'Outstanding'}")
        print("-" * 70)
        
        for customer, sales in sorted_sales[:10]:
            print(f"{customer[:33]:<35}{sales['invoice_count']:<10}${sales['total_invoiced']:>12,.2f}  ${sales['outstanding']:>10,.2f}")
        
        print(f"\n✅ Report generated successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  XERO CUSTOM REPORTS TEST SUITE")
    print("  Testing reports derived from Invoice/Contact/Payment data")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Business: InHouse Print (ID: 1)")
    
    # Test 1: Fetch data
    success, data = test_basic_data_fetch()
    
    if not success or not data:
        print("\n❌ FAILED: Could not fetch basic data from Xero")
        print("   Check Supabase credentials in user_platform_credentials table")
        sys.exit(1)
    
    # Test 2-4: Run reports
    results = {
        'Contact Activity': test_contact_activity_report(data),
        'Aged Receivables': test_aged_receivables_report(data),
        'Sales Summary': test_sales_summary_report(data)
    }
    
    # Summary
    print_header("TEST SUMMARY")
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\n✅ {success_count}/{total_count} reports generated successfully\n")
    
    for name, success in results.items():
        status = '✅' if success else '❌'
        print(f"   {status} {name}")
    
    print("\n" + "="*70)
    print("  All reports can be derived from existing Xero data!")
    print("  Ready to implement backend endpoints and frontend UI")
    print("="*70 + "\n")
