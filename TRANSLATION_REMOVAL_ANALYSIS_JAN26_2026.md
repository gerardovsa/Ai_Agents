# Translation Removal Analysis - January 26, 2026

## Executive Summary

**STATUS:** ❌ **TRANSLATION IS ACTIVE** - Multiple layers of parameter translation exist between AI and backend calculators.

**CRITICAL FINDING:** The "fuzzy shit inbetween" you wanted eliminated is STILL ACTIVE across all calculator wrappers.

---

## Current Error Handling Flow

### How Errors Are Returned to AI

**Pattern 1: Wrapper Validation Errors (Lines 1175-1189)**
```python
# calculator_wrapper.py - BEFORE calling backend
if print_type not in ["Colour", "Black & White"]:
    return {
        "success": False,
        "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
    }
```

**Pattern 2: Backend Calculator Errors (EconomicalBusinessCards_Shopify_Calculator.py line 157)**
```python
# Backend calculator - DURING calculation
if artworks < 1 or artworks > 50:
    raise ValueError(f"Artworks must be between 1 and 50. Got: {artworks}")
```

**Pattern 3: Wrapper Exception Handler (Lines 1224-1230)**
```python
except Exception as e:
    print(f"❌ [Shopify Economical Business Cards] Error: {e}")
    return {
        "success": False,
        "error": str(e)
    }
```

### How Platform Fixes/Adjusts for Errors

**Current System:**
1. AI sends invalid parameter → Wrapper validates → Returns `{"success": False, "error": "Invalid X"}`
2. Flask returns HTTP 200 with error JSON (NOT HTTP 500)
3. AI receives error message → Interprets message → Asks user for correction → Resubmits

**Example Flow:**
```
AI sends: {"quantity": 300, "double_sided": true}
                ↓
Wrapper: quantity 300 not in [250, 500, 1000, 2000, 5000, 10000]
                ↓
Return: {"success": false, "error": "Invalid quantity: 300. Must be one of: [250, 500, 1000, 2000, 5000, 10000]"}
                ↓
AI interprets: "I need a valid quantity"
                ↓
AI asks user: "The quantity 300 isn't available. Would you like 250 or 500 cards?"
                ↓
User: "500"
                ↓
AI resubmits: {"quantity": 500, "double_sided": true}
```

---

## Translation Locations Found

### **ACTIVE TRANSLATION - 50+ Instances**

#### **Type 1: Boolean → String Translation**

**Location:** calculator_wrapper.py lines 1192, 1355, 1553, etc.

```python
# TRANSLATION HAPPENING HERE
print_sides = "Double side print" if double_sided else "Single side print"

# AI sends:     double_sided = True (boolean)
# Backend gets: print_sides = "Double side print" (string)
```

**Affected Calculators:**
- calculate_economical_business_cards_shopify (line 1192)
- calculate_premium_business_cards_shopify (line 1355)
- calculate_folded_flyers_shopify (line 1553)
- calculate_printed_flyers_shopify
- calculate_business_cards (line 144)

#### **Type 2: Legacy Parameter Name Translation**

**Location:** calculator_wrapper.py lines 1130-1149 (Economical Business Cards)

```python
# LEGACY TRANSLATION (backwards compatibility)
if colour is not None:
    print_type = "Colour" if colour else "Black & White"
    warnings.append({
        "deprecated_parameter": "colour",
        "translated_to": print_type,
        "message": "⚠️ Parameter 'colour' is deprecated. Use 'print_type' instead."
    })
```

**Legacy Translations Active:**
- `colour` (bool) → `print_type` (string) - Lines 1133-1141
- `stock` (string) → `paper_stock` (string) - Lines 1287-1296
- `fold_type` (string) → `folding` (string) - Lines 1457-1466
- `cellophane` (string) → `celloglaze` (string) - Lines 1473-1482
- `pages` (int) → `internal_pages` (int) - Lines 1772-1780
- `size` (string) → `finish_size` (string) - Lines 1782-1800
- `cover_stock` (string) → `printed_front_cover` (string) - Lines 1802-1810
- `inner_stock` (string) → `internal_stock` (string) - Lines 1812-1828
- `cover_cellophane` (string) → `front_celloglaze` (string) - Lines 1830-1844
- `front_cover_pvc` (string) → `outer_front_cover` (string) - Lines 1846-1854

