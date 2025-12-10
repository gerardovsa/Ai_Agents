"""
CAD Generator Module
Parametric CAD generation using delimiter-based output for visualization engine
Generates 3D models and 2D technical drawings
"""

import json
from typing import Dict, List, Tuple
from .material_database import get_profile_properties


def generate_tslot_beam_cad(
    profile_id: str,
    length_mm: float,
    color: str = "#C0C0C0"
) -> str:
    """
    Generate CAD visualization for a T-slot beam using delimiters.
    Returns formatted string with 3D geometry and technical drawing.
    
    Args:
        profile_id: T-slot profile identifier
        length_mm: Beam length in mm
        color: Hex color for 3D model
    
    Returns:
        Delimiter-formatted string for visualization engine
    """
    profile = get_profile_properties(profile_id)
    if not profile:
        raise ValueError(f"Profile '{profile_id}' not found")
    
    dim = profile['dimensions']
    width = dim['width_mm']
    height = dim['height_mm']
    
    # Build CAD output with delimiters
    output = []
    
    # Header
    output.append("```ENGINEERING_CAD")
    output.append(json.dumps({
        "type": "tslot_beam",
        "profile": profile['name'],
        "dimensions": {
            "width_mm": width,
            "height_mm": height,
            "length_mm": length_mm
        }
    }))
    output.append("```")
    
    # 3D Model (JSON format for Three.js)
    output.append("")
    output.append("```3D_MODEL")
    model_data = {
        "type": "box",
        "dimensions": {
            "width": width,
            "height": height,
            "depth": length_mm
        },
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0},
        "material": {
            "type": "standard",
            "color": color,
            "metalness": 0.7,
            "roughness": 0.3
        },
        "label": f"{profile['name']} - {length_mm}mm"
    }
    output.append(json.dumps(model_data, indent=2))
    output.append("```")
    
    # 2D Technical Drawing (SVG)
    output.append("")
    output.append("```TECHNICAL_DRAWING")
    svg = generate_beam_technical_drawing(width, height, length_mm, profile['name'])
    output.append(svg)
    output.append("```")
    
    return "\n".join(output)


def generate_beam_technical_drawing(
    width_mm: float,
    height_mm: float,
    length_mm: float,
    label: str
) -> str:
    """Generate SVG technical drawing for beam"""
    
    # Scale factors for drawing
    scale_length = 600 / length_mm if length_mm > 600 else 1
    scale_section = 2.0
    
    # Scaled dimensions
    draw_length = length_mm * scale_length
    draw_width = width_mm * scale_section
    draw_height = height_mm * scale_section
    
    svg = f'''<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
    <!-- Side View -->
    <g id="side-view">
        <text x="50" y="30" fill="currentColor" font-size="16" font-weight="bold">Side View</text>
        <rect x="50" y="50" width="{draw_length}" height="{draw_height}" 
              fill="none" stroke="currentColor" stroke-width="2"/>
        
        <!-- Dimension line - Length -->
        <line x1="50" y1="{70 + draw_height}" x2="{50 + draw_length}" y2="{70 + draw_height}" 
              stroke="currentColor" stroke-width="1" marker-end="url(#arrowhead)"/>
        <line x1="50" y1="{65 + draw_height}" x2="50" y2="{75 + draw_height}" stroke="currentColor" stroke-width="1"/>
        <line x1="{50 + draw_length}" y1="{65 + draw_height}" x2="{50 + draw_length}" y2="{75 + draw_height}" stroke="currentColor" stroke-width="1"/>
        <text x="{50 + draw_length/2}" y="{95 + draw_height}" fill="currentColor" font-size="12" text-anchor="middle">{length_mm:.0f} mm</text>
        
        <!-- Dimension line - Height -->
        <line x1="{65 + draw_length}" y1="50" x2="{65 + draw_length}" y2="{50 + draw_height}" 
              stroke="currentColor" stroke-width="1" marker-end="url(#arrowhead)"/>
        <line x1="{60 + draw_length}" y1="50" x2="{70 + draw_length}" y2="50" stroke="currentColor" stroke-width="1"/>
        <line x1="{60 + draw_length}" y1="{50 + draw_height}" x2="{70 + draw_length}" y2="{50 + draw_height}" stroke="currentColor" stroke-width="1"/>
        <text x="{85 + draw_length}" y="{50 + draw_height/2}" fill="currentColor" font-size="12">{height_mm:.0f} mm</text>
    </g>
    
    <!-- End View -->
    <g id="end-view">
        <text x="50" y="200" fill="currentColor" font-size="16" font-weight="bold">End View (Section)</text>
        <rect x="50" y="220" width="{draw_width}" height="{draw_height}" 
              fill="none" stroke="currentColor" stroke-width="2"/>
        
        <!-- T-slot representation (simplified) -->
        <rect x="{50 + draw_width/2 - 8}" y="220" width="16" height="10" 
              fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="2,2"/>
        <text x="{50 + draw_width/2}" y="{240 + draw_height}" fill="currentColor" font-size="11" text-anchor="middle">{width_mm:.0f} × {height_mm:.0f} mm</text>
    </g>
    
    <!-- Label -->
    <text x="50" y="380" fill="currentColor" font-size="14" font-weight="bold">{label}</text>
    
    <!-- Arrow marker definition -->
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
            <polygon points="0 0, 10 5, 0 10" fill="currentColor"/>
        </marker>
    </defs>
</svg>'''
    
    return svg


