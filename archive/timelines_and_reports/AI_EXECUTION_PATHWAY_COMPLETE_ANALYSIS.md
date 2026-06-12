# AI Execution Pathway - Complete Analysis
**Date: January 22, 2026**
**Analysis Type: Production Platform Route (Not Testing)**

---

## Executive Summary

This document traces the complete execution pathway from an AI agent receiving a user request to calculate a quote, through all system layers, to the final result delivery. This is the **PRODUCTION ROUTE** - the actual pathway used in the platform, not testing/development routes.

**Request Example:** "Calculate 500 economical business cards, double-sided, colour"

**Complete Journey:**
```
User Request
    ↓
AI Agent (Claude) - Guided by tool_usage_system_prompt.md
    ↓
4-Layer Tool Discovery (Navigation → Guidance → Specification → Execution)
    ↓
Flask HTTP Endpoint (/api/test-calculator)
    ↓
Registry V3 (execute_tool)
    ↓
Module Plugin System (Auto-discovery)
    ↓
Calculator Wrapper (@tool_executor decorator)
    ↓
Backend Calculator (Shopify implementation)
    ↓
Config Manager (JSON pricing loader)
    ↓
Database (Fred/G_Folder - InHouse Print)
    ↓
Result flows back through layers to AI → User
```

---

## Layer 1: AI Agent System Instructions

**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md` (2,709 lines)

### Purpose
Provides the AI agent (Claude) with behavioral instructions, tool discovery patterns, and workflow protocols.

### Key Components

**4-Layer Tool Ecosystem (Lines 400-600):**

1. **Layer 1 - Navigation Tools**
   - `list_platform_tools()` - Browse available platforms (InHouse Print, Microsoft, Google, etc.)
   - `search_tools()` - Semantic search across tool catalog
   - `inhouse_get_domain_guide()` - **MANDATORY FIRST CALL** for printing operations

2. **Layer 2 - Guidance Tools**
   - `inhouse_calculator_guide()` - Learn available calculators
   - `inhouse_query_guide()` - Database query examples
   - `platform_guide()` - Platform-specific documentation

3. **Layer 3 - Specification Tools**
   - `get_tool_schema()` - Get parameter requirements for specific tool

4. **Layer 4 - Execution Tools**
   - `execute_tool()` - Meta-tool for executing other tools
   - Calculator wrappers (e.g., `calculate_economical_business_cards_shopify`)
   - Database tools, platform integrations

**InHouse Print Workflow Protocol (Lines 2400-2600):**

**Mandatory Entry Point:**
```
inhouse_get_domain_guide() → identifies domain (printing/calculator/queries/stock)
```

**8-Stage Calculator Transparency Protocol:**
1. **Parameter Identification** - Call `inhouse_calculator_guide()` to learn calculators
2. **User Clarification** - Call `inhouse_get_calculator_requirements()` for parameter schema
3. **State Parameters** - List all parameters in text before execution
4. **Execute** - Call `inhouse_calculate_quote()` with validated parameters
5. **Breakdown Analysis** - Present itemized cost breakdown
6. **Validation** - Verify math adds up correctly
7. **Correction** - If discrepancies found, re-calculate
8. **Final Report** - Deliver comprehensive quote with breakdown

**Example Workflow:**
```
User: "How much for 500 business cards?"

AI Agent thinks:
1. This is a printing request → call inhouse_get_domain_guide()
2. Domain identified as "calculator" → call inhouse_calculator_guide()
3. Multiple calculators available → ask user: economical or premium stock?
4. User says "economical" → call inhouse_get_calculator_requirements("calculate_economical_business_cards_shopify")
5. Schema received → ask clarifying questions (double-sided? celloglaze finish?)
6. User clarifies → State: "I will calculate quote with: quantity=500, double_sided=True, print_type='Colour', celloglaze='None', artworks=1"
7. Execute → call calculate_economical_business_cards_shopify(...)
8. Receive result → Present breakdown: Setup: $15, Stock: $25, Print: $45, Total: $85 + GST
9. Validate math → Confirm 85 * 1.10 = $93.50 final
10. Report to user
```

**Key Directives:**
- "inhouse_get_domain_guide() - MANDATORY FIRST CALL for printing, quotes, orders, business data"
- "Always state parameters in text before executing calculator"
- "Present itemized breakdown, not just total"
- "Verify math, re-calculate if discrepancy found"

---

## Layer 2: Flask HTTP Server

**File:** `AI_infrastructure/flask_app.py` (4,192 lines)

### Route: `/api/test-calculator` (Lines 630-675)

**Purpose:** Execute calculator tools via HTTP POST request (used by AI agent in production)

**Request Format:**
```json
{
  "tool_name": "calculate_economical_business_cards_shopify",
  "params": {
    "quantity": "500",
    "print_type": "Colour",
    "double_sided": true,
    "celloglaze": "None",
    "artworks": 1
  }
}
```

**Execution Flow:**
```python
# Line 640 - Import Registry V3
from tools.registry_v3 import RegistryV3

# Line 653 - Initialize registry (loads all 611+ tools)
registry = RegistryV3()

# Line 657 - Execute tool with timing
start_time = time.time()
result = registry.execute_tool(tool_name=tool_name, **params)
execution_time = (time.time() - start_time) * 1000  # ms

# Return result with metadata
return jsonify({
    "success": True,
    "result": result,
    "execution_time_ms": round(execution_time, 2),
    "tool_name": tool_name,
    "params": params
})
```

**Response Format:**
```json
{
  "success": true,
  "result": {
    "Product": "Business Cards - Economical",
    "Quantity": 500,
    "Unit_Cost": "$0.19",
    "Subtotal": "$95.00",
    "GST": "$9.50",
    "Total": "$104.50",
    "Profit_Margin": "65%",
    "Breakdown": {
      "setup_costs": 15.0,
      "stock_cost": 25.0,
      "print_cost": 45.0,
      "finishing_cost": 0.0,
      "artwork_cost": 0.0
    }
  },
  "execution_time_ms": 45.23
}
```

**Alternative Route:** `/api/calculator/list` (Lines 677-700)
- Lists all available calculators from Registry V3
- Used by UI to populate calculator dropdown menus

---

## Layer 3: Registry V3 - Tool Orchestration

**File:** `tools/registry_v3.py` (1,086 lines)

### Purpose
Central orchestrator for ALL tool execution - discovers, loads, and executes 611+ tools across platforms.

### Initialization (Lines 1-200)

**Constructor Flow:**
```python
class RegistryV3:
    def __init__(self):
        self.tools = {}              # Schema definitions
        self.implementations = {}    # Executable functions
        
        # Try Redis cache first (50x faster on cache hit)
        cache_hit = self._load_from_cache()
        
        if not cache_hit:
            # Cache miss - load everything
            self._load_schemas()           # Load from tools/schemas/*.json
            self._load_implementations()   # Load from tools/implementations/
            self._load_module_plugins()    # AUTO-DISCOVER quote-calculator, inhouse-print, etc.
            self._save_to_cache()          # Save to Redis (1-hour TTL)
        
        logger.info(f"Registry V3 initialized: {len(self.tools)} tools loaded")
