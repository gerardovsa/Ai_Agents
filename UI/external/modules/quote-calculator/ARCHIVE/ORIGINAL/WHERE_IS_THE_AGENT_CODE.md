# WHERE IS THE AGENT CODE?

**Date:** October 4, 2025  
**You Asked:** "WHERE IS ALL THAT? Where are the tools, thinking, prompt?"

---

## 📂 ACTUAL AGENT FILES

### **Primary Agent Implementation:**

```
c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\
    AI_Quote_Agent\
        core\
            ├── calculator_first_autonomous_agent.py    ⭐ MAIN AGENT
            └── autonomous_quote_agent_with_sql.py      📊 SQL-ENHANCED VERSION
        production\
            └── comprehensive_ai_quote_agent.py         🚀 PRODUCTION VERSION
```

---

## ⭐ 1. MAIN AGENT (Calculator-First Architecture)

**File:** `AI_Quote_Agent/core/calculator_first_autonomous_agent.py`  
**Lines:** 1,448 lines  
**Status:** Active development version

### What's Inside:

#### System Prompt (Lines 145-760)
```python
def _build_system_prompt(self, calculator_interface, schema_info, product_types):
    return f"""
You are an AI quote assistant for InHousePrint...

AVAILABLE TOOLS:
- get_calculator_requirements(product_type)
- execute_sql(sql_query)
- calculate_quote(product_type, parameters)

CALCULATOR SELECTION RULES:
- business card → FLYERS
- 1-4 pages → FLYERS
- 4-60 pages → BOOKLETS
- 60+ pages → PERFECT_BOUND_BOOKS

WORKFLOW:
1. Identify product type
2. Call get_calculator_requirements()
3. Extract parameters from database
4. Call calculate_quote()
5. Generate response
"""
```

#### Tool Handling (Lines 900-1100)
```python
def _run_autonomous_conversation(self, conversation, system_prompt, max_turns):
    """
    Multi-turn conversation with tool use.
    AI can call tools multiple times autonomously.
    """
    
    response = self.anthropic_client.messages.create(
        model=self.model,
        max_tokens=4000,
        temperature=1.0,
        thinking={
            "type": "enabled",
            "budget_tokens": 3000
        },
        system=system_prompt,
        messages=conversation
    )
    
    # Extract thinking and response
    for block in response.content:
        if block.type == "thinking":
            thinking_content = block.thinking
        elif block.type == "text":
            response_content = block.text
```

#### Tool Execution (Lines 1150-1350)
```python
def _execute_tool_call(self, tool_name, tool_input):
    """Execute actual tool calls"""
    
    if tool_name == "get_calculator_requirements":
        return self.calculator.get_calculator_requirements(
            tool_input['product_type']
        )
    
    elif tool_name == "execute_sql":
        result = self.db.execute_query(tool_input['sql_query'])
        return result.to_dict('records')
    
    elif tool_name == "calculate_quote":
        product_type = tool_input['product_type']
        params = tool_input['parameters']
        
        if product_type == "flyers":
            return self.calculator.calculate_flyers(**params)
        elif product_type == "booklets":
            return self.calculator.calculate_booklets(**params)
        elif product_type == "perfect_bound_books":
            return self.calculator.calculate_perfect_bound_books(**params)
```

---

## 📊 2. SQL-ENHANCED VERSION

**File:** `AI_Quote_Agent/core/autonomous_quote_agent_with_sql.py`  
**Lines:** 2,098 lines  
**Status:** Extended version with DashboardSQLAgent integration

### Key Differences:

```python
class AutonomousQuoteAgentWithSQL:
    """
    Enhanced agent that integrates:
    - DashboardSQLAgent (for advanced SQL generation)
    - Historical quote verification
    - Multi-round parameter extraction
    """
    
    def __init__(self):
        self.sql_agent = DashboardSQLAgent(db_connection=self.db)
        # Can generate SQL autonomously using AI
```

### Extra Features:
- AI-generated SQL queries (not just executing provided SQL)
- Historical quote verification
- Price variance analysis
- Alternative quote generation

---

## 🚀 3. PRODUCTION VERSION

**File:** `AI_Quote_Agent/production/comprehensive_ai_quote_agent.py`  
**Lines:** 744 lines  
**Status:** Streamlined production version

### Differences from Core:
- Simplified workflow
- Focus on email processing
- Less verbose logging
- Production-ready error handling

```python
class ComprehensiveAIQuoteAgent:
    def process_customer_email(self, email_text, sender_email=None):
        """
        Main entry point for production use.
        Processes email → Generates quote → Returns response
        """
```

---

## 🛠️ SUPPORTING FILES

### Calculator Implementation:
```
c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\
    ├── complete_calculator_implementation.py    📝 CALCULATOR CORE (3,117 lines)
    └── config\
        └── database-config.json                🔑 API KEY & DB CONFIG
```

### Database Connector:
```
c:\Users\gpoli\GIT\In_House_SQL\G_Folder\tools\
    └── db_connector.py                        💾 DATABASE CONNECTION
```

---

## 🔍 HOW TO FIND SPECIFIC PARTS

### Where is the System Prompt?
```python
# File: calculator_first_autonomous_agent.py
# Lines: 145-760

def _build_system_prompt(self, ...):
    return f"""
You are an AI quote assistant...
[FULL PROMPT HERE]
"""
```

