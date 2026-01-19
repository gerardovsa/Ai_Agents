# Quick Start: Group 3 Calculator Alignment
**Target:** 5 calculators in Group 3 (Notepads & Printing)  
**Priority:** MEDIUM - Simpler products, backend uses **kwargs  
**Time Estimate:** 3-5 hours

---

## 🎯 YOUR MISSION

Fix parameter alignment for 5 calculators:
1. `calculate_notepads_a4_shopify`
2. `calculate_notepads_a5_shopify`
3. `calculate_notepads_a6_shopify`
4. `calculate_custom_poster_printing_shopify`
5. `calculate_custom_vinyl_stickers_shopify`

---

## 📁 FILES YOU'LL MODIFY

```
UI/modules_external/quote-calculator/
├── implementations/
│   └── calculator_wrapper.py (Lines 1823-2071)
│
└── backend/shopify_calculators/
    ├── NotepadsA4_Shopify_Calculator.py
    ├── NotepadsA5_Shopify_Calculator.py
    ├── NotepadsA6_Shopify_Calculator.py
    ├── CustomPosterPrinting_Shopify_Calculator.py
    └── CustomVinylStickers_Shopify_Calculator.py

schema/calculator_tools.json (Lines 1142-1450)

tests/calculators/alignment/
├── test_calculator_notepads_a4_alignment.py (CREATE)
├── test_calculator_notepads_a5_alignment.py (CREATE)
├── test_calculator_notepads_a6_alignment.py (CREATE)
├── test_calculator_custom_poster_alignment.py (CREATE)
└── test_calculator_custom_vinyl_stickers_alignment.py (CREATE)
```

---

## ⚡ CALCULATOR 1: NOTEPADS A4

### **Backend Signature:**
```python
# File: backend/shopify_calculators/NotepadsA4_Shopify_Calculator.py
def calculate(self, **kwargs) -> NotepadsA4ShopifyCalculatorQuoteResult:
    """
    Calculate Notepads A4 Shopify quote
    
    Backend extracts these parameters:
        quantity: int(kwargs.get('quantity', kwargs.get('qty', 250)))
        print_sides: kwargs.get('print_sides', 'Single side print')
        print_type: kwargs.get('print_type', 'Colour')
        paper_stock: kwargs.get('paper_stock', 'Standard')
        artworks: int(kwargs.get('artworks', 1))
        pads_per_book: int(kwargs.get('pads_per_book', 1))  # UNUSED IN CALCULATION
    """
```

### **Current Schema (Line 1142):**
```json
{
  "name": "calculate_notepads_a4",
  "parameters": {
    "quantity": {
      "type": "string",  // ❌ Should be integer
      "enum": ["25", "50", "75", "100", "150", "200", "250", "300", "400", "500", "750", "1000", "2000"]
    },
    "artworks": {
      "type": "integer"  // ✅ CORRECT
    },
    "leaves_per_pad": {  // ❌ Backend expects 'pads_per_book' (but doesn't use it)
      "type": "string",
      "enum": ["25", "50", "100"]
    },
    "finish_size": {  // ❌ NOT IN BACKEND
      "type": "string",
      "enum": ["A4 Portrait"]
    },
    "print_type": {
      "type": "string",
      "enum": [
        "Colour 1 sided",      // ❌ Backend expects "Colour" + "Single side print"
        "Colour 2 sided",      // ❌ Backend expects "Colour" + "Double side print"
        "Black & White 1 sided",
        "Black & White 2 sided"
      ]
    },
    "stock_type": {  // ❌ Backend expects 'paper_stock'
      "type": "string"
    }
  }
}
```

### **Current Wrapper (Line 2006):**
```python
def calculate_notepads_a4(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Notepads A4"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator
        calculator = NotepadsA4ShopifyCalculator()
        result = calculator.calculate(**kwargs)  # ❌ Passes everything blindly
        return {
            "success": True,
            "product_type": "Notepads A4",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Notepads A4] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}
```

### **Issues Found:**

