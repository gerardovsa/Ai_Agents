"""
Engineering Tools - AI Agent Wrapper Functions
Provides natural language interface for AI agents to access engineering capabilities
"""

from typing import Dict, List, Optional
from .structural_analysis import (
    calculate_beam_deflection,
    analyze_multiple_profiles,
    calculate_distributed_load_capacity,
    calculate_column_buckling
)
from .material_database import (
    get_profile_properties,
    get_material_properties,
    list_available_profiles,
    list_available_materials,
    recommend_profile_for_load,
    get_profile_for_application,
    calculate_total_cost
)
from .cad_generator import (
    generate_tslot_beam_cad,
    generate_bed_frame_cad,
    generate_kitchen_module_cad
)
from .constrained_cad_generator import (
    ai_generate_constrained_beam,
    ai_generate_constrained_assembly,
    ConstrainedCADGenerator
)
from .parts_sourcing import (
    generate_bom,
    generate_bed_frame_bom,
    generate_kitchen_module_bom,
    compare_suppliers_for_design,
    export_bom_markdown
)


# ============================================================================
# AI TOOL FUNCTIONS - Natural Language Interface
# ============================================================================

def design_engineering_calculate_beam(
    length_mm: float,
    load_kg: float,
    profile_type: str = '40x40_standard',
    support_type: str = 'simply_supported'
) -> Dict:
    """
    AI Tool: Calculate structural properties for a beam under load.
    
    Use this when the user asks to:
    - "Calculate beam deflection for..."
    - "Check if this beam can support..."
    - "What's the safety factor for..."
    - "Analyze structural performance..."
    
    Args:
        length_mm: Beam span in millimeters (e.g., 1900 for 1.9m bed frame)
        load_kg: Expected load in kilograms (e.g., 200 for two people)
        profile_type: T-slot profile size:
            - '20x20_light': Small hobbyist projects
            - '30x30_standard': Medium furniture
            - '40x40_light': Light campervan frames
            - '40x40_standard': Standard campervan use (MOST COMMON)
            - '40x40_heavy': Heavy-duty applications
            - '60x60_standard': Very heavy loads
            - '80x80_standard': Industrial machinery
        support_type: How beam is supported:
            - 'simply_supported': Both ends on supports (most common for beds/benches)
            - 'cantilever': One end fixed, one end free (overhangs, shelves)
            - 'fixed_both': Both ends rigidly fixed (rare)
    
    Returns:
        Analysis with deflection, stress, safety factor, and pass/fail status
    """
    result = calculate_beam_deflection(length_mm, load_kg, profile_type, support_type)
    
    # Add human-readable explanation
    if result['checks']['overall_pass']:
        explanation = f"✓ This design is SAFE. The {result['profile_name']} beam will deflect only "
        explanation += f"{result['deflection_mm']:.2f}mm under {load_kg}kg load, which is within acceptable limits "
        explanation += f"({result['deflection_ratio']}). Safety factor is {result['safety_factor']:.1f}x."
    else:
        explanation = f"✗ This design FAILS safety checks. "
        if not result['checks']['deflection_ok']:
            explanation += f"Deflection ({result['deflection_mm']:.2f}mm) exceeds limit "
            explanation += f"({result['max_allowed_deflection_mm']:.2f}mm). "
        if not result['checks']['safety_ok']:
            explanation += f"Safety factor ({result['safety_factor']:.1f}) is below minimum 2.0. "
        explanation += "Recommendation: Use a larger profile or reduce span/load."
    
    result['explanation'] = explanation
    return result


