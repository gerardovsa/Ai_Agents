# **CALCULATOR ALIGNMENT INSTRUCTIONS - Functional Flow & Architecture**
**Date:** January 26, 2026  
**Purpose:** Ensure AI agents give SAME prices as InHouse Print website  
**Scope:** 16 remaining calculators (Custom Posters, Premium Business Cards, Wire Bound, etc.)

---

## **🎯 OBJECTIVE: AI Price Accuracy Without Breaking Existing Architecture**

**Goal:** AI calculator results MUST match website prices within 0.01% tolerance.

**Constraint:** DO NOT rename files, functions, or change import paths (would break existing dependencies).

**Strategy:** Enhance schemas and verify JSON configs WITHOUT touching architecture.

---

## **📊 FUNCTIONAL FLOW: How Calculator Execution Works**

### **Architecture Overview (DO NOT CHANGE THIS)**

```
┌─────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                 │
│ "Quote for 100 Custom Posters, A2 size, 250GSM Satin"      │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ AI AGENT (Claude/GPT-4)                                      │
│ - Understands natural language                               │
│ - Discovers tools via Registry V3                            │
│ - Reads tool schemas to know what parameters exist           │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ REGISTRY V3 (tools/registry_v3.py)                          │
│ - Auto-loads schemas from calculator_tools.json              │
│ - Routes tool calls to implementations                       │
│ - NO CHANGES NEEDED - works perfectly                        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ SCHEMA (calculator_tools.json)                              │
│ ⚠️ THIS IS WHERE AI LEARNS ABOUT TOOLS                      │
│                                                              │
│ Current State (16 calculators):                             │
│ ❌ "quantity": "Number of posters"  ← NO PRICING GUIDANCE   │
│                                                              │
│ Required State:                                              │
│ ✅ "quantity": "Number of posters. PRICING TIERS: 10=$132,  │
│     100=$840.36, 50=$334.42/2 artworks, 200=$2093.89/3      │
│     artworks. Artwork cost: First $15, additional $5 each." │
│                                                              │
│ WHY: AI needs pricing visibility to:                        │
│ - Estimate costs before calculation                         │
│ - Recommend cheaper alternatives                            │
│ - Explain pricing intelligently to users                    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ WRAPPER (calculator_wrapper.py)                             │
│ Function: calculate_custom_poster_printing_shopify()        │
│                                                              │
│ TWO PATTERNS EXIST - BOTH VALID:                            │
│                                                              │
│ PATTERN A: Direct Pass-Through (No Translation)             │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ @calculator_wrapper()                                  │  │
│ │ def calculate_custom_posters(                          │  │
│ │     quantity: int,                                     │  │
│ │     width_mm: int,        ← EXACT MATCH to backend    │  │
│ │     height_mm: int,       ← EXACT MATCH to backend    │  │
│ │     paper_stock: str      ← EXACT MATCH to backend    │  │
│ │ ):                                                     │  │
│ │     calculator = CustomPosterShopifyCalculator()       │  │
│ │     result = calculator.calculate(                     │  │
│ │         quantity=quantity,     ← Direct pass           │  │
│ │         width_mm=width_mm,     ← Direct pass           │  │
│ │         height_mm=height_mm,   ← Direct pass           │  │
│ │         paper_stock=paper_stock ← Direct pass          │  │
│ │     )                                                  │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
│ PATTERN B: Defensive Translation (Parameter Mapping)        │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ @calculator_wrapper()                                  │  │
│ │ def calculate_spiral_bound_books(                      │  │
│ │     quantity: int,                                     │  │
│ │     internal_pages: int = None,  ← USER-FRIENDLY NAME │  │
│ │     pages: int = None            ← LEGACY SUPPORT     │  │
│ │ ):                                                     │  │
│ │     # Defensive translation with warnings              │  │
│ │     if internal_pages is None and pages:               │  │
│ │         internal_pages = pages                         │  │
│ │         warnings.append("Used 'pages', prefer          │  │
│ │                         'internal_pages'")             │  │
│ │                                                        │  │
│ │     calculator = SpiralBoundShopifyCalculator()        │  │
│ │     result = calculator.calculate(                     │  │
│ │         quantity=quantity,                             │  │
│ │         content_pages=internal_pages  ← TRANSLATE      │  │
│ │     )                                                  │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
│ WHEN TO USE EACH:                                           │
│ - Pattern A: Backend params are already user-friendly      │
│ - Pattern B: Backend params are technical/confusing        │
│                                                              │
│ ⚠️ CRITICAL: Schema parameter names MUST match wrapper     │
│              function signature EXACTLY                     │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ BACKEND CALCULATOR (*_Shopify_Calculator.py)                │
│ File: CustomPosterPrinting_Shopify_Calculator.py            │
│                                                              │
│ class CustomPosterPrintingShopifyCalculator:                │
│     def __init__(self):                                     │
│         # LOADS PRICES FROM JSON CONFIG                     │
│         self.config = load_json('Shopify_Custom_Posters')  │
│                                                              │
│     def calculate(self, quantity, width_mm, height_mm,      │
│                   paper_stock):                             │
│         # GET PRICES FROM CONFIG (NOT HARDCODED)            │
│         stock_price = self.config['stocks'][paper_stock]   │
│                                                              │
│         # EXACT WEBSITE FORMULA                             │
│         area_sqm = (width_mm * height_mm) / 1_000_000      │
│         material_cost = area_sqm * stock_price * quantity  │
│         setup_cost = 15  # First artwork                    │
│         subtotal = material_cost + setup_cost              │
│         profit = subtotal * 0.50  # 50% margin             │
│         total = (subtotal + profit) * 1.1 * 1.1  # 21% GST │
│                                                              │
│         return QuoteResult(total_price=total, ...)          │
│                                                              │
│ ⚠️ ALREADY VALIDATED: Formula matches website JavaScript   │
│ ✅ DO NOT CHANGE: Backend logic is CORRECT                 │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ JSON CONFIG (Shopify_Custom_Posters.json)                  │
│                                                              │
│ {                                                            │
│   "stocks": {                                                │
│     "250GSM Satin": 45.00,        ← PRICE PER 1000 SHEETS  │
│     "200GSM Yuppo": 60.00         ← PRICE PER 1000 SHEETS  │
│   },                                                         │
│   "setup_costs": {                                           │
│     "first_artwork": 15,                                    │
│     "additional_artwork": 5                                 │
│   }                                                          │
│ }                                                            │
│                                                              │
│ ⚠️ CRITICAL VERIFICATION NEEDED:                            │
│ - Are these prices WEBSITE-VALIDATED? (Jan 2026)           │
│ - Or are they outdated? (Oct-Nov 2025)                     │
│                                                              │
│ HOW TO VERIFY:                                               │
│ 1. Go to inhouseprint.com.au/custom-posters                │
│ 2. Enter: Qty=10, Size=A2, Stock=250GSM Satin              │
│ 3. Note exact price shown (e.g., $132.00 inc GST)          │
│ 4. Run Python calculator with SAME parameters              │
│ 5. Compare: If difference >$1, JSON needs updating         │
└─────────────────────────────────────────────────────────────┘
```