#### ❌ Schema Issues:
1. `quantity` type is "string" → Should be "integer"
2. `leaves_per_pad` → Backend doesn't use this (expects `pads_per_book` but ignores it)
3. `finish_size` → Backend doesn't use this at all
4. `print_type` combines color + sides → Backend expects separate `print_type` and `print_sides`
5. `stock_type` → Backend expects `paper_stock`

#### ❌ Wrapper Issues:
1. Uses `**kwargs` blindly - no parameter validation
2. No translation layer for mismatched parameter names
3. No type conversion (string quantity → integer)
4. No parameter splitting (print_type → print_type + print_sides)

### **FIX SCHEMA:**
```json
{
  "name": "calculate_notepads_a4",
  "parameters": {
    "quantity": {
      "type": "integer",
      "enum": [25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000],
      "required": true,
      "description": "Number of notepads to print"
    },
    "print_type": {
      "type": "string",
      "enum": ["Colour", "Black & White"],
      "required": false,
      "description": "Print color mode"
    },
    "print_sides": {
      "type": "string",
      "enum": ["Single side print", "Double side print"],
      "required": false,
      "description": "Print on one or both sides"
    },
    "paper_stock": {
      "type": "string",
      "enum": ["Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM", "Standard"],
      "required": false,
      "description": "Paper weight and type"
    },
    "artworks": {
      "type": "integer",
      "required": false,
      "description": "Number of unique artwork designs (1-50)"
    },
    
    // ⚠️ LEGACY PARAMETERS (for backwards compatibility)
    "stock_type": {
      "type": "string",
      "description": "DEPRECATED: Use 'paper_stock' instead",
      "required": false
    },
    "leaves_per_pad": {
      "type": "string",
      "description": "DEPRECATED: Not used by backend",
      "required": false
    }
  }
}
```

### **FIX WRAPPER:**
```python
@calculator_wrapper(quantity_enum=[25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000], validate_params=True)
def calculate_notepads_a4(
    quantity: int,
    print_type: str = "Colour",
    print_sides: str = "Single side print",
    paper_stock: str = "Standard",
    artworks: int = 1,
    
    # ⚠️ LEGACY PARAMETERS (backwards compatibility)
    stock_type: str = None,
    leaves_per_pad: str = None,
    finish_size: str = None
    
    # ❌ NO **kwargs!
) -> Dict[str, Any]:
    """
    Shopify calculator for Notepads A4
    
    ✅ CURRENT PARAMETERS:
        quantity: Number of notepads (25-2000)
        print_type: "Colour" or "Black & White"
        print_sides: "Single side print" or "Double side print"
        paper_stock: "Uncoated Bond 80GSM", "90GSM", "100GSM", or "Standard"
        artworks: Number of designs (1-50)
    
    ⚠️ DEPRECATED PARAMETERS:
        stock_type → use paper_stock instead
        leaves_per_pad → not used by backend
        finish_size → not used by backend
    """
    
    # Legacy translation with warnings
    warnings = []
    
    if stock_type is not None:
        paper_stock = stock_type
        warnings.append({
            "deprecated": "stock_type",
            "use_instead": "paper_stock",
            "value_sent": stock_type,
            "translated_to": paper_stock
        })
    
    if leaves_per_pad is not None:
        warnings.append({
            "deprecated": "leaves_per_pad",
            "message": "Parameter not used by backend - ignored"
        })
    
    if finish_size is not None:
        warnings.append({
            "deprecated": "finish_size",
            "message": "Parameter not used by backend - ignored"
        })
    
    # Call backend with correct parameters
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator
        calculator = NotepadsA4ShopifyCalculator()
        
        # Build backend parameters
        backend_params = {
            'quantity': quantity,
            'print_type': print_type,
            'print_sides': print_sides,
            'paper_stock': paper_stock,
            'artworks': artworks
        }
        
        result = calculator.calculate(**backend_params)
        
        response = {
            "success": True,
            "product_type": "Notepads A4",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Notepads A4] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}
```

---

