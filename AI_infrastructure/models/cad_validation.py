"""
Pydantic Validation Models for CAD Visualization
Based on OpenAI Structured Outputs + Plotly AI best practices
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional, List, Dict, Any, Union
from enum import Enum
import re


class CameraPosition(BaseModel):
    """3D camera position"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")


class CameraTarget(BaseModel):
    """3D camera target (can be at origin)"""
    x: float = Field(default=0, description="X coordinate")
    y: float = Field(default=0, description="Y coordinate")
    z: float = Field(default=0, description="Z coordinate")


class Dimensions(BaseModel):
    """3D dimensions with positive validation"""
    width: float = Field(gt=0, description="Width in meters")
    height: float = Field(gt=0, description="Height in meters")
    depth: float = Field(gt=0, description="Depth in meters")
    
    @field_validator('width', 'height', 'depth')
    @classmethod
    def validate_positive(cls, v):
        """Ensure all dimensions are positive"""
        if v <= 0:
            raise ValueError(f"Dimension must be positive, got {v}")
        return v
    
    @field_validator('width', 'height', 'depth')
    @classmethod
    def validate_reasonable(cls, v):
        """Ensure dimensions are reasonable (not microscopic or enormous)"""
        if v < 0.001:  # 1mm minimum
            raise ValueError(f"Dimension too small: {v}m (minimum 0.001m)")
        if v > 100:  # 100m maximum
            raise ValueError(f"Dimension too large: {v}m (maximum 100m)")
        return v


class TSlotProfile(str, Enum):
    """Standard T-slot extrusion profiles"""
    PROFILE_5 = "profile-5"  # 20x20mm
    PROFILE_6 = "profile-6"  # 30x30mm
    PROFILE_8 = "profile-8"  # 40x40mm
    PROFILE_10 = "profile-10"  # 50x50mm
    SERIES_1010 = "1010"  # 1" x 1"
    SERIES_1515 = "1515"  # 1.5" x 1.5"
    SERIES_2020 = "2020"  # 2" x 2"


class Model3D(BaseModel):
    """3D geometry definition"""
    type: Literal["box", "extrusion", "parametric"] = Field(..., description="Geometry type")
    dimensions: Optional[Dimensions] = None
    profile: Optional[TSlotProfile] = None
    length: Optional[float] = Field(None, gt=0, description="Extrusion length in meters")
    position: Optional[Dict[str, float]] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation: Optional[Dict[str, float]] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    
    @field_validator('position', 'rotation')
    @classmethod
    def validate_xyz_keys(cls, v):
        """Ensure position/rotation have x, y, z keys"""
        if v and not all(k in v for k in ['x', 'y', 'z']):
            raise ValueError("Position/rotation must have x, y, z keys")
        return v


class SVGDrawing(BaseModel):
    """SVG technical drawing validation"""
    content: str = Field(..., description="SVG XML content")
    viewBox: str = Field(..., pattern=r'^\d+ \d+ \d+ \d+$', description="SVG viewBox (e.g., '0 0 800 400')")
    
    @field_validator('content')
    @classmethod
    def validate_svg_format(cls, v):
        """Ensure SVG starts with proper tag and has no escaped quotes"""
        if not v.strip().startswith('<svg'):
            raise ValueError("SVG content must start with <svg> tag")
        
        # Check for improperly escaped quotes
        if '\\"' in v or "\\'" in v:
            raise ValueError("SVG has escaped quotes - use viewBox=\"0 0 800 400\" not viewBox=\\\"0 0 800 400\\\"")
        
        # Ensure closing tag
        if not v.strip().endswith('</svg>'):
            raise ValueError("SVG content must end with </svg> tag")
        
        return v
    
    @field_validator('viewBox')
    @classmethod
    def validate_viewbox_format(cls, v):
        """Ensure viewBox has 4 positive numbers"""
        parts = v.split()
        if len(parts) != 4:
            raise ValueError(f"viewBox must have 4 numbers, got {len(parts)}")
        try:
            nums = [float(p) for p in parts]
            if any(n < 0 for n in nums):
                raise ValueError("viewBox values must be positive")
        except ValueError:
            raise ValueError(f"viewBox must contain numbers, got '{v}'")
        return v


class Constraints(BaseModel):
    """Engineering constraints"""
    accuracy: Optional[str] = Field(None, pattern=r'±\d+(\.\d+)?(mm|m|cm)', description="Tolerance (e.g., ±0.1mm)")
    material: Optional[str] = Field(None, description="Material specification")
    finish: Optional[str] = Field(None, description="Surface finish")
    
    @field_validator('accuracy')
    @classmethod
    def validate_tolerance_format(cls, v):
        """Ensure tolerance format is correct"""
        if v and not re.match(r'±\d+(\.\d+)?(mm|m|cm)', v):
            raise ValueError(f"Tolerance must be in format ±0.1mm, got '{v}'")
        return v