#### **Type 3: Enum String Mapping Translation**

**Location:** calculator_wrapper.py lines 1562-1580 (Folded Flyers)

```python
# Translation: Map schema strings to backend enums
if size == "DL":
    backend_size = "DL Flyer"
elif size == "A6":
    backend_size = "A6 Flyer"
# ... etc
```

#### **Type 4: Format String Translation**

**Location:** calculator_wrapper.py line 1819 (Wire Bound Books)

```python
# Translate inner_stock format
if internal_stock == "80gsm Offset":
    internal_stock = "80gsm Offset 100% Recycled"  # Add full name
```

---

## Backend Calculator Parameter Requirements

### **ALL BACKEND CALCULATORS USE `print_sides` STRING (NOT `double_sided` BOOL)**

#### **Economical Business Cards** (EconomicalBusinessCards_Shopify_Calculator.py line 119)
```python
def calculate(self,
              quantity: int,
              print_sides: str = "Single side print",  # ❌ NOT double_sided bool
              print_type: str = "Colour",
              finish_size: str = "90mm x 55mm",
              paper_stock: str = "Satin 300GSM",
              artworks: int = 1
              ):
```

#### **Premium Business Cards** (PremiumBusinessCards_Shopify_Calculator.py line 123)
```python
def calculate(self,
              quantity: int,
              print_sides: str = "Single side print",  # ❌ NOT double_sided bool
              print_type: str = "Colour",
              finish_size: str = "90mm x 55mm",
              paper_stock: str = "Satin 350GSM",
              artworks: int = 1,
              celloglaze: str = "1 Side Gloss"
              ):
```

#### **Printed Flyers** (PrintedFlyers_Shopify_Calculator.py line 236)
```python
def calculate(self,
              quantity: int,
              print_sides: str,  # ❌ NOT double_sided bool - "Single" or "Double"
              print_type: str,
              finish_size: str,
              paper_stock: str,
              artworks: int = 1
              ):
```

### **Backend Validation Logic**

**Line 175 in EconomicalBusinessCards_Shopify_Calculator.py:**
```python
if "Double" in print_sides:
    sides_multiplier = Decimal('2')
else:  # Single side
    sides_multiplier = Decimal('1')
```

**Backend expects:**
- `print_sides = "Single side print"` → sides_multiplier = 1
- `print_sides = "Double side print"` → sides_multiplier = 2

**Backend does NOT accept:**
- `double_sided = True` ❌ AttributeError: 'bool' object has no attribute 'in'
- `double_sided = False` ❌ AttributeError

---

## Analysis: Remove Translation - Two Approaches

### **Option A: Update AI Schemas to Match Backend (RECOMMENDED)**

**Approach:** Make AI send EXACTLY what backend expects - NO TRANSLATION LAYER

**Changes Required:**

#### **1. Update AI Tool Schemas**

**Current AI Schema (calculator_wrapper.py line 1095):**
```python
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    double_sided: bool = None,  # ❌ REMOVE THIS
    celloglaze: str = None,
    artworks: int = None
):
```

**NEW AI Schema:**
```python
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    print_sides: str = None,  # ✅ ADD THIS - matches backend
    celloglaze: str = None,
    artworks: int = None
):
```

**AI Schema Parameter Definition:**
```python
{
    "print_sides": {
        "type": "string",
        "enum": ["Single side print", "Double side print"],
        "description": "Printing on one side or both sides",
        "default": "Double side print"
    }
}
```

#### **2. Remove Translation Code**

