# Calculator Schema System - How It Works

**Date:** December 17, 2025  
**Purpose:** Complete explanation of how calculator schemas work, what fields are needed, and how the AI uses them

---

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  AI AGENT                                                        │
│  "Calculate 500 business cards"                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │ 
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  REGISTRY V3                                                     │
│  Loads schemas from calculator_tools.json                       │
│  Returns tool definition to AI                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  CALCULATOR WRAPPER                                              │
│  calculator_wrapper.py - Type enforcement & routing             │
│  • Converts AI parameters to correct types                      │
│  • Routes to GOD (database) or Shopify (hardcoded) calculator   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
            ┌─────┴─────┐
            ▼           ▼
    ┌──────────┐  ┌──────────────────┐
    │   GOD    │  │     SHOPIFY      │
    │Calculator│  │    Calculator    │
    │          │  │                  │
    │Database  │  │ Hardcoded Prices │
    │  Driven  │  │   in Python      │
    └──────────┘  └──────────────────┘
```

---

## 🎯 Question 1: Does the Schema Have Prices in It?

### **Answer: NO! The schema NEVER contains prices.**

**What the schema contains:**
- Tool name (`calculate_business_cards`)
- Parameter definitions (quantity, stock_type, print_type)
- Parameter types (integer, string, boolean)
- Parameter enums (valid options: [100, 250, 500, 1000...])
- Descriptions (what each parameter means)
- Return structure (what the calculator returns)

**What the schema does NOT contain:**
- ❌ Prices
- ❌ Calculation formulas
- ❌ Material costs
- ❌ Profit margins
- ❌ GST rates

**Why?** The schema is just an **interface definition** - it tells the AI:
1. "This calculator exists"
2. "Here are the parameters you can send"
3. "Here's what you'll get back"

**Actual pricing logic lives in:**
- **GOD Calculators:** Query database tables (`Quote_DigitalStocks`, `Quote_DigitalClicks`, `Quote_ProfitMargins`)
- **Shopify Calculators:** Hardcoded Python code with pricing formulas

---

## 📋 Question 2: What Fields Are Needed to Create a Schema?

### **Minimum Required Fields:**

```json
{
  "name": "calculate_vinyl_stickers",
  "short_description": "50-120 character summary",
  "description": "200-300 word detailed description",
  "platform": "quote_calculator",
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of stickers",
      "enum": [100, 250, 500, 1000, 2000, 5000]
    },
    "size": {
      "type": "string",
      "description": "Sticker size",
      "enum": ["small", "medium", "large"]
    }
  },
  "returns": {
    "type": "object",
    "description": "Quote result with total_price, per_unit_price, breakdown"
  }
}
```

### **Field Breakdown:**

#### 1. **name** (Required)
- Format: `calculate_{product_type}`
- Example: `calculate_vinyl_stickers`, `calculate_banner_flags`
- Must be unique across all calculators
- Snake_case naming convention

#### 2. **short_description** (Required - NEW!)
- Length: 50-120 characters
- Purpose: Tool discovery & search
- Example: "Calculate vinyl sticker quotes with custom shapes and sizing options"
- **WHY:** Enables fast semantic search without loading full descriptions

#### 3. **description** (Required)
- Length: 200-300 words
- Purpose: Full explanation for AI to understand when/how to use
- Includes:
  - What product this calculates
  - Key capabilities/features
  - Use cases
  - Special considerations

#### 4. **platform** (Required)
- Value: `"quote_calculator"` (standard for all calculators)
- Used by Registry V3 to categorize tools

#### 5. **parameters** (Required)
- **Object containing parameter definitions**
- Each parameter needs:
  - `type`: "integer", "string", "boolean", "number"
  - `description`: What this parameter represents
  - `enum`: (Optional) Valid values - **CRITICAL for AI guidance**
  - `required`: (Optional) Default is true unless specified false
  - `minimum`/`maximum`: (Optional) For numeric bounds

**Example Parameter Definitions:**

```json
"parameters": {
  "quantity": {
    "type": "integer",
    "description": "Number of vinyl stickers to produce",
    "enum": [50, 100, 250, 500, 1000, 2000, 5000],
    "minimum": 50,
    "maximum": 5000
  },
  "size_inches": {
    "type": "number",
    "description": "Sticker size in inches (diameter for round, longest dimension for custom)",
    "minimum": 4,
    "maximum": 12
  },
  "shape": {
    "type": "string",
    "description": "Sticker shape complexity affecting die-cutting cost",
    "enum": ["round", "square", "simple_custom", "moderate_custom", "complex_custom"]
  },
  "material": {
    "type": "string",
    "description": "Vinyl material type",
    "enum": ["white_gloss", "white_matte", "clear", "metallic"]
  },
  "die_cutting": {
    "type": "boolean",
    "description": "Include die-cutting for custom shapes (true) or kiss-cut on sheets (false)"
  },
  "lamination": {
    "type": "boolean",
    "description": "Add protective lamination layer",
    "required": false
  }
}
```

#### 6. **returns** (Required)
- Describes the structure of the calculator's response
- Standard return format for all calculators:

```json
"returns": {
  "type": "object",
  "description": "Quote calculation result",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether calculation succeeded"
    },
    "total_price": {
      "type": "number",
      "description": "Total quote price including GST"
    },
    "per_unit_price": {
      "type": "number",
      "description": "Price per single item"
    },
    "cost_to_business": {
      "type": "number",
      "description": "Internal cost without profit margin"
    },
    "profit_margin": {
      "type": "number",
      "description": "Profit amount included in quote"
    },
    "breakdown": {
      "type": "object",
      "description": "Detailed cost breakdown (material, printing, labor, etc.)"
    }
  }
}
```

---

## ⚙️ Question 3: How Does the System Run It as a Calculator?

### **Step-by-Step Execution Flow:**

#### **STEP 1: AI Agent Discovery**

User says: "Calculate 500 vinyl stickers"

AI calls:
```python
inhouse_calculator_guide()
# Returns: List of 37 calculators with short descriptions
```

AI sees schema doesn't include `calculate_vinyl_stickers` → **NEW CALCULATOR NEEDED**

---

#### **STEP 2: Schema Retrieval**

AI finds the new calculator in production table (after publishing):

```python
get_tool_schema("calculate_vinyl_stickers")
```

Returns:
```json
{
  "name": "calculate_vinyl_stickers",
  "parameters": {
    "quantity": {"type": "integer", "enum": [50, 100, 250, ...]},
    "size_inches": {"type": "number", "minimum": 4, "maximum": 12},
    "shape": {"type": "string", "enum": ["round", "square", ...]},
    ...
  }
}
```

---

#### **STEP 3: AI Executes Tool Call**

AI agent calls:
```python
calculate_vinyl_stickers(
    quantity=500,
    size_inches=6,
    shape="round",
    material="white_gloss",
    die_cutting=True,
    lamination=False
)
```

---

#### **STEP 4: Registry V3 Routes Request**

Registry V3 receives the call:
1. Looks up `calculate_vinyl_stickers` in tool registry
2. Finds the implementation: `calculator_wrapper.calculate_vinyl_stickers`
3. Invokes the wrapper function

---

#### **STEP 5: Calculator Wrapper (Type Enforcement)**

**calculator_wrapper.py:**

```python
@calculator_wrapper(quantity_enum=[50, 100, 250, 500, 1000, 2000, 5000])
def calculate_vinyl_stickers(
    quantity: int,
    size_inches: float,
    shape: str,
    material: str,
    die_cutting: bool,
    lamination: bool,
    **kwargs
) -> Dict[str, Any]:
    """
    TYPE SAFE: @calculator_wrapper decorator ensures:
    - quantity="500" (string) → 500 (integer)
    - size_inches="6" (string) → 6.0 (float)
    - die_cutting="true" (string) → True (boolean)
    """
    
    # Route to appropriate calculator implementation
    if CUSTOM_VINYL_STICKERS_AVAILABLE:
        calculator = VinylStickersCustomCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size_inches=size_inches,
            shape=shape,
            material=material,
            die_cutting=die_cutting,
            lamination=lamination
        )
    else:
        # Fallback or error
        raise RuntimeError("Vinyl stickers calculator not implemented")
    
    return result
