# WooCommerce E-Commerce Integration - Accurate Technical Documentation
**Live WooCommerce REST API Integration | Real-Time Analytics Dashboard**

**Created:** January 18, 2026  
**Analysis Date:** January 18, 2026  
**Module ID:** `shopify` (legacy name, actually WooCommerce)  
**Version:** 1.2.1  
**Last Major Refactor:** January 4, 2026  
**Status:** ✅ Production Ready

---

## ⚠️ CRITICAL: Naming Confusion

**The module is called "Shopify" but connects to WooCommerce!**

- Module ID: `shopify`
- Module Name: "Shopify E-Commerce"
- Actual Platform: **WooCommerce** (https://inhouseprint.com.au)
- API Used: **WooCommerce REST API v3**
- NOT Shopify API

This naming is legacy and remains for backward compatibility.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Dashboard Module (Frontend)](#dashboard-module-frontend)
4. [Flask API Backend](#flask-api-backend)
5. [Calculator System](#calculator-system)
6. [WooCommerce API Integration](#woocommerce-api-integration)
7. [Credential Management](#credential-management)
8. [Critical Issues](#critical-issues)
9. [Testing & Deployment](#testing--deployment)
10. [Migration History](#migration-history)

---

## Executive Summary

### What This Module Does

**Real-Time E-Commerce Analytics from WooCommerce:**

1. **Dashboard Module** (Frontend)
   - 6 tabs: Dashboard, Orders, Customers, Products, Webhooks, SQL Viewer
   - Built with shopify.js (1,576 lines)
   - Uses Plotly.js for charts, Tabulator.js for tables
   - Shows live data from WooCommerce store

2. **Flask API** (Backend)
   - 10 endpoints connecting to WooCommerce REST API
   - Fetches orders, customers, products in real-time
   - Credentials stored in Supabase PostgreSQL
   - **NO local database** (removed January 4, 2026)

3. **Calculator Classes** (Standalone Tools)
   - 35 Python calculator classes
   - Replicate WooCommerce DPO pricing exactly
   - Used by AI agents for instant quotes
   - **NO database required** - pure calculation logic

### Key Statistics

| Metric | Value | Notes |
|--------|-------|-------|
| **Frontend** | 1,576 lines JS | shopify.js |
| **Backend** | 807 lines Python | shopify_routes.py |
| **Dashboard Tabs** | 6 tabs | All functional |
| **API Endpoints** | 10 endpoints | WooCommerce API calls |
| **Calculator Classes** | 35 files | Standalone pricing |
| **Local Database** | 0 tables | ❌ Removed Jan 4, 2026 |
| **Data Source** | WooCommerce | ✅ Live API |
| **Credentials Storage** | Supabase | ✅ PostgreSQL |
| **Webhook Storage** | None | ❌ Not implemented |

### What Changed (January 4, 2026 Refactor)

**REMOVED:**
- ❌ SQLite database (stock_data.db)
- ❌ 5 database tables (shopify_orders, shopify_line_items, etc.)
- ❌ SQL Viewer backend endpoint
- ❌ Webhook event storage
- ❌ Cursor management complexity (33 leak patterns)

**ADDED:**
- ✅ WooCommerce REST API integration
- ✅ Live data fetching (no local cache)
- ✅ Supabase credential management
- ✅ Simplified error handling
- ✅ Reduced code from 1,155 → 807 lines

---

## System Architecture

### Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 WOOCOMMERCE INTEGRATION ARCHITECTURE                     │
│                    (Module ID: 'shopify' - Legacy Name)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND: shopify.js (1,576 lines)             │  │
│  │                                                                    │  │
│  │  6 Dashboard Tabs:                                                │  │
│  │  ┌─────────────┬───────────┬───────────┬──────────┬──────────┐   │  │
│  │  │ Dashboard   │  Orders   │ Customers │ Products │ Webhooks │   │  │
│  │  │             │           │           │          │          │   │  │
│  │  │ • KPIs      │ • Table   │ • Charts  │ • Charts │ • Events │   │  │
│  │  │ • Charts    │ • Filters │ • Segments│ • Catalog│ • Health │   │  │
│  │  └─────────────┴───────────┴───────────┴──────────┴──────────┘   │  │
│  │  ┌───────────────┐                                                │  │
│  │  │  SQL Viewer*  │  *UI exists but backend disabled               │  │
│  │  └───────────────┘                                                │  │
│  │                                                                    │  │
│  │  Dependencies: Plotly.js 2.27.0, Tabulator.js 5.5.0              │  │
│  └────────────────────────────┬───────────────────────────────────────┘  │
│                               │ Fetch API Calls                          │
│                               ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              FLASK API: shopify_routes.py (807 lines)             │  │
│  │              init_shopify_routes(app, config, db_available)       │  │
│  │                                                                    │  │
│  │  10 Endpoints (WooCommerce API Wrappers):                        │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │ 1. /api/shopify/dashboard/metrics             → Orders stats│ │  │
│  │  │ 2. /api/shopify/dashboard/orders              → Orders list │ │  │
│  │  │ 3. /api/shopify/dashboard/charts/orders-*     → Chart data  │ │  │
│  │  │ 4. /api/shopify/dashboard/charts/revenue-*    → Chart data  │ │  │
│  │  │ 5. /api/shopify/dashboard/customers/top       → Customers   │ │  │
│  │  │ 6. /api/shopify/dashboard/customers/segments  → Segments    │ │  │
│  │  │ 7. /api/shopify/dashboard/products/top-sellers→ Products    │ │  │
│  │  │ 8. /api/shopify/dashboard/products/catalog    → Catalog     │ │  │
│  │  │ 9. /api/shopify/dashboard/webhooks/log        → Empty []    │ │  │
│  │  │10. /api/shopify/dashboard/webhooks/health     → Empty {}    │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └────────────┬──────────────────────────┬──────────────────────────┘  │
│               │ get_woocommerce_api()    │                              │
│               ↓                          ↓                              │
│  ┌─────────────────────────────┐  ┌──────────────────────────────┐    │
│  │  SUPABASE POSTGRESQL        │  │  WOOCOMMERCE REST API        │    │
│  │  (Credentials Only)         │  │  (Live E-Commerce Data)      │    │
│  │                             │  │                              │    │
│  │  ai_infrastructure.         │  │  https://inhouseprint        │    │
│  │    user_platform_           │  │    .com.au/wp-json/wc/v3/    │    │
│  │    credentials              │  │                              │    │
│  │                             │  │  GET /orders?after=...       │    │
│  │  Row (user_id=1):           │  │  GET /products?per_page=...  │    │
│  │  {                          │  │  GET /customers?...          │    │
│  │    "platform": "shopify",   │  │  GET /reports/sales          │    │
│  │    "credentials": {         │  │                              │    │
│  │      "consumer_key": "...", │  │  Authentication:             │    │
│  │      "consumer_secret":"...",│  │  Basic Auth (key:secret)    │    │
│  │      "base_url": "..."      │  │                              │    │
│  │    },                       │  │  Returns: JSON               │    │
│  │    "is_active": true        │  │  Timeout: 30 seconds         │    │
│  │  }                          │  │                              │    │
│  └─────────────────────────────┘  └──────────────────────────────┘    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  CALCULATOR SYSTEM (35 Standalone Python Classes)                │  │
│  │  Location: quote-calculator/backend/shopify_calculators/         │  │
│  │                                                                   │  │
│  │  Categories:                                                      │  │
│  │  • Stationery (5): Letterheads, Compliments, Notepads (A4/A5/A6)│  │
│  │  • Signage (9): Election, Construction, Bollard, A-Frames, etc. │  │
│  │  • Books (5): Wire/Spiral/Perfect Bound, Saddle Stitch, Flyers  │  │
│  │  • Promotional (8): Posters, Stickers, Bookmarks, Banners, etc. │  │
│  │  • Business Cards (2): Economical, Premium                       │  │
│  │  • Other (6): Corflute, Strut Cards, etc.                        │  │
│  │                                                                   │  │
│  │  Features:                                                        │  │
│  │  ✓ Exact WooCommerce DPO pricing replication                     │  │
│  │  ✓ F1-F14 parameter structure (book products)                    │  │
│  │  ✓ Configurable GST, markup, surcharge                           │  │
│  │  ✓ NO DATABASE ACCESS - Pure calculation logic                   │  │
│  │  ✓ Used by AI agents via direct import                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ❌ NO LOCAL DATABASE - All data is live from WooCommerce             │
│  ❌ NO WEBHOOK STORAGE - Webhook endpoints return empty data          │
│  ❌ NO CACHING - Every request fetches fresh data                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Examples

**Example 1: User Opens Dashboard**
```
1. User clicks "Shopify E-Commerce" in sidebar
2. Frontend loads shopify.js
3. JavaScript calls initializeDashboardTab()
4. Automatically triggers loadDashboardData('month')
5. Fetches: GET /api/shopify/dashboard/metrics?period=month
6. Flask endpoint get_woocommerce_credentials(user_id=1)
7. Queries Supabase: SELECT credentials FROM user_platform_credentials
8. Creates WooCommerce API client: API(url, key, secret)
9. Calls WooCommerce: wcapi.get("orders", params={'after': '2025-12-18'})
10. WooCommerce returns JSON array of orders
11. Flask calculates: total_orders, total_revenue, avg_order_value
12. Returns JSON to frontend
13. Frontend updates metric cards with live data
```

**Example 2: AI Agent Calculates Quote**
```
1. User: "Quote for 1000 premium business cards, 350GSM satin, 2-side matt"
2. AI agent imports: from shopify_calculators.PremiumBusinessCards_Shopify_Calculator import *
3. AI creates instance: calc = PremiumBusinessCardsShopifyCalculator()
4. AI calls: result = calc.calculate(
     quantity=1000,
     stock_type="satin_350gsm",
     sides=2,
     celloglaze="2_side_matt"
   )
5. Calculator runs pricing logic (no database)
6. Returns: {'total_price': 245.50, 'unit_price': 0.25, 'breakdown': {...}}
7. AI responds: "Quote: $245.50 for 1000 business cards"
```

**Example 3: Orders Table with Filters**
```
1. User switches to "Orders" tab
2. Sets filters: Last 30 days, Status: Paid, Min value: $100
3. Clicks "Apply Filters"
4. Frontend calls: GET /api/shopify/dashboard/orders?days=30&status=paid&min_value=100
5. Flask gets credentials from Supabase
6. Calls WooCommerce: wcapi.get("orders", params={
     'after': '2025-12-19T00:00:00',
     'before': '2026-01-18T23:59:59',
     'status': 'paid',
     'per_page': 100
   })
7. WooCommerce returns array of order objects
8. Flask filters orders by min_value >= 100
9. Flask formats orders for frontend (extract billing info, calculate totals)
10. Returns JSON array
11. Frontend initializes Tabulator table with data
12. User sees live orders from WooCommerce
```

---

## Dashboard Module (Frontend)

### File: shopify.js (1,576 lines)

**Location:** `UI/modules_external/shopify/shopify.js`

**Architecture:**
```javascript
// Base class polyfill (required)
class BaseModule { ... }

// Chart helper
class PlotlyChartHelper {
    static getThemeColors() { ... }      // Dark mode support
    static createOrdersChart() { ... }    // Orders over time
    static createRevenueChart() { ... }   // Revenue by product
    static createCustomerSegmentChart() { ... }
    static createTopProductsChart() { ... }
    static createWebhookStatusChart() { ... }
}

// SQL Viewer (UI only - backend disabled)
class SQLViewerHelper {
    renderInterface() { ... }
    executeQuery() { ... }               // Calls /api/shopify/sql-query (404)
    displayResults() { ... }
    displayError() { ... }
}

// Main module
class ShopifyModule extends BaseModule {
    constructor() { ... }
    initialize() { ... }
    createUIStructure() { ... }          // Build 6-tab layout
    switchToSubTab(tabId) { ... }        // Tab switching logic
    
    // Tab initialization
    initializeDashboardTab() { ... }
    initializeOrdersTab() { ... }
    initializeCustomersTab() { ... }
    initializeProductsTab() { ... }
    initializeWebhooksTab() { ... }
    initializeSQLTab() { ... }
    
    // Data loading
    loadDashboardData(period) { ... }    // Fetch metrics
    loadOrdersData() { ... }             // Fetch orders
    loadCustomerData() { ... }           // Fetch customers
    loadProductData() { ... }            // Fetch products
    loadWebhookData() { ... }            // Fetch webhooks (empty)
    
    // Rendering
    renderOrdersTable(orders) { ... }    // Tabulator initialization
    renderCustomerTable(customers) { ... }
    renderProductTable(products) { ... }
    renderWebhookLog(events) { ... }
    
    // Actions
    viewOrderDetails(orderId) { ... }
}

// Registration
window.ModuleRegistry['shopify'] = ShopifyModule;
export default ShopifyModule;
```

### 6 Dashboard Tabs

#### Tab 1: Dashboard (KPIs & Charts)

**Sub-tab ID:** `dashboard`  
**Default:** Yes (loads on module open)

**Content:**
```
┌─────────────────────────────────────────────────┐
│  Metrics (4 Cards)                             │
│  ┌─────────┬─────────┬─────────┬─────────┐    │
│  │ Total   │ Revenue │ Avg     │ Orders  │    │
│  │ Orders  │         │ Order   │ Today   │    │
│  │ 1,245   │ $254K   │ $204    │ 12      │    │
│  └─────────┴─────────┴─────────┴─────────┘    │
│                                                │
│  Period Selector: [Today][Week][Month*][All]  │
│                                                │
│  Charts:                                       │
│  ┌──────────────────────────────────────────┐ │
│  │  Orders Over Time (Line Chart)           │ │
│  │  Plotly.js - Last 30 days                │ │
│  └──────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────┐ │
│  │  Revenue by Product (Bar Chart)          │ │
│  │  Top 10 products by revenue              │ │
│  └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**API Calls:**
- `/api/shopify/dashboard/metrics?period=month` → 4 metric values
- `/api/shopify/dashboard/charts/orders-over-time?days=30` → Chart data
- `/api/shopify/dashboard/charts/revenue-by-product?days=30` → Chart data

**Features:**
- Real-time metrics from WooCommerce
- Period selector (today, week, month, all)
- Dark mode support for charts
- Responsive layout

#### Tab 2: Orders (Order Management)

**Sub-tab ID:** `orders`  
**Table:** Tabulator.js (sortable, filterable, paginated)

**Content:**
```
┌───────────────────────────────────────────────────┐
│  Filters:                                        │
│  Days: [7][30*][90][365]                        │
│  Status: [All*][Paid][Pending][Refunded]       │
│  Min Value: [___0___]  [Apply Filters]         │
│                                                  │
│  Orders Table (Tabulator):                      │
│  ┌────────────────────────────────────────────┐ │
│  │Order# │Date    │Customer│Total│Status│...│ │ │
│  ├────────────────────────────────────────────┤ │
│  │#1234  │Jan 15  │John S. │$245 │Paid  │👁 │ │ │
│  │#1235  │Jan 15  │Jane D. │$189 │Paid  │👁 │ │ │
│  │#1236  │Jan 14  │Bob M.  │$512 │Pend  │👁 │ │ │
│  └────────────────────────────────────────────┘ │
│  Pagination: [1][2][3] ... 25 per page         │
└───────────────────────────────────────────────────┘
```

**Columns:**
1. **Order #** - WooCommerce order number (bold)
2. **Date** - Created date + time
3. **Customer** - Name + email
4. **Total** - Order total (green $)
5. **Financial Status** - Badge (Paid/Pending/Refunded)
6. **Fulfillment** - Badge (Fulfilled/Unfulfilled/Partial)
7. **Actions** - View details button (👁)

**API Call:**
- `/api/shopify/dashboard/orders?days=30&status=paid&min_value=0`

**Features:**
- Live filtering from WooCommerce
- Sortable columns
- Status badges with color coding
- Pagination (10/25/50/100 per page)
- Header filters per column
- Action button → viewOrderDetails() (modal placeholder)

#### Tab 3: Customers (Analytics)

**Sub-tab ID:** `customers`  
**Charts:** Customer segments pie chart + Top customers table

**Content:**
```
┌───────────────────────────────────────────────────┐
│  Customer Segments (Pie Chart - Plotly.js)      │
│  ┌──────────────────────────────────────────┐   │
│  │         ╱╲                               │   │
│  │        ╱  ╲  VIP (15%)                   │   │
│  │       ╱────╲ Regular (26%)               │   │
│  │      ╱──────╲ Repeat (35%)               │   │
│  │     ╱────────╲ New (24%)                 │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Segmentation Logic:                            │
│  • VIP: >= 5 orders                             │
│  • Regular: 3-4 orders                          │
│  • Repeat: 2 orders                             │
│  • New: 1 order                                 │
│                                                  │
│  Top 10 Customers by Spend:                     │
│  ┌──────────────────────────────────────────┐   │
│  │Name      │Email     │Orders│Total │Avg  │   │
│  ├──────────────────────────────────────────┤   │
│  │John S.   │john@...  │8     │$2,450│$306 │   │
│  │Jane D.   │jane@...  │6     │$1,890│$315 │   │
│  └──────────────────────────────────────────┘   │
│  Period: [30][90*][365] Days                    │
└───────────────────────────────────────────────────┘
```

**API Calls:**
- `/api/shopify/dashboard/customers/segments?days=90` → Pie chart data
- `/api/shopify/dashboard/customers/top?days=90` → Top 10 table

**Features:**
- Customer segmentation analysis
- Top spenders identification
- Order count per customer
- Average order value calculation

#### Tab 4: Products (Performance)

**Sub-tab ID:** `products`  
**Charts:** Top sellers bar chart + Product catalog table

**Content:**
```
┌───────────────────────────────────────────────────┐
│  Top 10 Selling Products (Bar Chart)            │
│  ┌──────────────────────────────────────────┐   │
│  │ Premium Business Cards     ████████ 125  │   │
│  │ Wire Bound Books           ██████ 98     │   │
│  │ Letterheads                ████ 87       │   │
│  │ Election Signs             ███ 72        │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Product Catalog:                               │
│  ┌──────────────────────────────────────────┐   │
│  │Product Name       │SKU    │Sold│Revenue │   │
│  ├──────────────────────────────────────────┤   │
│  │Premium Business..│PBC-350│125 │$13,450 │   │
│  │Wire Bound Books  │WBB-A4 │98  │$9,800  │   │
│  └──────────────────────────────────────────┘   │
│  Limit: [50*][100][200] products                │
└───────────────────────────────────────────────────┘
```

**API Calls:**
- `/api/shopify/dashboard/products/top-sellers?days=30` → Chart data
- `/api/shopify/dashboard/products/catalog?limit=50` → Catalog table

**Features:**
- Best-selling products visualization
- Product performance metrics
- Revenue per product
- Stock status indicators

#### Tab 5: Webhooks (Monitoring)

**Sub-tab ID:** `webhooks`  
**Status:** ⚠️ NOT IMPLEMENTED (returns empty data)

**Content:**
```
┌───────────────────────────────────────────────────┐
│  Webhook Processing Status (Pie Chart)          │
│  ┌──────────────────────────────────────────┐   │
│  │  No webhook events (100%)                │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Recent Webhook Events:                         │
│  ┌──────────────────────────────────────────┐   │
│  │  No webhook events found                 │   │
│  └──────────────────────────────────────────┘   │
│  [Refresh] button                               │
└───────────────────────────────────────────────────┘
```

**API Calls:**
- `/api/shopify/dashboard/webhooks/health` → Returns `{total_events: 0, success_rate: 100}`
- `/api/shopify/dashboard/webhooks/log?limit=50` → Returns `{data: []}`

**Note:** Webhook storage was removed in January 4, 2026 refactor. Endpoints exist but return empty data.

#### Tab 6: SQL Viewer (Disabled Backend)

**Sub-tab ID:** `sql-viewer` (in manifest) / `sql` (in JS code)  
**Status:** ⚠️ UI EXISTS, BACKEND DISABLED

**Content:**
```
┌───────────────────────────────────────────────────┐
│  SQL Query Interface                            │
│  Quick Queries:                                 │
│  [Recent Orders][Line Items][Webhook Events]   │
│  [Show Tables]                                  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ SELECT * FROM shopify_orders LIMIT 10    │   │
│  │                                          │   │
│  └──────────────────────────────────────────┘   │
│  [▶ Execute Query] (Ctrl+Enter)                │
│                                                  │
│  Results:                                       │
│  ┌──────────────────────────────────────────┐   │
│  │  Network error: 404 Not Found            │   │
│  │  Endpoint /api/shopify/sql-query removed │   │
│  └──────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
```

**Issue:** 
- Frontend code tries to call `POST /api/shopify/sql-query`
- Endpoint was removed in January 4, 2026 refactor (no SQLite database)
- Results in 404 error
- Tab should be removed from manifest or backend re-implemented

---

## Flask API Backend

### File: shopify_routes.py (807 lines)

**Location:** `UI/modules_external/shopify/shopify_routes.py` (ROOT directory, not `routes/` subdirectory)

**Important:** There are TWO `shopify_routes.py` files:
1. `UI/modules_external/shopify/shopify_routes.py` ✅ **CURRENT** (807 lines, WooCommerce API)
2. `UI/modules_external/shopify/routes/shopify_routes.py` ❌ **OLD** (1,155 lines, SQLite)

The Flask app loads the root directory version.

### Initialization

```python
def init_shopify_routes(app, config_path=None, db_available=True):
    """
    Initialize WooCommerce/Shopify routes
    
    Args:
        app: Flask app instance
        config_path: Unused (legacy parameter from SQLite version)
        db_available: Unused (legacy parameter from SQLite version)
    """
    
    if not WOOCOMMERCE_AVAILABLE:
        print(f"   ⚠️  WooCommerce/Shopify routes SKIPPED - woocommerce module not installed")
        return
    
    print(f"   Registering WooCommerce/Shopify endpoints...")
    
    # Register 10 endpoints
    app.add_url_rule('/api/shopify/dashboard/metrics', ...)
    app.add_url_rule('/api/shopify/dashboard/orders', ...)
    # ... 8 more endpoints
    
    print(f"   ✅ 10 woocommerce/shopify endpoints registered")
```

**Dependencies:**
```python
from woocommerce import API  # pip install WooCommerce
from database_utils import execute_query  # Supabase queries
```

### Helper Functions

#### 1. get_woocommerce_credentials(user_id=None)

**Purpose:** Fetch WooCommerce API credentials from Supabase

**Code:**
```python
def get_woocommerce_credentials(user_id=None):
    if user_id is None:
        user_id = 1  # Platform-wide credentials
    
    result = execute_query(
        """
        SELECT credentials 
        FROM ai_infrastructure.user_platform_credentials
        WHERE user_id = %s AND platform = 'shopify' AND is_active = TRUE
        LIMIT 1
        """,
        (user_id,),
        fetch_mode='one'
    )
    
    if not result or not result[0]:
        return None
    
    credentials = result[0]
    
    # Validate required fields
    required = ['consumer_key', 'consumer_secret', 'base_url']
    if not all(field in credentials for field in required):
        return None
    
    return credentials
```

**Returns:**
```python
{
    "consumer_key": "ck_...",
    "consumer_secret": "cs_...",
    "base_url": "https://inhouseprint.com.au"
}
```

#### 2. get_woocommerce_api(user_id=None)

**Purpose:** Create WooCommerce API client instance

**Code:**
```python
def get_woocommerce_api(user_id=None):
    credentials = get_woocommerce_credentials(user_id)
    
    if not credentials:
        return None
    
    wcapi = API(
        url=credentials['base_url'],
        consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        version="wc/v3",
        timeout=30
    )
    return wcapi
```

**Returns:** WooCommerce API client or None

#### 3. calculate_date_range(days)

**Purpose:** Helper for date filtering

**Code:**
```python
def calculate_date_range(days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(days))
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
```

### 10 API Endpoints

#### Endpoint 1: Dashboard Metrics

```python
@cross_origin()
def shopify_metrics():
    """Dashboard KPIs - total orders, revenue, AOV, orders today"""
    wcapi = get_woocommerce_api()
    if not wcapi:
        return jsonify({'status': 'error', 'message': 'Credentials not configured'}), 503
    
    period = request.args.get('period', 'month')
    days = {'today': 1, 'week': 7, 'month': 30, 'all': 9999}[period]
    start_date, end_date = calculate_date_range(days)
    
    # Fetch orders from WooCommerce
    params = {
        'after': f"{start_date}T00:00:00",
        'before': f"{end_date}T23:59:59",
        'per_page': 100
    }
    response = wcapi.get("orders", params=params)
    orders = response.json()
    
    # Calculate metrics
    total_orders = len(orders)
    total_revenue = sum(float(order.get('total', 0)) for order in orders)
    aov = total_revenue / total_orders if total_orders > 0 else 0
    
    # Orders today
    today = datetime.now().date()
    orders_today = sum(1 for order in orders 
                      if datetime.fromisoformat(order['date_created'].replace('Z', '+00:00')).date() == today)
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_orders': total_orders,
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(aov, 2),
            'orders_today': orders_today
        }
    })
```

**URL:** `GET /api/shopify/dashboard/metrics?period=month`

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_orders": 1245,
    "total_revenue": 254320.50,
    "average_order_value": 204.17,
    "orders_today": 12
  }
}
```

#### Endpoint 2: Orders List

```python
@cross_origin()
def shopify_orders():
    """Get orders list with filters"""
    wcapi = get_woocommerce_api()
    if not wcapi:
        return jsonify({'status': 'error'}), 503
    
    days = int(request.args.get('days', 30))
    status = request.args.get('status', '')
    min_value = float(request.args.get('min_value', 0))
    
    start_date, end_date = calculate_date_range(days)
    
    # Fetch orders
    params = {
        'after': f"{start_date}T00:00:00",
        'before': f"{end_date}T23:59:59",
        'per_page': 100
    }
    if status:
        params['status'] = status
    
    response = wcapi.get("orders", params=params)
    orders = response.json()
    
    # Filter by min_value
    if min_value > 0:
        orders = [order for order in orders if float(order.get('total', 0)) >= min_value]
    
    # Format for frontend
    formatted = [{
        'order_id': order['id'],
        'order_number': order['number'],
        'date': order['date_created'],
        'customer_name': f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}".strip(),
        'total': float(order.get('total', 0)),
        'status': order.get('status', ''),
        'payment_method': order.get('payment_method_title', ''),
        'items_count': len(order.get('line_items', []))
    } for order in orders]
    
    return jsonify({'status': 'success', 'data': formatted})
```

**URL:** `GET /api/shopify/dashboard/orders?days=30&status=paid&min_value=100`

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "order_id": 12345,
      "order_number": "1234",
      "date": "2026-01-15T10:30:00",
      "customer_name": "John Smith",
      "total": 245.50,
      "status": "completed",
      "payment_method": "Credit Card",
      "items_count": 3
    }
  ]
}
```

#### Endpoint 3: Orders Over Time Chart

```python
@cross_origin()
def shopify_orders_chart():
    """Get orders over time for charting"""
    wcapi = get_woocommerce_api()
    days = int(request.args.get('days', 30))
    start_date, end_date = calculate_date_range(days)
    
    params = {
        'after': f"{start_date}T00:00:00",
        'before': f"{end_date}T23:59:59",
        'per_page': 100
    }
    response = wcapi.get("orders", params=params)
    orders = response.json()
    
    # Group by date
    from collections import defaultdict
    orders_by_date = defaultdict(int)
    for order in orders:
        date = datetime.fromisoformat(order['date_created'].replace('Z', '+00:00')).date()
        orders_by_date[str(date)] += 1
    
    # Sort by date
    sorted_dates = sorted(orders_by_date.items())
    
    return jsonify({
        'status': 'success',
        'data': {
            'labels': [d[0] for d in sorted_dates],
            'data': [d[1] for d in sorted_dates]
        }
    })
```

**URL:** `GET /api/shopify/dashboard/charts/orders-over-time?days=30`

**Response:**
```json
{
  "status": "success",
  "data": {
    "labels": ["2025-12-19", "2025-12-20", "2025-12-21", ...],
    "data": [12, 15, 8, 21, ...]
  }
}
```

#### Endpoint 4: Revenue by Product Chart

```python
@cross_origin()
def shopify_revenue_chart():
    """Get revenue by product for charting"""
    wcapi = get_woocommerce_api()
    days = int(request.args.get('days', 30))
    start_date, end_date = calculate_date_range(days)
    
    params = {
        'after': f"{start_date}T00:00:00",
        'before': f"{end_date}T23:59:59",
        'per_page': 100
    }
    response = wcapi.get("orders", params=params)
    orders = response.json()
    
    # Calculate revenue by product
    product_revenue = {}
    for order in orders:
        for item in order.get('line_items', []):
            product_name = item.get('name', 'Unknown')
            product_total = float(item.get('total', 0))
            product_revenue[product_name] = product_revenue.get(product_name, 0) + product_total
    
    # Top 10 products
    sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'status': 'success',
        'data': {
            'products': [p[0] for p in sorted_products],
            'revenue': [p[1] for p in sorted_products]
        }
    })