def design_engineering_compare_profiles(
    length_mm: float,
    load_kg: float,
    support_type: str = 'simply_supported'
) -> Dict:
    """
    AI Tool: Compare multiple profiles to find the best option.
    
    Use this when the user asks:
    - "What's the cheapest profile that will work?"
    - "Compare different beam sizes for..."
    - "Which profile should I use for..."
    
    Returns:
        Comparison of all suitable profiles with cost analysis
    """
    # Analyze common profiles
    common_profiles = ['40x40_light', '40x40_standard', '40x40_heavy', 
                      '30x30_standard', '60x60_standard']
    
    comparisons = analyze_multiple_profiles(
        length_mm, load_kg, support_type, common_profiles
    )
    
    # Find cheapest passing option
    passing_options = [c for c in comparisons if c['checks']['overall_pass']]
    
    if passing_options:
        best_option = passing_options[0]  # Already sorted by cost
        summary = f"Cheapest option: {best_option['profile_name']} at ${best_option['cost_aud_per_meter']:.2f}/m. "
        summary += f"SF={best_option['safety_factor']:.1f}, deflection={best_option['deflection_mm']:.2f}mm."
    else:
        summary = "⚠ None of the standard profiles meet requirements. Consider custom design or reduce span/load."
    
    return {
        'comparisons': comparisons,
        'passing_count': len(passing_options),
        'best_option': passing_options[0] if passing_options else None,
        'summary': summary
    }


def design_engineering_recommend_profile(
    length_mm: float,
    load_kg: float,
    application: str = None
) -> Dict:
    """
    AI Tool: Get automatic profile recommendation for specific application.
    
    Use this when the user asks:
    - "What profile do I need for a bed frame?"
    - "Recommend a beam size for..."
    - "Size this for me..."
    
    Args:
        length_mm: Span length
        load_kg: Expected load
        application: Optional application hint:
            - 'campervan_bed'
            - 'campervan_kitchen'
            - 'workbench'
            - 'display_stand'
    
    Returns:
        Recommended profile with analysis and justification
    """
    recommendation = recommend_profile_for_load(length_mm, load_kg)
    
    if not recommendation:
        return {
            'success': False,
            'message': 'No suitable profile found. The load or span may be too large for standard T-slot profiles.',
            'suggestion': 'Consider: 1) Reduce span with additional supports, 2) Use steel instead of aluminum, 3) Add center support beam'
        }
    
    # Get full analysis for recommended profile
    analysis = calculate_beam_deflection(
        length_mm, load_kg, recommendation['profile_id']
    )
    
    return {
        'success': True,
        'recommended_profile': recommendation['profile_id'],
        'profile_name': recommendation['name'],
        'cost_per_meter_aud': recommendation['cost_aud_m'],
        'total_cost_aud': round(recommendation['cost_aud_m'] * (length_mm / 1000), 2),
        'safety_factor': recommendation['safety_factor'],
        'deflection_mm': recommendation['deflection_mm'],
        'weight_kg': round(recommendation['weight_kg_m'] * (length_mm / 1000), 2),
        'analysis': analysis,
        'justification': f"This is the most economical profile that meets safety requirements (SF={recommendation['safety_factor']:.1f}, deflection={recommendation['deflection_mm']:.2f}mm)."
    }


def design_engineering_generate_cad_model(
    component_type: str,
    specifications: Dict
) -> str:
    """
    AI Tool: Generate 3D CAD model and 2D technical drawings.
    
    Use this when the user asks:
    - "Show me a 3D model of..."
    - "Generate CAD for..."
    - "Create a drawing of..."
    - "Visualize this design..."
    
    Args:
        component_type: Type of component to generate:
            - 'beam': Single T-slot beam
            - 'bed_frame': Complete campervan bed frame
            - 'kitchen_module': Kitchen frame structure
        specifications: Component parameters:
            For 'beam':
                - profile_id: '40x40_standard'
                - length_mm: 1900
            For 'bed_frame':
                - width_mm: 1400
                - length_mm: 1900
                - profile_id: '40x40_standard'
            For 'kitchen_module':
                - width_mm: 600
                - height_mm: 900
                - depth_mm: 600
                - profile_id: '30x30_standard'
    
    Returns:
        Delimiter-formatted CAD output for visualization engine
    """
    if component_type == 'beam':
        return generate_tslot_beam_cad(
            specifications['profile_id'],
            specifications['length_mm'],
            specifications.get('color', '#C0C0C0')
        )
    
    elif component_type == 'bed_frame':
        return generate_bed_frame_cad(
            specifications.get('width_mm', 1400),
            specifications.get('length_mm', 1900),
            specifications.get('profile_id', '40x40_standard')
        )
    
    elif component_type == 'kitchen_module':
        return generate_kitchen_module_cad(
            specifications.get('width_mm', 600),
            specifications.get('height_mm', 900),
            specifications.get('depth_mm', 600),
            specifications.get('profile_id', '30x30_standard')
        )
    
    else:
        return f"Error: Unknown component type '{component_type}'"