```

**Module Plugin Auto-Discovery:**
```python
def _load_module_plugins(self):
    """
    Auto-discover modules from UI/modules_external/
    
    Scans for:
    - quote-calculator/tools/*.json (tool definitions)
    - quote-calculator/implementations/*_wrapper.py (implementations)
    - inhouse-print/tools/*.json
    - inhouse-print/implementations/*_wrapper.py
    - shopify/tools/*.json
    - xero/tools/*.json
    """
    modules_dir = self.root_dir / "UI" / "modules_external"
    
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir():
            # Load tool definitions from tools/*.json
            tools_dir = module_dir / "tools"
            if tools_dir.exists():
                for json_file in tools_dir.glob("*.json"):
                    self._load_tool_definition(json_file)
            
            # Load implementations from implementations/*_wrapper.py
            impl_dir = module_dir / "implementations"
            if impl_dir.exists():
                for py_file in impl_dir.glob("*_wrapper.py"):
                    self._load_tool_implementation(py_file)
```

**Key Features:**
- **Thread-local storage** (Lines 35-115) - Stores user_id for authentication in worker threads
- **Redis caching** (Lines 58-65) - 1-hour TTL, 50x faster cache hits
- **Tool Intelligence Logger** (Lines 47-55) - Silent learning system tracking usage patterns
- **Dynamic schema injection** (Lines 157-175) - Replaces {{DYNAMIC:...}} placeholders
- **Security exclusions** (Lines 149-154) - Email sending tools blocked for safety

### Tool Execution (Lines 500-600)

**Method Signature:**
```python
def execute_tool(self, **kwargs) -> Any:
    """
    Execute a tool with proper credential injection + passive user feedback
    
    CRITICAL: This method is intentionally SIMPLE and delegates type conversion
    to individual tool implementations.
    
    Why no automatic type conversion:
    1. Some tools need strings (IDs, dates, text)
    2. Some tools need integers (counts, limits)
    3. Meta-tools break if we auto-convert their string parameters
    4. Wrappers handle type conversion with @tool_executor decorator
    """
```

**Execution Flow for Calculator Request:**
```python
# Line 544 - execute_tool() called from Flask
# kwargs = {
#     "tool_name": "calculate_economical_business_cards_shopify",
#     "quantity": "500",  # Note: string from JSON
#     "print_type": "Colour",
#     "double_sided": true,
#     "celloglaze": "None",
#     "artworks": 1
# }

tool_name = kwargs.pop("tool_name")  # Extract tool name

# Find implementation function
tool_function = self._get_tool_function(tool_name)

# Check if tool needs credential injection (_user_id, _injected_credentials)
if self._needs_credential_injection(tool_name):
    user_id = self.get_thread_user_id()
    kwargs["_user_id"] = user_id
    kwargs["_injected_credentials"] = self._get_credentials(user_id)

# Execute tool function
result = tool_function(**kwargs)

# Log to Tool Intelligence system (silent learning)
if self.intelligence_logger:
    self.intelligence_logger.log_execution(
        tool_name=tool_name,
        parameters=kwargs,
        result=result,
        execution_time_ms=execution_time
    )

return result
```

**Tool Function Discovery:**
```python
def _get_tool_function(self, tool_name):
    """
    Find executable function for tool name.
    
    Search order:
    1. Direct function lookup in self.implementations
       - meta_tools (execute_tool, get_tool_schema)
       - sql_database tools
       - Directly registered functions
    
    2. Module-based lookup
       - Look for tool_name as method in loaded modules
       - Example: "calculate_economical_business_cards_shopify" in calculator_wrapper module
    
    3. Class instance lookup (Microsoft/Google tools)
       - Tool is method on global class instance
       - Example: microsoft_outlook_tools.outlook_list_messages
    
    4. Extract module name from tool name
       - "gmail_send_email" → look for "gmail" module → find send_email method
    """
```

---

## Layer 4: Calculator Wrapper - Type Safety & Translation

**File:** `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py` (5,040 lines)

### Purpose
Translation layer between AI schema (strings, booleans) and backend calculator requirements (specific formats, enums, defaults).

### Architecture (Lines 1-100)

**File Header Comment:**
```python
"""
CALCULATOR WRAPPER - Translation layer for quote calculators
==============================================================

Architecture:
AI Agent Request 
    → Registry V3 
    → calculator_wrapper.py (THIS FILE)
    → backend calculators (Shopify implementations)
    → G_Folder database (Fred)

Current State (Jan 13, 2026):
- GOD calculators: DEACTIVATED (commented out)
- Shopify calculators: ACTIVE (27 implementations)
- SHOPIFY_CALCULATORS_AVAILABLE = True

Type Safety:
- @tool_executor decorator from registry_v3.py
- @calculator_wrapper decorator for parameter validation
- @enforce_schema_types decorator from RestrictedPython
"""
```

**Imports:**
```python
from tools.registry_v3 import tool_executor
from RestrictedPython.schema_validator import enforce_schema_types

# Shopify calculator imports (ACTIVE)
from UI.modules_external.quote-calculator.backend.shopify_calculators.EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from UI.modules_external.quote-calculator.backend.shopify_calculators.PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
from UI.modules_external.quote-calculator.backend.shopify_calculators.Printed_Flyers_Shopify_Calculator import PrintedFlyersShopifyCalculator
# ... 24 more calculator imports
```

### Function Example: Economical Business Cards (Lines 1080-1200)

**Function Signature:**
```python
@tool_executor()  # Registers with Registry V3
@calculator_wrapper(
    quantity_enum=[250, 500, 1000, 2000, 5000, 10000],  # Valid quantities
    validate_params=True  # Enable parameter validation
)
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = "Colour",
    double_sided: bool = True,
    celloglaze: str = "None",
    artworks: int = 1,
    **kwargs
):
    """
    Calculate quote for economical business cards using Shopify pricing.
    
    Economical stock options:
    - 310gsm Satin (standard)
    - 400gsm Silk
    - 350gsm Uncoated
    
    Parameters:
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        print_type: "Colour" or "Black & White"
        double_sided: True for double-sided, False for single-sided
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"
        artworks: Number of artwork designs (1-50, first free, $15 each extra)
    
    Returns:
        Dict with pricing breakdown
    """
```

**Execution Flow:**
```python
# Step 1: Legacy parameter translation (backward compatibility)
if "colour" in kwargs:
    # Old schema used colour (bool), new schema uses print_type (str)
    logger.warning("'colour' parameter deprecated - use 'print_type' instead")
    colour = kwargs.pop("colour")
    if isinstance(colour, bool):
        print_type = "Colour" if colour else "Black & White"

# Step 2: Parameter validation
if print_type not in ["Colour", "Black & White"]:
    raise ValueError(f"print_type must be 'Colour' or 'Black & White', got: {print_type}")

valid_celloglaze = ["None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"]
if celloglaze not in valid_celloglaze:
    raise ValueError(f"celloglaze must be one of {valid_celloglaze}, got: {celloglaze}")

if artworks < 1 or artworks > 50:
    raise ValueError(f"artworks must be 1-50, got: {artworks}")

# Step 3: Type translation (AI schema → Backend schema)
# Backend expects string "Single side print" / "Double side print"
print_sides = "Double side print" if double_sided else "Single side print"

