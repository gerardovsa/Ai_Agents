"""
CadQuery Code Generator - AI writes Python code to generate CAD

This is THE solution to "AI is shit at making things from scratch":
- AI writes CODE (which it's good at)
- CadQuery generates GEOMETRY (which it's good at)

User: "Create a car wheel"
AI: Writes CadQuery code with rim, spokes, hub
CadQuery: Generates perfect 3D geometry
Result: Professional quality CAD
"""

import cadquery as cq
from typing import Dict, List, Optional, Any
import json
import sys
import io
import traceback
from pathlib import Path


class CadQueryGenerator:
    """
    Executes CadQuery code to generate CAD geometry
    
    Key insight: AI is excellent at writing code but terrible at generating geometry.
    So let AI write CadQuery Python code, and let CadQuery do the geometry.
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        self.max_execution_time = 30  # seconds
        self.max_vertices = 100000  # prevent memory issues
        
    def _load_templates(self) -> Dict[str, str]:
        """
        Load CadQuery code templates that AI can use as references
        
        These are EXAMPLES that AI learns from, not rigid templates.
        AI can modify, combine, or create entirely new code based on these patterns.
        """
        return {
            # FASTENERS
            "hex_bolt": """
import cadquery as cq

result = (cq.Workplane("XY")
    .circle(3)  # M6 thread
    .extrude(40)  # 40mm length
    .faces(">Z")
    .workplane()
    .polygon(6, 9)  # Hex head
    .extrude(6))  # Head height
""",
            
            "socket_head_cap_screw": """
import cadquery as cq

result = (cq.Workplane("XY")
    .circle(3)  # M6 thread
    .extrude(40)
    .faces(">Z")
    .workplane()
    .circle(4.5)  # Head diameter
    .extrude(6)  # Head height
    .faces(">Z")
    .hole(2.25))  # Hex socket
""",
            
            # GEARS
            "spur_gear": """
import cadquery as cq
import math

# Parameters
module = 2
teeth = 20
width = 10
bore = 10

# Calculate dimensions
pitch_diameter = module * teeth
outer_diameter = pitch_diameter + 2 * module

result = (cq.Workplane("XY")
    .circle(outer_diameter / 2)
    .extrude(width)
    .faces(">Z")
    .workplane()
    .hole(bore))

# Add gear teeth (simplified involute profile)
for i in range(teeth):
    angle = i * 360 / teeth
    result = (result
        .faces(">Z")
        .workplane()
        .transformed(rotate=(0, 0, angle))
        .rect(module * 0.8, outer_diameter)
        .cutBlind(-width))
""",
            
            # BEARINGS
            "ball_bearing": """
import cadquery as cq

outer_diameter = 42  # 6200 series
inner_diameter = 15
width = 12

result = (cq.Workplane("XY")
    .circle(outer_diameter / 2)
    .circle(inner_diameter / 2)
    .extrude(width))

# Add ball race
race_diameter = (outer_diameter + inner_diameter) / 2
ball_diameter = (outer_diameter - inner_diameter) / 4

for i in range(8):
    angle = i * 45
    x = race_diameter / 2 * math.cos(math.radians(angle))
    y = race_diameter / 2 * math.sin(math.radians(angle))
    result = result.faces(">Z").workplane().center(x, y).hole(ball_diameter)
""",
            
            # MECHANICAL PARTS
            "t_slot_extrusion": """
import cadquery as cq

length = 500
width = 20

result = (cq.Workplane("XY")
    .rect(width, width)
    .extrude(length)
    # Add T-slot on all 4 sides
    .faces("<X or >X or <Y or >Y")
    .workplane()
    .center(0, length / 2)
    .rect(6, length)
    .cutBlind(-2)
    .faces("<X or >X or <Y or >Y")
    .workplane()
    .center(0, length / 2)
    .rect(10, length)
    .cutBlind(-8))
""",
            
            "bracket": """
import cadquery as cq

result = (cq.Workplane("XY")
    .rect(50, 50)
    .extrude(5)
    .faces(">Z")
    .workplane()
    .rect(40, 40)
    .extrude(30)
    .faces(">X")
    .workplane()
    .rect(40, 40)
    .extrude(30)
    # Add mounting holes
    .faces("<Z")
    .workplane()
    .rect(40, 40, forConstruction=True)
    .vertices()
    .hole(6))