**DELETE Line 1192 in calculator_wrapper.py:**
```python
# ❌ DELETE THIS LINE
print_sides = "Double side print" if double_sided else "Single side print"
```

**NEW Code:**
```python
# ✅ NO TRANSLATION - Pass directly to backend
calculator = EconomicalBusinessCardsShopifyCalculator()
result = calculator.calculate(
    quantity=quantity,
    print_sides=print_sides,  # AI sends this directly
    print_type=print_type,
    artworks=artworks
)
```

#### **3. Add Parameter Validation**

**NEW Validation (replaces translation):**
```python
# Validate print_sides matches backend expectations
if print_sides not in ["Single side print", "Double side print"]:
    return {
        "success": False,
        "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print'",
        "valid_options": ["Single side print", "Double side print"]
    }
```

**AI Response to Error:**
```
AI receives: {"success": false, "error": "Invalid print_sides: 'double_sided'. Must be 'Single side print' or 'Double side print'"}

AI interprets: "I sent wrong parameter format"

AI asks user: "Do you want single-sided or double-sided printing?"
User: "double-sided"

AI resubmits: {"print_sides": "Double side print"}  # ✅ Correct format
```

#### **Pros:**
✅ AI learns EXACT backend parameters
✅ No translation layer = no bugs
✅ Error messages show exact format needed
✅ Backend stays unchanged (stable, tested)
✅ Future calculators follow same pattern

#### **Cons:**
❌ AI schemas less natural (`"Double side print"` vs `true`)
❌ Must update 27 calculator wrapper functions
❌ Must update AI system prompt documentation
❌ Existing AI conversations using `double_sided` will break

---

### **Option B: Update Backend Calculators to Accept Boolean (NOT RECOMMENDED)**

**Approach:** Change ALL backend calculators to accept `double_sided: bool`

**Changes Required:**

#### **1. Update Backend Calculator Signatures**

**Current (EconomicalBusinessCards_Shopify_Calculator.py line 119):**
```python
def calculate(self,
              quantity: int,
              print_sides: str = "Single side print",  # ❌ CHANGE THIS
              ...
```

**NEW:**
```python
def calculate(self,
              quantity: int,
              double_sided: bool = True,  # ✅ NEW - boolean instead of string
              ...
```

#### **2. Update Backend Logic**

**Current (line 175):**
```python
if "Double" in print_sides:
    sides_multiplier = Decimal('2')
else:
    sides_multiplier = Decimal('1')
```

**NEW:**
```python
sides_multiplier = Decimal('2') if double_sided else Decimal('1')
```

#### **3. Update ALL 27+ Backend Calculators**

Must change:
- EconomicalBusinessCards_Shopify_Calculator.py
- PremiumBusinessCards_Shopify_Calculator.py
- PrintedFlyers_Shopify_Calculator.py
- FoldedFlyers_Shopify_Calculator.py
- WireBound_Shopify_Calculator.py
- SpiralBound_Shopify_Calculator.py
- PerfectBound_Shopify_Calculator.py
- ... 20+ more calculators

#### **Pros:**
✅ AI schemas more natural (`double_sided: true` vs `"Double side print"`)
✅ Remove translation from wrappers
✅ Wrapper functions become simpler

#### **Cons:**
❌ Must update 27+ backend calculator files (HIGH RISK)
❌ Must re-test ALL calculators (time consuming)
❌ Backend calculators are source of truth (tested against Shopify)
❌ Shopify JSON configs expect string format
❌ Risk breaking production pricing
❌ Future Shopify calculators may use string format

---

## Answer to Your Questions

### **Question 1: "Remove the translation and update AI schemas to use print_sides directly?"**

**ANSWER: YES - THIS IS THE CORRECT APPROACH (Option A)**

**Why:**
1. **Backend is source of truth** - Backend calculators match Shopify DPO JavaScript exactly
2. **Backend is tested** - All 27 calculators validated against Shopify pricing
3. **Backend is stable** - No need to touch production pricing logic
4. **AI should adapt to backend** - Not the other way around
5. **Error messages are clear** - AI will learn exact format needed