# Step 4: Apply backend defaults (if not provided by AI)
print_type = print_type or "Colour"
celloglaze = celloglaze or "None"
artworks = artworks or 1

# Step 5: Instantiate backend calculator
calculator = EconomicalBusinessCardsShopifyCalculator()

# Step 6: Execute calculation
result = calculator.calculate(
    quantity=quantity,
    print_sides=print_sides,       # Translated from bool to string
    print_type=print_type,         # Validated enum
    finish_size="90mm x 55mm",     # Hardcoded standard size
    paper_stock="satin_310gsm",    # Default economical stock
    artworks=artworks              # Validated 1-50
)

# Step 7: Format result for AI consumption
return {
    "success": True,
    "calculator": "Economical Business Cards (Shopify)",
    "parameters_used": {
        "quantity": quantity,
        "print_sides": print_sides,
        "print_type": print_type,
        "celloglaze": celloglaze,
        "artworks": artworks
    },
    "pricing": result  # Backend calculator result
}
```

**@calculator_wrapper Decorator Responsibilities:**
- **Type conversion:** String "500" → int 500 (decorator auto-converts before function receives it)
- **Quantity validation:** Ensures quantity is in enum [250, 500, 1000, 2000, 5000, 10000]
- **Rounding:** If user requests 375 cards, rounds DOWN to 250 (customer-friendly pricing)
- **Error handling:** Catches validation errors and returns structured error response

**Translation Examples:**
```python
# AI sends (from JSON/WebSocket):
{
  "quantity": "500",           # String
  "double_sided": true,        # Boolean
  "celloglaze": "2 Side Matt"  # String
}

# Wrapper translates to:
{
  "quantity": 500,                        # @calculator_wrapper converts to int
  "print_sides": "Double side print",    # bool → string translation
  "celloglaze": "2 Side Matt"            # Pass through after validation
}

# Backend receives (correct types):
calculator.calculate(
    quantity=500,                    # int
    print_sides="Double side print", # str
    celloglaze="2 Side Matt"         # str
)
```

---

## Layer 5: Backend Calculator - Shopify Implementation

**File:** `UI/modules_external/quote-calculator/backend/shopify_calculators/EconomicalBusinessCards_Shopify_Calculator.py` (450 lines)

### Purpose
Exact implementation of Shopify DPO (Dynamic Pricing Option) JavaScript formula in Python.

### Class Definition (Lines 1-150)

**Class Header:**
```python
class EconomicalBusinessCardsShopifyCalculator:
    """
    Exact implementation of Shopify DPO JavaScript formula for Economical Business Cards
    
    Based on: shopify_economical_business_cards.json specification
    
    Fields:
    - F1 (quantity): Number of business cards
    - F2 (print_sides): "Single side print" or "Double side print"
    - F3 (print_type): "Colour" or "Black & White"
    - F4 (finish_size): "90mm x 55mm" (standard business card)
    - F5 (paper_stock): "satin_310gsm" (economical stock)
    - F6 (artworks): Number of artwork designs (1-50)
    
    Pricing Logic:
    1. Artwork costs: First free, $15 per additional
    2. Cards-per-sheet: 21 cards per sheet (90x55mm on SRA3 sheet)
    3. Sheets needed: ceil(quantity / 21)
    4. Stock cost: sheets * stock_price_per_sheet
    5. Print cost: sheets * print_price_per_sheet * (1 or 2 for single/double)
    6. Finishing cost: Based on celloglaze option
    7. Subtotal: sum of all costs
    8. Profit margin: 13-tier system (50%-90% based on final price)
    9. Retail price: Subtotal * (1 + profit_margin)
    10. GST: Retail * 1.10 (Australian 10% GST)
    """
```

**Constants:**
```python
# Pricing tiers (customer-friendly rounding)
PRICING_TIERS = [250, 500, 1000, 2000, 5000, 10000]

# GST rate (Australia)
GST_RATE = 1.10  # 10% GST

# Price increase multiplier (can be adjusted for market changes)
PRICE_INCREASE_MULTIPLIER = 1.00  # No increase default

# Surcharge (for rush orders, special requirements)
SURCHARGE = 0.00  # No surcharge default

# Cards per sheet (90x55mm business cards on SRA3 sheet)
CARDS_PER_SHEET = 21

# Profit margin tiers (13 levels from 50% to 90%)
PROFIT_MARGINS = {
    0: 0.90,      # 0-50: 90% margin
    50: 0.85,     # 50-100: 85% margin
    100: 0.80,    # 100-200: 80% margin
    200: 0.75,    # 200-500: 75% margin
    500: 0.70,    # 500-1000: 70% margin
    1000: 0.65,   # 1000-2000: 65% margin
    2000: 0.60,   # 2000-5000: 60% margin
    5000: 0.55,   # 5000-10000: 55% margin
    10000: 0.50   # 10000+: 50% margin
}
```

**Constructor:**
```python
def __init__(self, config_path: Optional[str] = None):
    """
    Initialize calculator with optional JSON config
    
    Args:
        config_path: Path to JSON config file (e.g., "shopify_economical_business_cards.json")
                    If None, uses hardcoded pricing
    """
    self.config = {}
    
    # Try to load config via config_manager
    if config_path:
        from .config_manager import config_manager
        self.config = config_manager.load_shopify_config(config_path)
    
    # Pricing loaded from JSON or hardcoded
    self.stock_prices = self.config.get("stock_prices", {
        "satin_310gsm": {"price_per_sheet": 0.25},
        "silk_400gsm": {"price_per_sheet": 0.35},
        "uncoated_350gsm": {"price_per_sheet": 0.30}
    })
    
    self.print_prices = self.config.get("print_prices", {
        "Colour": {"price_per_sheet": 0.15},
        "Black & White": {"price_per_sheet": 0.05}
    })
    
    self.finishing_prices = self.config.get("finishing_prices", {
        "None": 0.0,
        "1 Side Gloss": 0.10,
        "2 Side Gloss": 0.20,
        "1 Side Matt": 0.10,
        "2 Side Matt": 0.20
    })