## ⚡ CALCULATOR 2-3: NOTEPADS A5 & A6

**Pattern:** Same as A4 with different sizes

### **Expected Parameters:**
- `quantity` (int) - 25 to 2000
- `print_type` (str) - "Colour" or "Black & White"
- `print_sides` (str) - "Single side print" or "Double side print"
- `paper_stock` (str) - Stock options
- `artworks` (int) - Number of designs

### **Common Issues:**
- ❌ Schema has combined print_type (e.g., "Colour 1 sided")
- ❌ Backend expects separate `print_type` and `print_sides`
- ❌ Wrapper uses `**kwargs` blindly
- ❌ No legacy parameter translation

### **Fix Strategy:** Apply same pattern as Notepads A4

---

## ⚡ CALCULATOR 4: CUSTOM POSTER PRINTING

### **Backend Signature:**
```python
# File: backend/shopify_calculators/CustomPosterPrinting_Shopify_Calculator.py
def calculate(self, **kwargs) -> CustomPosterPrintingShopifyCalculatorQuoteResult:
    """
    Calculate Custom Poster Printing Shopify quote
    
    Backend extracts these parameters:
        quantity: int(kwargs.get('quantity', kwargs.get('qty', 50)))
        width: Decimal(kwargs.get('width_mm', kwargs.get('width', 420)))  # A3 width
        height: Decimal(kwargs.get('height_mm', kwargs.get('height', 594)))  # A3 height
        paper_stock: kwargs.get('paper_stock', '150gsm')
    """
```

### **Expected Parameters:**
- `quantity` (int) - Number of posters (50 default)
- `width_mm` (decimal/int) - Width in millimeters (420mm = A3 default)
- `height_mm` (decimal/int) - Height in millimeters (594mm = A3 default)
- `paper_stock` (str) - Paper weight (e.g., "150gsm")

### **Common Issues:**
- ❌ Backend accepts both `width_mm` OR `width` (aliasing)
- ❌ Backend accepts both `height_mm` OR `height` (aliasing)
- ❌ Schema may use different parameter names
- ❌ Wrapper uses `**kwargs` blindly

### **Fix Strategy:**
1. Update schema to use `width_mm` and `height_mm` (preferred names)
2. Add legacy aliases `width` and `height` for backwards compatibility
3. Create explicit wrapper with parameter validation

---

## ⚡ CALCULATOR 5: CUSTOM VINYL STICKERS

### **Backend Signature:**
```python
# File: backend/shopify_calculators/CustomVinylStickers_Shopify_Calculator.py
def calculate(self, **kwargs) -> CustomVinylStickersShopifyCalculatorQuoteResult:
    """
    Calculate Custom Vinyl Stickers Shopify quote
    
    Backend extracts these parameters:
        quantity: int(kwargs.get('quantity', kwargs.get('qty', 100)))
        width: Decimal(kwargs.get('width_mm', kwargs.get('width', 100)))  # Width in mm
        height: Decimal(kwargs.get('height_mm', kwargs.get('height', 100)))  # Height in mm
        finish: kwargs.get('finish', 'Gloss')  # Gloss or Matt
    """
```

### **Expected Parameters:**
- `quantity` (int) - Number of stickers (100 default)
- `width_mm` (decimal/int) - Width in millimeters (100mm default)
- `height_mm` (decimal/int) - Height in millimeters (100mm default)
- `finish` (str) - "Gloss" or "Matt" (affects vinyl cost)

### **Key Features:**
- ✅ Vinyl cost varies by finish: Gloss = $25/m², Matt = $22/m²
- ✅ Cutting cost per item: $0.40
- ✅ Print cost: $10/m²
- ❌ NO VSA stock database integration (uses hardcoded costs)

### **Common Issues:**
- ❌ Backend accepts both `width_mm` OR `width` (aliasing)
- ❌ Backend accepts both `height_mm` OR `height` (aliasing)
- ❌ Wrapper uses `**kwargs` blindly

