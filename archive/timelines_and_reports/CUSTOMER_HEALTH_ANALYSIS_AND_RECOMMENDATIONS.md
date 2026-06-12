# Customer Health/Churn Analysis - Full Assessment & Recommendations

## Current State: 3 Similar But Different Dashboards

### **1. Customer Health Dashboard** (Simple Time-Based)
**Location:** Contact Reports → Customer Health button  
**Backend:** `xero_routes.py` lines 2438-2541

**Logic:**
```python
# Time-based thresholds (days since last invoice):
- Active: Last invoice ≤ 30 days ago
- At-Risk: Last invoice 60-89 days ago  
- Churned: Last invoice ≥ 90 days ago
- New: First invoice ≤ 30 days ago
```

**What User Sees:**
- 4 metric cards: Total, New (7), Churned (4769), Retention (3.3%)
- 2 detail boxes: Growth (+4762) and At-Risk (28)
- Key insights bullets

**PROBLEM: No customer list - just numbers!**  
User cannot see WHO the 28 at-risk customers are.

---

### **2. Customer Segmentation (RFM)** (Score-Based)
**Location:** Contact Reports → Customer Segmentation button  
**Backend:** `xero_routes.py` lines 2331-2430

**Logic:**
```python
# RFM Scoring (1-5 for each):
1. Recency Score: How recently they purchased
2. Frequency Score: How often they purchase  
3. Monetary Score: How much they spend

# Total RFM Score (3-15) determines segment:
- Champions: 13-15 (best customers)
- Loyal Customers: 10-12
- Potential Loyalists: 7-9
- At Risk: 5-6
- Lost: 0-4
```

**What User Sees:**
- 5 colored boxes showing count per segment:
  - Champions: X customers
  - Loyal Customers: X customers
  - Potential Loyalists: X customers
  - At Risk: X customers
  - Lost: X customers

**PROBLEM: No customer list - just segment counts!**  
User cannot see WHO is in each segment.

**Data Available But Not Shown:**
The backend returns a `customers` array with:
- contact_name
- recency_days, frequency_score, monetary_score
- rfm_score
- segment

This data exists but the UI only shows the counts!

---

### **3. Customer Churn Prediction (ML)** (Machine Learning)
**Location:** Reports → ML-Powered Predictions → Customer Churn button  
**Backend:** `xero_reports_enhanced.py` (not found, likely deleted)

**Logic:**
```python
# Random Forest ML model predicts churn probability (0-100%):
Features:
1. Months since last order (recency)
2. Order frequency (orders per month)
3. Average order value (monetary)

# Risk categories:
- High Risk: >70% churn probability
- Medium Risk: 40-70% churn probability  
- Low Risk: <40% churn probability
```

**What User Sees:**
- 4 metric cards: High Risk (0), Medium Risk (0), Low Risk (210), Total Analyzed (292)
- Feature Importance chart (what matters most: 80.8% recency, 9.6% frequency, 9.6% value)
- Scatter plot showing risk vs months since order
- **✅ FULL TABLE with all customers** showing:
  - Customer name
  - Churn risk %
  - Risk category (colored badge)
  - Months since order
  - Order frequency
  - Lifetime revenue

**✅ THIS IS THE ONLY ONE WITH A CUSTOMER LIST!**

---

## Why Are The Numbers So Different?

### **Customer Health Dashboard:**
- **At-Risk: 28 customers** (60-89 days no invoice)
- **Churned: 4769 customers** (90+ days no invoice)

### **Customer Segmentation (RFM):**
- **At Risk: ? customers** (RFM score 5-6)
- **Lost: ? customers** (RFM score 0-4)

### **Customer Churn Prediction (ML):**
- **High Risk: 0 customers** (>70% ML churn prediction)
- **Medium Risk: 0 customers** (40-70% ML churn prediction)
- **Low Risk: 210 customers** (<40% ML churn prediction)

### **Why Different?**

| Dashboard | Definition of "At-Risk" | Considers Multiple Factors? | ML-Based? |
|-----------|-------------------------|----------------------------|-----------|
| **Customer Health** | 60-89 days no invoice | ❌ Only time | ❌ No |
| **RFM Segmentation** | RFM score 5-6 (low recency + frequency + value) | ✅ Yes (3 factors) | ❌ No |
| **ML Churn Prediction** | >40% ML churn probability | ✅ Yes (3+ factors + patterns) | ✅ Yes |

**Example: Why a customer might be "At-Risk" in one but not another:**

**Customer A:**
- Last invoice: 65 days ago
- Frequency: Orders every 90 days (normally)
- Lifetime value: $50,000

