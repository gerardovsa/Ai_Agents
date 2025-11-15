# 🧠 Smart Accounts Payable Statistics & Export Tool

**Purpose:** AI-powered tool to pull Xero accounts payable data with comprehensive time-based statistics, aging analysis, trends, and forecasts. Exports formatted Excel workbook to OneDrive and returns both shareable link + parsed data to AI.  
**Status:** Design Phase - Ready to Implement  
**Category:** Smart Financial Reporting Tool  
**Tool Name:** `smart_export_accounts_payable_stats`

---

## 🎯 **TOOL DESIGN: `smart_export_accounts_payable_stats`**

### **Core Concept:**

AI agent can request accounts payable data with custom filters, and the tool will:
1. ✅ Pull data from Xero API
2. ✅ Analyze and categorize invoices
3. ✅ Calculate totals, aging buckets, trends
4. ✅ Flag overdue/urgent items
5. ✅ Create formatted Excel workbook
6. ✅ Upload to OneDrive with shareable link
7. ✅ Return BOTH link + parsed data to AI

### **Why This is Powerful:**

- **AI gets structured data** to answer questions: "What's our largest overdue invoice?"
- **Human gets professional report** via shareable Excel link
- **One tool call** handles everything (Smart Tool pattern)

---

## 📋 **TOOL SPECIFICATION**

```python
def smart_export_accounts_payable_stats(
    days_back: int = 30,
    date_from: str = None,
    date_to: str = None,
    status: str = "PAYABLE",  # PAYABLE, PAID, ALL
    min_amount: float = 0,
    supplier: str = None,
    include_analysis: bool = True,
    export_format: str = "excel",  # excel, csv, both
    auto_share: bool = True
) -> Dict:
    """
    SMART TOOL: Pull Xero accounts payable data with comprehensive statistics, trends, and intelligent analysis
    
    This tool orchestrates multiple operations:
    1. Query Xero API for bills/payables
    2. Enrich data with aging analysis
    3. Calculate totals, averages, trends
    4. Flag overdue/urgent items
    5. Create formatted Excel workbook
    6. Upload to OneDrive with shareable link
    7. Return both link + structured data to AI
    
    Args:
        days_back: How many days of history (default: 30)
        date_from: Start date (ISO format: "2025-10-15") - overrides days_back
        date_to: End date (ISO format: "2025-11-13") - defaults to today
        status: Filter by status
            - "PAYABLE": Unpaid bills only (default)
            - "PAID": Paid bills only
            - "ALL": Both paid and unpaid
        min_amount: Only include bills >= this amount (default: 0)
        supplier: Filter by supplier name (partial match)
        include_analysis: Add analysis tabs (aging, trends, flags)
        export_format: "excel", "csv", or "both"
        auto_share: Create shareable OneDrive link (default: True)
    
    Returns:
        {
            "success": True,
            "summary": {
                "total_bills": 45,
                "total_amount": 125750.50,
                "total_paid": 87500.00,
                "total_outstanding": 38250.50,
                "overdue_count": 8,
                "overdue_amount": 12450.00,
                "avg_payment_days": 35,
                "payment_rate": 78,
                "date_range": {
                    "from": "2025-10-14",
                    "to": "2025-11-13"
                }
            },
            "time_periods": {
                "7_days": {"count": 12, "amount": 8450.00, "avg": 704.17, "trend": "↑ +15%"},
                "2_weeks": {"count": 18, "amount": 14200.00, "avg": 788.89, "trend": "↑ +8%"},
                "3_weeks": {"count": 25, "amount": 21500.00, "avg": 860.00, "trend": "→ Stable"},
                "1_month": {"count": 37, "amount": 38250.50, "avg": 1033.80, "trend": "↑ +12%"},
                "6_weeks": {"count": 42, "amount": 45800.00, "avg": 1090.50, "trend": "↑ +18%"},
                "2_months": {"count": 68, "amount": 72300.00, "avg": 1063.20, "trend": "↑ +22%"},
                "3_months": {"count": 95, "amount": 98750.00, "avg": 1039.50, "trend": "↓ -5%"},
                "6_months_plus": {"count": 12, "amount": 15200.00, "avg": 1266.70, "trend": "⚠️ Review"}
            },
            "monthly_breakdown": {
                "2025-11": {"created": 45, "created_amount": 125750, "paid": 32, "paid_amount": 87500, "net": 38250},
                "2025-10": {"created": 52, "created_amount": 138200, "paid": 48, "paid_amount": 132100, "net": 6100},
                "2025-09": {"created": 48, "created_amount": 115300, "paid": 44, "paid_amount": 109800, "net": 5500}
            },
            "trends": {
                "mom_growth": 12.5,
                "avg_monthly_created": 118025,
                "avg_monthly_paid": 108433,
                "trend_direction": "INCREASING"
            },
            "velocity": {
                "avg_payment_time": 35,
                "fastest_payment": {"days": 7, "invoice": "INV-12348"},
                "slowest_payment": {"days": 68, "invoice": "INV-12299"},
                "on_time_rate": 78
            },
            "aging_buckets": {
                "current": {"count": 15, "amount": 18500.50},
                "1-30_days": {"count": 12, "amount": 7300.00},
                "31-60_days": {"count": 5, "amount": 3200.00},
                "61-90_days": {"count": 2, "amount": 1500.00},
                "90+_days": {"count": 3, "amount": 7750.00}
            },
            "top_suppliers": [
                {"name": "ABC Supplies", "amount": 15000.00, "bills": 5},
                {"name": "XYZ Materials", "amount": 12500.00, "bills": 3}
            ],
            "flagged_items": [
                {
                    "invoice_number": "INV-12345",
                    "supplier": "ABC Supplies",
                    "amount": 5000.00,
                    "due_date": "2025-10-15",
                    "days_overdue": 29,
                    "flags": ["OVERDUE", "HIGH_VALUE"]
                }
            ],
            "files": {
                "excel": {
                    "filename": "Accounts_Payable_2025-10-14_to_2025-11-13.xlsx",
                    "onedrive_url": "https://1drv.ms/x/s!Abc123...",
                    "download_url": "https://...",
                    "file_id": "onedrive-file-id",
                    "size_kb": 245
                },
                "csv": {
                    "filename": "Accounts_Payable_2025-10-14_to_2025-11-13.csv",
                    "onedrive_url": "https://1drv.ms/...",
                    "download_url": "https://..."
                }
            },
            "raw_data": [
                {
                    "invoice_id": "guid",
                    "invoice_number": "INV-12345",
                    "supplier_name": "ABC Supplies",
                    "date": "2025-10-15",
                    "due_date": "2025-11-15",
                    "total": 5000.00,
                    "amount_paid": 0.00,
                    "amount_due": 5000.00,
                    "status": "PAYABLE",
                    "days_since_invoice": 29,
                    "days_until_due": 2,
                    "aging_bucket": "current",
                    "flags": ["HIGH_VALUE"]
                },
                // ... more invoices
            ],
            "ai_insights": [
                "8 invoices are overdue totaling $12,450",
                "Largest overdue: ABC Supplies - $5,000 (29 days overdue)",
                "3 invoices are 90+ days overdue - recommend review",
                "Average payment cycle: 35 days"
            ]
        }
    
    Excel Workbook Structure:
        📊 Tab 1: "Summary Dashboard"
            - KPI cards (total outstanding, overdue, etc.)
            - Aging chart (pie chart)
            - Top suppliers chart (bar chart)
            - Payment trends (line chart)
        
        📋 Tab 2: "All Bills"
            - Full list of bills with all fields
            - Conditional formatting (overdue = red)
            - Filters enabled
            - Frozen header row
        
        ⚠️ Tab 3: "Flagged Items"
            - Only bills that need attention
            - Sorted by urgency
            - Color-coded severity
        
        📈 Tab 4: "Aging Analysis"
            - Aging buckets breakdown
            - Pivot table by supplier
            - Trend analysis
        
        🏢 Tab 5: "By Supplier"
            - Grouped by supplier
            - Subtotals for each
            - Payment history
    
    Use Cases:
        1. Quick check: "What's our accounts payable for last 30 days?"
           → AI calls: smart_export_accounts_payable_stats(days_back=30)
           → AI reads summary, time-based stats, and flags
           → AI responds: "You have $38,250 outstanding with 8 overdue invoices. 
              Last week saw 12 bills totaling $8,450 (↑15% vs previous week)"
        
        2. Custom date range: "Show me Q4 accounts payable statistics"
           → AI calls: smart_export_accounts_payable_stats(date_from="2025-10-01", date_to="2025-12-31")
           → Returns comprehensive stats + Excel link
        
        3. Trend analysis: "How are our payables trending?"
           → AI calls: smart_export_accounts_payable_stats(days_back=90)
           → AI analyzes monthly_breakdown and trends
           → AI responds: "AP increasing 12% month-over-month. Last 3 months show upward trend."
        
        4. Payment planning: "What bills are due in the next 2 weeks?"
           → AI calls: smart_export_accounts_payable_stats(days_back=30)
           → AI reads time_periods['2_weeks'] from results
           → Presents prioritized payment schedule
    """
```