### **Fix Strategy:**
1. Update schema to use `width_mm` and `height_mm` (preferred names)
2. Add legacy aliases `width` and `height` for backwards compatibility
3. Create explicit wrapper with parameter validation
4. Add enum for finish options: ["Gloss", "Matt"]

---

## 📋 TESTING CHECKLIST

For each calculator, create test file with:

### ✅ Test 1: Schema Validation
- [ ] All required parameters present
- [ ] Parameter types match backend expectations
- [ ] Enums include all valid values

### ✅ Test 2: Wrapper Validation
- [ ] No `**kwargs` in signature
- [ ] All parameters explicitly defined
- [ ] Type hints match schema types

### ✅ Test 3: Legacy Translation
- [ ] Deprecated parameters translated correctly
- [ ] Warnings returned in response
- [ ] Old code still works

### ✅ Test 4: Backend Call
- [ ] Parameters passed with correct names
- [ ] No extra parameters sent
- [ ] Backend receives expected types

### ✅ Test 5: Calculation
- [ ] Sample quote calculates successfully
- [ ] Price breakdown returned
- [ ] GST applied correctly (double GST for Shopify)

---

## 🚀 EXECUTION STEPS

### **Step 1:** Fix Notepads A4 (Start Here)
1. Update schema (quantity type, split print_type, rename stock_type)
2. Update wrapper (explicit params, legacy translation)
3. Create test file
4. Run test: `python -m pytest tests/calculators/alignment/test_calculator_notepads_a4_alignment.py -v`

### **Step 2:** Fix Notepads A5
1. Copy A4 pattern
2. Adjust size-specific parameters
3. Create test file
4. Run test

### **Step 3:** Fix Notepads A6
1. Copy A4 pattern
2. Adjust size-specific parameters
3. Create test file
4. Run test

### **Step 4:** Analyze & Fix Custom Poster Printing
1. Read backend file to understand parameters
2. Update schema with correct parameters
3. Create explicit wrapper
4. Create test file
5. Run test

### **Step 5:** Analyze & Fix Custom Vinyl Stickers
1. Read backend file to understand parameters
2. Check VSA stock integration
3. Update schema with correct parameters
4. Create explicit wrapper
5. Create test file
6. Run test

---

## 🎯 SUCCESS CRITERIA

**Group 3 Complete When:**
- [ ] All 5 calculators have updated schemas
- [ ] All 5 wrappers use explicit parameters
- [ ] All 5 test files pass 12/12 tests
- [ ] Legacy parameters translated with warnings
- [ ] Sample quotes calculate successfully
- [ ] Documentation updated

---

## 📝 NOTES

### **Key Differences from Group 1:**
1. **Backend uses `**kwargs`** - Must analyze backend code to find parameter names
2. **Simpler products** - Fewer parameters than business cards/flyers
3. **No complex enums** - Mostly basic string/integer parameters
4. **Less legacy confusion** - Newer calculators with less historical baggage

### **Common Patterns:**
- Notepads: All three sizes follow same structure
- Print options: Usually split into `print_type` (color) + `print_sides` (1 or 2)
- Stock naming: Backend often expects `paper_stock` not `stock_type`
- Quantity: Always integer, never string

### **Testing Strategy:**
- Start with Notepads A4 as template
- Apply same pattern to A5 and A6 (should be fast)
- Poster and Vinyl may have unique parameters - analyze carefully
- Test with minimal valid parameters first
- Add optional parameters incrementally

---

## 🔗 RELATED FILES

- **Main Instructions:** `.github/CALCULATOR_ALIGNMENT_INSTRUCTIONS.md`
- **Project Summary:** `.github/CALCULATOR_ALIGNMENT_SUMMARY.md`
- **All Groups:** `.github/CALCULATOR_GROUPS.md`
- **Test Template:** `.github/TEST_TEMPLATE.py`
- **Group 1 Example:** `.github/QUICK_START_GROUP_1.md`

---

**Last Updated:** January 19, 2026  
**Status:** Ready to start  
**Next:** Analyze Notepads A4 backend parameters
