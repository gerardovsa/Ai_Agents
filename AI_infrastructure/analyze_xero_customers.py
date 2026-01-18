"""
Analyze Xero Customer Data - Real Behavior Patterns
Purpose: Get baseline metrics for intelligent risk scoring
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
from collections import defaultdict

# Add paths for imports
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Set up environment
from dotenv import load_dotenv
env_path = root_path / '.env.master'
load_dotenv(env_path)

# Import Xero client
sys.path.insert(0, str(root_path / 'UI' / 'modules_external' / 'xero'))
from xero_routes import XeroAPIClient, parse_xero_date

print('🔍 ANALYZING XERO CUSTOMER DATA (1 YEAR BASELINE)')
print('='*80)

try:
    # Connect to InHouse Print (business_id=1)
    client = XeroAPIClient(business_id=1)
    
    # Fetch all invoices from last 12 months
    from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    print(f'📅 Date range: {from_date} to {datetime.now().strftime("%Y-%m-%d")}')
    print()
    
    # Build where clause
    from_dt = f'DateTime({from_date.split("-")[0]},{from_date.split("-")[1]},{from_date.split("-")[2]})'
    params = {'where': f'Date>={from_dt}'}
    
    print('⏳ Fetching invoices from Xero API...')
    invoices_data = client.make_request('GET', 'Invoices', params=params)
    invoices = invoices_data.get('Invoices', [])
    
    print(f'✅ Fetched {len(invoices)} invoices')
    print()
    
    # Analyze customer behavior
    customer_stats = defaultdict(lambda: {
        'orders': [],
        'values': [],
        'contact_name': '',
        'contact_id': ''
    })
    
    for inv in invoices:
        if inv.get('Status') not in ['PAID', 'AUTHORISED']:
            continue
            
        contact = inv.get('Contact', {})
        contact_id = contact.get('ContactID')
        contact_name = contact.get('Name', 'Unknown')
        
        if not contact_id:
            continue
        
        # Parse date
        inv_date = parse_xero_date(inv.get('Date'))
        if not inv_date:
            continue
        
        customer_stats[contact_id]['orders'].append(inv_date)
        customer_stats[contact_id]['values'].append(float(inv.get('Total', 0)))
        customer_stats[contact_id]['contact_name'] = contact_name
        customer_stats[contact_id]['contact_id'] = contact_id
    
    print(f'📊 CUSTOMER POPULATION METRICS')
    print('='*80)
    print(f'Total unique customers: {len(customer_stats)}')
    print()
    
    # Calculate metrics
    single_order_customers = []
    multi_order_customers = []
    high_frequency_customers = []
    
    all_reorder_intervals = []
    all_order_counts = []
    all_ltv_values = []
    
    for customer_id, data in customer_stats.items():
        order_count = len(data['orders'])
        all_order_counts.append(order_count)
        
        total_value = sum(data['values'])
        all_ltv_values.append(total_value)
        
        if order_count == 1:
            single_order_customers.append({
                'name': data['contact_name'],
                'value': data['values'][0],
                'date': data['orders'][0]
            })
        else:
            # Calculate reorder intervals
            sorted_dates = sorted(data['orders'])
            intervals = []
            for i in range(1, len(sorted_dates)):
                days_between = (sorted_dates[i] - sorted_dates[i-1]).days
                if days_between > 0:
                    intervals.append(days_between)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                all_reorder_intervals.extend(intervals)
                
                # Variance
                if len(intervals) > 1:
                    mean = avg_interval
                    variance = (sum((x - mean) ** 2 for x in intervals) / len(intervals)) ** 0.5
                else:
                    variance = 0
                
                multi_order_customers.append({
                    'name': data['contact_name'],
                    'order_count': order_count,
                    'avg_interval': avg_interval,
                    'variance': variance,
                    'total_value': total_value,
                    'avg_order_value': total_value / order_count,
                    'last_order': sorted_dates[-1],
                    'days_since_last': (datetime.now() - sorted_dates[-1]).days
                })
                
                # High frequency = avg interval < 60 days
                if avg_interval < 60:
                    high_frequency_customers.append(data['contact_name'])
    
    # Summary statistics
    print(f'Single-order customers: {len(single_order_customers)} ({len(single_order_customers)/len(customer_stats)*100:.1f}%)')
    print(f'Multi-order customers: {len(multi_order_customers)} ({len(multi_order_customers)/len(customer_stats)*100:.1f}%)')
    print(f'High-frequency customers (<60d avg): {len(high_frequency_customers)}')
    print()
    
    if all_order_counts:
        print('📈 ORDER FREQUENCY DISTRIBUTION')
        print('='*80)
        print(f'Average orders per customer: {sum(all_order_counts)/len(all_order_counts):.1f}')
        print(f'Median orders per customer: {sorted(all_order_counts)[len(all_order_counts)//2]}')
        print(f'Max orders (single customer): {max(all_order_counts)}')
        print()
    
    if all_reorder_intervals:
        print('⏱️  REORDER INTERVAL STATISTICS')
        print('='*80)
        avg_reorder = sum(all_reorder_intervals) / len(all_reorder_intervals)
        median_reorder = sorted(all_reorder_intervals)[len(all_reorder_intervals)//2]
        print(f'Average reorder interval: {avg_reorder:.1f} days')
        print(f'Median reorder interval: {median_reorder} days')
        print(f'Min reorder interval: {min(all_reorder_intervals)} days')
        print(f'Max reorder interval: {max(all_reorder_intervals)} days')
        print()
    
    if all_ltv_values:
        print('💰 CUSTOMER VALUE DISTRIBUTION')
        print('='*80)
        avg_ltv = sum(all_ltv_values) / len(all_ltv_values)
        median_ltv = sorted(all_ltv_values)[len(all_ltv_values)//2]
        top_10_threshold = sorted(all_ltv_values, reverse=True)[len(all_ltv_values)//10]
        print(f'Average LTV: ${avg_ltv:,.2f}')
        print(f'Median LTV: ${median_ltv:,.2f}')
        print(f'Top 10% threshold: ${top_10_threshold:,.2f}')
        print()
    
    # Sample high-frequency customers
    if multi_order_customers:
        print('🔥 TOP 10 HIGH-FREQUENCY CUSTOMERS')
        print('='*80)
        sorted_by_freq = sorted(multi_order_customers, key=lambda x: x['avg_interval'])[:10]
        for i, cust in enumerate(sorted_by_freq, 1):
            name_display = cust['name'][:40].ljust(40)
            print(f'{i:2d}. {name_display} | {cust["order_count"]:3d} orders | Avg: {cust["avg_interval"]:5.1f}d | Var: {cust["variance"]:5.1f}d | LTV: ${cust["total_value"]:>10,.2f}')
        print()
    
    # Sample single-order customers
    if single_order_customers:
        print('📋 SINGLE-ORDER CUSTOMERS (High vs Low Value)')
        print('='*80)
        sorted_by_value = sorted(single_order_customers, key=lambda x: x['value'], reverse=True)
        print('Top 5 High-Value Single Orders:')
        for i, cust in enumerate(sorted_by_value[:5], 1):
            days_ago = (datetime.now() - cust['date']).days
            name_display = cust['name'][:40].ljust(40)
            print(f'  {i}. {name_display} | ${cust["value"]:>10,.2f} | {days_ago:3d} days ago')
        print()
        print('Bottom 5 Low-Value Single Orders:')
        for i, cust in enumerate(sorted_by_value[-5:], 1):
            days_ago = (datetime.now() - cust['date']).days
            name_display = cust['name'][:40].ljust(40)
            print(f'  {i}. {name_display} | ${cust["value"]:>10,.2f} | {days_ago:3d} days ago')
        print()
    
    # Save analysis results
    analysis = {
        'generated_at': datetime.now().isoformat(),
        'total_customers': len(customer_stats),
        'single_order_count': len(single_order_customers),
        'multi_order_count': len(multi_order_customers),
        'avg_orders_per_customer': sum(all_order_counts)/len(all_order_counts) if all_order_counts else 0,
        'avg_reorder_interval_days': sum(all_reorder_intervals)/len(all_reorder_intervals) if all_reorder_intervals else 0,
        'median_reorder_interval_days': sorted(all_reorder_intervals)[len(all_reorder_intervals)//2] if all_reorder_intervals else 0,
        'avg_ltv': sum(all_ltv_values)/len(all_ltv_values) if all_ltv_values else 0,
        'median_ltv': sorted(all_ltv_values)[len(all_ltv_values)//2] if all_ltv_values else 0
    }
    
    print('✅ ANALYSIS COMPLETE')
    print('='*80)
    print('Key Findings:')
    print(f'  • {analysis["single_order_count"]/analysis["total_customers"]*100:.1f}% customers have only 1 order')
    print(f'  • Average reorder cycle: {analysis["avg_reorder_interval_days"]:.0f} days')
    print(f'  • High-frequency customers (<60d): {len(high_frequency_customers)} ({len(high_frequency_customers)/len(customer_stats)*100:.1f}%)')
    print()
    print('💡 RECOMMENDATIONS:')
    print('  1. Use customer-specific reorder intervals (mean + variance) instead of fixed 30/60/90 days')
    print('  2. High-frequency customers (even low value) should be high priority')
    print('  3. Single high-value orders: 30-day follow-up trigger')
    print('  4. Single low-value orders: lower priority, monitor at 90+ days')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