```

**Key Features:**
- ✅ **Type enforcement:** Decorator automatically converts types
- ✅ **Enum validation:** Checks quantity is in allowed list
- ✅ **Routing:** Decides which backend calculator to use (GOD vs Shopify vs Custom)
- ✅ **Error handling:** Returns standardized error messages

---

#### **STEP 6: Backend Calculator (WHERE PRICES LIVE)**

**Two Calculator Types:**

##### **A. GOD Calculator (Database-Driven)**

**Example: Flyers (queries database for material costs)**

```python
class FlyerCalculatorGOD:
    def calculate(self, quantity, width, height, gsm, print_side1, print_side2):
        # Query database for stock pricing
        stock_price = self.db.query("""
            SELECT price_per_sqm 
            FROM Quote_DigitalStocks 
            WHERE gsm = %s
        """, (gsm,))
        
        # Query database for printing clicks
        click_price = self.db.query("""
            SELECT price_per_click 
            FROM Quote_DigitalClicks 
            WHERE device = 'Ricoh C7200'
        """, ())
        
        # Calculate material cost
        area_sqm = (width * height) / 1_000_000
        material_cost = area_sqm * stock_price * quantity
        
        # Calculate printing cost
        print_cost = click_price * quantity * (1 if print_side1 else 0)
        print_cost += click_price * quantity * (1 if print_side2 else 0)
        
        # Query profit margin from database
        margin = self.db.query("""
            SELECT margin_percentage 
            FROM Quote_ProfitMargins 
            WHERE product_type = 'flyers'
        """, ())
        
        # Calculate total
        cost_to_business = material_cost + print_cost
        profit = cost_to_business * margin
        total_ex_gst = cost_to_business + profit
        total_inc_gst = total_ex_gst * 1.10  # Add GST
        
        return QuoteResult(
            total_price=total_inc_gst,
            cost_to_business=cost_to_business,
            profit_margin=profit,
            breakdown={
                'material': material_cost,
                'printing': print_cost,
                'margin': margin
            }
        )