**Implementation:**
- Remove translation line: `print_sides = "Double side print" if double_sided else "Single side print"`
- Update AI schemas: Change `double_sided: bool` → `print_sides: str`
- Add validation: Check `print_sides in ["Single side print", "Double side print"]`
- Update system prompt: Document exact parameter formats

### **Question 2: "Change backend calculators to accept double_sided boolean instead?"**

**ANSWER: NO - DO NOT CHANGE BACKEND CALCULATORS**

**Why:**
1. **High risk** - 27+ files to change, 100+ tests to re-run
2. **Breaks Shopify alignment** - Backend matches Shopify JavaScript exactly
3. **Config files use strings** - JSON configs expect `print_sides: "Double side print"`
4. **Production stability** - Backend is tested source of truth
5. **Future maintenance** - Shopify updates may require string format

---

## Recommended Implementation Plan

### **Phase 1: Remove Translation (URGENT)**

**Delete these lines from calculator_wrapper.py:**
- Line 144: `print_sides = "Double side print" if print_type == "double_sided" else "Single side print"`
- Line 1192: `print_sides = "Double side print" if double_sided else "Single side print"`
- Line 1355: `print_sides = "Double side print" if double_sided else "Single side print"`
- Line 1553: `print_sides = "Double side print" if double_sided else "Single side print"`
- Lines 1130-1149: Legacy `colour` → `print_type` translation
- Lines 1275-1296: Legacy `stock` → `paper_stock` translation
- Lines 1445-1482: Legacy `fold_type`, `cellophane` translations
- Lines 1768-1854: Wire Bound legacy parameter translations
- Lines 2005+: Spiral Bound legacy parameter translations

### **Phase 2: Update AI Schemas**

**Change wrapper function signatures:**

**Before:**
```python
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    double_sided: bool = None,  # ❌ REMOVE
    celloglaze: str = None,
    artworks: int = None
):
```

**After:**
```python
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    print_sides: str = None,  # ✅ ADD - matches backend exactly
    celloglaze: str = None,
    artworks: int = None
):
```

### **Phase 3: Add Strict Validation**

**Replace translation with validation:**

**Before (Line 1192):**
```python
# TRANSLATION LAYER: Schema → Backend
print_sides = "Double side print" if double_sided else "Single side print"
```

**After:**
```python
# STRICT VALIDATION: No translation - AI must send exact format
if print_sides not in ["Single side print", "Double side print"]:
    return {
        "success": False,
        "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print'",
        "parameter": "print_sides",
        "valid_options": ["Single side print", "Double side print"],
        "ai_instruction": "You must send print_sides as exactly 'Single side print' or 'Double side print'"
    }
```

### **Phase 4: Update System Prompt**

**Update tool_usage_system_prompt.md:**

**Add section:**
```markdown
## CRITICAL: Exact Parameter Formats Required

**NO TRANSLATION LAYER EXISTS**

When calling calculator tools, you MUST send parameters in EXACT format backend expects:

❌ WRONG: {"double_sided": true}
✅ CORRECT: {"print_sides": "Double side print"}

❌ WRONG: {"double_sided": false}
✅ CORRECT: {"print_sides": "Single side print"}

**If you send wrong format:**
- Backend will return: {"success": false, "error": "Invalid print_sides: ..."}
- You must ask user for clarification
- You must resubmit with EXACT format from error message

**No fuzzy matching, no auto-correction, no translation**
```

### **Phase 5: Remove Legacy Parameter Support**

**Delete all deprecated parameter handling:**
- `colour` → `print_type` (remove lines 1130-1149)
- `stock` → `paper_stock` (remove lines 1287-1296)
- `fold_type` → `folding` (remove lines 1457-1466)
- All legacy warnings and translation