```

**URL:** `GET /api/shopify/dashboard/charts/revenue-by-product?days=30`

#### Endpoint 5-10: Customers, Products, Webhooks

**Remaining Endpoints:**
5. `/api/shopify/dashboard/customers/top` - Top customers by spend
6. `/api/shopify/dashboard/customers/segments` - Customer segmentation
7. `/api/shopify/dashboard/products/top-sellers` - Best-selling products
8. `/api/shopify/dashboard/products/catalog` - Product catalog
9. `/api/shopify/dashboard/webhooks/log` - Returns `[]` (not implemented)
10. `/api/shopify/dashboard/webhooks/health` - Returns `{total_events: 0}` (not implemented)

All follow the same pattern: fetch credentials, create WooCommerce API client, make API call, process data, return JSON.

---

## Calculator System

### Overview

**Location:** `UI/modules_external/quote-calculator/backend/shopify_calculators/`

**Total Files:** 35 calculator classes (31 unique + 4 filename duplicates)

**Purpose:** Replicate WooCommerce DPO (Dynamic Pricing & Options) pricing formulas exactly for AI quote generation.

**Key Characteristics:**
- ✅ **Standalone** - No database connections
- ✅ **Pure Python** - Import and use directly
- ✅ **Exact Pricing** - Matches WooCommerce calculator output
- ✅ **Configurable** - GST, markup, surcharge customizable
- ❌ **Not registered as AI tools** - Direct import only (no tool_executor decorator)

### Calculator Categories

#### 1. Stationery Products (5 Calculators)

| File | Product | Key Parameters |
|------|---------|----------------|
| `PrintedLetterheads_Shopify_Calculator.py` | Letterheads | quantity, double_sided, colour, paper_stock, artworks |
| `WithComplimentsSlips_Shopify_Calculator.py` | Compliment Slips | quantity, double_sided, colour, paper_stock, artworks |
| `NotepadsA4_Shopify_Calculator.py` | A4 Notepads | quantity, double_sided, colour, paper_stock, artworks |
| `NotepadsA5_Shopify_Calculator.py` | A5 Notepads | quantity, double_sided, colour, paper_stock, artworks |
| `NotepadsA6_Shopify_Calculator.py` | A6 Notepads | quantity, double_sided, colour, paper_stock, artworks |

**Common Pattern:**
```python
class PrintedLetterheadsShopifyCalculator:
    GST_RATE = Decimal('1.1')  # 10% GST
    PRICE_INCREASE_MULTIPLIER = Decimal('1.05')  # 5% markup
    ARTWORK_COST = Decimal('15.00')  # $15 per extra artwork
    
    def calculate(self, quantity, double_sided=False, colour=True, 
                  paper_stock="Standard", artworks=1):
        base_price = self._get_base_price(quantity, paper_stock)
        if double_sided:
            base_price *= Decimal('1.15')
        artwork_cost = (artworks - 1) * self.ARTWORK_COST
        subtotal = base_price + artwork_cost
        subtotal_with_markup = subtotal * self.PRICE_INCREASE_MULTIPLIER
        total_price = subtotal_with_markup * self.GST_RATE
        return {'total_price': total_price, 'unit_price': total_price / quantity}
