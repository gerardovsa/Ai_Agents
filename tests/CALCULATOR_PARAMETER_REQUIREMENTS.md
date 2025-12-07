# InHouse Print Calculator - Actual Parameter Requirements

**Database:** FRED (SQL Server at 3.25.76.138\INHPSQLSERVER)  
**Status:** ✅ Connected successfully  
**Tested:** December 8, 2025

---

## 🎯 VERIFIED CALCULATOR SIGNATURES

###  1. Business Cards (`calculate_business_cards`)

```python
def calculate_business_cards(
    quantity: int,                        # REQUIRED
    stock_type: str = "satin_350gsm",     # "satin_300gsm", "satin_350gsm", "kingkong_420gsm", "ecostar_350gsm"
    sides: int = 2,                       # 1 or 2
    print_type: str = "color",            # "color" or "bw"
    finish_size: str = "standard",        # "standard" (90x55) or "small" (90x45)
    celloglaze: str = "none",             # "none", "1_side_gloss", "2_side_gloss", "1_side_matt", "2_side_matt", "1_side_silk", "2_side_silk"
    artworks: int = 1                     # Number of different artworks (1 = included, >1 = $15 each)
)
```

**Example:**
```python
result = calc.calculate_business_cards(
    quantity=500,
    stock_type="satin_350gsm",
    sides=2,
    print_type="color",
    finish_size="standard",
    celloglaze="none",
    artworks=1
)
```

---

### 2. Flyers (`calculate_flyers`)

```python
def calculate_flyers(
    quantity: int,                        # REQUIRED
    width: int,                           # REQUIRED - in mm (e.g., 148 for A5, 210 for A4)
    height: int,                          # REQUIRED - in mm (e.g., 210 for A5, 297 for A4)
    gsm: int,                             # REQUIRED - paper weight (e.g., 100, 150, 170, 200, 250, 300)
    print_side1: int = 1,                 # 0 (no print), 1 (B&W), 2 (Color)
    print_side2: int = 0,                 # 0 (no print), 1 (B&W), 2 (Color)
    folding_required: bool = False,
    folding_passes: int = 1,
    folding_extra_mins: int = 0,
    cello_required: bool = False,
    cello_side1: int = 0,                 # 0 (none), 1 (gloss), 2 (matt)
    cello_side2: int = 0,                 # 0 (none), 1 (gloss), 2 (matt)
    discount: Decimal = Decimal('0')
)
```

**Common Paper Sizes:**
- A5: 148mm x 210mm
- A4: 210mm x 297mm
- A3: 297mm x 420mm
- DL: 99mm x 210mm

**Example:**
```python
result = calc.calculate_flyers(
    quantity=1000,
    width=148,
    height=210,
    gsm=170,
    print_side1=2,  # Color on front
    print_side2=0   # Nothing on back
)
```

---

### 3. Perfect Bound Books (`calculate_perfect_bound_book`)

```python
def calculate_perfect_bound_book(
    quantity: int,                        # REQUIRED
    book_width: int,                      # REQUIRED - in mm (e.g., 148 for A5, 210 for A4)
    book_height: int,                     # REQUIRED - in mm (e.g., 210 for A5, 297 for A4)
    pages: int,                           # REQUIRED - total pages INCLUDING cover (must be multiple of 4)
    stock_type_id: int = 1,               # Internal stock type (1 = default)
    internal_stock_gsm: int = 80,         # Internal paper weight (e.g., 80, 100, 120)
    internal_print_mode: int = 1,         # 1 = Color, 2 = B&W, 3 = Mixed
    cover_stock_type_id: int = 1,         # Cover stock type
    cover_stock_gsm: int = 300,           # Cover paper weight
    cover_print_mode: int = 1,            # 1 = Color, 2 = B&W
    cello_type: int = 0,                  # 0 = None, 1 = Gloss, 2 = Matt, 3 = Silk
    is_scored: bool = False,              # Score the cover
    colour_pages: int = 0,                # Number of color pages (for mixed mode)
    colour_insert_type: int = 0,          # 0 = None, 1 = Insert
    binding_type: str = "Perfect Bound",  # "Perfect Bound", "Wire Bound", "Spiral Bound"
    clear_pvc_front: bool = False,        # Clear PVC cover (wire/spiral only)
    clear_pvc_back: bool = False,         # Clear PVC back (wire/spiral only)
    front_cello_type: int = None,         # Cello for layered covers
    back_cello_type: int = None,          # Cello for layered covers
    artworks: int = 1,                    # Number of different artworks
    discount: Decimal = Decimal('0')
)
```