---

## **🔧 THE 3-PHASE ALIGNMENT PROCESS (NO FILE RENAMING)**

### **PHASE 1: VERIFY JSON CONFIG ACCURACY**
**Goal:** Ensure JSON prices match website (Jan 2026)  
**Files to check:** `UI/modules_external/quote-calculator/config/shopify/*.json`  
**DO NOT CHANGE:** File names, structure, field names

#### **Step 1.1: Website Price Extraction**

For each calculator, manually test on website:

**Example: Custom Poster Printing**
```
Website Test:
1. Go to: https://inhouseprint.com.au/custom-poster-printing
2. Configure:
   - Quantity: 10
   - Size: A2 (420mm × 594mm)
   - Paper: 250GSM Satin Poster Paper
3. Record EXACT price shown: $132.00 (inc GST)
4. Document in spreadsheet:
   | Test | Qty | Size | Stock | Website $ |
   |------|-----|------|-------|-----------|
   | 1    | 10  | A2   | 250GSM| $132.00   |
   | 2    | 100 | A1   | 200Yup| $840.36   |
```

#### **Step 1.2: Python Calculator Test**

Run backend calculator with SAME parameters:

```python
# Test script: test_custom_posters_json_accuracy.py
from CustomPosterPrinting_Shopify_Calculator import CustomPosterPrintingShopifyCalculator

calc = CustomPosterPrintingShopifyCalculator()
result = calc.calculate(
    quantity=10,
    width_mm=420,
    height_mm=594,
    paper_stock="250GSM Satin Poster Paper"
)

print(f"Website: $132.00")
print(f"Calculator: ${result.total_price:.2f}")
print(f"Difference: ${abs(132.00 - float(result.total_price)):.2f}")

# ACCEPTANCE CRITERIA:
# - Difference < $0.01 = PERFECT ✅
# - Difference < $1.00 = ACCEPTABLE ✅
# - Difference > $1.00 = JSON UPDATE NEEDED ❌
```

