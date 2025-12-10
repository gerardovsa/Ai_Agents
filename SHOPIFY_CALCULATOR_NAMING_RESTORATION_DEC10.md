# Shopify Calculator Naming Restoration - December 10, 2025

## 🔍 **Problem Identified**

The AI cannot use Wire Bound, Spiral Bound, or Premium Business Card calculators because:

1. **Calculator names were changed** from `shopify_wire_bound` to just `wire_bound`
2. **MCP tool `inhouse_get_calculator_requirements` doesn't document these calculators**
3. **Parameter signatures are completely different** between GOD and Shopify calculators

## 📊 **Current State Analysis**

### **What the AI Tried to Do:**
```python
# AI attempted to use perfect_bound_books with GOD calculator parameters
inhouse_calculate_quote(
    product_type="perfect_bound_books",
    parameters={
        "quantity": 3,
        "book_width": 210,        # ❌ GOD parameter
        "book_height": 297,       # ❌ GOD parameter  
        "pages": 316,             # ❌ GOD parameter
        "stock_type_id": 29,      # ❌ GOD parameter
        "binding_type": "Wire Bound"  # ❌ Not recognized
    }
)
```

### **What Shopify Calculators Actually Need:**
```python
# Shopify Wire Bound Calculator expects F1-F14 parameters
WireBoundShopifyCalculator.calculate(
    quantity=3,                           # F1
    artworks=1,                           # F2
    finish_size="A4 Portrait",            # F14
    outer_front_cover="Clear PVC",        # F3
    printed_front_cover="350GSM Satin",   # F4
    front_cover_print="2pp Colour",       # F5
    front_celloglaze="None",              # F6
    outer_back_cover="350GSM Satin Blank Card",  # F7
    printed_back_cover="None",            # F8
    back_cover_print="None",              # F9
    back_celloglaze="None",               # F10
    internal_pages=316,                   # F11
    internal_stock="Uncoated Bond 100GSM", # F12
    internal_print="Full Colour"          # F13
)
```

## 🎯 **Solution: Restore Shopify Naming**

### **Step 1: Rename Product Types (Back to Shopify Names)**

Update product type names to include "shopify" prefix:

| Current Name | Restore To | Calculator Class |
|--------------|------------|------------------|
| `wire_bound` | `shopify_wire_bound` | `WireBoundShopifyCalculator` |
| `spiral_bound` | `shopify_spiral_bound` | `SpiralBoundShopifyCalculator` |
| `perfect_bound_books` (Shopify) | `shopify_perfect_bound` | `PerfectBoundShopifyCalculator` |
| `premium_business_cards` | `shopify_premium_business_cards` | `PremiumBusinessCardsShopifyCalculator` |
| `economical_business_cards` | `shopify_economical_business_cards` | `EconomicalBusinessCardsShopifyCalculator` |
| `folded_flyers` | `shopify_folded_flyers` | `FoldedFlyersShopifyCalculator` |

**Keep GOD calculator as:** `perfect_bound_books` (no rename)

### **Step 2: Add Shopify Calculator Documentation**

File: `complete_calculator_implementation.py`

Add method: `get_shopify_calculator_requirements(product_type: str)`