### Where are the Tools defined?
```python
# Tools are NOT explicitly defined in code!
# Instead, they're described in the system prompt as TEXT

system_prompt = f"""
AVAILABLE TOOLS:
- get_calculator_requirements(product_type)
- execute_sql(sql_query)  
- calculate_quote(product_type, parameters)
"""

# The AI agent uses TEXT PARSING to detect tool calls
# (Not using Anthropic's official Tool Use API yet)
```

### Where is Thinking enabled?
```python
# File: calculator_first_autonomous_agent.py  
# Lines: ~900

response = self.anthropic_client.messages.create(
    model=self.model,
    max_tokens=4000,
    thinking={
        "type": "enabled",        #  THINKING ENABLED
        "budget_tokens": 3000     # 3000 tokens for reasoning
    },
    system=system_prompt,
    messages=conversation
)
```

### Where does Calculator return intelligence?
```python
# File: complete_calculator_implementation.py
# Lines: 139-1370

def get_calculator_requirements(self, product_type: str) -> Dict[str, Any]:
    """
    Returns 70+ pieces of intelligence including:
    - HISTORICAL_DATA_INSIGHTS (10,055+ orders analyzed)
    - natural_language_hints (phrase mappings)
    - product_mapping_rules
    - required_parameters
    - optional_parameters
    - business_rules
    - validation_rules
    """
    
    if product_type == "flyers":
        return {
            "HISTORICAL_DATA_INSIGHTS": {
                "business_cards_analysis": {...},
                "folded_products_analysis": {...}
            },
            "natural_language_hints": {
                "business_cards": "→ 90x55mm, 350GSM Satin",
                ...
            },
            ...
        }
```

---

## 🧪 TEST SCRIPTS

### To Test the Agent:
```
c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\
    ├── test_email_quote_request.py          📧 Test email processing
    ├── test_calculator_ai_interface.py      🧪 Test tool calls
    └── SHOW_ACTUAL_AI_PROMPT_AND_TOOLS.py   📊 Show what AI receives
```

### Run a Test:
```powershell
cd "c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator"
python test_email_quote_request.py
```

---

## 🔑 CONFIGURATION FILES

### API Keys & Database:
```json
// File: config/database-config.json
{
  "DatabaseConnections": {
    "Primary": {
      "Server": "3.25.76.138\\INHPSQLSERVER",
      "Database": "InHousePrint"
    }
  },
  "AI": {
    "AnthropicAPIKey": "sk-ant-...",
    "Model": "claude-sonnet-4-5-20250929"
  }
}
```

---

## 📋 QUICK REFERENCE

### Want to change the System Prompt?
**Edit:** `AI_Quote_Agent/core/calculator_first_autonomous_agent.py`  
**Lines:** 145-760  
**Method:** `_build_system_prompt()`

### Want to add calculator intelligence?
**Edit:** `complete_calculator_implementation.py`  
**Lines:** 139-1370  
**Method:** `get_calculator_requirements()`

### Want to change tool behavior?
**Edit:** `AI_Quote_Agent/core/calculator_first_autonomous_agent.py`  
**Lines:** 1150-1350  
**Method:** `_execute_tool_call()`

### Want to change thinking budget?
**Edit:** `AI_Quote_Agent/core/calculator_first_autonomous_agent.py`  
**Lines:** ~900  
**Change:** `budget_tokens: 3000` → your value

### Want to change AI model?
**Edit:** `config/database-config.json`  
**Line:** `"Model": "claude-sonnet-4-5-20250929"`  
**Options:** 
- `claude-sonnet-4-5-20250929` (current)
- `claude-opus-4-20250514` (more powerful)
- `claude-3-5-sonnet-20241022` (previous version)

---

## 🎯 SUMMARY

### The Complete Stack:

```
AGENT CODE:
├── calculator_first_autonomous_agent.py     ⭐ Main agent
│   ├── System prompt (lines 145-760)
│   ├── Tool handling (lines 900-1100)
│   └── Tool execution (lines 1150-1350)
│
├── complete_calculator_implementation.py    📝 Calculator
│   └── get_calculator_requirements() (lines 139-1370)
│
├── db_connector.py                          💾 Database
│   └── execute_query()
│
└── config/database-config.json              🔑 Configuration
    ├── Database connection
    ├── Anthropic API key
    └── Model selection
```

### Information Flow:

```
CUSTOMER EMAIL
    ↓
AGENT RECEIVES:
- System Prompt (~1,250 tokens) ← calculator_first_autonomous_agent.py
- Tool Definitions (~200 tokens) ← calculator_first_autonomous_agent.py
- Extended Thinking (3000 budget) ← API call settings
    ↓
AGENT CALLS TOOLS:
- get_calculator_requirements() → complete_calculator_implementation.py
- execute_sql() → db_connector.py
- calculate_quote() → complete_calculator_implementation.py
    ↓
AGENT GENERATES:
- Professional response
- Quote details
- Specifications
```

---

**Everything is in these 3 files:**
1. `AI_Quote_Agent/core/calculator_first_autonomous_agent.py` (agent logic)
2. `complete_calculator_implementation.py` (calculator + intelligence)
3. `config/database-config.json` (configuration)

**That's it!** 🎯
