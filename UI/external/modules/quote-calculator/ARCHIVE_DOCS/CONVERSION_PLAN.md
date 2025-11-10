# Quote Calculator → Module Conversion Plan

**Date:** October 30, 2025  
**Goal:** Convert InHouse Print Quote Calculator into AI_agents module  
**Architecture:** Module Architecture V2 with AI Integration

---

## 🎯 Executive Summary

Convert the Quote Calculator from standalone files into a **fully integrated AI_agents module** with:
- **Pastel color scheme** (Orange `#ffb347` for printing/manufacturing)
- **5 sub-tabs** (Business Cards, Flyers, Perfect Bound Books, Booklets, Advanced)
- **22 AI tools** (7 calculator tools + 15 query library tools)
- **Dashboard export** for AI consumption
- **Smart bundled tools** for batch operations

---

## 📋 Module Structure

```
UI/external/modules/quote-calculator/
├── manifest.json                       # Module config + colors
├── quote-calculator.js                 # Main module class
├── quote-calculator.css                # Custom styles
│
├── tools/                              # AI-callable tools
│   ├── manifest.json                   # Tool registry
│   ├── calculator-tools.json           # 7 calculator tools
│   ├── query-library-tools.json        # 15 query tools
│   └── smart-tools.json                # 5 smart bundled tools
│
└── lib/                                # Calculator libraries
    ├── complete_calculator_implementation.py  # Python backend
    ├── shopify_calculators/            # Shopify calculators
    └── db_connector.py                 # Database connector
```

**Note:** Python files stay in `calculator-module/ORIGINAL/` - Module communicates via Flask API

---

## 🎨 Module Design

### Color Scheme (Pastel Orange - Printing Industry)
```json
{
  "colors": {
    "primary": "#ffb347",      // Pastel orange (printing/manufacturing)
    "secondary": "#ffd699",    // Lighter gradient
    "hover": "#ffaa33"         // Darker on hover
  }
}
```

### Icon & Branding
- **Icon:** `fas fa-calculator` (main) / `fas fa-print` (alternate)
- **Name:** "Quote Calculator"
- **Description:** "InHouse Print quote generation and pricing tools"

---

## 📊 Sub-Tabs Design

### Tab 1: Business Cards (Default)
**ID:** `business-cards`  
**Icon:** `fas fa-id-card`  
**Status:** ✅ Ready (Shopify calculator, no DB needed)

**Features:**
- Quantity selector (1,000 - 10,000)
- Stock dropdown (350gsm Satin, 400gsm Uncoated, 350gsm Gloss)
- Finish options (None, Gloss Cello, Matt Cello)
- Print sides (Single, Double)
- Real-time quote calculation
- Cost breakdown display

**UI Components:**
- Quote form (left side)
- Live preview card (right side)
- Cost breakdown table
- Comparison to historical quotes

### Tab 2: Flyers
**ID:** `flyers`  
**Icon:** `fas fa-file-alt`  
**Status:** ⏳ Requires database export

**Features:**
- Size selector (A4, A5, A6, DL)
- Quantity input
- Stock selector (from database)
- Print mode (Color, B&W, Mixed)
- Quote calculation
- Turnaround time display

### Tab 3: Perfect Bound Books
**ID:** `perfect-bound-books`  
**Icon:** `fas fa-book`  
**Status:** ⏳ Requires database export

**Features:**
- Page count selector
- Cover stock selector
- Interior stock selector
- Quantity input
- Quote calculation
- Binding options

### Tab 4: Booklets
**ID:** `booklets`  
**Icon:** `fas fa-book-open`  
**Status:** ⏳ Requires database export

**Features:**
- Page count (4-48, divisible by 4)
- Stock selector
- Quantity input
- Saddle-stitch quote
- Turnaround time

### Tab 5: Advanced (Query Library)
**ID:** `advanced`  
**Icon:** `fas fa-chart-line`  
**Status:** ✅ Ready

**Features:**
- Historical quote analysis
- Customer analytics
- Production planning queries
- Revenue reports
- Stock usage analysis
- Pre-built query selector (50+ queries)

---

## 🔧 Tool Definitions

### Calculator Tools (7 tools)