```python
def get_shopify_calculator_requirements(self, product_type: str) -> Dict[str, Any]:
    """
    Get parameter requirements for Shopify DPO calculators
    
    Shopify calculators use F1-F14 field naming from WooCommerce DPO
    These are DIFFERENT from GOD calculator database-driven parameters
    """
    
    if product_type == "shopify_wire_bound":
        return {
            "description": "Wire Bound Books - WooCommerce DPO Calculator",
            "calculator_class": "WireBoundShopifyCalculator",
            "note": "Uses F1-F14 Shopify field structure - NOT database-driven",
            
            "required_parameters": {
                "quantity": {
                    "type": "int",
                    "description": "Number of books (F1)",
                    "example": 3,
                    "validation": "Must be > 0"
                },
                "internal_pages": {
                    "type": "int", 
                    "description": "Number of internal pages (F11)",
                    "example": 316,
                    "validation": "1-700 pages"
                }
            },
            
            "optional_parameters": {
                "artworks": {
                    "type": "int",
                    "description": "Number of artworks (F2, first free, $15 each)",
                    "default": 1,
                    "range": "1-50"
                },
                "finish_size": {
                    "type": "str",
                    "description": "Book size (F14)",
                    "options": [
                        "A6 Portrait", "A6 Landscape",
                        "DL Portrait", "DL Landscape", 
                        "A5 Portrait", "A5 Landscape",
                        "A4 Portrait", "A4 Landscape"
                    ],
                    "default": "A4 Portrait"
                },
                "outer_front_cover": {
                    "type": "str",
                    "description": "Front outer cover (F3)",
                    "options": ["Not Required", "Clear PVC"],
                    "default": "Clear PVC"
                },
                "printed_front_cover": {
                    "type": "str",
                    "description": "Front printed cover stock (F4)",
                    "options": ["250GSM Satin", "300GSM Satin", "350GSM Satin"],
                    "default": "300GSM Satin"
                },
                "front_cover_print": {
                    "type": "str",
                    "description": "Front cover print (F5)",
                    "options": ["1pp Colour", "2pp Colour", "1pp Black & White", "2pp Black & White"],
                    "default": "2pp Colour"
                },
                "front_celloglaze": {
                    "type": "str",
                    "description": "Front cover celloglaze (F6)",
                    "options": ["None", "1 Side Gloss", "2 Sided Gloss", "1 Side Matt", "2 Sided Matt"],
                    "default": "None"
                },
                "outer_back_cover": {
                    "type": "str",
                    "description": "Back outer cover (F7)",
                    "options": ["None", "Clear PVC", "Black Leather Grain", "350GSM Satin Blank Card"],
                    "default": "350GSM Satin Blank Card"
                },
                "printed_back_cover": {
                    "type": "str",
                    "description": "Back printed cover (F8)",
                    "options": ["250GSM Satin", "300GSM Satin", "350GSM Satin", "None"],
                    "default": "None"
                },
                "back_cover_print": {
                    "type": "str",
                    "description": "Back cover print (F9)",
                    "options": ["None", "1pp Colour", "2pp Colour", "1pp Black & White", "2pp Black & White"],
                    "default": "None"
                },
                "back_celloglaze": {
                    "type": "str",
                    "description": "Back cover celloglaze (F10)",
                    "options": ["None", "1 Side Gloss", "2 Sided Gloss", "1 Side Matt", "2 Sided Matt"],
                    "default": "None"
                },
                "internal_stock": {
                    "type": "str",
                    "description": "Internal paper stock (F12)",
                    "options": [
                        "Satin 128GSM",
                        "Satin 150GSM",
                        "Uncoated Bond 80GSM",
                        "Uncoated Bond 90GSM",
                        "Uncoated Bond 100GSM"
                    ],
                    "default": "Uncoated Bond 100GSM"
                },
                "internal_print": {
                    "type": "str",
                    "description": "Internal print type (F13)",
                    "options": ["Full Colour", "Black & White"],
                    "default": "Full Colour"
                }
            },
            
            "natural_language_mapping": {
                "clear acetate front": "outer_front_cover='Clear PVC'",
                "black satin back": "outer_back_cover='350GSM Satin Blank Card' (use blank card for black cover)",
                "100gsm uncoated": "internal_stock='Uncoated Bond 100GSM'",
                "full colour internals": "internal_print='Full Colour'",
                "A4 portrait": "finish_size='A4 Portrait'"
            },
            
            "example_quote": {
                "description": "Wire bound book - Pacific Partnerships spec",
                "parameters": {
                    "quantity": 3,
                    "artworks": 1,
                    "finish_size": "A4 Portrait",
                    "outer_front_cover": "Clear PVC",
                    "printed_front_cover": "350GSM Satin",
                    "front_cover_print": "2pp Colour",
                    "front_celloglaze": "None",
                    "outer_back_cover": "350GSM Satin Blank Card",
                    "printed_back_cover": "None",
                    "back_cover_print": "None",
                    "back_celloglaze": "None",
                    "internal_pages": 316,
                    "internal_stock": "Uncoated Bond 100GSM",
                    "internal_print": "Full Colour"
                }
            }
        }
    
    elif product_type == "shopify_spiral_bound":
        # Similar structure for Spiral Bound
        pass
    
    elif product_type == "shopify_perfect_bound":
        # Similar structure for Perfect Bound Shopify
        pass
    
    else:
        return {
            "error": f"Product type '{product_type}' not supported",
            "supported_shopify_types": [
                "shopify_wire_bound",
                "shopify_spiral_bound", 
                "shopify_perfect_bound",
                "shopify_premium_business_cards",
                "shopify_economical_business_cards",
                "shopify_folded_flyers"
            ]
        }
```

### **Step 3: Update MCP Tool Response**

File: MCP Server tool implementation (wherever `inhouse_get_calculator_requirements` is defined)

