# 🚀 Shopify Calculator Implementation Roadmap

**Date:** December 10, 2024  
**Status:** 9/26 calculators complete (35%)  
**Remaining:** 17 calculators need implementation  

---

## 🎯 Current Status

### ✅ Fully Implemented & Integrated (9)
1. Wire Bound Books
2. Spiral Bound Books  
3. Perfect Bound Books
4. Saddle Stitch Books
5. Folded Flyers
6. Economical Business Cards
7. Premium Business Cards
8. Saddle Stitch Books (wrapper complete)
9. All wrappers tested and documented

### ❌ Need Implementation (17)

All remaining calculators have:
- ✅ Template structure created
- ✅ Result dataclass defined
- ✅ Profit margin tiers defined
- ✅ Padding rate methods defined
- ❌ **`calculate()` method implementation** ← MISSING!

---

## 📋 Implementation Priority Order

### **PRIORITY 1: Stationery (5 calculators) - High Business Value**

#### 1. Printed Letterheads
- **File:** `PrintedLetterheads_Shopify_Calculator.py`
- **Config:** `Shopify_Printed_Letterheads.json`
- **Complexity:** ⭐⭐ (Low-Medium)
- **Business Impact:** HIGH - Common office stationery
- **Parameters:** Quantity, stock, print sides, color
- **Estimated Time:** 2-3 hours

#### 2. With Compliments Slips  
- **File:** `WithComplimentsSlips_Shopify_Calculator.py`
- **Config:** `Shopify_With_Compliments_Slips.json`
- **Complexity:** ⭐⭐ (Low-Medium)
- **Business Impact:** MEDIUM - Often ordered with letterheads
- **Parameters:** Similar to letterheads, smaller size
- **Estimated Time:** 2-3 hours

#### 3. Notepads A4
- **File:** `NotepadsA4_Shopify_Calculator.py`
- **Config:** `Shopify_Notepads_A4.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** HIGH - Popular office product
- **Parameters:** Quantity, sheets per pad, backing type
- **Estimated Time:** 3-4 hours

#### 4. Notepads A6
- **File:** `NotepadsA6_Shopify_Calculator.py`
- **Config:** `Shopify_Notepads_A6.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** MEDIUM
- **Parameters:** Similar to A4, smaller size
- **Estimated Time:** 2-3 hours (copy from A4)

#### 5. Notepads A5
- **File:** `NotepadsA5_Shopify_Calculator.py`
- **Config:** `Shopify_Notepads_A5.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** MEDIUM
- **Parameters:** Similar to A4/A6
- **Estimated Time:** 2-3 hours

**Total Priority 1:** 12-16 hours

---

### **PRIORITY 2: Signs (7 calculators) - Large Format Products**

#### 6. Election Signs
- **File:** `ElectionSigns_Shopify_Calculator.py`
- **Config:** `Shopify_Election_Signs.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** MEDIUM - Seasonal demand
- **Estimated Time:** 3-4 hours

#### 7. Construction Signs
- **File:** `ConstructionSigns_Shopify_Calculator.py`
- **Config:** `Shopify_Construction_Signs.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** MEDIUM
- **Estimated Time:** 3-4 hours

#### 8. Bollard Signs
- **File:** `BollardSigns_Shopify_Calculator.py`
- **Config:** `Shopify_Bollard_Signs.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** LOW-MEDIUM
- **Estimated Time:** 3-4 hours

#### 9. Corflute Insert A-Frame
- **File:** `CorfluteInsertA-Frame_Shopify_Calculator.py`
- **Config:** `Shopify_Corflute_Insert_A-Frame.json`
- **Complexity:** ⭐⭐⭐⭐ (Medium-High)
- **Business Impact:** MEDIUM
- **Estimated Time:** 4-5 hours