def design_engineering_create_bom(
    design_type: str,
    specifications: Dict,
    supplier: str = 'makerbeam_australia'
) -> Dict:
    """
    AI Tool: Generate Bill of Materials with supplier pricing.
    
    Use this when the user asks:
    - "What parts do I need for..."
    - "Create a shopping list for..."
    - "How much will this cost..."
    - "Generate BOM for..."
    
    Args:
        design_type: Type of design:
            - 'bed_frame'
            - 'kitchen_module'
            - 'custom'
        specifications: Design parameters (same as CAD generation)
        supplier: Preferred supplier:
            - 'makerbeam_australia': Australian local, fast shipping
            - 'openbuilds_parts': USA, good hobbyist selection
            - 'faztek_global': USA, heavy-duty industrial
            - 'misumi_australia': Australian, custom cut lengths
    
    Returns:
        Complete BOM with part numbers, costs, and supplier links
    """
    if design_type == 'bed_frame':
        bom = generate_bed_frame_bom(
            specifications.get('width_mm', 1400),
            specifications.get('length_mm', 1900),
            specifications.get('profile_id', '40x40_standard'),
            supplier
        )
    
    elif design_type == 'kitchen_module':
        bom = generate_kitchen_module_bom(
            specifications.get('width_mm', 600),
            specifications.get('height_mm', 900),
            specifications.get('depth_mm', 600),
            specifications.get('profile_id', '30x30_standard'),
            supplier
        )
    
    elif design_type == 'custom':
        bom = generate_bom(specifications, supplier)
    
    else:
        return {'error': f"Unknown design type '{design_type}'"}
    
    # Add markdown export for easy reading
    bom['markdown'] = export_bom_markdown(bom)
    
    return bom


def design_engineering_get_specifications() -> Dict:
    """
    AI Tool: Get complete reference of available profiles and materials.
    
    Use this when the user asks:
    - "What profiles are available?"
    - "Show me T-slot options..."
    - "What materials can I use?"
    - "List aluminum types..."
    
    Returns:
        Complete catalog of profiles, materials, and typical applications
    """
    profiles = list_available_profiles()
    materials = list_available_materials()
    
    return {
        'profiles': {
            'count': len(profiles),
            'list': profiles,
            'sizes_available': list(set(p['size'] for p in profiles)),
            'price_range_aud_per_meter': {
                'min': min(p['cost_aud_m'] for p in profiles),
                'max': max(p['cost_aud_m'] for p in profiles)
            }
        },
        'materials': {
            'count': len(materials),
            'list': materials
        },
        'common_applications': {
            'campervan_bed_1400x1900mm': {
                'recommended_profiles': ['40x40_standard', '40x40_heavy'],
                'typical_load_kg': 200,
                'estimated_cost_aud': '150-250'
            },
            'campervan_kitchen_600x900mm': {
                'recommended_profiles': ['30x30_standard', '40x40_standard'],
                'typical_load_kg': 50,
                'estimated_cost_aud': '100-180'
            },
            'workbench_2000x800mm': {
                'recommended_profiles': ['40x40_standard', '60x60_standard'],
                'typical_load_kg': 300,
                'estimated_cost_aud': '200-350'
            }
        },
        'usage_tips': [
            "40x40_standard is the most versatile profile for campervan use",
            "Always aim for safety factor ≥ 2.0",
            "Keep deflection under L/360 for general structures",
            "Add center supports for spans over 1500mm",
            "Use corner brackets rated for expected loads"
        ]
    }