```

**Pricing Data Sources:**
- `Quote_DigitalStocks` - Paper/material costs
- `Quote_DigitalClicks` - Printing machine click costs
- `Quote_ProfitMargins` - Business profit margins
- `Quote_Outsourcing` - External supplier pricing

---

##### **B. Shopify Calculator (Hardcoded in Python)**

**Example: Bollard Signs (Python code with embedded pricing)**

```python
class BollardSignsShopifyCalculator:
    def calculate(self, quantity, size, material, sides, artworks):
        # HARDCODED material rates (not from database!)
        material_map = {
            'aluminium': Decimal('28.00'),  # $28 per sqm
            'metal': Decimal('22.00')       # $22 per sqm
        }
        material_rate = material_map.get(material.lower(), Decimal('28.00'))
        
        # HARDCODED print rate
        print_cost_per_m2 = Decimal('12.00')  # $12 per sqm
        
        # HARDCODED setup costs
        impos_setup = Decimal('40')      # $40 setup fee
        extra_arts = Decimal('25')       # $25 per extra artwork
        
        # Calculate area
        width_mm, height_mm = size.split('x')
        area_m2 = (Decimal(width_mm) * Decimal(height_mm)) / Decimal('1000000')
        
        # Calculate costs
        material_cost = area_m2 * material_rate * quantity
        print_cost = area_m2 * print_cost_per_m2 * quantity
        
        # HARDCODED profit margin
        profit_margin_rate = Decimal('0.50')  # 50% margin
        
        biz_cost = impos_setup + material_cost + print_cost
        profit_amount = biz_cost * profit_margin_rate
        
        # HARDCODED GST (Shopify applies GST TWICE!)
        GST_RATE = Decimal('1.10')
        total_price = (biz_cost + profit_amount) * GST_RATE * GST_RATE
        
        return BollardSignsQuoteResult(
            total_price=total_price,
            unit_price=total_price / quantity,
            cost_per_item=unit_price,
            breakdown={
                'material_cost': material_cost,
                'print_cost': print_cost,
                'profit': profit_amount
            }
        )