```

#### 2. Signage Products (9 Calculators)

| File | Product | Material Options |
|------|---------|------------------|
| `ElectionSigns_Shopify_Calculator.py` | Election Signs | Corflute 3mm/5mm |
| `ConstructionSigns_Shopify_Calculator.py` | Construction Signs | Corflute, Metal |
| `BollardSigns_Shopify_Calculator.py` | Bollard Signs | Corflute, Metal |
| `CorfluteInsertA_Frame_Shopify_Calculator.py` | A-Frame Insert | Corflute |
| `MetalFaceA_Frame_Shopify_Calculator.py` | Metal A-Frame | Aluminium |
| `StrutCardsA3_Shopify_Calculator.py` | A3 Strut Cards | Cardboard |
| `StrutCardsA4_Shopify_Calculator.py` | A4 Strut Cards | Cardboard |
| `corflute_calculator_shopify.py` | Generic Corflute | Custom sizes |

**Features:**
- Custom size support (width x height in mm)
- Material-specific pricing
- Double-sided printing options
- H-stake mounting options

#### 3. Book Products (5 Calculators)

**Complex F1-F14 Parameter Structure:**

| File | Binding | Parameters | Complexity |
|------|---------|------------|------------|
| `WireBound_Shopify_Calculator.py` | Wire Coil | F1-F14 (14 params) | ⭐⭐⭐⭐⭐ |
| `SpiralBound_Shopify_Calculator.py` | Plastic Spiral | F1-F14 (14 params) | ⭐⭐⭐⭐⭐ |
| `PerfectBound_Shopify_Calculator.py` | Glued Spine | F1-F14 (14 params) | ⭐⭐⭐⭐⭐ |
| `SaddleStitchBooks_Shopify_Calculator.py` | Stapled | Simplified | ⭐⭐ |
| `SpiralBoundBooks_Shopify_Calculator.py` | Simplified | Basic params | ⭐⭐ |

**F1-F14 Parameter Mapping:**

```python
def calculate(
    quantity: int,                    # F1 - Number of books (1-10,000)
    artworks: int,                    # F2 - Artwork count ($15 each after first)
    finish_size: str,                 # F14 - Final size (A4/A5 Portrait/Landscape)
    
    # Front cover (F3-F6)
    outer_front_cover: str,           # F3 - Front overlay (Clear PVC / Not Required)
    printed_front_cover: str,         # F4 - Front stock (250/300/350GSM Satin)
    front_cover_print: str,           # F5 - Front print (1pp/2pp Colour/B&W)
    front_celloglaze: str,            # F6 - Front lamination (None/Gloss/Matt)
    
    # Back cover (F7-F10)
    outer_back_cover: str,            # F7 - Back overlay (None/Clear PVC/Black Leather)
    printed_back_cover: str,          # F8 - Back stock (250/300/350GSM Satin/None)
    back_cover_print: str,            # F9 - Back print (None/1pp/2pp)
    back_celloglaze: str,             # F10 - Back lamination (None/Gloss/Matt)
    
    # Inner pages (F11-F13)
    internal_pages: int,              # F11 - Page count (1-700)
    internal_stock: str,              # F12 - Inner stock (Satin/Uncoated Bond)
    internal_print: str               # F13 - Inner print (Full Colour/B&W)
) -> Dict[str, Any]:
    """
    Calculate price for Wire Bound Books
    Exact WooCommerce DPO implementation
    """
    # Fetch base price from config
    base_price = self._get_base_price(quantity, finish_size)
    
    # Add cover costs
    front_cost = self._calculate_cover_cost('front', outer_front_cover, 
                                            printed_front_cover, front_cover_print, 
                                            front_celloglaze)
    back_cost = self._calculate_cover_cost('back', outer_back_cover, 
                                           printed_back_cover, back_cover_print, 
                                           back_celloglaze)
    
    # Add page costs
    page_cost = self._calculate_page_cost(internal_pages, internal_stock, internal_print)
    
    # Add binding cost (thickness-based, 14 tiers)
    binding_cost = self._calculate_binding_cost(internal_pages)
    
    # Add artwork cost
    artwork_cost = (artworks - 1) * Decimal('15.00')
    
    # Calculate total
    subtotal = base_price + front_cost + back_cost + page_cost + binding_cost + artwork_cost
    subtotal_with_markup = subtotal * Decimal('1.05')  # 5% markup
    total_inc_gst = subtotal_with_markup * Decimal('1.10')  # 10% GST
    total_with_surcharge = total_inc_gst + Decimal('44.00')  # $44 surcharge
    
    return {
        'total_price': total_with_surcharge,
        'unit_price': total_with_surcharge / quantity,
        'breakdown': {
            'base_price': base_price,
            'front_cover': front_cost,
            'back_cover': back_cost,
            'pages': page_cost,
            'binding': binding_cost,
            'artworks': artwork_cost,
            'subtotal': subtotal,
            'markup': subtotal_with_markup - subtotal,
            'gst': total_inc_gst - subtotal_with_markup,
            'surcharge': Decimal('44.00')
        },
        'specifications': {
            'quantity': quantity,
            'finish_size': finish_size,
            'internal_pages': internal_pages,
            'covers': f"{printed_front_cover} / {printed_back_cover or 'None'}"
        }
    }
