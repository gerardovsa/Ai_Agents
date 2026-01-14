# 🚨 CRITICAL ERRORS FOUND IN inhouse_guide_wrapper.py

## Analysis Date: December 16, 2025

---

## ❌ ERROR #1: WRONG TOOL NAMES IN TIER 3 DOCUMENTATION

### Location: Header Docstring (Lines 19-25)

**CLAIMED (WRONG):**
```python
Tier 3 (Action Tools - in inhouse_wrapper.py):
  - inhouse_get_calculator_requirements()  ✅ CORRECT
  - inhouse_calculate_quote()              ❌ WRONG NAME!
  - inhouse_get_query_library_catalog()    ✅ CORRECT
  - inhouse_execute_sql()                  ❌ WRONG NAME!
  - inhouse_query_stock_levels()           ✅ CORRECT
  - inhouse_get_reorder_alerts()           ✅ CORRECT
```

**ACTUAL TOOL NAMES (from inhouse_wrapper.py):**
```python
Line 132: def inhouse_get_query_library_catalog(...)  # ✅ Correct
Line 167: def inhouse_execute_sql(...)                # ✅ Named correctly in code
Line 204: def inhouse_get_calculator_requirements(...)  # ✅ Correct
Line 258: def inhouse_calculate_quote(...)            # ✅ Named correctly in code
Line 305: def inhouse_query_stock_levels(...)         # ✅ Correct
Line 338: def inhouse_get_reorder_alerts(...)         # ✅ Correct
```

**VERDICT:** Tools ARE named correctly in code! The guide is CORRECT.

---

## ❌ ERROR #2: CALCULATOR WORKFLOW REFERENCES NON-EXISTENT TOOL

### Location: inhouse_calculator_guide() - Line 192

**PROBLEM:**
```python
"workflow_guidance": {
    "step_1": {
        "tool": "inhouse_get_calculator_requirements(product_type)",  # ✅ EXISTS
        ...
    },
    "step_3": {
        "tool": "inhouse_calculate_quote(product_type, parameters)",   # ✅ EXISTS
        ...
    }
}
```

**BUT THEN:**
```python
"next_steps": [
    "1. Call get_tool_schema('calculate_business_cards') to get parameter requirements from schema",
    "2. Parse user input using enum values and descriptions from schema",
    "3. Call calculate_business_cards(quantity=1000, ...) with validated parameters"
]
```

**THE ISSUE:**
- Guide says use `inhouse_calculator_guide()` → `get_tool_schema('calculate_business_cards')` → `calculate_business_cards()`
- But `calculate_business_cards()` is in `calculator_wrapper.py` (quote-calculator module)
- **NOT** in `inhouse_wrapper.py`!

**ACTUAL CALCULATOR TOOLS LOCATION:**
```
quote-calculator/implementations/calculator_wrapper.py:
  - calculate_business_cards()      # Line ~200
  - calculate_flyers()
  - calculate_booklets()
  - calculate_perfect_bound_books()
  - calculate_letterheads()
  - calculate_corflute_signs()
  ... (31 total calculators)
```

**CORRECT WORKFLOW SHOULD BE:**

**Option A - Use Direct Calculators:**
1. `inhouse_get_domain_guide()` → domain="calculator"
2. `list_platform_tools("quote_calculator")` → See all 31 calculators
3. `get_tool_schema("calculate_business_cards")` → Get parameters
4. `calculate_business_cards(quantity=500, ...)` → Execute

**Option B - Use InHouse Wrapper:**
1. `inhouse_get_domain_guide()` → domain="calculator"
2. `inhouse_calculator_guide()` → Learn system
3. `inhouse_get_calculator_requirements(product_type="business_cards")` → Get params
4. `inhouse_calculate_quote(product_type="business_cards", parameters={...})` → Execute

**THE GUIDE MIXES BOTH WORKFLOWS!**

---