```python
def inhouse_get_calculator_requirements(product_type: str):
    """Get calculator requirements for both GOD and Shopify calculators"""
    
    # Check if Shopify calculator
    if product_type.startswith("shopify_"):
        return calculator.get_shopify_calculator_requirements(product_type)
    
    # Otherwise use GOD calculator requirements
    else:
        return calculator.get_calculator_requirements(product_type)
```

Update supported types list:

```python
"supported_types": [
    # GOD Calculators (Database-Driven)
    "flyers",
    "perfect_bound_books",    # GOD version with stock_type_id, book_width, etc.
    "booklets",
    "business_cards",
    "letterheads",
    "corflute_signs",
    "notepads_a5",
    
    # Shopify Calculators (WooCommerce DPO - Hardcoded Pricing)
    "shopify_wire_bound",     # F1-F14 parameters
    "shopify_spiral_bound",    # F1-F14 parameters
    "shopify_perfect_bound",   # F1-F11 parameters (different from GOD)
    "shopify_premium_business_cards",
    "shopify_economical_business_cards",
    "shopify_folded_flyers"
]
```

### **Step 4: Update Calculator Routing**

File: `complete_calculator_implementation.py` (or wherever routing happens)

```python
def calculate_quote(self, product_type: str, parameters: Dict[str, Any]) -> QuoteResult:
    """Route to appropriate calculator based on product_type"""
    
    # Shopify Calculators
    if product_type == "shopify_wire_bound":
        calc = WireBoundShopifyCalculator()
        result = calc.calculate(**parameters)
        return self._convert_shopify_result(result)
    
    elif product_type == "shopify_spiral_bound":
        calc = SpiralBoundShopifyCalculator()
        result = calc.calculate(**parameters)
        return self._convert_shopify_result(result)
    
    elif product_type == "shopify_perfect_bound":
        calc = PerfectBoundShopifyCalculator()
        result = calc.calculate(**parameters)
        return self._convert_shopify_result(result)
    
    # GOD Calculators
    elif product_type == "perfect_bound_books":
        return self.calculate_perfect_bound_book(**parameters)
    
    # ... other GOD calculators
```

## 📋 **Implementation Checklist**

- [ ] **Restore Shopify naming** in product type constants
- [ ] **Add `get_shopify_calculator_requirements()` method** to return F1-F14 parameter docs
- [ ] **Update MCP tool** to support both GOD and Shopify types
- [ ] **Update routing logic** to recognize `shopify_` prefix
- [ ] **Test Wire Bound calculator** with Pacific Partnerships spec
- [ ] **Document all 6 Shopify calculators** (Wire, Spiral, Perfect, Premium BC, Economical BC, Folded)
- [ ] **Update AI instructions** to explain GOD vs Shopify calculators

## ✅ **Expected AI Workflow (After Fix)**

```python
# Step 1: AI discovers Shopify calculator exists
requirements = inhouse_get_calculator_requirements("shopify_wire_bound")
# Returns F1-F14 parameter documentation

# Step 2: AI calls calculator with correct Shopify parameters
quote = inhouse_calculate_quote(
    product_type="shopify_wire_bound",
    parameters={
        "quantity": 3,
        "finish_size": "A4 Portrait",
        "outer_front_cover": "Clear PVC",
        "printed_front_cover": "350GSM Satin",
        "outer_back_cover": "350GSM Satin Blank Card",
        "internal_pages": 316,
        "internal_stock": "Uncoated Bond 100GSM",
        "internal_print": "Full Colour"
    }
)
# ✅ Works! Returns quote with breakdown
```

## 🎨 **Why "Shopify" Prefix is Essential**

1. **Clear Distinction**: Immediately tells AI these are different from GOD calculators
2. **Parameter Clarity**: Prevents confusion between `book_width` (GOD) vs `finish_size` (Shopify)
3. **Documentation Separation**: Each has its own requirements doc
4. **Routing Logic**: Easy to route: `if product_type.startswith("shopify_")`
5. **Historical Context**: Matches original naming when calculators were first created

## 🚀 **Next Steps**

1. **Locate MCP tool implementation** (find where `inhouse_get_calculator_requirements` is defined)
2. **Update supported_types** to include all 6 Shopify calculators
3. **Add Shopify parameter documentation** for each calculator
4. **Test with Pacific Partnerships quote** (5 wire bound books)
5. **Create comprehensive guide** for AI on GOD vs Shopify calculators

---

**Status:** 🔴 **BLOCKED** - AI cannot use Shopify calculators until naming is restored
**Priority:** 🔥 **HIGH** - Customer waiting for wire bound book quotes
**Owner:** @gerardovsa
**Date:** December 10, 2025