**Example - Wisdom College Parent Handbook:**
```python
result = calc.calculate_perfect_bound_book(
    quantity=100,
    book_width=148,        # A5 width
    book_height=210,       # A5 height
    pages=200,             # 200 pages total
    internal_stock_gsm=100,
    internal_print_mode=1, # All color
    cover_stock_gsm=300,
    cover_print_mode=1,    # Color cover
    cello_type=1,          # Gloss celloglaze
    artworks=1
)
```

---

### 4. Booklets (`calculate_booklets`)

```python
def calculate_booklets(
    quantity: int,                        # REQUIRED
    width: int,                           # REQUIRED - in mm
    height: int,                          # REQUIRED - in mm
    pages: Decimal,                       # REQUIRED - must be multiple of 4
    stock_type_id: int = 1,               # Stock type from database
    stock_gsm: int = 100,                 # Paper weight
    print_mode: int = 1,                  # 1 = Color, 2 = B&W, 3 = Mixed
    staple_required: bool = True,         # Saddle stitch stapling
    fold_required: bool = True,           # Folding
    is_scored: bool = False,              # Score the cover
    colour_pages: int = 0,                # For mixed mode
    discount: Decimal = Decimal('0')
)
```

**Example:**
```python
result = calc.calculate_booklets(
    quantity=200,
    width=148,
    height=210,
    pages=24,
    stock_gsm=100,
    print_mode=1  # All color
)
```

---

### 5. Letterheads (`calculate_letterheads`)

```python
def calculate_letterheads(
    quantity: int,                        # REQUIRED
    width: int,                           # REQUIRED - in mm (usually 210 for A4)
    height: int,                          # REQUIRED - in mm (usually 297 for A4)
    gsm: int,                             # REQUIRED - paper weight
    print_side1: int = 1,                 # 0 (no print), 1 (B&W), 2 (Color)
    print_side2: int = 0,                 # 0 (no print), 1 (B&W), 2 (Color)
    discount: Decimal = Decimal('0')
)
```

**Example:**
```python
result = calc.calculate_letterheads(
    quantity=500,
    width=210,
    height=297,
    gsm=100,
    print_side1=2,  # Color letterhead
    print_side2=0   # Blank back
)
```

---

### 6. Ridged Boards (`calculate_ridged_boards`)

```python
def calculate_ridged_boards(
    quantity: int,                        # REQUIRED
    width: int,                           # REQUIRED - in mm
    height: int,                          # REQUIRED - in mm
    flute_type: str = "E",                # "E", "B", "C" flute
    print_sides: int = 1,                 # Number of sides to print
    cutting_complexity: str = "simple"    # "simple", "complex"
)
```

---

## ❌ PARAMETER MISMATCHES IDENTIFIED

### Documentation vs Implementation

| Documentation Says | Actual Parameter | Product |
|--------------------|------------------|---------|
| `pages` | `pages` (for books) | ✅ MATCHES |
| `printed_pages` | **`pages`** | ❌ WRONG - use `pages` |
| `book_width`, `book_height` | ✅ CORRECT | Perfect Bound Books |
| `cello_type` (0/1/2) | ✅ CORRECT | Perfect Bound Books |
| `cello_gloss` (bool) | **`cello_type`** (int) | ❌ WRONG - use int |
| `finish` (string) | NOT ACCEPTED | ❌ WRONG - use print_side1/2 |
| `sides` (for flyers) | **`print_side1`, `print_side2`** | ❌ WRONG - separate params |
| `stock_type` (for flyers) | **`gsm`** + database lookup | ❌ WRONG - use GSM number |

---

## 🔧 CRITICAL FIXES NEEDED

### 1. Parameter Name Aliases
The `tool_use_agent.py` needs to map common parameter names to actual names:

