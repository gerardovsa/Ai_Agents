# Quick Integration Guide - Quote Calculator → AI_agents
**Goal:** Integrate InHouse Print Quote Calculator into AI_agents tool system

---

## 🎯 Integration Strategy

### Recommended Approach: **Wrapper Pattern**

Instead of modifying the original calculator files, create a thin wrapper that adapts them to AI_agents:

```
AI_agents Tool Registry
    ↓
tools/implementations/calculator.py (NEW WRAPPER)
    ↓
UI/external/modules/calculator-module/ORIGINAL/complete_calculator_implementation.py
```

---

## 📋 Step-by-Step Integration

### Step 1: Create Tool Schema
**File:** `tools/schemas/calculator_tools.json`

```json
{
  "calculator_tools": [
    {
      "name": "calculate_business_cards",
      "description": "Calculate quote for business cards using InHouse Print pricing",
      "category": "calculator",
      "parameters": {
        "quantity": {
          "type": "integer",
          "description": "Number of business cards (minimum 1000)",
          "required": true
        },
        "stock_type": {
          "type": "string",
          "description": "Paper stock: 350gsm_satin, 400gsm_uncoated, 350gsm_gloss",
          "required": true
        },
        "finish": {
          "type": "string",
          "description": "Finish type: none, gloss_cello, matt_cello",
          "required": false,
          "default": "none"
        },
        "print_sides": {
          "type": "string",
          "description": "Printing: double_sided, single_sided",
          "required": false,
          "default": "double_sided"
        }
      }
    },
    {
      "name": "calculate_flyers",
      "description": "Calculate quote for digital printing flyers",
      "category": "calculator",
      "parameters": {
        "quantity": {
          "type": "integer",
          "description": "Number of flyers (minimum 100)",
          "required": true
        },
        "size": {
          "type": "string",
          "description": "Paper size: A4, A5, A6, DL",
          "required": true
        },
        "stock_id": {
          "type": "integer",
          "description": "Stock ID from database",
          "required": true
        }
      }
    }
  ]
}
```

### Step 2: Create Implementation Wrapper
**File:** `tools/implementations/calculator.py`

