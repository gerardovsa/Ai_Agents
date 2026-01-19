# Quick Start: Group 1 Calculator Alignment
**Target:** 5 calculators in Group 1 (Business Cards & Flyers)  
**Priority:** HIGHEST - User's bug found here  
**Time Estimate:** 4-6 hours

---

## 🎯 YOUR MISSION

Fix parameter alignment for 5 calculators:
1. `calculate_economical_business_cards_shopify`
2. `calculate_premium_business_cards_shopify`
3. `calculate_folded_flyers_shopify` ⚠️ **USER'S BUG HERE**
4. `calculate_printed_letterheads_shopify`
5. `calculate_with_compliments_slips_shopify`

---

## 📁 FILES YOU'LL MODIFY

```
UI/modules_external/quote-calculator/
├── implementations/
│   └── calculator_wrapper.py (Lines 1118-1950)
│
└── backend/shopify_calculators/
    ├── EconomicalBusinessCards_Shopify_Calculator.py
    ├── PremiumBusinessCards_Shopify_Calculator.py
    ├── FoldedFlyers_Shopify_Calculator.py
    ├── PrintedLetterheads_Shopify_Calculator.py
    └── WithComplimentsSlips_Shopify_Calculator.py

tools/schemas/ARCHIVE/
└── calculator_tools.json (Lines 1855-2100)

tests/calculators/alignment/
├── test_calculator_economical_business_cards_alignment.py (CREATE)
├── test_calculator_premium_business_cards_alignment.py (CREATE)
├── test_calculator_folded_flyers_alignment.py (CREATE)
├── test_calculator_printed_letterheads_alignment.py (CREATE)
└── test_calculator_with_compliments_slips_alignment.py (CREATE)
```

---

## ⚡ CALCULATOR 1: FOLDED FLYERS (Start Here - User's Bug!)

### **Known Issues:**
- ❌ Schema has `cellophane` → Backend expects `celloglaze`
- ❌ Schema has `colour` (bool) → Backend expects `print_type` (str)
- ❌ Schema has `fold_type` → Backend expects `folding`
- ❌ Schema missing `artworks` parameter
- ❌ Wrapper has `**kwargs` catching errors

### **Backend Signature:**
```python
# File: backend/shopify_calculators/FoldedFlyers_Shopify_Calculator.py
def calculate_quote(
    quantity: int,
    print_sides: PrintSides,        # Enum
    print_type: PrintType,          # Enum
    finish_size: FinishSize,        # Enum (A5, A4, A3, 6pp A4)
    paper_stock: PaperStock,        # Enum (Satin 150GSM, etc.)
    artworks: int,
    fold_type: FoldType,            # Enum (Single/Double/Triple Fold)
    celloglaze: Celloglaze = Celloglaze.NONE  # Enum
) -> FoldedFlyerResult:
```

### **Current Wrapper (Line 1259):**
```python
def calculate_folded_flyers_shopify(
    quantity: int,
    size: str,
    stock: str,
    double_sided: bool = True,      # ✅ KEEP (AI-friendly)
    folding: str = "Single Fold",   # ✅ CORRECT NAME
    print_type: str = "Colour",     # ✅ CORRECT NAME
    artworks: int = 1,              # ✅ CORRECT NAME
    celloglaze: str = "None",       # ✅ CORRECT NAME
    **kwargs                        # ❌ REMOVE THIS!
):
```

### **Current Schema (Line 1855):**
```json
{
  "name": "calculate_folded_flyers_shopify",
  "parameters": {
    "quantity": {"type": "integer"},
    "size": {"type": "string"},
    "stock": {"type": "string"},
    "double_sided": {"type": "boolean"},
    "colour": {"type": "boolean"},      // ❌ WRONG - should be print_type
    "fold_type": {"type": "string"},    // ❌ WRONG - should be folding
    "cellophane": {"type": "string"}    // ❌ WRONG - should be celloglaze
  }
}
```

### **FIX SCHEMA:**
```json
{
  "name": "calculate_folded_flyers_shopify",
  "parameters": {
    "quantity": {"type": "integer", "enum": [100, 250, 500, 1000, 2000, 5000, 10000]},
    "size": {"type": "string", "enum": ["A4", "A5", "A6", "DL", "A3", "6pp A4"]},
    "stock": {
      "type": "string",
      "enum": ["Satin 150GSM", "Satin 300GSM", "Uncoated Bond 80GSM", "Satin 128GSM", 
               "Satin 250GSM", "Satin 350GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
    },
    "double_sided": {"type": "boolean", "required": false},
    "print_type": {
      "type": "string",
      "enum": ["Colour", "Black & White"],
      "required": false,
      "description": "Use EXACT strings: 'Colour' or 'Black & White'"
    },
    "folding": {
      "type": "string", 
      "enum": ["Single Fold", "Double Fold", "Triple Fold"],
      "required": false
    },
    "artworks": {
      "type": "integer",
      "required": false,
      "description": "Number of artwork designs (1-50)"
    },
    "celloglaze": {
      "type": "string",
      "enum": ["None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"],
      "required": false,
      "description": "Use 'celloglaze' not 'cellophane'"
    }
  }
}
```

