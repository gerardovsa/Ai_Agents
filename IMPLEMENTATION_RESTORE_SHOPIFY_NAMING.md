# Implementation: Restore Shopify Calculator Naming

## 🎯 Files to Modify

### 1. `complete_calculator_implementation.py`

Add this method to the main calculator class (around line 6500):

```python
def get_shopify_calculator_requirements(self, product_type: str) -> Dict[str, Any]:
    """
    Get parameter requirements for Shopify DPO calculators.
    
    These calculators use F1-F14 field naming from WooCommerce DPO.
    Parameters are COMPLETELY DIFFERENT from GOD calculator parameters.
    """
    
    shopify_calculators = {
        "shopify_wire_bound": {
            "description": "Wire Bound Books - WooCommerce DPO exact pricing",
            "calculator_class": "WireBoundShopifyCalculator", 
            "note": "Metal wire coil binding. Uses F1-F14 Shopify field structure.",
            "pricing": "WooCommerce hardcoded prices + 5% markup + 10% GST + $44 surcharge",
            
            "required_parameters": {
                "quantity": {
                    "type": "int",
                    "field": "F1",
                    "description": "Number of books to produce",
                    "example": 3,
                    "validation": "Must be >= 1"
                },
                "internal_pages": {
                    "type": "int",
                    "field": "F11",
                    "description": "Number of internal pages",
                    "example": 316,
                    "validation": "1-700 pages"
                }
            },
            
            "optional_parameters": {
                "artworks": {
                    "type": "int",
                    "field": "F2",
                    "description": "Number of artworks (first free, $15 each additional)",
                    "default": 1,
                    "range": "1-50"
                },
                "finish_size": {
                    "type": "str",
                    "field": "F14",
                    "description": "Finished book size after trimming",
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
                    "field": "F3",
                    "description": "Front outer cover overlay",
                    "options": ["Not Required", "Clear PVC"],
                    "default": "Clear PVC",
                    "cost": "$0.12 per book if Clear PVC"
                },
                "printed_front_cover": {
                    "type": "str",
                    "field": "F4",
                    "description": "Front printed cover stock weight",
                    "options": ["250GSM Satin", "300GSM Satin", "350GSM Satin"],
                    "default": "300GSM Satin"
                },
                "front_cover_print": {
                    "type": "str",
                    "field": "F5",
                    "description": "Front cover printing",
                    "options": ["1pp Colour", "2pp Colour", "1pp Black & White", "2pp Black & White"],
                    "default": "2pp Colour"
                },
                "front_celloglaze": {
                    "type": "str",
                    "field": "F6",
                    "description": "Front cover celloglaze/lamination",
                    "options": ["None", "1 Side Gloss", "2 Sided Gloss", "1 Side Matt", "2 Sided Matt"],
                    "default": "None"
                },
                "outer_back_cover": {
                    "type": "str",
                    "field": "F7",
                    "description": "Back outer cover",
                    "options": ["None", "Clear PVC", "Black Leather Grain", "350GSM Satin Blank Card"],
                    "default": "None",
                    "note": "Use '350GSM Satin Blank Card' for black satin back cover"
                },
                "printed_back_cover": {
                    "type": "str",
                    "field": "F8",
                    "description": "Back printed cover stock",
                    "options": ["250GSM Satin", "300GSM Satin", "350GSM Satin", "None"],
                    "default": "None"
                },
                "back_cover_print": {
                    "type": "str",
                    "field": "F9",
                    "description": "Back cover printing",
                    "options": ["None", "1pp Colour", "2pp Colour", "1pp Black & White", "2pp Black & White"],
                    "default": "None"
                },
                "back_celloglaze": {
                    "type": "str",
                    "field": "F10",
                    "description": "Back cover celloglaze/lamination",
                    "options": ["None", "1 Side Gloss", "2 Sided Gloss", "1 Side Matt", "2 Sided Matt"],
                    "default": "None"
                },
                "internal_stock": {
                    "type": "str",
                    "field": "F12",
                    "description": "Internal pages paper stock",
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
                    "field": "F13",
                    "description": "Internal pages print type",
                    "options": ["Full Colour", "Black & White"],
                    "default": "Black & White"
                }
            },
            
            "natural_language_mapping": {
                "clear acetate": "outer_front_cover='Clear PVC'",
                "clear front": "outer_front_cover='Clear PVC'",
                "black satin back": "outer_back_cover='350GSM Satin Blank Card'",
                "black back cover": "outer_back_cover='350GSM Satin Blank Card' or 'Black Leather Grain'",
                "350gsm satin": "printed_front_cover='350GSM Satin'",
                "300gsm satin": "printed_front_cover='300GSM Satin'",
                "100gsm uncoated": "internal_stock='Uncoated Bond 100GSM'",
                "full colour both sides": "internal_print='Full Colour'",
                "full color": "internal_print='Full Colour'",
                "A4 portrait": "finish_size='A4 Portrait'"
            },
            
            "example_pacific_partnerships": {
                "description": "Pacific Partnerships - Wire Bound Books (Job 1: 316 pages)",
                "specs": {
                    "Front Cover": "Clear Acetate (250mic)",
                    "Back Cover": "350gsm Black Satin Card",
                    "Internal Pages": "100gsm uncoated, Full colour both sides",
                    "Quantity": "3 copies"
                },
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
        },
        
        "shopify_spiral_bound": {
            "description": "Spiral Bound Books - WooCommerce DPO exact pricing",
            "calculator_class": "SpiralBoundShopifyCalculator",
            "note": "Plastic spiral coil binding. Uses same F1-F14 structure as Wire Bound.",
            "pricing": "WooCommerce hardcoded prices + 5% markup + 10% GST + $44 surcharge",
            "parameters": "Same as shopify_wire_bound (F1-F14 structure)"
        },
        
        "shopify_perfect_bound": {
            "description": "Perfect Bound Books - WooCommerce DPO exact pricing",
            "calculator_class": "PerfectBoundShopifyCalculator",
            "note": "Glued square spine binding. Uses F1-F11 structure (simpler than Wire/Spiral).",
            "pricing": "WooCommerce hardcoded prices + profit margins",
            "parameters": "Different structure - use get_calculator_requirements for details"
        }
    }
    
    if product_type in shopify_calculators:
        return {
            "success": True,
            "product_type": product_type,
            "requirements": shopify_calculators[product_type]
        }
    else:
        return {
            "success": True,
            "product_type": product_type,
            "requirements": {
                "error": f"Shopify calculator '{product_type}' not documented yet",
                "supported_shopify_types": list(shopify_calculators.keys()),
                "hint": "Use one of the supported types above"
            }
        }
```