def design_engineering_complete_workflow(
    description: str,
    length_mm: float,
    width_mm: Optional[float] = None,
    load_kg: float = 200
) -> Dict:
    """
    AI Tool: Complete design workflow from description to BOM.
    
    Use this when the user provides a complete design request:
    - "I want to build a bed frame, 1900mm x 1400mm for 200kg"
    - "Design a kitchen module 600mm wide..."
    
    This function automatically:
    1. Recommends profile
    2. Performs structural analysis
    3. Generates CAD model
    4. Creates BOM with pricing
    
    Returns:
        Complete design package with all deliverables
    """
    # Determine design type from description
    design_type = 'beam'
    if 'bed' in description.lower():
        design_type = 'bed_frame'
        if not width_mm:
            width_mm = 1400  # Default bed width
    elif 'kitchen' in description.lower():
        design_type = 'kitchen_module'
        if not width_mm:
            width_mm = 600  # Default kitchen width
    
    # Step 1: Recommend profile
    recommendation = design_engineering_recommend_profile(length_mm, load_kg)
    
    if not recommendation['success']:
        return {
            'success': False,
            'message': recommendation['message'],
            'suggestion': recommendation['suggestion']
        }
    
    profile_id = recommendation['recommended_profile']
    
    # Step 2: Structural analysis
    analysis = recommendation['analysis']
    
    # Step 3: Generate CAD
    specifications = {
        'length_mm': length_mm,
        'profile_id': profile_id
    }
    
    if design_type == 'bed_frame':
        specifications['width_mm'] = width_mm
        specifications['length_mm'] = length_mm
        cad_output = design_engineering_generate_cad_model('bed_frame', specifications)
    elif design_type == 'kitchen_module':
        specifications['width_mm'] = width_mm
        specifications['height_mm'] = 900  # Default height
        specifications['depth_mm'] = 600   # Default depth
        cad_output = design_engineering_generate_cad_model('kitchen_module', specifications)
    else:
        cad_output = design_engineering_generate_cad_model('beam', specifications)
    
    # Step 4: Generate BOM
    bom = design_engineering_create_bom(design_type, specifications)
    
    # Compile complete design package
    return {
        'success': True,
        'design_type': design_type,
        'description': description,
        'recommended_profile': {
            'id': profile_id,
            'name': recommendation['profile_name'],
            'cost_per_meter_aud': recommendation['cost_per_meter_aud']
        },
        'structural_analysis': analysis,
        'cad_model': cad_output,
        'bill_of_materials': bom,
        'total_project_cost_aud': bom['summary']['grand_total_aud'],
        'summary': f"Design complete! Using {recommendation['profile_name']}, "
                  f"safety factor {recommendation['safety_factor']:.1f}, "
                  f"total cost ${bom['summary']['grand_total_aud']:.2f} AUD including shipping."
    }