```python
PARAMETER_ALIASES = {
    "printed_pages": "pages",
    "cello_gloss": lambda v: {"cello_type": 1 if v else 0},
    "cello_required": lambda v: {"cello_type": 1 if v else 0},
    "sides": "print_side1",  # Needs logic to split into print_side1/2
    "finish": None,  # Not supported - remove
}
```

### 2. Parameter Validation
Before calling calculator, validate:
- `pages` must be multiple of 4 for books/booklets
- `width` and `height` must be positive integers
- `gsm` must be valid paper weight (80, 100, 120, 150, 170, 200, 250, 300, 350)
- `quantity` must be positive integer

### 3. Stock Type Resolution
Flyers don't accept "satin_170gsm" - they need:
- `gsm`: 170 (the number)
- Database looks up stock type from GSM + finish preferences

---

## 📊 TEST RESULTS

**Database Connection:** ✅ SUCCESS  
**Calculator Initialization:** ✅ SUCCESS  
- Loaded 185 stocks
- Loaded 3 click prices  
- Loaded 7 profit margin tiers
- Loaded 7 PBB binding cost scales

**Calculator Tests:** ❌ ALL FAILED (0/6)
- Reason: Parameter name mismatches
- Business Cards was CLOSEST - almost worked (formatting issue only)

---

## 🎯 RECOMMENDED IMPLEMENTATION

### For `tool_use_agent.py` Router:

```python
def _map_calculator_parameters(self, product_type: str, params: dict) -> dict:
    """Map user-friendly parameter names to actual calculator parameters"""
    
    mapped = {}
    
    if product_type == "perfect_bound_books":
        # Map documented names to actual names
        mapped['quantity'] = params.get('quantity')
        mapped['book_width'] = params.get('book_width') or params.get('width')
        mapped['book_height'] = params.get('book_height') or params.get('height')
        mapped['pages'] = params.get('pages') or params.get('printed_pages')
        
        # Handle cello parameter variations
        if 'cello_gloss' in params:
            mapped['cello_type'] = 1 if params['cello_gloss'] else 0
        elif 'cello_required' in params:
            mapped['cello_type'] = 1 if params['cello_required'] else 0
        elif 'cello_type' in params:
            mapped['cello_type'] = params['cello_type']
        
        # Copy remaining parameters
        for key in ['stock_type_id', 'internal_stock_gsm', 'internal_print_mode',
                    'cover_stock_type_id', 'cover_stock_gsm', 'cover_print_mode',
                    'is_scored', 'colour_pages', 'binding_type', 'artworks', 'discount']:
            if key in params:
                mapped[key] = params[key]
    
    elif product_type == "flyers":
        # Flyers need width, height, gsm - NOT stock_type string
        mapped['quantity'] = params.get('quantity')
        mapped['width'] = params.get('width')
        mapped['height'] = params.get('height')
        mapped['gsm'] = params.get('gsm')
        
        # Handle sides parameter
        sides = params.get('sides', 1)
        if sides == 2:
            mapped['print_side1'] = 2  # Color
            mapped['print_side2'] = 2  # Color
        else:
            mapped['print_side1'] = 2  # Color
            mapped['print_side2'] = 0  # None
        
        # Copy optional parameters
        for key in ['folding_required', 'folding_passes', 'cello_required', 'discount']:
            if key in params:
                mapped[key] = params[key]
    
    elif product_type == "business_cards":
        # Business cards parameters match documentation
        for key in ['quantity', 'stock_type', 'sides', 'print_type', 
                    'finish_size', 'celloglaze', 'artworks']:
            if key in params:
                mapped[key] = params[key]
    
    return mapped
```

---

## ✅ NEXT STEPS

1. ✅ Database connection working
2. ✅ Calculator signatures documented
3. ⏳ Add parameter mapping in tool_use_agent.py
4. ⏳ Update calculator requirements documentation
5. ⏳ Re-test all calculators with correct parameters
6. ⏳ Generate Wisdom College quote

---

**Generated:** December 8, 2025  
**Test File:** `tests/test_all_calculators_with_fred_db.py`  
**Database:** FRED (InHousePrint @ 3.25.76.138)