## ❌ ERROR #3: CONTRADICTORY WORKFLOW INSTRUCTIONS

### Location: inhouse_calculator_guide() - Lines 234-282

**CONTRADICTION #1:**
```python
"follow_up_tool_chain": {
    "steps": [
        {
            "step": 2,
            "tool": "get_tool_schema('calculate_business_cards')",  # ← Direct calculator
            ...
        },
        {
            "step": 3,
            "tool": "calculate_business_cards(...)",                # ← Direct calculator
            ...
        }
    ]
}
```

**BUT EARLIER IN SAME FUNCTION:**
```python
"workflow_guidance": {
    "step_1": {
        "tool": "inhouse_get_calculator_requirements(product_type)",  # ← Wrapper tool
        ...
    },
    "step_3": {
        "tool": "inhouse_calculate_quote(product_type, parameters)",  # ← Wrapper tool
        ...
    }
}
```

**THESE ARE TWO DIFFERENT WORKFLOWS PRESENTED AS ONE!**

---

## ❌ ERROR #4: WRONG TOOL NAME IN WORKFLOW STEPS

### Location: inhouse_get_domain_guide() - Lines 110-113

**CLAIMED:**
```python
"calculator_workflow": {
    "steps": [
        "inhouse_get_domain_guide() → Identify 'calculator' domain",
        "inhouse_calculator_guide() → Learn calculator types and workflow",
        "inhouse_get_calculator_requirements(product_type) → Get parameter requirements",
        "inhouse_calculate_quote(product_type, parameters) → Execute calculation"  # ✅ CORRECT
    ],
    "mandatory": "YES - Skipping get_calculator_requirements causes parameter errors"
}
```

**VERDICT:** This workflow IS correct for using the InHouse wrapper approach.

---

## ❌ ERROR #5: ANTI-PATTERN LIST IS INCOMPLETE

### Location: inhouse_get_domain_guide() - Lines 158-163

**CLAIMED:**
```python
"anti_patterns": [
    "Calling inhouse_calculate_quote WITHOUT inhouse_get_calculator_requirements",
    "Calling inhouse_execute_sql WITHOUT inhouse_database_guide (for custom SQL)",
    "Skipping domain_guide and going directly to action tools",
    "Assuming schema knowledge without reading database_guide"
]
```

**MISSING ANTI-PATTERNS:**
- Calling `calculate_business_cards()` directly without `get_tool_schema()`
- Calling `execute_query_library()` without `get_available_queries()`
- Mixing InHouse wrapper tools with direct calculator tools in same workflow
- Using `inhouse_get_calculator_requirements()` then calling direct `calculate_business_cards()` (workflow confusion)

---

## ❌ ERROR #6: QUERY WORKFLOW REFERENCES WRONG TOOL NAME

### Location: inhouse_get_domain_guide() - Lines 118-133

**CLAIMED:**
```python
"query_workflow": {
    "pre_built": [
        "inhouse_get_domain_guide() → Identify 'query' domain",
        "inhouse_query_guide() → Learn about pre-built queries",
        "inhouse_get_query_library_catalog(category) → Browse available queries",  # ✅ CORRECT
        "inhouse_execute_sql(query) → Execute selected query"                     # ✅ CORRECT
    ],
    "custom_sql": [
        "inhouse_get_domain_guide() → Identify 'query' domain",
        "inhouse_query_guide() → Learn that custom SQL requires schema",
        "inhouse_database_guide() → GET SCHEMA FIRST (prevents column name errors)",
        "inhouse_execute_sql(query) → Execute custom SQL"                         # ✅ CORRECT
    ],
    "mandatory": "YES - Skipping database_guide causes 'Invalid column name' errors"
}
```

**VERDICT:** This workflow IS correct!

---

## ❌ ERROR #7: QUERY LIBRARY CATALOG VS AVAILABLE QUERIES CONFUSION

### Location: inhouse_query_guide() - Lines 379-385