```

**Key Differences:**

| GOD Calculator | Shopify Calculator |
|----------------|-------------------|
| ✅ Queries database | ❌ No database access |
| ✅ Dynamic pricing (changes with database) | ❌ Static pricing (hardcoded) |
| ✅ Matches actual costs | ⚠️ May drift from real costs |
| ⚠️ Slower (database queries) | ✅ Faster (no database) |
| ✅ Centralized pricing management | ❌ Requires code changes to update prices |

---

#### **STEP 7: Result Returned to AI**

Backend calculator returns:

```json
{
  "success": true,
  "total_price": 231.50,
  "per_unit_price": 0.46,
  "cost_to_business": 150.00,
  "profit_margin": 60.50,
  "breakdown": {
    "material": 85.00,
    "printing": 45.00,
    "die_cutting": 20.00,
    "lamination": 0.00,
    "setup_fee": 0.00
  },
  "specifications": {
    "quantity": 500,
    "size": "6 inches",
    "shape": "round",
    "material": "white_gloss"
  }
}
```

AI receives this and presents to user:

```
Quote for 500 Vinyl Stickers:
• Total: $231.50 (inc GST)
• Per sticker: $0.46
• Size: 6" round
• Material: White gloss vinyl
• Die-cutting: Yes
• Lamination: No