| Dashboard | Classification | Reasoning |
|-----------|----------------|-----------|
| Customer Health | ✅ **At-Risk** | 60-89 day window |
| RFM Segmentation | ✅ **Loyal Customer** | High monetary score overcomes recency |
| ML Churn Prediction | ❌ **Low Risk (15%)** | Pattern shows 90-day cycle = normal |

---

## The Real Problem: Lack of Actionability

### **What Users Need:**
1. ✅ **WHO is at risk?** (names, not just counts)
2. ✅ **WHY are they at risk?** (recency? frequency? value?)
3. ✅ **WHAT should I do?** (call them? send email? offer discount?)
4. ✅ **WHEN should I act?** (today? this week? this month?)

### **What Users Currently Get:**

| Feature | Customer Health | RFM Segmentation | ML Churn Prediction |
|---------|----------------|------------------|---------------------|
| **Customer Names** | ❌ No | ❌ No | ✅ **YES** |
| **Risk Score** | ❌ No | ❌ No | ✅ **YES (0-100%)** |
| **Risk Category** | ✅ Yes (3 buckets) | ✅ Yes (5 segments) | ✅ **YES (3 levels)** |
| **Reason for Risk** | ❌ No | ❌ No | ✅ **YES (feature importance)** |
| **Actionable Insights** | ⚠️ Generic bullets | ❌ No | ⚠️ Charts only |
| **Export List** | ❌ No | ❌ No | ⚠️ Table copy only |
| **Contact Links** | ❌ No | ❌ No | ❌ No |

---

## Recommended Solutions

### **Option 1: Fix Existing Dashboards (Quick Win - 2 hours)**

#### **A. Add Customer Lists to Customer Health**
```javascript
// After showing metrics, add table:
new Tabulator('#customer-health-table', {
    data: [
        { name: 'Customer A', days_since: 65, status: 'At-Risk', revenue: 50000 },
        // ... 28 at-risk customers
    ],
    columns: [
        { title: 'Customer', field: 'name' },
        { title: 'Days Since Last Invoice', field: 'days_since' },
        { title: 'Status', field: 'status' },
        { title: 'Lifetime Revenue', field: 'revenue', formatter: 'money' }
    ]
});
```

**What Changes:**
- ✅ Add "At-Risk Customers (28)" expandable section
- ✅ Show table with customer names, days inactive, revenue
- ✅ Add "Contact Customer" button (opens Xero contact page)

#### **B. Add Customer Lists to RFM Segmentation**
```javascript
// Backend already returns customers array - just show it!
// Change from showing only counts to showing:
1. Segment counts (keep existing)
2. NEW: Expandable sections for each segment
3. NEW: Table showing top 50 customers per segment

// Example:
"At Risk (42 customers)" [Expand ▼]
  → Table: Name | RFM Score | Recency | Frequency | Monetary
```