class CADVisualization(BaseModel):
    """Complete CAD visualization with full validation"""
    type: Literal["constrained_engineering_cad", "parametric_cad", "concept_sketch"] = Field(
        ..., description="Type of CAD visualization"
    )
    model3D: Model3D = Field(..., description="3D geometry definition")
    technical_drawing: Optional[SVGDrawing] = Field(None, description="2D technical drawing")
    camera: Optional[Dict[str, CameraPosition]] = Field(
        default_factory=lambda: {
            "position": {"x": 1.5, "y": 1.5, "z": 1.5},  # Isometric default
            "target": {"x": 0, "y": 0, "z": 0}
        },
        description="Camera position (default isometric view)"
    )
    constraints: Optional[Constraints] = Field(None, description="Engineering constraints")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @model_validator(mode='after')
    def validate_complete_cad(self):
        """Cross-field validation"""
        model3d = self.model3D
        cad_type = self.type
        
        # Parametric CAD requires profile
        if cad_type == "parametric_cad" and model3d and not model3d.profile:
            raise ValueError("Parametric CAD requires a profile specification")
        
        # Extrusion requires length
        if model3d and model3d.type == "extrusion" and not model3d.length:
            raise ValueError("Extrusion type requires length parameter")
        
        # Box requires dimensions
        if model3d and model3d.type == "box" and not model3d.dimensions:
            raise ValueError("Box type requires dimensions")
        
        return self
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "type": "parametric_cad",
                "model3D": {
                    "type": "extrusion",
                    "profile": "profile-5",
                    "length": 0.5,
                    "position": {"x": 0, "y": 0, "z": 0},
                    "rotation": {"x": 0, "y": 0, "z": 0}
                },
                "technical_drawing": {
                    "content": '<svg viewBox="0 0 800 400">...</svg>',
                    "viewBox": "0 0 800 400"
                },
                "camera": {
                    "position": {"x": 1.5, "y": 1.5, "z": 1.5},
                    "target": {"x": 0, "y": 0, "z": 0}
                },
                "constraints": {
                    "accuracy": "±0.1mm",
                    "material": "Aluminum 6061-T6",
                    "finish": "Anodized"
                }
            }
        }


# Progressive Refinement Models
class CADTypeStep(BaseModel):
    """Step 1: Get CAD type and profile"""
    type: Literal["constrained_engineering_cad", "parametric_cad", "concept_sketch"]
    profile: Optional[TSlotProfile] = None
    description: str = Field(..., description="Brief description of what to create")


class CADDimensionsStep(BaseModel):
    """Step 2: Get dimensions and parameters"""
    dimensions: Optional[Dimensions] = None
    length: Optional[float] = Field(None, gt=0)
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})


class CADRenderingStep(BaseModel):
    """Step 3: Get rendering details"""
    camera_position: CameraPosition = Field(
        default=CameraPosition(x=1.5, y=1.5, z=1.5),
        description="Camera position (default isometric)"
    )
    camera_target: CameraTarget = Field(
        default_factory=CameraTarget,
        description="Camera target"
    )
    include_technical_drawing: bool = Field(default=True, description="Include 2D drawing")
    constraints: Optional[Constraints] = None


def validate_cad_json(data: Dict[str, Any]) -> Union[CADVisualization, List[str]]:
    """
    Validate CAD JSON data using Pydantic
    
    Returns:
        CADVisualization if valid, List[str] of errors if invalid
    """
    try:
        return CADVisualization(**data)
    except Exception as e:
        return [str(e)]


def lint_cad_visualization(cad_json: Dict[str, Any]) -> List[str]:
    """
    Lint CAD visualization for common AI errors
    Based on Plotly AI best practices
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check model3D exists
    if 'model3D' not in cad_json:
        errors.append("Missing required field: model3D")
        return errors
    
    model3d = cad_json['model3D']
    
    # Check dimensions are positive
    if 'dimensions' in model3d:
        dims = model3d['dimensions']
        for key in ['width', 'height', 'depth']:
            if key in dims and dims[key] <= 0:
                errors.append(f"Dimension {key} must be positive, got {dims[key]}")
    
    # Check SVG format if present
    if 'technical_drawing' in cad_json:
        svg_content = cad_json['technical_drawing']
        if isinstance(svg_content, dict):
            svg = svg_content.get('content', '')
        else:
            svg = svg_content
            
        if svg:
            if 'viewBox=\\"' in svg or "viewBox=\\'" in svg:
                errors.append("SVG has escaped quotes - use viewBox=\"0 0 800 400\" not viewBox=\\\"0 0 800 400\\\"")
            
            if not svg.strip().startswith('<svg'):
                errors.append("SVG must start with <svg> tag")
            
            if not svg.strip().endswith('</svg>'):
                errors.append("SVG must end with </svg> tag")
    
# Check camera position  
        if 'camera' in cad_json:
            cam = cad_json['camera']
            if 'position' in cam:
                pos = cam['position']
                if pos.get('x') == 0 and pos.get('y') == 0 and pos.get('z') == 0:
                    errors.append("Camera position at origin (0,0,0) - set isometric view (e.g., x:1.5, y:1.5, z:1.5)")
    
    # Check for reasonable values
    if 'model3D' in cad_json and 'length' in cad_json['model3D']:
        length = cad_json['model3D']['length']
        if length and (length < 0.001 or length > 100):
            errors.append(f"Length {length}m is unreasonable (expected 0.001-100m)")
    
    return errors


# Template library (from research: Plotly uses templates for consistency)
CAD_TEMPLATES = {
    "t_slot_beam": {
        "type": "parametric_cad",
        "model3D": {
            "type": "extrusion",
            "profile": "profile-5",
            "length": "{length}",
            "position": {"x": 0, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0}
        },
        "camera": {
            "position": {"x": 1.5, "y": 1.5, "z": 1.5},
            "target": {"x": 0, "y": 0, "z": 0}
        }
    },
    "simple_box": {
        "type": "constrained_engineering_cad",
        "model3D": {
            "type": "box",
            "dimensions": {
                "width": "{width}",
                "height": "{height}",
                "depth": "{depth}"
            },
            "position": {"x": 0, "y": 0, "z": 0},
            "rotation": {"x": 0, "y": 0, "z": 0}
        },
        "camera": {
            "position": {"x": 1.5, "y": 1.5, "z": 1.5},
            "target": {"x": 0, "y": 0, "z": 0}
        }
    }
}