def generate_frame_assembly_cad(
    frame_spec: Dict
) -> str:
    """
    Generate CAD for complete frame assembly.
    
    Args:
        frame_spec: Dictionary with:
            - members: List of beam specifications
            - connections: List of joint specifications
    
    Returns:
        Delimiter-formatted CAD output
    """
    output = []
    
    output.append("```ENGINEERING_CAD")
    output.append(json.dumps({
        "type": "frame_assembly",
        "member_count": len(frame_spec.get('members', [])),
        "connection_count": len(frame_spec.get('connections', []))
    }))
    output.append("```")
    
    output.append("")
    output.append("```3D_MODEL")
    
    # Generate assembly model
    assembly = {
        "type": "assembly",
        "components": []
    }
    
    for i, member in enumerate(frame_spec.get('members', [])):
        profile = get_profile_properties(member['profile_id'])
        if not profile:
            continue
        
        component = {
            "id": f"member_{i}",
            "type": "box",
            "dimensions": {
                "width": profile['dimensions']['width_mm'],
                "height": profile['dimensions']['height_mm'],
                "depth": member['length_mm']
            },
            "position": member.get('position', {"x": 0, "y": 0, "z": 0}),
            "rotation": member.get('rotation', {"x": 0, "y": 0, "z": 0}),
            "material": {
                "type": "standard",
                "color": member.get('color', "#C0C0C0"),
                "metalness": 0.7,
                "roughness": 0.3
            },
            "label": f"{profile['name']} - {member['length_mm']}mm"
        }
        assembly["components"].append(component)
    
    output.append(json.dumps(assembly, indent=2))
    output.append("```")
    
    return "\n".join(output)