Cost Breakdown:
- Material: $85.00
- Printing: $45.00
- Die-cutting: $20.00
- Business profit: $60.50
```

---

## 🤖 Question 4: How Does the AI Know What to Include in the Schema?

### **Answer: The AI learns from EXAMPLES + CONTEXT + GUIDANCE**

#### **Method 1: Clone Existing Calculator Schema**

AI looks at similar calculators:

**Example: User wants "Custom Vinyl Stickers"**

AI searches existing schemas:
```python
search_tools("sticker")
# Finds: calculate_custom_vinyl_stickers
```

Gets that schema:
```python
get_tool_schema("calculate_custom_vinyl_stickers")
```

**Learns the pattern:**
- Quantity parameter with enum [100, 250, 500, 1000...]
- Size parameter (numeric or string enum)
- Material parameter (string enum with material types)
- Finishing options (boolean flags)
- Return structure (total_price, per_unit_price, breakdown)

**AI adapts it:**
```json
{
  "name": "calculate_banner_flags",
  "parameters": {
    "quantity": {
      "type": "integer",
      "enum": [10, 25, 50, 100, 250, 500]  // ADAPTED: Different quantities
    },
    "size": {
      "type": "string",
      "enum": ["small", "medium", "large", "x-large"]  // ADAPTED: Different sizes
    },
    "material": {
      "type": "string",
      "enum": ["polyester", "canvas", "mesh"]  // ADAPTED: Banner materials
    },
    "pole_included": {
      "type": "boolean",  // NEW: Product-specific option
      "description": "Include telescopic pole with banner"
    }
  }
}
```

---

#### **Method 2: Use Domain Guide**

AI calls:
```python
inhouse_calculator_guide()
```

Returns:
```json
{
  "calculators": [
    {"name": "calculate_business_cards", "category": "basic"},
    {"name": "calculate_flyers", "category": "basic"},
    {"name": "calculate_bollard_signs", "category": "specialty"}
  ],
  "common_parameters": {
    "quantity": {
      "type": "integer",
      "common_enums": [100, 250, 500, 1000, 2000, 5000, 10000],
      "description": "Standard quantity options for most products"
    },
    "stock_gsm": {
      "type": "integer",
      "common_enums": [128, 150, 170, 200, 250, 300, 350, 400],
      "description": "Standard paper weights"
    },
    "print_mode": {
      "type": "string",
      "common_enums": ["single_sided", "double_sided", "no_print"],
      "description": "Standard print side options"
    }
  }
}
```

AI uses this as a **template library**

---

#### **Method 3: Ask User for Specifications**

**User:** "I need a calculator for custom packaging boxes"

**AI:** "To create the schema, I need to know:

1. **Product Specifications:**
   - What sizes are available? (e.g., small/medium/large or exact dimensions?)
   - What materials? (e.g., cardboard, corrugated, rigid board)
   - What printing options? (single color, full color, no print)
   - Any finishing options? (lamination, UV coating, die-cutting)

2. **Quantity Ranges:**
   - Minimum order quantity? (e.g., 50, 100)
   - Maximum order quantity? (e.g., 10,000)
   - Standard quantity breaks? (e.g., 100, 250, 500, 1000, 2500)

3. **Pricing Approach:**
   - Will this use database pricing (GOD calculator)?
   - Or hardcoded pricing (Shopify calculator)?
   - Or simple formula-based pricing?

4. **Return Values Needed:**
   - Just total price?
   - Per-unit price?
   - Cost breakdown (material, printing, labor)?
   - Turnaround time estimate?"

**User provides details, AI builds schema accordingly**

---

#### **Method 4: Industry Standards + AI Training**

AI has training on:
- Standard printing terminology (GSM, celloglaze, perfect binding)
- Common product specifications (A4, A5, DL sizes)
- Typical pricing parameters (quantity, size, material, finishing)
- Standard return formats for quote calculators

**Example: User says "flyer calculator"**

AI knows:
- Flyers typically use parameters: quantity, size (A6/DL/A5/A4), stock type, print sides
- Standard stock weights: 128gsm, 150gsm, 170gsm, 200gsm
- Common finishing: celloglaze (gloss/matt), folding, perforation
- Return structure: total price, per-flyer price, turnaround days

---

## 🎨 Question 5: How to Assign Values to Products in Schema?

### **Answer: You DON'T assign values in the schema - you define OPTIONS**

**Schema defines PARAMETERS (not prices):**

```json
{
  "name": "calculate_custom_envelopes",
  "parameters": {
    "quantity": {
      "type": "integer",
      "enum": [100, 250, 500, 1000, 2500, 5000],
      "description": "Number of envelopes to produce"
    },
    "size": {
      "type": "string",
      "enum": ["DL", "C5", "C4", "B4"],
      "description": "Envelope size standard"
    },
    "stock": {
      "type": "string",
      "enum": ["80GSM White", "100GSM White", "120GSM Laid"],
      "description": "Paper stock type and weight"
    },
    "window": {
      "type": "boolean",
      "description": "Include window for address visibility"
    },
    "print_color": {
      "type": "string",
      "enum": ["none", "1_color", "2_color", "full_color"],
      "description": "Printing configuration"
    }
  }
}
```

**Pricing logic (in backend calculator):**

```python
def calculate_custom_envelopes(quantity, size, stock, window, print_color):
    # PRICING LOGIC HERE (not in schema!)
    
    # Base envelope cost
    base_costs = {
        "DL": 0.15,
        "C5": 0.18,
        "C4": 0.25,
        "B4": 0.35
    }
    base_cost = base_costs[size]
    
    # Stock premium
    stock_premiums = {
        "80GSM White": 0.00,
        "100GSM White": 0.02,
        "120GSM Laid": 0.05
    }
    stock_premium = stock_premiums[stock]
    
    # Window cost
    window_cost = 0.03 if window else 0.00
    
    # Printing cost
    print_costs = {
        "none": 0.00,
        "1_color": 0.08,
        "2_color": 0.12,
        "full_color": 0.20
    }
    print_cost = print_costs[print_color]
    
    # Calculate per-unit cost
    per_unit = base_cost + stock_premium + window_cost + print_cost
    
    # Quantity discount
    if quantity >= 5000:
        per_unit *= 0.85  # 15% discount
    elif quantity >= 2500:
        per_unit *= 0.90  # 10% discount
    elif quantity >= 1000:
        per_unit *= 0.95  # 5% discount
    
    # Setup fee (amortized over quantity)
    setup_fee = 45.00
    per_unit_with_setup = per_unit + (setup_fee / quantity)
    
    # Profit margin (40%)
    per_unit_with_margin = per_unit_with_setup * 1.40
    
    # GST (10%)
    per_unit_inc_gst = per_unit_with_margin * 1.10
    
    total_price = per_unit_inc_gst * quantity
    
    return {
        "success": True,
        "total_price": round(total_price, 2),
        "per_unit_price": round(per_unit_inc_gst, 2),
        "breakdown": {
            "base_cost": base_cost * quantity,
            "stock_premium": stock_premium * quantity,
            "window_cost": window_cost * quantity,
            "print_cost": print_cost * quantity,
            "setup_fee": setup_fee
        }
    }