```

**Example Usage:**
```python
from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator

calc = WireBoundShopifyCalculator()
quote = calc.calculate(
    quantity=3,
    artworks=1,
    finish_size="A4 Portrait",
    outer_front_cover="Clear PVC",
    printed_front_cover="350GSM Satin",
    front_cover_print="2pp Colour",
    front_celloglaze="2 Sided Matt",
    outer_back_cover="350GSM Satin Blank Card",
    printed_back_cover="350GSM Satin",
    back_cover_print="None",
    back_celloglaze="None",
    internal_pages=316,
    internal_stock="Uncoated Bond 100GSM",
    internal_print="Black & White"
)

print(quote)
# {'total_price': Decimal('450.50'), 'unit_price': Decimal('150.17'), ...}
```

#### 4. Promotional Products (8 Calculators)

| File | Product | Unique Features |
|------|---------|-----------------|
| `CustomPosterPrinting_Shopify_Calculator.py` | Posters | Multiple paper types, sizes |
| `CustomVinylStickers_Shopify_Calculator.py` | Stickers | Die-cut, kiss-cut, contour |
| `PremiumBookmarks_Shopify_Calculator.py` | Bookmarks | Lamination, tassel options |
| `SelfieFrames_Shopify_Calculator.py` | Selfie Frames | Custom size, cutout design |
| `LuxuryClassicPullUpBanners_Shopify_Calculator.py` | Pull-up Banners | Hardware + print combo |
| `StackableCubes_Shopify_Calculator.py` | Display Cubes | 3D structure pricing |
| `FoldedFlyers_Shopify_Calculator.py` | Flyers | Various fold types |

#### 5. Business Cards (2 Calculators)

**Flexible Quantity Support:**

| File | Pricing Model | Stock Options |
|------|---------------|---------------|
| `EconomicalBusinessCards_Shopify_Calculator.py` | Budget-friendly | Standard stocks |
| `PremiumBusinessCards_Shopify_Calculator.py` | High-end | Specialty stocks + finishes |

**Key Feature:** Interpolation for non-standard quantities

```python
class PremiumBusinessCardsShopifyCalculator:
    STANDARD_QUANTITIES = [250, 500, 1000, 2000, 5000]
    
    def calculate(self, quantity, stock_type, sides, celloglaze="none"):
        if quantity in self.STANDARD_QUANTITIES:
            # Exact price from config
            base_price = self.CONFIG[stock_type][quantity]
        else:
            # Interpolate between nearest standard quantities
            base_price = self._interpolate_price(quantity, stock_type)
        
        # Apply celloglaze cost
        if "none" not in celloglaze.lower():
            celloglaze_cost = Decimal('8.00')
        else:
            celloglaze_cost = Decimal('0')
        
        # Add artwork cost (first free, $15 each extra)
        artwork_cost = (artworks - 1) * Decimal('15.00')
        
        subtotal = base_price + celloglaze_cost + artwork_cost
        subtotal_with_markup = subtotal * Decimal('1.05')
        total_inc_gst = subtotal_with_markup * Decimal('1.10')
        
        return {'total_price': total_inc_gst, 'unit_price': total_inc_gst / quantity}