def generate_bed_frame_cad(
    width_mm: float = 1400,
    length_mm: float = 1900,
    profile_id: str = '40x40_standard'
) -> str:
    """
    Generate CAD for complete campervan bed frame.
    
    Args:
        width_mm: Bed width
        length_mm: Bed length
        profile_id: T-slot profile to use
    
    Returns:
        Delimiter-formatted CAD output
    """
    profile = get_profile_properties(profile_id)
    if not profile:
        raise ValueError(f"Profile '{profile_id}' not found")
    
    dim = profile['dimensions']
    profile_size = dim['width_mm']
    
    # Define frame members
    members = [
        # Long sides (2x)
        {"profile_id": profile_id, "length_mm": length_mm, "position": {"x": 0, "y": 0, "z": 0}, 
         "rotation": {"x": 0, "y": 0, "z": 0}, "label": "Side Rail 1"},
        {"profile_id": profile_id, "length_mm": length_mm, "position": {"x": width_mm - profile_size, "y": 0, "z": 0}, 
         "rotation": {"x": 0, "y": 0, "z": 0}, "label": "Side Rail 2"},
        
        # Short ends (2x)
        {"profile_id": profile_id, "length_mm": width_mm, "position": {"x": 0, "y": 0, "z": 0}, 
         "rotation": {"x": 0, "y": 0, "z": 90}, "label": "End Rail 1"},
        {"profile_id": profile_id, "length_mm": width_mm, "position": {"x": 0, "y": 0, "z": length_mm - profile_size}, 
         "rotation": {"x": 0, "y": 0, "z": 90}, "label": "End Rail 2"},
        
        # Center support
        {"profile_id": profile_id, "length_mm": length_mm, "position": {"x": width_mm / 2, "y": 0, "z": 0}, 
         "rotation": {"x": 0, "y": 0, "z": 0}, "label": "Center Support"},
    ]
    
    frame_spec = {
        "members": members,
        "connections": []
    }
    
    output = []
    output.append(f"# Campervan Bed Frame - {width_mm}mm × {length_mm}mm")
    output.append(f"Profile: {profile['name']}")
    output.append("")
    output.append(generate_frame_assembly_cad(frame_spec))
    
    # Add bill of materials
    output.append("")
    output.append("```BOM")
    bom = {
        "description": "Bed Frame Components",
        "items": [
            {"qty": 2, "part": f"{profile['name']}", "length_mm": length_mm, "purpose": "Side Rails"},
            {"qty": 2, "part": f"{profile['name']}", "length_mm": width_mm, "purpose": "End Rails"},
            {"qty": 1, "part": f"{profile['name']}", "length_mm": length_mm, "purpose": "Center Support"},
            {"qty": 8, "part": "90° Corner Bracket", "purpose": "Corner Joints"},
            {"qty": 16, "part": "M8 T-Slot Bolt", "purpose": "Fasteners"}
        ]
    }
    output.append(json.dumps(bom, indent=2))
    output.append("```")
    
    return "\n".join(output)


def generate_kitchen_module_cad(
    width_mm: float = 600,
    height_mm: float = 900,
    depth_mm: float = 600,
    profile_id: str = '30x30_standard'
) -> str:
    """
    Generate CAD for campervan kitchen module frame.
    
    Args:
        width_mm: Module width
        height_mm: Module height
        depth_mm: Module depth
        profile_id: T-slot profile to use
    
    Returns:
        Delimiter-formatted CAD output
    """
    profile = get_profile_properties(profile_id)
    if not profile:
        raise ValueError(f"Profile '{profile_id}' not found")
    
    # Define frame members (4 vertical posts, top/bottom frames)
    members = [
        # Vertical posts (4x)
        {"profile_id": profile_id, "length_mm": height_mm, "position": {"x": 0, "y": 0, "z": 0}, 
         "rotation": {"x": 90, "y": 0, "z": 0}, "label": "Post 1"},
        {"profile_id": profile_id, "length_mm": height_mm, "position": {"x": width_mm, "y": 0, "z": 0}, 
         "rotation": {"x": 90, "y": 0, "z": 0}, "label": "Post 2"},
        {"profile_id": profile_id, "length_mm": height_mm, "position": {"x": 0, "y": 0, "z": depth_mm}, 
         "rotation": {"x": 90, "y": 0, "z": 0}, "label": "Post 3"},
        {"profile_id": profile_id, "length_mm": height_mm, "position": {"x": width_mm, "y": 0, "z": depth_mm}, 
         "rotation": {"x": 90, "y": 0, "z": 0}, "label": "Post 4"},
    ]
    
    frame_spec = {"members": members, "connections": []}
    
    output = []
    output.append(f"# Kitchen Module Frame - {width_mm}mm × {depth_mm}mm × {height_mm}mm")
    output.append(f"Profile: {profile['name']}")
    output.append("")
    output.append(generate_frame_assembly_cad(frame_spec))
    
    return "\n".join(output)


if __name__ == '__main__':
    # Test the module
    print("Testing CAD Generator Module\n")
    
    print("1. Single Beam CAD:")
    beam_cad = generate_tslot_beam_cad('40x40_standard', 1900)
    print(beam_cad[:200] + "...\n")
    
    print("2. Bed Frame CAD:")
    bed_cad = generate_bed_frame_cad(1400, 1900, '40x40_standard')
    print(bed_cad[:200] + "...\n")
    
    print("3. Kitchen Module CAD:")
    kitchen_cad = generate_kitchen_module_cad(600, 900, 600, '30x30_standard')
    print(kitchen_cad[:200] + "...")
