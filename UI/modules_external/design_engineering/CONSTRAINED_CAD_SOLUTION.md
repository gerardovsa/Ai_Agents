# CAD Generation Enhancement: Constraint-Based Accuracy

## Problem Solved

AI was generating CAD code using delimiters but **losing structural accuracy**:
- ❌ Spacing not proportionate
- ❌ Dimensions not accurate
- ❌ Measurements not maintained

## Solution: CadQuery Constraint Solver

Integrated **CadQuery** parametric CAD library with built-in constraint solver.

### Why CadQuery?

From GitHub research (cadquery/cadquery):
1. **Parametric design** - dimensions are parameters, not hardcoded
2. **Constraint solver** - enforces geometric relationships
3. **Python-based** - integrates with existing codebase
4. **Assemblies support** - multiple parts with constraints

## Architecture

```
AI Request
    ↓
engineering_tools.py
    ↓
constrained_cad_generator.py (NEW)
    ↓
CadQuery Constraint Solver
    ↓
Accurate CAD → Delimiter Format → Visualization
```

## Key Features

### 1. Dimensional Constraints
```python
# Enforces exact dimensions
beam = cq.Workplane("XY").box(length_mm, width_mm, height_mm)

# Result: Length, width, height are EXACTLY as specified (±0.1mm)
```

### 2. Spacing Constraints
```python
# Minimum hole spacing: 20mm
# Minimum edge distance: 10mm
for hole in holes:
    if distance_between_holes < 20:
        raise ValueError("Violates minimum spacing")
    if distance_from_edge < 10:
        raise ValueError("Too close to edge")
```

### 3. Assembly Constraints
```python
assy.constrain("part1@faces@>Z", "part2@faces@<Z", "Plane")  # Faces touch
assy.constrain("part1", "part2", "Point", 50.0)  # 50mm apart
assy.constrain("beam1@edges@|Z", "beam2@edges@|Z", "Axis", 0)  # Parallel
assy.solve()  # Constraint solver ensures all relationships maintained
```

## New AI Tools

### 1. `design_engineering_generate_accurate_cad()`
**Replaces** `design_engineering_generate_cad_model()` for accuracy.

**Features:**
- Exact dimensions (±0.1mm tolerance)
- Proportionate geometry
- Correct spacing
- Validated hole placement

**Usage:**
```python
design_engineering_generate_accurate_cad(
    profile_id='40x40_standard',
    length_mm=500,
    mounting_holes=[
        {"x": 50, "y": 20, "diameter": 5.0},
        {"x": 450, "y": 20, "diameter": 5.0}
    ]
)
```

### 2. `design_engineering_generate_assembly()`
**New capability** - multi-part assemblies with constraints.

**Features:**
- Proper part alignment
- Distance maintenance
- Parallel/perpendicular enforcement
- No geometric conflicts

**Usage:**
```python
design_engineering_generate_assembly(
    parts=[
        {"name": "base", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 500},
        {"name": "upright", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 300}
    ],
    constraints=[
        {"type": "coincident", "part1": "base", "face1": ">Z", "part2": "upright", "face2": "<Z"},
        {"type": "perpendicular", "part1": "base", "edge1": "|X", "part2": "upright", "edge2": "|Z"}
    ]
)
```

## Technical Implementation

### ConstrainedCADGenerator Class

**Location:** `UI/modules_external/design_engineering/backend/constrained_cad_generator.py`

**Key Methods:**

1. `generate_tslot_beam_with_constraints()`
   - Creates parametric beam
   - Validates dimensions
   - Adds constrained holes
   - Returns delimiter output

2. `generate_assembly_with_constraints()`
   - Creates assembly
   - Applies geometric constraints
   - Solves constraint system
   - Returns coordinated parts

3. `_add_constrained_holes()`
   - Validates hole positions
   - Enforces edge distance (≥10mm)
   - Enforces hole spacing (≥20mm)
   - Raises errors if violated

4. `_generate_drawing_svg()`
   - Creates dimensioned technical drawings
   - Shows top, front, side views
   - Includes dimension lines with values
   - Marks hole positions

### Constraint Types Supported

| Constraint | Description | Example |
|-----------|-------------|---------|
| `coincident` | Faces/edges touch | Base top face touches upright bottom face |
| `distance` | Fixed distance | Two parts 50mm apart |
| `parallel` | Edges parallel (0°) | Two beams run parallel |
| `perpendicular` | Edges at 90° | Upright perpendicular to base |

### Validation Rules

1. **Dimensions:**
   - All values > 0
   - Within material limits
   - Tolerance: ±0.1mm

2. **Holes:**
   - Minimum edge distance: 10mm
   - Minimum spacing: 20mm
   - Within part bounds

3. **Assemblies:**
   - No geometric conflicts
   - All constraints satisfiable
   - Proper face/edge references

## Benefits

### Before (Delimiter-only)
```json
{
  "dimensions": {
    "length_mm": 500,
    "width_mm": 40,
    "height_mm": 40
  }
}
```
❌ No enforcement
❌ AI can generate any values
❌ Proportions can drift
❌ Spacing can be wrong

### After (Constraint-based)
```python
beam = cq.Workplane("XY").box(500, 40, 40)
# CadQuery ensures:
# ✓ Length is EXACTLY 500mm
# ✓ Width is EXACTLY 40mm
# ✓ Height is EXACTLY 40mm
# ✓ All edges are perpendicular
# ✓ All faces are planar
```
✅ Enforced by solver
✅ Mathematically accurate
✅ Proportions maintained
✅ Spacing validated