#### 1. `quote_calc_business_cards`
```json
{
  "name": "quote_calc_business_cards",
  "description": "Calculate quote for business cards (1000-10000 cards)",
  "parameters": {
    "quantity": {"type": "integer", "required": true},
    "stock_type": {"type": "string", "enum": ["350gsm_satin", "400gsm_uncoated", "350gsm_gloss"]},
    "finish": {"type": "string", "enum": ["none", "gloss_cello", "matt_cello"]},
    "print_sides": {"type": "string", "enum": ["single", "double"]}
  },
  "returns": {
    "total_inc_gst": "number",
    "price_per_unit": "number",
    "breakdown": "object",
    "turnaround": "string"
  }
}
```

#### 2. `quote_calc_flyers`
```json
{
  "name": "quote_calc_flyers",
  "description": "Calculate quote for digital printing flyers",
  "parameters": {
    "quantity": {"type": "integer", "required": true},
    "size": {"type": "string", "enum": ["A4", "A5", "A6", "DL"]},
    "stock_id": {"type": "integer", "required": true}
  }
}
```

#### 3. `quote_calc_perfect_bound_books`
#### 4. `quote_calc_booklets`
#### 5. `quote_calc_letterheads`
#### 6. `quote_get_stock_list`
#### 7. `quote_get_calculator_requirements`

### Query Library Tools (15 tools)

#### Category: Sales & Revenue
1. `quote_query_sales_trend` - Monthly sales trends
2. `quote_query_revenue_by_product` - Revenue breakdown by product
3. `quote_query_top_revenue_products` - Highest revenue products

#### Category: Customer Analytics
4. `quote_query_top_customers` - Best customers by revenue
5. `quote_query_customer_lifetime_value` - CLV analysis
6. `quote_query_new_vs_repeat` - Customer acquisition vs retention

#### Category: Quote Analysis
7. `quote_query_quote_history` - Historical quote data
8. `quote_query_average_quote_value` - Average quote by product
9. `quote_query_conversion_rate` - Quote to order conversion

#### Category: Production Planning
10. `quote_query_production_schedule` - Upcoming jobs
11. `quote_query_capacity_utilization` - Machine usage
12. `quote_query_turnaround_analysis` - Delivery performance

#### Category: Stock Analytics
13. `quote_query_stock_usage` - Stock consumption patterns
14. `quote_query_low_stock_alerts` - Inventory warnings
15. `quote_query_stock_cost_trends` - Price changes over time

### Smart Tools (5 bundled tools)

#### 1. `quote_smart_bulk_price_quotes`
**Description:** Generate quotes for multiple products in ONE call  
**Efficiency:** 90% reduction (10 quotes → 1 call)  
**Parameters:**
```json
{
  "quote_requests": [
    {"product": "business_cards", "quantity": 1000, "stock": "350gsm_satin"},
    {"product": "flyers", "quantity": 5000, "size": "A4", "stock_id": 16}
  ]
}
```

#### 2. `quote_smart_price_comparison_report`
**Description:** Compare quotes across time periods with trends  
**Efficiency:** Analyzes 1000+ quotes in seconds

#### 3. `quote_smart_customer_quote_history`
**Description:** Generate comprehensive customer quote history with analytics  
**Efficiency:** 50+ database queries → 1 smart call

#### 4. `quote_smart_profitability_analysis`
**Description:** Analyze profitability by product, customer, time period  
**Efficiency:** Complete business intelligence in 1 call

#### 5. `quote_export_dashboard_data`
**Description:** Export current dashboard view as JSON for AI consumption  
**Parameters:**
```json
{
  "subtab": {"enum": ["business-cards", "flyers", "perfect-bound-books", "booklets", "advanced", "all"]}
}
```

---

## 🏗️ Module Class Structure

### Main Class (`quote-calculator.js`)