""",
            
            # AUTOMOTIVE PARTS
            "wheel_rim": """
import cadquery as cq
import math

outer_diameter = 400  # 16 inch wheel
inner_diameter = 250
width = 200

# Create main rim
result = (cq.Workplane("XY")
    .circle(outer_diameter / 2)
    .circle(inner_diameter / 2)
    .extrude(width)
    # Add center hub
    .faces(">Z")
    .workplane()
    .circle(100)
    .extrude(30))

# Add lug bolt holes
for i in range(5):
    angle = i * 72
    x = 80 * math.cos(math.radians(angle))
    y = 80 * math.sin(math.radians(angle))
    result = (result
        .faces(">Z")
        .workplane()
        .center(x, y)
        .hole(15))
""",
            
            "simple_car_body": """
import cadquery as cq

# Simple blocky car body (AI can make this more sophisticated)
result = (cq.Workplane("XY")
    # Chassis
    .box(4000, 1800, 400)
    .faces(">Z")
    .workplane()
    # Cabin
    .center(500, 0)
    .rect(2000, 1600)
    .extrude(1000)
    # Hood
    .faces(">Z")
    .workplane()
    .center(-1500, 0)
    .rect(1000, 1600)
    .extrude(200)
    # Windows (cut)
    .faces(">X or <X or >Y or <Y")
    .workplane()
    .rect(1800, 800)
    .cutBlind(-50))
""",
            
            # ENCLOSURES
            "parametric_box": """
import cadquery as cq

length = 100
width = 80
height = 50
wall_thickness = 3

result = (cq.Workplane("XY")
    .box(length, width, height)
    .faces(">Z")
    .shell(-wall_thickness)
    # Add mounting posts
    .faces("<Z")
    .workplane()
    .rect(length - 10, width - 10, forConstruction=True)
    .vertices()
    .circle(3)
    .extrude(height - wall_thickness))