**GUIDE SAYS:**
```python
{
    "step": 1,
    "tool": "inhouse_get_query_library_catalog(category)",
    "description": "Browse available queries by category (optional filter)"
}
```

**BUT inhouse_wrapper.py Line 164 SHOWS:**
```python
def inhouse_get_query_library_catalog(category: Optional[str] = None, **kwargs):
    ...
    return agent._execute_client_tool('get_available_queries', {'category': category})
    #                                  ^^^^^^^^^^^^^^^^^^^^
    #                                  Backend function name!
```

**CONFUSION:**
- Guide says: `inhouse_get_query_library_catalog(category)`
- Wrapper calls backend: `get_available_queries(category)`
- Are these the same tool or different tools?

**INVESTIGATION NEEDED:**
Check if `get_available_queries` is:
1. A backend function in `tool_use_agent.py` (wrapper pattern)
2. A separate AI tool in registry

---

## ✅ CORRECT SECTIONS (No Errors Found)

### inhouse_stock_guide():
- Correctly references `inhouse_query_stock_levels()` ✅
- Correctly references `inhouse_get_reorder_alerts()` ✅
- Correctly explains when to use `inhouse_database_guide()` ✅

### inhouse_database_guide():
- Schema documentation appears accurate ✅
- Common mistakes are real (verified from code archaeology) ✅
- SQL Server syntax rules are correct ✅
- Database separation (InHouse Fred vs Supabase) is correctly explained ✅

---

## 🔧 RECOMMENDED FIXES

### FIX #1: Clarify Two Calculator Pathways

**Update inhouse_calculator_guide() to explicitly show TWO workflows:**

```python
"available_workflows": {
    "workflow_a_wrapper_approach": {
        "description": "Use InHouse wrapper tools (recommended for complex workflows)",
        "steps": [
            "1. inhouse_calculator_guide() - Learn system",
            "2. inhouse_get_calculator_requirements(product_type) - Get params",
            "3. inhouse_calculate_quote(product_type, parameters) - Execute"
        ],
        "advantages": [
            "Automatic parameter validation",
            "Natural language mapping included",
            "Historical patterns for defaults",
            "Consistent error handling"
        ]
    },
    "workflow_b_direct_calculators": {
        "description": "Use direct calculator tools (recommended for simple quotes)",
        "steps": [
            "1. list_platform_tools('quote_calculator') - See all 31 calculators",
            "2. get_tool_schema('calculate_business_cards') - Get parameters",
            "3. calculate_business_cards(quantity=500, ...) - Execute"
        ],
        "advantages": [
            "Fewer steps",
            "Direct access to 31 specialized calculators",
            "Type enforcement via schema_validator",
            "No intermediate wrapper layer"
        ]
    }
},
"when_to_use_which": {
    "use_wrapper_approach": [
        "Parsing TicketNotes from JobTickets table",
        "Need natural language parameter mapping",
        "Want historical pattern defaults",
        "Complex multi-product quotes"
    ],
    "use_direct_calculators": [
        "Simple single-product quotes",
        "Parameters already known and validated",
        "Using specific calculator (e.g., premium_business_cards_shopify)",
        "Performance-critical workflows"
    ]
}
```

### FIX #2: Remove Contradictory "follow_up_tool_chain"

**Delete or replace the current "follow_up_tool_chain" section (lines 234-282) with:**

