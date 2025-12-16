"""
Professional Verification API Server
=====================================

Lightweight Flask API for verification engine - perfect for Docker deployment.

ENDPOINTS:
    GET  /health                     - Health check
    POST /api/verify                 - Run verification
    GET  /api/report/:report_id      - Get report
    POST /api/risk-score             - Calculate risk score only

USAGE:
    python api_server.py
    curl http://localhost:5001/health

DOCKER:
    docker-compose up api
    curl http://localhost:5001/health

CREATED: December 16, 2025
"""

from flask import Flask, request, jsonify
from verification_engine import VerificationEngine
from report_generator import ReportGenerator
import logging
import os
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# In-memory report storage (use Redis/DB in production)
reports = {}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'module': 'professional-verification',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/verify', methods=['POST'])
def verify_candidate():
    """
    Run verification workflow.
    
    Request Body:
    {
        "profession": "software_engineer",
        "results": {
            "parse_resume": {"result": {...}},
            "verify_github_profile": {"result": {...}},
            ...
        }
    }
    
    Response:
    {
        "report_id": "uuid",
        "risk_assessment": {...},
        "red_flags": [...],
        "recommendations": [...]
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        profession = data.get('profession', 'default')
        results = data.get('results', {})
        
        if not results:
            return jsonify({'error': 'No verification results provided'}), 400
        
        # Initialize engine
        logger.info(f"Starting verification for profession: {profession}")
        engine = VerificationEngine(profession=profession)
        
        # Add results
        for tool_name, result in results.items():
            engine.add_result(tool_name, result)
        
        # Calculate risk
        risk_assessment = engine.calculate_risk_score()
        logger.info(f"Risk score: {risk_assessment['overall_score']}/100")
        
        # Detect red flags
        red_flags = engine.detect_red_flags()
        logger.info(f"Detected {len(red_flags)} red flags")
        
        # Generate report
        generator = ReportGenerator(engine)
        report = generator.compile_report()
        
        # Store report
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        reports[report_id] = report
        
        # Return summary
        return jsonify({
            'report_id': report_id,
            'risk_assessment': risk_assessment,
            'red_flags': red_flags,
            'recommendations': report['recommendations'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    Get full report by ID.
    
    Query Parameters:
        format=json|html (default: json)
    
    Response:
        Full report data
    """
    try:
        if report_id not in reports:
            return jsonify({'error': 'Report not found'}), 404
        
        report = reports[report_id]
        format_type = request.args.get('format', 'json')
        
        if format_type == 'html':
            # Generate HTML
            generator = ReportGenerator(None)
            generator.report_data = report
            html = generator._generate_html_report()
            return html, 200, {'Content-Type': 'text/html'}
        else:
            # Return JSON
            return jsonify(report)
        
    except Exception as e:
        logger.error(f"Report retrieval error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/risk-score', methods=['POST'])
def calculate_risk_score():
    """
    Calculate risk score only (lightweight endpoint).
    
    Request Body:
    {
        "profession": "software_engineer",
        "results": {
            "parse_resume": {"result": {...}},
            ...
        }
    }
    
    Response:
    {
        "overall_score": 45.3,
        "risk_level": "Medium",
        "confidence": 85.0,
        "category_scores": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        profession = data.get('profession', 'default')
        results = data.get('results', {})
        
        # Initialize engine
        engine = VerificationEngine(profession=profession)
        
        # Add results
        for tool_name, result in results.items():
            engine.add_result(tool_name, result)
        
        # Calculate risk only
        risk_assessment = engine.calculate_risk_score()
        
        return jsonify(risk_assessment)
        
    except Exception as e:
        logger.error(f"Risk score error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/professions', methods=['GET'])
def list_professions():
    """List available profession templates"""
    return jsonify({
        'professions': list(VerificationEngine.PROFESSION_TEMPLATES.keys()),
        'default': 'default'
    })


@app.route('/api/test', methods=['GET'])
def run_test():
    """Run a test verification (for Docker health checks)"""
    try:
        engine = VerificationEngine('software_engineer')
        
        # Add minimal test data
        engine.add_result('parse_resume', {
            'result': {
                'name': 'Test User',
                'ai_detection': {'is_ai_generated': False, 'confidence': 10}
            }
        })
        
        risk = engine.calculate_risk_score()
        
        return jsonify({
            'status': 'ok',
            'test_result': 'passed',
            'risk_score': risk['overall_score']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Professional Verification API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
