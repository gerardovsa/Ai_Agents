# Invoice ML Dashboard - Complete Design Specification
**Last Updated:** January 2, 2026

---

## 🎯 Design Philosophy

**Core Principle:** Every customer/contact row across ALL ML dashboards (Invoice Risk Scoring, Smart Collection Queue, Customer Intelligence, Cohort Analysis, etc.) should be **clickable** to reveal a comprehensive modal with:
1. **Customer Profile** (name, contact info, account details)
2. **Transaction History** (invoices, payments, timeline)
3. **ML Insights** (risk scores, churn probability, LTV, segment, behavior trends)
4. **Actionable Recommendations** (next best action, contact timing, scenario impacts)
5. **Quick Actions** (send email, make call, create invoice, apply discount)

---

## 📊 Invoice Tab - ML Dashboard Layout

### **1. Invoice Risk Scoring Dashboard**

#### **Top Summary Cards (4 metrics)**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  HIGH RISK  │  │ MEDIUM RISK │  │  LOW RISK   │  │  SAFE TOTAL │  │
│  │   $125,400  │  │   $89,200   │  │  $245,800   │  │  $460,400   │  │
│  │  12 invoices│  │ 23 invoices │  │ 65 invoices │  │ 100 invoices│  │
│  │   📈 +15%   │  │   📊 +5%    │  │   📉 -8%    │  │   ✅ 92%    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

#### **Risk Distribution Chart**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  INVOICE RISK DISTRIBUTION BY AMOUNT                                    │
│                                                                          │
│  ████████████████████████████████████████ High Risk    $125,400  27%   │
│  ████████████████████████████ Medium Risk  $89,200   19%                │
│  ██████████████████████████████████████████ Low Risk   $245,800  54%   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### **High-Risk Invoices Table** (Tabulator - with clickable contact names)
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Invoice #  │ Contact Name ↓        │ Amount    │ Days Overdue │ Risk Score │ Customer LTV │ Action   │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INV-10234  │ 🔴 Acme Corp         │ $45,200   │ 45 days      │ 87% HIGH   │ $230,000     │ 👁️ 📞 ✉️ │
│ INV-10189  │ 🔴 BuildTech Inc     │ $32,100   │ 67 days      │ 82% HIGH   │ $180,000     │ 👁️ 📞 ✉️ │
│ INV-10211  │ 🔴 Metro Supplies    │ $18,900   │ 52 days      │ 78% HIGH   │ $95,000      │ 👁️ 📞 ✉️ │
│ INV-10156  │ 🟡 TechFlow Ltd      │ $15,600   │ 38 days      │ 72% HIGH   │ $120,000     │ 👁️ 📞 ✉️ │
│ INV-10198  │ 🔴 GlobalTrade Co    │ $13,600   │ 59 days      │ 71% HIGH   │ $65,000      │ 👁️ 📞 ✉️ │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                     ↑ Click to open detailed modal
```

#### **Smart Filters**
```
[All Risk Levels ▼] [VIP Customers Only ☑] [>$10K Only ☑] [In-house Only ☑]
```

---

### **2. Smart Collection Queue Dashboard**

#### **Priority Action Queue** (Top 50 priority-ranked)
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Rank │ Contact Name ↓        │ Invoice # │ Amount    │ Priority │ Action           │ Expected Recovery │ Actions  │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  1   │ 🔴 Acme Corp         │ INV-10234 │ $45,200   │ 9,840    │ Executive Call   │ $40,680 (90%)     │ 👁️ 📞 ✉️ │
│  2   │ 🔴 BuildTech Inc     │ INV-10189 │ $32,100   │ 8,520    │ Executive Call   │ $25,680 (80%)     │ 👁️ 📞 ✉️ │
│  3   │ 🟡 TechFlow Ltd      │ INV-10211 │ $18,900   │ 7,560    │ Payment Plan     │ $17,010 (90%)     │ 👁️ 📞 ✉️ │
│  4   │ 🔴 Metro Supplies    │ INV-10156 │ $15,600   │ 6,240    │ Email Reminder   │ $13,260 (85%)     │ 👁️ 📞 ✉️ │
│  5   │ 🟡 GlobalTrade Co    │ INV-10198 │ $13,600   │ 5,440    │ Payment Plan     │ $10,880 (80%)     │ 👁️ 📞 ✉️ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                           ↑ Click to open detailed modal + quick actions

Total Expected Recovery: $107,510 (85% of $126,400)
```

#### **Best Contact Timing** (shown in modal)
```
📅 Tuesday-Thursday, 10am-2pm
⏰ Next optimal contact window: Tomorrow at 10:30am
```