```

**Main Calculation Method:**
```python
def calculate(
    self,
    quantity: int,
    print_sides: str,
    print_type: str,
    finish_size: str,
    paper_stock: str,
    artworks: int
) -> Dict[str, Any]:
    """
    Calculate quote for business cards
    
    Args:
        quantity: Number of cards (will be rounded to tier)
        print_sides: "Single side print" or "Double side print"
        print_type: "Colour" or "Black & White"
        finish_size: "90mm x 55mm"
        paper_stock: "satin_310gsm" (economical default)
        artworks: Number of designs (1-50)
    
    Returns:
        {
            "Product": "Business Cards - Economical",
            "Quantity": 500,
            "Unit_Cost": "$0.19",
            "Subtotal": "$95.00",
            "GST": "$9.50",
            "Total": "$104.50",
            "Profit_Margin": "65%",
            "Breakdown": {
                "setup_costs": 15.0,
                "stock_cost": 25.0,
                "print_cost": 45.0,
                "finishing_cost": 10.0,
                "artwork_cost": 0.0
            }
        }
    """
    
    # Step 1: Defensive type conversion (handle AI sending strings)
    quantity = int(quantity) if not isinstance(quantity, int) else quantity
    artworks = int(artworks) if not isinstance(artworks, int) else artworks
    
    # Step 2: Round quantity to pricing tier
    quantity = self._round_to_pricing_tier(quantity)
    
    # Step 3: Calculate sheets needed
    sheets_needed = math.ceil(quantity / self.CARDS_PER_SHEET)
    
    # Step 4: Calculate costs
    
    # Artwork setup (first free, $15 each extra)
    artwork_cost = max(0, artworks - 1) * 15.0
    
    # Stock cost
    stock_price_per_sheet = self.stock_prices[paper_stock]["price_per_sheet"]
    stock_cost = sheets_needed * stock_price_per_sheet
    
    # Print cost (double for double-sided)
    print_price_per_sheet = self.print_prices[print_type]["price_per_sheet"]
    sides_multiplier = 2 if print_sides == "Double side print" else 1
    print_cost = sheets_needed * print_price_per_sheet * sides_multiplier
    
    # Finishing cost (celloglaze)
    celloglaze = "None"  # Default if not in parameters
    finishing_cost = self.finishing_prices.get(celloglaze, 0.0) * sheets_needed
    
    # Step 5: Calculate subtotal
    subtotal = artwork_cost + stock_cost + print_cost + finishing_cost
    
    # Step 6: Apply profit margin
    profit_margin = self._get_profit_margin(subtotal)
    retail_price = subtotal * (1 + profit_margin)
    
    # Step 7: Apply price increase multiplier (market adjustments)
    retail_price *= self.PRICE_INCREASE_MULTIPLIER
    
    # Step 8: Add surcharge (rush orders, special requirements)
    retail_price += self.SURCHARGE
    
    # Step 9: Calculate GST
    gst_amount = retail_price * 0.10  # 10% GST
    total_with_gst = retail_price * self.GST_RATE
    
    # Step 10: Calculate unit cost
    unit_cost = retail_price / quantity
    
    # Step 11: Format result
    return {
        "Product": "Business Cards - Economical",
        "Quantity": quantity,
        "Unit_Cost": f"${unit_cost:.2f}",
        "Subtotal": f"${retail_price:.2f}",
        "GST": f"${gst_amount:.2f}",
        "Total": f"${total_with_gst:.2f}",
        "Profit_Margin": f"{profit_margin*100:.0f}%",
        "Breakdown": {
            "setup_costs": 0.0,           # No setup costs for this product
            "stock_cost": stock_cost,
            "print_cost": print_cost,
            "finishing_cost": finishing_cost,
            "artwork_cost": artwork_cost,
            "sheets_needed": sheets_needed,
            "cards_per_sheet": self.CARDS_PER_SHEET
        }
    }
```

**Helper Methods:**
```python
def _round_to_pricing_tier(self, quantity: int) -> int:
    """
    Round quantity to nearest pricing tier (customer-friendly - rounds DOWN)
    
    Examples:
    - 375 → 250 (rounds down to lower tier for better unit price)
    - 500 → 500 (exact match)
    - 847 → 500 (rounds down)
    - 1200 → 1000 (rounds down)
    """
    for i in range(len(self.PRICING_TIERS)):
        if quantity <= self.PRICING_TIERS[i]:
            return self.PRICING_TIERS[i]
    
    # If quantity exceeds highest tier, return highest tier
    return self.PRICING_TIERS[-1]

def _get_profit_margin(self, subtotal: float) -> float:
    """
    Get profit margin based on subtotal (13-tier system)
    
    Examples:
    - $25 subtotal → 90% margin (low-value jobs need higher margins)
    - $150 subtotal → 75% margin
    - $800 subtotal → 65% margin
    - $5000 subtotal → 55% margin (high-value jobs can have lower margins)
    """
    for threshold in sorted(self.PROFIT_MARGINS.keys(), reverse=True):
        if subtotal >= threshold:
            return self.PROFIT_MARGINS[threshold]
    
    # Default to highest margin for very low values
    return self.PROFIT_MARGINS[0]