```javascript
class QuoteCalculatorModule extends BaseModule {
    constructor(config) {
        super(config);
        
        // Module data
        this.quotes = [];
        this.stockList = [];
        this.queryResults = {};
        
        // Tool system
        this.tools = null;
        this.toolImplementations = {};
        
        // API endpoint (Flask backend)
        this.apiBaseUrl = '/api/quote-calculator';
    }
    
    async initialize() {
        console.log('🔧 Initializing Quote Calculator module...');
        
        // Load and register tools
        await this.loadTools();
        this.registerToolsWithAI();
        
        // Apply module colors
        this.applyModuleColors();
        
        // Create UI structure
        await super.initialize();
        
        // Load stock list (cached)
        await this.loadStockList();
        
        console.log('Quote Calculator ready - 22 tools loaded');
    }
    
    // ==================== TOOL SYSTEM ====================
    
    async loadTools() { /* Load from tools/*.json */ }
    bindToolImplementations() { /* Map tool names to methods */ }
    registerToolsWithAI() { /* Register with global AI */ }
    async executeTool(toolName, params) { /* Execute tool */ }
    
    // ==================== CALCULATOR TOOLS ====================
    
    async calculateBusinessCards(params) {
        // Call Flask API: POST /api/quote-calculator/business-cards
        const response = await fetch(`${this.apiBaseUrl}/business-cards`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params)
        });
        return await response.json();
    }
    
    async calculateFlyers(params) { /* Similar to above */ }
    async calculatePerfectBoundBooks(params) { /* Similar */ }
    async calculateBooklets(params) { /* Similar */ }
    async getStockList(params) { /* Cached stock list */ }
    
    // ==================== QUERY LIBRARY TOOLS ====================
    
    async querySalesTrend(params) {
        // Call Flask API: POST /api/quote-calculator/query/sales-trend
        const response = await fetch(`${this.apiBaseUrl}/query/sales-trend`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params)
        });
        return await response.json();
    }
    
    // ... 14 more query methods
    
    // ==================== SMART TOOLS ====================
    
    async smartBulkPriceQuotes(params) {
        // Call multiple calculator endpoints in parallel
        const results = await Promise.all(
            params.quote_requests.map(req => this.calculateQuote(req))
        );
        return {
            total_quotes: results.length,
            quotes: results,
            total_cost: results.reduce((sum, q) => sum + q.total_inc_gst, 0)
        };
    }
    
    async smartPriceComparisonReport(params) { /* Analytics */ }
    async smartCustomerQuoteHistory(params) { /* Customer analysis */ }
    async smartProfitabilityAnalysis(params) { /* Business intelligence */ }
    
    async exportDashboardData(params) {
        // Package current view
        const subtab = params.subtab || this.activeSubTab;
        const dashboardData = {
            module: 'quote-calculator',
            timestamp: new Date().toISOString(),
            subtab: subtab,
            data: {}
        };
        
        switch (subtab) {
            case 'business-cards':
                dashboardData.data.recent_quotes = this.quotes.slice(0, 10);
                break;
            case 'advanced':
                dashboardData.data.query_results = this.queryResults;
                break;
        }
        
        return dashboardData;
    }
    
    // ==================== UI INITIALIZATION ====================
    
    initializeSubTabs() {
        this.initializeBusinessCards();
        this.initializeFlyers();
        this.initializePerfectBoundBooks();
        this.initializeBooklets();
        this.initializeAdvanced();
    }
    
    initializeBusinessCards() {
        const container = document.getElementById('subtab-business-cards');
        const primaryColor = this.config.colors.primary;
        
        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-id-card" style="color: ${primaryColor};"></i>
                        Business Card Quote Calculator
                    </h2>
                    <p class="module-description">Calculate accurate quotes for business card printing</p>
                </div>
            </div>
            
            <div class="quote-calculator-grid">
                <!-- Left: Quote Form -->
                <div class="dashboard-card">
                    <div class="dashboard-card-header">
                        <i class="fas fa-edit dashboard-card-icon" style="color: ${primaryColor};"></i>
                        <span class="dashboard-card-title">Quote Details</span>
                    </div>
                    <div class="dashboard-card-content">
                        ${this.renderBusinessCardForm()}
                    </div>
                </div>
                
                <!-- Right: Live Quote Preview -->
                <div class="dashboard-card">
                    <div class="dashboard-card-header">
                        <i class="fas fa-file-invoice-dollar dashboard-card-icon" style="color: ${primaryColor};"></i>
                        <span class="dashboard-card-title">Quote Preview</span>
                    </div>
                    <div class="dashboard-card-content" id="business-card-quote-result">
                        <p class="text-secondary">Configure options and click "Calculate Quote"</p>
                    </div>
                </div>
            </div>
        `;
        
        // Attach event listeners
        this.attachBusinessCardFormListeners();
    }
    
    renderBusinessCardForm() {
        return `
            <form id="business-card-form" onsubmit="return false;">
                <!-- Quantity -->
                <div class="form-group">
                    <label>Quantity</label>
                    <select id="bc-quantity" class="form-control">
                        <option value="1000">1,000 cards</option>
                        <option value="2000">2,000 cards</option>
                        <option value="3000">3,000 cards</option>
                        <option value="5000">5,000 cards</option>
                        <option value="10000">10,000 cards</option>
                    </select>
                </div>
                
                <!-- Stock Type -->
                <div class="form-group">
                    <label>Paper Stock</label>
                    <select id="bc-stock" class="form-control">
                        <option value="350gsm_satin">350gsm Satin (Most Popular)</option>
                        <option value="400gsm_uncoated">400gsm Uncoated</option>
                        <option value="350gsm_gloss">350gsm Gloss</option>
                    </select>
                </div>
                
                <!-- Finish -->
                <div class="form-group">
                    <label>Finish</label>
                    <select id="bc-finish" class="form-control">
                        <option value="none">No Cellophane</option>
                        <option value="gloss_cello">Gloss Cellophane</option>
                        <option value="matt_cello">Matt Cellophane</option>
                    </select>
                </div>
                
                <!-- Print Sides -->
                <div class="form-group">
                    <label>Printing</label>
                    <select id="bc-print-sides" class="form-control">
                        <option value="double">Double Sided</option>
                        <option value="single">Single Sided</option>
                    </select>
                </div>
                
                <!-- Calculate Button -->
                <button type="button" class="btn-primary" style="background: ${this.config.colors.primary}; border-color: ${this.config.colors.primary}; width: 100%;" onclick="window.ModuleRegistry['quote-calculator'].calculateBusinessCardQuote()">
                    <i class="fas fa-calculator"></i> Calculate Quote
                </button>
            </form>
        `;
    }
    
    async calculateBusinessCardQuote() {
        const quantity = parseInt(document.getElementById('bc-quantity').value);
        const stock_type = document.getElementById('bc-stock').value;
        const finish = document.getElementById('bc-finish').value;
        const print_sides = document.getElementById('bc-print-sides').value;
        
        const resultContainer = document.getElementById('business-card-quote-result');
        resultContainer.innerHTML = '<div class="loading-spinner">Calculating...</div>';
        
        try {
            const result = await this.executeTool('quote_calc_business_cards', {
                quantity,
                stock_type,
                finish,
                print_sides
            });
            
            this.renderBusinessCardQuote(result);
        } catch (error) {
            resultContainer.innerHTML = `<div class="error-message"> ${error.message}</div>`;
        }
    }
    
    renderBusinessCardQuote(result) {
        const resultContainer = document.getElementById('business-card-quote-result');
        const primaryColor = this.config.colors.primary;
        
        resultContainer.innerHTML = `
            <div class="quote-result">
                <div class="quote-total" style="border-left-color: ${primaryColor};">
                    <div class="quote-label">Total (inc GST)</div>
                    <div class="quote-value">$${result.total_inc_gst.toFixed(2)}</div>
                </div>
                
                <div class="quote-per-unit">
                    <div class="quote-label">Per Card</div>
                    <div class="quote-value">$${result.price_per_unit.toFixed(3)}</div>
                </div>
                
                <div class="quote-turnaround">
                    <i class="fas fa-clock" style="color: ${primaryColor};"></i>
                    ${result.turnaround}
                </div>
                
                <hr>
                
                <div class="quote-breakdown">
                    <h4>Cost Breakdown</h4>
                    <table class="breakdown-table">
                        <tr>
                            <td>Paper Cost</td>
                            <td>$${result.breakdown.paper_cost.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <td>Print Cost</td>
                            <td>$${result.breakdown.print_cost.toFixed(2)}</td>
                        </tr>
                        ${result.breakdown.cello_cost > 0 ? `
                        <tr>
                            <td>Cellophane</td>
                            <td>$${result.breakdown.cello_cost.toFixed(2)}</td>
                        </tr>
                        ` : ''}
                        <tr>
                            <td>Cutting Cost</td>
                            <td>$${result.breakdown.cutting_cost.toFixed(2)}</td>
                        </tr>
                        <tr class="breakdown-subtotal">
                            <td>Subtotal</td>
                            <td>$${result.breakdown.subtotal.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <td>GST (10%)</td>
                            <td>$${result.breakdown.gst.toFixed(2)}</td>
                        </tr>
                        <tr class="breakdown-total">
                            <td><strong>Total</strong></td>
                            <td><strong>$${result.total_inc_gst.toFixed(2)}</strong></td>
                        </tr>
                    </table>
                </div>
            </div>
        `;
    }
}