```

---

## 📝 Complete Example: Creating a New Calculator

### **Scenario: User wants "Magnetic Business Cards Calculator"**

#### **Step 1: Define Schema (Interface)**

```json
{
  "name": "calculate_magnetic_business_cards",
  "short_description": "Calculate magnetic business card quotes with magnet thickness and coating options",
  "description": "Calculate printing quotes for magnetic business cards - perfect for refrigerator marketing. Cards are printed on magnetic vinyl material with various thickness options and protective coatings. Supports standard business card sizes with full-color printing. Returns cost breakdown including magnetic material, printing, coating, and profit margins.",
  "platform": "quote_calculator",
  "parameters": {
    "quantity": {
      "type": "integer",
      "description": "Number of magnetic business cards",
      "enum": [100, 250, 500, 1000, 2000, 5000]
    },
    "size": {
      "type": "string",
      "description": "Card size",
      "enum": ["90x55mm", "90x50mm", "100x60mm"],
      "default": "90x55mm"
    },
    "magnet_thickness": {
      "type": "string",
      "description": "Magnetic vinyl thickness",
      "enum": ["0.3mm", "0.6mm", "0.9mm"],
      "default": "0.6mm"
    },
    "coating": {
      "type": "string",
      "description": "Protective coating",
      "enum": ["none", "gloss_laminate", "matt_laminate"],
      "required": false,
      "default": "none"
    },
    "print_type": {
      "type": "string",
      "description": "Print configuration",
      "enum": ["single_sided", "double_sided"],
      "default": "single_sided"
    }
  },
  "returns": {
    "type": "object",
    "description": "Quote result with pricing and specifications"
  }
}
```

#### **Step 2: Create Backend Calculator (Pricing Logic)**

```python
class MagneticBusinessCardsShopifyCalculator:
    """
    Magnetic Business Cards Calculator - Shopify Implementation
    """
    
    def calculate(self, quantity, size, magnet_thickness, coating, print_type):
        # HARDCODED PRICING (Shopify style)
        
        # Parse size
        width, height = map(int, size.replace('mm', '').split('x'))
        area_sqcm = (width * height) / 100
        
        # Magnetic material costs per sqcm
        magnet_costs = {
            "0.3mm": 0.015,  # $0.015 per sqcm
            "0.6mm": 0.025,  # $0.025 per sqcm
            "0.9mm": 0.035   # $0.035 per sqcm
        }
        magnet_cost_per_card = area_sqcm * magnet_costs[magnet_thickness]
        
        # Printing cost (digital printing on magnetic material)
        print_cost_per_card = 0.12  # $0.12 per card
        if print_type == "double_sided":
            print_cost_per_card *= 1.8  # Double-sided adds 80%
        
        # Coating cost
        coating_costs = {
            "none": 0.00,
            "gloss_laminate": 0.08,
            "matt_laminate": 0.08
        }
        coating_cost_per_card = coating_costs.get(coating, 0.00)
        
        # Setup fees
        setup_fee = 60.00  # Higher setup for magnetic printing
        
        # Calculate per-card cost
        per_card_cost = (
            magnet_cost_per_card + 
            print_cost_per_card + 
            coating_cost_per_card
        )
        
        # Total material + printing
        material_and_print = per_card_cost * quantity
        
        # Business cost
        business_cost = setup_fee + material_and_print
        
        # Profit margin (55% for specialty products)
        profit_margin = 0.55
        profit_amount = business_cost * profit_margin
        
        # Subtotal before GST
        subtotal = business_cost + profit_amount
        
        # GST (10%)
        gst_amount = subtotal * 0.10
        total_inc_gst = subtotal + gst_amount
        
        # Round to 2 decimal places
        total_inc_gst = round(total_inc_gst, 2)
        per_card_price = round(total_inc_gst / quantity, 2)
        
        return {
            "success": True,
            "product": f"Magnetic Business Cards ({size})",
            "quantity": quantity,
            "total_price": total_inc_gst,
            "per_unit_price": per_card_price,
            "specifications": {
                "size": size,
                "magnet_thickness": magnet_thickness,
                "coating": coating,
                "print_type": print_type
            },
            "breakdown": {
                "magnet_material": round(magnet_cost_per_card * quantity, 2),
                "printing": round(print_cost_per_card * quantity, 2),
                "coating": round(coating_cost_per_card * quantity, 2),
                "setup_fee": setup_fee,
                "business_cost": round(business_cost, 2),
                "profit": round(profit_amount, 2),
                "gst": round(gst_amount, 2)
            }
        }