---

## 📊 **EXCEL WORKBOOK DESIGN**

### **Tab 1: Summary Dashboard** 📊

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  ACCOUNTS PAYABLE SUMMARY & TRENDS                                                     │
│  Period: 2025-10-14 to 2025-11-13                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  CURRENT PERIOD SNAPSHOT                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Total Bills  │  │ Outstanding  │  │   Overdue    │  │ Avg Invoice  │              │
│  │     45       │  │  $38,250.50  │  │  $12,450.00  │  │   $1,033.80  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Total Paid   │  │ Avg Payment  │  │ Overdue Count│  │ Payment Rate │              │
│  │  $87,500.00  │  │   35 days    │  │      8       │  │    78%       │              │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  TIME-BASED BREAKDOWN (Outstanding Amounts by Period)                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Period          │ Count │ Amount      │ % of Total │ Avg/Bill │ Trend              │
│  ──────────────────────────────────────────────────────────────────────────────────   │
│  Last 7 Days     │  12   │ $8,450.00   │   22%      │ $704.17  │ ↑ +15% vs prev     │
│  Last 2 Weeks    │  18   │ $14,200.00  │   37%      │ $788.89  │ ↑ +8% vs prev      │
│  Last 3 Weeks    │  25   │ $21,500.00  │   56%      │ $860.00  │ → Stable           │
│  Last 1 Month    │  37   │ $38,250.50  │  100%      │ $1,033.8 │ ↑ +12% vs prev     │
│  Last 6 Weeks    │  42   │ $45,800.00  │  120%*     │ $1,090.5 │ ↑ +18% vs prev     │
│  Last 2 Months   │  68   │ $72,300.00  │  189%*     │ $1,063.2 │ ↑ +22% vs prev     │
│  Last 3 Months   │  95   │ $98,750.00  │  258%*     │ $1,039.5 │ ↓ -5% vs prev      │
│  Over 6 Months   │  12   │ $15,200.00  │   40%*     │ $1,266.7 │ ⚠️ Review needed   │
│                                                                                         │
│  * Percentages > 100% include bills outside primary period                            │
│                                                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  MONTHLY TREND ANALYSIS (Last 12 Months)                                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  Month       │ Bills Created │ Amount Created │ Bills Paid │ Amount Paid │ Net Change │
│  ─────────────────────────────────────────────────────────────────────────────────────  │
│  Nov 2025    │      45       │   $125,750     │     32     │  $87,500    │  +$38,250  │
│  Oct 2025    │      52       │   $138,200     │     48     │ $132,100    │   +$6,100  │
│  Sep 2025    │      48       │   $115,300     │     44     │ $109,800    │   +$5,500  │
│  Aug 2025    │      55       │   $142,800     │     51     │ $138,900    │   +$3,900  │
│  Jul 2025    │      41       │    $98,500     │     39     │  $96,200    │   +$2,300  │
│  Jun 2025    │      38       │    $87,600     │     37     │  $86,100    │   +$1,500  │
│                                                                                         │
│  📊 AVERAGE MONTHLY:  48 bills  |  $118,025 created  |  42 bills paid  |  $108,433 paid│
│                                                                                         │
│  [Line Chart: Monthly Trend]                                                           │
│  Amount                                                                                │
│  $150K ┤                     ●                                                         │
│        │                ●         ●                                                    │
│  $100K ┤           ●                   ●     ●     ●                                   │
│        │                                                                                │
│   $50K ┤                                                                                │
│        │                                                                                │
│     $0 └────────────────────────────────────────────────────────────────────→         │
│        Jun      Jul      Aug      Sep      Oct      Nov                                │
│        ─── Created    ─── Paid                                                         │
│                                                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  AGING BREAKDOWN                    TOP SUPPLIERS (Current Period)                     │
│  ┌─────────────────────┐            ┌────────────────────┐                            │
│  │  [Pie Chart]        │            │ ABC Supplies       │                            │
│  │  Current: 48%       │            │ $15,000 (5 bills)  │                            │
│  │  1-30: 19%          │            │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   │                            │
│  │  31-60: 8%          │            │                    │                            │
│  │  61-90: 4%          │            │ XYZ Materials      │                            │
│  │  90+: 21% ⚠️        │            │ $12,500 (3 bills)  │                            │
│  └─────────────────────┘            │ ▓▓▓▓▓▓▓▓▓▓▓▓▓     │                            │
│                                     │                    │                            │
│                                     │ Office Direct      │                            │
│                                     │ $6,000 (4 bills)   │                            │
│                                     │ ▓▓▓▓▓▓▓▓          │                            │
│                                     └────────────────────┘                            │
│                                                                                         │
│  VELOCITY METRICS                                                                      │
│  ┌─────────────────────────────────────────────────────────┐                          │
│  │ Average time to pay: 35 days                            │                          │
│  │ Fastest payment: 7 days (Office Direct INV-12348)       │                          │
│  │ Slowest payment: 68 days (ABC Supplies INV-12299)       │                          │
│  │ On-time payment rate: 78% (improving ↑)                 │                          │
│  │ Average overdue period: 18 days                         │                          │
│  └─────────────────────────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Formatting:**
- Large KPI numbers (24pt, bold)
- Green = good metrics (paid on time)
- Red = bad metrics (overdue)
- Charts auto-update with data

---

### **Tab 2: All Bills** 📋

