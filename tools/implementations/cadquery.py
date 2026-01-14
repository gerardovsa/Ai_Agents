"""
CadQuery Tool Implementation
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
ai_infra_path = Path(__file__).parent.parent.parent / "AI_infrastructure"
sys.path.insert(0, str(ai_infra_path))

# Import from AI_infrastructure/tools
from AI_infrastructure.tools.cadquery_generator import (
    generate_cad_from_code as _generate_cad,
    validate_cadquery_code as _validate_code,
    list_cadquery_templates as _list_templates,
    get_cadquery_template as _get_template,
    cadquery_export_dxf as _export_dxf,
    cadquery_export_svg as _export_svg,
    cadquery_list_generated_files as _list_files,
    cadquery_get_file_info as _get_file_info,
    cadquery_calculate_mass as _calculate_mass
)


def generate_cad_from_code(code: str, description: str = "CAD part"):
    """
    Generate CAD from CadQuery Python code
    
    Args:
        code: CadQuery Python code (must set 'result' variable)
        description: Human-readable description
    
    Returns:
        Dict with success, file paths, geometry stats
    """
    return _generate_cad(code, description)


def validate_cadquery_code(code: str):
    """
    Validate CadQuery code before execution
    
    Args:
        code: CadQuery Python code
    
    Returns:
        Dict with valid (bool) and error (if invalid)
    """
    return _validate_code(code)


def list_cadquery_templates():
    """
    List all available CadQuery templates
    
    Returns:
        List of template objects with name, code, description, category
    """
    templates = _list_templates()
    return {"templates": templates}


def get_cadquery_template(name: str):
    """
    Get specific CadQuery template by name
    
    Args:
        name: Template name
    
    Returns:
        Dict with code and description, or error if not found
    """
    code = _get_template(name)
    if code:
        # Get description from list
        templates = _list_templates()
        template_info = next((t for t in templates if t['name'] == name), None)
        return {
            "code": code,
            "description": template_info['description'] if template_info else name
        }
    else:
        return {"error": f"Template '{name}' not found"}


def cadquery_export_dxf(step_file_path: str, output_path: str = None):
    """
    Export STEP file to DXF format for laser cutting/CNC
    
    Args:
        step_file_path: Path to STEP file
        output_path: Optional custom output path
    
    Returns:
        Dict with success, dxf_file path, or error
    """
    return _export_dxf(step_file_path, output_path)


def cadquery_export_svg(step_file_path: str, output_path: str = None, width: int = 800, height: int = 600):
    """
    Export STEP file as SVG technical drawing
    
    Args:
        step_file_path: Path to STEP file
        output_path: Optional custom output path
        width: SVG width in pixels (default 800)
        height: SVG height in pixels (default 600)
    
    Returns:
        Dict with success, svg_file path, svg_content, or error
    """
    return _export_svg(step_file_path, output_path, width, height)


def cadquery_list_generated_files(filter_type: str = None):
    """
    List all generated CAD files
    
    Args:
        filter_type: Optional filter ('step', 'stl', 'dxf', 'svg')
    
    Returns:
        Dict with files list, count, total_size_mb, directory
    """
    return _list_files(filter_type)


def cadquery_get_file_info(file_path: str):
    """
    Get detailed information about a CAD file
    
    Args:
        file_path: Path to CAD file
    
    Returns:
        Dict with file metadata and geometry info, or error
    """
    return _get_file_info(file_path)


def cadquery_calculate_mass(step_file_path: str, material_density: float, units: str = 'g/cm3'):
    """
    Calculate mass of CAD part given material density
    
    Args:
        step_file_path: Path to STEP file
        material_density: Material density (e.g., 2.7 for aluminum)
        units: Density units ('g/cm3' or 'kg/m3')
    
    Returns:
        Dict with mass_grams, mass_kg, volume, or error
    """
    return _calculate_mass(step_file_path, material_density, units)