**Force breaking change:**
- Old AI conversations using `colour`, `stock`, etc. will fail
- Error messages will tell AI to use correct parameter names
- AI will learn correct names from errors

---

## Error Response Examples (After Translation Removed)

### **Example 1: Wrong Parameter Name**

**AI sends:**
```json
{
  "tool_name": "calculate_economical_business_cards_shopify",
  "params": {
    "quantity": 500,
    "double_sided": true  // ❌ Wrong parameter name
  }
}
```

**Wrapper response:**
```json
{
  "success": false,
  "error": "Unknown parameter 'double_sided' in calculate_economical_business_cards_shopify",
  "valid_parameters": ["quantity", "print_type", "print_sides", "celloglaze", "artworks"],
  "hint": "Did you mean 'print_sides'? Use 'print_sides' with values: 'Single side print' or 'Double side print'"
}
```

**AI learns:** "I sent wrong parameter name, use `print_sides` instead"

### **Example 2: Wrong Parameter Value**

**AI sends:**
```json
{
  "tool_name": "calculate_economical_business_cards_shopify",
  "params": {
    "quantity": 500,
    "print_sides": "double sided"  // ❌ Wrong value format
  }
}
```

**Wrapper response:**
```json
{
  "success": false,
  "error": "Invalid print_sides: 'double sided'. Must be 'Single side print' or 'Double side print'",
  "parameter": "print_sides",
  "value_sent": "double sided",
  "valid_options": ["Single side print", "Double side print"]
}
```

**AI learns:** "I sent wrong format, must use exact string 'Double side print'"

### **Example 3: Correct Format**

**AI sends:**
```json
{
  "tool_name": "calculate_economical_business_cards_shopify",
  "params": {
    "quantity": 500,
    "print_sides": "Double side print",  // ✅ Correct
    "print_type": "Colour",
    "artworks": 1
  }
}
```

**Backend response:**
```json
{
  "success": true,
  "product_type": "Economical Business Cards",
  "quantity": 500,
  "total_price": 104.50,
  "breakdown": {...}
}
```

**AI learns:** "This format works, remember it"

---

## Implementation Checklist

- [ ] **Remove all `print_sides =` translation lines** (4 locations)
- [ ] **Remove all legacy parameter translations** (10+ locations)
- [ ] **Update wrapper function signatures** (27 calculators)
- [ ] **Add strict validation** (replace translation with validation)
- [ ] **Update system prompt** (document exact formats)
- [ ] **Test all 27 calculators** (verify errors returned correctly)
- [ ] **Update any existing AI conversation templates** (fix parameter names)
- [ ] **Monitor AI behavior** (ensure AI learns from error messages)

---

## Risk Assessment

### **Option A (Update AI Schemas) - LOW RISK** ✅
- Backend untouched (stable)
- AI learns from errors (self-correcting)
- Clear error messages (no ambiguity)
- Wrappers become simpler (remove code)

### **Option B (Update Backend) - HIGH RISK** ❌
- 27+ files to change (error-prone)
- Must re-test all calculators (time-consuming)
- Risk breaking production pricing (critical failure)
- Shopify alignment breaks (future maintenance issues)

---

## Final Recommendation

**REMOVE TRANSLATION - UPDATE AI SCHEMAS (Option A)**

**Reasoning:**
1. Backend calculators are source of truth (match Shopify exactly)
2. AI is smart enough to learn exact formats from error messages
3. No translation = no bugs, no ambiguity
4. Clear error messages guide AI to correct format
5. Lower risk than changing 27 backend files

**Next Steps:**
1. ✅ Analysis complete (this document)
2. ⏳ Approve approach (awaiting confirmation)
3. ⏳ Remove translation code (delete ~200 lines)
4. ⏳ Update schemas (change parameter names)
5. ⏳ Test with AI (verify error handling works)
6. ⏳ Deploy to production

---

**Document Version:** 1.0  
**Last Updated:** January 26, 2026  
**Analysis By:** AI Agent System