#### 10. Metal Face A-Frame
- **File:** `MetalFaceA-Frame_Shopify_Calculator.py`
- **Config:** `Shopify_Metal_Face_A-Frame.json`
- **Complexity:** ⭐⭐⭐⭐ (Medium-High)
- **Business Impact:** MEDIUM
- **Estimated Time:** 4-5 hours

#### 11. Strut Cards A4
- **File:** `StrutCardsA4_Shopify_Calculator.py`
- **Config:** `Shopify_Strut_Cards_A4.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** LOW-MEDIUM
- **Estimated Time:** 3-4 hours

#### 12. Strut Cards A3
- **File:** `StrutCardsA3_Shopify_Calculator.py`
- **Config:** `Shopify_Strut_Cards_A3.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** LOW-MEDIUM
- **Estimated Time:** 3-4 hours

**Total Priority 2:** 23-30 hours

---

### **PRIORITY 3: Promotional (6 calculators) - Specialty Products**

#### 13. Custom Poster Printing
- **File:** `CustomPosterPrinting_Shopify_Calculator.py`
- **Config:** `Shopify_Custom_Poster_Printing.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** MEDIUM
- **Estimated Time:** 3-4 hours

#### 14. Custom Vinyl Stickers
- **File:** `CustomVinylStickers_Shopify_Calculator.py`
- **Config:** `Shopify_Custom_Vinyl_Stickers.json`
- **Complexity:** ⭐⭐⭐⭐ (Medium-High)
- **Business Impact:** HIGH - Popular promotional item
- **Estimated Time:** 4-5 hours

#### 15. Premium Bookmarks
- **File:** `PremiumBookmarks_Shopify_Calculator.py`
- **Config:** `Shopify_Premium_Bookmarks.json`
- **Complexity:** ⭐⭐⭐ (Medium)
- **Business Impact:** LOW-MEDIUM
- **Estimated Time:** 3-4 hours

#### 16. Selfie Frames
- **File:** `SelfieFrames_Shopify_Calculator.py`
- **Config:** `Shopify_Selfie_Frames.json`
- **Complexity:** ⭐⭐⭐⭐ (Medium-High)
- **Business Impact:** MEDIUM - Event/promotional
- **Estimated Time:** 4-5 hours

#### 17. Luxury Classic Pull Up Banners
- **File:** `LuxuryClassicPullUpBanners_Shopify_Calculator.py`
- **Config:** `Shopify_Luxury_Classic_Pull_Up_Banners.json`
- **Complexity:** ⭐⭐⭐⭐⭐ (High)
- **Business Impact:** HIGH - Trade show essential
- **Estimated Time:** 5-6 hours

#### 18. Stackable Cubes
- **File:** `StackableCubes_Shopify_Calculator.py`
- **Config:** `Shopify_Stackable_Cubes.json`
- **Complexity:** ⭐⭐⭐⭐⭐ (High)
- **Business Impact:** MEDIUM - Display furniture
- **Estimated Time:** 5-6 hours

**Total Priority 3:** 24-30 hours

---

## 🛠️ Implementation Template

### Standard Calculator Structure

Every calculator follows this pattern:

```python
def calculate(self, **kwargs) -> CalculatorQuoteResult:
    """
    Calculate quote for [Product Name]
    
    Args:
        **kwargs: Parameters from JSON config or direct calls
    
    Returns:
        CalculatorQuoteResult with pricing breakdown
    """
    
    # ========================================================================
    # STEP 1: EXTRACT & VALIDATE PARAMETERS
    # ========================================================================
    quantity = kwargs.get('quantity')
    param2 = kwargs.get('param2')
    # ... validate all required params
    
    # ========================================================================
    # STEP 2: LOAD CONFIG VALUES (from JSON if needed)
    # ========================================================================
    if self.config:
        setup_costs = self.config.get('setup_costs', {})
        # ... load other config values
    
    # ========================================================================
    # STEP 3: CALCULATE MATERIAL COSTS
    # ========================================================================
    # Stock cost per sheet/item
    stock_cost_per_1000 = Decimal('126.00')
    sheets_needed = (Decimal(quantity) / cards_per_sheet) * Decimal('1.05')
    stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000
    
    # Click charges (printing cost)
    sides = 2 if double_sided else 1
    click_cost = sheets_needed * Decimal('0.048') * sides
    
    # Cutting/finishing costs
    cutting_cost = sheets_needed * Decimal('0.05')
    
    # ========================================================================
    # STEP 4: CALCULATE SETUP COSTS
    # ========================================================================
    impos_setup = Decimal('15.00')
    guilo_setup = Decimal('12.00')
    cello_setup = Decimal('17.00') if has_celloglaze else Decimal('0')
    
    setup_costs = impos_setup + guilo_setup + cello_setup
    
    # ========================================================================
    # STEP 5: CALCULATE TOTAL BUSINESS COST
    # ========================================================================
    material_costs = stock_cost + click_cost + cutting_cost
    biz_cost = setup_costs + material_costs
    
    # ========================================================================
    # STEP 6: APPLY PROFIT MARGIN (using existing tier method)
    # ========================================================================
    profit_rate = self._get_profit_margin(float(biz_cost))
    profit_amount = biz_cost * profit_rate
    
    # ========================================================================
    # STEP 7: CALCULATE SUBTOTAL
    # ========================================================================
    subtotal = biz_cost + profit_amount
    
    # ========================================================================
    # STEP 8: APPLY GST
    # ========================================================================
    # Standard: single GST application
    total_with_gst = subtotal * Decimal('1.1')
    gst_amount = subtotal * Decimal('0.1')
    
    # Premium/Special: dual GST (Shopify quirk)
    # first_gst = subtotal * Decimal('1.1')
    # total_with_gst = first_gst * Decimal('1.1')
    # gst_amount = total_with_gst - subtotal
    
    # ========================================================================
    # STEP 9: CALCULATE PER-UNIT COSTS
    # ========================================================================
    unit_price = total_with_gst / Decimal(quantity)
    cost_per_item = biz_cost / Decimal(quantity)
    
    # ========================================================================
    # STEP 10: BUILD BREAKDOWN & SPECIFICATIONS
    # ========================================================================
    breakdown = {
        'setup_costs': float(setup_costs),
        'stock_cost': float(stock_cost),
        'click_cost': float(click_cost),
        'cutting_cost': float(cutting_cost),
        'material_costs': float(material_costs),
        'biz_cost': float(biz_cost),
        'profit_margin_rate': float(profit_rate),
        'profit_amount': float(profit_amount),
        'subtotal': float(subtotal),
        'gst_amount': float(gst_amount),
        'total_price': float(total_with_gst)
    }
    
    specifications = {
        'quantity': quantity,
        'param2': param2,
        # ... all parameters used
    }
    
    # ========================================================================
    # STEP 11: RETURN RESULT
    # ========================================================================
    return CalculatorQuoteResult(
        total_price=total_with_gst,
        unit_price=unit_price,
        cost_per_item=cost_per_item,
        quantity=quantity,
        breakdown=breakdown,
        specifications=specifications
    )