```
| Invoice # | Supplier         | Date       | Due Date   | Amount    | Paid      | Outstanding | Days Old | Days Until Due | Status   | Flags            |
|-----------|------------------|------------|------------|-----------|-----------|-------------|----------|----------------|----------|------------------|
| INV-12345 | ABC Supplies     | 2025-10-15 | 2025-11-15 | $5,000.00 | $0.00     | $5,000.00   | 29       | 2              | PAYABLE  | HIGH_VALUE       |
| INV-12346 | XYZ Materials    | 2025-10-20 | 2025-11-20 | $2,500.00 | $0.00     | $2,500.00   | 24       | 7              | PAYABLE  |                  |
| INV-12347 | Office Direct    | 2025-09-15 | 2025-10-15 | $3,200.00 | $0.00     | $3,200.00   | 59       | -29            | PAYABLE  | OVERDUE, URGENT  |
| INV-12348 | Print Co         | 2025-11-01 | 2025-12-01 | $1,250.00 | $1,250.00 | $0.00       | 12       | 18             | PAID     |                  |
```

**Formatting:**
- Overdue rows: Red background
- Due within 7 days: Yellow background
- Paid invoices: Gray text
- High value (>$5K): Bold
- Excel filters enabled on all columns
- Auto-sum at bottom
- Frozen header row

---

### **Tab 3: Flagged Items** ⚠️

```
| Priority | Invoice # | Supplier      | Amount    | Due Date   | Days Overdue | Flags                  | Recommended Action      |
|----------|-----------|---------------|-----------|------------|--------------|------------------------|-------------------------|
| 🔴 HIGH  | INV-12347 | Office Direct | $3,200.00 | 2025-10-15 | 29           | OVERDUE, URGENT        | Pay immediately         |
| 🔴 HIGH  | INV-12350 | ABC Supplies  | $5,000.00 | 2025-10-01 | 43           | OVERDUE, HIGH_VALUE    | Contact supplier        |
| 🟡 MED   | INV-12345 | ABC Supplies  | $5,000.00 | 2025-11-15 | 0            | HIGH_VALUE, DUE_SOON   | Schedule payment        |
| 🟡 MED   | INV-12351 | Print Co      | $1,800.00 | 2025-11-18 | 0            | DUE_SOON               | Prepare payment         |
| 🟢 LOW   | INV-12352 | XYZ Materials | $8,500.00 | 2025-08-10 | 95           | OLD_INVOICE            | Review if still valid   |
```

**Flags Logic:**
- `OVERDUE`: Past due date
- `URGENT`: >30 days overdue
- `HIGH_VALUE`: Amount > $5,000
- `DUE_SOON`: Due within 7 days
- `OLD_INVOICE`: >90 days old
- `LARGE_SUPPLIER`: Supplier has >$10K total outstanding
- `DUPLICATE_POSSIBLE`: Similar amount/supplier within 7 days

**Priority Calculation:**
```python
def calculate_priority(bill):
    score = 0
    
    # Overdue factors
    if bill['days_overdue'] > 60:
        score += 10
    elif bill['days_overdue'] > 30:
        score += 7
    elif bill['days_overdue'] > 0:
        score += 5
    
    # Amount factors
    if bill['amount'] > 10000:
        score += 5
    elif bill['amount'] > 5000:
        score += 3
    
    # Due soon factor
    if 0 < bill['days_until_due'] <= 7:
        score += 4
    
    # Priority levels
    if score >= 10:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    else:
        return "LOW"
```

---

### **Tab 4: Aging Analysis** 📈

```
AGING BUCKETS SUMMARY

| Bucket      | Count | Total Amount | Avg Amount | % of Total | Trend      |
|-------------|-------|--------------|------------|------------|------------|
| Current     | 15    | $18,500.50   | $1,233.37  | 48%        | ↑ +12%     |
| 1-30 days   | 12    | $7,300.00    | $608.33    | 19%        | → Stable   |
| 31-60 days  | 5     | $3,200.00    | $640.00    | 8%         | ↓ -5%      |
| 61-90 days  | 2     | $1,500.00    | $750.00    | 4%         | ↓ -3%      |
| 90+ days    | 3     | $7,750.00    | $2,583.33  | 21%        | ⚠️ +8%     |
|-------------|-------|--------------|------------|------------|------------|
| TOTALS      | 37    | $38,250.50   | $1,033.80  | 100%       |            |


BY SUPPLIER (AGING BREAKDOWN)

| Supplier         | Current  | 1-30 days | 31-60 days | 61-90 days | 90+ days  | Total      |
|------------------|----------|-----------|------------|------------|-----------|------------|
| ABC Supplies     | $8,000   | $3,000    | $2,000     | $0         | $2,000    | $15,000    |
| XYZ Materials    | $5,500   | $2,500    | $1,200     | $1,500     | $1,800    | $12,500    |
| Office Direct    | $2,000   | $800      | $0         | $0         | $3,200    | $6,000     |
| Print Co         | $3,000   | $1,000    | $0         | $0         | $750      | $4,750     |


AGING CHART (Stacked Bar by Supplier)
[Shows each supplier's aging distribution visually]
```

**Features:**
- Pivot table for dynamic analysis
- Conditional formatting (90+ days = red)
- Trend indicators (vs. previous period)
- Auto-refresh formulas

---

### **Tab 5: By Supplier** 🏢

```
═══════════════════════════════════════════════════════════════
  ABC SUPPLIES                                 Total: $15,000.00
═══════════════════════════════════════════════════════════════

| Invoice #  | Date       | Due Date   | Amount    | Status  | Days Overdue |
|------------|------------|------------|-----------|---------|--------------|
| INV-12345  | 2025-10-15 | 2025-11-15 | $5,000.00 | PAYABLE | 0            |
| INV-12350  | 2025-09-01 | 2025-10-01 | $5,000.00 | PAYABLE | 43 ⚠️        |
| INV-12355  | 2025-10-20 | 2025-11-20 | $3,000.00 | PAYABLE | 0            |
| INV-12360  | 2025-11-05 | 2025-12-05 | $2,000.00 | PAYABLE | 0            |
├────────────┴────────────┴────────────┴───────────┴─────────┴──────────────┤
│ SUBTOTAL: $15,000.00    Outstanding: $15,000.00    Overdue: $5,000.00    │
└───────────────────────────────────────────────────────────────────────────┘

Payment History (Last 6 Months):
• Average invoice amount: $3,750
• Average payment time: 38 days
• On-time payment rate: 75%
• Total paid YTD: $87,500


═══════════════════════════════════════════════════════════════
  XYZ MATERIALS                               Total: $12,500.00
═══════════════════════════════════════════════════════════════

| Invoice #  | Date       | Due Date   | Amount    | Status  | Days Overdue |
|------------|------------|------------|-----------|---------|--------------|
| INV-12346  | 2025-10-20 | 2025-11-20 | $2,500.00 | PAYABLE | 0            |
| INV-12352  | 2025-08-10 | 2025-09-10 | $8,500.00 | PAYABLE | 64 ⚠️        |
| INV-12358  | 2025-11-01 | 2025-12-01 | $1,500.00 | PAYABLE | 0            |
├────────────┴────────────┴────────────┴───────────┴─────────┴──────────────┤
│ SUBTOTAL: $12,500.00    Outstanding: $12,500.00    Overdue: $8,500.00    │
└───────────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Grouped by supplier with subtotals
- Collapsible sections (Excel outline feature)
- Payment history summary per supplier
- Risk indicators (overdue rate, large amounts)

---

## 🧮 **CALCULATIONS & ANALYSIS**

### **1. Aging Buckets**
```python
def calculate_aging_bucket(invoice_date, today):
    days_old = (today - invoice_date).days
    
    if days_old <= 30:
        return "current"
    elif days_old <= 60:
        return "1-30_days"
    elif days_old <= 90:
        return "31-60_days"
    elif days_old <= 120:
        return "61-90_days"
    else:
        return "90+_days"
