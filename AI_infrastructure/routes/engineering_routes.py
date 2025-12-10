"""
Engineering Design Routes - Flask API
Endpoints for AI-powered T-slot aluminum structure design
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

# Import engineering tools
try:
    from inhouse_modules.design_engineering.engineering_tools import (
        calculate_beam_deflection_tool,
        calculate_column_buckling_tool,
        generate_bed_frame_cad_tool,
        generate_workbench_cad_tool,
        get_profile_recommendations_tool,
        create_bom_with_sourcing_tool,
        analyze_full_structure_tool
    )
    TOOLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Engineering tools not available: {e}")
    TOOLS_AVAILABLE = False

engineering_bp = Blueprint('engineering', __name__, url_prefix='/api/engineering')

logger = logging.getLogger(__name__)

def require_tools(f):
    """Decorator to check if engineering tools are available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not TOOLS_AVAILABLE:
            return jsonify({
                'error': 'Engineering tools not available',
                'message': 'Design engineering module is not properly configured'
            }), 503
        return f(*args, **kwargs)
    return decorated_function


@engineering_bp.route('/health', methods=['GET'])
def health_check():
    """Check if engineering module is available"""
    return jsonify({
        'status': 'healthy' if TOOLS_AVAILABLE else 'unavailable',
        'tools_loaded': TOOLS_AVAILABLE,
        'module': 'design_engineering'
    })