// Register module
window.ModuleRegistry['quote-calculator'] = QuoteCalculatorModule;
```

---

## 🔌 Flask Backend Integration

### New Flask Routes Needed

**File:** `AI_infrastructure/routes/quote_calculator_routes.py`

```python
from flask import Blueprint, request, jsonify
import sys
import os

# Add calculator module to path
calculator_path = os.path.join(
    os.path.dirname(__file__), 
    '..', '..', 'UI', 'external', 'modules', 'calculator-module', 'ORIGINAL'
)
sys.path.insert(0, calculator_path)

from shopify_calculators.business_card_calculator_shopify import (
    ShopifyBusinessCardCalculator,
    PrintType,
    StockTypeStandard,
    CelloglazePremium
)

quote_calc_bp = Blueprint('quote_calculator', __name__, url_prefix='/api/quote-calculator')

@quote_calc_bp.route('/business-cards', methods=['POST'])
def calculate_business_cards():
    """Calculate business card quote"""
    data = request.json
    
    # Map parameters
    quantity = data.get('quantity', 1000)
    stock_type = data.get('stock_type', '350gsm_satin')
    finish = data.get('finish', 'none')
    print_sides = data.get('print_sides', 'double')
    
    # Map to calculator enums
    stock_map = {
        '350gsm_satin': StockTypeStandard.SATIN_350GSM,
        '400gsm_uncoated': StockTypeStandard.UNCOATED_400GSM,
        '350gsm_gloss': StockTypeStandard.GLOSS_350GSM
    }
    
    finish_map = {
        'none': None,
        'gloss_cello': CelloglazePremium.GLOSS,
        'matt_cello': CelloglazePremium.MATT
    }
    
    print_map = {
        'double': PrintType.DOUBLE_SIDED,
        'single': PrintType.SINGLE_SIDED
    }
    
    # Calculate
    calculator = ShopifyBusinessCardCalculator()
    result = calculator.calculate(
        quantity=quantity,
        print_type=print_map[print_sides],
        stock_type=stock_map[stock_type],
        celloglaze=finish_map[finish]
    )
    
    # Format response
    return jsonify({
        'success': True,
        'total_inc_gst': float(result.total_inc_gst),
        'price_per_unit': float(result.price_per_unit),
        'turnaround': '3-5 business days',
        'breakdown': {
            'paper_cost': float(result.base_cost) if hasattr(result, 'base_cost') else 0,
            'print_cost': float(result.print_cost) if hasattr(result, 'print_cost') else 0,
            'cello_cost': float(result.celloglaze_cost) if hasattr(result, 'celloglaze_cost') else 0,
            'cutting_cost': 0,  # Included in base
            'subtotal': float(result.subtotal),
            'gst': float(result.gst)
        }
    })