Add this routing method (around line 6400):

```python
def calculate_quote(self, product_type: str, parameters: Dict[str, Any]) -> QuoteResult:
    """
    Calculate quote for any product type.
    Routes to appropriate calculator (GOD or Shopify).
    """
    
    # Shopify Calculators (WooCommerce DPO pricing)
    if product_type == "shopify_wire_bound":
        from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator
        calc = WireBoundShopifyCalculator()
        result = calc.calculate(**parameters)
        return self._convert_shopify_wire_result(result)
    
    elif product_type == "shopify_spiral_bound":
        from shopify_calculators.SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
        calc = SpiralBoundShopifyCalculator()
        result = calc.calculate(**parameters)
        return self._convert_shopify_spiral_result(result)
    
    elif product_type == "shopify_perfect_bound":
        from shopify_calculators.PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
        calc = PerfectBoundShopifyCalculator()
        result = calc.calculate(**parameters)
        return self._convert_shopify_perfect_result(result)
    
    # GOD Calculators (Database-driven pricing)
    elif product_type == "perfect_bound_books":
        # Existing GOD calculator
        return self.calculate_perfect_bound_book(**parameters)
    
    elif product_type == "booklets":
        return self.calculate_booklet(**parameters)
    
    elif product_type == "business_cards":
        return self.calculate_business_card(**parameters)
    
    elif product_type == "flyers":
        return self.calculate_flyer(**parameters)
    
    else:
        raise ValueError(f"Unknown product type: {product_type}")

def _convert_shopify_wire_result(self, shopify_result) -> QuoteResult:
    """Convert WireBoundQuoteResult to standard QuoteResult"""
    return QuoteResult(
        product_type="Wire Bound Books",
        quantity=shopify_result.quantity,
        cost_to_business=shopify_result.breakdown.get('total_business_cost', Decimal('0')),
        profit_margin=shopify_result.breakdown.get('profit_margin_pct', Decimal('0')),
        total_cost_ex_gst=shopify_result.total_price / Decimal('1.10'),  # Remove GST
        total_cost_inc_gst=shopify_result.total_price,
        breakdown=shopify_result.breakdown,
        specifications=shopify_result.specifications
    )
```

### 2. Update Tool Registration (wherever MCP tools are defined)

Find where `inhouse_get_calculator_requirements` is registered and update:

```typescript
// Or in Python if it's a Python MCP server
{
  name: "inhouse_get_calculator_requirements",
  description: "Get parameter requirements for InHouse Print calculators (GOD and Shopify)",
  input_schema: {
    type: "object",
    properties: {
      product_type: {
        type: "string",
        description: "Calculator type",
        enum: [
          // GOD Calculators
          "flyers",
          "perfect_bound_books",
          "booklets",
          "business_cards",
          "letterheads",
          "corflute_signs",
          "notepads_a5",
          
          // Shopify Calculators
          "shopify_wire_bound",
          "shopify_spiral_bound",
          "shopify_perfect_bound",
          "shopify_premium_business_cards",
          "shopify_economical_business_cards",
          "shopify_folded_flyers"
        ]
      }
    },
    required: ["product_type"]
  }
}
```

And update the tool handler:

```python
def handle_inhouse_get_calculator_requirements(product_type: str):
    calculator = ComprehensiveQuoteCalculator(db_connection)
    
    # Route to appropriate requirements method
    if product_type.startswith("shopify_"):
        return calculator.get_shopify_calculator_requirements(product_type)
    else:
        return calculator.get_calculator_requirements(product_type)
```

## ✅ Quick Test After Implementation

```python
# Test 1: Discover Shopify Wire Bound
requirements = inhouse_get_calculator_requirements("shopify_wire_bound")
print(requirements["requirements"]["required_parameters"])
# Should show: quantity, internal_pages

# Test 2: Calculate Pacific Partnerships Job 1
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
print(f"Total: ${quote.total_cost_inc_gst}")
# Should return a valid quote
```

## 📋 Summary of Changes

1. ✅ Add `get_shopify_calculator_requirements()` method
2. ✅ Add `calculate_quote()` routing method  
3. ✅ Add Shopify result converters
4. ✅ Update MCP tool enum to include shopify_ types
5. ✅ Update tool handler to route based on prefix

**Result:** AI can now discover and use Shopify calculators with correct F1-F14 parameters! 🎉