```python
"""
InHouse Print Quote Calculator Wrapper
Adapts complete_calculator_implementation.py for AI_agents tool system
"""

import sys
import os
from typing import Dict, Any

# Add calculator module to path
calculator_path = os.path.join(
    os.path.dirname(__file__), 
    '..', '..', 'UI', 'external', 'modules', 'calculator-module', 'ORIGINAL'
)
sys.path.insert(0, calculator_path)

# Import Shopify Business Card Calculator (no database needed)
from shopify_calculators.business_card_calculator_shopify import (
    ShopifyBusinessCardCalculator,
    PrintType,
    StockTypeStandard,
    CelloglazePremium
)


class CalculatorWrapper:
    """
    Wrapper for InHouse Print calculators
    Provides credential injection and result formatting for AI_agents
    """
    
    def __init__(self, **kwargs):
        self.credentials = None
        # Initialize Shopify calculator (no DB needed)
        self.bc_calculator = ShopifyBusinessCardCalculator()
    
    def calculate_business_cards(self, quantity: int, stock_type: str, 
                                  finish: str = "none", 
                                  print_sides: str = "double_sided",
                                  **kwargs) -> Dict[str, Any]:
        """
        Calculate business card quote using Shopify pricing
        
        Args:
            quantity: Number of cards (1000-10000)
            stock_type: "350gsm_satin", "400gsm_uncoated", etc.
            finish: "none", "gloss_cello", "matt_cello"
            print_sides: "double_sided", "single_sided"
        
        Returns:
            Dict with quote details
        """
        
        # Map stock type string to enum
        stock_map = {
            "350gsm_satin": StockTypeStandard.SATIN_350GSM,
            "400gsm_uncoated": StockTypeStandard.UNCOATED_400GSM,
            "350gsm_gloss": StockTypeStandard.GLOSS_350GSM
        }
        
        # Map finish string to enum
        finish_map = {
            "none": None,
            "gloss_cello": CelloglazePremium.GLOSS,
            "matt_cello": CelloglazePremium.MATT
        }
        
        # Map print sides to enum
        print_map = {
            "double_sided": PrintType.DOUBLE_SIDED,
            "single_sided": PrintType.SINGLE_SIDED
        }
        
        try:
            # Execute calculation
            result = self.bc_calculator.calculate(
                quantity=quantity,
                print_type=print_map.get(print_sides, PrintType.DOUBLE_SIDED),
                stock_type=stock_map.get(stock_type, StockTypeStandard.SATIN_350GSM),
                celloglaze=finish_map.get(finish)
            )
            
            # Format result for AI_agents
            return {
                "success": True,
                "product": "Business Cards",
                "quantity": quantity,
                "total_inc_gst": float(result.total_inc_gst),
                "price_per_unit": float(result.price_per_unit),
                "stock": stock_type,
                "finish": finish,
                "turnaround": "3-5 business days",
                "breakdown": {
                    "base_cost": float(result.base_cost),
                    "print_cost": float(result.print_cost) if hasattr(result, 'print_cost') else 0,
                    "celloglaze_cost": float(result.celloglaze_cost) if hasattr(result, 'celloglaze_cost') else 0,
                    "gst": float(result.gst),
                    "subtotal": float(result.subtotal)
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to calculate business card quote: {str(e)}"
            }
    
    def calculate_flyers(self, quantity: int, size: str, stock_id: int, **kwargs) -> Dict[str, Any]:
        """
        Calculate flyer quote (requires database connection)
        
        Note: This requires SQL Server or SQLite export
        Currently returns placeholder
        """
        return {
            "success": False,
            "error": "Database required",
            "message": "Flyer calculator requires SQL Server connection or SQLite export. Use Business Card calculator for now."
        }
    
    def get_stock_list(self, **kwargs) -> Dict[str, Any]:
        """
        Get list of available paper stocks
        
        Returns:
            Dict with stock options
        """
        return {
            "success": True,
            "stocks": [
                {
                    "id": "350gsm_satin",
                    "name": "350gsm Satin",
                    "description": "Premium satin finish, most popular",
                    "recommended": True
                },
                {
                    "id": "400gsm_uncoated",
                    "name": "400gsm Uncoated",
                    "description": "Thick uncoated stock, writable"
                },
                {
                    "id": "350gsm_gloss",
                    "name": "350gsm Gloss",
                    "description": "High gloss finish"
                }
            ]
        }
```

### Step 3: Update Tool Registry
**File:** `tools/registry.py`

Add import at top:
```python
from tools.implementations.calculator import CalculatorWrapper
```

Add to registry initialization (around line 50):
```python
# Calculator Tools
calculator_tools = self.load_schema('calculator_tools.json')
if calculator_tools:
    for tool in calculator_tools.get('calculator_tools', []):
        tool['implementation'] = CalculatorWrapper
        self.tools[tool['name']] = tool
```

### Step 4: Test Integration
**File:** `test_calculator_integration.py`