#### **Quick Actions Toolbar**
```
[📞 Generate Call List] [✉️ Send Bulk Reminder Emails] [📊 Export to Excel] [🔍 Filter by Segment]
```

---

### **3. Payment Pattern Analysis Dashboard**

#### **Customer Payment Clusters** (4 clusters)
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Cluster Name           │ Customer Count │ Avg Pay Time │ Consistency │ Recommended Action      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚡ Fast & Reliable     │ 45 customers   │ 8 days       │ 95%         │ No action needed        │
│ 📅 End-of-Month Payers │ 32 customers   │ 28 days      │ 88%         │ Align due dates to EOM  │
│ 🐌 Slow but Consistent │ 18 customers   │ 45 days      │ 72%         │ Offer early pay discount│
│ ⚠️ Unpredictable       │ 12 customers   │ 52 days      │ 35%         │ Require deposit         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### **Cluster Detail View** (Click cluster to expand customer list)
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📅 END-OF-MONTH PAYERS (32 customers)                                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Contact Name ↓         │ Avg Pay Time │ Invoices Paid │ Pattern Confidence │ Recommendation  │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Acme Corp             │ 29 days      │ 24            │ 92%                │ Set due on 1st  │
│ BuildTech Inc         │ 27 days      │ 18            │ 85%                │ Set due on 1st  │
│ TechFlow Ltd          │ 31 days      │ 15            │ 78%                │ Set due on 1st  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                              ↑ Click to open detailed modal
```

---

### **4. ML-Enhanced Aged Receivables Dashboard**

#### **Side-by-Side Comparison**
```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  TRADITIONAL AGING                           ML-ADJUSTED AGING                                │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Current:      $245,800 (54%)                Safe Amount:      $185,400 (40%)                 │
│  1-30 days:    $89,200 (19%)                 At-Risk Amount:   $60,400 (13%)                  │
│  31-60 days:   $67,500 (15%)                                                                   │
│  61-90 days:   $32,100 (7%)                  Safe Amount:      $42,000 (9%)                   │
│  90+ days:     $25,800 (5%)                  At-Risk Amount:   $25,500 (6%)                   │
│                                                                                                 │
│  TOTAL:        $460,400                      TOTAL:            $460,400                        │
│                                              REAL COLLECTIBLE: $413,100 (90%)                  │
│                                              AT RISK:          $47,300 (10%)                   │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### **At-Risk Detail Table** (Drill-down)
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Contact Name ↓         │ Invoice # │ Aging Bucket │ Amount   │ Risk Score │ Safe │ At-Risk   │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🔴 Acme Corp          │ INV-10234 │ 31-60 days   │ $45,200  │ 87% HIGH   │ $5,876│ $39,324   │
│ 🔴 BuildTech Inc      │ INV-10189 │ 61-90 days   │ $32,100  │ 82% HIGH   │ $5,778│ $26,322   │
│ 🟡 Metro Supplies     │ INV-10211 │ 31-60 days   │ $18,900  │ 78% HIGH   │ $4,158│ $14,742   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                              ↑ Click to open detailed modal
```

---

## 🔍 Contact/Customer Detail View Design (Full Tab Replacement)

### **When User Clicks ANY Contact Row in ANY Dashboard:**

**Navigation Flow:** Dashboard → Click Row → **Full Tab Replacement** → Back Button Returns to Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  [◀ Back to Dashboard]  Invoice Risk Scoring > Acme Corp         [Export] [Edit]    │  │
│  └──────────────────────────────────────────────────────────────────────────────────────┘  │
│  ╔═══════════════════════════════════════════════════════════════════════════════════════╗  │
│  ║  👤 ACME CORP - Churn: 78% | Payment Risk: 82% | LTV: $230,000                      ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════════════╝  │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  📋 Profile  │  📊 ML Insights  │  💰 Financial  │  📅 History  │  🎯 Actions     │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  📋 CUSTOMER PROFILE                                                               │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  Name:              Acme Corp                                                      │    │
│  │  Contact Person:    John Smith (CEO)                                              │    │
│  │  Email:             john.smith@acmecorp.com                                        │    │
│  │  Phone:             (555) 123-4567                                                 │    │
│  │  Address:           123 Main St, Suite 400, San Francisco, CA 94105               │    │
│  │  Customer Since:    March 15, 2022                                                 │    │
│  │  Account Manager:   Sarah Johnson                                                  │    │
│  │  Payment Terms:     Net 30                                                         │    │
│  │  Credit Limit:      $100,000                                                       │    │
│  │  Tax Number:        12-3456789                                                     │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  📊 ML INSIGHTS & RISK ASSESSMENT                                                  │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │    │
│  │  │ CHURN RISK   │  │ PAYMENT RISK │  │  DEVIATION   │  │  LTV VALUE   │         │    │
│  │  │   🔴 78%     │  │   🔴 82%     │  │   🔴 3.2σ    │  │  $230,000    │         │    │
│  │  │   HIGH       │  │   HIGH       │  │   HIGH       │  │  Rank: #3    │         │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘         │    │
│  │                                                                                    │    │
│  │  Segment:            🔴 VIP At-Risk                                               │    │
│  │  Behavior Trend:     📉 Declining (last 3 orders: 52, 67, 89 days avg)          │    │
│  │  ML Confidence:      85% (high data quality)                                     │    │
│  │                                                                                    │    │
│  │  Root Causes:                                                                     │    │
│  │    1. Payment Issues (Payment delay increased 45% over 6 months)                 │    │
│  │    2. Timing Issues (Order frequency dropped from 45 to 67 days)                 │    │
│  │    3. Engagement Issues (Last contact: 89 days ago)                              │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  💰 FINANCIAL SUMMARY                                                              │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  Historical LTV:         $230,000  (24 invoices over 33 months)                   │    │
│  │  Predicted 12M LTV:      $78,000   (based on current trend)                       │    │
│  │  Churn-Adjusted LTV:     $17,160   (78% churn risk applied)                       │    │
│  │  Total Expected LTV:     $247,160                                                  │    │
│  │                                                                                     │    │
│  │  Avg Invoice Value:      $9,583                                                    │    │
│  │  Avg Reorder Frequency:  67 days (target: 45 days)                                │    │
│  │  Reorder Variance:       18 days (inconsistent)                                   │    │
│  │                                                                                     │    │
│  │  Current Outstanding:    $45,200 (1 invoice)                                      │    │
│  │  Days Overdue:           45 days (Expected: 45 days ago)                          │    │
│  │  Collection Risk:        87% HIGH                                                  │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  📅 TRANSACTION HISTORY (Last 10 invoices)                                         │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  Date       │ Invoice #  │ Amount    │ Paid Date  │ Days to Pay │ Status          │    │
│  │  ─────────────────────────────────────────────────────────────────────────────────│    │
│  │  Dec 15 '25 │ INV-10234  │ $45,200   │ UNPAID     │ 45 days     │ 🔴 OVERDUE     │    │
│  │  Oct 28 '25 │ INV-10189  │ $12,800   │ Nov 30 '25 │ 33 days     │ ✅ PAID        │    │
│  │  Sep 10 '25 │ INV-10156  │ $18,900   │ Oct 25 '25 │ 45 days     │ ✅ PAID        │    │
│  │  Jul 22 '25 │ INV-10098  │ $9,200    │ Sep 15 '25 │ 55 days     │ ✅ PAID        │    │
│  │  Jun 5 '25  │ INV-10045  │ $14,600   │ Aug 2 '25  │ 58 days     │ ✅ PAID        │    │
│  │  Apr 18 '25 │ INV-9989   │ $8,700    │ Jun 20 '25 │ 63 days     │ ✅ PAID        │    │
│  │  Mar 2 '25  │ INV-9921   │ $11,300   │ May 8 '25  │ 67 days     │ ✅ PAID        │    │
│  │  Jan 15 '25 │ INV-9856   │ $7,900    │ Mar 28 '25 │ 72 days     │ ✅ PAID        │    │
│  │  Dec 1 '24  │ INV-9789   │ $10,500   │ Feb 18 '25 │ 79 days     │ ✅ PAID        │    │
│  │  Oct 14 '24 │ INV-9712   │ $6,800    │ Jan 5 '25  │ 83 days     │ ✅ PAID        │    │
│  │                                                                                     │    │
│  │  📈 Trend: Payment time increasing (33d → 72d over 6 months)                      │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  🎯 RECOMMENDED ACTIONS & SCENARIO MODELING                                         │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  Best Action: Executive Call (Value: $17,160 at risk)                             │    │
│  │  Priority Rank: #1 (highest priority in collection queue)                         │    │
│  │  Best Contact Time: Tuesday-Thursday, 10am-2pm                                    │    │
│  │  Next Optimal Window: Tomorrow at 10:30am                                         │    │
│  │                                                                                     │    │
│  │  Scenario Analysis:                                                                │    │
│  │  ┌───────────────────────┬──────────────────┬──────────────────┬────────────┐    │    │
│  │  │ Action                │ Churn Reduction  │ Expected Impact  │ ROI        │    │    │
│  │  ├───────────────────────┼──────────────────┼──────────────────┼────────────┤    │    │
│  │  │ 📞 Executive Call     │ -15% (78% → 63%) │ +$25,740 LTV     │ 1,500%     │    │    │
│  │  │ 💰 Offer 5% Discount  │ -10% (78% → 68%) │ +$17,160 LTV     │ 350%       │    │    │
│  │  │ 📋 Payment Plan       │ -8% (78% → 70%)  │ +$13,728 LTV     │ N/A        │    │    │
│  │  │ ⚠️ No Action          │ +5% (78% → 83%)  │ -$8,580 LTV      │ -100%      │    │    │
│  │  └───────────────────────┴──────────────────┴──────────────────┴────────────┘    │    │
│  │                                                                                     │    │
│  │  AI Summary:                                                                       │    │
│  │  "VIP customer showing 45% payment delay increase and declining order              │    │
│  │   frequency. Current $45K invoice is 45 days overdue. Recommend immediate          │    │
│  │   executive outreach to address concerns and protect $230K relationship.           │    │
│  │   Expected recovery rate: 90% if contacted within 48 hours."                       │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  🔗 XERO INTEGRATION - QUICK ACTIONS                                               │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  [📞 Make Call] [✉️ Send Email] [💰 Create Invoice] [📝 Add Note]                │    │
│  │  [💵 Apply Discount] [📋 Payment Plan] [🔗 View in Xero] [📊 Export to PDF]      │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  📝 ACTIVITY LOG (Last 5 interactions)                                             │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │  Dec 20, 2025  │ Email sent: Payment reminder for INV-10234                       │    │
│  │  Nov 30, 2025  │ Payment received: $12,800 for INV-10189                          │    │
│  │  Oct 28, 2025  │ Invoice created: INV-10189 ($12,800)                             │    │
│  │  Oct 25, 2025  │ Payment received: $18,900 for INV-10156                          │    │
│  │  Sep 10, 2025  │ Invoice created: INV-10156 ($18,900)                             │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                              │
│  [Close]                                      [Export Customer Report PDF]  [Save Changes]  │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Modal Sections Breakdown

### **Section 1: Customer Profile** (Always visible)
- **What to show:** Name, contact person, email, phone, address, customer since, account manager, payment terms, credit limit, tax number
- **Source:** Xero Contacts API + custom fields
- **Why:** Basic identification and contact information for immediate reference

### **Section 2: ML Insights & Risk Assessment** (Contacts + Reports tabs)
- **What to show:** 
  - 4 key metrics: Churn Risk, Payment Risk, Deviation Score, LTV Value
  - Strategic Segment (7 segments: VIP-Protect, VIP At-Risk, High-Value Declining, Rising Star, Lost Cause, Stable Regular, Standard)
  - Behavior Trend (Declining/Improving/Stable with specific data)
  - ML Confidence (data quality score)
  - Root Causes (ranked 1-3: Timing, Payment, Engagement, Value)
- **Source:** Customer Intelligence ML pipeline (8-stage)
- **Why:** Provides context for WHY the customer is in this dashboard

### **Section 3: Financial Summary** (All tabs)
- **What to show:**
  - Historical LTV (lifetime revenue to date)
  - Predicted 12M LTV (forecasted future value)
  - Churn-Adjusted LTV (risk-weighted prediction)
  - Total Expected LTV (historical + adjusted future)
  - Avg Invoice Value
  - Avg Reorder Frequency (actual vs target)
  - Reorder Variance (consistency metric)
  - Current Outstanding (unpaid invoices total)
  - Days Overdue (for oldest unpaid invoice)
  - Collection Risk (payment risk score)
- **Source:** Customer Intelligence + Invoice data
- **Why:** Financial context for decision-making (is this worth pursuing?)

### **Section 4: Transaction History** (All tabs)
- **What to show:**
  - Last 10-20 invoices (Date, Invoice #, Amount, Paid Date, Days to Pay, Status)
  - Payment trend visualization (are they slowing down?)
  - Late payment frequency
  - Average days to pay (rolling 6-month average)
- **Source:** Xero Invoices API + calculated fields
- **Why:** Pattern recognition - see if current behavior is new or consistent

### **Section 5: Recommended Actions & Scenario Modeling** (Contacts + Reports tabs)
- **What to show:**
  - Best Action (Call/Discount/Payment Plan) with reasoning
  - Priority Rank (where they sit in collection queue)
  - Best Contact Time (optimal timing based on research)
  - Next Optimal Window (specific date/time recommendation)
  - Scenario Analysis table:
    - Action → Churn Reduction → Expected Impact → ROI
    - 4 scenarios: Executive Call, Offer Discount, Payment Plan, No Action
  - AI-generated summary paragraph (natural language explanation)
- **Source:** Scenario modeling from Customer Intelligence ML
- **Why:** Actionable guidance - what to do NOW

### **Section 6: Xero Integration - Quick Actions** (All tabs)
- **What to show:**
  - Buttons for common actions:
    - 📞 Make Call (logs call in Xero, opens dialer if available)
    - ✉️ Send Email (pre-populated template with context)
    - 💰 Create Invoice (opens invoice creation modal)
    - 📝 Add Note (quick note to customer record)
    - 💵 Apply Discount (create credit note)
    - 📋 Payment Plan (set up installment schedule)
    - 🔗 View in Xero (open customer in Xero web app)
    - 📊 Export to PDF (customer report)
- **Source:** Frontend actions → Xero API calls
- **Why:** One-click actions without leaving the modal

### **Section 7: Activity Log** (All tabs)
- **What to show:**
  - Last 5-10 interactions (emails sent, payments received, invoices created, calls logged, notes added)
  - Timestamp + action description
  - User who performed action (if available)
- **Source:** Xero activity log + custom logging
- **Why:** Recent interaction history for context

---

## 🔧 Technical Implementation

### **Backend Endpoint: `/api/xero/customer-details/<contact_id>`**

```python
@xero_bp.route('/api/xero/customer-details/<contact_id>', methods=['GET'])
def get_customer_details(contact_id):
    """
    Comprehensive customer details for modal display.
    Combines data from:
    1. Xero Contacts API
    2. Customer Intelligence ML pipeline
    3. Invoice history
    4. Activity log
    """
    business_id = request.args.get('business_id')
    
    # 1. Get Xero contact details
    contact = fetch_xero_contact(business_id, contact_id)
    
    # 2. Get ML insights from Customer Intelligence
    ml_insights = get_customer_intelligence_for_contact(business_id, contact_id)
    
    # 3. Get invoice history (last 20 invoices)
    invoices = fetch_customer_invoices(business_id, contact_id, limit=20)
    
    # 4. Calculate financial metrics
    financial_summary = {
        'historical_ltv': ml_insights.get('lifetime_revenue', 0),
        'predicted_12m_ltv': ml_insights.get('predicted_12m_ltv', 0),
        'churn_adjusted_ltv': ml_insights.get('churn_adjusted_ltv', 0),
        'total_expected_ltv': ml_insights.get('total_expected_ltv', 0),
        'avg_invoice_value': ml_insights.get('avg_invoice_value', 0),
        'avg_reorder_frequency': ml_insights.get('avg_reorder_days', 0),
        'reorder_variance': ml_insights.get('reorder_variance_days', 0),
        'current_outstanding': sum(inv['amount_due'] for inv in invoices if inv['status'] != 'PAID'),
        'days_overdue': ml_insights.get('days_since_expected_reorder', 0),
        'collection_risk': ml_insights.get('payment_risk_score', 0)
    }
    
    # 5. Get activity log
    activity_log = fetch_customer_activity_log(business_id, contact_id, limit=10)
    
    # 6. Get scenario modeling results
    scenarios = ml_insights.get('scenario_impacts', {})
    
    return jsonify({
        'success': True,
        'customer': {
            'profile': contact,
            'ml_insights': ml_insights,
            'financial_summary': financial_summary,
            'invoices': invoices,
            'activity_log': activity_log,
            'scenarios': scenarios,
            'best_action': ml_insights.get('ml_best_action', 'call'),
            'best_action_reason': ml_insights.get('ml_best_action_reason', ''),
            'priority_rank': ml_insights.get('action_priority_rank', None),
            'best_contact_time': 'Tuesday-Thursday, 10am-2pm',
            'next_optimal_window': calculate_next_contact_window()
        }
    })