```

### **2. Flag Detection**
```python
def detect_flags(bill, all_bills):
    flags = []
    
    # Overdue check
    if bill['days_overdue'] > 0:
        flags.append("OVERDUE")
        if bill['days_overdue'] > 30:
            flags.append("URGENT")
    
    # High value check
    if bill['amount_due'] > 5000:
        flags.append("HIGH_VALUE")
    
    # Due soon check
    if 0 < bill['days_until_due'] <= 7:
        flags.append("DUE_SOON")
    
    # Old invoice check
    if bill['days_since_invoice'] > 90:
        flags.append("OLD_INVOICE")
    
    # Large supplier check
    supplier_total = sum(b['amount_due'] for b in all_bills if b['supplier'] == bill['supplier'])
    if supplier_total > 10000:
        flags.append("LARGE_SUPPLIER")
    
    # Duplicate check (similar amount + supplier within 7 days)
    for other in all_bills:
        if other['invoice_id'] != bill['invoice_id']:
            if other['supplier'] == bill['supplier']:
                if abs(other['amount'] - bill['amount']) < 10:  # Within $10
                    date_diff = abs((other['date'] - bill['date']).days)
                    if date_diff <= 7:
                        flags.append("DUPLICATE_POSSIBLE")
                        break
    
    return flags
```

### **3. Trend Analysis**
```python
def calculate_trends(current_period_bills, previous_period_bills):
    current_total = sum(b['amount_due'] for b in current_period_bills)
    previous_total = sum(b['amount_due'] for b in previous_period_bills)
    
    if previous_total > 0:
        change_pct = ((current_total - previous_total) / previous_total) * 100
        
        if change_pct > 5:
            return f"↑ +{change_pct:.0f}%"
        elif change_pct < -5:
            return f"↓ {change_pct:.0f}%"
        else:
            return "→ Stable"
    
    return "N/A"
```

### **4. Payment Velocity**
```python
def calculate_payment_velocity(paid_bills):
    """Calculate average time from invoice date to payment date"""
    payment_times = []
    
    for bill in paid_bills:
        if bill['date_paid']:
            days_to_pay = (bill['date_paid'] - bill['invoice_date']).days
            payment_times.append(days_to_pay)
    
    if payment_times:
        avg_days = sum(payment_times) / len(payment_times)
        return avg_days
    
    return None
```

### **5. Supplier Risk Score**
```python
def calculate_supplier_risk(supplier_bills):
    """Calculate risk score for supplier relationship"""
    score = 0
    
    total_outstanding = sum(b['amount_due'] for b in supplier_bills)
    overdue_count = sum(1 for b in supplier_bills if b['days_overdue'] > 0)
    overdue_amount = sum(b['amount_due'] for b in supplier_bills if b['days_overdue'] > 0)
    
    # High outstanding
    if total_outstanding > 20000:
        score += 3
    
    # Many overdue invoices
    if overdue_count > 3:
        score += 3
    
    # Large overdue amount
    if overdue_amount > 10000:
        score += 4
    
    # Risk levels
    if score >= 7:
        return "HIGH"
    elif score >= 4:
        return "MEDIUM"
    else:
        return "LOW"
```

---

## 📊 **XERO DATA AVAILABILITY & POSSIBILITIES**

### **What Data is in Xero?**

Xero's Accounting API provides comprehensive financial data. Here's what's available for accounts payable reporting:

#### **1. Bill/Invoice Data (Core)**
```json
{
  "InvoiceID": "guid",
  "InvoiceNumber": "INV-12345",
  "Type": "ACCPAY",  // Accounts Payable
  "Contact": {
    "ContactID": "guid",
    "Name": "ABC Supplies",
    "EmailAddress": "billing@abc.com",
    "BankAccountDetails": "BSB: 123-456, Acc: 12345678"
  },
  "Date": "2025-10-15",  // Invoice date
  "DueDate": "2025-11-15",  // Payment due date
  "DateString": "2025-10-15",
  "Status": "AUTHORISED",  // DRAFT, SUBMITTED, AUTHORISED, PAID
  "LineAmountTypes": "Exclusive",  // Tax calculation method
  "LineItems": [
    {
      "Description": "Office supplies",
      "Quantity": 10,
      "UnitAmount": 50.00,
      "AccountCode": "400",
      "TaxType": "OUTPUT",
      "TaxAmount": 50.00,
      "LineAmount": 500.00
    }
  ],
  "SubTotal": 500.00,
  "TotalTax": 50.00,
  "Total": 550.00,
  "UpdatedDateUTC": "2025-10-15T14:30:00Z",
  "CurrencyCode": "AUD",
  "CurrencyRate": 1.0,
  "IsDiscounted": false,
  "HasAttachments": true,
  "Payments": [
    {
      "PaymentID": "guid",
      "Date": "2025-11-10",
      "Amount": 550.00,
      "Reference": "Payment via EFT"
    }
  ],
  "AmountDue": 0.00,  // Remaining unpaid amount
  "AmountPaid": 550.00,  // Total paid so far
  "AmountCredited": 0.00,
  "SentToContact": true,
  "Reference": "PO #12345",  // Your internal reference
  "BrandingThemeID": "guid",
  "HasErrors": false
}
```

#### **2. Payment Data**
```json
{
  "PaymentID": "guid",
  "Date": "2025-11-10",
  "Amount": 550.00,
  "Reference": "EFT Payment",
  "CurrencyRate": 1.0,
  "PaymentType": "ACCPAYPAYMENT",
  "Status": "AUTHORISED",
  "UpdatedDateUTC": "2025-11-10T09:15:00Z",
  "Invoice": {
    "InvoiceID": "guid",
    "InvoiceNumber": "INV-12345"
  },
  "Account": {
    "AccountID": "guid",
    "Code": "200",
    "Name": "Operating Account"
  },
  "IsReconciled": true
}
```

#### **3. Contact/Supplier Data**
```json
{
  "ContactID": "guid",
  "ContactNumber": "SUPP001",
  "Name": "ABC Supplies",
  "FirstName": "John",
  "LastName": "Smith",
  "EmailAddress": "billing@abc.com",
  "BankAccountDetails": "BSB: 123-456, Account: 12345678",
  "TaxNumber": "12-345-678-901",
  "AccountsPayableTaxType": "INPUT",
  "Addresses": [
    {
      "AddressType": "POBOX",
      "AddressLine1": "PO Box 123",
      "City": "Melbourne",
      "PostalCode": "3000",
      "Country": "Australia"
    }
  ],
  "Phones": [
    {
      "PhoneType": "DEFAULT",
      "PhoneNumber": "03 9123 4567"
    }
  ],
  "UpdatedDateUTC": "2025-10-01T10:00:00Z",
  "IsSupplier": true,
  "IsCustomer": false,
  "DefaultCurrency": "AUD",
  "Balances": {
    "AccountsPayable": {
      "Outstanding": 15000.00,
      "Overdue": 5000.00
    }
  },
  "PaymentTerms": {
    "Bills": {
      "Day": 30,
      "Type": "DAYSAFTERBILLDATE"
    }
  }
}
```

#### **4. Historical Data (Reporting Endpoints)**
```json
// Aged Payables Report
GET /Reports/AgedPayablesByContact
{
  "ReportID": "AgedPayablesByContact",
  "ReportName": "Aged Payables By Contact",
  "ReportDate": "2025-11-13",
  "Rows": [
    {
      "RowType": "Row",
      "Cells": [
        {"Value": "ABC Supplies"},
        {"Value": "8500.00"},  // Current
        {"Value": "3000.00"},  // 1-30 days
        {"Value": "2000.00"},  // 31-60 days
        {"Value": "1500.00"},  // 61-90 days
        {"Value": "0.00"}      // 90+ days
      ]
    }
  ]
}

