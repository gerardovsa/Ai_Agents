"""
Parametric CAD Module - CadQuery Tool Wrappers
This module provides @tool_executor wrappers for CadQuery CAD generation.

NOTE: This is a lightweight wrapper that delegates to the main cadquery implementation
in tools/implementations/cadquery.py to avoid code duplication.
"""

from tools.registry_v3 import tool_executor
from typing import Dict, Optional


@tool_executor()
def generate_cad_from_code(code: str, description: str = "CAD part") -> Dict:
    """
    Generate 3D CAD geometry from CadQuery Python code.
    
    AI writes the code, CadQuery generates professional-quality CAD geometry.
    Exports to STEP (for CAD software) and STL (for 3D printing/visualization).
    
    Args:
        code: CadQuery Python code that creates geometry. MUST set 'result' variable.
              Example: result = cq.Workplane('XY').box(100, 100, 50)
        description: Human-readable description of the CAD part
    
    Returns:
        Dict with success, step_file path, stl_file path, geometry stats
    """
    try:
        # Import the main cadquery implementation
        from tools.implementations.cadquery import generate_cad_from_code as _generate
        
        result = _generate(code, description)
        
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
def validate_cadquery_code(code: str) -> Dict:
    """
    Validate CadQuery Python code before execution.
    
    Checks for syntax errors, missing imports, and common mistakes.
    Use this before calling generate_cad_from_code to avoid errors.
    
    Args:
        code: CadQuery Python code to validate
    
    Returns:
        Dict with valid (bool) and error (if invalid)
    """
    try:
        from tools.implementations.cadquery import validate_cadquery_code as _validate
        
        result = _validate(code)
        
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
def list_cadquery_templates() -> Dict:
    """
    List all available CadQuery code templates.
    
    Returns templates for fasteners, gears, bearings, mechanical parts,
    automotive components, and enclosures. Use as reference patterns.
    
    Returns:
        Dict with templates list (name, code, description, category)
    """
    try:
        from tools.implementations.cadquery import list_cadquery_templates as _list
        
        result = _list()
        
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
def get_cadquery_template(name: str) -> Dict:
    """
    Get specific CadQuery template code by name.
    
    Returns working Python code that can be modified for your needs.
    
    Args:
        name: Template name (e.g., 'simple_car_body', 'wheel_rim', 'spur_gear')
    
    Returns:
        Dict with code and description, or error if not found
    """
    try:
        from tools.implementations.cadquery import get_cadquery_template as _get
        
        result = _get(name)
        
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
def cadquery_export_dxf(step_file_path: str, output_path: Optional[str] = None) -> Dict:
    """
    Export STEP file to DXF format for laser cutting or CNC machining.
    
    Converts 3D CAD to 2D profile suitable for manufacturing.
    
    Args:
        step_file_path: Path to STEP file (from generate_cad_from_code result)
        output_path: Optional custom output path for DXF file
    
    Returns:
        Dict with success, dxf_file path, or error
    """
    try:
        from tools.implementations.cadquery import cadquery_export_dxf as _export
        
        result = _export(step_file_path, output_path)
        
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
def cadquery_export_svg(step_file_path: str, output_path: Optional[str] = None) -> Dict:
    """
    Export STEP file to SVG format for technical drawings.
    
    Creates 2D vector graphics with orthographic projections.
    
    Args:
        step_file_path: Path to STEP file
        output_path: Optional custom output path for SVG file
    
    Returns:
        Dict with success, svg_file path, or error
    """
    try:
        from tools.implementations.cadquery import cadquery_export_svg as _export
        
        result = _export(step_file_path, output_path)
        
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
def cadquery_list_generated_files(file_type: str = 'all') -> Dict:
    """
    List all previously generated CAD files.
    
    Shows file names, sizes, creation dates for STEP, STL, DXF, SVG files.
    
    Args:
        file_type: Filter by file type (all, step, stl, dxf, svg)
    
    Returns:
        Dict with files list
    """
    try:
        from tools.implementations.cadquery import cadquery_list_generated_files as _list
        
        result = _list(file_type)
        
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
def cadquery_get_file_info(file_path: str) -> Dict:
    """
    Get detailed information about a specific CAD file.
    
    Returns geometry statistics (vertices, faces, volume), bounding box, metadata.
    
    Args:
        file_path: Path to CAD file (STEP or STL)
    
    Returns:
        Dict with file info and geometry stats
    """
    try:
        from tools.implementations.cadquery import cadquery_get_file_info as _info
        
        result = _info(file_path)
        
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
def cadquery_calculate_mass(step_file_path: str, density_g_cm3: float = 2.7) -> Dict:
    """
    Calculate mass properties of a CAD part given material density.
    
    Returns mass, center of gravity, moment of inertia for engineering analysis.
    
    Args:
        step_file_path: Path to STEP file
        density_g_cm3: Material density in g/cm³
                       (2.7 for aluminum, 7.85 for steel, 1.2 for ABS plastic)
    
    Returns:
        Dict with mass, center_of_gravity, moment_of_inertia
    """
    try:
        from tools.implementations.cadquery import cadquery_calculate_mass as _calculate
        
        result = _calculate(step_file_path, density_g_cm3)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
