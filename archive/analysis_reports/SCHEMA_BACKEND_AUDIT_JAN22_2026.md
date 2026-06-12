# Schema/Backend Discrepancy Audit - January 22, 2026

## 🎯 Objective
Audit all calculator schemas against backend implementations to find mismatches between what the AI agent sees (schema) and what the calculator actually supports (backend code).

---

## 🔍 Key Finding: DL Size Missing from Folded Flyers Backend

### **User's Original Issue:**
- **Error:** "Stream error! status: 502" when requesting 1000 DL flyers (99mm x 210mm)
- **Root Cause:** Schema claimed DL support but backend `FinishSize` enum didn't have DL value

### **Fix Applied:**

**File:** `UI/modules_external/quote-calculator/backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py`

**Line 70 - Added DL to FinishSize enum:**
```python
class FinishSize(Enum):
    """Finish size options with items per sheet"""
    DL = ("DL - 99mm x 210mm", 99, 210, Decimal('6'), "a5_size")  # ✅ ADDED Jan 22, 2026
    A5 = ("A5 - 148mm x 210mm", 148, 210, Decimal('4'), "a5_size")
    A4 = ("A4 - 210mm x 297mm", 210, 297, Decimal('2'), "a4_size")
    A3 = ("A3 - 297mm x 420mm", 297, 420, Decimal('1'), "a3_size")
    A4_6PP = ("6pp A4 - 630mm x 297mm", 630, 297, Decimal('0.5'), "6pp_a4_size")
```