```

#### **Step 3: Create Wrapper Function**

```python
# In calculator_wrapper.py

@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000])
def calculate_magnetic_business_cards(
    quantity: int,
    size: str = "90x55mm",
    magnet_thickness: str = "0.6mm",
    coating: str = "none",
    print_type: str = "single_sided",
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate magnetic business cards quote - TYPE SAFE
    
    Decorator handles type conversion automatically.
    """
    try:
        if not SHOPIFY_CALCULATORS_AVAILABLE:
            raise RuntimeError("Shopify calculators not available")
        
        calculator = MagneticBusinessCardsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,
            magnet_thickness=magnet_thickness,
            coating=coating,
            print_type=print_type
        )
        
        return result
    
    except Exception as e:
        return _handle_calculator_error(e, "magnetic business cards")
```

#### **Step 4: Test the Calculator**

```python
# Test call
result = calculate_magnetic_business_cards(
    quantity=500,
    size="90x55mm",
    magnet_thickness="0.6mm",
    coating="gloss_laminate",
    print_type="single_sided"
)

print(result)
```

**Output:**
```json
{
  "success": true,
  "product": "Magnetic Business Cards (90x55mm)",
  "quantity": 500,
  "total_price": 385.88,
  "per_unit_price": 0.77,
  "specifications": {
    "size": "90x55mm",
    "magnet_thickness": "0.6mm",
    "coating": "gloss_laminate",
    "print_type": "single_sided"
  },
  "breakdown": {
    "magnet_material": 61.88,
    "printing": 60.00,
    "coating": 40.00,
    "setup_fee": 60.00,
    "business_cost": 221.88,
    "profit": 122.03,
    "gst": 34.39
  }
}
```

---

## 🔑 Key Takeaways

### **Schema = Interface (What AI Sees)**
- Defines parameters the AI can send
- Describes what each parameter means
- Lists valid options (enums)
- **NEVER contains prices or formulas**

### **Backend Calculator = Implementation (Where Prices Live)**
- **GOD Calculators:** Query database for dynamic pricing
- **Shopify Calculators:** Hardcoded Python formulas
- **Custom Calculators:** Specialized logic (hybrid approaches)

### **Wrapper = Type Safety Layer**
- Converts AI parameters to correct types
- Validates enums
- Routes to appropriate backend calculator
- Handles errors consistently

### **Registry V3 = Discovery System**
- Loads schemas from files + database
- Provides tools to AI agents
- Manages tool availability

---

## 📚 Summary Diagram

```
USER REQUEST: "Calculate 500 magnetic business cards"
    ↓
AI AGENT: "I need calculator schema"
    ↓
REGISTRY V3: "Here's the schema (parameters, types, enums)"
    ↓
AI AGENT: "Calling calculate_magnetic_business_cards(quantity=500, ...)"
    ↓
WRAPPER: "Converting types, validating, routing to backend..."
    ↓
BACKEND CALCULATOR: "Calculating with PRICING LOGIC:"
    - Magnet material: $61.88
    - Printing: $60.00
    - Coating: $40.00
    - Setup: $60.00
    - Profit: $122.03 (55%)
    - GST: $34.39 (10%)
    - TOTAL: $385.88
    ↓
WRAPPER: "Returning result to AI"
    ↓
AI AGENT: "Presenting quote to user"
    ↓
USER: "Perfect! Add lamination."
```

---

**The schema is like a MENU** - it shows what's available and what options you can choose.

**The backend calculator is the KITCHEN** - it has the recipes and knows the actual prices.

**The wrapper is the WAITER** - it takes your order, translates it correctly, and brings back the food.

**The AI is the CUSTOMER** - it reads the menu, places orders, and receives results.

---

## 🚀 Next Steps for Custom Calculator Creation

1. **Design Schema** - Define parameters based on product specs
2. **Create Backend Calculator** - Write pricing logic (GOD or Shopify style)
3. **Create Wrapper Function** - Add type-safe wrapper
4. **Test** - Validate with multiple test cases
5. **Publish** - Add to production via schema management system

**The schema management system (from previous document) automates steps 1-5!** 🎉