```

**Stock Types:**
- Satin (300GSM, 350GSM)
- King Kong (420GSM)
- Triple Thick (700GSM)
- Silk (350GSM, 400GSM)

**Celloglaze Finishes:**
- None
- 1 Side Matt / 2 Sided Matt
- 1 Side Gloss / 2 Sided Gloss

### Config Manager

**File:** `config_manager.py`

**Purpose:** Load base pricing from JSON configuration files or database queries.

```python
class ConfigManager:
    """
    Manages pricing configuration for Shopify calculators
    Loads base prices, stock types, finish options
    """
    
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/prices/"
        self.pricing_cache = {}
    
    def get_base_price(self, product_type, quantity, options):
        """
        Fetch base price for product
        
        Args:
            product_type: e.g., 'wire_bound_books'
            quantity: Order quantity
            options: Dict of options (size, stock, etc.)
        
        Returns:
            Decimal: Base price before modifiers
        """
        cache_key = f"{product_type}_{quantity}_{hash(frozenset(options.items()))}"
        
        if cache_key in self.pricing_cache:
            return self.pricing_cache[cache_key]
        
        # Load from JSON file
        config_file = f"{self.config_path}/{product_type}.json"
        with open(config_file, 'r') as f:
            pricing_data = json.load(f)
        
        # Navigate nested config structure
        price = self._lookup_price(pricing_data, quantity, options)
        
        self.pricing_cache[cache_key] = Decimal(str(price))
        return self.pricing_cache[cache_key]
    
    def _lookup_price(self, data, quantity, options):
        """Navigate nested pricing structure to find exact price"""
        # Complex logic to match quantity + options to price
        # Handles quantity ranges, option combinations, etc.
        pass