**What Changes:**
- ✅ Keep existing segment count cards
- ✅ Add expandable table for each segment
- ✅ Show RFM breakdown (why they're in that segment)

---

### **Option 2: Consolidate Into One Unified Dashboard (Best Long-Term - 4 hours)**

**New: "Customer Risk Intelligence Dashboard"**

**Layout:**

```
╔════════════════════════════════════════════════════════════════╗
║  🎯 Customer Risk Intelligence Dashboard                      ║
║  [Powered by ML + RFM Analysis]                               ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  📊 QUICK METRICS                                             ║
║  ┌─────────┬─────────┬─────────┬─────────┬─────────┐        ║
║  │ Total   │ Active  │ At-Risk │ Lost    │ Growth  │        ║
║  │ 4932    │ 150     │ 42      │ 4740    │ +4762   │        ║
║  └─────────┴─────────┴─────────┴─────────┴─────────┘        ║
║                                                                ║
║  🚨 ACTION REQUIRED (42 customers)                            ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ Filter: [All] [High Risk] [Medium Risk] [Call Today] │   ║
║  │                                                        │   ║
║  │ Customer         │ Risk  │ Category │ Last Order │ Action│
║  │ ─────────────────┼───────┼──────────┼───────────┼──────│
║  │ ABC Corp         │ 87%   │ High     │ 85 days   │ 📞 Call│
║  │ XYZ Ltd          │ 76%   │ High     │ 92 days   │ 📞 Call│
║  │ Smith Inc        │ 68%   │ Medium   │ 65 days   │ ✉️ Email│
║  │ ...              │       │          │           │       │
║  └──────────────────────────────────────────────────────┘   ║
║                                                                ║
║  📈 INSIGHTS & TRENDS                                         ║
║  • 12 customers moved from "At-Risk" to "Lost" this month    ║
║  • Top churn driver: Time since order (81% importance)        ║
║  • Avg time to churn: 94 days (was 87 days last month)       ║
║                                                                ║
║  💡 RECOMMENDED ACTIONS                                       ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ TODAY (3 customers)                                     │  ║
║  │ • Call ABC Corp (87% churn risk, $50K lifetime value)  │  ║
║  │ • Call XYZ Ltd (76% churn risk, $35K lifetime value)   │  ║
║  │                                                         │  ║
║  │ THIS WEEK (15 customers)                               │  ║
║  │ • Email campaign to 15 medium-risk customers           │  ║
║  │ • Offer: 10% discount for next order                   │  ║
║  │                                                         │  ║
║  │ THIS MONTH (24 customers)                              │  ║
║  │ • Re-engagement campaign for low-risk customers        │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  [📥 Export At-Risk List] [📧 Send to Sales Team] [📊 Details]║
╚════════════════════════════════════════════════════════════════╝
```

**What This Combines:**
1. ✅ **Customer Health metrics** (total, active, growth)
2. ✅ **RFM Segmentation logic** (multi-factor scoring)
3. ✅ **ML Churn Prediction** (accurate risk scores)
4. ✅ **Actionable customer list** (names, not just numbers)
5. ✅ **Recommended actions** (call today, email this week)
6. ✅ **Export functionality** (CSV, send to sales team)

**Key Features:**
- **Real-time filtering:** High risk only, call today, email campaign
- **Click to contact:** Clicking customer name opens Xero contact page
- **Bulk actions:** Select 10 customers → "Add to email campaign"
- **Historical tracking:** "12 customers moved from At-Risk to Lost" (trend analysis)

---

### **Option 3: Add "View Details" Links to Existing Dashboards (Hybrid - 1 hour)**

**Quick fix without rebuilding:**

#### **Customer Health Dashboard:**
```javascript
// Add click handler to "At-Risk (28)" card:
<div onclick="showAtRiskDetails()" style="cursor: pointer;">
    <div>28</div>
    <div>At-Risk Customers</div>
    <div style="font-size: 10px; color: #13B5EA;">Click to view list →</div>
</div>

// When clicked, opens modal with table:
showAtRiskDetails() {
    // Fetch /api/xero/reports/customer-health-details?category=at_risk
    // Show table with customer names
}
```

#### **RFM Segmentation:**
```javascript
// Change from static counts to clickable cards:
<div onclick="showSegmentDetails('At Risk')" style="cursor: pointer;">
    <div>At Risk</div>
    <div>42</div>
    <div style="font-size: 10px; color: #13B5EA;">Click to view customers →</div>
</div>

// When clicked, shows table from existing backend data:
showSegmentDetails(segment) {
    // Filter customers array by segment
    // Show table with RFM scores
}
```

**Benefit:** Minimal code changes, adds discoverability without rebuilding.

---

## Decision Matrix: Which Option to Implement?

| Option | Time | Complexity | User Value | Maintenance |
|--------|------|------------|------------|-------------|
| **Option 1: Fix Existing** | 2 hours | Low | Medium | High (3 dashboards) |
| **Option 2: Consolidate** | 4 hours | Medium | **High** | Low (1 dashboard) |
| **Option 3: Add Links** | 1 hour | **Low** | **Medium** | High (3 dashboards) |

### **Recommendation: Option 2 (Consolidate)**

**Why:**
1. ✅ **Best user experience** - One place for all customer risk analysis
2. ✅ **Actionable** - Names, risk scores, recommended actions
3. ✅ **Accurate** - Combines rule-based (RFM) + ML predictions
4. ✅ **Less confusing** - No more "why are the numbers different?"
5. ✅ **Lower maintenance** - One dashboard instead of three
6. ✅ **Scalable** - Easy to add new features (email campaigns, call tracking)

**Implementation Plan:**

### **Phase 1: Backend (1 hour)**
```python
# New endpoint: /api/xero/reports/customer-risk-intelligence
@cross_origin()
def xero_report_customer_risk_intelligence():
    """Unified customer risk dashboard combining ML + RFM + time-based logic"""
    
    # 1. Fetch all customers
    # 2. Calculate ML churn prediction (existing logic)
    # 3. Calculate RFM scores (existing logic)
    # 4. Calculate time-based risk (existing logic)
    # 5. Create weighted risk score: (ML: 50%, RFM: 30%, Time: 20%)
    # 6. Generate recommended actions based on risk level
    # 7. Return unified dataset
    
    return {
        'success': True,
        'metrics': {
            'total_customers': 4932,
            'active': 150,
            'at_risk': 42,
            'lost': 4740,
            'net_growth': 4762
        },
        'customers': [
            {
                'name': 'ABC Corp',
                'risk_score': 87,  # 0-100% (weighted)
                'risk_category': 'High',  # High/Medium/Low
                'ml_churn_prob': 89,
                'rfm_segment': 'At Risk',
                'days_since_order': 85,
                'lifetime_revenue': 50000,
                'order_frequency': 0.3,
                'recommended_action': 'call_today',  # call_today/email_this_week/monitor
                'action_priority': 1  # 1-5 (1 = urgent)
            },
            # ... all customers
        ],
        'insights': [
            {'type': 'alert', 'text': '12 customers moved from At-Risk to Lost this month'},
            {'type': 'info', 'text': 'Top churn driver: Time since order (81% importance)'}
        ],
        'actions': {
            'call_today': ['ABC Corp', 'XYZ Ltd'],  # 3 customers
            'email_this_week': ['Smith Inc', ...],  # 15 customers
            'monitor': [...]  # 24 customers
        }
    }
```

### **Phase 2: Frontend (2 hours)**
```javascript
// xero.js - New function
async showCustomerRiskIntelligence() {
    // 1. Fetch unified data
    const data = await fetch('/api/xero/reports/customer-risk-intelligence');
    
    // 2. Render metrics cards (existing pattern)
    
    // 3. Render action-required table (Tabulator)
    new Tabulator('#risk-table', {
        data: data.customers,
        columns: [
            { title: 'Customer', field: 'name', formatter: linkFormatter },
            { title: 'Risk Score', field: 'risk_score', formatter: riskBadgeFormatter },
            { title: 'Category', field: 'risk_category', formatter: categoryBadgeFormatter },
            { title: 'Last Order', field: 'days_since_order', formatter: daysFormatter },
            { title: 'Action', field: 'recommended_action', formatter: actionButtonFormatter }
        ],
        rowClick: (e, row) => {
            // Open Xero contact page in new tab
            window.open(`https://go.xero.com/Contacts/View/${row.getData().contact_id}`, '_blank');
        }
    });
    
    // 4. Render insights
    
    // 5. Render recommended actions grouped by urgency
}
```

### **Phase 3: Polish (1 hour)**
- ✅ Add export to CSV button
- ✅ Add "Send to Sales Team" email button
- ✅ Add filters (high risk only, call today, etc.)
- ✅ Add historical comparison ("12 customers moved to Lost")

---

## Alternative: Quick Wins (30 minutes each)

### **Quick Win #1: Add "View Details" to ML Churn Prediction**
**Problem:** ML dashboard shows table but no export/email functionality  
**Solution:** Add buttons:
```javascript
[📥 Export At-Risk List (CSV)] [📧 Email Sales Team] [📞 Add to Call List]
```

### **Quick Win #2: Show Customer Count in Customer Health**
**Problem:** Shows "28 At-Risk" but no way to see who they are  
**Solution:** Add expandable section:
```javascript
<div onclick="toggleAtRiskList()">
    <div>28 At-Risk Customers</div>
    <div style="font-size: 10px;">Click to expand ▼</div>
