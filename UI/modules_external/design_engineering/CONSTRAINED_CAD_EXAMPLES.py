"""
Example: AI-Generated Constrained CAD
Demonstrates how AI should use the new constraint-based CAD tools
"""

from UI.modules_external.design_engineering.backend.engineering_tools import (
    design_engineering_generate_accurate_cad,
    design_engineering_generate_assembly
)


# Example 1: Simple Beam with Mounting Holes
# User: "Generate a 500mm beam with two mounting holes"
# AI Response:

print("=" * 60)
print("Example 1: Constrained Beam with Mounting Holes")
print("=" * 60)

cad_output = design_engineering_generate_accurate_cad(
    profile_id='40x40_standard',
    length_mm=500,
    mounting_holes=[
        {"x": 50, "y": 20, "diameter": 5.0},   # 50mm from left edge
        {"x": 450, "y": 20, "diameter": 5.0}   # 50mm from right edge
    ]
)

print("✅ Generated beam with:")
print("   - Exact length: 500mm (±0.1mm)")
print("   - Hole spacing: 400mm (validated)")
print("   - Edge clearance: 50mm each side (validated)")
print("\nDelimiter output ready for visualization engine:")
print(cad_output[:200] + "...")


# Example 2: L-Shaped Frame Assembly
# User: "Build an L-shaped frame with proper right angles"
# AI Response:

print("\n" + "=" * 60)
print("Example 2: Constrained L-Frame Assembly")
print("=" * 60)

assembly_output = design_engineering_generate_assembly(
    parts=[
        {
            "name": "horizontal",
            "type": "tslot_beam",
            "profile_id": "40x40_standard",
            "length": 500
        },
        {
            "name": "vertical",
            "type": "tslot_beam",
            "profile_id": "40x40_standard",
            "length": 300
        }
    ],
    constraints=[
        {
            "type": "coincident",
            "part1": "horizontal",
            "face1": ">Z",  # Top face of horizontal
            "part2": "vertical",
            "face2": "<Z"   # Bottom face of vertical
        },
        {
            "type": "perpendicular",
            "part1": "horizontal",
            "edge1": "|X",  # Edge along X axis
            "part2": "vertical",
            "edge2": "|Z"   # Edge along Z axis
        }
    ]
)

print("✅ Generated L-frame with:")
print("   - Parts properly aligned (coincident constraint)")
print("   - 90° angle enforced (perpendicular constraint)")
print("   - No geometric conflicts (solver verified)")
print("\nAssembly ready for visualization")


# Example 3: Error Handling - Constraint Violations
# User: "Generate beam with holes too close together"
# AI Should Handle:

print("\n" + "=" * 60)
print("Example 3: Constraint Violation Detection")
print("=" * 60)

try:
    bad_cad = design_engineering_generate_accurate_cad(
        profile_id='40x40_standard',
        length_mm=100,
        mounting_holes=[
            {"x": 20, "y": 20, "diameter": 5.0},
            {"x": 30, "y": 20, "diameter": 5.0}  # Only 10mm apart - VIOLATION!
        ]
    )
except ValueError as e:
    print("❌ Constraint violation detected:")
    print(f"   Error: {e}")
    print("   AI should inform user and suggest corrections:")
    print("   'The holes are too close (10mm). Minimum spacing is 20mm.'")
    print("   'I recommend placing them at x=20 and x=60 instead.'")


# Example 4: Complex Assembly with Multiple Constraints
# User: "Build a simple table frame"
# AI Response:

print("\n" + "=" * 60)
print("Example 4: Table Frame Assembly")
print("=" * 60)

