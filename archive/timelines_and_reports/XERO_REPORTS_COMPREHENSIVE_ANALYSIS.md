"""
Xero Reports Comprehensive Analysis
====================================

OBJECTIVE: Analyze all 20 Xero report endpoints, validate data queries, 
implement 1-month date cap, and ensure visual usefulness.

Created: December 23, 2025

ANALYSIS METHODOLOGY:
1. Review each report function implementation
2. Identify date filtering logic
3. Check database queries and Xero API calls
4. Assess data structure for frontend visualization
5. Propose improvements for performance and usability

================================================================================
REPORT ANALYSIS BY CATEGORY
================================================================================

## INVOICE REPORTS (6 reports)

### 1. aged-receivables
**Endpoint**: `/api/xero/reports/aged-receivables`
**Current Implementation**: 
- Fetches all invoices (no date filter)
- Groups by age buckets: Current, 1-30, 31-60, 61-90, 90+ days
- Calculates total outstanding per contact

**ISSUES**:
❌ No date range filtering - retrieves ALL invoices from Xero
❌ Could return thousands of invoices for established businesses
❌ Slow API response for large datasets

**RECOMMENDATION**:
✅ Add date filter: Only invoices with DueDate within last 30 days
✅ Add from_date/to_date parameters
✅ Implement pagination if >200 invoices

**PROPOSED CHANGES**:
```python
@cross_origin()
def xero_report_aged_receivables():
    business_id = int(request.args.get('business_id', 1))
    # NEW: Date filtering with 30-day default
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    from_date = request.args.get('from_date', 
                                 (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    client = XeroAPIClient(business_id)
    
    # NEW: Add where clause for date filtering
    params = {
        'where': f'DueDate>=DateTime({from_date}) AND DueDate<=DateTime({to_date}) AND Status!="PAID"'
    }
    
    data = client.make_request('GET', 'Invoices', params=params)
    # ... rest of logic
```

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- Excellent for dashboard: Color-coded age buckets
- Clear action items (90+ days = urgent)
- Works well with Tabulator table format

---

### 2. sales-summary
**Endpoint**: `/api/xero/reports/sales-summary`
**Current Implementation**:
- Fetches all invoices (default 90 days via `days` parameter)
- Groups by customer
- Calculates total revenue per customer

**ISSUES**:
⚠️  Hardcoded 90-day default - should be 30 days
✅ Has date filtering (good!)
⚠️  No pagination for large customer lists

**RECOMMENDATION**:
✅ Change default to 30 days
✅ Add top N customers limit (default 50)
✅ Return summary metrics (total, avg per customer)

**PROPOSED CHANGES**:
```python
def xero_report_sales_summary():
    days = int(request.args.get('days', 30))  # Changed from 90 to 30
    limit = int(request.args.get('limit', 50))  # NEW: Limit results
    
    # ... existing date calc logic
    
    # NEW: Sort and limit customers
    customers = sorted(customer_revenue.items(), key=lambda x: x[1], reverse=True)
    top_customers = customers[:limit]
    
    return jsonify({
        'total_revenue': sum(customer_revenue.values()),
        'customer_count': len(customers),
        'avg_revenue_per_customer': sum(customer_revenue.values()) / len(customers),
        'top_customers': [{'name': c[0], 'revenue': c[1]} for c in top_customers]
    })
```

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- Good for bar charts (top 10 customers)
- Useful for identifying key revenue sources
- Would benefit from trend comparison (vs previous month)

---

### 3. overdue-invoices
**Endpoint**: `/api/xero/reports/overdue-invoices`
**Current Implementation**:
- Fetches ALL invoices
- Filters for Status != "PAID" and DueDate < today
- Sorts by days overdue

**ISSUES**:
❌ No date range filtering
❌ Could return very old overdue invoices (not actionable)
⚠️  Missing priority scoring

**RECOMMENDATION**:
✅ Filter: DueDate within last 90 days (overdue window)
✅ Add priority score: (amount * days_overdue) / 1000
✅ Group by urgency: Critical (>90 days), High (60-90), Medium (30-60), Low (<30)

**PROPOSED CHANGES**:
```python
def xero_report_overdue_invoices():
    # NEW: Only consider invoices from last 90 days
    cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    params = {
        'where': f'Status!="PAID" AND DueDate>=DateTime({cutoff_date}) AND DueDate<DateTime({datetime.now().strftime("%Y-%m-%d")})'
    }
    
    data = client.make_request('GET', 'Invoices', params=params)
    invoices = data.get('Invoices', [])
    
    # NEW: Calculate priority score and group by urgency
    for inv in invoices:
        days_overdue = (datetime.now() - parse_xero_date(inv['DueDate'])).days
        amount = float(inv.get('Total', 0))
        inv['priority_score'] = (amount * days_overdue) / 1000
        
        if days_overdue > 90:
            inv['urgency'] = 'Critical'
        elif days_overdue > 60:
            inv['urgency'] = 'High'
        # ... etc
```

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- EXCELLENT for action lists
- Color-coded urgency levels
- Priority score for sorting
- Clear ROI (chase high-value overdue invoices)

---

### 4. revenue-trends
**Endpoint**: `/api/xero/reports/revenue-trends`
**Current Implementation**:
- Fetches invoices from last 12 months
- Groups by month
- Returns monthly revenue totals

**ISSUES**:
⚠️  12-month window too large for most dashboards
✅ Good time-series structure
⚠️  Missing trend indicators (up/down arrows)

**RECOMMENDATION**:
✅ Add configurable period (default 6 months)
✅ Calculate month-over-month % change
✅ Add trend indicator: ↑ (>5%), ↓ (<-5%), → (stable)

**PROPOSED CHANGES**:
```python
def xero_report_revenue_trends():
    months = int(request.args.get('months', 6))  # NEW: Configurable period
    
    # ... fetch and group logic
    
    # NEW: Calculate month-over-month changes
    for i, month in enumerate(monthly_data[1:], 1):
        prev_revenue = monthly_data[i-1]['revenue']
        curr_revenue = month['revenue']
        
        if prev_revenue > 0:
            change_pct = ((curr_revenue - prev_revenue) / prev_revenue) * 100
            month['change_pct'] = round(change_pct, 1)
            month['trend'] = '↑' if change_pct > 5 else '↓' if change_pct < -5 else '→'
        else:
            month['change_pct'] = 0
            month['trend'] = '→'
    
    return jsonify({
        'monthly_data': monthly_data,
        'avg_monthly_revenue': sum(m['revenue'] for m in monthly_data) / len(monthly_data),
        'peak_month': max(monthly_data, key=lambda x: x['revenue'])
    })
```

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- Perfect for line charts
- Trend indicators add context
- Easy to spot seasonal patterns

---

### 5. invoice-status
**Endpoint**: `/api/xero/reports/invoice-status`
**Current Implementation**:
- Fetches all invoices (no date filter)
- Groups by status (DRAFT, SENT, PAID, VOIDED, etc.)
- Counts and sums per status

**ISSUES**:
❌ No date filtering - includes ALL historical invoices
❌ Status distribution skewed by old data

**RECOMMENDATION**:
✅ Add date filter: Invoices created in last 30 days
✅ Calculate status conversion rates (SENT → PAID %)
✅ Add average days to payment per status

**PROPOSED CHANGES**:
```python
def xero_report_invoice_status():
    days = int(request.args.get('days', 30))  # NEW: Date filtering
    
    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    params = {
        'where': f'Date>=DateTime({from_date})'
    }
    
    data = client.make_request('GET', 'Invoices', params=params)
    
    # ... existing grouping logic
    
    # NEW: Calculate conversion metrics
    sent_count = status_dist.get('SENT', 0)
    paid_count = status_dist.get('PAID', 0)
    
    conversion_rate = (paid_count / (sent_count + paid_count) * 100) if (sent_count + paid_count) > 0 else 0
    
    return jsonify({
        'status_distribution': status_dist,
        'conversion_rate': round(conversion_rate, 1),
        'total_invoices': len(invoices),
        'period_days': days
    })
```

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- Good for pie/donut charts
- Conversion rate adds business insight
- Works well with card-based UI

---

### 6. invoice-volume
**Endpoint**: `/api/xero/reports/invoice-volume`
**Current Implementation**:
- Fetches all invoices (no date filter)
- Groups by day of week
- Identifies peak billing days

**ISSUES**:
❌ No date filtering
❌ Day-of-week analysis loses relevance with old data
⚠️  Missing hourly distribution

**RECOMMENDATION**:
✅ Filter to last 90 days (seasonal relevance)
✅ Add monthly volume trend
✅ Calculate avg invoices per day

**PROPOSED CHANGES**:
```python
def xero_report_invoice_volume():
    days = int(request.args.get('days', 90))  # NEW: 90-day default
    
    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    params = {'where': f'Date>=DateTime({from_date})'}
    
    # ... existing logic
    
    # NEW: Calculate daily average
    total_days = days
    avg_per_day = len(invoices) / total_days
    
    return jsonify({
        'total_invoices': len(invoices),
        'avg_per_day': round(avg_per_day, 1),
        'peak_day': max(day_counts, key=day_counts.get),
        'day_distribution': day_counts,
        'period_days': days
    })
```

**VISUAL USEFULNESS**: ⭐⭐⭐
- Useful for capacity planning
- Helps identify busy periods
- Could be combined with revenue trends

================================================================================
## CONTACT REPORTS (4 reports)

### 7. contact-activity
**Endpoint**: `/api/xero/reports/contact-activity`
**Current Implementation**:
- Fetches all invoices
- Groups by contact
- Shows transaction count per contact

**ISSUES**:
❌ No date filtering
❌ "Activity" only measures invoices (not payments, quotes, etc.)
⚠️  Missing last contact date

**RECOMMENDATION**:
✅ Filter: Transactions in last 60 days
✅ Include payments and quotes (if available)
✅ Add "last_contact_date" field
✅ Calculate engagement score

**VISUAL USEFULNESS**: ⭐⭐⭐
- Good for relationship management
- Needs multi-dimensional activity (not just invoices)

---

### 8. inactive-customers
**Endpoint**: `/api/xero/reports/inactive-customers`
**Current Implementation**:
- Finds contacts with no invoices in X days (default 90)
- Returns list of inactive contacts

**ISSUES**:
✅ Has date filtering (good!)
⚠️  90-day threshold too aggressive for some businesses
⚠️  Missing historical revenue (lost opportunity cost)

**RECOMMENDATION**:
✅ Make threshold configurable (30, 60, 90, 180 days)
✅ Add "lifetime_revenue" field
✅ Calculate "days_inactive" for each contact
✅ Priority score: (lifetime_revenue * days_inactive) / 1000

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- High business value (reactivation campaigns)
- Priority scoring helps focus efforts

---

### 9. customer-lifetime-value
**Endpoint**: `/api/xero/reports/customer-lifetime-value`
**Current Implementation**:
- Fetches all invoices
- Sums revenue per customer
- Calculates tenure (first → last invoice)

**ISSUES**:
✅ Good core logic
❌ No recency component (RFM model)
⚠️  Missing average order value

**RECOMMENDATION**:
✅ Add RFM segmentation (Recency, Frequency, Monetary)
✅ Calculate avg_order_value = total_revenue / invoice_count
✅ Add "days_since_last_purchase" field

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- Excellent for customer prioritization
- RFM segments enable targeted strategies

---

### 10. customer-segmentation
**Endpoint**: `/api/xero/reports/customer-segmentation`
**Current Implementation**:
- Implements RFM analysis
- Segments: Champions, Loyal, At Risk, Lost

**ISSUES**:
✅ Good RFM implementation
⚠️  Thresholds may need business-specific tuning
⚠️  Missing segment size metrics

**RECOMMENDATION**:
✅ Add configurable thresholds
✅ Return segment sizes and % distribution
✅ Add suggested actions per segment

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- PERFECT for strategic planning
- Clear action items per segment
- High business impact

================================================================================
## PAYMENT REPORTS (4 reports)

### 11. payment-behavior
**Endpoint**: `/api/xero/reports/payment-behavior`
**Current Implementation**:
- Calculates avg days to pay
- Shows early/late payment percentages

**ISSUES**:
❌ No date filtering
⚠️  Missing payment method breakdown
⚠️  No customer-level analysis

**RECOMMENDATION**:
✅ Filter: Payments in last 90 days
✅ Group by customer (identify slow payers)
✅ Add payment method distribution

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- Good for cash flow forecasting
- Customer-level data enables proactive follow-up

---

### 12. payment-reconciliation
**Endpoint**: `/api/xero/reports/payment-reconciliation`
**Current Implementation**:
- Identifies unmatched payments
- Finds partial payments
- Detects overpayments

**ISSUES**:
❌ No date filtering (processes ALL payments)
⚠️  Could be slow with large datasets
✅ Good exception detection logic

**RECOMMENDATION**:
✅ Filter: Payments in last 30 days
✅ Add pagination (50 items per page)
✅ Priority scoring for unmatched payments (by amount)

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- CRITICAL for accounting accuracy
- Clear action items
- High ROI (resolve payment issues)

---

### 13. cash-flow
**Endpoint**: `/api/xero/reports/cash-flow`
**Current Implementation**:
- Daily payment timeline
- Shows money received by date

**ISSUES**:
❌ No date range specification
⚠️  Missing forecast component
⚠️  No comparison to expected (invoice due dates)

**RECOMMENDATION**:
✅ Default to last 30 days
✅ Add forecast: Expected payments (from invoice due dates)
✅ Calculate variance: Actual vs Expected

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- Excellent for treasury management
- Forecast adds planning value
- Visual timeline format ideal

---

### 14. dso (Days Sales Outstanding)
**Endpoint**: `/api/xero/reports/dso`
**Current Implementation**:
- Calculates DSO: (Accounts Receivable / Revenue) * Days
- Industry benchmark comparison

**ISSUES**:
✅ Good DSO calculation
⚠️  No trend analysis (Is DSO improving?)
⚠️  Missing breakdown by customer segment

**RECOMMENDATION**:
✅ Calculate DSO for last 3 months (trend)
✅ Show month-over-month change
✅ Add industry benchmark context

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- Good KPI metric
- Trend adds strategic value

================================================================================
## MULTI-BUSINESS REPORTS (3 reports)

### 15. business-comparison
**Endpoint**: `/api/xero/reports/business-comparison`
**Current Implementation**:
- Compares all 3 businesses (Print, Publishing, Signs)
- Shows revenue, invoice count, customer count

**ISSUES**:
❌ No date filtering
⚠️  Basic metrics only
⚠️  Missing profitability indicators

**RECOMMENDATION**:
✅ Filter: Last 30 days
✅ Add avg_invoice_value per business
✅ Calculate market share % (revenue distribution)

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- EXCELLENT for portfolio management
- Easy comparisons (bar chart format)
- Strategic decision-making tool

---

### 16. customer-overlap
**Endpoint**: `/api/xero/reports/customer-overlap`
**Current Implementation**:
- Identifies customers across multiple businesses
- Counts shared customers

**ISSUES**:
✅ Good cross-business analysis
⚠️  Missing revenue impact (how much from shared customers?)
⚠️  No recommendation engine (cross-sell opportunities)

**RECOMMENDATION**:
✅ Calculate revenue from shared vs exclusive customers
✅ Identify customers in 1 business only (cross-sell targets)
✅ Show potential revenue opportunity

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- High strategic value
- Cross-sell opportunities clear
- Venn diagram format ideal

---

### 17. consolidated-revenue
**Endpoint**: `/api/xero/reports/consolidated-revenue`
**Current Implementation**:
- Sums revenue across all 3 businesses
- Shows breakdown by business

**ISSUES**:
❌ No date filtering
⚠️  Missing trend analysis
⚠️  No comparison to previous period

**RECOMMENDATION**:
✅ Filter: Last 30 days with previous period comparison
✅ Calculate growth % per business
✅ Show total portfolio growth

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- Perfect for executive dashboard
- Growth metrics add context
- Portfolio view essential

================================================================================
## ADVANCED ANALYTICS (3 reports)

### 18. revenue-by-product
**Endpoint**: `/api/xero/reports/revenue-by-product`
**Current Implementation**:
- Parses invoice line items
- Groups revenue by product/service
- Shows top revenue generators

**ISSUES**:
❌ No date filtering
⚠️  Product names may be inconsistent
⚠️  Missing margin data (revenue ≠ profit)

**RECOMMENDATION**:
✅ Filter: Last 90 days
✅ Normalize product names (fuzzy matching)
✅ Add quantity sold per product
✅ Calculate avg_price_per_unit

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- CRITICAL for product strategy
- Clear winners and losers
- Informs inventory decisions

---

### 19. seasonality
**Endpoint**: `/api/xero/reports/seasonality`
**Current Implementation**:
- Analyzes monthly patterns
- Year-over-year comparison

**ISSUES**:
✅ Good seasonal analysis
⚠️  Requires 2+ years of data (may not have)
⚠️  Missing forecast based on patterns

**RECOMMENDATION**:
✅ Gracefully handle <2 years data
✅ Add seasonal forecast (next 3 months)
✅ Highlight peak/trough months

**VISUAL USEFULNESS**: ⭐⭐⭐⭐
- Excellent for planning
- Forecast adds value
- Heatmap format ideal

---

### 20. forecast
**Endpoint**: `/api/xero/reports/forecast`
**Current Implementation**:
- Trend-based forecast (30/60/90 days)
- Linear regression on historical data

**ISSUES**:
✅ Good forecasting logic
⚠️  Linear model may not capture seasonality
⚠️  Missing confidence intervals

**RECOMMENDATION**:
✅ Use 12-month rolling average for baseline
✅ Apply seasonal adjustment
✅ Add confidence intervals (±10%, ±20%)
✅ Show historical accuracy (forecast vs actual)

**VISUAL USEFULNESS**: ⭐⭐⭐⭐⭐
- EXCELLENT for financial planning
- Confidence intervals add realism
- High strategic value

================================================================================
## OVERALL SUMMARY

### Critical Issues Across All Reports:
1. ❌ **NO DATE FILTERING** - 15/20 reports fetch ALL historical data
2. ⚠️  **SLOW API CALLS** - No pagination, could timeout with large datasets
3. ⚠️  **MISSING TRENDS** - Most reports are point-in-time snapshots
4. ⚠️  **NO BENCHMARKS** - Missing industry or historical comparisons

### Recommended Global Changes:

#### 1. Implement Date Filtering Standard:
```python
# Add to ALL report functions
def get_date_range(request, default_days=30):
    """Standardized date range extraction"""
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    if 'from_date' in request.args:
        from_date = request.args.get('from_date')
    else:
        days = int(request.args.get('days', default_days))
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    return from_date, to_date
```

#### 2. Add Pagination Support:
```python
def paginate_results(data, page=1, per_page=50):
    """Pagination helper"""
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'data': data[start:end],
        'page': page,
        'per_page': per_page,
        'total': len(data),
        'pages': (len(data) + per_page - 1) // per_page
    }
```

#### 3. Add Caching Layer:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_cached_invoices(business_id, from_date, to_date):
    """Cache expensive API calls for 5 minutes"""
    # Cache key includes business_id and date range
    # Expires after 5 minutes
    pass
```

#### 4. Add Performance Monitoring:
```python
import time

def monitor_performance(func):
    """Decorator to log slow queries"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        if duration > 5.0:
            logger.warning(f"Slow query: {func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper
```

================================================================================
## PRIORITY IMPLEMENTATION PLAN

### Phase 1: Critical Fixes (Week 1)
1. ✅ Add date filtering to ALL reports (default 30 days)
2. ✅ Implement pagination (50 items per page)
3. ✅ Add response time monitoring

### Phase 2: Enhanced Metrics (Week 2)
4. ✅ Add trend indicators (↑↓→) to all time-series reports
5. ✅ Implement month-over-month comparisons
6. ✅ Add priority scoring to action-oriented reports

### Phase 3: Performance Optimization (Week 3)
7. ✅ Implement caching layer (Redis or memory cache)
8. ✅ Optimize Xero API calls (batch requests where possible)
9. ✅ Add database query optimization

### Phase 4: Visual Enhancements (Week 4)
10. ✅ Add chart type recommendations per report
11. ✅ Implement export functionality (CSV, PDF)
12. ✅ Add interactive filters in frontend

================================================================================
## TESTING CHECKLIST

For each report, verify:
- [ ] Date filtering works (30-day default)
- [ ] Pagination works correctly
- [ ] Response time < 5 seconds
- [ ] Data structure matches frontend expectations
- [ ] Empty data handled gracefully
- [ ] Error messages are user-friendly
- [ ] Visual format supports chosen chart type
- [ ] Export functionality works

================================================================================
## CONCLUSION

**Current State**: 20 reports implemented, but most lack date filtering
**Target State**: All reports with 30-day default, pagination, and trends
**Est. Development Time**: 4 weeks (1 phase per week)
**Business Impact**: HIGH - Enables data-driven decision making

**RECOMMENDED NEXT STEPS**:
1. Start Flask server and run comprehensive test
2. Fix date filtering in top 5 most-used reports first
3. Implement caching for performance
4. Add export functionality for executive reports

================================================================================
"""