</div>
<div id="at-risk-list" style="display: none;">
    <!-- Table with 28 customers -->
</div>
```

### **Quick Win #3: Link Dashboards Together**
**Problem:** Users don't know there are 3 different dashboards  
**Solution:** Add cross-links:
```javascript
// In Customer Health:
"For detailed RFM analysis, see [Customer Segmentation →]"
"For ML predictions, see [Churn Prediction (ML) →]"

// In RFM Segmentation:
"For time-based analysis, see [Customer Health →]"
"For ML predictions, see [Churn Prediction (ML) →]"

// In ML Churn Prediction:
"For time-based analysis, see [Customer Health →]"
"For RFM segments, see [Customer Segmentation →]"
```

---

## Summary: What Should You Do?

### **If You Have 4 Hours:**
✅ **Implement Option 2: Unified Dashboard**
- Best user experience
- Most actionable
- Easiest to maintain
- Highest ROI

### **If You Have 1 Hour:**
✅ **Implement Quick Wins 1-3**
- Add export buttons to ML dashboard
- Add expandable customer lists to existing dashboards
- Link dashboards together

### **If You Have 30 Minutes:**
✅ **Fix RFM Segmentation Only**
- Backend already returns customer data
- Just show it in a table (already have Tabulator code)
- Biggest bang for buck (5 segments of customers revealed)

---

## Next Steps

**Tell me which option you prefer and I'll implement it:**

1. **Option 1:** Fix existing dashboards (add customer lists)
2. **Option 2:** Create unified risk dashboard (best long-term)
3. **Option 3:** Add "view details" links (quickest)
4. **Quick Wins:** Just add export/expand functionality
5. **Custom:** Mix and match features you want

**I recommend Option 2 (Unified Dashboard)** because it solves all the problems:
- ✅ Shows customer names (not just numbers)
- ✅ Explains risk reasons (ML + RFM + time)
- ✅ Provides actionable steps (call today, email this week)
- ✅ Eliminates confusion (one source of truth)
- ✅ Easy to export/share (CSV, email)

**Which would you like me to build?**