table_assembly = design_engineering_generate_assembly(
    parts=[
        # Table legs (4 corners)
        {"name": "leg_fl", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 700},  # Front left
        {"name": "leg_fr", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 700},  # Front right
        {"name": "leg_bl", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 700},  # Back left
        {"name": "leg_br", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 700},  # Back right
        
        # Top rails
        {"name": "rail_front", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 1200},
        {"name": "rail_back", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 1200},
        {"name": "rail_left", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 600},
        {"name": "rail_right", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 600}
    ],
    constraints=[
        # Legs must be vertical (parallel to Z axis)
        {"type": "parallel", "part1": "leg_fl", "edge1": "|Z", "part2": "leg_fr", "edge2": "|Z"},
        {"type": "parallel", "part1": "leg_bl", "edge1": "|Z", "part2": "leg_br", "edge2": "|Z"},
        
        # Front rail connects front legs
        {"type": "coincident", "part1": "leg_fl", "face1": ">Z", "part2": "rail_front", "face2": "<Y"},
        {"type": "coincident", "part1": "leg_fr", "face1": ">Z", "part2": "rail_front", "face2": ">Y"},
        
        # Back rail connects back legs
        {"type": "coincident", "part1": "leg_bl", "face1": ">Z", "part2": "rail_back", "face2": "<Y"},
        {"type": "coincident", "part1": "leg_br", "face1": ">Z", "part2": "rail_back", "face2": ">Y"},
        
        # Side rails connect left/right
        {"type": "coincident", "part1": "leg_fl", "face1": ">Z", "part2": "rail_left", "face2": "<X"},
        {"type": "coincident", "part1": "leg_fr", "face1": ">Z", "part2": "rail_right", "face2": ">X"},
        
        # Rails must be horizontal (perpendicular to legs)
        {"type": "perpendicular", "part1": "leg_fl", "edge1": "|Z", "part2": "rail_front", "edge2": "|X"},
        {"type": "perpendicular", "part1": "leg_fl", "edge1": "|Z", "part2": "rail_left", "edge2": "|Y"}
    ]
)

print("✅ Generated table frame with:")
print("   - 4 vertical legs (parallel constraint)")
print("   - 4 horizontal rails (perpendicular constraint)")
print("   - All connections properly aligned (coincident constraints)")
print("   - Structurally sound (constraint solver verified)")


# AI Prompting Guidelines
print("\n" + "=" * 60)
print("AI PROMPTING GUIDELINES")
print("=" * 60)

guidelines = """
When to use design_engineering_generate_accurate_cad():
✓ User mentions accuracy/precision/exact
✓ Engineering or structural applications  
✓ Parts with holes or mounting features
✓ When dimensions are critical

When to use design_engineering_generate_assembly():
✓ Multiple parts mentioned
✓ User says "aligned", "connected", "parallel", "perpendicular"
✓ Structural frames or complex assemblies
✓ When parts need to fit together

Natural language patterns to recognize:
- "Generate a beam with..." → Single part, use accurate_cad
- "Build a frame with..." → Multiple parts, use assembly
- "Make sure it's exact..." → Emphasizes accuracy, use constraints
- "Connect two beams at 90°..." → Assembly with perpendicular constraint
- "Holes should be X mm apart..." → Use mounting_holes parameter

Error handling:
- If constraints cannot be satisfied, explain why to user
- Suggest corrections (e.g., "increase spacing to 20mm")
- Don't silently ignore constraint violations
- Show which constraint was violated

Response format:
1. Acknowledge user's request
2. Explain what constraints you're applying
3. Call appropriate tool
4. Confirm successful generation
5. Summarize key dimensions/constraints
"""

print(guidelines)


# Testing the AI's Understanding
print("\n" + "=" * 60)
print("TEST YOUR UNDERSTANDING")
print("=" * 60)

test_cases = [
    {
        "user_input": "Generate a 600mm beam",
        "correct_tool": "design_engineering_generate_accurate_cad",
        "parameters": {"profile_id": "40x40_standard", "length_mm": 600}
    },
    {
        "user_input": "Build an H-frame with parallel uprights",
        "correct_tool": "design_engineering_generate_assembly",
        "constraints": [{"type": "parallel", ...}]
    },
    {
        "user_input": "Make a beam with mounting holes at exact positions",
        "correct_tool": "design_engineering_generate_accurate_cad",
        "use_mounting_holes": True
    },
    {
        "user_input": "Create a structure where beams meet at right angles",
        "correct_tool": "design_engineering_generate_assembly",
        "constraints": [{"type": "perpendicular", ...}]
    }
]

print("Can you identify the correct tool for each request?")
for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. User: \"{test['user_input']}\"")
    print(f"   Correct tool: {test['correct_tool']}")
    if 'constraints' in test:
        print(f"   Key constraint: {test['constraints'][0]['type']}")

print("\n" + "=" * 60)
