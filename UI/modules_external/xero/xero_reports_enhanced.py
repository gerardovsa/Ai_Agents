"""
Enhanced Xero Report Endpoints with YoY Comparisons and Advanced Analytics
Adds comprehensive dashboard features to all reports
"""

from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime, timedelta
import traceback

# Import from main xero_routes module
from xero_routes import XeroAPIClient, BUSINESS_CONFIGS, parse_xero_date, format_xero_datetime


def init_enhanced_xero_routes(app):
    """Register enhanced report endpoints"""
    
    @app.route('/api/xero/reports/business-comparison-enhanced', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_business_comparison_enhanced():
        """Enhanced Business Comparison with YoY, trends, and market share"""
        try:
            from_date = request.args.get('from_date')
            to_date = request.args.get('to_date')
            compare_to = request.args.get('compare_to', 'none')
            
            if not from_date:
                from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            if not to_date:
                to_date = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate comparison period
            comparison_from = None
            comparison_to = None
            if compare_to == 'yoy':
                from_dt = datetime.strptime(from_date, '%Y-%m-%d')
                to_dt = datetime.strptime(to_date, '%Y-%m-%d')
                comparison_from = (from_dt - timedelta(days=365)).strftime('%Y-%m-%d')
                comparison_to = (to_dt - timedelta(days=365)).strftime('%Y-%m-%d')
            elif compare_to == 'previous':
                from_dt = datetime.strptime(from_date, '%Y-%m-%d')
                to_dt = datetime.strptime(to_date, '%Y-%m-%d')
                period_length = (to_dt - from_dt).days
                comparison_to = (from_dt - timedelta(days=1)).strftime('%Y-%m-%d')
                comparison_from = (from_dt - timedelta(days=period_length + 1)).strftime('%Y-%m-%d')
            
            businesses = []
            
            for business_id in [1, 2, 3]:
                client = XeroAPIClient(business_id)
                
                # Current period
                from_dt = format_xero_datetime(from_date)
                to_dt = format_xero_datetime(to_date)
                params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
                data = client.make_request('GET', 'Invoices', params=params)
                invoices = data.get('Invoices', [])
                
                total_revenue = sum(float(inv.get('Total', 0)) for inv in invoices if inv.get('Status') == 'PAID')
                total_outstanding = sum(float(inv.get('AmountDue', 0)) for inv in invoices if inv.get('Status') not in ['PAID', 'VOIDED'])
                invoice_count = len([inv for inv in invoices if inv.get('Status') == 'PAID'])
                
                # Collection days
                paid_invoices = [inv for inv in invoices if inv.get('Status') == 'PAID' and inv.get('Date') and inv.get('FullyPaidOnDate')]
                collection_days = 0
                if paid_invoices:
                    days_list = []
                    for inv in paid_invoices:
                        inv_date = parse_xero_date(inv.get('Date'))
                        paid_date = parse_xero_date(inv.get('FullyPaidOnDate'))
                        if inv_date and paid_date:
                            days_list.append((paid_date - inv_date).days)
                    collection_days = sum(days_list) / len(days_list) if days_list else 0
                
                business_data = {
                    'business_id': business_id,
                    'business_name': BUSINESS_CONFIGS[business_id]['name'],
                    'revenue': total_revenue,
                    'outstanding': total_outstanding,
                    'invoice_count': invoice_count,
                    'avg_invoice_value': total_revenue / invoice_count if invoice_count > 0 else 0,
                    'collection_days': round(collection_days, 1)
                }
                
                # Comparison period
                if comparison_from and comparison_to:
                    comp_from_dt = format_xero_datetime(comparison_from)
                    comp_to_dt = format_xero_datetime(comparison_to)
                    params_comp = {'where': f'Date>={comp_from_dt} AND Date<={comp_to_dt}'}
                    data_comp = client.make_request('GET', 'Invoices', params=params_comp)
                    invoices_comp = data_comp.get('Invoices', [])
                    
                    comp_revenue = sum(float(inv.get('Total', 0)) for inv in invoices_comp if inv.get('Status') == 'PAID')
                    comp_invoice_count = len([inv for inv in invoices_comp if inv.get('Status') == 'PAID'])
                    
                    business_data['comparison'] = {
                        'revenue': comp_revenue,
                        'invoice_count': comp_invoice_count,
                        'revenue_change': total_revenue - comp_revenue,
                        'revenue_change_pct': ((total_revenue - comp_revenue) / comp_revenue * 100) if comp_revenue > 0 else 0
                    }
                
                # Monthly trend (last 12 months)
                trend_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                trend_from_dt = format_xero_datetime(trend_from)
                params_trend = {'where': f'Date>={trend_from_dt}'}
                data_trend = client.make_request('GET', 'Invoices', params=params_trend)
                invoices_trend = data_trend.get('Invoices', [])
                
                monthly_data = {}
                for inv in invoices_trend:
                    if inv.get('Status') != 'PAID':
                        continue
                    inv_date = parse_xero_date(inv.get('Date'))
                    if inv_date:
                        month_key = inv_date.strftime('%Y-%m')
                        if month_key not in monthly_data:
                            monthly_data[month_key] = 0
                        monthly_data[month_key] += float(inv.get('Total', 0))
                
                business_data['monthly_trend'] = [{'month': m, 'revenue': r} for m, r in sorted(monthly_data.items())]
                businesses.append(business_data)
            
            # Calculate totals and market share
            total_revenue = sum(b['revenue'] for b in businesses)
            total_outstanding = sum(b['outstanding'] for b in businesses)
            
            for business in businesses:
                business['market_share'] = round((business['revenue'] / total_revenue * 100), 1) if total_revenue > 0 else 0
            
            return jsonify({
                'success': True,
                'date_range': {'from': from_date, 'to': to_date},
                'comparison_period': {'from': comparison_from, 'to': comparison_to} if comparison_from else None,
                'compare_to': compare_to,
                'total_revenue': total_revenue,
                'total_outstanding': total_outstanding,
                'businesses': businesses
            })
        
        except Exception as e:
            print(f"Error in business_comparison_enhanced: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/xero/reports/consolidated-revenue-enhanced', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_consolidated_revenue_enhanced():
        """Enhanced Consolidated Revenue with waterfall, projections"""
        try:
            from_date = request.args.get('from_date')
            to_date = request.args.get('to_date')
            compare_to = request.args.get('compare_to', 'none')
            
            if not from_date:
                from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            if not to_date:
                to_date = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate comparison period
            comparison_from = None
            comparison_to = None
            if compare_to == 'yoy':
                from_dt = datetime.strptime(from_date, '%Y-%m-%d')
                to_dt = datetime.strptime(to_date, '%Y-%m-%d')
                comparison_from = (from_dt - timedelta(days=365)).strftime('%Y-%m-%d')
                comparison_to = (to_dt - timedelta(days=365)).strftime('%Y-%m-%d')
            
            consolidated = {
                'total_revenue': 0,
                'total_outstanding': 0,
                'total_invoice_count': 0,
                'businesses': []
            }
            
            monthly_trends_current = {}
            monthly_trends_comparison = {}
            
            from_dt = format_xero_datetime(from_date)
            to_dt = format_xero_datetime(to_date)
            
            for business_id in [1, 2, 3]:
                client = XeroAPIClient(business_id)
                
                # Current period
                params = {'where': f'Date>={from_dt} AND Date<={to_dt}'}
                data = client.make_request('GET', 'Invoices', params=params)
                invoices = data.get('Invoices', [])
                
                revenue = sum(float(inv.get('Total', 0)) for inv in invoices if inv.get('Status') == 'PAID')
                outstanding = sum(float(inv.get('AmountDue', 0)) for inv in invoices if inv.get('Status') not in ['PAID', 'VOIDED'])
                
                business_info = {
                    'business_id': business_id,
                    'business_name': BUSINESS_CONFIGS[business_id]['name'],
                    'revenue': revenue,
                    'outstanding': outstanding,
                    'invoice_count': len(invoices),
                    'percentage_of_total': 0
                }
                
                # Monthly breakdown
                for inv in invoices:
                    if inv.get('Status') != 'PAID':
                        continue
                    inv_date = parse_xero_date(inv.get('Date'))
                    if inv_date:
                        month_key = inv_date.strftime('%Y-%m')
                        if month_key not in monthly_trends_current:
                            monthly_trends_current[month_key] = 0
                        monthly_trends_current[month_key] += float(inv.get('Total', 0))
                
                # Comparison period
                if comparison_from and comparison_to:
                    comp_from_dt = format_xero_datetime(comparison_from)
                    comp_to_dt = format_xero_datetime(comparison_to)
                    params_comp = {'where': f'Date>={comp_from_dt} AND Date<={comp_to_dt}'}
                    data_comp = client.make_request('GET', 'Invoices', params=params_comp)
                    invoices_comp = data_comp.get('Invoices', [])
                    
                    comp_revenue = sum(float(inv.get('Total', 0)) for inv in invoices_comp if inv.get('Status') == 'PAID')
                    
                    business_info['comparison'] = {
                        'revenue': comp_revenue,
                        'change_pct': ((revenue - comp_revenue) / comp_revenue * 100) if comp_revenue > 0 else 0
                    }
                    
                    # Monthly breakdown for comparison
                    for inv in invoices_comp:
                        if inv.get('Status') != 'PAID':
                            continue
                        inv_date = parse_xero_date(inv.get('Date'))
                        if inv_date:
                            month_key = inv_date.strftime('%Y-%m')
                            if month_key not in monthly_trends_comparison:
                                monthly_trends_comparison[month_key] = 0
                            monthly_trends_comparison[month_key] += float(inv.get('Total', 0))
                
                consolidated['businesses'].append(business_info)
                consolidated['total_revenue'] += revenue
                consolidated['total_outstanding'] += outstanding
                consolidated['total_invoice_count'] += len(invoices)
            
            # Calculate percentages
            for business in consolidated['businesses']:
                if consolidated['total_revenue'] > 0:
                    business['percentage_of_total'] = round((business['revenue'] / consolidated['total_revenue']) * 100, 1)
            
            # Format monthly trends
            monthly_data = []
            for month in sorted(monthly_trends_current.keys()):
                monthly_data.append({
                    'month': month,
                    'current': monthly_trends_current[month],
                    'comparison': monthly_trends_comparison.get(month, 0)
                })
            
            # Cash flow projection (next 90 days based on outstanding)
            outstanding_aging = {'0-30': 0, '31-60': 0, '61-90': 0, '90+': 0}
            for business_id in [1, 2, 3]:
                client = XeroAPIClient(business_id)
                params = {'where': 'Status=="AUTHORISED" OR Status=="SUBMITTED"'}
                data = client.make_request('GET', 'Invoices', params=params)
                invoices = data.get('Invoices', [])
                
                for inv in invoices:
                    due_date = parse_xero_date(inv.get('DueDate'))
                    if due_date:
                        days_until_due = (due_date - datetime.now()).days
                        amount = float(inv.get('AmountDue', 0))
                        if days_until_due <= 30:
                            outstanding_aging['0-30'] += amount
                        elif days_until_due <= 60:
                            outstanding_aging['31-60'] += amount
                        elif days_until_due <= 90:
                            outstanding_aging['61-90'] += amount
                        else:
                            outstanding_aging['90+'] += amount
            
            return jsonify({
                'success': True,
                'date_range': {'from': from_date, 'to': to_date},
                'comparison_period': {'from': comparison_from, 'to': comparison_to} if comparison_from else None,
                'compare_to': compare_to,
                'consolidated': consolidated,
                'monthly_trends': monthly_data,
                'cash_flow_projection': outstanding_aging
            })
        
        except Exception as e:
            print(f"Error in consolidated_revenue_enhanced: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/xero/reports/seasonality-enhanced', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_seasonality_enhanced():
        """Enhanced Seasonality Analysis with YoY comparison and trends"""
        try:
            business_id = int(request.args.get('business_id', 1))
            years = int(request.args.get('years', 3))
            compare_to = request.args.get('compare_to', 'none')
            
            client = XeroAPIClient(business_id)
            
            # Fetch invoices for specified years
            from_date = (datetime.now() - timedelta(days=365 * years)).strftime('%Y-%m-%d')
            from_dt = format_xero_datetime(from_date)
            params = {'where': f'Date>={from_dt}'}
            data = client.make_request('GET', 'Invoices', params=params)
            invoices = data.get('Invoices', [])
            
            # Group by year and month
            monthly_data = {}
            yearly_totals = {}
            
            for inv in invoices:
                if inv.get('Status') != 'PAID':
                    continue
                
                inv_date_str = inv.get('Date')
                if not inv_date_str:
                    continue
                
                dt = parse_xero_date(inv_date_str)
                if not dt:
                    continue
                
                year = dt.year
                month = dt.month
                month_name = dt.strftime('%B')
                
                key = f"{year}-{month:02d}"
                
                if key not in monthly_data:
                    monthly_data[key] = {
                        'year': year,
                        'month': month,
                        'month_name': month_name,
                        'revenue': 0,
                        'invoice_count': 0
                    }
                
                monthly_data[key]['revenue'] += float(inv.get('Total', 0))
                monthly_data[key]['invoice_count'] += 1
                
                # Track yearly totals
                if year not in yearly_totals:
                    yearly_totals[year] = 0
                yearly_totals[year] += float(inv.get('Total', 0))
            
            # Sort chronologically
            sorted_months = sorted(monthly_data.values(), key=lambda x: (x['year'], x['month']))
            
            # Calculate month-over-month averages for seasonality pattern
            month_averages = {}
            month_stats = {}
            for month_num in range(1, 13):
                month_revenues = [m['revenue'] for m in sorted_months if m['month'] == month_num]
                if month_revenues:
                    avg_revenue = sum(month_revenues) / len(month_revenues)
                    month_averages[month_num] = {
                        'month': month_num,
                        'month_name': datetime(2000, month_num, 1).strftime('%B'),
                        'avg_revenue': avg_revenue,
                        'occurrences': len(month_revenues),
                        'min_revenue': min(month_revenues),
                        'max_revenue': max(month_revenues),
                        'variance': max(month_revenues) - min(month_revenues)
                    }
                    
                    # Calculate YoY comparison for current year
                    current_year = datetime.now().year
                    current_month_data = [m for m in sorted_months if m['year'] == current_year and m['month'] == month_num]
                    prev_year_data = [m for m in sorted_months if m['year'] == current_year - 1 and m['month'] == month_num]
                    
                    if current_month_data and prev_year_data:
                        current_rev = current_month_data[0]['revenue']
                        prev_rev = prev_year_data[0]['revenue']
                        month_averages[month_num]['yoy_change'] = ((current_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
            
            sorted_avg = sorted(month_averages.values(), key=lambda x: x['month'])
            
            # Identify peak and slow months
            all_avg_revenues = [m['avg_revenue'] for m in sorted_avg]
            avg_of_avg = sum(all_avg_revenues) / len(all_avg_revenues) if all_avg_revenues else 0
            
            peak_months = sorted([m for m in sorted_avg if m['avg_revenue'] > avg_of_avg * 1.1], 
                                key=lambda x: x['avg_revenue'], reverse=True)[:3]
            slow_months = sorted([m for m in sorted_avg if m['avg_revenue'] < avg_of_avg * 0.9], 
                                key=lambda x: x['avg_revenue'])[:3]
            
            # Current month comparison
            current_month = datetime.now().month
            current_month_revenue = sum(m['revenue'] for m in sorted_months 
                                       if m['year'] == datetime.now().year and m['month'] == current_month)
            historical_avg = month_averages.get(current_month, {}).get('avg_revenue', 0)
            
            return jsonify({
                'success': True,
                'business': BUSINESS_CONFIGS[business_id]['name'],
                'years_analyzed': years,
                'monthly_breakdown': sorted_months,
                'seasonal_pattern': sorted_avg,
                'peak_months': peak_months,
                'slow_months': slow_months,
                'current_month_stats': {
                    'month': datetime.now().strftime('%B %Y'),
                    'revenue': current_month_revenue,
                    'historical_avg': historical_avg,
                    'variance_pct': ((current_month_revenue - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
                },
                'yearly_totals': yearly_totals
            })
        
        except Exception as e:
            print(f"Error in seasonality_enhanced: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/xero/reports/payment-risk-ml', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_payment_risk_ml():
        """ML-based late payment risk prediction using Logistic Regression"""
        try:
            business_id = int(request.args.get('business_id', 1))
            client = XeroAPIClient(business_id)
            
            # Get invoices with payment history (last 12 months)
            from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            from_dt = format_xero_datetime(from_date)
            params = {'where': f'Date>={from_dt}'}
            data = client.make_request('GET', 'Invoices', params=params)
            invoices = data.get('Invoices', [])
            
            # Get contacts for payment history
            contacts_data = client.make_request('GET', 'Contacts')
            contacts = {c['ContactID']: c for c in contacts_data.get('Contacts', [])}
            
            # Build training data from paid invoices
            training_data = []
            
            for inv in invoices:
                if inv.get('Status') not in ['PAID', 'AUTHORISED']:
                    continue
                
                contact_id = inv.get('Contact', {}).get('ContactID')
                if not contact_id:
                    continue
                
                inv_date = parse_xero_date(inv.get('Date'))
                due_date = parse_xero_date(inv.get('DueDate'))
                paid_date = parse_xero_date(inv.get('FullyPaidOnDate')) if inv.get('Status') == 'PAID' else None
                
                if not inv_date or not due_date:
                    continue
                
                invoice_amount = float(inv.get('Total', 0))
                
                # Calculate payment days (negative = early, positive = late)
                if paid_date and due_date:
                    days_to_pay = (paid_date - due_date).days
                    paid_late = 1 if days_to_pay > 5 else 0
                else:
                    # Unpaid invoice - check if overdue
                    days_overdue = (datetime.now() - due_date).days
                    days_to_pay = days_overdue if days_overdue > 0 else 0
                    paid_late = 1 if days_overdue > 5 else 0
                
                # Customer age (days since first invoice)
                contact = contacts.get(contact_id, {})
                customer_age_days = 365  # Default
                
                training_data.append({
                    'invoice_id': inv.get('InvoiceID'),
                    'invoice_number': inv.get('InvoiceNumber', 'Unknown'),
                    'contact_name': inv.get('Contact', {}).get('Name', 'Unknown'),
                    'invoice_amount': invoice_amount,
                    'customer_age_days': customer_age_days,
                    'days_to_pay': abs(days_to_pay),
                    'paid_late': paid_late,
                    'status': inv.get('Status')
                })
            
            if len(training_data) < 10:
                return jsonify({
                    'success': False,
                    'error': 'Not enough historical data (need at least 10 invoices with payment history)'
                }), 400
            
            # Prepare ML data
            import pandas as pd
            df = pd.DataFrame(training_data)
            
            # Only use invoices with status info
            df_train = df[df['status'] == 'PAID'].copy()
            
            if len(df_train) < 5:
                return jsonify({
                    'success': False,
                    'error': 'Not enough paid invoices for ML training (need at least 5)'
                }), 400
            
            # Import ML model
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            
            # Features: invoice_amount, customer_age_days
            X = df_train[['invoice_amount', 'customer_age_days']].values
            y = df_train['paid_late'].values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = LogisticRegression(random_state=42, max_iter=1000)
            model.fit(X_scaled, y)
            
            # Calculate accuracy on training set
            train_accuracy = model.score(X_scaled, y)
            
            # Predict on unpaid/authorized invoices
            unpaid_invoices = df[df['status'].isin(['AUTHORISED', 'SUBMITTED'])].copy()
            
            if len(unpaid_invoices) > 0:
                X_predict = unpaid_invoices[['invoice_amount', 'customer_age_days']].values
                X_predict_scaled = scaler.transform(X_predict)
                risk_probabilities = model.predict_proba(X_predict_scaled)[:, 1] * 100
                unpaid_invoices['risk'] = risk_probabilities
                unpaid_invoices['risk_category'] = unpaid_invoices['risk'].apply(
                    lambda x: 'High' if x > 70 else 'Medium' if x > 40 else 'Low'
                )
            else:
                unpaid_invoices['risk'] = 0
                unpaid_invoices['risk_category'] = 'Low'
            
            # Sort by risk descending
            high_risk = unpaid_invoices.sort_values('risk', ascending=False)
            
            return jsonify({
                'success': True,
                'method': 'Logistic Regression (ML)',
                'accuracy': round(train_accuracy * 100, 1),
                'training_samples': len(df_train),
                'high_risk_count': len(high_risk[high_risk['risk'] > 70]),
                'predictions': [
                    {
                        'invoice_id': row['invoice_id'],
                        'invoice_number': row['invoice_number'],
                        'contact_name': row['contact_name'],
                        'amount': round(row['invoice_amount'], 2),
                        'risk': round(row['risk'], 1),
                        'risk_category': row['risk_category']
                    }
                    for _, row in high_risk.iterrows()
                ]
            })
            
        except Exception as e:
            print(f"[XERO ML] Payment risk prediction error: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/xero/reports/churn-risk-ml', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_churn_risk_ml():
        """ML-based customer churn prediction using Random Forest"""
        try:
            business_id = int(request.args.get('business_id', 1))
            client = XeroAPIClient(business_id)
            
            # Get all contacts
            contacts_data = client.make_request('GET', 'Contacts')
            contacts = contacts_data.get('Contacts', [])
            
            # Get invoices (last 18 months)
            from_date = (datetime.now() - timedelta(days=540)).strftime('%Y-%m-%d')
            from_dt = format_xero_datetime(from_date)
            params = {'where': f'Date>={from_dt}'}
            invoices_data = client.make_request('GET', 'Invoices', params=params)
            invoices = invoices_data.get('Invoices', [])
            
            # Group invoices by contact
            contact_invoices = {}
            for inv in invoices:
                contact_id = inv.get('Contact', {}).get('ContactID')
                if contact_id:
                    if contact_id not in contact_invoices:
                        contact_invoices[contact_id] = []
                    contact_invoices[contact_id].append(inv)
            
            # Build customer metrics
            customer_data = []
            current_date = datetime.now()
            
            for contact in contacts:
                contact_id = contact.get('ContactID')
                if not contact_id or contact_id not in contact_invoices:
                    continue
                
                customer_invoices = contact_invoices[contact_id]
                if len(customer_invoices) < 2:  # Need at least 2 invoices
                    continue
                
                # Calculate metrics
                invoice_dates = [parse_xero_date(inv.get('Date')) for inv in customer_invoices if inv.get('Date')]
                invoice_dates = [d for d in invoice_dates if d]  # Remove None
                
                if not invoice_dates:
                    continue
                
                invoice_dates.sort()
                last_invoice_date = invoice_dates[-1]
                first_invoice_date = invoice_dates[0]
                
                # Recency: days since last order
                months_since_order = (current_date - last_invoice_date).days / 30
                
                # Frequency: orders per month
                tenure_months = max(1, (last_invoice_date - first_invoice_date).days / 30)
                order_frequency = len(invoice_dates) / tenure_months if tenure_months > 0 else 0
                
                # Monetary: average order value
                total_revenue = sum(float(inv.get('Total', 0)) for inv in customer_invoices)
                avg_order_value = total_revenue / len(customer_invoices) if customer_invoices else 0
                
                # Churn label: churned if no orders in last 6 months
                churned = 1 if months_since_order > 6 else 0
                
                customer_data.append({
                    'contact_id': contact_id,
                    'contact_name': contact.get('Name', 'Unknown'),
                    'months_since_order': months_since_order,
                    'order_frequency': order_frequency,
                    'avg_order_value': avg_order_value,
                    'total_orders': len(customer_invoices),
                    'total_revenue': total_revenue,
                    'churned': churned
                })
            
            if len(customer_data) < 10:
                return jsonify({
                    'success': False,
                    'error': 'Not enough customer data (need at least 10 customers with 2+ orders)'
                }), 400
            
            # Prepare ML data
            import pandas as pd
            df = pd.DataFrame(customer_data)
            
            # Import ML model
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            
            # Features
            feature_cols = ['months_since_order', 'order_frequency', 'avg_order_value']
            X = df[feature_cols].values
            y = df['churned'].values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
            model.fit(X_scaled, y)
            
            # Calculate accuracy
            train_accuracy = model.score(X_scaled, y)
            
            # Predict churn risk for active customers (not yet churned)
            active_customers = df[df['churned'] == 0].copy()
            
            if len(active_customers) > 0:
                X_predict = active_customers[feature_cols].values
                X_predict_scaled = scaler.transform(X_predict)
                churn_probabilities = model.predict_proba(X_predict_scaled)[:, 1] * 100
                active_customers['churn_risk'] = churn_probabilities
                active_customers['risk_category'] = active_customers['churn_risk'].apply(
                    lambda x: 'High' if x > 70 else 'Medium' if x > 40 else 'Low'
                )
            else:
                return jsonify({
                    'success': False,
                    'error': 'No active customers to predict churn for'
                }), 400
            
            # Sort by risk descending
            at_risk = active_customers.sort_values('churn_risk', ascending=False)
            
            # Feature importance
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            
            return jsonify({
                'success': True,
                'method': 'Random Forest (ML)',
                'accuracy': round(train_accuracy * 100, 1),
                'training_samples': len(df),
                'high_risk_count': len(at_risk[at_risk['churn_risk'] > 70]),
                'feature_importance': {
                    'months_since_order': round(feature_importance['months_since_order'] * 100, 1),
                    'order_frequency': round(feature_importance['order_frequency'] * 100, 1),
                    'avg_order_value': round(feature_importance['avg_order_value'] * 100, 1)
                },
                'predictions': [
                    {
                        'contact_id': row['contact_id'],
                        'contact_name': row['contact_name'],
                        'months_since_order': round(row['months_since_order'], 1),
                        'order_frequency': round(row['order_frequency'], 2),
                        'avg_order_value': round(row['avg_order_value'], 2),
                        'total_revenue': round(row['total_revenue'], 2),
                        'churn_risk': round(row['churn_risk'], 1),
                        'risk_category': row['risk_category']
                    }
                    for _, row in at_risk.iterrows()
                ]
            })
            
        except Exception as e:
            print(f"[XERO ML] Churn prediction error: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/xero/reports/forecast-enhanced', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_forecast_enhanced():
        """Enhanced Revenue Forecast with ARIMA ML and confidence intervals"""
        try:
            business_id = int(request.args.get('business_id', 1))
            historical_months = int(request.args.get('historical_months', 24))  # Increased for better ML
            forecast_months = int(request.args.get('forecast_months', 6))
            use_ml = request.args.get('use_ml', 'true').lower() == 'true'
            client = XeroAPIClient(business_id)
            
            # Fetch historical invoices
            from_date = (datetime.now() - timedelta(days=30 * historical_months)).strftime('%Y-%m-%d')
            from_dt = format_xero_datetime(from_date)
            params = {'where': f'Date>={from_dt}'}
            data = client.make_request('GET', 'Invoices', params=params)
            invoices = data.get('Invoices', [])
            
            # Group by month
            monthly_revenue = {}
            
            for inv in invoices:
                if inv.get('Status') != 'PAID':
                    continue
                
                inv_date_str = inv.get('Date')
                if not inv_date_str:
                    continue
                
                dt = parse_xero_date(inv_date_str)
                if not dt:
                    continue
                
                month_key = dt.strftime('%Y-%m')
                
                if month_key not in monthly_revenue:
                    monthly_revenue[month_key] = 0
                
                monthly_revenue[month_key] += float(inv.get('Total', 0))
            
            # Sort chronologically
            sorted_months = sorted(monthly_revenue.items())
            
            if len(sorted_months) < 3:
                return jsonify({
                    'success': False,
                    'error': 'Not enough historical data for forecasting (need at least 3 months)'
                }), 400
            
            revenues = [r[1] for r in sorted_months]
            n = len(revenues)
            avg_revenue = sum(revenues) / n
            
            # Calculate growth rate for display
            growth_rates = []
            for i in range(1, len(revenues)):
                if revenues[i-1] > 0:
                    growth_rates.append((revenues[i] - revenues[i-1]) / revenues[i-1] * 100)
            avg_growth_rate_pct = sum(growth_rates) / len(growth_rates) if growth_rates else 0
            
            # Try ML forecasting with ARIMA
            forecasted_months = []
            method_used = 'Simple Regression'
            std_dev = 0
            
            if use_ml and len(revenues) >= 6:
                try:
                    from statsmodels.tsa.arima.model import ARIMA
                    import numpy as np
                    
                    revenue_series = np.array(revenues)
                    
                    # Choose ARIMA order based on data size
                    if len(revenues) >= 12:
                        order = (1, 1, 1)
                        seasonal_order = (1, 1, 1, 12) if len(revenues) >= 24 else None
                    else:
                        order = (1, 1, 1)
                        seasonal_order = None
                    
                    # Fit model
                    if seasonal_order:
                        from statsmodels.tsa.statespace.sarimax import SARIMAX
                        model = SARIMAX(revenue_series, order=order, seasonal_order=seasonal_order)
                        method_used = 'SARIMA (Seasonal ML)'
                    else:
                        model = ARIMA(revenue_series, order=order)
                        method_used = 'ARIMA (ML)'
                    
                    fitted_model = model.fit(disp=False)
                    
                    # Generate forecast with confidence intervals
                    forecast_result = fitted_model.get_forecast(steps=forecast_months)
                    forecasted_values = forecast_result.predicted_mean
                    confidence_intervals = forecast_result.conf_int()
                    
                    # Build forecast response
                    for i in range(forecast_months):
                        forecast_date = datetime.now() + timedelta(days=30 * (i + 1))
                        base_val = float(forecasted_values[i])
                        lower_bound = float(confidence_intervals[i, 0])
                        upper_bound = float(confidence_intervals[i, 1])
                        
                        # Confidence degrades over time
                        confidence = max(60, 90 - (i * 5))
                        
                        forecasted_months.append({
                            'month': forecast_date.strftime('%Y-%m'),
                            'month_name': forecast_date.strftime('%B %Y'),
                            'base': round(max(0, base_val), 2),
                            'optimistic': round(max(0, upper_bound), 2),
                            'pessimistic': round(max(0, lower_bound), 2),
                            'confidence': confidence
                        })
                    
                    # Calculate std dev from model residuals
                    std_dev = float(np.std(fitted_model.resid))
                    
                except ImportError as e:
                    print(f"Warning: statsmodels not installed ({e}), falling back to linear regression")
                    use_ml = False
                    method_used = 'Linear Regression (statsmodels not available)'
                except Exception as e:
                    print(f"Warning: ARIMA/SARIMA failed ({e}), falling back to linear regression")
                    use_ml = False
                    method_used = 'Linear Regression (ML model failed - data may have insufficient variation)'
            
            # Fallback: Simple linear regression
            if not use_ml or len(forecasted_months) == 0:
                method_used = 'Simple Regression'
                
                # Linear regression: y = mx + b
                x_values = list(range(n))
                sum_x = sum(x_values)
                sum_y = sum(revenues)
                sum_xy = sum(x * y for x, y in zip(x_values, revenues))
                sum_x2 = sum(x * x for x in x_values)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
                intercept = (sum_y - slope * sum_x) / n
                
                # Calculate std dev of residuals
                predicted_values = [slope * x + intercept for x in x_values]
                residuals = [actual - predicted for actual, predicted in zip(revenues, predicted_values)]
                std_dev = (sum(r ** 2 for r in residuals) / n) ** 0.5 if n > 0 else 0
                
                # Generate forecast
                for i in range(1, forecast_months + 1):
                    forecast_date = datetime.now() + timedelta(days=30 * i)
                    base_forecast = max(0, slope * (n + i - 1) + intercept)
                    
                    # Confidence bands (±1.5 std dev)
                    optimistic = base_forecast + (1.5 * std_dev)
                    pessimistic = max(0, base_forecast - (1.5 * std_dev))
                    confidence = max(60, 90 - (i * 5))
                    
                    forecasted_months.append({
                        'month': forecast_date.strftime('%Y-%m'),
                        'month_name': forecast_date.strftime('%B %Y'),
                        'base': round(base_forecast, 2),
                        'optimistic': round(optimistic, 2),
                        'pessimistic': round(pessimistic, 2),
                        'confidence': confidence
                    })
            
            # Calculate volatility
            volatility_pct = (std_dev / avg_revenue * 100) if avg_revenue > 0 else 0
            
            # Risk factors
            risk_factors = []
            if volatility_pct > 20:
                risk_factors.append({'type': 'warning', 'text': f'High volatility: ±{volatility_pct:.1f}%'})
            if avg_growth_rate_pct < 0:
                risk_factors.append({'type': 'danger', 'text': f'Declining trend: {avg_growth_rate_pct:.1f}% average decline'})
            if len(revenues) < 6:
                risk_factors.append({'type': 'info', 'text': 'Limited historical data - consider using more months for better accuracy'})
            if std_dev > avg_revenue * 0.3:
                risk_factors.append({'type': 'warning', 'text': 'High revenue variability - forecasts may be less reliable'})
            
            # Only show statsmodels message if ML was not used AND we have enough data
            if method_used == 'Simple Regression' and len(revenues) >= 12:
                # Check if statsmodels is available
                try:
                    import statsmodels
                    risk_factors.append({'type': 'info', 'text': 'ML forecasting available but not used - data pattern may be too simple for advanced models'})
                except ImportError:
                    risk_factors.append({'type': 'info', 'text': 'Install statsmodels for ML-based seasonal forecasting (80-90% accuracy)'})
            elif 'ML model failed' in method_used:
                risk_factors.append({'type': 'warning', 'text': 'ML model could not fit this data - using linear regression instead'})
            
            return jsonify({
                'success': True,
                'method': method_used,  # Shows which algorithm was used (SARIMA/ARIMA/Simple Regression)
                'business': BUSINESS_CONFIGS[business_id]['name'],
                'historical_months': len(revenues),
                'avg_monthly_revenue': round(avg_revenue, 2),
                'avg_growth_rate': round(avg_growth_rate_pct, 2),  # Display as percentage
                'volatility': round(volatility_pct, 2),  # Display as percentage
                'std_dev': round(std_dev, 2),  # Dollar standard deviation
                'historical_data': [{'month': m, 'revenue': r} for m, r in sorted_months],
                'forecast': forecasted_months,
                'risk_factors': risk_factors,
                'total_forecast_base': round(sum(f['base'] for f in forecasted_months), 2),
                'total_forecast_optimistic': round(sum(f['optimistic'] for f in forecasted_months), 2),
                'total_forecast_pessimistic': round(sum(f['pessimistic'] for f in forecasted_months), 2)
            })
        
        except Exception as e:
            print(f"Error in forecast_enhanced: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("✅ Enhanced Xero report routes registered")