```

---

## Layer 6: Config Manager - JSON Pricing Loader

**File:** `UI/modules_external/quote-calculator/backend/shopify_calculators/config_manager.py` (100 lines)

### Purpose
Load Shopify calculator configuration files from G_Folder (JSON pricing data).

### Implementation

**Class Definition:**
```python
class ConfigManager:
    """
    Config manager for Shopify calculators
    
    Purpose:
    - Some calculators have hardcoded pricing (e.g., EconomicalBusinessCards)
    - Some calculators load pricing from JSON (e.g., SaddleStitchBooks)
    - ConfigManager provides unified interface for both patterns
    """
    
    # Config file search paths
    CONFIG_PATHS = [
        Path(__file__).parent.parent.parent / "config" / "shopify",  
        # Resolves to: AI_agents/UI/modules_external/quote-calculator/config/shopify
        
        r"c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\config\shopify"
        # Absolute fallback path
    ]
    
    def __init__(self):
        """Initialize empty config dictionary"""
        self.config = {}
    
    def load_shopify_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load Shopify config file from G_Folder
        
        Args:
            config_file: Filename (e.g., "Shopify_Saddle_Stitch_Books.json")
        
        Returns:
            Dict with config data, or empty dict if file not found
            
        Examples:
            # Calculator with config file
            config = config_manager.load_shopify_config("Shopify_Saddle_Stitch_Books.json")
            # Returns: {"stock_prices": {...}, "print_prices": {...}, "binding_costs": {...}}
            
            # Calculator without config file (hardcoded pricing)
            config = config_manager.load_shopify_config("nonexistent.json")
            # Returns: {} (empty dict, calculator uses hardcoded values)
        """
        # Try each config path
        for base_path in self.CONFIG_PATHS:
            try:
                config_path = Path(base_path) / config_file
                
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    logger.info(f"[CONFIG] Loaded {config_file} from {config_path}")
                    return data
                    
            except Exception as e:
                logger.warning(f"[CONFIG] Error loading {config_file} from {base_path}: {e}")
                continue
        
        # File not found in any location - return empty dict
        # Most calculators have hardcoded pricing and don't need config
        logger.debug(f"[CONFIG] No config file found for {config_file} - using hardcoded pricing")
        return {}

# Global singleton instance
config_manager = ConfigManager()
```

**Usage in Calculators:**
```python
# Calculator initialization (EconomicalBusinessCards example)
class EconomicalBusinessCardsShopifyCalculator:
    def __init__(self, config_path: Optional[str] = None):
        # Try to load config
        if config_path:
            from .config_manager import config_manager
            self.config = config_manager.load_shopify_config(config_path)
        else:
            self.config = {}
        
        # Use config or fallback to hardcoded pricing
        self.stock_prices = self.config.get("stock_prices", {
            "satin_310gsm": {"price_per_sheet": 0.25},  # Hardcoded fallback
            "silk_400gsm": {"price_per_sheet": 0.35}
        })
```

**Config File Structure (Example: Shopify_Saddle_Stitch_Books.json):**
```json
{
  "stock_prices": {
    "80gsm_bond": {"price_per_sheet": 0.02},
    "100gsm_gloss": {"price_per_sheet": 0.03},
    "150gsm_silk": {"price_per_sheet": 0.05}
  },
  "print_prices": {
    "black_and_white": {"price_per_sheet": 0.01},
    "full_colour": {"price_per_sheet": 0.03}
  },
  "binding_costs": {
    "saddle_stitch": {"base_cost": 2.50, "per_page": 0.05}
  },
  "cover_options": {
    "standard": 0.0,
    "laminated": 1.50,
    "spot_uv": 3.00
  }
}
```

---

## Layer 7: Database Integration (Fred/G_Folder)

**File:** `UI/modules_external/inhouse-print/db_connector.py`

### Purpose
Connect to "Fred" (InHouse Print database - G_Folder/In_House_SQL) for live pricing data, customer records, job tickets, stock levels.

### Class Definition (Line 29)

**InHousePrintDB Class:**
```python
class InHousePrintDB:
    """
    Database connector for InHouse Print (Fred)
    
    Features:
    - Auto-detects Render environment vs local development
    - Fetches credentials from Supabase (ai_infrastructure.user_platform_credentials)
    - Executes SQL queries with pandas DataFrame results
    - Used by calculators for live pricing data (optional)
    """
    
    def __init__(self):
        """Initialize database connection"""
        # Check if running on Render (production)
        is_render = os.getenv('RENDER') == 'true'
        
        if is_render:
            # Production: Fetch credentials from Supabase
            self.connection_string = self._fetch_credentials_from_supabase()
        else:
            # Local: Use environment variable
            self.connection_string = os.getenv('INHOUSE_PRINT_CONNECTION_STRING')
        
        if not self.connection_string:
            raise ValueError("InHouse Print database credentials not configured")
    
    def _fetch_credentials_from_supabase(self) -> str:
        """
        Fetch InHouse Print credentials from Supabase
        
        Query: SELECT connection_string 
               FROM ai_infrastructure.user_platform_credentials 
               WHERE platform = 'inhouse_print' AND user_id = 1
        """
        from AI_infrastructure.shared.database_utils import execute_query
        
        result = execute_query(
            "SELECT connection_string FROM ai_infrastructure.user_platform_credentials "
            "WHERE platform = %s AND user_id = %s",
            ('inhouse_print', 1),
            fetch_mode='value'
        )
        
        return result
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Execute SQL query against InHouse Print database
        
        Args:
            query: SQL query string (e.g., "SELECT TOP 10 * FROM JobTickets WHERE CustomerID = ?")
            params: Query parameters tuple (e.g., (12345,))
        
        Returns:
            pandas DataFrame with query results
        
        Examples:
            # Get recent job tickets
            df = db.execute_query("SELECT TOP 10 * FROM JobTickets ORDER BY DateCreated DESC")
            
            # Get customer order history
            df = db.execute_query(
                "SELECT * FROM JobTickets WHERE CustomerID = ? AND DateCreated >= ?",
                (12345, '2024-01-01')
            )
        """
        import pyodbc
        
        conn = pyodbc.connect(self.connection_string)
        try:
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            conn.close()
```

**Usage in Calculators (Optional - Live Pricing):**
```python
# Most calculators use hardcoded/JSON pricing
# Some calculators CAN query Fred for live pricing data

class AdvancedCalculator:
    def __init__(self):
        # Initialize DB connector
        try:
            from UI.modules_external.inhouse-print.db_connector import InHousePrintDB
            self.db = InHousePrintDB()
            self.use_live_pricing = True
        except Exception as e:
            logger.warning(f"Database unavailable - using hardcoded pricing: {e}")
            self.use_live_pricing = False
    
    def calculate(self, quantity, product_type):
        if self.use_live_pricing:
            # Query Fred for current stock prices
            df = self.db.execute_query(
                "SELECT PricePerSheet FROM StockPricing WHERE StockType = ?",
                (product_type,)
            )
            stock_price = df['PricePerSheet'].iloc[0]
        else:
            # Fallback to hardcoded pricing
            stock_price = 0.25
        
        # ... rest of calculation
```

**Database Schema (Fred/G_Folder):**
```
Common Tables:
- JobTickets: Customer orders, pricing, specifications
- Customers: Customer details, contact info, credit terms
- StockPricing: Current stock prices per sheet/unit
- Products: Product catalog, specifications
- Pricing: Historical pricing data
- StockLevels: Current inventory (not actively tracked per user note)
```

---

## Complete Execution Pathway - Step-by-Step Example

### Request: "Calculate 500 economical business cards, double-sided, colour"

**Step 1: AI Agent System Prompt Processing**
```
File: tool_usage_system_prompt.md
Line: 2508

AI Agent receives user message: "Calculate 500 economical business cards, double-sided, colour"

AI Agent thinks (guided by system prompt):
1. This is a printing/calculator request
2. Must call inhouse_get_domain_guide() first (MANDATORY)
3. Then call inhouse_calculator_guide() to learn calculators
4. Then call inhouse_get_calculator_requirements() for parameter schema
5. Then execute calculation
6. Present breakdown and validate math

AI Agent decides:
- tool_name: "calculate_economical_business_cards_shopify"
- parameters: {
    "quantity": 500,
    "print_type": "Colour",
    "double_sided": true,
    "celloglaze": "None",
    "artworks": 1
  }
```

**Step 2: HTTP Request to Flask**
```
POST /api/test-calculator
Content-Type: application/json

{
  "tool_name": "calculate_economical_business_cards_shopify",
  "params": {
    "quantity": "500",        ← Note: JSON sends as string
    "print_type": "Colour",
    "double_sided": true,
    "celloglaze": "None",
    "artworks": 1
  }
}

Flask receives request at line 640 (flask_app.py)
```

**Step 3: Registry V3 Initialization & Lookup**
```python
# flask_app.py line 653
registry = RegistryV3()

# Registry initializes (if not cached):
# 1. Load schemas from tools/schemas/*.json (meta-tools)
# 2. Load implementations from tools/implementations/ (meta-tools)
# 3. Auto-discover modules from UI/modules_external/:
#    - quote-calculator/tools/*.json (calculator definitions)
#    - quote-calculator/implementations/calculator_wrapper.py (implementations)
# 4. Total tools loaded: 611+

# Registry lookup:
registry.tools["calculate_economical_business_cards_shopify"] = {
  "name": "calculate_economical_business_cards_shopify",
  "description": "Calculate quote for economical business cards...",
  "platform": "quote_calculator",
  "parameters": {
    "quantity": {"type": "integer", "enum": [250, 500, 1000, 2000, 5000, 10000]},
    "print_type": {"type": "string", "enum": ["Colour", "Black & White"]},
    "double_sided": {"type": "boolean"},
    "celloglaze": {"type": "string", "enum": ["None", "1 Side Gloss", ...]},
    "artworks": {"type": "integer", "minimum": 1, "maximum": 50}
  }
}

registry.implementations["calculate_economical_business_cards_shopify"] = <function object>
```

**Step 4: Registry V3 Execution**
```python
# flask_app.py line 657
result = registry.execute_tool(
    tool_name="calculate_economical_business_cards_shopify",
    quantity="500",        ← String from JSON
    print_type="Colour",
    double_sided=True,
    celloglaze="None",
    artworks=1
)