```

### **Frontend Function: `showCustomerDetailsModal(contactId)`**

```javascript
async showCustomerDetailsModal(contactId, businessId) {
    try {
        // Fetch comprehensive customer data
        const response = await fetch(
            `${this.API_BASE_URL}/api/xero/customer-details/${contactId}?business_id=${businessId}`
        );
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load customer details');
        }
        
        const customer = data.customer;
        
        // Build modal HTML
        const modalHTML = `
            <div class="xero-modal-overlay" id="xero-customer-modal" style="
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0, 0, 0, 0.8); display: flex;
                align-items: center; justify-content: center;
                z-index: 10000; backdrop-filter: blur(8px);
            ">
                <div class="xero-modal-content" style="
                    background: #0d1117; border: 1px solid #30363d;
                    border-radius: 12px; width: 95%; max-width: 1200px;
                    max-height: 90vh; overflow-y: auto;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                ">
                    <!-- Modal Header -->
                    <div style="padding: 24px 32px; border-bottom: 1px solid #30363d;
                                display: flex; justify-content: space-between; align-items: center;
                                background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);">
                        <h2 style="margin: 0; font-size: 24px; color: #c9d1d9;">
                            <i class="fas fa-user-circle" style="color: var(--xero-primary); margin-right: 12px;"></i>
                            ${customer.profile.name}
                        </h2>
                        <button id="xero-close-customer-modal" style="
                            background: transparent; border: none;
                            color: #8b949e; font-size: 24px; cursor: pointer;
                            padding: 8px; border-radius: 6px; transition: all 0.2s;
                        ">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <!-- Modal Body -->
                    <div style="padding: 32px;">
                        ${this.renderCustomerProfile(customer.profile)}
                        ${this.renderMLInsights(customer.ml_insights)}
                        ${this.renderFinancialSummary(customer.financial_summary)}
                        ${this.renderTransactionHistory(customer.invoices)}
                        ${this.renderRecommendedActions(customer)}
                        ${this.renderQuickActions(customer.profile.contact_id)}
                        ${this.renderActivityLog(customer.activity_log)}
                    </div>

                    <!-- Modal Footer -->
                    <div style="padding: 16px 32px; border-top: 1px solid #30363d;
                                display: flex; justify-content: space-between; align-items: center;
                                background: #161b22;">
                        <button id="xero-close-modal-btn" style="
                            padding: 10px 20px; background: #30363d;
                            border: none; border-radius: 6px; color: #c9d1d9;
                            font-size: 14px; cursor: pointer;
                        ">Close</button>
                        <div style="display: flex; gap: 12px;">
                            <button id="xero-export-customer-report" style="
                                padding: 10px 20px; background: #238636;
                                border: none; border-radius: 6px; color: white;
                                font-size: 14px; cursor: pointer;
                            ">
                                <i class="fas fa-file-pdf"></i> Export Report
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Inject modal into DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Add event listeners
        document.getElementById('xero-close-customer-modal').addEventListener('click', () => {
            document.getElementById('xero-customer-modal').remove();
        });
        
        document.getElementById('xero-close-modal-btn').addEventListener('click', () => {
            document.getElementById('xero-customer-modal').remove();
        });
        
        document.getElementById('xero-export-customer-report').addEventListener('click', () => {
            this.exportCustomerReport(contactId);
        });
        
        // Quick action buttons
        this.attachQuickActionListeners(contactId, businessId);
        
    } catch (error) {
        console.error('[Xero] Error loading customer details:', error);
        alert('Failed to load customer details. Please try again.');
    }
}

renderMLInsights(mlInsights) {
    return `
        <div style="margin-bottom: 24px; border: 1px solid #30363d; border-radius: 8px; overflow: hidden;">
            <div style="padding: 16px; background: #161b22; border-bottom: 1px solid #30363d;">
                <h3 style="margin: 0; font-size: 16px; color: #c9d1d9;">
                    <i class="fas fa-brain" style="color: var(--xero-primary); margin-right: 8px;"></i>
                    ML Insights & Risk Assessment
                </h3>
            </div>
            <div style="padding: 24px; background: #0d1117;">
                <!-- 4 Key Metrics -->
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;">
                    <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">CHURN RISK</div>
                        <div style="font-size: 28px; font-weight: 700; color: ${mlInsights.ml_churn_probability >= 70 ? '#f85149' : mlInsights.ml_churn_probability >= 40 ? '#d29922' : '#3fb950'};">
                            ${mlInsights.ml_churn_probability}%
                        </div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                            ${mlInsights.ml_churn_probability >= 70 ? 'HIGH' : mlInsights.ml_churn_probability >= 40 ? 'MEDIUM' : 'LOW'}
                        </div>
                    </div>
                    <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">PAYMENT RISK</div>
                        <div style="font-size: 28px; font-weight: 700; color: ${mlInsights.payment_risk_score >= 70 ? '#f85149' : mlInsights.payment_risk_score >= 40 ? '#d29922' : '#3fb950'};">
                            ${mlInsights.payment_risk_score}%
                        </div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                            ${mlInsights.payment_risk_score >= 70 ? 'HIGH' : mlInsights.payment_risk_score >= 40 ? 'MEDIUM' : 'LOW'}
                        </div>
                    </div>
                    <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">DEVIATION</div>
                        <div style="font-size: 28px; font-weight: 700; color: ${mlInsights.deviation_score >= 2.5 ? '#f85149' : mlInsights.deviation_score >= 1.5 ? '#d29922' : '#3fb950'};">
                            ${mlInsights.deviation_score.toFixed(1)}σ
                        </div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                            ${mlInsights.deviation_score >= 2.5 ? 'HIGH' : mlInsights.deviation_score >= 1.5 ? 'MEDIUM' : 'NORMAL'}
                        </div>
                    </div>
                    <div style="padding: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; text-align: center;">
                        <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">LTV VALUE</div>
                        <div style="font-size: 28px; font-weight: 700; color: #3fb950;">
                            ${this.formatCurrency(mlInsights.lifetime_revenue)}
                        </div>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                            Rank: #${mlInsights.ltv_rank || 'N/A'}
                        </div>
                    </div>
                </div>

                <!-- Segment & Trend -->
                <div style="margin-bottom: 16px;">
                    <strong style="color: #c9d1d9;">Segment:</strong>
                    <span style="margin-left: 8px; padding: 4px 12px; background: ${this.getSegmentColor(mlInsights.strategic_segment)}; 
                                border-radius: 12px; font-size: 13px; font-weight: 600;">
                        ${mlInsights.strategic_segment}
                    </span>
                </div>

                <div style="margin-bottom: 16px; color: #8b949e; font-size: 14px;">
                    <strong style="color: #c9d1d9;">Behavior Trend:</strong>
                    ${mlInsights.behavior_trend === 'declining' ? '📉' : mlInsights.behavior_trend === 'improving' ? '📈' : '➡️'}
                    ${mlInsights.behavior_trend} (${mlInsights.behavior_trend_reason || 'N/A'})
                </div>

                <div style="margin-bottom: 16px; color: #8b949e; font-size: 14px;">
                    <strong style="color: #c9d1d9;">ML Confidence:</strong>
                    ${mlInsights.ml_confidence_score}% (${mlInsights.ml_confidence_score >= 80 ? 'high' : mlInsights.ml_confidence_score >= 60 ? 'moderate' : 'low'} data quality)
                </div>

                <!-- Root Causes -->
                <div style="margin-top: 20px;">
                    <strong style="color: #c9d1d9; display: block; margin-bottom: 12px;">Root Causes:</strong>
                    ${mlInsights.root_causes.map((cause, i) => `
                        <div style="margin-bottom: 8px; padding-left: 20px; color: #8b949e; font-size: 14px;">
                            ${i + 1}. <strong style="color: #c9d1d9;">${cause.name}</strong>
                            <span style="color: #8b949e;">(${cause.description})</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}
```

---

## 🎯 Key Design Decisions

### **1. Consistency Across All Dashboards**
- **Every** customer/contact row in **every** ML dashboard uses the **same modal system**
- Same data structure, same sections, same quick actions
- Reduces cognitive load, increases user confidence

### **2. Progressive Disclosure**
- Show most critical info first (Profile, ML Insights, Financial)
- Expand to full history and recommendations
- User can scroll for more detail, but top section answers "who is this and why do I care?"

### **3. Contextual Intelligence**
- Modal shows **why** this customer is in this particular dashboard
- Example: Invoice Risk Scoring → emphasizes collection risk and days overdue
- Example: Customer Intelligence → emphasizes churn risk and LTV
- Same data, different emphasis based on entry point

### **4. Actionability**
- Every modal includes **Quick Actions** section
- One-click to call, email, create invoice, apply discount
- No need to leave the modal to take action

### **5. Data-Driven Recommendations**
- **Scenario modeling** shows expected impact of different actions
- Not just "call them" but "calling reduces churn 15% and adds $25K LTV"
- ROI calculation helps prioritize actions

---

## 📐 Visual Design Guidelines

### **Color Palette**
```
Background Primary:   #0d1117 (dark charcoal)
Background Secondary: #161b22 (lighter charcoal)
Border:               #30363d (medium gray)
Text Primary:         #c9d1d9 (light gray)
Text Secondary:       #8b949e (medium gray)
Accent Primary:       #13b9fd (bright cyan - Xero brand)
Success:              #3fb950 (green)
Warning:              #d29922 (yellow)
Danger:               #f85149 (red)
```

### **Typography**
```
Headings:  16-24px, font-weight: 600-700
Body:      14px, font-weight: 400
Labels:    12px, font-weight: 500
Metrics:   28-32px, font-weight: 700
```

### **Spacing**
```
Section padding:       24-32px
Card padding:          16-20px
Element gaps:          8-16px
Modal border-radius:   12px
Card border-radius:    6-8px
```

### **Animations**
```
Modal fade-in:         300ms ease-in-out
Backdrop blur:         4-8px
Hover transitions:     200ms
Button press:          100ms
```

---

## 🚀 Implementation Phases

### **Phase 1: Invoice Risk Scoring Dashboard (Week 1)**
1. Create backend endpoint for invoice risk scoring
2. Build frontend dashboard with 4 summary cards + risk distribution chart
3. Implement high-risk invoices Tabulator table
4. Add click handlers to open customer detail modal
5. Build customer detail modal with 7 sections
6. Test with sample data

### **Phase 2: Customer Detail Modal System (Week 1-2)**
1. Create `/api/xero/customer-details/<contact_id>` endpoint
2. Integrate Customer Intelligence ML data
3. Build modal HTML structure
4. Implement all 7 sections with real data
5. Add Quick Actions functionality
6. Test modal from multiple entry points (Invoices, Contacts, Reports)

### **Phase 3: Smart Collection Queue (Week 2)**
1. Create backend endpoint for collection queue
2. Build priority calculation formula
3. Implement queue dashboard with top 50 contacts
4. Add "Generate Call List" and "Send Bulk Emails" actions
5. Integrate with customer detail modal
6. Test priority ranking accuracy

### **Phase 4: Payment Pattern Analysis (Week 3)**
1. Implement K-means clustering for payment patterns
2. Create 4 cluster categories
3. Build cluster summary dashboard
4. Add drill-down to customer lists per cluster
5. Integrate with customer detail modal
6. Test clustering accuracy

### **Phase 5: ML-Enhanced Aged Receivables (Week 3)**
1. Apply risk scores to traditional aging buckets
2. Create side-by-side comparison view
3. Build at-risk detail table
4. Add drill-down to customer details
5. Integrate with customer detail modal
6. Test risk-adjusted calculations

---

## 📊 Success Metrics

### **User Engagement**
- Modal open rate: >80% of dashboard views
- Average modal session time: 45-90 seconds
- Quick Actions usage: >40% of modal opens
- Export usage: >25% of modal opens

### **Business Impact**
- Collection rate improvement: +15-20%
- Average days to pay reduction: -10 days
- Customer retention improvement: +5-8%
- Time to action reduction: -60% (from finding data to taking action)

### **Technical Performance**
- Modal load time: <500ms
- Dashboard initial render: <1000ms
- Table performance: 1000+ rows without lag
- API response time: <300ms (95th percentile)

---

## 🔄 Iteration Plan

### **V1.0 (MVP - 4 weeks)**
- Invoice Risk Scoring Dashboard
- Smart Collection Queue
- Customer Detail Modal (core 7 sections)
- Basic Quick Actions (call, email, view in Xero)

### **V1.1 (Enhancement - 2 weeks)**
- Payment Pattern Analysis
- ML-Enhanced Aged Receivables
- Advanced Quick Actions (discount, payment plan, create invoice)
- Activity log integration

### **V1.2 (Polish - 1 week)**
- Cohort Analysis integration
- Export functionality (PDF, Excel)
- Email templates with AI-generated content
- Bulk actions for multiple customers

### **V2.0 (Advanced - 3 weeks)**
- Real-time updates (WebSocket)
- AI chat integration in modal
- Predictive notifications
- Advanced scenario modeling with custom parameters

---

## 📝 Notes for Implementation

1. **Reuse Existing Code:**
   - Customer Intelligence ML pipeline already exists (lines 2550-3180 in xero_routes.py)
   - Customer detail modal pattern exists for create contact (lines 3010+ in xero.js)
   - Tabulator table setup exists for invoices and contacts
   - Just need to combine and extend

2. **Data Flow:**
   - Dashboard → User clicks contact row → `showCustomerDetailsModal(contactId)` → Fetch `/api/xero/customer-details/<contactId>` → Render modal → User takes action → Update backend → Refresh dashboard

3. **Caching Strategy:**
   - Cache customer intelligence data for 5 minutes (reduce API calls)
   - Invalidate cache on invoice payment or new invoice creation
   - Use session storage for modal data during single session

4. **Error Handling:**
   - Graceful degradation if ML data unavailable (show basic profile)
   - Timeout after 5 seconds with retry option
   - Log errors to backend for debugging
   - User-friendly error messages

5. **Accessibility:**
   - Keyboard navigation support (Tab, Esc to close)
   - ARIA labels for screen readers
   - Focus management (trap focus in modal)
   - Color contrast ratio >4.5:1

---

**Ready to implement? Let's start with Phase 1: Invoice Risk Scoring Dashboard + Customer Detail Modal MVP.**