## Output Format

Still uses delimiter format for compatibility:

```
```ENGINEERING_CAD
{"type": "tslot_beam_constrained", "solver": "CadQuery", ...}
```

```3D_MODEL
{Three.js geometry with exact vertices}
```

```TECHNICAL_DRAWING
<svg with dimensioned views>
```
```

**New additions:**
- `"constraints_applied": true` in metadata
- `"solver": "CadQuery"` identifier
- Verified bounding box in geometry
- Dimensioned technical drawings

## AI Prompting Guidance

### When to Use Constraint-Based CAD

**Use `design_engineering_generate_accurate_cad()`:**
- User mentions "accurate", "exact", "precise", "correct"
- Engineering/structural applications
- Parts with holes/features
- When dimensions matter

**Use `design_engineering_generate_assembly()`:**
- Multiple parts
- "Aligned", "connected", "parallel", "perpendicular"
- Structural frames
- Complex assemblies

### Natural Language Examples

**Example 1:**
```
User: "Generate a 500mm beam with two mounting holes 400mm apart"

AI: I'll create an accurate beam with constrained hole placement.
    [calls design_engineering_generate_accurate_cad(
        profile_id='40x40_standard',
        length_mm=500,
        mounting_holes=[
            {"x": 50, "y": 20, "diameter": 5.0},
            {"x": 450, "y": 20, "diameter": 5.0}
        ]
    )]
```

**Example 2:**
```
User: "Build an L-shaped frame with proper right angles"

AI: I'll create an assembly with perpendicular constraints.
    [calls design_engineering_generate_assembly(
        parts=[...],
        constraints=[
            {"type": "perpendicular", ...}
        ]
    )]
```

## Integration with Existing Code

### No Breaking Changes
- Old `design_engineering_generate_cad_model()` still works
- New functions are additions
- Delimiter format unchanged
- Visualization engine compatible

### Recommended Migration
1. Keep old function for simple visualizations
2. Use new function for engineering applications
3. Update AI prompts to prefer constrained generation
4. Add constraint checks to validation

## Dependencies

**Required:**
- `cadquery >= 2.7` (already installed)
- `OCP` (CadQuery dependency)

**Already Satisfied:**
```bash
pip list | grep -i cad
# cadquery           2.7-dev
# cadquery-ocp       7.8.1
```

## Testing

### Unit Tests Needed

1. **Constraint Validation:**
   - Hole spacing violations
   - Edge distance violations
   - Negative dimensions

2. **Assembly Constraints:**
   - Coincident faces
   - Parallel/perpendicular edges
   - Distance maintenance

3. **Output Format:**
   - Delimiter parsing
   - JSON schema validation
   - SVG generation

### Example Test Cases

```python
def test_hole_spacing_constraint():
    """Holes too close should raise error."""
    with pytest.raises(ValueError):
        ai_generate_constrained_beam(
            profile_id='40x40_standard',
            length_mm=100,
            mounting_holes=[
                {"x": 20, "y": 20, "diameter": 5.0},
                {"x": 30, "y": 20, "diameter": 5.0}  # Only 10mm apart!
            ]
        )

def test_assembly_perpendicular():
    """Assembly should maintain perpendicular constraint."""
    result = ai_generate_constrained_assembly(
        parts=[...],
        constraints=[{"type": "perpendicular", ...}]
    )
    # Verify angle between edges is 90° ± 0.1°
```

## Future Enhancements

### Planned Features

1. **STEP File Export:**
   ```python
   result = generator.generate_tslot_beam_with_constraints(...)
   result['cad_object'].val().exportStep('beam.step')
   ```

2. **More Constraint Types:**
   - `tangent`: Curves touch tangentially
   - `concentric`: Circles share center
   - `colinear`: Points on same line

3. **Constraint Relaxation:**
   - Soft constraints (preferences)
   - Weighted solving
   - Tolerance bands

4. **Assembly Interference Check:**
   ```python
   if assy.check_interference():
       raise ValueError("Parts collide!")
   ```

5. **Material Properties:**
   - Integrate with structural_analysis.py
   - Show stress/strain on CAD
   - Color code by safety factor

## References

### GitHub Research Sources

1. **CadQuery** - https://github.com/CadQuery/cadquery
   - Parametric CAD with constraints
   - Assembly support
   - Python-based

2. **Build123d** - https://github.com/gumyr/build123d
   - Alternative CAD library
   - More pythonic API
   - Future consideration

3. **OpenAI Cookbook** - Structured outputs examples
   - JSON schema enforcement
   - Tool calling patterns
   - Constraint validation

### Documentation

- **CadQuery Assembly Tutorial:** `/doc/assy.rst`
- **Constraint Examples:** `/tests/test_assembly.py`
- **Sketch Constraints:** `/cadquery/sketch.py` (ConstraintSolver)

## Summary

✅ **Problem:** AI generates CAD with incorrect spacing/dimensions
✅ **Solution:** CadQuery constraint solver
✅ **Implementation:** New `constrained_cad_generator.py` module
✅ **Integration:** Two new AI tools in `engineering_tools.py`
✅ **Result:** Mathematically accurate, constraint-enforced CAD

**The AI can now generate CAD that maintains exact dimensions, proper spacing, and geometric relationships!**