# registry_v3.py line 544
def execute_tool(self, **kwargs):
    tool_name = kwargs.pop("tool_name")  # Extract tool name
    
    # Find implementation function
    tool_function = self._get_tool_function(tool_name)
    # Returns: calculate_economical_business_cards_shopify function from calculator_wrapper.py
    
    # Check if needs credential injection (this tool doesn't)
    # Credential injection used for Google/Microsoft tools
    
    # Execute tool
    result = tool_function(**kwargs)
    # Calls: calculate_economical_business_cards_shopify(
    #     quantity="500",
    #     print_type="Colour",
    #     double_sided=True,
    #     celloglaze="None",
    #     artworks=1
    # )
    
    return result
```

**Step 5: Calculator Wrapper Translation**
```python
# calculator_wrapper.py line 1091
@tool_executor()  # Registered with Registry V3
@calculator_wrapper(quantity_enum=[250, 500, 1000, 2000, 5000, 10000], validate_params=True)
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = "Colour",
    double_sided: bool = True,
    celloglaze: str = "None",
    artworks: int = 1,
    **kwargs
):
    # @calculator_wrapper decorator already converted:
    # quantity: "500" (string) → 500 (int)
    
    # Validate parameters
    if print_type not in ["Colour", "Black & White"]:
        raise ValueError(...)
    
    if celloglaze not in ["None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"]:
        raise ValueError(...)
    
    if artworks < 1 or artworks > 50:
        raise ValueError(...)
    
    # Translate bool to backend string format
    print_sides = "Double side print" if double_sided else "Single side print"
    
    # Instantiate backend calculator
    calculator = EconomicalBusinessCardsShopifyCalculator()
    
    # Execute calculation
    result = calculator.calculate(
        quantity=500,                        ← int (converted by decorator)
        print_sides="Double side print",     ← string (translated from bool)
        print_type="Colour",                 ← string (validated)
        finish_size="90mm x 55mm",           ← hardcoded standard
        paper_stock="satin_310gsm",          ← hardcoded economical default
        artworks=1                           ← int (validated)
    )
    
    return {
        "success": True,
        "calculator": "Economical Business Cards (Shopify)",
        "pricing": result
    }
```

**Step 6: Backend Calculator Execution**
```python
# EconomicalBusinessCards_Shopify_Calculator.py line 1
class EconomicalBusinessCardsShopifyCalculator:
    def calculate(self, quantity, print_sides, print_type, finish_size, paper_stock, artworks):
        # Step 1: Defensive type conversion
        quantity = int(quantity)  # Already int, but defensive
        artworks = int(artworks)
        
        # Step 2: Round to pricing tier
        quantity = self._round_to_pricing_tier(500)  # Returns: 500 (exact match)
        
        # Step 3: Calculate sheets
        sheets_needed = math.ceil(500 / 21)  # 21 cards per sheet = 24 sheets
        
        # Step 4: Calculate costs
        artwork_cost = max(0, 1 - 1) * 15.0 = 0.0  # First artwork free
        stock_cost = 24 * 0.25 = 6.00  # 24 sheets * $0.25/sheet
        print_cost = 24 * 0.15 * 2 = 7.20  # 24 sheets * $0.15/sheet * 2 sides
        finishing_cost = 0.0  # No celloglaze
        
        # Step 5: Subtotal
        subtotal = 0.0 + 6.00 + 7.20 + 0.0 = 13.20
        
        # Step 6: Profit margin (13-tier system)
        profit_margin = self._get_profit_margin(13.20)  # Returns: 0.90 (90% for low-value jobs)
        
        # Step 7: Retail price
        retail_price = 13.20 * (1 + 0.90) = 25.08
        
        # Step 8: Price increase (none)
        retail_price *= 1.00 = 25.08
        
        # Step 9: Add surcharge (none)
        retail_price += 0.00 = 25.08
        
        # Step 10: GST
        gst_amount = 25.08 * 0.10 = 2.51
        total_with_gst = 25.08 * 1.10 = 27.59
        
        # Step 11: Unit cost
        unit_cost = 25.08 / 500 = 0.05
        
        # Step 12: Format result
        return {
            "Product": "Business Cards - Economical",
            "Quantity": 500,
            "Unit_Cost": "$0.05",
            "Subtotal": "$25.08",
            "GST": "$2.51",
            "Total": "$27.59",
            "Profit_Margin": "90%",
            "Breakdown": {
                "setup_costs": 0.0,
                "stock_cost": 6.00,
                "print_cost": 7.20,
                "finishing_cost": 0.0,
                "artwork_cost": 0.0,
                "sheets_needed": 24,
                "cards_per_sheet": 21
            }
        }
```

**Step 7: Config Manager (Optional - Not Used in This Example)**
```python
# EconomicalBusinessCards calculator uses hardcoded pricing
# Some calculators load JSON pricing:

calculator = SaddleStitchBooksShopifyCalculator(
    config_path="Shopify_Saddle_Stitch_Books.json"
)

# Constructor calls:
from .config_manager import config_manager
self.config = config_manager.load_shopify_config("Shopify_Saddle_Stitch_Books.json")

# Config manager searches:
# 1. AI_agents/UI/modules_external/quote-calculator/config/shopify/Shopify_Saddle_Stitch_Books.json
# 2. c:\Users\gpoli\...\config\shopify\Shopify_Saddle_Stitch_Books.json

# If found:
# Returns: {"stock_prices": {...}, "print_prices": {...}, "binding_costs": {...}}

# If not found:
# Returns: {} (calculator uses hardcoded fallback)
```

**Step 8: Database Integration (Optional - Not Used in This Example)**
```python
# Most calculators don't query Fred database
# Database is used for:
# 1. Customer lookup (order history, credit terms)
# 2. Job ticket creation
# 3. Stock level checks (not actively tracked per user note)
# 4. Historical pricing data

# Example database query:
from UI.modules_external.inhouse-print.db_connector import InHousePrintDB
db = InHousePrintDB()

# Query recent job tickets
df = db.execute_query(
    "SELECT TOP 10 * FROM JobTickets WHERE CustomerID = ? ORDER BY DateCreated DESC",
    (12345,)
)

# Query stock prices (if live pricing enabled)
df = db.execute_query(
    "SELECT PricePerSheet FROM StockPricing WHERE StockType = ?",
    ('satin_310gsm',)
)
stock_price = df['PricePerSheet'].iloc[0]
```

**Step 9: Result Flows Back Through Layers**
```python
# Backend calculator → Wrapper
calculator.calculate(...) returns result dict

# Wrapper → Registry
return {
    "success": True,
    "calculator": "Economical Business Cards (Shopify)",
    "pricing": result
}

# Registry → Flask
result = registry.execute_tool(...) returns wrapper response

# Flask → HTTP Response
return jsonify({
    "success": True,
    "result": result,
    "execution_time_ms": 45.23,
    "tool_name": "calculate_economical_business_cards_shopify",
    "params": {...}
})

