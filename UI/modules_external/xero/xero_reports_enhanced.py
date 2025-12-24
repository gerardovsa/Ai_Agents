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
    
    
    @app.route('/api/xero/reports/forecast-enhanced', methods=['GET', 'OPTIONS'])
    @cross_origin()
    def xero_report_forecast_enhanced():
        """Enhanced Revenue Forecast with confidence intervals and scenarios"""
        try:
            business_id = int(request.args.get('business_id', 1))
            historical_months = int(request.args.get('historical_months', 12))
            forecast_months = int(request.args.get('forecast_months', 6))
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
            
            if len(sorted_months) < 2:
                return jsonify({
                    'success': False,
                    'error': 'Not enough historical data for forecasting (need at least 2 months)'
                }), 400
            
            # Calculate trend metrics using linear regression
            revenues = [r[1] for r in sorted_months]
            n = len(revenues)
            avg_revenue = sum(revenues) / n
            
            # Simple linear regression: y = mx + b
            # Calculate slope (m) and intercept (b)
            x_values = list(range(n))  # 0, 1, 2, ... n-1
            sum_x = sum(x_values)
            sum_y = sum(revenues)
            sum_xy = sum(x * y for x, y in zip(x_values, revenues))
            sum_x2 = sum(x * x for x in x_values)
            
            # Slope: m = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
            
            # Intercept: b = (Σy - m*Σx) / n
            intercept = (sum_y - slope * sum_x) / n
            
            # Calculate standard deviation of residuals for confidence intervals
            predicted_values = [slope * x + intercept for x in x_values]
            residuals = [actual - predicted for actual, predicted in zip(revenues, predicted_values)]
            std_dev = (sum(r ** 2 for r in residuals) / n) ** 0.5 if n > 0 else 0
            
            # Calculate average growth rate as percentage (for display)
            growth_rates = []
            for i in range(1, len(revenues)):
                if revenues[i-1] > 0:
                    growth_rates.append((revenues[i] - revenues[i-1]) / revenues[i-1] * 100)
            avg_growth_rate_pct = sum(growth_rates) / len(growth_rates) if growth_rates else 0
            
            # Calculate volatility (coefficient of variation)
            volatility_pct = (std_dev / avg_revenue * 100) if avg_revenue > 0 else 0
            
            # Generate forecast scenarios using linear trend
            forecasted_months = []
            
            for i in range(1, forecast_months + 1):
                forecast_date = datetime.now() + timedelta(days=30 * i)
                
                # Base forecast using linear regression
                # x = n + i - 1 (continue the series)
                base_forecast = slope * (n + i - 1) + intercept
                
                # Ensure non-negative forecasts
                base_forecast = max(0, base_forecast)
                
                # Optimistic scenario: +1.5 std dev
                optimistic = base_forecast + (1.5 * std_dev)
                
                # Pessimistic scenario: -1.5 std dev (but not below zero)
                pessimistic = max(0, base_forecast - (1.5 * std_dev))
                
                # Confidence degrades over time (90% → 60%)
                confidence = max(60, 90 - (i * 5))
                
                forecasted_months.append({
                    'month': forecast_date.strftime('%Y-%m'),
                    'month_name': forecast_date.strftime('%B %Y'),
                    'base': round(base_forecast, 2),
                    'optimistic': round(optimistic, 2),
                    'pessimistic': round(pessimistic, 2),
                    'confidence': confidence
                })
            
            # Risk factors based on linear model
            risk_factors = []
            if volatility_pct > 20:
                risk_factors.append({'type': 'warning', 'text': f'High volatility: ±{volatility_pct:.1f}%'})
            if slope < 0:
                monthly_decline = abs(slope)
                risk_factors.append({'type': 'danger', 'text': f'Declining trend: ${monthly_decline:,.0f}/month decline'})
            elif avg_growth_rate_pct < 0:
                risk_factors.append({'type': 'warning', 'text': f'Negative average growth: {avg_growth_rate_pct:.1f}%'})
            if len(revenues) < 6:
                risk_factors.append({'type': 'info', 'text': 'Limited historical data - lower confidence'})
            if std_dev > avg_revenue * 0.3:
                risk_factors.append({'type': 'warning', 'text': 'High revenue variability - forecasts less reliable'})
            
            return jsonify({
                'success': True,
                'business': BUSINESS_CONFIGS[business_id]['name'],
                'historical_months': historical_months,
                'avg_monthly_revenue': round(avg_revenue, 2),
                'avg_growth_rate': round(avg_growth_rate_pct, 2),  # Display as percentage
                'monthly_trend': round(slope, 2),  # Dollar change per month
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