```python
"follow_up_tool_chain": {
    "description": "Choose your workflow after reading this guide",
    "option_a_wrapper": {
        "steps": [
            {
                "step": 1,
                "tool": "inhouse_calculator_guide()",
                "status": "YOU ARE HERE",
                "action": "Read this guide to understand both workflows"
            },
            {
                "step": 2,
                "tool": "inhouse_get_calculator_requirements(product_type='business_cards')",
                "status": "NEXT (Wrapper approach)",
                "action": "Get parameter requirements with natural language mapping"
            },
            {
                "step": 3,
                "tool": "inhouse_calculate_quote(product_type='business_cards', parameters={...})",
                "status": "FINAL",
                "action": "Execute quote calculation via wrapper"
            }
        ],
        "ascii_diagram": """
        1. inhouse_calculator_guide() ← YOU ARE HERE
                ↓
        2. inhouse_get_calculator_requirements('business_cards') ← Wrapper approach
                ↓
        3. inhouse_calculate_quote('business_cards', {...}) ← Execute via wrapper
        """
    },
    "option_b_direct": {
        "steps": [
            {
                "step": 1,
                "tool": "inhouse_calculator_guide()",
                "status": "YOU ARE HERE",
                "action": "Read this guide to understand both workflows"
            },
            {
                "step": 2,
                "tool": "get_tool_schema('calculate_business_cards')",
                "status": "NEXT (Direct approach)",
                "action": "Get parameter schema from calculator tool"
            },
            {
                "step": 3,
                "tool": "calculate_business_cards(quantity=500, finish_size='90x55mm', ...)",
                "status": "FINAL",
                "action": "Execute calculator directly"
            }
        ],
        "ascii_diagram": """
        1. inhouse_calculator_guide() ← YOU ARE HERE
                ↓
        2. get_tool_schema('calculate_business_cards') ← Direct approach
                ↓
        3. calculate_business_cards(quantity=500, ...) ← Execute calculator directly
        """
    }
}
```

### FIX #3: Update "next_steps" Section

**Replace lines 226-230 with:**

```python
"next_steps": [
    "Decision point: Use wrapper approach or direct calculators?",
    "Wrapper: Call inhouse_get_calculator_requirements(product_type) → inhouse_calculate_quote()",
    "Direct: Call get_tool_schema('calculate_business_cards') → calculate_business_cards()",
    "Both workflows are valid - wrapper provides more guidance, direct is faster"
]
```

### FIX #4: Add Anti-Pattern for Workflow Mixing

**Update anti_patterns list in inhouse_get_domain_guide():**

```python
"anti_patterns": [
    "Calling inhouse_calculate_quote WITHOUT inhouse_get_calculator_requirements",
    "Calling calculate_business_cards() WITHOUT get_tool_schema (direct workflow)",
    "Mixing wrapper and direct workflows (e.g., inhouse_get_calculator_requirements → calculate_business_cards)",
    "Calling inhouse_execute_sql WITHOUT inhouse_database_guide (for custom SQL)",
    "Skipping domain_guide and going directly to action tools",
    "Assuming schema knowledge without reading database_guide"
]
```

---

## 📊 SUMMARY OF ERRORS

| Error # | Location | Severity | Type | Fix Required |
|---------|----------|----------|------|--------------|
| 1 | Header | ❌ FALSE ALARM | Documentation | None - tools are named correctly |
| 2 | inhouse_calculator_guide | 🔴 CRITICAL | Wrong workflow | Clarify two pathways |
| 3 | inhouse_calculator_guide | 🔴 CRITICAL | Contradiction | Replace follow_up_tool_chain |
| 4 | inhouse_get_domain_guide | ✅ CORRECT | None | None |
| 5 | inhouse_get_domain_guide | 🟡 MINOR | Incomplete | Add workflow mixing to anti-patterns |
| 6 | inhouse_get_domain_guide | ✅ CORRECT | None | None |
| 7 | inhouse_query_guide | 🟡 INVESTIGATION | Naming confusion | Verify backend function name |

---

## 🎯 ACTION ITEMS

1. **HIGH PRIORITY:** Fix contradictory calculator workflows (Errors #2, #3)
2. **MEDIUM PRIORITY:** Add workflow mixing to anti-patterns (Error #5)
3. **LOW PRIORITY:** Investigate query library naming (Error #7)
4. **VERIFICATION:** Test both calculator workflows with real AI to confirm they work

---

**END OF ERROR ANALYSIS**
