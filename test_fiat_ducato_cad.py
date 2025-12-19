"""
Test Fiat Ducato CAD Generation
Verifies that the fixed generate_cad_from_code tool works correctly
"""

from tools.registry_v3 import RegistryV3

# Initialize registry
registry = RegistryV3()

print("=" * 70)
print("TESTING CAD MODULE REGISTRATION")
print("=" * 70)

# Check if cadquery tools are registered
cad_tools = [name for name in registry.tools.keys() if 'cad' in name.lower()]
print(f"\nCAD-related tools found: {len(cad_tools)}")
for tool in sorted(cad_tools):
    print(f"  ✓ {tool}")

print("\n" + "=" * 70)
print("TESTING FIAT DUCATO CAD GENERATION")
print("=" * 70)

# Simplified Fiat Ducato model code
ducato_code = """
import cadquery as cq

# 2011 Fiat Ducato Australian Mid Roof LWB - Simplified dimensions in mm
LENGTH = 5998
WIDTH = 2050
HEIGHT = 2524
WHEELBASE = 4035
CLEARANCE = 200
CARGO_LEN = 4070
CARGO_W = 1870
CARGO_H = 1932

# Create main cargo box
result = cq.Workplane("XY").box(CARGO_W, CARGO_LEN, CARGO_H).translate((0, -1000, CLEARANCE + CARGO_H/2))

# Add cab section
result = result.union(cq.Workplane("XY").box(WIDTH, 1800, 1800).translate((0, 2200, CLEARANCE + 900)))

# Add roof
result = result.union(cq.Workplane("XY").box(WIDTH, 4600, 100).translate((0, -300, HEIGHT - 50)))

# Add wheels (4 wheels)
wheel_radius = 360
wheel_width = 220
track = 1600

# Front left wheel
result = result.union(
    cq.Workplane("YZ").workplane(offset=-track/2).center(WHEELBASE/2, wheel_radius).circle(wheel_radius).extrude(wheel_width)
)

# Front right wheel  
result = result.union(
    cq.Workplane("YZ").workplane(offset=track/2 - wheel_width).center(WHEELBASE/2, wheel_radius).circle(wheel_radius).extrude(wheel_width)
)

# Rear left wheel
result = result.union(
    cq.Workplane("YZ").workplane(offset=-track/2).center(-WHEELBASE/2, wheel_radius).circle(wheel_radius).extrude(wheel_width)
)

# Rear right wheel
result = result.union(
    cq.Workplane("YZ").workplane(offset=track/2 - wheel_width).center(-WHEELBASE/2, wheel_radius).circle(wheel_radius).extrude(wheel_width)
)

# Add front bumper
result = result.union(cq.Workplane("XY").box(WIDTH * 0.95, 150, 200).translate((0, LENGTH/2 - 75, 150)))

# Add rear bumper
result = result.union(cq.Workplane("XY").box(WIDTH * 0.95, 150, 200).translate((0, -LENGTH/2 + 75, 150)))
"""

print("\nValidating code...")
validation_result = registry.execute_tool(
    tool_name="validate_cadquery_code",
    code=ducato_code
)

if validation_result.get('success'):
    print("✓ Code validation passed")
    
    print("\nGenerating CAD model...")
    generation_result = registry.execute_tool(
        tool_name="generate_cad_from_code",
        code=ducato_code,
        description="2011 Fiat Ducato Australian Mid Roof LWB"
    )
    
    if generation_result.get('success'):
        data = generation_result.get('data', {})
        print("✓ CAD generation successful!")
        print(f"\n  STEP file: {data.get('step_file')}")
        print(f"  STL file: {data.get('stl_file')}")
        print(f"  Vertices: {data.get('vertices')}")
        print(f"  Faces: {data.get('faces')}")
        print(f"  Volume: {data.get('volume', 'N/A')}")
        
        bbox = data.get('bounding_box', {})
        if bbox:
            size = bbox.get('size', {})
            print(f"\n  Bounding Box:")
            print(f"    Length: {size.get('y', 0):.1f}mm")
            print(f"    Width: {size.get('x', 0):.1f}mm")
            print(f"    Height: {size.get('z', 0):.1f}mm")
        
        print("\n" + "=" * 70)
        print("SUCCESS! Fiat Ducato CAD model generated")
        print("=" * 70)
    else:
        print(f"✗ CAD generation failed: {generation_result.get('error')}")
else:
    print(f"✗ Code validation failed: {validation_result.get('error')}")

print("\n" + "=" * 70)
print("TESTING DESIGN ENGINEERING TOOLS")
print("=" * 70)

# Check engineering tools
eng_tools = [name for name in registry.tools.keys() if 'beam' in name.lower() or 'profile' in name.lower()]
print(f"\nEngineering tools found: {len(eng_tools)}")
for tool in sorted(eng_tools):
    print(f"  ✓ {tool}")

# Test beam calculation
print("\nTesting beam calculation for campervan bed frame...")
beam_result = registry.execute_tool(
    tool_name="calculate_beam_deflection",
    length_mm=1900,
    load_kg=200,
    profile_type="40x40_standard",
    support_type="simply_supported"
)

if beam_result.get('success'):
    data = beam_result.get('data', {})
    print("✓ Beam calculation successful!")
    print(f"\n  {data.get('explanation', 'No explanation')}")
else:
    print(f"✗ Beam calculation failed: {beam_result.get('error')}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