// Balance Sheet (includes AP totals)
GET /Reports/BalanceSheet
{
  "Rows": [
    {
      "Title": "Liabilities",
      "Rows": [
        {
          "Title": "Current Liabilities",
          "Rows": [
            {
              "Title": "Accounts Payable",
              "Cells": [
                {"Value": "38250.50"}  // Total AP
              ]
            }
          ]
        }
      ]
    }
  ]
}

// Profit & Loss (expense tracking)
GET /Reports/ProfitAndLoss?fromDate=2025-01-01&toDate=2025-11-13
```

---

### **What Time-Based Stats Are Possible?**

#### **✅ AVAILABLE (Direct from Xero API):**

1. **Bills by Creation Date**
   - Count of bills created per day/week/month
   - Total amount of bills created per period
   - Endpoint: `GET /Invoices?where=Type=="ACCPAY"&DateFrom=...&DateTo=...`

2. **Bills by Due Date**
   - Count of bills due per day/week/month
   - Total amount due per period
   - Endpoint: `GET /Invoices?where=Type=="ACCPAY"&DueDateFrom=...&DueDateTo=...`

3. **Payments by Date**
   - Count of payments made per day/week/month
   - Total amount paid per period
   - Endpoint: `GET /Payments?where=Date>=DateTime(...)&Date<=DateTime(...)`

4. **Aged Payables Buckets**
   - Current, 1-30, 31-60, 61-90, 90+ days
   - By supplier or total
   - Endpoint: `GET /Reports/AgedPayablesByContact`

5. **Historical Snapshots**
   - Balance sheet at any date (total AP)
   - Endpoint: `GET /Reports/BalanceSheet?date=2025-10-01`

#### **✅ CALCULABLE (From API Data):**

1. **Custom Time Periods:**
   ```python
   # Last 7 days
   bills_7_days = filter_bills(bills, days_back=7)
   
   # Last 2 weeks
   bills_2_weeks = filter_bills(bills, days_back=14)
   
   # Last 3 weeks
   bills_3_weeks = filter_bills(bills, days_back=21)
   
   # Last 1 month
   bills_1_month = filter_bills(bills, days_back=30)
   
   # Last 6 weeks
   bills_6_weeks = filter_bills(bills, days_back=42)
   
   # Last 2 months
   bills_2_months = filter_bills(bills, days_back=60)
   
   # Last 3 months
   bills_3_months = filter_bills(bills, days_back=90)
   
   # Over 6 months
   bills_6_months_plus = filter_bills(bills, days_back=180, only_older=True)
   ```

2. **Monthly Aggregations:**
   ```python
   # Group bills by month
   by_month = {}
   for bill in bills:
       month_key = bill['Date'][:7]  # "2025-11"
       if month_key not in by_month:
           by_month[month_key] = {'count': 0, 'amount': 0}
       by_month[month_key]['count'] += 1
       by_month[month_key]['amount'] += bill['Total']
   ```

3. **Trend Calculations:**
   ```python
   # Compare current period to previous period
   current_total = sum(bill['Total'] for bill in current_bills)
   previous_total = sum(bill['Total'] for bill in previous_bills)
   
   if previous_total > 0:
       trend_pct = ((current_total - previous_total) / previous_total) * 100
       trend = f"↑ +{trend_pct:.0f}%" if trend_pct > 5 else "→ Stable"
   ```

4. **Velocity Metrics:**
   ```python
   # Average time from invoice to payment
   payment_times = []
   for bill in paid_bills:
       if bill['Payments']:
           payment_date = bill['Payments'][0]['Date']
           invoice_date = bill['Date']
           days = (payment_date - invoice_date).days
           payment_times.append(days)
   
   avg_payment_time = sum(payment_times) / len(payment_times)
   ```

5. **Growth Rates:**
   ```python
   # Month-over-month growth
   months = sorted(by_month.keys())
   for i in range(1, len(months)):
       current = by_month[months[i]]['amount']
       previous = by_month[months[i-1]]['amount']
       growth = ((current - previous) / previous) * 100
       by_month[months[i]]['growth'] = growth
   ```

---

### **Enhanced Stats Page Design**

Based on Xero data availability, here's what we can add to Tab 1:

```python
def calculate_time_based_stats(bills):
    """Calculate comprehensive time-based statistics"""
    
    today = datetime.now()
    
    stats = {
        'time_periods': {
            '7_days': filter_and_sum(bills, days=7),
            '2_weeks': filter_and_sum(bills, days=14),
            '3_weeks': filter_and_sum(bills, days=21),
            '1_month': filter_and_sum(bills, days=30),
            '6_weeks': filter_and_sum(bills, days=42),
            '2_months': filter_and_sum(bills, days=60),
            '3_months': filter_and_sum(bills, days=90),
            '6_months_plus': filter_old_bills(bills, min_days=180)
        },
        'monthly_breakdown': calculate_monthly_breakdown(bills),
        'trends': calculate_trends(bills),
        'velocity': {
            'avg_payment_time': calculate_avg_payment_time(bills),
            'fastest_payment': find_fastest_payment(bills),
            'slowest_payment': find_slowest_payment(bills),
            'on_time_rate': calculate_on_time_rate(bills)
        },
        'forecasts': {
            'next_7_days_due': forecast_due(bills, days=7),
            'next_30_days_due': forecast_due(bills, days=30),
            'next_90_days_due': forecast_due(bills, days=90)
        }
    }
    
    return stats

def filter_and_sum(bills, days):
    """Filter bills by days back and calculate stats"""
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = [b for b in bills if b['Date'] >= cutoff_date]
    
    # Calculate trend vs previous period
    prev_cutoff = cutoff_date - timedelta(days=days)
    prev_filtered = [b for b in bills if prev_cutoff <= b['Date'] < cutoff_date]
    
    current_total = sum(b['AmountDue'] for b in filtered)
    prev_total = sum(b['AmountDue'] for b in prev_filtered)
    
    trend = calculate_trend_indicator(current_total, prev_total)
    
    return {
        'count': len(filtered),
        'total_amount': current_total,
        'avg_amount': current_total / len(filtered) if filtered else 0,
        'percent_of_total': (current_total / sum(b['AmountDue'] for b in bills)) * 100,
        'trend': trend,
        'vs_previous': current_total - prev_total
    }