@quote_calc_bp.route('/stock-list', methods=['GET'])
def get_stock_list():
    """Get available paper stocks"""
    # Hardcoded for now (Shopify calculator)
    stocks = [
        {
            'id': '350gsm_satin',
            'name': '350gsm Satin',
            'description': 'Premium satin finish, most popular',
            'recommended': True
        },
        {
            'id': '400gsm_uncoated',
            'name': '400gsm Uncoated',
            'description': 'Thick uncoated stock, writable'
        },
        {
            'id': '350gsm_gloss',
            'name': '350gsm Gloss',
            'description': 'High gloss finish'
        }
    ]
    
    return jsonify({
        'success': True,
        'stocks': stocks,
        'total': len(stocks)
    })
```

**Register in `flask_app.py`:**
```python
from routes.quote_calculator_routes import quote_calc_bp
app.register_blueprint(quote_calc_bp)
```

---

## 📅 Implementation Timeline

### Phase 1: Module Shell (Week 1 - Day 1-2)
- [ ] Create `quote-calculator/` folder
- [ ] Create `manifest.json` with colors and tabs
- [ ] Create `quote-calculator.js` class skeleton
- [ ] Create `quote-calculator.css` basic styles
- [ ] Register in main `manifest.json`
- [ ] Test: Module appears in sidebar

### Phase 2: Business Cards Tab (Week 1 - Day 3-4)
- [ ] Create business card UI (form + preview)
- [ ] Create Flask route `/api/quote-calculator/business-cards`
- [ ] Implement `calculateBusinessCards()` method
- [ ] Test: Can generate business card quote
- [ ] Style with pastel orange colors

### Phase 3: Tool System (Week 1 - Day 5)
- [ ] Create `tools/manifest.json`
- [ ] Create `tools/calculator-tools.json` (7 tools)
- [ ] Implement `loadTools()`, `bindToolImplementations()`, `registerToolsWithAI()`
- [ ] Test: Tools appear in `ModuleToolRegistry`
- [ ] Test: AI can call `quote_calc_business_cards`

### Phase 4: Query Library Tab (Week 2 - Day 1-2)
- [ ] Create Advanced tab UI
- [ ] Create `tools/query-library-tools.json` (15 tools)
- [ ] Implement query methods
- [ ] Test: Can run historical quote queries

### Phase 5: Smart Tools (Week 2 - Day 3)
- [ ] Create `tools/smart-tools.json` (5 tools)
- [ ] Implement `smartBulkPriceQuotes()`
- [ ] Implement `exportDashboardData()`
- [ ] Test: AI can bulk quote multiple products

### Phase 6: Remaining Calculators (Week 2 - Day 4-5)
- [ ] Flyers tab (requires DB export)
- [ ] Perfect Bound Books tab (requires DB export)
- [ ] Booklets tab (requires DB export)
- [ ] Database migration from SQL Server to SQLite

### Phase 7: Polish & Deploy (Week 3)
- [ ] Error handling
- [ ] Loading states
- [ ] Responsive design
- [ ] Documentation
- [ ] User testing
- [ ] Production deployment

---

## ✅ Success Criteria

### Module Functionality
- [x] Module appears in sidebar with orange icon
- [ ] All 5 sub-tabs accessible
- [ ] Business card calculator working (no DB)
- [ ] 22 tools loaded and registered
- [ ] AI can call tools via chat
- [ ] Dashboard export packages data for AI
- [ ] Colors consistent (pastel orange)

### AI Integration
- [ ] User: "Quote 1000 business cards" → AI calls tool → Returns price
- [ ] User: "Show quote history" → AI calls query tool → Returns data
- [ ] User: "Quote 5 different products" → AI calls smart tool → Bulk quotes
- [ ] User: "What's on the business cards tab?" → AI exports dashboard data

### Code Quality
- [ ] Clean module structure
- [ ] Consistent naming conventions
- [ ] Error handling
- [ ] Console logging for debugging
- [ ] Comments explain complex logic
- [ ] No hardcoded values

---

## 🚀 Quick Start Command

```bash
# 1. Create module folder
cd C:\Users\gpoli\GIT\AI_agents\UI\external\modules
mkdir quote-calculator
cd quote-calculator

# 2. Create tool structure
mkdir tools

# 3. Copy files from templates above:
# - manifest.json
# - quote-calculator.js
# - quote-calculator.css
# - tools/manifest.json
# - tools/calculator-tools.json

# 4. Register in main manifest
# Add entry to: UI/external/modules/manifest.json

# 5. Create Flask routes
# Add file: AI_infrastructure/routes/quote_calculator_routes.py

# 6. Test
# Open http://localhost:5001
# Click "Quote Calculator" in sidebar
# Should see module load
```

---

## 📚 Documentation References

- **Instructions.md** - Module development guide
- **MODULE_ARCHITECTURE_V2.md** - AI integration architecture
- **AI_prompt.md** - AI conversion guide
- **INTEGRATION_GUIDE.md** - Calculator integration steps
- **ARCHITECTURE_DIAGRAM.md** - System flow diagrams

---

**Status:** ✅ **PLAN COMPLETE** - Ready to implement

**Next Action:** Create `manifest.json` and start Phase 1

---

**Created:** October 30, 2025  
**Version:** 1.0.0