def design_engineering_generate_accurate_cad(
    profile_id: str,
    length_mm: float,
    mounting_holes: Optional[List[Dict]] = None
) -> str:
    """
    AI Tool: Generate CAD with geometric constraints for accurate dimensions.
    
    **USE THIS INSTEAD OF design_engineering_generate_cad_model FOR ACCURATE CAD**
    
    Use this when the user asks:
    - "Generate accurate CAD..."
    - "Create a beam with proper dimensions..."
    - "Design with correct spacing..."
    - "Make sure measurements are exact..."
    
    This uses CadQuery constraint solver to ensure:
    - ✓ Exact dimensions (within 0.1mm tolerance)
    - ✓ Proportionate geometry
    - ✓ Correct spacing between features
    - ✓ Proper hole placement (min 20mm apart, 10mm from edges)
    
    Args:
        profile_id: T-slot profile (e.g., '40x40_standard', '20x20_lite')
        length_mm: Beam length in millimeters
        mounting_holes: Optional list of hole specifications:
            [{"x": 50, "y": 20, "diameter": 5.0}, ...]
    
    Returns:
        Delimiter-formatted CAD with verified dimensions
    
    Example AI conversation:
        User: "Generate a 500mm beam with mounting holes"
        AI: calls design_engineering_generate_accurate_cad(
            profile_id='40x40_standard',
            length_mm=500,
            mounting_holes=[
                {"x": 50, "y": 20, "diameter": 5.0},
                {"x": 450, "y": 20, "diameter": 5.0}
            ]
        )
    """
    return ai_generate_constrained_beam(
        profile_id=profile_id,
        length_mm=length_mm,
        mounting_holes=mounting_holes
    )


def design_engineering_generate_assembly(
    parts: List[Dict],
    constraints: List[Dict]
) -> str:
    """
    AI Tool: Generate multi-part assembly with geometric constraints.
    
    Use this when the user asks:
    - "Create a structure with multiple beams..."
    - "Design a frame with proper connections..."
    - "Make an assembly where parts align..."
    - "Build something with parallel/perpendicular beams..."
    
    This ensures:
    - ✓ Parts are properly aligned
    - ✓ Distances between parts are maintained
    - ✓ Parallel/perpendicular relationships are enforced
    - ✓ No geometric conflicts
    
    Args:
        parts: List of part specifications:
            [{
                "name": "base",
                "type": "tslot_beam",
                "profile_id": "40x40_standard",
                "length": 500
            }, ...]
        
        constraints: List of geometric constraints:
            [{
                "type": "coincident",
                "part1": "base",
                "face1": ">Z",
                "part2": "upright",
                "face2": "<Z"
            }, ...]
        
        Constraint types:
        - "coincident": Faces/edges touch
        - "distance": Fixed distance between parts
        - "parallel": Edges stay parallel
        - "perpendicular": Edges stay perpendicular (90°)
    
    Returns:
        Delimiter-formatted assembly CAD
    
    Example AI conversation:
        User: "Build an L-shaped frame"
        AI: calls design_engineering_generate_assembly(
            parts=[
                {"name": "horizontal", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 500},
                {"name": "vertical", "type": "tslot_beam", "profile_id": "40x40_standard", "length": 300}
            ],
            constraints=[
                {"type": "coincident", "part1": "horizontal", "face1": ">Z", "part2": "vertical", "face2": "<Z"},
                {"type": "perpendicular", "part1": "horizontal", "edge1": "|X", "part2": "vertical", "edge2": "|Z"}
            ]
        )
    """
    return ai_generate_constrained_assembly(
        parts=parts,
        constraints=constraints
    )


# Export all tool functions
__all__ = [
    'design_engineering_calculate_beam',
    'design_engineering_compare_profiles',
    'design_engineering_recommend_profile',
    'design_engineering_generate_cad_model',
    'design_engineering_generate_accurate_cad',
    'design_engineering_generate_assembly',
    'design_engineering_create_bom',
    'design_engineering_get_specifications',
    'design_engineering_complete_workflow'
]


if __name__ == '__main__':
    # Test the AI tools
    print("Testing Engineering AI Tools\n")
    
    print("1. Calculate Beam:")
    result = design_engineering_calculate_beam(1900, 200, '40x40_standard')
    print(f"   {result['explanation']}\n")
    
    print("2. Recommend Profile:")
    rec = design_engineering_recommend_profile(1900, 200)
    print(f"   {rec['justification']}\n")
    
    print("3. Complete Workflow:")
    workflow = design_engineering_complete_workflow(
        "I want to build a bed frame for my campervan",
        length_mm=1900,
        width_mm=1400,
        load_kg=200
    )
    print(f"   {workflow['summary']}")