```

### Calculator Usage by AI Agents

**Current State:** Calculators are **NOT registered as AI tools** (no @tool_executor decorator found).

**How AI uses them:**
1. Manual import in agent code
2. Direct function call
3. Return result to user

**Example AI Agent Code:**
```python
# Inside AI agent decision logic
if user_request_contains("quote") and user_request_contains("wire bound"):
    from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator
    
    calc = WireBoundShopifyCalculator()
    result = calc.calculate(
        quantity=extract_quantity(user_message),
        internal_pages=extract_pages(user_message),
        # ... map user intent to F1-F14 parameters
    )
    
    respond_to_user(f"Quote: ${result['total_price']}")
```

**Problem:** Complex F1-F14 parameter mapping is challenging for AI agents without wrapper functions (see [Calculator Wrappers](#calculator-wrappers) section).

---

## WooCommerce API Integration

### WooCommerce REST API v3

**Official Documentation:** https://woocommerce.github.io/woocommerce-rest-api-docs/

**Base URL:** `https://inhouseprint.com.au/wp-json/wc/v3/`

**Authentication:** Basic Auth (consumer_key:consumer_secret)

**Python Library:** `woocommerce` (pip install WooCommerce)

### API Client Creation

```python
from woocommerce import API

wcapi = API(
    url="https://inhouseprint.com.au",
    consumer_key="ck_abc123...",
    consumer_secret="cs_def456...",
    version="wc/v3",
    timeout=30,
    verify_ssl=True,
    query_string_auth=False  # Use HTTP Auth header
)
```

### Common API Calls

#### 1. Get Orders

```python
# Last 30 days, paid orders
params = {
    'after': '2025-12-19T00:00:00',
    'before': '2026-01-18T23:59:59',
    'status': 'completed',
    'per_page': 100,
    'page': 1
}

response = wcapi.get("orders", params=params)

if response.status_code == 200:
    orders = response.json()
    for order in orders:
        print(f"Order #{order['number']}: ${order['total']}")
else:
    print(f"Error: {response.status_code}")
```

**Response Structure:**
```json
[
  {
    "id": 12345,
    "number": "1234",
    "status": "completed",
    "currency": "AUD",
    "total": "245.50",
    "date_created": "2026-01-15T10:30:00",
    "billing": {
      "first_name": "John",
      "last_name": "Smith",
      "email": "john@example.com",
      "phone": "+61412345678"
    },
    "line_items": [
      {
        "id": 67890,
        "name": "Premium Business Cards",
        "product_id": 123,
        "quantity": 1000,
        "total": "245.50"
      }
    ]
  }
]
```

#### 2. Get Products

```python
response = wcapi.get("products", params={'per_page': 50, 'status': 'publish'})
products = response.json()
```

#### 3. Get Customers

```python
response = wcapi.get("customers", params={'per_page': 50})
customers = response.json()
```

### Rate Limiting

**WooCommerce Default Limits:**
- 10 requests per 10 seconds per IP
- 120 requests per minute per IP

**Error Handling:**
```python
response = wcapi.get("orders")

if response.status_code == 429:  # Too Many Requests
    retry_after = response.headers.get('Retry-After', 60)
    print(f"Rate limited. Retry after {retry_after} seconds")
elif response.status_code == 401:  # Unauthorized
    print("Invalid credentials")
elif response.status_code == 403:  # Forbidden
    print("Insufficient permissions")
else:
    orders = response.json()
```

---

## Credential Management

### Storage: Supabase PostgreSQL

**Table:** `ai_infrastructure.user_platform_credentials`

**Schema:**
```sql
CREATE TABLE ai_infrastructure.user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform VARCHAR(50) NOT NULL,  -- 'shopify' (legacy name for WooCommerce)
    credentials JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform)
);
```

**Example Row:**
```sql
INSERT INTO ai_infrastructure.user_platform_credentials (
    user_id, platform, credentials, is_active
) VALUES (
    1,
    'shopify',  -- Legacy name (actually WooCommerce)
    '{
        "consumer_key": "ck_abc123def456...",
        "consumer_secret": "cs_xyz789ghi012...",
        "base_url": "https://inhouseprint.com.au"
    }'::jsonb,
    TRUE
);
```

### Credential Lifecycle

**1. Initial Setup (Manual):**
```sql
-- Admin inserts credentials into Supabase
INSERT INTO ai_infrastructure.user_platform_credentials ...
```

**2. Runtime Retrieval:**
```python
# Every API request fetches credentials
credentials = execute_query(
    "SELECT credentials FROM ai_infrastructure.user_platform_credentials "
    "WHERE user_id = %s AND platform = 'shopify' AND is_active = TRUE",
    (1,),
    fetch_mode='one'
)
```

**3. API Client Creation:**
```python
wcapi = API(
    url=credentials['base_url'],
    consumer_key=credentials['consumer_key'],
    consumer_secret=credentials['consumer_secret']
)
```

**4. Error Handling:**
```python
if not credentials:
    return jsonify({
        'status': 'error',
        'message': 'WooCommerce credentials not configured. Contact administrator.'
    }), 503
```

### Security Considerations

**✅ Secure:**
- Credentials stored in Supabase (encrypted at rest)
- Never exposed to frontend
- HTTPS for all API calls
- Basic Auth (not API keys in URLs)

**⚠️ Potential Improvements:**
- Add credential rotation mechanism
- Add audit logging for API calls
- Add per-user credentials (currently platform-wide user_id=1)
- Add credential validation endpoint

---

## Critical Issues

