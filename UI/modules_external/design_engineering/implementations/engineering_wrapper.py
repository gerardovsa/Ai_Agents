"""
Design Engineering Module - Tool Wrappers
Implements @tool_executor wrappers for AI agent integration
"""

from tools.registry_v3 import tool_executor
from typing import Dict, List, Optional


@tool_executor()
def calculate_beam_deflection(
    length_mm: float,
    load_kg: float,
    profile_type: str = '40x40_standard',
    support_type: str = 'simply_supported'
) -> Dict:
    """
    Calculate structural properties for a T-slot aluminum beam under load.
    
    Returns deflection, stress, safety factor, and pass/fail status.
    Use when users ask to analyze beam performance or check load capacity.
    
    Args:
        length_mm: Beam span in millimeters
        load_kg: Expected load in kilograms
        profile_type: T-slot profile size (20x20_light to 80x80_standard)
        support_type: Support configuration (simply_supported, cantilever, fixed_both)
    
    Returns:
        Dict with deflection_mm, stress_mpa, safety_factor, checks, explanation
    """
    try:
        # Import inside function to avoid circular imports
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.engineering_tools import design_engineering_calculate_beam
        
        result = design_engineering_calculate_beam(
            length_mm=length_mm,
            load_kg=load_kg,
            profile_type=profile_type,
            support_type=support_type
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def compare_beam_profiles(
    length_mm: float,
    load_kg: float,
    support_type: str = 'simply_supported'
) -> Dict:
    """
    Compare multiple T-slot profiles to find the best option.
    
    Returns cost comparison and recommendations for different profile sizes.
    Use when users ask which profile to use or want cost optimization.
    
    Args:
        length_mm: Beam span in millimeters
        load_kg: Expected load in kilograms
        support_type: Support configuration
    
    Returns:
        Dict with comparisons, best_option, passing_count, summary
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.engineering_tools import design_engineering_compare_profiles
        
        result = design_engineering_compare_profiles(
            length_mm=length_mm,
            load_kg=load_kg,
            support_type=support_type
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def recommend_profile(
    length_mm: float,
    load_kg: float,
    application: Optional[str] = None
) -> Dict:
    """
    Get automatic T-slot profile recommendation for specific applications.
    
    Returns recommended profile with engineering justification.
    Use when users describe a project and need profile selection guidance.
    
    Args:
        length_mm: Primary span dimension in millimeters
        load_kg: Expected load in kilograms
        application: Application type (campervan_bed, workbench, etc.)
    
    Returns:
        Dict with recommended_profile, justification, alternatives
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.engineering_tools import design_engineering_recommend_profile
        
        result = design_engineering_recommend_profile(
            length_mm=length_mm,
            load_kg=load_kg,
            application=application
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def generate_bom(
    parts: List[Dict],
    include_fasteners: bool = True,
    format: str = 'markdown'
) -> Dict:
    """
    Generate Bill of Materials with real supplier parts and pricing.
    
    Returns detailed BOM with part numbers, quantities, costs from 4 suppliers.
    Use when users ask about project costs or need a parts list.
    
    Args:
        parts: List of parts with profile_id, length_mm, quantity
        include_fasteners: Include corner brackets, screws, t-nuts
        format: Output format (json, markdown, csv)
    
    Returns:
        Dict with BOM data, total_cost, supplier_comparison
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.parts_sourcing import generate_bom, export_bom_markdown
        
        bom_data = generate_bom(
            parts=parts,
            include_fasteners=include_fasteners
        )
        
        if format == 'markdown':
            bom_data['formatted_output'] = export_bom_markdown(bom_data)
        
        return {
            "success": True,
            "data": bom_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def generate_tslot_cad(
    profile_id: str,
    length_mm: float,
    color: str = "#C0C0C0"
) -> Dict:
    """
    Generate parametric CAD model of T-slot beam.
    
    Returns delimiter-formatted output with 3D visualization and technical drawing.
    Use when users ask to see a CAD model or need visual representation.
    
    Args:
        profile_id: T-slot profile identifier
        length_mm: Beam length in millimeters
        color: Hex color code for 3D model
    
    Returns:
        Dict with cad_output (delimiter-formatted string)
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.cad_generator import generate_tslot_beam_cad
        
        cad_output = generate_tslot_beam_cad(
            profile_id=profile_id,
            length_mm=length_mm,
            color=color
        )
        
        return {
            "success": True,
            "data": {
                "cad_output": cad_output,
                "profile_id": profile_id,
                "length_mm": length_mm
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def generate_constrained_beam_cad(
    profile_id: str,
    length_mm: float,
    mounting_holes: Optional[List[Dict]] = None,
    color: str = "#C0C0C0"
) -> Dict:
    """
    Generate parametric CAD model using CadQuery constraint solver.
    
    Returns accurate CAD with dimensional constraints validated.
    Use for precision engineering CAD where accuracy is critical.
    
    Args:
        profile_id: T-slot profile identifier
        length_mm: Beam length in millimeters
        mounting_holes: Optional list of hole specs with positions
        color: Hex color code
    
    Returns:
        Dict with delimiter_output, geometry, constraints_satisfied
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.constrained_cad_generator import ai_generate_constrained_beam
        
        result = ai_generate_constrained_beam(
            profile_id=profile_id,
            length_mm=length_mm,
            mounting_holes=mounting_holes,
            color=color
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def list_available_profiles(category: str = 'all') -> Dict:
    """
    List all available T-slot aluminum profiles.
    
    Returns complete profile catalog with dimensions and specifications.
    Use when users ask what profiles are available.
    
    Args:
        category: Filter by category (all, light, standard, heavy)
    
    Returns:
        Dict with profiles list
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.material_database import list_available_profiles
        
        profiles = list_available_profiles()
        
        if category != 'all':
            profiles = [p for p in profiles if category in p['id'].lower()]
        
        return {
            "success": True,
            "data": {
                "profiles": profiles,
                "count": len(profiles)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool_executor()
def list_available_materials() -> Dict:
    """
    List aluminum alloy materials with mechanical properties.
    
    Returns material specifications including yield strength, elastic modulus.
    Use when users ask about material properties or aluminum alloys.
    
    Returns:
        Dict with materials list
    """
    try:
        import sys
        import os
        module_path = os.path.join(os.path.dirname(__file__), '..')
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        from backend.material_database import list_available_materials
        
        materials = list_available_materials()
        
        return {
            "success": True,
            "data": {
                "materials": materials,
                "count": len(materials)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