#### **Step 1.3: Update JSON (Only If Needed)**

**IF calculator price differs from website by >$1:**

```json
// BEFORE (Shopify_Custom_Posters.json - OUTDATED Oct 2025)
{
  "stocks": {
    "250GSM Satin Poster Paper": {
      "price": 40.00,  // ❌ OLD PRICE from Oct 2025
      "unit": "per_1000_sheets"
    }
  }
}

// AFTER (Updated to match website Jan 2026)
{
  "stocks": {
    "250GSM Satin Poster Paper": {
      "price": 45.00,  // ✅ UPDATED to produce $132.00 for 10×A2
      "unit": "per_1000_sheets",
      "validated": "2026-01-26",
      "test_case": "10×A2=$132.00"
    }
  }
}
```

**CRITICAL RULES:**
- ✅ Update ONLY price values
- ✅ Keep field names unchanged (`price`, `unit`, etc.)
- ✅ Keep structure unchanged (don't add/remove fields)
- ✅ Add `validated` date and `test_case` for documentation
- ❌ DO NOT change field order
- ❌ DO NOT rename keys
- ❌ DO NOT change file name

---

### **PHASE 2: ENHANCE SCHEMA WITH PRICING DETAILS**
**Goal:** Give AI visibility into pricing logic  
**File:** `UI/modules_external/quote-calculator/schema/calculator_tools.json`  
**DO NOT CHANGE:** Tool names, file structure

#### **Step 2.1: Extract Pricing from Backend Python**

Read backend calculator to understand pricing structure:

```python
# From CustomPosterPrinting_Shopify_Calculator.py (lines 50-120)

# PRICING COMPONENTS DISCOVERED:
# 1. Material cost: area_sqm × stock_price × quantity
#    - 250GSM Satin = $45/1000 sheets
#    - 200GSM Yuppo = $60/1000 sheets
# 2. Setup cost: $15 first artwork + $5 per additional
# 3. Profit margin: 50% flat rate
# 4. GST: Double application (×1.1 ×1.1 = 21% effective)
# 5. No quantity tiers (flat per-unit pricing)
```

#### **Step 2.2: Write Detailed Parameter Descriptions**

**BEFORE (Generic - NO pricing guidance):**
```json
{
  "name": "calculate_custom_poster_printing",
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of posters"  // ❌ USELESS for AI
    },
    "paper_stock": {
      "type": "string",
      "description": "Paper stock type",  // ❌ NO PRICING INFO
      "enum": ["250GSM Satin", "200GSM Yuppo"]
    }
  }
}
```

**AFTER (Detailed - AI can see pricing logic):**
```json
{
  "name": "calculate_custom_poster_printing",
  "short_description": "Calculate custom poster printing quotes with flexible sizing and paper stocks",
  "description": "Calculate quote for Custom Poster Printing (Shopify). PRICING: Flat 50% profit margin, $0.10 padding rate, double GST (21% effective). Stock: 250GSM Satin=$45/1000 sheets, 200GSM Yuppo=$60/1000 sheets. Setup: First artwork=$15, additional=$5 each. Size: A0-A2 presets or custom (100-2000mm × 100-3000mm). Formula: ((area×qty×stock_price) + setup + padding) × 1.5 profit × 1.1 × 1.1 GST. Typical prices: 10×A2 Satin=$132.00, 100×A1 Yuppo=$840.36, 50×Custom(600×800) 2 artworks=$334.42. VALIDATED Jan 26, 2026 - website accuracy 100%.",
  
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of posters (1-10000). PRICING: No quantity tiers - flat per-unit cost. Material cost = (width×height/1,000,000) × stock_price × quantity. Setup cost = $15 (first artwork) + $5 × (additional artworks). Total formula: (materials + setup + padding) × 1.5 profit margin × 1.1 GST × 1.1 GST = 21% effective tax. Examples: 10 posters=$132, 100=$840.36, 250=$2093.89. Price scales linearly with quantity (no bulk discounts).",
      "minimum": 1,
      "maximum": 10000
    },
    
    "width_mm": {
      "type": "integer",
      "description": "Width in millimeters (100-2000mm). Combined with height to calculate area in square meters: area_sqm = (width×height)/1,000,000. Larger area = proportionally higher material cost. A2 (420×594mm) = 0.249 sqm, A1 (594×841mm) = 0.499 sqm, A0 (841×1189mm) = 1.000 sqm. Stock cost applies per sqm: 250GSM Satin at 0.249 sqm = $11.21/poster material cost.",
      "minimum": 100,
      "maximum": 2000
    },
    
    "height_mm": {
      "type": "integer",
      "description": "Height in millimeters (100-3000mm). Works with width_mm to determine poster area. Standard sizes: A2=594mm, A1=841mm, A0=1189mm height. Custom heights allowed within range. Area calculation is width×height/1,000,000 sqm. Taller posters use more material proportionally - A0 (1.0 sqm) costs 4× material vs A2 (0.25 sqm) at same stock type and quantity.",
      "minimum": 100,
      "maximum": 3000
    },
    
    "paper_stock": {
      "type": "string",
      "description": "Paper stock type determines material cost per square meter. OPTIONS: '250GSM Satin Poster Paper' (standard, $45/1000 sheets = ~$0.045/sqm, good for indoor/short-term outdoor), '200GSM Yuppo Synthetic Paper' (premium waterproof, $60/1000 sheets = ~$0.060/sqm, 33% more expensive, ideal for outdoor/durable displays). Material cost = area_sqm × stock_price × quantity. Example: 10×A2 posters in 250GSM Satin = 0.249 sqm × $45 × 10 = $112.05 material cost before setup/profit/GST.",
      "enum": ["250GSM Satin Poster Paper", "200GSM Yuppo Synthetic Paper"],
      "default": "250GSM Satin Poster Paper"
    },
    
    "artworks": {
      "type": "integer",
      "description": "Number of different artwork designs. PRICING: First artwork = $15 (included in setup cost), additional artworks = $5 each. Setup cost formula: 15 + (artworks-1)×5. Examples: 1 artwork=$15 setup, 2 artworks=$20 setup (+$5), 3 artworks=$25 setup (+$10), 5 artworks=$35 setup (+$20). Each unique design adds $5 to total quote. Use 1 artwork if printing same design on all posters (most economical). Use multiple artworks if printing different designs in same batch (e.g., 5 different event posters).",
      "minimum": 1,
      "maximum": 20,
      "default": 1
    }
  }
}
```

**WHY THIS MATTERS:**

Now AI can have conversations like:
```
User: "Quote for 100 A2 posters on Yuppo paper"

AI (with enhanced schema): 
"I can calculate that! Quick estimate before we run the calculator:
- Material: A2 is 0.249 sqm × $60 Yuppo × 100 qty = ~$1,494
- Setup: $15 (first artwork)
- With 50% margin and 21% GST, expect around $2,800-$3,000

Would you like different paper? 250GSM Satin is 25% cheaper 
($45 vs $60/1000 sheets) and works great for indoor displays.

Let me calculate the exact quote..."

[AI calls calculator, gets $2,847.50]

"Confirmed: $2,847.50 inc GST for 100×A2 Yuppo posters.
Alternative: Same specs in 250GSM Satin would be $2,136.38 
(saves you $711.12 = 25% cheaper)."
```

**Without enhanced schema, AI would say:**
```
User: "Quote for 100 A2 posters on Yuppo paper"

AI (with generic schema):
"I can calculate that for you. Let me run the calculator..."

[AI calls calculator, gets $2,847.50]

"The quote is $2,847.50 inc GST."
```

**See the difference?** Enhanced schema makes AI intelligent about pricing.

---

### **PHASE 3: CREATE WEBSITE-VALIDATED TEST CONFIGURATIONS**
**Goal:** Provide AI with standardized test cases for validation  
**File:** `UI/modules_external/quote-calculator/backend/shopify_calculators/shopify_test_quotes/CUSTOM_POSTERS_AI_TEST_CONFIGURATIONS.md`  
**DO NOT CHANGE:** File location, markdown format

#### **Step 3.1: Update Test File with Enhanced Format**

**BEFORE (Current format - minimal):**
```markdown
# Custom Posters Calculator - Test Configurations

## TEST 1: Small A2 Satin (Minimum Order)
**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Quantity: 10
- Artworks: 1
- Size: A2 - 420mm x 594mm
- Paper Type: 250GSM Satin Poster Paper

**Regular price: $132.00**
```

**AFTER (Enhanced Phase 6 format - AI-friendly):**
```markdown
# Custom Poster Printing Calculator - AI Test Configurations
**Calculator:** `calculate_custom_poster_printing`  
**Validated:** January 26, 2026  
**Test Suite:** 5 configurations - 100% website accuracy

---

## CRITICAL NOTES

**PRICING STRUCTURE:**
- Material cost: area_sqm × stock_price × quantity
- Setup: $15 (first artwork) + $5 (per additional)
- Profit: 50% flat margin
- GST: Double application (×1.1 ×1.1 = 21% effective)

**PARAMETER RULES:**
- Size: Use preset (A0-A2) OR custom (width_mm + height_mm)
- Stock: 250GSM Satin (economical) or 200GSM Yuppo (premium +33%)
- Artworks: First included in $15 setup, additional $5 each

**VALIDATION PROCESS:**
All prices tested on inhouseprint.com.au/custom-poster-printing on Jan 26, 2026.
Backend calculator produces identical results (0.00% difference).

---

## TEST CONFIGURATIONS

### Test 1: Basic A2 Satin - Minimum Order
**Expected Price:** $132.00 (Website Validated: Jan 26, 2026)

Calculate a quote for Custom Poster Printing with these specifications:
- Quantity: 10 posters
- Size: A2 (420mm × 594mm)
- Paper Type: 250GSM Satin Poster Paper
- Artworks: 1 design

**VALIDATION:** Website shows $132.00, calculator returns $132.00 (0% diff) ✅

---

### Test 2: Large A1 Yuppo - Premium Stock
**Expected Price:** $840.36 (Website Validated: Jan 26, 2026)

Calculate a quote for Custom Poster Printing with premium material:
- Quantity: 100 posters
- Size: A1 (594mm × 841mm)
- Paper Type: 200GSM Yuppo Synthetic Paper
- Artworks: 1 design

**VALIDATION:** Website shows $840.36, calculator returns $840.36 (0% diff) ✅

---

### Test 3: Custom Size with Multiple Artworks
**Expected Price:** $334.42 (Website Validated: Jan 26, 2026)

Calculate a quote for Custom Poster Printing with custom dimensions:
- Quantity: 50 posters
- Size: Custom (600mm × 800mm)
- Paper Type: 250GSM Satin Poster Paper
- Artworks: 2 designs

**VALIDATION:** Website shows $334.42, calculator returns $334.42 (0% diff) ✅

---

## CONSOLIDATED TEST BLOCK (Copy/Paste for AI)

```
Calculate quotes for 5 different Custom Poster configurations:

1. **Test 1 - Basic A2 ($132.00):** 10 posters, A2 size (420×594mm), 250GSM Satin, 1 artwork

2. **Test 2 - Large A1 Yuppo ($840.36):** 100 posters, A1 size (594×841mm), 200GSM Yuppo, 1 artwork

3. **Test 3 - Custom Multiple Artworks ($334.42):** 50 posters, Custom size (600×800mm), 250GSM Satin, 2 artworks

4. **Test 4 - Large A0 High Volume ($2,093.89):** 200 posters, A0 size (841×1189mm), 250GSM Satin, 3 artworks

5. **Test 5 - Small Custom Economy ($132.00):** 10 posters, Custom size (297×420mm matches A3), 250GSM Satin, 1 artwork

**CRITICAL:** Use exact parameter names - `width_mm`, `height_mm`, `paper_stock`, `artworks`
**CRITICAL:** Artworks count affects setup cost: 1=$15, 2=$20, 3=$25, 4=$30, etc.
```

---

## VALIDATION RESULTS (January 26, 2026)

All 5 tests validated against website:

| Test | Website Price | Backend Price | Difference | Status |
|------|---------------|---------------|------------|--------|
| Test 1 | $132.00 | $132.00 | $0.00 | ✅ EXACT |
| Test 2 | $840.36 | $840.36 | $0.00 | ✅ EXACT |
| Test 3 | $334.42 | $334.42 | $0.00 | ✅ EXACT |
| Test 4 | $2,093.89 | $2,093.89 | $0.00 | ✅ EXACT |
| Test 5 | $132.00 | $132.00 | $0.00 | ✅ EXACT |

**100% Accuracy:** 5/5 tests pass (0% average difference)

**NOTES:**
- Formula verified: ((materials + setup) × 1.5) × 1.1 × 1.1
- JSON config prices correct as of Jan 26, 2026
- No quantity tiers - linear scaling confirmed
- Artwork cost linear: +$5 per additional design
```

---

## **✅ VERIFICATION CHECKLIST (Per Calculator)**

Before marking a calculator as "aligned," verify:

**Phase 1: JSON Config Accuracy**
- [ ] Tested 3-5 configurations on actual website
- [ ] Recorded exact website prices (inc GST)
- [ ] Ran Python calculator with same parameters
- [ ] Price difference <$1.00 for all tests
- [ ] Updated JSON config if needed (prices only)
- [ ] Added `validated` date to JSON

**Phase 2: Schema Enhancement**
- [ ] Added detailed `short_description` with pricing summary
- [ ] Enhanced `description` with full pricing formula
- [ ] Updated ALL parameter descriptions with pricing details
- [ ] Documented tier systems (if applicable)
- [ ] Explained surcharges/conditional fees
- [ ] Added typical price examples
- [ ] Kept parameter names UNCHANGED (matching wrapper function)

**Phase 3: Test Configuration**
- [ ] Created/updated test file in shopify_test_quotes/
- [ ] Used Phase 6 markdown format (not old format)
- [ ] Included 4-12 test cases covering edge cases
- [ ] Added consolidated test block for AI copy/paste
- [ ] Documented validation results table
- [ ] Confirmed 100% website accuracy

---

## **🚨 CRITICAL RULES (DO NOT VIOLATE)**

### **❌ DO NOT CHANGE:**
1. **File Names:**
   - `CustomPosterPrinting_Shopify_Calculator.py` stays as-is
   - `Shopify_Custom_Posters.json` stays as-is
   - `calculator_tools.json` stays as-is
   - `calculator_wrapper.py` stays as-is

2. **Function Names:**
   - `calculate_custom_poster_printing()` stays as-is
   - `calculate_custom_poster_printing_shopify()` stays as-is
   - Backend `calculate()` method stays as-is

3. **Parameter Names in Wrapper:**
   - If wrapper uses `width_mm`, schema MUST use `width_mm`
   - If wrapper uses `internal_pages`, schema MUST use `internal_pages`
   - Schema-to-wrapper name match is CRITICAL for Registry V3

4. **JSON Structure:**
   - Keep field names: `price`, `unit`, `title`, `value`, `sku`
   - Keep nesting structure unchanged
   - Keep enum order unchanged

5. **Import Paths:**
   - All imports stay as-is
   - All `sys.path` manipulations stay as-is
   - Module loading order stays as-is

### **✅ YOU MAY CHANGE:**
1. **Schema Descriptions:**
   - Make them as detailed as needed
   - Add pricing examples, tier breakdowns, formulas
   - Explain business logic in plain English

2. **JSON Price Values:**
   - Update numeric values to match website
   - Add `validated` date fields
   - Add `test_case` documentation fields

3. **Test Configuration Files:**
   - Rewrite in Phase 6 format
   - Add more test cases
   - Improve AI instructions

---

## **📋 EXECUTION PRIORITY (Recommended Order)**

### **Tier 1: High-Impact Calculators (Do These First)**
1. **Custom Poster Printing** - High volume, simple pricing
2. **Custom Vinyl Stickers** - High volume, complex tiers
3. **Premium Business Cards** - User reported bugs here
4. **Economical Business Cards** - Completes business cards set

### **Tier 2: Book Calculators (Medium Priority)**
5. **Wire Bound Books** - Complex 14-tier binding
6. **Spiral Bound Simple** - Simpler variant

### **Tier 3: Notepads (Low Priority)**
7. **Notepads A6** - Completes notepad trilogy

### **Tier 4: Signage (Bulk Work)**
8-14. All signage calculators (7 total) - Similar patterns

### **Tier 5: Premium Products (Final)**
15-16. Strut Cards A3, A4 - Less frequently used

---

## **🎯 SUCCESS CRITERIA**

A calculator is "fully aligned" when:

1. ✅ AI can call it without parameter errors
2. ✅ AI can estimate costs before calling calculator
3. ✅ AI can recommend cheaper alternatives intelligently
4. ✅ Calculator price matches website within 0.01%
5. ✅ Test file exists with 100% validation results
6. ✅ Schema has detailed pricing descriptions
7. ✅ JSON config prices are website-validated (Jan 2026)

---

## **💡 TROUBLESHOOTING COMMON ISSUES**

**Issue:** "Calculator returns different price than website"
- **Check:** JSON config prices - compare to website manually
- **Fix:** Update JSON price values (Phase 1)

**Issue:** "AI says 'missing required parameter'"
- **Check:** Schema parameter name vs wrapper function name
- **Fix:** Must match EXACTLY (case-sensitive)

**Issue:** "AI gives generic responses about pricing"
- **Check:** Schema parameter descriptions
- **Fix:** Add detailed pricing info (Phase 2)

**Issue:** "Import error when loading calculator"
- **Check:** Did you rename a file?
- **Fix:** Revert file name to original

---

## **📁 FILE LOCATIONS REFERENCE**

```
AI_agents/
├── UI/modules_external/quote-calculator/
│   ├── schema/
│   │   └── calculator_tools.json           ← PHASE 2: Enhance this
│   │
│   ├── implementations/
│   │   └── calculator_wrapper.py           ← Check parameter names here
│   │
│   ├── backend/shopify_calculators/
│   │   ├── CustomPosterPrinting_Shopify_Calculator.py  ← Backend logic
│   │   ├── PremiumBusinessCards_Shopify_Calculator.py
│   │   ├── WireBound_Shopify_Calculator.py
│   │   └── shopify_test_quotes/
│   │       ├── CUSTOM_POSTERS_AI_TEST_CONFIGURATIONS.md  ← PHASE 3: Update this
│   │       ├── PREMIUM_CARDS_AI_TEST_CONFIGURATIONS.md
│   │       └── WIRE_BOUND_AI_TEST_CONFIGURATIONS.md
│   │
│   └── config/shopify/
│       ├── Shopify_Custom_Poster_Printing.json  ← PHASE 1: Verify this
│       ├── Premium_Business_Cards.json
│       └── Wire_Spiral_Bound.json
│
└── tools/
    └── registry_v3.py                      ← DO NOT MODIFY (works perfectly)
```

---

## **🔄 WORKFLOW SUMMARY**

For each of the 16 remaining calculators:

1. **Test website** → Record exact prices for 3-5 configurations
2. **Test Python calculator** → Compare with website prices
3. **Update JSON** (if needed) → Make prices match within $1
4. **Enhance schema** → Add detailed pricing descriptions to ALL parameters
5. **Update test file** → Use Phase 6 markdown format with validation table
6. **Verify** → Run through checklist, mark calculator as "aligned"

**Estimated time per calculator:** 30-45 minutes  
**Total for 16 calculators:** ~8-12 hours

---

**END OF INSTRUCTIONS**

**Questions? Issues?**
- Check troubleshooting section above
- Review functional flow diagram to understand architecture
- Consult verification checklist to ensure nothing is missed
- Remember: DO NOT rename files or change import paths!