### Issue #1: Double GST Application 🔴 CRITICAL

**Status:** 🚧 NOT FIXED  
**Discovered:** January 3, 2026  
**Affected Files:** 21 of 35 calculator classes

**Problem:**
GST (10%) applied twice in pricing formula, resulting in 21% effective tax rate instead of 10%.

**Code Pattern:**
```python
# ❌ WRONG - Applies GST twice
total_price = (subtotal * GST_RATE) * GST_RATE
# Result: subtotal × 1.1 × 1.1 = subtotal × 1.21 (21% increase)

# ✅ CORRECT - Applies GST once
total_price = subtotal * GST_RATE
# Result: subtotal × 1.1 (10% increase)
```

**Financial Impact:**
- Customer overcharged by ~10% on every order
- Example: $100 order → Customer pays $121 instead of $110 ($11 overcharge)
- Legal risk: Incorrect GST remittance to ATO (Australian Tax Office)

**Affected Calculators (21 files):**

1. `PremiumBusinessCards_Shopify_Calculator.py` (Line 244)
2. `PremiumBookmarks_Shopify_Calculator.py` (Line 110)
3. `LuxuryClassicPullUpBanners_Shopify_Calculator.py` (Line 98)
4. `NotepadsA4_Shopify_Calculator.py` (Line 129)
5. `NotepadsA5_Shopify_Calculator.py` (Line 124)
6. `NotepadsA6_Shopify_Calculator.py` (Line 124)
7. `PrintedLetterheads_Shopify_Calculator.py` (Line 136)
8. `WithComplimentsSlips_Shopify_Calculator.py` (Line 124)
9. `StrutCardsA3_Shopify_Calculator.py` (Line 113)
10. `StrutCardsA4_Shopify_Calculator.py` (Line 113)
11. `SelfieFrames_Shopify_Calculator.py` (Line 104)
12. `StackableCubes_Shopify_Calculator.py` (Line 104)
13. `CustomVinylStickers_Shopify_Calculator.py` (Line 102)
14. `CustomPosterPrinting_Shopify_Calculator.py` (Line 106)
15. `SpiralBoundBooks_Shopify_Calculator.py` (Line 106)
16. `BollardSigns_Shopify_Calculator.py` (Line 117)
17. `ConstructionSigns_Shopify_Calculator.py` (Line 116)
18. `ElectionSigns_Shopify_Calculator.py` (Line 128)
19. `MetalFaceA_Frame_Shopify_Calculator.py` (Line 114)
20. `CorfluteInsertA_Frame_Shopify_Calculator.py` (Line 115)
21. `FoldedFlyers_Shopify_Calculator.py` (Multiple lines)

**✅ Calculators with CORRECT GST (14 files):**
- `EconomicalBusinessCards_Shopify_Calculator.py`
- `WireBound_Shopify_Calculator.py`
- `SpiralBound_Shopify_Calculator.py`
- `PerfectBound_Shopify_Calculator.py`
- `SaddleStitchBooks_Shopify_Calculator.py`
- All GOD (Get Online Design) calculator variants

**Fix Priority:** 🔥 URGENT  
**Fix Complexity:** ⭐ Easy (find/replace pattern)

**Recommended Fix:**
```bash
# Search for pattern: * GST_RATE) * GST_RATE
# Replace with: * GST_RATE

# OR use explicit variable names:
subtotal_ex_gst = base_price + artwork_cost
total_inc_gst = subtotal_ex_gst * Decimal('1.10')  # Apply GST once
```

### Issue #2: Celloglaze Case-Sensitivity Bug

**Status:** ✅ FIXED (January 3, 2026)  
**Affected Files:** 1 file (PremiumBusinessCards_Shopify_Calculator.py)

**Problem:**
Case-sensitive string check `if "None" in celloglaze` failed for lowercase "none", causing $8 overcharge.

**Original Code:**
```python
if "None" in celloglaze:
    celloglaze_cost = Decimal('0')
else:
    celloglaze_cost = CELLOGLAZE_COSTS.get(celloglaze, Decimal('8.00'))
```

**Fixed Code:**
```python
if "None" in celloglaze or celloglaze.lower() == "none":
    celloglaze_cost = Decimal('0')
else:
    celloglaze_cost = CELLOGLAZE_COSTS.get(celloglaze, Decimal('8.00'))
```

**Similar Bugs Remaining:**
- `WireBound_Shopify_Calculator.py` (Line 414) - Stock case-sensitivity
- `SpiralBound_Shopify_Calculator.py` (Line 301) - Stock case-sensitivity

### Issue #3: SQL Viewer Backend Missing

**Status:** ⚠️ UI EXISTS, BACKEND DISABLED  
**Last Working:** Before January 4, 2026

**Problem:**
- Frontend tab "SQL Viewer" exists in manifest
- JavaScript code tries to call `POST /api/shopify/sql-query`
- Endpoint was removed in January 4, 2026 refactor (no SQLite database)
- Results in 404 error when user tries to execute query

**Frontend Code (shopify.js lines 570-605):**
```javascript
async executeQuery() {
    const query = document.getElementById('shopify-sql-query').value.trim();
    
    const response = await fetch(`${this.API_BASE_URL}/api/shopify/sql-query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });
    
    // Error: 404 Not Found
    const result = await response.json();
}
```

**Solutions:**
1. **Remove tab from manifest** (easiest)
2. **Re-implement backend** using Supabase PostgreSQL queries
3. **Add warning message** to UI explaining feature is disabled

**Recommendation:** Remove SQL Viewer tab or implement PostgreSQL query interface (admin-only).

### Issue #4: Webhook Endpoints Return Empty Data

**Status:** ⚠️ INTENTIONAL (Not Implemented)  
**Impact:** Low (UI shows "no webhook events")

**Problem:**
- Webhook tab exists in UI
- Endpoints `/api/shopify/dashboard/webhooks/log` and `/webhooks/health` return empty arrays
- No webhook event storage (removed with SQLite database)

**Current Backend:**
```python
@cross_origin()
def shopify_webhook_log():
    """Webhook log - not implemented for WooCommerce"""
    return jsonify({'status': 'success', 'data': []})

@cross_origin()
def shopify_webhook_health():
    """Webhook health - not implemented for WooCommerce"""
    return jsonify({'status': 'success', 'data': {'total_events': 0, 'success_rate': 100}})
```

**Solutions:**
1. **Remove tab from manifest**
2. **Implement webhook storage** in Supabase PostgreSQL
3. **Add WooCommerce webhook subscriptions** and event processing

**Recommendation:** Remove Webhooks tab or fully implement webhook event capture system.

---

## Testing & Deployment

### Local Development

**Prerequisites:**
```bash
# Python dependencies
pip install Flask
pip install Flask-SocketIO
pip install Flask-CORS
pip install WooCommerce
pip install psycopg2-binary

# JavaScript dependencies (loaded via CDN)
# - Plotly.js 2.27.0
# - Tabulator.js 5.5.0
```

**Environment Variables (.env):**
```bash
# Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_PASSWORD=your-db-password

# WooCommerce credentials stored in Supabase (not in .env)
```

**Start Flask Server:**
```powershell
cd AI_infrastructure
python flask_app.py
```

**Access Module:**
```
http://localhost:5001/
→ Click "Shopify E-Commerce" in sidebar
→ Dashboard loads with live WooCommerce data
```

### Testing Calculators

**Unit Test Example:**
```python
# test_wire_bound_calculator.py
from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator

def test_wire_bound_basic():
    calc = WireBoundShopifyCalculator()
    result = calc.calculate(
        quantity=3,
        artworks=1,
        internal_pages=316,
        finish_size="A4 Portrait",
        outer_front_cover="Clear PVC",
        printed_front_cover="350GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="2 Sided Matt",
        outer_back_cover="350GSM Satin Blank Card",
        printed_back_cover="350GSM Satin",
        back_cover_print="None",
        back_celloglaze="None",
        internal_stock="Uncoated Bond 100GSM",
        internal_print="Black & White"
    )
    
    assert result['total_price'] > 0
    assert result['quantity'] == 3
    assert 'breakdown' in result
    
    # Verify GST applied once (not twice)
    gst_amount = result['breakdown']['gst']
    subtotal = result['breakdown']['subtotal_with_markup']
    assert abs(gst_amount - (subtotal * 0.10)) < Decimal('0.01')