def calculate_monthly_breakdown(bills):
    """Group bills by month with detailed stats"""
    by_month = {}
    
    for bill in bills:
        month = bill['Date'][:7]  # "2025-11"
        
        if month not in by_month:
            by_month[month] = {
                'created_count': 0,
                'created_amount': 0,
                'paid_count': 0,
                'paid_amount': 0,
                'outstanding_count': 0,
                'outstanding_amount': 0
            }
        
        # Count created bills
        by_month[month]['created_count'] += 1
        by_month[month]['created_amount'] += bill['Total']
        
        # Count paid bills
        if bill['Status'] == 'PAID':
            by_month[month]['paid_count'] += 1
            by_month[month]['paid_amount'] += bill['AmountPaid']
        else:
            by_month[month]['outstanding_count'] += 1
            by_month[month]['outstanding_amount'] += bill['AmountDue']
    
    # Calculate net change per month
    for month in by_month:
        by_month[month]['net_change'] = (
            by_month[month]['created_amount'] - by_month[month]['paid_amount']
        )
    
    return by_month

def calculate_trends(bills):
    """Calculate various trend indicators"""
    # Get last 12 months of data
    monthly = calculate_monthly_breakdown(bills)
    months = sorted(monthly.keys())[-12:]
    
    if len(months) < 2:
        return {'insufficient_data': True}
    
    # Calculate month-over-month growth
    recent_month = months[-1]
    prev_month = months[-2]
    
    mom_growth = (
        (monthly[recent_month]['created_amount'] - monthly[prev_month]['created_amount'])
        / monthly[prev_month]['created_amount'] * 100
    )
    
    # Calculate average monthly values
    avg_monthly_created = sum(m['created_amount'] for m in monthly.values()) / len(months)
    avg_monthly_paid = sum(m['paid_amount'] for m in monthly.values()) / len(months)
    
    # Identify trend direction (last 3 months)
    if len(months) >= 3:
        last_3_totals = [monthly[m]['created_amount'] for m in months[-3:]]
        if last_3_totals[2] > last_3_totals[1] > last_3_totals[0]:
            trend_direction = "INCREASING"
        elif last_3_totals[2] < last_3_totals[1] < last_3_totals[0]:
            trend_direction = "DECREASING"
        else:
            trend_direction = "STABLE"
    else:
        trend_direction = "UNKNOWN"
    
    return {
        'mom_growth': mom_growth,
        'avg_monthly_created': avg_monthly_created,
        'avg_monthly_paid': avg_monthly_paid,
        'trend_direction': trend_direction,
        'months_analyzed': len(months)
    }
```

---

### **What's NOT Possible from Xero?**

❌ **Limitations:**

1. **No Built-in Forecasting**
   - Xero doesn't predict future bills
   - We calculate based on historical patterns

2. **No Supplier Performance Scoring**
   - Xero doesn't rate suppliers
   - We calculate from payment history

3. **No Automatic Risk Detection**
   - Xero doesn't flag unusual patterns
   - We implement custom logic

4. **Limited Historical Data**
   - API typically returns last 12 months
   - For older data, need to query reports

5. **No Real-time Notifications**
   - Xero doesn't push updates
   - We poll API periodically

---

### **Recommended Stats Page Structure**

**Section 1: Current Period Snapshot** (6 KPI cards)
- Total bills, Outstanding, Overdue, Avg invoice, Total paid, Payment rate

**Section 2: Time-Based Breakdown** (Table)
- Last 7 days, 2 weeks, 3 weeks, 1 month, 6 weeks, 2 months, 3 months, 6+ months
- Shows: Count, Amount, % of total, Avg per bill, Trend vs previous period

**Section 3: Monthly Trend Analysis** (Table + Chart)
- Last 12 months breakdown
- Bills created vs bills paid per month
- Net change per month
- Line chart showing trends

**Section 4: Velocity Metrics** (Cards)
- Average time to pay
- Fastest/slowest payments
- On-time payment rate
- Average overdue period

**Section 5: Aging & Suppliers** (Charts)
- Pie chart: Aging buckets
- Bar chart: Top suppliers
- Stacked bar: Supplier aging breakdown

**Section 6: Forecasts** (Table)
- Bills due in next 7 days
- Bills due in next 30 days
- Bills due in next 90 days
- Cash flow impact

---

### **Excel Implementation Pseudocode**

```python
def create_stats_page(ws, bills):
    """Create comprehensive stats page with all time-based breakdowns"""
    
    # Calculate all stats
    stats = calculate_time_based_stats(bills)
    monthly = calculate_monthly_breakdown(bills)
    trends = calculate_trends(bills)
    velocity = calculate_velocity_metrics(bills)
    
    row = 1
    
    # Section 1: Current Period Snapshot
    row = create_kpi_cards(ws, stats['current_period'], row)
    row += 2
    
    # Section 2: Time-Based Breakdown
    row = create_time_breakdown_table(ws, stats['time_periods'], row)
    row += 2
    
    # Section 3: Monthly Trends
    row = create_monthly_trends_table(ws, monthly, row)
    row = create_monthly_trends_chart(ws, monthly, row)
    row += 2
    
    # Section 4: Velocity Metrics
    row = create_velocity_cards(ws, velocity, row)
    row += 2
    
    # Section 5: Charts
    row = create_aging_chart(ws, stats['aging'], row, col=1)
    row = create_supplier_chart(ws, stats['suppliers'], row, col=7)
    row += 15
    
    # Section 6: Forecasts
    row = create_forecast_table(ws, stats['forecasts'], row)
    
    return ws
```

---

## 🔧 **IMPLEMENTATION DETAILS**

### **Backend Structure:**

```python
# tools/implementations/smart_financial_reports.py

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import PieChart, BarChart, LineChart
from datetime import datetime, timedelta
import requests

