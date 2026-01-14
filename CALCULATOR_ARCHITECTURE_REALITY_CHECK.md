# Calculator Architecture - Reality vs Documentation

## 🚨 CRITICAL FINDING (December 12, 2025)

User feedback revealed a **major disconnect** between system instructions and actual tool availability.

---

## 📊 THE CONFUSION

### What System Prompt Says:
> "For InHouse Print calculators:
> 1. ALWAYS call `inhouse_calculator_guide()` first
> 2. Call `inhouse_get_calculator_requirements(product_type)` (MANDATORY)
> 3. Then call `inhouse_calculate_quote(product_type, parameters)`"

### What Actually Works:
- ❌ `inhouse_get_calculator_requirements()` - **FAILS** with backend import errors
- ❌ `inhouse_calculate_quote()` - **FAILS** with backend import errors  
- ✅ `calculate_business_cards()` - **WORKS** (direct calculator)
- ✅ `calculate_flyers()` - **WORKS** (direct calculator)
- ✅ `calculate_spiral_bound_books_shopify()` - **WORKS** (direct calculator)

---

## 🏗️ ACTUAL ARCHITECTURE (Two Systems)

### System 1: InHouse Print Module (`inhouse-print` platform)
**Location:** `UI/modules_external/inhouse-print/`

**Tools:**
1. `inhouse_calculator_guide()` - Guide tool (works)
2. `inhouse_get_calculator_requirements()` - **BROKEN** (ToolUseAgent import fails)
3. `inhouse_calculate_quote()` - **BROKEN** (ToolUseAgent import fails)
4. `inhouse_query_stock_levels()` - **BROKEN** (ToolUseAgent import fails)
5. `inhouse_get_reorder_alerts()` - **BROKEN** (ToolUseAgent import fails)

**Status:** 🔴 **Backend integration broken** - requires `complete_calculator_implementation.py` which we just restored

**Intended Use:** Complex quotes with database-driven pricing, stock checks, reorder alerts

---

### System 2: Quote Calculator Platform (`quote_calculator` platform)
**Location:** `UI/modules_external/quote-calculator/`

**Tools:** 37 direct calculator functions
- `calculate_business_cards()`
- `calculate_flyers()`
- `calculate_booklets()`
- `calculate_perfect_bound_books()`
- `calculate_spiral_bound_books_shopify()`
- `calculate_wire_bound_books_shopify()`
- ... (31 more)

**Status:** ✅ **Working** - Direct Python implementations, no backend dependency

**Actual Use:** All standard Shopify product calculations

---

## ⚠️ THE PROBLEM

### Issue 1: System Prompt Mismatch
The system prompt **enforces** the InHouse workflow, but those tools are broken:

```
CURRENT INSTRUCTIONS (MISLEADING):
"For calculators: MUST call calculator_guide → get_calculator_requirements → THEN calculate"

REALITY:
- calculator_guide works ✅
- get_calculator_requirements FAILS ❌
- calculate_quote FAILS ❌
- Direct calculators (calculate_business_cards) WORK ✅
```

### Issue 2: Backend Dependency Hell
The InHouse tools depend on:
1. `ToolUseAgent` from `quote-calculator/backend/tool_use_agent.py`
2. Which depends on `complete_calculator_implementation.py` (6,368 lines)
3. Which we just restored from archive
4. But might still have import issues with other dependencies

### Issue 3: Schema vs Reality
- Schemas show parameters as "optional" when they're actually required
- Enum values in schema get rejected by backend validation
- No indication in schema which calculator is actually working

---

## ✅ RECOMMENDED SOLUTION

### Option A: Fix InHouse Backend (Proper Solution)
1. Debug the `ToolUseAgent` import chain completely
2. Ensure all backend dependencies are present
3. Test all 6 inhouse tools thoroughly
4. Update schemas to match actual validation
5. Keep the "official" InHouse workflow in system prompt

**Effort:** High (backend debugging, dependency resolution)
**Benefit:** Unified architecture, proper database integration

---

### Option B: Update Instructions to Reality (Quick Fix)
1. Acknowledge two systems in system prompt
2. Provide fallback guidance when InHouse fails
3. Document which calculators are reliable
4. Add troubleshooting steps