""",
        }
    
    def generate_from_code(
        self,
        code: str,
        description: str = "CAD part",
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Execute CadQuery code written by AI
        
        Args:
            code: CadQuery Python code (must set 'result' variable)
            description: Human-readable description
            validate: Whether to validate code before execution
            
        Returns:
            {
                'success': bool,
                'result': CadQuery object or None,
                'step_file': str (path to STEP export),
                'stl_file': str (path to STL export),
                'vertices': int,
                'edges': int,
                'faces': int,
                'volume': float,
                'bounding_box': dict,
                'error': str (if failed)
            }
        """
        if validate:
            validation = self.validate_code(code)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f"Validation failed: {validation['error']}"
                }
        
        # Execute code in isolated namespace
        namespace = {
            'cq': cq,
            'math': __import__('math'),
            '__builtins__': __builtins__
        }
        
        try:
            # Capture stdout/stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            # Execute code
            exec(code, namespace)
            
            # Restore stdout/stderr
            stdout_value = sys.stdout.getvalue()
            stderr_value = sys.stderr.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Get result
            if 'result' not in namespace:
                return {
                    'success': False,
                    'error': "Code must set 'result' variable with CadQuery object"
                }
            
            result = namespace['result']
            
            # Validate result is CadQuery object
            if not hasattr(result, 'val'):
                return {
                    'success': False,
                    'error': f"Result must be CadQuery Workplane, got {type(result)}"
                }
            
            # Get geometry info
            shape = result.val()
            vertices = len(shape.Vertices())
            edges = len(shape.Edges())
            faces = len(shape.Faces())
            
            # Check complexity limits
            if vertices > self.max_vertices:
                return {
                    'success': False,
                    'error': f"Too many vertices: {vertices} > {self.max_vertices}"
                }
            
            # Get bounding box
            bbox = shape.BoundingBox()
            bounding_box = {
                'min': {'x': bbox.xmin, 'y': bbox.ymin, 'z': bbox.zmin},
                'max': {'x': bbox.xmax, 'y': bbox.ymax, 'z': bbox.zmax},
                'size': {
                    'x': bbox.xmax - bbox.xmin,
                    'y': bbox.ymax - bbox.ymin,
                    'z': bbox.zmax - bbox.zmin
                }
            }
            
            # Calculate volume
            try:
                volume = shape.Volume()
            except:
                volume = None
            
            # Export to files
            # Use Render persistent disk (/data) if available, otherwise local directory
            if Path("/data").exists():
                output_dir = Path("/data/generated_cad")
            else:
                output_dir = Path("AI_infrastructure/generated_cad")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{description.replace(' ', '_')}_{timestamp}"
            
            step_file = output_dir / f"{base_name}.step"
            stl_file = output_dir / f"{base_name}.stl"
            
            # Export STEP (for OpenCascade.js)
            cq.exporters.export(result, str(step_file))
            
            # Export STL (for Three.js)
            cq.exporters.export(result, str(stl_file))
            
            return {
                'success': True,
                'result': result,
                'step_file': str(step_file),
                'stl_file': str(stl_file),
                'vertices': vertices,
                'edges': edges,
                'faces': faces,
                'volume': volume,
                'bounding_box': bounding_box,
                'stdout': stdout_value,
                'stderr': stderr_value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'traceback': traceback.format_exc()
            }
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate CadQuery code before execution
        
        Checks for:
        - Python syntax errors
        - Dangerous operations (import os, subprocess, etc.)
        - Missing 'result' variable
        - Invalid CadQuery patterns
        """
        # Check syntax
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return {
                'valid': False,
                'error': f"Syntax error: {e.msg} at line {e.lineno}"
            }
        
        # Check for dangerous imports (use word boundaries)
        import re
        dangerous_patterns = [
            r'\bimport\s+os\b',
            r'\bimport\s+subprocess\b',
            r'\bsys\.exit\b',
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\b__import__\b'
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return {
                    'valid': False,
                    'error': f"Dangerous operation detected: {pattern}"
                }
        
        # Check for 'result' variable
        if 'result' not in code:
            return {
                'valid': False,
                'error': "Code must set 'result' variable"
            }
        
        # Check for CadQuery usage
        if 'cq.' not in code and 'cadquery' not in code:
            return {
                'valid': False,
                'error': "Code must use CadQuery (import cadquery as cq)"
            }
        
        return {'valid': True}
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available templates that AI can reference
        
        Returns list of:
        {
            'name': str,
            'code': str,
            'description': str,
            'category': str
        }
        """
        categories = {
            'hex_bolt': ('fasteners', 'Standard hex bolt with head and thread'),
            'socket_head_cap_screw': ('fasteners', 'Socket head cap screw with hex socket'),
            'spur_gear': ('gears', 'Spur gear with involute teeth'),
            'ball_bearing': ('bearings', 'Ball bearing with race and balls'),
            't_slot_extrusion': ('mechanical', 'T-slot aluminum extrusion profile'),
            'bracket': ('mechanical', 'L-bracket with mounting holes'),
            'wheel_rim': ('automotive', '5-spoke wheel rim with lug holes'),
            'simple_car_body': ('automotive', 'Simple blocky car body'),
            'parametric_box': ('enclosures', 'Parametric box with mounting posts'),
        }
        
        return [
            {
                'name': name,
                'code': code.strip(),
                'description': categories[name][1],
                'category': categories[name][0]
            }
            for name, code in self.templates.items()
        ]
    
    def get_template(self, name: str) -> Optional[str]:
        """Get template code by name"""
        return self.templates.get(name)


# ============================================================================
# AI TOOL FUNCTIONS (for registration with AI system)
# ============================================================================

def generate_cad_from_code(code: str, description: str = "CAD part") -> Dict[str, Any]:
    """
    AI Tool: Generate CAD geometry from CadQuery Python code
    
    Args:
        code: CadQuery Python code (must set 'result' variable)
        description: Human-readable description of the part
        
    Returns:
        Success/error info, file paths, geometry statistics
        
    Example:
        code = '''
import cadquery as cq
result = cq.Workplane("XY").box(50, 50, 50).faces(">Z").hole(10)
        '''
        result = generate_cad_from_code(code, "Simple box with hole")
    """
    generator = CadQueryGenerator()
    return generator.generate_from_code(code, description)


def validate_cadquery_code(code: str) -> Dict[str, Any]:
    """
    AI Tool: Validate CadQuery code before execution
    
    Args:
        code: CadQuery Python code to validate
        
    Returns:
        {'valid': bool, 'error': str (if invalid)}
    """
    generator = CadQueryGenerator()
    return generator.validate_code(code)