# HTTP → AI Agent
AI Agent receives JSON response:
{
  "success": true,
  "result": {
    "success": true,
    "calculator": "Economical Business Cards (Shopify)",
    "pricing": {
      "Product": "Business Cards - Economical",
      "Quantity": 500,
      "Unit_Cost": "$0.05",
      "Subtotal": "$25.08",
      "GST": "$2.51",
      "Total": "$27.59",
      "Profit_Margin": "90%",
      "Breakdown": {
        "setup_costs": 0.0,
        "stock_cost": 6.00,
        "print_cost": 7.20,
        "finishing_cost": 0.0,
        "artwork_cost": 0.0
      }
    }
  },
  "execution_time_ms": 45.23
}

# AI Agent → User (Following 8-Stage Transparency Protocol)
AI Agent formats response per system prompt:

"I've calculated your quote for 500 economical business cards:

**Quote Summary:**
- Product: Business Cards - Economical
- Quantity: 500 cards
- Unit Cost: $0.05 per card

**Cost Breakdown:**
- Stock Cost (24 sheets @ $0.25): $6.00
- Print Cost (24 sheets @ $0.15, double-sided): $7.20
- Finishing Cost: $0.00
- Artwork Cost: $0.00 (first design free)

**Pricing:**
- Subtotal: $25.08
- GST (10%): $2.51
- **Total: $27.59**

Profit Margin: 90% (standard for orders under $50)

Would you like to adjust the quantity or add celloglaze finishing?"
```

---

## Key Integration Points

### 1. Type Safety & Conversion

**Problem:** AI sends JSON with string values, but calculators need proper types.

**Solution:** Multi-layer type conversion:

```python
# Layer 1: AI Agent (Claude) - Sends JSON
{
  "quantity": "500",           # String (JSON limitation)
  "double_sided": true,        # Boolean (JSON native)
  "print_type": "Colour"       # String
}

# Layer 2: Flask - Receives JSON, passes to Registry
request.json = {
  "tool_name": "calculate_economical_business_cards_shopify",
  "params": {
    "quantity": "500",         # Still string
    "double_sided": true,
    "print_type": "Colour"
  }
}

# Layer 3: Registry V3 - No type conversion (intentional)
# Passes parameters as-is to tool function

# Layer 4: Calculator Wrapper - @calculator_wrapper decorator converts
@calculator_wrapper(quantity_enum=[250, 500, 1000, 2000, 5000, 10000])
def calculate_economical_business_cards_shopify(quantity: int, ...):
    # Decorator has ALREADY converted:
    # quantity: "500" → 500 (int)
    
    # Decorator has ALREADY validated:
    # quantity must be in [250, 500, 1000, 2000, 5000, 10000]
    
    # If quantity was 375, decorator rounded to 250 (customer-friendly)

# Layer 5: Backend Calculator - Defensive type conversion
quantity = int(quantity) if not isinstance(quantity, int) else quantity
# Extra safety in case wrapper decorator bypassed
```

### 2. Parameter Translation

**Problem:** AI schema uses simple types (bool, enum), backend expects specific strings.

**Solution:** Wrapper layer translates:

```python
# AI Schema:
{
  "double_sided": true,                    # Boolean
  "print_type": "Colour",                  # Simple enum
  "celloglaze": "2 Side Matt"              # Simple string
}

# Backend Calculator Schema:
{
  "print_sides": "Double side print",      # Specific string format
  "print_type": "Colour",                  # Matches (no translation needed)
  "celloglaze": "2 Side Matt"              # Matches (no translation needed)
}

# Wrapper Translation:
print_sides = "Double side print" if double_sided else "Single side print"
```

### 3. Error Handling

**Error Flow:** Backend → Wrapper → Registry → Flask → AI Agent → User

```python
# Backend Calculator Error:
if artworks < 1 or artworks > 50:
    raise ValueError("artworks must be 1-50, got: 0")

# Wrapper Catches:
try:
    result = calculator.calculate(...)
except ValueError as e:
    return {
        "success": False,
        "error": str(e),
        "calculator": "Economical Business Cards (Shopify)"
    }

# Registry Propagates:
result = tool_function(**kwargs)
# If result["success"] == False, Registry logs and returns error

# Flask Returns HTTP 500:
return jsonify({
    "success": False,
    "error": "artworks must be 1-50, got: 0",
    "traceback": "..."
}), 500

# AI Agent Interprets:
"I encountered an error calculating your quote: artworks must be 1-50. 
How many artwork designs do you need? (First design is free, $15 per additional)"
```

### 4. Configuration Loading

**Hardcoded vs JSON Pricing:**

```python
# Pattern 1: Hardcoded Pricing (EconomicalBusinessCards)
class EconomicalBusinessCardsShopifyCalculator:
    def __init__(self):
        # No config file needed
        self.stock_prices = {
            "satin_310gsm": {"price_per_sheet": 0.25},
            "silk_400gsm": {"price_per_sheet": 0.35}
        }

# Pattern 2: JSON Pricing (SaddleStitchBooks)
class SaddleStitchBooksShopifyCalculator:
    def __init__(self, config_path="Shopify_Saddle_Stitch_Books.json"):
        from .config_manager import config_manager
        self.config = config_manager.load_shopify_config(config_path)
        
        # Use config or fallback
        self.stock_prices = self.config.get("stock_prices", {
            # Hardcoded fallback if JSON missing
            "80gsm_bond": {"price_per_sheet": 0.02}
        })
```

### 5. Database Integration

**Live Pricing vs Hardcoded:**

```python
# Pattern 1: No Database (Most Calculators)
class EconomicalBusinessCardsShopifyCalculator:
    def calculate(...):
        # Use hardcoded or JSON pricing
        stock_price = 0.25

# Pattern 2: Optional Database (Advanced Calculators)
class AdvancedCalculator:
    def __init__(self):
        try:
            from UI.modules_external.inhouse-print.db_connector import InHousePrintDB
            self.db = InHousePrintDB()
            self.use_live_pricing = True
        except:
            self.use_live_pricing = False
    
    def calculate(...):
        if self.use_live_pricing:
            df = self.db.execute_query(
                "SELECT PricePerSheet FROM StockPricing WHERE StockType = ?",
                (stock_type,)
            )
            stock_price = df['PricePerSheet'].iloc[0]
        else:
            stock_price = 0.25  # Fallback
```

---

## Production vs Testing Routes

### Production Route (This Document)

```
User Request → AI Agent → Flask (/api/test-calculator) → Registry V3 → Wrapper → Backend → Result
```

**Used By:**
- Production platform (business-ai-platform-v2.html)
- Real customer quotes
- AI agents (Claude)
- WebSocket connections

**Characteristics:**
- HTTP POST requests
- JSON request/response
- Full type conversion chain
- Error handling at every layer
- Tool Intelligence logging
- Redis caching
- Execution time tracking

### Testing Route (NOT This Document)

```
Manual Python Script → Direct Calculator Import → Backend.calculate() → Result
```

**Used By:**
- Development testing
- Unit tests
- Calculator alignment analysis
- Direct Python invocation

**Example Testing Code:**
```python
# TESTING ROUTE (bypasses AI, Flask, Registry, Wrapper)
from UI.modules_external.quote-calculator.backend.shopify_calculators.EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator

