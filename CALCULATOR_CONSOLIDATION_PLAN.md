# Calculator System Consolidation Plan
## ONE Pathway - Remove Broken Backend

---

## 🎯 USER FEEDBACK (December 12, 2025)

> "Fix it so it does not fail... make it only have ONE pathway? Why do we have two pathways?  
> If quote calculator works then use it and remove the other...  
> They should not directly use the calculators... they need to understand how to use them?"

**User is right** - We need ONE clear pathway that works.

---

## 📊 CURRENT STATE

### What Works ✅
1. **Guide Tools** (InHouse module)
   - `inhouse_get_domain_guide()` - Entry point
   - `inhouse_calculator_guide()` - Teaching tool
   - `inhouse_query_guide()` - SQL guidance
   - `inhouse_database_guide()` - Schema reference

2. **Direct Calculators** (Quote Calculator module)
   - 37 calculator functions
   - `calculate_business_cards()`, `calculate_flyers()`, etc.
   - Direct execution, no backend dependencies

### What's Broken ❌
3. **InHouse Action Tools** (Backend-dependent)
   - `inhouse_get_calculator_requirements()` - Import errors
   - `inhouse_calculate_quote()` - Import errors
   - Requires: ToolUseAgent → complete_calculator_implementation → db_connector → etc.

---

## 🔧 THE SOLUTION: Redirect Guides to Direct Calculators

### Current Flow (BROKEN):
```
User: "Calculate business cards"
  ↓
inhouse_calculator_guide() → "Call inhouse_get_calculator_requirements()"
  ↓
inhouse_get_calculator_requirements() → ❌ FAILS (backend import error)
  ↓
inhouse_calculate_quote() → ❌ FAILS (backend import error)
```

### New Flow (ONE PATHWAY):
```
User: "Calculate business cards"
  ↓
inhouse_calculator_guide() → "Here are the working calculators and how to use them"
  ↓
Shows: calculate_business_cards(quantity, stock_type, print_sides, celloglaze)
  ↓
calculate_business_cards() → ✅ WORKS (direct implementation)
```

---

## 📝 IMPLEMENTATION PLAN

### Step 1: Update inhouse_calculator_guide()
**Change:** Remove references to broken backend tools  
**Add:** Direct calculator workflow with examples

**NEW OUTPUT:**
```json
{
  "guide": "InHouse Print Calculator System",
  "purpose": "Learn how to use calculators before executing",
  
  "calculator_types": {
    "business_cards": {
      "tool": "calculate_business_cards",
      "parameters": {
        "quantity": [100, 250, 500, 1000, 2000, 5000, 10000],
        "finish_size": ["90x55mm", "90x50mm", "85x55mm"],
        "stock_type": ["standard", "premium", "satin", "uncoated"],
        "print_sides": ["single_sided", "double_sided"],
        "celloglaze": ["none", "gloss", "matt"]
      },
      "example": "calculate_business_cards(quantity=1000, finish_size='90x55mm', stock_type='satin', print_sides='double_sided', celloglaze='none')"
    },
    "flyers": { ... },
    "booklets": { ... },
    // etc for all 37 calculators
  },
  
  "workflow": {
    "step_1": "Read this guide to understand parameters",
    "step_2": "Call get_tool_schema('calculate_business_cards') for latest requirements",
    "step_3": "Execute: calculate_business_cards(quantity=1000, ...)",
    "step_4": "Review results and present quote to user"
  },
  
  "removed_tools": {
    "reason": "Backend-dependent tools removed for reliability",
    "deprecated": [
      "inhouse_get_calculator_requirements (replaced by guide + get_tool_schema)",
      "inhouse_calculate_quote (replaced by direct calculators)"
    ]
  }
}
```

### Step 2: Remove Broken Backend Tools from Schema
**File:** `UI/modules_external/inhouse-print/schema/inhouse_tools.json`

**REMOVE:**
- `inhouse_get_calculator_requirements` tool definition
- `inhouse_calculate_quote` tool definition
- `inhouse_query_stock_levels` (if broken)
- `inhouse_get_reorder_alerts` (if broken)

**KEEP:**
- All guide tools (they work!)
- `inhouse_get_query_library_catalog` (if working)
- `inhouse_execute_sql` (if working)

### Step 3: Update System Prompt
**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

**OLD:**
```markdown
For calculators: MUST call calculator_guide → get_calculator_requirements → THEN calculate
```

**NEW:**
```markdown
## Calculator Workflow (ONE Clear Path)

1. **Learn First:** Call `inhouse_calculator_guide()`
   - Understand calculator types and parameters
   - See examples for each product type
   
2. **Get Latest Schema:** Call `get_tool_schema('calculate_business_cards')`
   - Verify current parameter requirements
   - Check enum values and defaults
   
3. **Execute:** Call direct calculator
   - Example: `calculate_business_cards(quantity=1000, stock_type='satin', ...)`
   - All 37 calculators available in quote_calculator platform
   
4. **Present Results:** Format quote for user
```

### Step 4: Create Migration Notice
**File:** `CALCULATOR_BACKEND_DEPRECATION.md`

Document why backend tools were removed:
- Import dependency hell (ToolUseAgent → complete_calculator_implementation → db_connector)
- Direct calculators are more reliable
- Guide tools provide same educational value
- ONE pathway principle: Simpler is better

---

## 🎯 BENEFITS

### User Experience:
- ✅ ONE clear pathway (no confusion)
- ✅ Guide tools teach before execution
- ✅ All calculators actually work
- ✅ No backend dependency failures

### AI Agent Behavior:
- ✅ Learns from guide first (as user requested)
- ✅ Gets parameter requirements from schema
- ✅ Executes with direct tools that work
- ✅ No trial-and-error with broken tools

### Maintenance:
- ✅ Remove 6,368 lines of backend calculator code
- ✅ Remove db_connector, stock_database_tools dependencies
- ✅ Keep 37 simple, direct calculator implementations
- ✅ Guides remain as educational tools

---

## 📋 FILES TO CHANGE

1. **inhouse_guide_wrapper.py** - Update calculator_guide() output
2. **inhouse_tools.json** - Remove broken action tool definitions
3. **tool_usage_system_prompt.md** - Update workflow instructions
4. **CALCULATOR_BACKEND_DEPRECATION.md** - Document the change

---

## ⚠️ VALIDATION

After changes:
```python
# Test 1: Guide works
result = r.execute_tool('inhouse_calculator_guide')
assert 'calculate_business_cards' in str(result)

# Test 2: Direct calculator works
result = r.execute_tool('calculate_business_cards', 
                       quantity=1000, 
                       finish_size='90x55mm',
                       stock_type='satin',
                       print_sides='double_sided',
                       celloglaze='none')
assert result['success'] == True

# Test 3: Broken tools removed
tools = r.get_anthropic_tools()
assert 'inhouse_get_calculator_requirements' not in [t['name'] for t in tools]
assert 'inhouse_calculate_quote' not in [t['name'] for t in tools]
```

---

## ✅ FINAL RESULT

**ONE Pathway:**
```
User Request
  ↓
inhouse_calculator_guide() (Learn)
  ↓
get_tool_schema() (Verify)
  ↓
calculate_business_cards() (Execute)
  ↓
Present Quote (Success)
```

**No broken backend. No competing pathways. Just works.**

---

**Ready to implement?** This consolidates to ONE reliable pathway as user requested.