```python
"""
Test Quote Calculator Integration
"""

import sys
sys.path.insert(0, 'tools/implementations')

from calculator import CalculatorWrapper

def test_business_cards():
    """Test business card calculator"""
    
    calc = CalculatorWrapper()
    
    # Test 1: Standard 1000 business cards
    result = calc.calculate_business_cards(
        quantity=1000,
        stock_type="350gsm_satin",
        finish="none",
        print_sides="double_sided"
    )
    
    print("Test 1: 1000 Business Cards")
    print(f"  Success: {result['success']}")
    print(f"  Total: ${result['total_inc_gst']:.2f}")
    print(f"  Per card: ${result['price_per_unit']:.3f}")
    print()
    
    # Test 2: With gloss cello
    result = calc.calculate_business_cards(
        quantity=2000,
        stock_type="350gsm_satin",
        finish="gloss_cello",
        print_sides="double_sided"
    )
    
    print("Test 2: 2000 Business Cards with Gloss Cello")
    print(f"  Success: {result['success']}")
    print(f"  Total: ${result['total_inc_gst']:.2f}")
    print(f"  Per card: ${result['price_per_unit']:.3f}")
    print()
    
    # Test 3: Get stock list
    stocks = calc.get_stock_list()
    print("Test 3: Stock List")
    print(f"  Success: {stocks['success']}")
    print(f"  Available stocks: {len(stocks['stocks'])}")
    for stock in stocks['stocks']:
        print(f"    - {stock['name']}: {stock['description']}")

if __name__ == "__main__":
    test_business_cards()
```

---

## 🎯 Why This Approach?

### ✅ Advantages:
1. **No modification** of original calculator files
2. **Easy updates** - just replace ORIGINAL folder
3. **Clean separation** - wrapper in AI_agents, calculator unchanged
4. **Credential injection** ready for future database needs
5. **Standard tool pattern** - matches other AI_agents tools

### 🚫 Alternative (Not Recommended):
Directly importing tool_use_agent.py would require:
- Modifying tool_use_agent.py imports
- Adapting database connections
- Merging tool registries
- More complex maintenance

---

## 🧪 Testing Workflow

```bash
# 1. Test calculator wrapper directly
cd C:\Users\gpoli\GIT\AI_agents
python test_calculator_integration.py

# 2. Test through tool registry
python -c "from tools.registry import ToolRegistry; r = ToolRegistry(); print(f'{len(r.tools)} tools loaded'); print([t for t in r.tools.keys() if 'calculate' in t])"

# 3. Test through Flask API
# Start server: BISTART
# Call: POST /api/agent/execute-tool
# Body: {"tool_name": "calculate_business_cards", "parameters": {...}}
```

---

## 📊 Integration Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Files Copied** | ✅ Complete | 38+ files in ORIGINAL folder |
| **Business Cards** | ✅ Ready | Shopify calculator, no DB needed |
| **Flyers** | ⏳ Pending | Requires database migration |
| **Perfect Bound Books** | ⏳ Pending | Requires database migration |
| **Tool Schema** | 📝 To Create | calculator_tools.json |
| **Tool Wrapper** | 📝 To Create | calculator.py |
| **Registry Update** | 📝 To Create | registry.py modification |
| **Testing** | 📝 To Create | test_calculator_integration.py |

---

## 🚀 Quick Start (30 minutes)

1. **Create tool schema** (5 min)
   ```bash
   # Copy template above to:
   # tools/schemas/calculator_tools.json
   ```

2. **Create wrapper** (10 min)
   ```bash
   # Copy template above to:
   # tools/implementations/calculator.py
   ```

3. **Update registry** (5 min)
   ```bash
   # Add 5 lines to tools/registry.py
   ```

4. **Test** (10 min)
   ```bash
   python test_calculator_integration.py
   ```

---

## 🎯 Expected Result

After integration, AI agent can:

```
User: "Quote 1000 business cards, 350gsm Satin"

AI: [Calls calculate_business_cards tool]

Response:
"Your quote for 1,000 business cards:

💰 Total: $234.50 (inc GST)
📄 Per card: $0.23
📦 Stock: 350gsm Satin
⏱️ Turnaround: 3-5 business days

Cost Breakdown:
• Base cost: $185.00
• Print cost: $25.00
• GST (10%): $21.00"
```

---

## 📞 Next Steps

1. Create tool schema
2. Create wrapper implementation
3. Update registry
4. Test with business cards
5. (Future) Migrate database for other calculators

**Status:** ✅ Ready for implementation - All files copied, templates provided

---

**Last Updated:** October 30, 2025
