# Quote Calculator Integration Architecture

## 🏗️ Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI_AGENTS PLATFORM                                  │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        USER INTERFACE                                │   │
│  │  (Flask API + HTML/JS Frontend)                                      │   │
│  └────────────────────────────┬─────────────────────────────────────────┘   │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    AI AGENT ROUTES                                   │   │
│  │  (agent_routes.py - Tool Execution Orchestrator)                     │   │
│  └────────────────────────────┬─────────────────────────────────────────┘   │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   TOOL REGISTRY                                      │   │
│  │  (tools/registry.py - 576 Tools Loaded)                             │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ CALCULATOR TOOLS (NEW!)                                      │   │   │
│  │  │ • calculate_business_cards                                   │   │   │
│  │  │ • calculate_flyers                                           │   │   │
│  │  │ • calculate_perfect_bound_books                              │   │   │
│  │  │ • get_stock_list                                             │   │   │
│  │  │ • get_calculator_requirements                                │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────┬─────────────────────────────────────────┘   │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              CALCULATOR WRAPPER                                      │   │
│  │  (tools/implementations/calculator.py)                               │   │
│  │                                                                       │   │
│  │  class CalculatorWrapper:                                            │   │
│  │      def calculate_business_cards()                                  │   │
│  │      def calculate_flyers()                                          │   │
│  │      def get_stock_list()                                            │   │
│  └────────────────────────────┬─────────────────────────────────────────┘   │
│                                │                                              │
│                                ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                EXTERNAL CALCULATOR MODULE                            │   │
│  │  (UI/external/modules/calculator-module/ORIGINAL/)                   │   │
│  │                                                                       │   │
│  │  ┌──────────────────────┐  ┌───────────────────────┐                │   │
│  │  │ SHOPIFY CALCULATORS  │  │  GOD CALCULATORS      │                │   │
│  │  │ (No DB Required)     │  │  (DB Required)        │                │   │
│  │  │                      │  │                       │                │   │
│  │  │ • Business Cards     │  │ • Flyers              │                │   │
│  │  │ • Corflute Signs     │  │ • Perfect Bound       │                │   │
│  │  │ • Premium Cards      │  │ • Booklets            │                │   │
│  │  │ • Economy Cards      │  │ • Letterheads         │                │   │
│  │  │                      │  │                       │                │   │
│  │  │ Source:              │  │ Source:               │                │   │
│  │  │ shopify_calculators/ │  │ complete_calculator_  │                │   │
│  │  │ *.py files           │  │ implementation.py     │                │   │
│  │  │                      │  │                       │                │   │
│  │  │ Pricing: JSON files  │  │ Pricing: SQL Server   │                │   │
│  │  │ (shopify/*.json)     │  │ (Quote_* tables)      │                │   │
│  │  └──────────────────────┘  └───────────────────────┘                │   │
│  │                                                                       │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │           QUERY LIBRARY (Optional)                            │  │   │
│  │  │  (query_library.py - 50+ Pre-built SQL Queries)              │  │   │
│  │  │                                                                │  │   │
│  │  │  • Historical quote analysis                                  │  │   │
│  │  │  • Customer analytics                                         │  │   │
│  │  │  • Production data queries                                    │  │   │
│  │  │  • Sales & revenue reports                                    │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  │                                                                       │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │           TOOL USE AGENT (Reference)                          │  │   │
│  │  │  (tool_use_agent.py - System Prompt & Tool Definitions)      │  │   │
│  │  │                                                                │  │   │
│  │  │  Contains:                                                     │  │   │
│  │  │  • Calculator tool definitions                                │  │   │
│  │  │  • Business rules documentation                               │  │   │
│  │  │  • System prompt for AI agent                                 │  │   │
│  │  │  • Tool execution logic (reference only)                      │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: Quote Request

```
┌──────────────┐
│    USER      │ "Quote 1000 business cards, 350gsm Satin"
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Flask API Endpoint                     │
│  POST /api/agent/chat                   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Agent Routes                           │
│  • Parse user message                   │
│  • Route to Claude AI                   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Claude AI (via Anthropic API)         │
│  • Analyzes request                     │
│  • Selects tool: calculate_business_cards│
│  • Extracts parameters                  │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Tool Registry                          │
│  • Finds: calculate_business_cards      │
│  • Loads: CalculatorWrapper             │
│  • Injects credentials (if needed)      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  CalculatorWrapper                      │
│  • Maps parameters                      │
│  • Calls: shopify_calculators.          │
│    business_card_calculator_shopify     │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  ShopifyBusinessCardCalculator          │
│  • Loads JSON pricing config            │
│  • Applies tier-based pricing           │
│  • Calculates costs                     │
│  • Returns ShopifyBusinessCardResult    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  CalculatorWrapper                      │
│  • Formats result for AI_agents         │
│  • Returns JSON:                        │
│    {                                    │
│      "success": true,                   │
│      "total_inc_gst": 234.50,           │
│      "price_per_unit": 0.23,            │
│      "breakdown": {...}                 │
│    }                                    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Claude AI                              │
│  • Receives tool result                 │
│  • Formats natural language response    │
│  • Returns to user                      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌──────────────┐
│    USER      │ "Your quote: $234.50 for 1,000 business cards..."
└──────────────┘
```

---

## 📂 File Structure Map

```
AI_agents/
│
├── tools/
│   ├── registry.py                    # Tool registry (UPDATE THIS)
│   │
│   ├── schemas/
│   │   └── calculator_tools.json      # Tool definitions (CREATE THIS)
│   │
│   └── implementations/
│       └── calculator.py              # Wrapper (CREATE THIS)
│
├── UI/external/modules/calculator-module/
│   ├── INTEGRATION_GUIDE.md           # ✅ Quick start guide
│   │
│   └── ORIGINAL/                      # ✅ Source files from In_House_SQL
│       ├── README_INTEGRATION.md      # ✅ Complete documentation
│       ├── ARCHITECTURE_DIAGRAM.md    # ✅ This file
│       │
│       ├── complete_calculator_implementation.py  # ✅ Main calculator
│       ├── tool_use_agent.py                      # ✅ Reference agent
│       ├── query_library.py                       # ✅ SQL queries
│       ├── db_connector.py                        # ✅ Database connector
│       │
│       ├── shopify_calculators/                   # ✅ Website calculators
│       │   ├── business_card_calculator_shopify.py
│       │   ├── corflute_calculator_shopify.py
│       │   ├── [7 more calculators]
│       │   └── __init__.py
│       │
│       ├── shopify/                               # ✅ JSON configs
│       │   ├── Business_Cards_Economic.json
│       │   ├── Premium_Business_Cards.json
│       │   ├── Corflute_Signs_Shopify.json
│       │   └── [6 more configs]
│       │
│       └── [10 documentation files]               # ✅ Reference docs
│
└── AI_infrastructure/
    └── routes/
        └── agent_routes.py            # Calls tool registry
```

---

## 🎯 Integration Points

### 1. Tool Schema Definition
**File:** `tools/schemas/calculator_tools.json`
- Defines tool parameters
- Specifies data types
- Documents usage

### 2. Tool Implementation
**File:** `tools/implementations/calculator.py`
- CalculatorWrapper class
- Maps AI_agents calls → Calculator calls
- Handles credential injection
- Formats results

### 3. Tool Registry
**File:** `tools/registry.py`
- Loads calculator_tools.json
- Registers tools with CalculatorWrapper
- Makes tools available to AI agent

### 4. Calculator Module
**Folder:** `UI/external/modules/calculator-module/ORIGINAL/`
- Source calculator code
- Unchanged from In_House_SQL
- Can be updated independently

---

## 🔧 Technology Stack

### AI_agents Platform:
- **Backend:** Flask (Python 3.13)
- **Database:** SQLite (ai_infrastructure.db)
- **AI Provider:** Anthropic Claude (multi-provider support)
- **Tool System:** Centralized registry (576 tools)
- **Frontend:** HTML/JS + Server-Sent Events

### Quote Calculator:
- **Language:** Python 3.13
- **Database:** SQL Server (production) or SQLite (migration)
- **Calculators:** 
  - Shopify (hardcoded, no DB)
  - GOD (database-driven)
- **Dependencies:** pandas, pyodbc (optional), decimal, dataclasses

---

## 🚀 Deployment Strategies

### Strategy 1: Shopify Only (Recommended First)
```
✅ Business Cards (Shopify calculator)
✅ No database required
✅ 95% accurate website pricing
✅ Easy to deploy and test
❌ Limited to business cards
```

### Strategy 2: Hybrid (Recommended Production)
```
✅ Business Cards (Shopify - no DB)
✅ Flyers, Books, Booklets (GOD - SQLite export)
✅ Best accuracy
✅ Full product range
⚠️ Requires database migration
```

### Strategy 3: Full Integration (Future)
```
✅ All calculators
✅ Query library (historical data)
✅ Real-time SQL Server connection
✅ Production pricing
⚠️ Requires SQL Server access
⚠️ More complex deployment
```

---

## 📊 Calculator Comparison

| Feature | Shopify Calculators | GOD Calculators |
|---------|---------------------|-----------------|
| **Database Required** | ❌ No | ✅ Yes (SQL Server or SQLite) |
| **Accuracy** | 95% (website pricing) | 99% (production pricing) |
| **Products** | Business Cards, Corflute | Flyers, Books, Booklets, Letterheads |
| **Pricing Source** | JSON files (hardcoded) | Database tables (dynamic) |
| **Deployment** | Easy | Moderate |
| **Updates** | Manual (edit JSON) | Automatic (database sync) |
| **Use Case** | Quick quotes, website | Production planning, costing |

---

## 🧪 Testing Flow

```
1. Unit Test (Direct Calculator)
   └─ python test_calculator_integration.py
      └─ Calls CalculatorWrapper directly
         └─ Tests business card calculation

2. Registry Test (Tool System)
   └─ python -c "from tools.registry import ToolRegistry; ..."
      └─ Verifies tool is loaded
         └─ Shows 577 tools (576 + 1 calculator)

3. API Test (Flask Endpoint)
   └─ POST /api/agent/execute-tool
      └─ Body: {"tool_name": "calculate_business_cards", ...}
         └─ Tests through Flask API

4. Integration Test (Full Flow)
   └─ POST /api/agent/chat
      └─ Body: {"message": "Quote 1000 business cards"}
         └─ AI agent selects and executes tool
            └─ Returns formatted quote to user
```

---

## 📈 Scalability

### Current Scope:
- 5 calculators (1 ready, 4 pending database)
- Business cards: Ready to deploy
- No additional infrastructure needed

### Future Expansion:
- Add query library for historical analysis
- Connect to SQL Server for real-time pricing
- Add more Shopify calculators (easy - just JSON)
- Implement batch quoting
- Add PDF quote generation

---

## ⚡ Performance Expectations

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Tool registration | < 1 second | On Flask startup |
| Calculate business card | < 100ms | No database calls |
| Calculate flyer (future) | < 500ms | With database query |
| AI agent full cycle | 2-5 seconds | Including Claude API |

---

## 🎯 Success Metrics

### Phase 1 (Business Cards - Week 1):
- ✅ Calculator tools registered
- ✅ Business card quotes working
- ✅ < 5% error rate vs website
- ✅ AI agent can quote automatically

### Phase 2 (Database Integration - Week 2-3):
- ✅ SQLite export from SQL Server
- ✅ Flyer calculator working
- ✅ Query library adapted

### Phase 3 (Full Integration - Week 4+):
- ✅ All 5 calculators operational
- ✅ Historical quote analysis
- ✅ Production-ready deployment

---

**Architecture Status:** ✅ **COMPLETE** - Ready for implementation

**Next Step:** Create `tools/schemas/calculator_tools.json`

---

**Last Updated:** October 30, 2025