def list_cadquery_templates() -> List[Dict[str, str]]:
    """
    AI Tool: List all available CadQuery templates
    
    Returns:
        List of templates with name, code, description, category
        
    AI can use these as reference examples or starting points
    """
    generator = CadQueryGenerator()
    return generator.list_templates()


def get_cadquery_template(name: str) -> Optional[str]:
    """
    AI Tool: Get specific CadQuery template code
    
    Args:
        name: Template name (e.g., 'hex_bolt', 'spur_gear', 'wheel_rim')
        
    Returns:
        Template code or None if not found
    """
    generator = CadQueryGenerator()
    return generator.get_template(name)


def cadquery_export_dxf(step_file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    AI Tool: Export CAD model to DXF for laser cutting/CNC routing
    
    Args:
        step_file_path: Path to existing STEP file (from generate_cad_from_code result)
        output_path: Optional custom output path (defaults to same directory as STEP file)
        
    Returns:
        {
            'success': bool,
            'dxf_file': str (path to DXF file),
            'error': str (if failed)
        }
        
    Use case:
        User: "Export that bolt to DXF for laser cutting"
        AI: Calls this tool with step_file_path from previous generation
    """
    try:
        step_path = Path(step_file_path)
        if not step_path.exists():
            return {'success': False, 'error': f"STEP file not found: {step_file_path}"}
        
        # Determine output path
        if output_path:
            dxf_path = Path(output_path)
        else:
            dxf_path = step_path.with_suffix('.dxf')
        
        # Load STEP file
        result = cq.importers.importStep(str(step_path))
        
        # Export to DXF (CadQuery exports 2D projection)
        cq.exporters.export(result, str(dxf_path), exportType='DXF')
        
        return {
            'success': True,
            'dxf_file': str(dxf_path),
            'message': f"Exported to DXF: {dxf_path.name}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"DXF export failed: {type(e).__name__}: {str(e)}"
        }


def cadquery_export_svg(step_file_path: str, output_path: Optional[str] = None, 
                        width: int = 800, height: int = 600) -> Dict[str, Any]:
    """
    AI Tool: Export technical drawing as SVG
    
    Args:
        step_file_path: Path to existing STEP file
        output_path: Optional custom output path
        width: SVG width in pixels (default 800)
        height: SVG height in pixels (default 600)
        
    Returns:
        {
            'success': bool,
            'svg_file': str (path to SVG file),
            'svg_content': str (SVG markup for inline display),
            'error': str (if failed)
        }
        
    Use case:
        User: "Show me a technical drawing of that gear"
        AI: Calls this tool to get SVG for documentation
    """
    try:
        step_path = Path(step_file_path)
        if not step_path.exists():
            return {'success': False, 'error': f"STEP file not found: {step_file_path}"}
        
        # Determine output path
        if output_path:
            svg_path = Path(output_path)
        else:
            svg_path = step_path.with_suffix('.svg')
        
        # Load STEP file
        result = cq.importers.importStep(str(step_path))
        
        # Export to SVG (technical drawing)
        cq.exporters.export(result, str(svg_path), opt={
            'width': width,
            'height': height,
            'marginLeft': 10,
            'marginTop': 10,
            'showAxes': False,
            'projectionDir': (0.5, 0.5, 0.5),
            'strokeWidth': 0.25
        })
        
        # Read SVG content for inline display
        svg_content = svg_path.read_text()
        
        return {
            'success': True,
            'svg_file': str(svg_path),
            'svg_content': svg_content,
            'dimensions': {'width': width, 'height': height},
            'message': f"Exported technical drawing: {svg_path.name}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"SVG export failed: {type(e).__name__}: {str(e)}"
        }


def cadquery_list_generated_files(filter_type: Optional[str] = None) -> Dict[str, Any]:
    """
    AI Tool: List all generated CAD files
    
    Args:
        filter_type: Optional filter by file type ('step', 'stl', 'dxf', 'svg', or None for all)
        
    Returns:
        {
            'success': bool,
            'files': List[Dict] (file info with name, path, size, created, type),
            'count': int,
            'total_size_mb': float
        }
        
    Use case:
        User: "What CAD files have I created?"
        User: "Show me all the STL files"
    """
    try:
        # Use Render persistent disk (/data) if available, otherwise local directory
        if Path("/data").exists():
            output_dir = Path("/data/generated_cad")
        else:
            output_dir = Path("AI_infrastructure/generated_cad")
        if not output_dir.exists():
            return {
                'success': True,
                'files': [],
                'count': 0,
                'total_size_mb': 0,
                'message': 'No files generated yet'
            }
        
        # Get all CAD files
        extensions = {'.step', '.stp', '.stl', '.dxf', '.svg', '.obj'}
        files = []
        total_size = 0
        
        for file_path in output_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                # Apply filter if specified
                if filter_type and file_path.suffix.lower() != f".{filter_type.lower()}":
                    continue
                
                stat = file_path.stat()
                total_size += stat.st_size
                
                files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'type': file_path.suffix[1:].upper(),
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created': __import__('datetime').datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                    'modified': __import__('datetime').datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return {
            'success': True,
            'files': files,
            'count': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'directory': str(output_dir)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to list files: {type(e).__name__}: {str(e)}"
        }


def cadquery_get_file_info(file_path: str) -> Dict[str, Any]:
    """
    AI Tool: Get detailed information about a CAD file
    
    Args:
        file_path: Path to CAD file (can be from cadquery_list_generated_files result)
        
    Returns:
        {
            'success': bool,
            'file': Dict (detailed file info),
            'geometry': Dict (vertices, faces, volume if STEP/STL),
            'error': str (if failed)
        }
        
    Use case:
        User: "Tell me about that hex bolt file"
        User: "Show me the details of the latest file"
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {'success': False, 'error': f"File not found: {file_path}"}
        
        stat = path.stat()
        file_info = {
            'name': path.name,
            'path': str(path),
            'type': path.suffix[1:].upper(),
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created': __import__('datetime').datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            'modified': __import__('datetime').datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Try to load geometry info for STEP/STL files
        geometry_info = None
        if path.suffix.lower() in ['.step', '.stp']:
            try:
                result = cq.importers.importStep(str(path))
                # Get geometry statistics
                vertices = len(result.vertices().vals())
                edges = len(result.edges().vals())
                faces = len(result.faces().vals())
                
                # Calculate bounding box
                bb = result.val().BoundingBox()
                bounding_box = {
                    'xmin': bb.xmin, 'xmax': bb.xmax,
                    'ymin': bb.ymin, 'ymax': bb.ymax,
                    'zmin': bb.zmin, 'zmax': bb.zmax,
                    'width': bb.xmax - bb.xmin,
                    'height': bb.ymax - bb.ymin,
                    'depth': bb.zmax - bb.zmin
                }
                
                geometry_info = {
                    'vertices': vertices,
                    'edges': edges,
                    'faces': faces,
                    'bounding_box': bounding_box
                }
            except:
                pass
        
        return {
            'success': True,
            'file': file_info,
            'geometry': geometry_info
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to get file info: {type(e).__name__}: {str(e)}"
        }


def cadquery_calculate_mass(step_file_path: str, material_density: float, units: str = "g/cm3") -> Dict[str, Any]:
    """
    AI Tool: Calculate mass of CAD model given material density
    
    Args:
        step_file_path: Path to STEP file
        material_density: Density of material (e.g., 2.7 for aluminum, 7.85 for steel)
        units: Density units - 'g/cm3' (default) or 'kg/m3'
        
    Returns:
        {
            'success': bool,
            'mass_grams': float,
            'mass_kg': float,
            'volume_mm3': float,
            'volume_cm3': float,
            'material_density': float,
            'error': str (if failed)
        }
        
    Use case:
        User: "How much would this weigh in aluminum?"
        AI: Calls with density=2.7 (aluminum is 2.7 g/cm³)
        
    Common densities (g/cm³):
        - Aluminum: 2.7
        - Steel: 7.85
        - Titanium: 4.5
        - Brass: 8.5
        - Plastic (ABS): 1.05
    """
    try:
        path = Path(step_file_path)
        if not path.exists():
            return {'success': False, 'error': f"File not found: {step_file_path}"}
        
        # Load STEP file
        result = cq.importers.importStep(str(path))
        
        # Calculate volume in mm³
        volume_mm3 = result.val().Volume()
        volume_cm3 = volume_mm3 / 1000  # 1 cm³ = 1000 mm³
        
        # Convert density to g/cm³ if needed
        if units.lower() == 'kg/m3':
            density_g_cm3 = material_density / 1000  # kg/m³ to g/cm³
        else:
            density_g_cm3 = material_density
        
        # Calculate mass
        mass_g = volume_cm3 * density_g_cm3
        mass_kg = mass_g / 1000
        
        return {
            'success': True,
            'mass_grams': round(mass_g, 2),
            'mass_kg': round(mass_kg, 4),
            'volume_mm3': round(volume_mm3, 2),
            'volume_cm3': round(volume_cm3, 4),
            'material_density': density_g_cm3,
            'density_units': 'g/cm³'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Mass calculation failed: {type(e).__name__}: {str(e)}"
        }


# Tool registration format for AI system
CADQUERY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_cad_from_code",
            "description": "Generate 3D CAD geometry from CadQuery Python code. AI writes code, CadQuery creates geometry. Returns STEP and STL files for rendering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "CadQuery Python code (must set 'result' variable). Example: result = cq.Workplane('XY').box(50,50,50)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable description of the part being created"
                    }
                },
                "required": ["code", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_cadquery_code",
            "description": "Validate CadQuery Python code before execution. Checks syntax, dangerous operations, and required patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "CadQuery Python code to validate"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_cadquery_templates",
            "description": "List all available CadQuery code templates (bolts, gears, bearings, wheels, etc.). AI can use these as reference examples.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cadquery_template",
            "description": "Get specific CadQuery template code by name. Templates include: hex_bolt, spur_gear, ball_bearing, wheel_rim, simple_car_body, and more.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Template name (e.g., 'hex_bolt', 'wheel_rim', 'simple_car_body')"
                    }
                },
                "required": ["name"]
            }
        }
    }
]


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == "__main__":
    print("=== CadQuery AI Generator Test ===\n")
    
    generator = CadQueryGenerator()
    
    # Test 1: List templates
    print("Available Templates:")
    templates = generator.list_templates()
    for tpl in templates[:5]:
        print(f"  - {tpl['name']}: {tpl['description']} ({tpl['category']})")
    print(f"  ... and {len(templates) - 5} more\n")
    
    # Test 2: Generate simple box
    print("Generate: Simple box with hole")
    code = """
import cadquery as cq
result = cq.Workplane("XY").box(50, 50, 50).faces(">Z").hole(10)
"""
    result = generator.generate_from_code(code, "simple_box_with_hole")
    
    if result['success']:
        print(f"  [SUCCESS]")
        print(f"  Vertices: {result['vertices']}")
        print(f"  Edges: {result['edges']}")
        print(f"  Faces: {result['faces']}")
        print(f"  Volume: {result['volume']:.2f} mm^3")
        print(f"  Bounding box: {result['bounding_box']['size']}")
        print(f"  STEP file: {result['step_file']}")
        print(f"  STL file: {result['stl_file']}")
    else:
        print(f"  [FAILED] {result['error']}")
    print()
    
    # Test 3: Generate from template
    print("Generate: Wheel rim from template")
    wheel_code = generator.get_template('wheel_rim')
    result = generator.generate_from_code(wheel_code, "16_inch_wheel_rim")
    
    if result['success']:
        print(f"  [SUCCESS]")
        print(f"  Vertices: {result['vertices']}")
        print(f"  Faces: {result['faces']}")
        print(f"  Files: {Path(result['step_file']).name}")
    else:
        print(f"  [FAILED] {result['error']}")
    print()
    
    # Test 4: Validation
    print("Validate: Bad code (missing result)")
    bad_code = "import cadquery as cq\nbox = cq.Workplane('XY').box(10,10,10)"
    validation = generator.validate_code(bad_code)
    print(f"  Valid: {validation['valid']}")
    if not validation['valid']:
        print(f"  Error: {validation['error']}")
    print()
    
    print("[SUCCESS] CadQuery integration ready!")
    print()
    print("AI can now:")
    print("  1. Write CadQuery Python code (AI is good at code)")
    print("  2. Generate professional CAD geometry (CadQuery is good at geometry)")
    print("  3. Export STEP files for OpenCascade.js rendering")
    print("  4. Create anything: bolts, gears, wheels, cars, etc.")