class SmartAccountsPayableStatsExporter:
    def __init__(self):
        self.xero_api = XeroAPI()
        self.onedrive_api = OneDriveAPI()
    
    def export_accounts_payable(self, days_back=30, date_from=None, date_to=None, **kwargs):
        """Main orchestration method"""
        
        # Step 1: Determine date range
        if date_from and date_to:
            date_range = (date_from, date_to)
        else:
            date_to = datetime.now()
            date_from = date_to - timedelta(days=days_back)
            date_range = (date_from.isoformat(), date_to.isoformat())
        
        # Step 2: Fetch bills from Xero
        bills = self.fetch_bills_from_xero(date_range, kwargs.get('status'), kwargs.get('supplier'))
        
        # Step 3: Enrich with analysis
        enriched_bills = self.enrich_bills(bills)
        
        # Step 4: Calculate summary stats
        summary = self.calculate_summary(enriched_bills)
        
        # Step 5: Detect flags
        flagged_bills = self.detect_flagged_items(enriched_bills)
        
        # Step 6: Calculate aging
        aging_buckets = self.calculate_aging_buckets(enriched_bills)
        
        # Step 7: Analyze by supplier
        supplier_analysis = self.analyze_by_supplier(enriched_bills)
        
        # Step 8: Create Excel workbook
        workbook = self.create_excel_workbook(
            enriched_bills, summary, aging_buckets, flagged_bills, supplier_analysis
        )
        
        # Step 9: Save and upload to OneDrive
        file_info = self.upload_to_onedrive(workbook, date_range, kwargs.get('auto_share', True))
        
        # Step 10: Generate AI insights
        ai_insights = self.generate_ai_insights(summary, flagged_bills, aging_buckets)
        
        # Step 11: Return comprehensive results
        return {
            'success': True,
            'summary': summary,
            'aging_buckets': aging_buckets,
            'top_suppliers': supplier_analysis['top_suppliers'],
            'flagged_items': flagged_bills,
            'files': file_info,
            'raw_data': enriched_bills,
            'ai_insights': ai_insights
        }
    
    def create_excel_workbook(self, bills, summary, aging, flagged, suppliers):
        """Create formatted Excel workbook"""
        wb = openpyxl.Workbook()
        
        # Tab 1: Summary Dashboard
        ws_summary = wb.active
        ws_summary.title = "Summary Dashboard"
        self.create_summary_tab(ws_summary, summary, aging)
        
        # Tab 2: All Bills
        ws_bills = wb.create_sheet("All Bills")
        self.create_bills_tab(ws_bills, bills)
        
        # Tab 3: Flagged Items
        ws_flagged = wb.create_sheet("Flagged Items")
        self.create_flagged_tab(ws_flagged, flagged)
        
        # Tab 4: Aging Analysis
        ws_aging = wb.create_sheet("Aging Analysis")
        self.create_aging_tab(ws_aging, aging, suppliers)
        
        # Tab 5: By Supplier
        ws_suppliers = wb.create_sheet("By Supplier")
        self.create_supplier_tab(ws_suppliers, suppliers)
        
        return wb
    
    def create_summary_tab(self, ws, summary, aging):
        """Create visually appealing summary dashboard"""
        
        # Title
        ws['A1'] = "ACCOUNTS PAYABLE SUMMARY"
        ws['A1'].font = Font(size=20, bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        ws.merge_cells('A1:F1')
        
        # Date range
        ws['A2'] = f"Period: {summary['date_range']['from']} to {summary['date_range']['to']}"
        ws['A2'].font = Font(size=12, italic=True)
        ws.merge_cells('A2:F2')
        
        # KPI Cards
        kpis = [
            ("Total Bills", summary['total_bills'], "A4", "B4"),
            ("Outstanding", f"${summary['total_outstanding']:,.2f}", "C4", "D4"),
            ("Overdue", f"${summary['overdue_amount']:,.2f}", "E4", "F4"),
            ("Total Paid", f"${summary['total_paid']:,.2f}", "A6", "B6"),
            ("Avg Payment", f"{summary['avg_payment_days']} days", "C6", "D6"),
            ("Overdue Count", summary['overdue_count'], "E6", "F6")
        ]
        
        for label, value, cell1, cell2 in kpis:
            ws[cell1] = label
            ws[cell1].font = Font(size=10, color="666666")
            ws[cell2] = value
            ws[cell2].font = Font(size=18, bold=True, color="4472C4")
        
        # Aging Chart (Pie Chart)
        chart = PieChart()
        chart.title = "Aging Breakdown"
        # ... add chart data
        ws.add_chart(chart, "A10")
        
        # Top Suppliers Chart (Bar Chart)
        bar_chart = BarChart()
        bar_chart.title = "Top Suppliers"
        # ... add chart data
        ws.add_chart(bar_chart, "E10")
        
        return ws
```

---

## 📤 **ONEDRIVE INTEGRATION**

```python
def upload_to_onedrive(self, workbook, date_range, auto_share):
    """Upload workbook to OneDrive and create shareable link"""
    
    # Generate filename
    filename = f"Accounts_Payable_{date_range[0]}_to_{date_range[1]}.xlsx"
    
    # Save workbook to bytes
    import io
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    file_bytes = output.read()
    
    # Upload to OneDrive
    folder_path = "/Financial Reports/Accounts Payable"
    upload_result = self.onedrive_api.upload_file(
        file_bytes, filename, folder_path
    )
    
    # Create shareable link (if requested)
    if auto_share:
        share_link = self.onedrive_api.create_share_link(
            upload_result['file_id'],
            permission="view"  # View-only link
        )
    else:
        share_link = None
    
    return {
        'excel': {
            'filename': filename,
            'onedrive_url': share_link,
            'download_url': upload_result['download_url'],
            'file_id': upload_result['file_id'],
            'size_kb': len(file_bytes) / 1024
        }
    }
```

---

## 🤖 **AI INTEGRATION EXAMPLES**

### **Example 1: Quick Check**
```
User: "What's our current accounts payable situation?"

AI Agent:
1. Calls: smart_export_accounts_payable(days_back=30)
2. Receives: summary + flagged_items + ai_insights
3. Analyzes raw_data
4. Responds:

"Current accounts payable summary (last 30 days):

💰 **Outstanding:** $38,250.50 across 37 bills
⚠️ **Overdue:** $12,450.00 (8 invoices)
📊 **Largest overdue:** ABC Supplies - $5,000 (43 days overdue)

🚨 **Urgent items:**
• Office Direct - $3,200 (29 days overdue)
• ABC Supplies - $5,000 (43 days overdue)

📊 [View detailed Excel report](onedrive link)

Would you like me to:
- Show breakdown by supplier
- Prioritize payment schedule
- Generate payment batch file"
```

### **Example 2: Trend Analysis**
```
User: "How are our accounts payable trending over the last 3 months?"

AI Agent:
1. Calls: smart_export_accounts_payable_stats(days_back=90)
2. Analyzes monthly_breakdown and trends
3. Responds:

"Accounts Payable Trend Analysis (Last 3 Months):

📊 **Monthly Breakdown:**
• November: 45 bills created ($125,750) | 32 paid ($87,500) | Net: +$38,250
• October: 52 bills created ($138,200) | 48 paid ($132,100) | Net: +$6,100
• September: 48 bills created ($115,300) | 44 paid ($109,800) | Net: +$5,500

📈 **Trend Analysis:**
• Month-over-month growth: +12.5%
• Average monthly created: $118,025
• Average monthly paid: $108,433
• Trend direction: INCREASING ⚠️

⚡ **Insights:**
• AP increasing faster than payment rate
• November saw largest net increase ($38,250)
• Payment velocity slowing (35 days avg, was 32 days)

💡 **Recommendation:** Review payment processes to reduce outstanding balance growth

📊 [View detailed 12-month trend report](link)"

### **Example 3: Supplier Analysis**
```
User: "Show me all bills from ABC Supplies over the last quarter"

AI Agent:
1. Calls: smart_export_accounts_payable_stats(
     date_from="2025-08-01",
     date_to="2025-11-13",
     supplier="ABC Supplies"
   )
2. Filters raw_data for ABC Supplies
3. Responds:

"ABC Supplies - Q4 2024 Summary:

📊 **Total:** $15,000 across 4 invoices
⚠️ **Overdue:** $5,000 (1 invoice - 43 days)
✅ **Current:** $10,000 (3 invoices)

**Invoice Breakdown:**
• INV-12345: $5,000 - Due Nov 15 (current)
• INV-12350: $5,000 - Due Oct 1 ⚠️ OVERDUE
• INV-12355: $3,000 - Due Nov 20 (current)
• INV-12360: $2,000 - Due Dec 5 (current)

📊 [View detailed Excel report](link)

**Recommendation:** Pay INV-12350 immediately (43 days overdue)"
```

### **Example 4: Payment Planning**
```
User: "Help me plan this week's bill payments. I have $20,000 available."

AI Agent:
1. Calls: smart_export_accounts_payable_stats(days_back=90, status="PAYABLE")
2. Analyzes flagged_items, aging_buckets, and time_periods
3. Prioritizes by urgency score
4. Creates payment plan:

"Recommended payment schedule ($20,000 budget):

🔴 **Priority 1 - Pay immediately ($8,200):**
• Office Direct - $3,200 (29 days overdue)
• ABC Supplies - $5,000 (43 days overdue)

🟡 **Priority 2 - Pay this week ($5,000):**
• ABC Supplies - $5,000 (due in 2 days)

🟢 **Priority 3 - Can wait ($6,800 remaining):**
• Print Co - $1,800 (due in 5 days)
• XYZ Materials - $2,500 (due in 7 days)
• Office Direct - $2,500 (due in 10 days)

**Total planned:** $20,000
**Clears:** 2 overdue invoices + 3 current

📊 [View full payment plan Excel](link)

Should I generate payment batch file for your bank?"
```

---

## 🚀 **ADVANCED FEATURES (Optional)**

### **1. Automated Payment Reminders**
```python
def generate_payment_reminders(flagged_bills):
    """Generate email drafts for overdue invoices"""
    reminders = []
    
    for bill in flagged_bills:
        if "OVERDUE" in bill['flags']:
            email = {
                'to': bill['supplier_email'],
                'subject': f"Payment Status - Invoice {bill['invoice_number']}",
                'body': f"Dear {bill['supplier_name']},\n\n"
                       f"Our records show invoice {bill['invoice_number']} "
                       f"for ${bill['amount']:,.2f} is {bill['days_overdue']} days overdue.\n\n"
                       f"We are processing payment and expect to settle within 3-5 business days.\n\n"
                       f"Thank you for your patience."
            }
            reminders.append(email)
    
    return reminders
```

### **2. Cash Flow Forecast**
```python
def forecast_cash_flow(bills, days_ahead=30):
    """Predict upcoming payment obligations"""
    forecast = {}
    
    for bill in bills:
        if bill['status'] == 'PAYABLE':
            due_date = bill['due_date']
            if due_date in forecast:
                forecast[due_date] += bill['amount_due']
            else:
                forecast[due_date] = bill['amount_due']
    
    # Sort by date
    sorted_forecast = sorted(forecast.items())
    
    return sorted_forecast
```

### **3. Duplicate Invoice Detection**
```python
def detect_duplicate_invoices(bills):
    """Find potential duplicate invoices"""
    duplicates = []
    
    for i, bill1 in enumerate(bills):
        for bill2 in bills[i+1:]:
            # Same supplier, similar amount, close dates
            if bill1['supplier'] == bill2['supplier']:
                amount_diff = abs(bill1['amount'] - bill2['amount'])
                date_diff = abs((bill1['date'] - bill2['date']).days)
                
                if amount_diff < 10 and date_diff <= 7:
                    duplicates.append({
                        'invoice_1': bill1['invoice_number'],
                        'invoice_2': bill2['invoice_number'],
                        'supplier': bill1['supplier'],
                        'amount_1': bill1['amount'],
                        'amount_2': bill2['amount'],
                        'confidence': 'HIGH' if amount_diff < 1 else 'MEDIUM'
                    })
    
    return duplicates
```

### **4. Export to Accounting Software**
```python
def export_payment_batch(bills_to_pay):
    """Generate payment batch file for bank import"""
    # ABA format (Australian) or similar
    batch_lines = []
    
    for bill in bills_to_pay:
        line = {
            'bsb': bill['supplier_bsb'],
            'account': bill['supplier_account'],
            'amount': bill['amount_due'],
            'reference': bill['invoice_number'],
            'payee': bill['supplier_name']
        }
        batch_lines.append(line)
    
    # Format as ABA file or CSV
    return batch_lines
```

---

## 📋 **TOOL SCHEMA (JSON)**

```json
{
  "name": "smart_export_accounts_payable_stats",
  "description": "Pull Xero accounts payable data with comprehensive time-based statistics (7 days to 6+ months), aging analysis, monthly trends, payment velocity metrics, and forecasts. Exports formatted Excel workbook to OneDrive with interactive charts and returns both shareable link + structured data to AI agent for intelligent analysis.",
  "platform": "smart_financial_reporting",
  "parameters": {
    "type": "object",
    "properties": {
      "days_back": {
        "type": "integer",
        "description": "Number of days of history to include (default: 30)",
        "default": 30
      },
      "date_from": {
        "type": "string",
        "description": "Start date in ISO format (YYYY-MM-DD) - overrides days_back"
      },
      "date_to": {
        "type": "string",
        "description": "End date in ISO format (YYYY-MM-DD) - defaults to today"
      },
      "status": {
        "type": "string",
        "enum": ["PAYABLE", "PAID", "ALL"],
        "description": "Filter by bill status (default: PAYABLE)",
        "default": "PAYABLE"
      },
      "min_amount": {
        "type": "number",
        "description": "Only include bills >= this amount (default: 0)",
        "default": 0
      },
      "supplier": {
        "type": "string",
        "description": "Filter by supplier name (partial match)"
      },
      "include_analysis": {
        "type": "boolean",
        "description": "Include aging analysis, trends, and insights (default: true)",
        "default": true
      },
      "export_format": {
        "type": "string",
        "enum": ["excel", "csv", "both"],
        "description": "Export format (default: excel)",
        "default": "excel"
      },
      "auto_share": {
        "type": "boolean",
        "description": "Create shareable OneDrive link (default: true)",
        "default": true
      }
    },
    "required": []
  },
  "returns": {
    "type": "object",
    "description": "Comprehensive accounts payable report with summary, analysis, flags, Excel link, and raw data for AI processing"
  }
}
```

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core Functionality (Week 1)**
- [ ] Create `smart_export_accounts_payable()` function
- [ ] Integrate Xero API for bills query
- [ ] Implement basic aging calculation
- [ ] Create simple Excel export (Tab 2: All Bills)
- [ ] Upload to OneDrive with shareable link
- [ ] Return summary + raw data to AI

### **Phase 2: Analysis & Formatting (Week 2)**
- [ ] Implement flag detection logic
- [ ] Create Summary Dashboard tab (Tab 1)
- [ ] Create Flagged Items tab (Tab 3)
- [ ] Add conditional formatting (colors, fonts)
- [ ] Implement charts (pie, bar, line)

### **Phase 3: Advanced Tabs (Week 3)**
- [ ] Create Aging Analysis tab (Tab 4)
- [ ] Create By Supplier tab (Tab 5)
- [ ] Implement supplier risk scoring
- [ ] Add payment velocity calculation
- [ ] Generate AI insights

### **Phase 4: Polish & Testing (Week 4)**
- [ ] Test with real Xero data
- [ ] Optimize Excel file size
- [ ] Add error handling
- [ ] Create comprehensive tests
- [ ] Documentation

---

## 🎯 **SUCCESS METRICS**

- **Time Savings:** Manual AP report = 2-3 hours → Automated = 30 seconds
- **Accuracy:** Eliminate manual calculation errors
- **Insights:** AI can answer questions about AP instantly
- **Adoption:** Finance team uses it weekly for AP review

---

**STATUS:** Design complete - Ready to implement

**NEXT STEP:** Implement Phase 1 (Core functionality) - Estimated 1 week
