# Construction Signs Calculator Alignment Complete (Jan 23, 2026)

## ✅ Status: FULLY ALIGNED
**Backend + Wrapper + Schema all use JSON format**

---

## Changes Made

### 1. Backend (ConstructionSigns_Shopify_Calculator.py)

**Lines 66-180: Parameter Parsing**

**Size Parsing (with spaces):**
```python
# BEFORE:
size = kwargs.get('size', '600x450')
w_str, h_str = size.lower().split('x')

# AFTER:
size_raw = kwargs.get('size', '600mm x 900mm')  # JSON default
match = re.search(r'(\d+)\s*mm\s*x\s*(\d+)\s*mm', size_raw, re.IGNORECASE)
width_mm = Decimal(match.group(1))
height_mm = Decimal(match.group(2))
```

**Thickness Parameter (new):**
```python
# Added thickness parameter for material pricing
thickness_raw = kwargs.get('thickness', '5mm')
if '3mm' in thickness_raw:
    material_rate = Decimal('5.50')  # 3mm Corflute rate
elif '5mm' in thickness_raw:
    material_rate = Decimal('6.50')  # 5mm Corflute rate
```

**Sides Parsing (with suffix):**
```python
# BEFORE:
sides = kwargs.get('sides', 'Single').strip().lower()
sides_multiplier = Decimal('2') if sides == 'double' else Decimal('1')

# AFTER:
sides_raw = kwargs.get('sides', 'Single Sided')
if 'Double' in sides_raw:
    sides_multiplier = Decimal('2')
else:
    sides_multiplier = Decimal('1')
```

**New Parameters:**
```python
eyelets_raw = kwargs.get('eyelets', 'No Eyelets')
cutting_raw = kwargs.get('cutting', 'Standard square edge')
# Currently passed through, not affecting pricing
```

**Updated Defaults:**
- `size="600mm x 900mm"` (was `"600x450"`)
- `thickness="5mm"` (new parameter)
- `sides="Single Sided"` (was `"Single"`)
- `eyelets="No Eyelets"` (new parameter)
- `cutting="Standard square edge"` (new parameter)

### 2. Wrapper (calculator_wrapper.py, Lines 2839-2925)

**Parameter Changes:**
```python
# BEFORE:
def calculate_construction_signs(
    quantity: int,
    size: str = None,
    material: str = None,  # Removed
    sides: str = None,
    artworks: int = None
)

# AFTER:
def calculate_construction_signs(
    quantity: int,
    size: str = None,
    thickness: str = None,  # New (replaces material)
    sides: str = None,
    eyelets: str = None,    # New
    cutting: str = None,    # New
    artworks: int = None
)
```

**Validation Updates:**
```python
# Size validation (JSON format with spaces)
valid_sizes = [
    "450mm x 600mm",
    "600mm x 900mm",
    "900mm x 1200mm",
    "1200mm x 2400mm",
    "Custom"
]

# Thickness validation (new)
valid_thickness = ["3mm", "5mm"]

# Sides validation (with suffix)
valid_sides = ["Single Sided", "Double Sided"]

# Eyelets validation (7 options)
valid_eyelets = [
    "No Eyelets",
    "4 x Eyelets (1 In Each Corner)",
    "2 x Eyelets (top left & right corners)",
    "2 x Eyelets (center left & right)",
    "2 x Eyelets (center top & bottom)",
    "6 x Eyelets (3 each top & bottom)",
    "6 x Eyelets (3 each left & right)"
]

# Cutting validation (2 options)
valid_cutting = ["Standard square edge", "Custom Shape"]
```

**Direct Pass-Through:**
```python
# No translation - pass JSON format directly
result = calculator.calculate(
    quantity=quantity,
    size=size,        # "600mm x 900mm"
    thickness=thickness,  # "5mm"
    sides=sides,      # "Single Sided"
    eyelets=eyelets,  # "No Eyelets"
    cutting=cutting,  # "Standard square edge"
    artworks=artworks
)
```

---

## Test Results

### ✅ Test 1: JSON Format - Default Values
**Input:**
- Quantity: 10
- Size: "600mm x 900mm"
- Thickness: "5mm"
- Sides: "Single Sided"
- Eyelets: "No Eyelets"
- Cutting: "Standard square edge"
- Artworks: 1

**Result:**
- ✅ Accepted
- Total Price: $229.96
- Unit Price: $23.00
- Specs correctly show JSON format values