### **FIX WRAPPER:**
```python
@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000], validate_params=True)
def calculate_folded_flyers_shopify(
    quantity: int,
    size: str,
    stock: str,
    double_sided: bool = True,
    print_type: str = "Colour",         # ✅ NEW NAME (matches schema)
    folding: str = "Single Fold",       # ✅ CORRECT NAME
    artworks: int = 1,
    celloglaze: str = "None",           # ✅ CORRECT NAME
    
    # ⚠️ LEGACY PARAMETERS (backwards compatibility)
    colour: bool = None,                # OLD NAME - will warn
    fold_type: str = None,              # OLD NAME - will warn
    cellophane: str = None              # OLD NAME - will warn
    
    # ❌ NO **kwargs!
) -> Dict[str, Any]:
    """
    Shopify calculator for Folded Flyers
    
    ✅ CURRENT PARAMETERS:
        print_type: "Colour" or "Black & White"
        folding: "Single Fold", "Double Fold", or "Triple Fold"
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"
        artworks: Number of designs (1-50)
    
    ⚠️ DEPRECATED PARAMETERS:
        colour (bool) → use print_type instead
        fold_type (str) → use folding instead
        cellophane (str) → use celloglaze instead
    """
    
    # Legacy translation with warnings
    warnings = []
    
    if colour is not None:
        print_type = "Colour" if colour else "Black & White"
        warnings.append({
            "deprecated": "colour",
            "use_instead": "print_type",
            "value_sent": colour,
            "translated_to": print_type
        })
    
    if fold_type is not None:
        folding = fold_type
        warnings.append({
            "deprecated": "fold_type",
            "use_instead": "folding",
            "value_sent": fold_type,
            "translated_to": folding
        })
    
    if cellophane is not None:
        celloglaze = cellophane
        warnings.append({
            "deprecated": "cellophane",
            "use_instead": "celloglaze",
            "value_sent": cellophane,
            "translated_to": celloglaze
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_folded_flyers_shopify:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
        print(log_msg)
    
    # Continue with backend call...
    try:
        # Import enums
        from shopify_calculators.FoldedFlyers_Shopify_Calculator import (
            PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
        )
        
        # Translate to backend format
        print_sides = "Double side print" if double_sided else "Single side print"
        
        # Map to enums
        size_map = {"A5": FinishSize.A5, "A4": FinishSize.A4, "A3": FinishSize.A3, "6pp A4": FinishSize.A4_6PP, "DL": FinishSize.A5}
        sides_map = {"Single side print": PrintSides.SINGLE_SIDE, "Double side print": PrintSides.DOUBLE_SIDE}
        type_map = {"Colour": PrintType.COLOUR, "Black & White": PrintType.BLACK_WHITE}
        stock_map = {
            "Satin 128GSM": PaperStock.SATIN_128GSM,
            "Satin 150GSM": PaperStock.SATIN_150GSM,
            "Satin 250GSM": PaperStock.SATIN_250GSM,
            "Satin 300GSM": PaperStock.SATIN_300GSM,
            "Satin 350GSM": PaperStock.SATIN_350GSM,
            "Uncoated Bond 80GSM": PaperStock.UNCOATED_80GSM,
            "Uncoated Bond 90GSM": PaperStock.UNCOATED_90GSM,
            "Uncoated Bond 100GSM": PaperStock.UNCOATED_100GSM
        }
        fold_map = {
            "Single Fold": FoldType.SINGLE_FOLD,
            "Double Fold": FoldType.DOUBLE_FOLD,
            "Triple Fold": FoldType.TRIPLE_FOLD
        }
        cello_map = {
            "None": Celloglaze.NONE,
            "1 Side Gloss": Celloglaze.ONE_SIDE_GLOSS,
            "2 Side Gloss": Celloglaze.TWO_SIDE_GLOSS,
            "1 Side Matt": Celloglaze.ONE_SIDE_MATT,
            "2 Side Matt": Celloglaze.TWO_SIDE_MATT
        }
        
        calculator = FoldedFlyersShopifyCalculator()
        result = calculator.calculate_quote(
            quantity=quantity,
            print_sides=sides_map[print_sides],
            print_type=type_map[print_type],
            finish_size=size_map[size],
            paper_stock=stock_map[stock],
            artworks=artworks,
            fold_type=fold_map[folding],
            celloglaze=cello_map[celloglaze]
        )
        
        response = {
            "success": True,
            "product_type": "Folded Flyers",
            "quantity": result.quantity,
            "total_price": float(result.final_price),
            "unit_price": float(result.final_price / result.quantity),
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
```

### **CREATE TESTS:**
Use TEST_TEMPLATE.py and customize for folded flyers.

---

## 📊 COMPLETION CHECKLIST

- [ ] Calculator 1: Folded Flyers - Schema fixed, wrapper fixed, tests passing (5/5)
- [ ] Calculator 2: Economical Business Cards - Same process
- [ ] Calculator 3: Premium Business Cards - Same process
- [ ] Calculator 4: Printed Letterheads - Same process
- [ ] Calculator 5: With Compliments Slips - Same process
- [ ] All 25 tests passing (5 calculators × 5 tests each)
- [ ] Group 1 summary report created
- [ ] Git branch: `fix/calculator-alignment-group-1`
- [ ] Ready for PR

---

## 🚀 START NOW

```bash
# 1. Create test file
cp .github/TEST_TEMPLATE.py tests/calculators/alignment/test_calculator_folded_flyers_alignment.py

# 2. Edit schema
# Open: tools/schemas/ARCHIVE/calculator_tools.json
# Find: calculate_folded_flyers_shopify (line 1855)
# Apply fixes above

# 3. Edit wrapper
# Open: UI/modules_external/quote-calculator/implementations/calculator_wrapper.py
# Find: calculate_folded_flyers_shopify (line 1259)
# Apply fixes above

# 4. Run tests
pytest tests/calculators/alignment/test_calculator_folded_flyers_alignment.py -v

# 5. Verify all passing
# Should see: 5/5 tests PASSED

# 6. Move to next calculator
# Repeat for economical_business_cards
```

**GO! Fix the bug that started all of this!** 🚀