@engineering_bp.route('/analyze', methods=['POST'])
@require_tools
def analyze_design():
    """
    Analyze a design from natural language description
    
    POST /api/engineering/analyze
    Body: {
        "description": "Design a bed frame...",
        "include_cad": true,
        "include_bom": true,
        "include_analysis": true
    }
    
    Returns: {
        "design": {...},
        "analysis": {...},
        "bom": {...}
    }
    """
    try:
        data = request.get_json()
        description = data.get('description')
        
        if not description:
            return jsonify({'error': 'Design description required'}), 400
        
        include_cad = data.get('include_cad', True)
        include_bom = data.get('include_bom', True)
        include_analysis = data.get('include_analysis', True)
        
        logger.info(f"Analyzing design: {description[:100]}...")
        
        # Call full structure analysis tool
        result = analyze_full_structure_tool(
            description=description,
            include_cad=include_cad,
            include_bom=include_bom
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Design analysis error: {e}", exc_info=True)
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500


@engineering_bp.route('/beam/deflection', methods=['POST'])
@require_tools
def calculate_beam():
    """
    Calculate beam deflection and stress
    
    POST /api/engineering/beam/deflection
    Body: {
        "profile_size": "40x40",
        "length_mm": 1800,
        "load_kg": 100,
        "load_type": "distributed",
        "support_type": "simply_supported"
    }
    """
    try:
        data = request.get_json()
        
        result = calculate_beam_deflection_tool(
            profile_size=data.get('profile_size', '40x40'),
            length_mm=data.get('length_mm'),
            load_kg=data.get('load_kg'),
            load_type=data.get('load_type', 'distributed'),
            support_type=data.get('support_type', 'simply_supported')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Beam calculation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/column/buckling', methods=['POST'])
@require_tools
def calculate_column():
    """
    Calculate column buckling load capacity
    
    POST /api/engineering/column/buckling
    Body: {
        "profile_size": "60x60",
        "height_mm": 2000,
        "end_fixity": "pinned-pinned"
    }
    """
    try:
        data = request.get_json()
        
        result = calculate_column_buckling_tool(
            profile_size=data.get('profile_size', '40x40'),
            height_mm=data.get('height_mm'),
            end_fixity=data.get('end_fixity', 'pinned-pinned')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Column calculation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/cad/bed-frame', methods=['POST'])
@require_tools
def generate_bed_frame():
    """
    Generate CAD for bed frame design
    
    POST /api/engineering/cad/bed-frame
    Body: {
        "length_mm": 1800,
        "width_mm": 1200,
        "profile_size": "40x40",
        "include_3d": true
    }
    """
    try:
        data = request.get_json()
        
        result = generate_bed_frame_cad_tool(
            length_mm=data.get('length_mm', 1800),
            width_mm=data.get('width_mm', 1200),
            profile_size=data.get('profile_size', '40x40'),
            include_3d=data.get('include_3d', True)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Bed frame CAD error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/cad/workbench', methods=['POST'])
@require_tools
def generate_workbench():
    """
    Generate CAD for workbench design
    
    POST /api/engineering/cad/workbench
    Body: {
        "length_mm": 2000,
        "width_mm": 800,
        "height_mm": 900,
        "leg_profile": "60x60",
        "frame_profile": "40x40"
    }
    """
    try:
        data = request.get_json()
        
        result = generate_workbench_cad_tool(
            length_mm=data.get('length_mm', 2000),
            width_mm=data.get('width_mm', 800),
            height_mm=data.get('height_mm', 900),
            leg_profile=data.get('leg_profile', '60x60'),
            frame_profile=data.get('frame_profile', '40x40')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Workbench CAD error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/profiles/recommend', methods=['POST'])
@require_tools
def recommend_profile():
    """
    Get T-slot profile recommendations
    
    POST /api/engineering/profiles/recommend
    Body: {
        "load_kg": 200,
        "span_mm": 1800,
        "application": "bed_frame"
    }
    """
    try:
        data = request.get_json()
        
        result = get_profile_recommendations_tool(
            load_kg=data.get('load_kg'),
            span_mm=data.get('span_mm'),
            application=data.get('application', 'general')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Profile recommendation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/bom/generate', methods=['POST'])
@require_tools
def generate_bom():
    """
    Generate Bill of Materials with supplier pricing
    
    POST /api/engineering/bom/generate
    Body: {
        "parts": [
            {"part_name": "40x40 T-slot", "length_mm": 1800, "quantity": 4},
            {"part_name": "M8 T-nut", "quantity": 16}
        ],
        "preferred_suppliers": ["motedis", "tnutz"]
    }
    """
    try:
        data = request.get_json()
        
        parts = data.get('parts', [])
        if not parts:
            return jsonify({'error': 'Parts list required'}), 400
        
        result = create_bom_with_sourcing_tool(
            parts=parts,
            preferred_suppliers=data.get('preferred_suppliers'),
            include_shipping=data.get('include_shipping', True)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"BOM generation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/profiles/list', methods=['GET'])
@require_tools
def list_profiles():
    """
    Get list of available T-slot profiles
    
    GET /api/engineering/profiles/list
    """
    try:
        from inhouse_modules.design_engineering.material_database import MaterialDatabase
        
        db = MaterialDatabase()
        profiles = db.get_all_profiles()
        
        return jsonify({
            'profiles': profiles,
            'count': len(profiles)
        })
        
    except Exception as e:
        logger.error(f"Profile list error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/suppliers/list', methods=['GET'])
@require_tools
def list_suppliers():
    """
    Get list of available suppliers
    
    GET /api/engineering/suppliers/list
    """
    try:
        from inhouse_modules.design_engineering.parts_sourcing import PartsSourcingEngine
        
        engine = PartsSourcingEngine()
        suppliers = engine.get_available_suppliers()
        
        return jsonify({
            'suppliers': suppliers,
            'count': len(suppliers)
        })
        
    except Exception as e:
        logger.error(f"Supplier list error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@engineering_bp.route('/materials/alloys', methods=['GET'])
@require_tools
def list_alloys():
    """
    Get list of available aluminum alloys
    
    GET /api/engineering/materials/alloys
    """
    try:
        from inhouse_modules.design_engineering.material_database import MaterialDatabase
        
        db = MaterialDatabase()
        alloys = db.get_all_alloys()
        
        return jsonify({
            'alloys': alloys,
            'count': len(alloys)
        })
        
    except Exception as e:
        logger.error(f"Alloy list error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# Error handlers
@engineering_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@engineering_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404


@engineering_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


def init_app(app):
    """Initialize engineering routes with Flask app"""
    app.register_blueprint(engineering_bp)
    logger.info("Engineering routes registered")