### ✅ Test 2: JSON Format - Larger Size, 3mm, Double Sided
**Input:**
- Quantity: 25
- Size: "1200mm x 2400mm"
- Thickness: "3mm"
- Sides: "Double Sided"
- Eyelets: "4 x Eyelets (1 In Each Corner)"
- Artworks: 1

**Result:**
- ✅ Accepted
- Total Price: $3,189.86
- Unit Price: $127.59
- Specs correctly show JSON format values
- Price affected by thickness (3mm vs 5mm) and double sided

### ✅ Test 3: JSON Format - Custom Eyelets and Cutting
**Input:**
- Quantity: 15
- Size: "900mm x 1200mm"
- Thickness: "5mm"
- Sides: "Single Sided"
- Eyelets: "6 x Eyelets (3 each top & bottom)"
- Cutting: "Custom Shape"
- Artworks: 2

**Result:**
- ✅ Accepted
- Total Price: $580.07
- Unit Price: $38.67
- Eyelets and cutting options correctly passed through

### ❌ Test 4: Invalid Size (Old Format)
**Input:** size="600x450" (no spaces, no "mm")

**Result:**
- ✅ Correctly rejected
- Error: "Invalid size: '600x450'. Must be one of: 450mm x 600mm, 600mm x 900mm, ..."

### ❌ Test 5: Invalid Sides (Missing Suffix)
**Input:** sides="Single" (missing "Sided")

**Result:**
- ✅ Correctly rejected
- Error: "Invalid sides: 'Single'. Must be one of: Single Sided, Double Sided"

### ❌ Test 6: Invalid Thickness
**Input:** thickness="4mm" (not in enum)

**Result:**
- ✅ Correctly rejected
- Error: "Invalid thickness: '4mm'. Must be one of: 3mm, 5mm"

---

## Verification Checklist

**Backend (ConstructionSigns_Shopify_Calculator.py):**
- [x] Accepts JSON format size: "600mm x 900mm" (with spaces)
- [x] Parses size correctly using regex
- [x] Accepts JSON format thickness: "3mm", "5mm"
- [x] Thickness affects material pricing
- [x] Accepts JSON format sides: "Single Sided", "Double Sided"
- [x] Sides affects pricing (single vs double)
- [x] Accepts eyelets parameter (7 options)
- [x] Accepts cutting parameter (2 options)
- [x] Uses JSON default values
- [x] Returns JSON format in specifications

**Wrapper (calculator_wrapper.py):**
- [x] Validates JSON size enum (5 options)
- [x] Validates JSON thickness enum (2 options)
- [x] Validates JSON sides enum (2 options)
- [x] Validates JSON eyelets enum (7 options)
- [x] Validates JSON cutting enum (2 options)
- [x] Validates artworks range (1-20)
- [x] Uses JSON default values
- [x] Passes JSON format directly (no translation)
- [x] Material parameter removed (replaced with thickness)

**Schema (construction_signs_shopify.json):**
- [x] Already correct (JSON format enum values)
- [x] Matches backend and wrapper

**Testing:**
- [x] All valid JSON values accepted
- [x] Pricing accurate for different configurations
- [x] Invalid old format values rejected
- [x] Invalid enum values rejected
- [x] Specifications return JSON format

---

## Key Differences from Bollard Signs

**Bollard Signs:**
- 4 parameters total
- Size includes sides info: "270mm W x 1000mm H - Three Sided"
- Material includes thickness: "3mm Corflute"

**Construction Signs:**
- 7 parameters total (6 + quantity)
- Size is dimensions only: "600mm x 900mm"
- Thickness is separate parameter: "3mm", "5mm"
- Sides is separate parameter: "Single Sided", "Double Sided"
- Eyelets is separate parameter (7 options)
- Cutting is separate parameter (2 options)

---

## Progress Update

**Aligned Calculators:** 2 of 14
- ✅ Bollard Signs (Jan 23, 2026)
- ✅ Construction Signs (Jan 23, 2026)

**Remaining:** 12 calculators
- election_signs (5 mismatches - similar to construction_signs)
- stackable_cubes (2 mismatches)
- custom_vinyl_stickers (needs investigation)
- premium_bookmarks (5 fields missing validation)
- corflute_insert_a_frame (1 mismatch)
- metal_face_a_frame (1 mismatch)
- luxury_pull_up_banners (2 fields missing validation)
- selfie_frames (1 field missing validation)
- custom_poster_printing (2 fields missing validation)
- notepads_a4 (4 mismatches)
- printed_letterheads (2 fields missing validation)
- with_compliments_slips (2 fields missing validation)

**Next:** Election Signs (5 mismatches, similar to construction_signs)