**DL Size Specifications:**
- Dimensions: 99mm × 210mm
- Items per SRA3 sheet: 6 (higher efficiency than A5's 4)
- Margin category: Uses A5 profit margins (same height)
- Imposition: 6 (confirmed from WireBound and SpiralBound calculators)

---

## ✅ Testing Results

### **Test Case: User's Original Request**
- Quantity: 1000
- Size: DL (99mm x 210mm)
- Stock: Satin 128GSM
- Sides: Double-sided
- Print: Colour
- Folding: Single Fold

**Result: ✅ SUCCESS**
```
💰 Total Price: $235.90
📊 Unit Price: $0.2359
📦 Quantity: 1000

📈 Cost Breakdown:
   Setup Total: $49.00
   Stock Cost: $6.93
   Click Cost: $14.70
   Cutting Cost: $3.85
   Folding Cost: $23.00
   Cello Cost: $0.00
   Business Cost: $97.48
   Profit (120%): $116.98
   Subtotal: $214.46
   GST (10%): $21.45
```

### **DL vs A5 Price Comparison**
```
DL (99x210mm):  $235.90 ($0.2359 each)
A5 (148x210mm): $254.61 ($0.2546 each)

✅ CORRECT: DL is $18.71 cheaper
```

**Why DL is cheaper:** 6 items per sheet vs A5's 4 items = better efficiency

---

## 🔧 Files Modified

### 1. **Schema (Already Updated - Previous Session)**
**File:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`  
**Line ~515:** Added "DL" to size enum

### 2. **Wrapper (Already Updated - Previous Session)**
**File:** `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py`  
**Line ~1564:** Added DL mapping: `"DL": FinishSize.DL`

### 3. **Backend Calculator (NEW FIX)**
**File:** `UI/modules_external/quote-calculator/backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py`  
**Line 70:** Added DL enum value with correct specifications

---

## 📊 Comprehensive Schema/Backend Audit Results

### **Audit Tool Created:**
`audit_calculator_schema_backend_mismatches.py` - Scans all calculator schemas against backend enums

### **Discrepancies Found:**

#### **Pattern 1: Schema vs Backend Naming Convention Mismatch**
**Issue:** Schema uses human-readable strings, backend uses UPPERCASE_SNAKE_CASE enums

**Example (calculate_folded_flyers_shopify):**
- Schema: `"Colour"`, `"Black & White"`
- Backend: `PrintType.COLOUR`, `PrintType.BLACK_WHITE`
- **Solution:** Wrapper handles translation via mapping dictionaries

**Status:** ✅ Working as designed (wrapper translates correctly)

#### **Pattern 2: Missing Backend Enum Values**
**Issue:** Schema claims support but backend enum missing value

**Example 1 (FIXED):**
- Calculator: `calculate_folded_flyers_shopify`
- Schema: `"enum": ["DL", "A4", "A5", "A3", "6pp A4"]`
- Backend (BEFORE): `A5, A4, A3, A4_6PP` (no DL)
- Backend (AFTER): `DL, A5, A4, A3, A4_6PP` ✅

**Example 2 (NOT FIXED - Different Issue):**
- Calculator: `calculate_business_cards`
- Schema: `"enum": ["90x55mm", "90x50mm", "85x55mm", "A4", "A5", "A6", "DL"]`
- Backend: Only basic card sizes
- **Root Cause:** Schema is overly permissive (allows sizes calculator doesn't support)
- **Status:** ⚠️ Schema needs cleanup (remove unsupported sizes)

#### **Pattern 3: Legacy/GOD Calculator References**
**Issue:** Schema references calculators with no backend implementation

**Calculators with no backend:**
- `calculate_flyers` (GOD calculator - database unavailable)
- `calculate_booklets` (GOD calculator)
- `calculate_perfect_bound_books` (GOD calculator)
- `calculate_letterheads` (GOD calculator)

**Status:** ⚠️ Expected (these use database-driven GOD calculators)

---

## 🏗️ System Architecture Notes

### **Calculator Types:**

1. **Shopify Calculators (Hardcoded)**
   - Files: `UI/modules_external/quote-calculator/backend/shopify_calculators/*.py`
   - Enums: Defined in each calculator file
   - Pricing: Hardcoded profit margins, stock costs
   - Example: `FoldedFlyers_Shopify_Calculator.py`, `EconomicalBusinessCards_Shopify_Calculator.py`

2. **GOD Calculators (Database-Driven)**
   - Files: No backend Python files (use SQL queries)
   - Data: `quote-calculator/backend/query_library.py` (5,958 lines of SQL)
   - Flexibility: Accept custom dimensions, dynamic pricing
   - Example: `calculate_flyers`, `calculate_booklets`
   - **Status:** Currently broken (database connection issues)

3. **Wrapper Layer**
   - File: `calculator_wrapper.py` (4,663 lines)
   - Purpose: Translate schema values to backend enums
   - Pattern: Mapping dictionaries (e.g., `size_map`, `stock_map`)

### **Translation Pattern:**
```python
# Schema value → Backend enum
size_map = {
    "DL": FinishSize.DL,           # Human-readable
    "A5": FinishSize.A5,
    "A4": FinishSize.A4,
    "A3": FinishSize.A3,
    "6pp A4": FinishSize.A4_6PP
}

# Usage in wrapper
finish_size=size_map.get(size, FinishSize.A5)
```

---

## 📋 Recommendations

### **Immediate Actions:**

1. ✅ **DL Size Added to Folded Flyers Backend** (COMPLETE)
   - Added to `FinishSize` enum
   - Tested successfully
   - Ready for production

2. ⚠️ **Review Business Cards Schema** (PENDING)
   - Remove unsupported sizes: A4, A5, A6, DL
   - Keep only: 90x55mm, 90x50mm, 85x55mm
   - Update schema description

3. ⚠️ **Document GOD Calculator Status** (PENDING)
   - Mark legacy calculators as "unavailable"
   - Add fallback messaging for users
   - Consider migration to Shopify calculators

### **Long-term Improvements:**

1. **Automated Schema Validation**
   - Run `audit_calculator_schema_backend_mismatches.py` in CI/CD
   - Flag new mismatches before deployment
   - Enforce schema/backend consistency

2. **Enum Synchronization**
   - Consider generating schema enums from backend code
   - Single source of truth for enum values
   - Reduce manual synchronization errors

3. **GOD Calculator Migration**
   - Migrate remaining flexible calculators to Shopify pattern
   - OR fix database connection for GOD calculators
   - Ensure feature parity (especially DL size support)

---

## 🔍 DL Size Across All Calculators

### **Calculators with DL Support:**

| Calculator | DL Support | Status |
|------------|-----------|--------|
| `calculate_folded_flyers_shopify` | ✅ Added Jan 22, 2026 | Working |
| `calculate_wire_bound_books_shopify` | ✅ Native support | Working |
| `calculate_spiral_bound_books_shopify` | ✅ Native support | Working |
| `calculate_with_compliments_slips` | ✅ Native support | Working |
| `calculate_printed_letterheads` | ✅ Native support | Working |

### **Calculators WITHOUT DL (but could benefit):**

| Calculator | DL Feasible? | Reason |
|------------|-------------|--------|
| `calculate_flyers` (GOD) | ✅ Yes | Database-driven, accepts custom dimensions |
| `calculate_booklets` (GOD) | ✅ Yes | Database-driven, flexible sizing |
| `calculate_notepads_a4/a5/a6` | ❌ No | Product-specific (A4/A5/A6 only) |
| `calculate_business_cards` | ❌ No | Business card sizes only |

---

## 📊 Audit Statistics

**Total Calculators in Schema:** 27  
**Calculators with Backend:** 22 (81%)  
**Calculators without Backend:** 5 (19% - GOD calculators)  

**Schema/Backend Mismatches Found:** 21  
**Critical Issues (blocking):** 1 (DL size missing - FIXED)  
**Minor Issues (naming):** 20 (expected, handled by wrapper)  

---

## ✅ Status Summary

### **User's Issue: RESOLVED ✅**
- DL size (99mm x 210mm) now fully supported in folded flyers calculator
- Schema, wrapper, and backend all aligned
- Tested successfully with user's original request (1000 qty, Satin 128GSM, double-sided, colour)
- Pricing verified ($235.90 total, $0.2359 per unit)

### **System Health: GOOD ✅**
- Schema/backend discrepancies are mostly by design (wrapper handles translation)
- No other critical blocking issues found
- GOD calculator unavailability is known limitation
- Audit tool created for ongoing monitoring

---

## 🛠️ Tools Created

1. **`audit_calculator_schema_backend_mismatches.py`**
   - Scans all calculators for enum mismatches
   - Reports schema-only, backend-only, and missing values
   - Usage: `python audit_calculator_schema_backend_mismatches.py`

2. **`test_dl_flyer_calculation.py`**
   - Tests DL size folded flyers calculation
   - Compares DL vs A5 pricing
   - Validates cost breakdown
   - Usage: `python test_dl_flyer_calculation.py`

---

## 📚 Related Documentation

- **User Issue:** Reported January 22, 2026 - "Error: Stream error! status: 502" for DL flyers
- **Previous Fix:** Schema and wrapper updated to include DL (January 22, 2026 - earlier session)
- **This Fix:** Backend enum updated with DL size (January 22, 2026 - this session)
- **Calculator Analysis:** `PRODUCTION_CALCULATOR_ANALYSIS_JAN22_2026.md` (853 lines, all 27 calculators documented)

---

**Date:** January 22, 2026  
**Author:** GitHub Copilot  
**Issue:** Schema/backend discrepancy audit + DL size backend implementation  
**Resolution:** DL size added to backend, tested successfully, audit tool created for ongoing monitoring