calculator = EconomicalBusinessCardsShopifyCalculator()
result = calculator.calculate(
    quantity=500,
    print_sides="Double side print",  # Must use exact string format
    print_type="Colour",
    finish_size="90mm x 55mm",
    paper_stock="satin_310gsm",
    artworks=1
)
print(result)
```

**Differences:**
- No HTTP layer
- No Registry lookup
- No wrapper translation
- No type conversion (must provide exact types)
- No error handling wrapper
- No logging
- No caching
- Direct Python function call

---

## System Design Principles

### 1. Separation of Concerns

**Each Layer Has Clear Responsibility:**
- **AI Agent:** User intent interpretation, workflow orchestration
- **Flask:** HTTP routing, request/response handling
- **Registry V3:** Tool discovery, credential injection, execution orchestration
- **Wrapper:** Type conversion, parameter validation, translation
- **Backend:** Business logic, pricing calculations
- **Config Manager:** Configuration loading
- **Database:** Live data integration (optional)

### 2. Type Safety

**Multi-Layer Type Enforcement:**
- **Schema Definition:** JSON schema declares types (integer, string, boolean)
- **Wrapper Decorator:** @calculator_wrapper converts and validates
- **Backend Defensive:** Defensive type conversion in calculator
- **Error Messages:** Clear type errors propagate to user

### 3. Error Handling

**Fail-Safe at Every Layer:**
- **Backend:** Raises ValueError for invalid parameters
- **Wrapper:** try/except catches and returns structured errors
- **Registry:** Logs errors, propagates structured responses
- **Flask:** Returns HTTP 500 with error details
- **AI Agent:** Interprets error, asks user for correction

### 4. Configuration Flexibility

**Multiple Pricing Sources:**
- **Hardcoded:** Fast, reliable, no dependencies (EconomicalBusinessCards)
- **JSON Config:** Flexible, updatable without code changes (SaddleStitchBooks)
- **Database:** Live pricing, customer-specific rates (Advanced calculators)

### 5. Caching & Performance

**Redis Caching:**
- Registry loads from cache (50x faster)
- 1-hour TTL (balances freshness vs performance)
- Cache invalidation on tool changes

**Execution Time Tracking:**
- Every tool execution timed
- Logged to Tool Intelligence system
- Used for performance optimization

### 6. Observability

**Tool Intelligence Logging:**
- Silent learning system (no user-facing output)
- Tracks usage patterns
- Identifies common parameter combinations
- Detects errors and edge cases
- Generates AI observations for improvement

---

## Common Calculators Inventory

**27 Shopify Calculators (Active):**

1. calculate_business_cards (General - routes to Premium/Economical)
2. calculate_economical_business_cards_shopify (310gsm satin)
3. calculate_premium_business_cards_shopify (400gsm silk)
4. calculate_flyers (General)
5. calculate_printed_flyers_shopify
6. calculate_folded_flyers_shopify
7. calculate_booklets (General)
8. calculate_wire_bound_books_shopify
9. calculate_spiral_bound_books_shopify
10. calculate_perfect_bound_books_shopify
11. calculate_saddle_stitch_books_shopify
12. calculate_spiral_books_simple_shopify
13. calculate_letterheads
14. calculate_corflute_signs_shopify
15. calculate_bollard_signs
16. calculate_construction_signs
17. calculate_custom_vinyl_stickers
18. calculate_luxury_classic_pull_up_banners
19. calculate_premium_pull_up_banners
20. calculate_standard_pull_up_banners
21. calculate_metal_face_a_frame
22. calculate_pvc_face_a_frame
23. calculate_strut_cards_a4
24. calculate_strut_cards_a5
25. calculate_wedding_invitations
26. calculate_carbonless_books
27. calculate_perforated_business_cards

**GOD Calculators (Deactivated Jan 13, 2026):**
- calculate_flyers_god
- calculate_letterheads_god
- calculate_perfect_bound_books_god
- calculate_booklets_god

---

## Future Enhancements

### Planned Improvements

1. **Live Database Pricing**
   - Enable calculators to query Fred for real-time stock prices
   - Customer-specific pricing based on relationship history
   - Volume discount tiers from database

2. **Enhanced Caching**
   - Cache calculator results for common parameter combinations
   - Reduce execution time from 45ms to <5ms for cached quotes
   - Cache invalidation on price updates

3. **Tool Intelligence Insights**
   - AI-generated recommendations based on usage patterns
   - Common parameter presets (e.g., "Standard 500 cards" = pre-filled form)
   - Error pattern detection and automatic fixes

4. **Parameter Validation Improvements**
   - Pre-execution validation at Registry layer
   - Better error messages with correction suggestions
   - Auto-correction for common mistakes (e.g., "doublesided" → "double_sided")

5. **Multi-User Support**
   - User-specific pricing tiers (trade customers vs retail)
   - Saved quote templates per user
   - Quote history and re-order functionality

---

## Key Files Reference

**System Prompt:**
- `AI_infrastructure/prompts/tool_usage_system_prompt.md` (2,709 lines)

**Flask Server:**
- `AI_infrastructure/flask_app.py` (4,192 lines)
  - Route: `/api/test-calculator` (line 630)
  - Route: `/api/calculator/list` (line 677)

**Registry:**
- `tools/registry_v3.py` (1,086 lines)
  - Class: `RegistryV3` (line 27)
  - Method: `execute_tool()` (line 544)

**Calculator Wrapper:**
- `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py` (5,040 lines)
  - Function: `calculate_economical_business_cards_shopify()` (line 1091)
  - Function: `calculate_business_cards()` (line 112)

**Backend Calculators:**
- `UI/modules_external/quote-calculator/backend/shopify_calculators/`
  - `EconomicalBusinessCards_Shopify_Calculator.py` (450 lines)
  - `PremiumBusinessCards_Shopify_Calculator.py`
  - `PrintedFlyers_Shopify_Calculator.py`
  - ... 24 more calculator files

**Config Manager:**
- `UI/modules_external/quote-calculator/backend/shopify_calculators/config_manager.py` (100 lines)

**Database Connector:**
- `UI/modules_external/inhouse-print/db_connector.py`
  - Class: `InHousePrintDB` (line 29)
  - Method: `execute_query()` (line 185)

---

## Summary

This analysis documents the **PRODUCTION PATHWAY** - the actual route used by AI agents in the platform to execute calculator requests.

**Key Takeaways:**

1. **7 Layers:** AI Agent → Flask → Registry → Wrapper → Backend → Config → Database
2. **Type Safety:** Multi-layer conversion from JSON strings to proper types
3. **Translation:** Wrapper translates AI-friendly parameters to backend formats
4. **Error Handling:** Fail-safe at every layer with structured error responses
5. **Configuration:** Flexible pricing (hardcoded, JSON, or database)
6. **Caching:** Redis caching for 50x faster tool loading
7. **Observability:** Tool Intelligence logging for continuous improvement

**Execution Time:** Typical quote calculation takes 45-50ms end-to-end.

**Tool Count:** 611+ tools across all platforms (calculators, Google, Microsoft, Xero, Shopify, etc.)

---

**Document Version:** 1.0  
**Last Updated:** January 22, 2026  
**Maintained By:** AI Agents Development Team