**Effort:** Low (documentation update)
**Benefit:** Immediate usability improvement

---

## 📝 PROPOSED SYSTEM PROMPT UPDATE

### NEW Calculator Instructions:

```markdown
## 🧮 CALCULATOR TOOLS - DUAL ARCHITECTURE

### Primary System: InHouse Print Module (inhouse-print)
**Use for:** Database-driven pricing, stock checks, complex quotes

**Workflow:**
1. `inhouse_calculator_guide()` - Learn available calculators
2. `inhouse_get_calculator_requirements(product_type)` - Get parameters (MANDATORY)
3. `inhouse_calculate_quote(product_type, parameters)` - Execute calculation

**Fallback:** If tools fail with "ToolUseAgent could not be imported":
→ Use Quote Calculator Platform (see below)

---

### Secondary System: Quote Calculator Platform (quote_calculator)
**Use for:** Standard Shopify product quotes, direct calculations

**Discovery:**
1. `list_platform_tools('quote_calculator')` - See all calculators
2. `get_tool_schema('calculate_business_cards')` - Get parameters
3. Execute: `calculate_business_cards(quantity=1000, ...)`

**Available Calculators:** 37 direct tools
- Business cards: `calculate_business_cards()`, `calculate_economical_business_cards_shopify()`, `calculate_premium_business_cards_shopify()`
- Flyers: `calculate_flyers()`, `calculate_folded_flyers_shopify()`
- Books: `calculate_perfect_bound_books()`, `calculate_spiral_bound_books_shopify()`, `calculate_wire_bound_books_shopify()`
- Signs: `calculate_corflute_signs()`, `calculate_bollard_signs()`, `calculate_construction_signs()`
- And 28 more specialized calculators

---

### 🔄 RECOMMENDED FLOW

**Step 1:** Try InHouse system first
```
1. inhouse_calculator_guide()
2. inhouse_get_calculator_requirements('business_cards')
3. inhouse_calculate_quote('business_cards', {quantity: 1000, ...})
```

**Step 2:** If InHouse fails → Use direct calculators
```
1. list_platform_tools('quote_calculator')
2. get_tool_schema('calculate_business_cards')
3. calculate_business_cards(quantity=1000, stock_type='satin_350gsm', ...)
```

---

### ⚠️ KNOWN ISSUES

1. **InHouse Backend:** May fail with import errors - use fallback system
2. **Schema Accuracy:** Some parameters marked "optional" are actually required
3. **Enum Validation:** Backend may reject some enum values shown in schema
4. **Always call `get_tool_schema()` before executing** to see latest requirements
```

---

## 🎯 ACTION ITEMS

### Immediate (Today):
- [ ] Test if restored `complete_calculator_implementation.py` fixes InHouse tools
- [ ] Update system prompt with dual-architecture instructions
- [ ] Add fallback guidance to calculator_guide tool

### Short-term (This Week):
- [ ] Debug remaining InHouse backend issues
- [ ] Fix schema accuracy (required vs optional parameters)
- [ ] Sync enum values between schemas and backend validation
- [ ] Add calculator availability status check

### Long-term (Next Sprint):
- [ ] Unify the two systems into one coherent architecture
- [ ] Deprecate one system if redundant
- [ ] Document migration path if needed
- [ ] Add comprehensive calculator testing suite

---

## 📈 USER IMPACT

**Before Fix:**
- User follows system prompt → hits broken InHouse tools → confusion
- No fallback guidance → trial and error
- Schema mismatches → parameter validation failures
- Overall experience: **Frustrating 4/10**

**After Fix:**
- Clear instructions for both systems
- Explicit fallback when InHouse fails
- Better expectations about tool reliability
- Overall experience: **Expected 8/10**

---

## 💬 USER QUOTE

> "The system prompt said to ALWAYS use the InHouse workflow. But `inhouse_get_calculator_requirements()` and `inhouse_calculate_quote()` both failed. This made me question if I was doing something wrong."

**This is a critical UX failure** - we're instructing users to use broken tools without fallback guidance.

---

**Next Step:** Verify the backend fix worked, then update all documentation immediately.