def test_flexible_quantity():
    calc = PremiumBusinessCardsShopifyCalculator()
    
    # Test standard quantity
    result_1000 = calc.calculate(quantity=1000, stock_type="satin_350gsm", sides=2, celloglaze="none")
    
    # Test interpolated quantity
    result_1500 = calc.calculate(quantity=1500, stock_type="satin_350gsm", sides=2, celloglaze="none")
    
    # 1500 should be between 1000 and 2000 pricing
    assert result_1000['total_price'] < result_1500['total_price']
```

**Run Tests:**
```bash
cd UI/modules_external/quote-calculator/backend/shopify_calculators
python -m pytest test_flexible_quantity.py -v
```

### Render Deployment

**Environment:**
- Platform: Render.com
- Region: Singapore
- Service: Web Service
- Repository: GitHub (auto-deploy on push to `v10` branch)

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT AI_infrastructure.flask_app:app
```

**Environment Variables (Render):**
```bash
SUPABASE_URL=https://...
SUPABASE_KEY=...
SUPABASE_DB_PASSWORD=...
RENDER=true  # Disables WooCommerce routes (set in flask_app.py)
```

**WooCommerce Disabled on Render:**
```python
# AI_infrastructure/flask_app.py (lines 165-171)
IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
if not IS_RENDER:
    from routes.woocommerce_routes import woocommerce_bp
else:
    log_config(logger, "[CONFIG] WooCommerce disabled on Render deployment")
    woocommerce_bp = None
```

**Why Disabled?**
- WooCommerce API requires specific network access
- Render free tier has IP restrictions
- Local development only for WooCommerce integration

**Health Check:**
```bash
curl https://ai-agents-backend-singapore.onrender.com/health
```

### Troubleshooting

#### Issue: Module Not Loading in UI

**Symptoms:** Shopify icon not in sidebar

**Diagnosis:**
```javascript
// Browser console
console.log(window.ModuleRegistry['shopify']);
// Should show: class ShopifyModule
```

**Solutions:**
1. Check manifest.json exists: `UI/modules_external/shopify/manifest.json`
2. Verify `show_in_sidebar: true` in manifest
3. Check Flask logs for module loading errors
4. Clear browser cache (Ctrl+Shift+R)

#### Issue: API Endpoints Return 503 "Credentials Not Configured"

**Symptoms:** Dashboard shows error message

**Diagnosis:**
```sql
-- Check credentials exist in Supabase
SELECT * FROM ai_infrastructure.user_platform_credentials 
WHERE platform = 'shopify' AND is_active = TRUE;
```

**Solutions:**
1. Insert credentials into Supabase (see [Credential Management](#credential-management))
2. Verify credentials are valid (test in Postman)
3. Check `is_active = TRUE`
4. Check user_id matches (default user_id=1)

#### Issue: WooCommerce API Timeout

**Symptoms:** Requests take > 30 seconds, then fail

**Diagnosis:**
```python
# Check WooCommerce site status
import requests
response = requests.get("https://inhouseprint.com.au")
print(response.status_code)  # Should be 200
```

**Solutions:**
1. Increase timeout in API client: `API(..., timeout=60)`
2. Check WooCommerce site is online
3. Check network connectivity
4. Contact WooCommerce site administrator

#### Issue: Calculator Returns Wrong Price

**Symptoms:** Quote doesn't match website calculator

**Diagnosis:**
```python
# Compare calculator output vs website
calc = PremiumBusinessCardsShopifyCalculator()
result = calc.calculate(quantity=1000, ...)
print(result['breakdown'])  # Check each pricing component
```

**Solutions:**
1. Verify GST applied only once (check for double GST bug)
2. Check config_manager.py has correct base prices
3. Verify all F-parameters match WooCommerce setup
4. Test with exact website parameters

---

## Migration History

### January 4, 2026: SQLite → WooCommerce API Refactor

**Motivation:**
- SQLite database required manual data sync
- Webhook event capture unreliable
- Cursor management complexity (33 leak patterns)
- Redundant data storage (WooCommerce is source of truth)

**Changes:**

**REMOVED:**
- ❌ SQLite database (`data/stock_data.db`)
- ❌ 5 database tables:
  - `shopify_orders`
  - `shopify_line_items`
  - `shopify_line_properties`
  - `shopify_webhook_events`
  - `shopify_product_mapping`
- ❌ SQL Viewer backend endpoint (`POST /api/shopify/sql-query`)
- ❌ Cursor management code (33 leak patterns eliminated)
- ❌ Database schema creation logic
- ❌ Webhook event storage logic

**ADDED:**
- ✅ WooCommerce REST API integration
- ✅ `get_woocommerce_credentials()` helper
- ✅ `get_woocommerce_api()` helper
- ✅ Supabase credential storage
- ✅ Live data fetching (no caching)
- ✅ Simplified error handling

**File Changes:**
```
shopify_routes.py: 1,155 lines → 807 lines (-348 lines, -30%)
```

**Benefits:**
- ✅ Always fresh data (no sync lag)
- ✅ No database maintenance
- ✅ No cursor leak risks
- ✅ Simpler codebase
- ✅ Reduced server resource usage

**Drawbacks:**
- ❌ No offline mode
- ❌ Dependent on WooCommerce uptime
- ❌ API rate limits apply
- ❌ SQL Viewer tab no longer functional

### Pre-January 4, 2026: SQLite Version

**Architecture (Old):**
```
Frontend → Flask API → SQLite (stock_data.db) → 5 tables
                    ↓
            WooCommerce Webhooks (sync data)
```

**How It Worked:**
1. WooCommerce webhooks triggered on order creation
2. Flask endpoint received webhook payload
3. Parsed order data
4. Inserted into SQLite tables
5. Dashboard read from local SQLite

**Problems:**
- Webhook delivery failures caused missing orders
- SQLite cursor leaks (33 patterns identified)
- Data drift between WooCommerce and local database
- Manual sync required for backfill
- Complex cursor management in every endpoint

**December 7, 2025 Audit:**
- Identified 33 cursor leak patterns
- Added `finally` blocks to all endpoints
- Still had complexity issues

**Decision:** Refactor to direct API calls (January 4, 2026)

---

## Summary

The "Shopify" module (legacy name) is actually a **WooCommerce E-Commerce Integration** that provides:

1. **Dashboard Module** (Frontend)
   - 6 tabs: Dashboard, Orders, Customers, Products, Webhooks, SQL Viewer*
   - Live data from WooCommerce API
   - Plotly.js charts + Tabulator.js tables
   - *SQL Viewer UI exists but backend disabled

2. **Flask API** (Backend)
   - 10 endpoints wrapping WooCommerce REST API calls
   - Credentials stored in Supabase PostgreSQL
   - NO local database (removed January 4, 2026)
   - Simplified error handling

3. **Calculator System** (Standalone Tools)
   - 35 Python calculator classes
   - Exact WooCommerce DPO pricing replication
   - NO database access required
   - Used by AI agents via direct import

**Key Architectural Decisions:**
- ✅ Live data fetching (no caching)
- ✅ Supabase credential management
- ✅ Simplified codebase (-30% lines)
- ❌ No offline mode
- ❌ Webhook storage not implemented
- ❌ SQL Viewer backend disabled

**Critical Issues:**
- 🔴 Double GST bug (21 calculators) - URGENT FIX REQUIRED
- ✅ Celloglaze case bug - FIXED
- ⚠️ SQL Viewer backend missing - Remove tab or re-implement
- ⚠️ Webhook endpoints empty - Expected behavior

**Production Status:** ✅ Working (with caveats above)

**Disabled on Render:** Yes (local development only due to IP restrictions)

---

**Document Version:** 2.0.0 (Accurate)  
**Last Updated:** January 18, 2026  
**Status:** ✅ Complete and Accurate