```

---

## 📊 Implementation Timeline

### **Sprint 1: Stationery (Week 1)**
- Days 1-2: Printed Letterheads + With Compliments
- Days 3-4: Notepads A4 + A6
- Day 5: Notepads A5 + Testing
- **Output:** 5 calculators + wrappers + tests

### **Sprint 2: Signs (Week 2)**  
- Days 1-2: Election Signs + Construction Signs
- Days 3-4: Bollard Signs + Corflute A-Frame
- Day 5: Metal A-Frame + Testing
- **Output:** 5 calculators

### **Sprint 3: Signs & Promotional (Week 3)**
- Days 1-2: Strut Cards A4/A3
- Days 3-4: Custom Posters + Vinyl Stickers
- Day 5: Premium Bookmarks + Testing
- **Output:** 5 calculators

### **Sprint 4: Promotional Complete (Week 4)**
- Days 1-2: Selfie Frames
- Days 3-4: Pull Up Banners + Stackable Cubes
- Day 5: Final testing + documentation
- **Output:** 3 calculators + complete system

**Total Time:** 4 weeks (59-76 hours)

---

## 🔍 Reference Implementations

Study these working calculators as templates:

### **Simple Structure (150-400 lines)**
- `EconomicalBusinessCards_Shopify_Calculator.py` (387 lines)
  - Good for: Letterheads, Compliments, simple products
  - Features: Basic stock/print/quantity calculations

### **Medium Complexity (400-500 lines)**
- `PremiumBusinessCards_Shopify_Calculator.py` (477 lines)
  - Good for: Products with finishes (celloglaze, lamination)
  - Features: Dual GST, premium options

### **Complex Structure (600+ lines)**
- `FoldedFlyers_Shopify_Calculator.py` (635 lines)
  - Good for: Products with multiple size/fold options
  - Features: Complex validation, multiple configurations
  
- `PerfectBound_Shopify_Calculator.py` (large)
  - Good for: Multi-component products (cover + inner)
  - Features: Page calculations, binding costs

---

## 🎯 Success Criteria Per Calculator

- ✅ `calculate()` method implemented (no NotImplementedError)
- ✅ All parameters validated
- ✅ Profit margins applied correctly
- ✅ GST calculated (single or dual as appropriate)
- ✅ Breakdown dictionary complete
- ✅ Specifications dictionary complete
- ✅ Test case passing with real quote
- ✅ Wrapper function created
- ✅ Requirements documentation added
- ✅ Natural language triggers defined

---

## 📚 Required Information Per Calculator

Before implementing, gather:

1. **Product Specifications**
   - Sizes available (A4, A5, DL, custom)
   - Stocks supported (GSM, finishes)
   - Quantity ranges (min/max)

2. **Pricing Components**
   - Setup costs (imposition, guillotine, etc.)
   - Stock cost per 1000 sheets
   - Click charges (per sheet per side)
   - Finishing costs (cutting, folding, binding)
   - Special costs (lamination, celloglaze, frames)

3. **Business Rules**
   - Profit margin tiers (already defined in templates)
   - GST application (single or dual)
   - Validation rules
   - Common configurations

4. **JSON Config Structure**
   - Check if JSON file exists
   - Understand field mappings (F1-F14)
   - Validate against JavaScript original

---

## 🚀 Getting Started

### Step 1: Choose Calculator
Pick from Priority 1 list (highest business value)

### Step 2: Analyze Reference
Find similar working calculator, study its structure

### Step 3: Check JSON Config
Verify JSON config file exists and understand its structure

### Step 4: Implement `calculate()`
Follow 11-step template above

### Step 5: Test Immediately
Create test case, verify quote is reasonable

### Step 6: Create Wrapper
Add to `shopify_calculator_wrappers.py`

### Step 7: Document
Add requirements block to `complete_calculator_implementation.py`

### Step 8: Test Wrapper
Add test to test file, verify end-to-end

---

## 📈 Progress Tracking

Update this section as calculators are completed:

- [ ] Printed Letterheads
- [ ] With Compliments Slips
- [ ] Notepads A4
- [ ] Notepads A6
- [ ] Notepads A5
- [ ] Election Signs
- [ ] Construction Signs
- [ ] Bollard Signs
- [ ] Corflute Insert A-Frame
- [ ] Metal Face A-Frame
- [ ] Strut Cards A4
- [ ] Strut Cards A3
- [ ] Custom Poster Printing
- [ ] Custom Vinyl Stickers
- [ ] Premium Bookmarks
- [ ] Selfie Frames
- [ ] Luxury Classic Pull Up Banners
- [ ] Stackable Cubes

**Current: 9/26 (35%)**  
**Target: 26/26 (100%)**

---

*Roadmap Created: December 10, 2024*  
*Total Remaining Effort: 59-76 hours (4 weeks)*
