# 🏗️ Design Engineering Module

**AI-Powered Structural Analysis & CAD Generation for T-Slot Aluminum**

Complete engineering design system for camperyvan conversions, custom furniture, and industrial applications using T-slot aluminum extrusions.

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Backend API](#backend-api)
- [Frontend UI](#frontend-ui)
- [Data Library](#data-library)
- [AI Integration](#ai-integration)
- [Examples](#examples)
- [Installation](#installation)

---

## ✨ Features

### Structural Engineering
- **Beam Deflection Analysis**: Calculate deflection under load using engineering formulas
- **Stress Calculations**: Maximum bending stress and safety factors
- **Multiple Support Types**: Simply supported, cantilever, fixed-both-ends
- **Column Buckling**: Vertical member stability analysis
- **Load Capacity**: Determine maximum safe loads for profiles

### CAD Generation
- **Parametric 3D Models**: Generate STEP-compatible CAD models
- **Technical Drawings**: SVG 2D drawings with dimensions
- **Assembly Visualization**: Multi-component frame assemblies
- **Delimiter-Based Output**: Compatible with visualization engine

### Bill of Materials
- **Real Supplier Catalogs**: 4 Australian/international suppliers
- **Part Numbers & Pricing**: Accurate cost estimates in AUD
- **Cut-to-Length Options**: Custom lengths with cutting fees
- **Shipping Calculations**: Free shipping thresholds
- **Export Formats**: CSV, Markdown, JSON

### Material Database
- **8 T-Slot Profiles**: 20x20mm to 80x80mm
- **4 Aluminum Alloys**: 6061-T6, 6063-T5/T6, 5052-H32
- **Section Properties**: Area, moment of inertia, weight
- **Mechanical Properties**: Yield strength, elastic modulus, density

---

## 🚀 Quick Start

### Example 1: Campervan Bed Frame

```python
from backend.engineering_tools import design_engineering_complete_workflow

# Complete design in one function call
result = design_engineering_complete_workflow(
    description="I want to build a bed frame for my campervan",
    length_mm=1900,
    width_mm=1400,
    load_kg=200
)

print(result['summary'])
# Output: "Design complete! Using 40x40mm Standard T-Slot Profile, 
#          safety factor 3.2, total cost $182.50 AUD including shipping."

# Get CAD model
print(result['cad_model'])
# Output: Delimiter-formatted CAD with ```ENGINEERING_CAD, ```3D_MODEL, ```TECHNICAL_DRAWING

# Get BOM
print(result['bill_of_materials']['markdown'])
# Output: Complete markdown table with parts, quantities, costs
```

### Example 2: Structural Analysis Only

```python
from backend.engineering_tools import design_engineering_calculate_beam

analysis = design_engineering_calculate_beam(
    length_mm=1900,
    load_kg=200,
    profile_type='40x40_standard',
    support_type='simply_supported'
)

print(analysis['explanation'])
# Output: "✓ This design is SAFE. The 40x40mm Standard T-Slot Profile beam 
#          will deflect only 2.34mm under 200kg load, which is within 
#          acceptable limits (L/812). Safety factor is 3.2x."
```

### Example 3: Profile Recommendation

```python
from backend.engineering_tools import design_engineering_recommend_profile

recommendation = design_engineering_recommend_profile(
    length_mm=2000,
    load_kg=300
)

print(recommendation['justification'])
# Output: "This is the most economical profile that meets safety requirements 
#          (SF=2.4, deflection=4.12mm)."
```

---

## 🏛️ Architecture

```
design_engineering/
├── backend/                    # Python backend modules
│   ├── material_database.py    # Material & profile properties
│   ├── structural_analysis.py  # Engineering calculations
│   ├── cad_generator.py        # CAD generation with delimiters
│   ├── parts_sourcing.py       # BOM and supplier catalogs
│   └── engineering_tools.py    # AI tool wrappers (7 functions)
│
├── data/                       # JSON data libraries
│   ├── aluminum_alloys.json    # 4 aluminum alloy specifications
│   ├── tslot_profiles.json     # 8 T-slot profiles (20-80mm)
│   └── suppliers.json          # 4 suppliers with catalogs
│
├── design-engineering.html     # Frontend interface
├── design-engineering.css      # Theme-aware styling
├── design-engineering.js       # Frontend logic (TODO)
│
└── README.md                   # This file
```

### Visualization Engine Integration

```
UI/visualisation_engine/
├── cad_renderer.js                    # Existing CAD renderer
└── cad_renderer_engineering.js        # Engineering extension (NEW)
```

**Extension Features:**
- Auto-detects delimiter blocks: ```ENGINEERING_CAD, ```3D_MODEL, ```TECHNICAL_DRAWING, ```BOM
- Tabbed interface: 3D Model / Technical Drawing / BOM
- Integrates seamlessly with existing renderer
- Theme-aware Three.js 3D rendering

---

## 🔧 Backend API

### 7 AI Tool Functions

#### 1. `design_engineering_calculate_beam()`
Calculate structural properties for a beam.
```python
design_engineering_calculate_beam(
    length_mm=1900,
    load_kg=200,
    profile_type='40x40_standard',
    support_type='simply_supported'
) -> Dict
```

#### 2. `design_engineering_compare_profiles()`
Compare multiple profiles to find best option.
```python
design_engineering_compare_profiles(
    length_mm=1900,
    load_kg=200,
    support_type='simply_supported'
) -> Dict
```

#### 3. `design_engineering_recommend_profile()`
Get automatic profile recommendation.
```python
design_engineering_recommend_profile(
    length_mm=1900,
    load_kg=200,
    application='campervan_bed'
) -> Dict
```

#### 4. `design_engineering_generate_cad_model()`
Generate 3D CAD model with delimiter format.
```python
design_engineering_generate_cad_model(
    component_type='bed_frame',
    specifications={'width_mm': 1400, 'length_mm': 1900, 'profile_id': '40x40_standard'}
) -> str  # Delimiter-formatted output
```

#### 5. `design_engineering_create_bom()`
Generate Bill of Materials with pricing.
```python
design_engineering_create_bom(
    design_type='bed_frame',
    specifications={'width_mm': 1400, 'length_mm': 1900},
    supplier='makerbeam_australia'
) -> Dict
```

#### 6. `design_engineering_get_specifications()`
Get complete catalog reference.
```python
design_engineering_get_specifications() -> Dict
```

#### 7. `design_engineering_complete_workflow()`
Complete design workflow (all steps).
```python
design_engineering_complete_workflow(
    description="I want to build a bed frame",
    length_mm=1900,
    width_mm=1400,
    load_kg=200
) -> Dict
```

---

## 🎨 Frontend UI

### HTML Interface (`design-engineering.html`)

**Left Panel - Input Form:**
- Design Type selector (Beam, Bed Frame, Kitchen Module, Custom)
- Dimensions (Length, Width, Height)
- Load specifications (kg, support type)
- Profile selection (Auto-recommend or Manual)
- Action buttons (Calculate, Generate CAD, Create BOM)

**Right Panel - Results:**
- Structural analysis results
- Deflection, stress, safety factor
- Pass/fail status with badges
- Profile recommendations
- Cost estimates

**Expandable Sections:**
- 3D Visualization panel
- BOM table panel
- Quick Start modal with examples

---

## 📊 Data Library

### Aluminum Alloys (`aluminum_alloys.json`)

| Alloy | Yield (MPa) | Tensile (MPa) | Applications |
|-------|-------------|---------------|--------------|
| **6061-T6** | 276 | 310 | Structural framing, aircraft components |
| **6063-T5** | 145 | 185 | T-slot extrusions (most common) |
| **6063-T6** | 214 | 241 | Heavy-duty T-slot, load-bearing |
| **5052-H32** | 193 | 228 | Marine environments, corrosion resistance |

### T-Slot Profiles (`tslot_profiles.json`)

| Profile | Size (mm) | Weight (kg/m) | Cost (AUD/m) | Applications |
|---------|-----------|---------------|--------------|--------------|
| **20x20 Light** | 20×20 | 0.30 | $8.50 | Small frames, hobbyist |
| **30x30 Standard** | 30×30 | 0.61 | $11.20 | Medium furniture, equipment |
| **40x40 Light** | 40×40 | 1.04 | $12.50 | Campervan beds, displays |
| **40x40 Standard** | 40×40 | 1.66 | $16.80 | **Most common campervan use** |
| **40x40 Heavy** | 40×40 | 2.12 | $21.50 | Heavy-duty, industrial |
| **60x60 Standard** | 60×60 | 2.21 | $28.90 | Large frames, gantries |
| **80x80 Standard** | 80×80 | 3.35 | $42.50 | Very heavy loads, robots |
| **40x80 Rectangular** | 40×80 | 2.21 | $25.40 | Vertical supports, columns |

### Suppliers (`suppliers.json`)

1. **Makerbeam Australia** 🇦🇺
   - Website: https://www.makerbeam.com.au
   - Shipping: Australia-wide, free over $150
   - Delivery: 5 days
   - Cut-to-length: Yes ($2.50/cut)

2. **OpenBuilds Part Store** 🇺🇸
   - Website: https://openbuildspartstore.com
   - Shipping: Worldwide ($65 to AU)
   - Delivery: 10 days
   - Good hobbyist selection

3. **Faztek LLC** 🇺🇸
   - Website: https://www.faztek.com
   - Shipping: Worldwide ($85 to AU)
   - Delivery: 14 days
   - Heavy-duty industrial

4. **MISUMI Australia** 🇦🇺
   - Website: https://au.misumi-ec.com
   - Shipping: Free over $200
   - Delivery: 3 days
   - Custom lengths (100mm increments, no cut fee!)

---

## 🤖 AI Integration

### Natural Language Examples

```
User: "I want to build a bed frame, 1900mm x 1400mm for 200kg"
Agent: Calls design_engineering_complete_workflow()
Result: Complete design with analysis, CAD, BOM

User: "What's the cheapest profile that will work for a 2m bench?"
Agent: Calls design_engineering_compare_profiles()
Result: Comparison table sorted by cost

User: "Show me a 3D model of a kitchen module"
Agent: Calls design_engineering_generate_cad_model()
Result: Delimiter-formatted CAD output (renders in visualization engine)

User: "Create a shopping list for the bed frame"
Agent: Calls design_engineering_create_bom()
Result: BOM with part numbers, prices, supplier links
```

### Tool Integration

Add to `inhouse_modules/complete_calculator_implementation.py`:

```python
from UI.modules_external.design_engineering.backend.engineering_tools import (
    design_engineering_calculate_beam,
    design_engineering_compare_profiles,
    design_engineering_recommend_profile,
    design_engineering_generate_cad_model,
    design_engineering_create_bom,
    design_engineering_get_specifications,
    design_engineering_complete_workflow
)

# AI can now call these functions directly
```

---

## 💡 Examples

### Example 1: Bed Frame Analysis

```python
# Structural analysis
result = design_engineering_calculate_beam(1900, 200, '40x40_standard')

print(f"Deflection: {result['deflection_mm']:.2f}mm")
print(f"Safety Factor: {result['safety_factor']:.1f}")
print(f"Status: {result['recommendation']}")

# Output:
# Deflection: 2.34mm
# Safety Factor: 3.2
# Status: PASS - Design is adequate
```

### Example 2: Complete Campervan Kitchen

```python
# Full workflow
workflow = design_engineering_complete_workflow(
    description="Design a kitchen module for my campervan",
    length_mm=600,
    width_mm=600,
    load_kg=50
)

print(workflow['summary'])
# Output: "Design complete! Using 30x30mm Standard T-Slot Profile, 
#          safety factor 4.8, total cost $98.50 AUD including shipping."

# Display 3D model
print(workflow['cad_model'])
# Visualization engine auto-renders from delimiters

# Get BOM
bom = workflow['bill_of_materials']
print(bom['markdown'])
```

### Example 3: Storage Rack Optimization

```python
# Compare all profiles for best value
comparison = design_engineering_compare_profiles(
    length_mm=1200,
    load_kg=100
)

print(f"Found {comparison['passing_count']} suitable profiles:")
for option in comparison['comparisons']:
    if option['checks']['overall_pass']:
        print(f"  - {option['profile_name']}: ${option['cost_aud_per_meter']:.2f}/m (SF={option['safety_factor']:.1f})")

# Output:
# Found 4 suitable profiles:
#   - 30x30mm Standard: $11.20/m (SF=2.3)
#   - 40x40mm Light: $12.50/m (SF=2.8)
#   - 40x40mm Standard: $16.80/m (SF=4.2)
#   - 40x40mm Heavy: $21.50/m (SF=5.1)
```

---

## 🔌 Installation

### 1. Python Dependencies

```bash
pip install PyNiteFEA sectionproperties forallpeople handcalcs cadquery ezdxf
```

### 2. Enable Visualization Engine Extension

Add to `business-ai-platform-v2.html` before `</body>`:

```html
<!-- Design Engineering CAD Renderer Extension -->
<script src="UI/visualisation_engine/cad_renderer_engineering.js"></script>
```

### 3. Test Installation

```python
# Test backend
from UI.modules_external.design_engineering.backend.engineering_tools import design_engineering_get_specifications

specs = design_engineering_get_specifications()
print(f"Available profiles: {specs['profiles']['count']}")
print(f"Price range: ${specs['profiles']['price_range_aud_per_meter']['min']:.2f} - ${specs['profiles']['price_range_aud_per_meter']['max']:.2f}/m")
```

Expected output:
```
Available profiles: 8
Price range: $8.50 - $42.50/m
```

---

## 📖 Additional Documentation

- **Material Database**: See `data/aluminum_alloys.json` for full alloy specifications
- **Profile Catalog**: See `data/tslot_profiles.json` for section properties
- **Supplier Info**: See `data/suppliers.json` for contact details and catalogs
- **CAD Delimiters**: See `cad_renderer_engineering.js` for delimiter format specification

---

## 🎯 Roadmap

**Current Version: 1.0**

Completed:
- ✅ Structural analysis (beam deflection, stress, safety factors)
- ✅ Material database (8 profiles, 4 alloys)
- ✅ CAD generation with delimiters
- ✅ BOM with 4 suppliers
- ✅ Visualization engine integration
- ✅ 7 AI tool wrappers

**Future Enhancements:**
- 🔮 FEA (Finite Element Analysis) for complex structures
- 🔮 Fatigue analysis for dynamic loads
- 🔮 Cost optimization algorithms
- 🔮 Assembly instructions generator
- 🔮 Integration with procurement APIs
- 🔮 Mobile app interface

---

## 📞 Support

**Issues & Questions:**
- Check existing documentation in this README
- Review example code in `backend/` modules
- Test functions have `__main__` blocks for demonstration

**Contributing:**
- Add new profiles to `data/tslot_profiles.json`
- Add suppliers to `data/suppliers.json`
- Extend AI tools in `backend/engineering_tools.py`

---

**Built with ❤️ for campervan builders and makers**

*Part of the Valor AI Business Platform*
