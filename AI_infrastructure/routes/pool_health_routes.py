"""
Pool Health Metrics Dashboard API Route
========================================
Real-time view of connection pool health for debugging leaks.

Endpoints:
- GET /api/pool-health - Current pool metrics
- POST /api/pool-health/force-check - Force immediate leak check
- GET /api/pool-health/history - Historical metrics (last 24 hours)

Author: GitHub Copilot
Date: December 22, 2025
"""

from flask import Blueprint, jsonify, request
from AI_infrastructure.shared.connection_leak_detector import get_leak_detector
from AI_infrastructure.shared.database_utils import get_all_pool_stats
import logging

logger = logging.getLogger(__name__)

# Create blueprint
pool_health_bp = Blueprint('pool_health', __name__)


@pool_health_bp.route('/api/pool-health', methods=['GET'])
def get_pool_health():
    """
    Get current connection pool health metrics.
    
    Returns:
        {
            "success": true,
            "pool_stats": {
                "sessions": {"acquired": 2, "returned": 2, "leaked": 0, ...},
                "ai_infrastructure": {...},
                "user_1": {...},
                "customer_1": {...}
            },
            "leak_detector": {
                "is_running": true,
                "total_checked": 50,
                "idle_found": 2,
                "idle_closed": 2,
                "active_warned": 0,
                "errors": 0,
                "last_check": "2025-12-22T10:30:45",
                "check_interval": 60,
                "idle_timeout": 300,
                "auto_close_enabled": true
            },
            "alerts": [
                {"level": "warning", "message": "Pool 'sessions' has 2 leaked connections"},
                {"level": "critical", "message": "Pool 'ai_infrastructure' exhausted (60/60 connections used)"}
            ]
        }
    """
    try:
        # Get pool stats from database_utils
        pool_stats = get_all_pool_stats()
        
        # Get leak detector metrics
        detector = get_leak_detector()
        leak_metrics = detector.get_metrics()
        
        # Generate alerts
        alerts = []
        
        # Check for leaked connections
        for schema, stats in pool_stats.items():
            leaked = stats.get('leaked', 0)
            if leaked > 0:
                alerts.append({
                    'level': 'warning' if leaked < 5 else 'critical',
                    'message': f"Pool '{schema}' has {leaked} leaked connection(s)",
                    'schema': schema,
                    'leaked_count': leaked
                })
            
            # Check for pool exhaustion (>90% used)
            acquired = stats.get('acquired', 0)
            max_connections = stats.get('max_connections', 60)
            usage_percent = (acquired / max_connections * 100) if max_connections > 0 else 0
            
            if usage_percent > 90:
                alerts.append({
                    'level': 'critical',
                    'message': f"Pool '{schema}' nearly exhausted ({acquired}/{max_connections} = {usage_percent:.0f}%)",
                    'schema': schema,
                    'acquired': acquired,
                    'max_connections': max_connections,
                    'usage_percent': usage_percent
                })
            elif usage_percent > 75:
                alerts.append({
                    'level': 'warning',
                    'message': f"Pool '{schema}' high usage ({acquired}/{max_connections} = {usage_percent:.0f}%)",
                    'schema': schema,
                    'acquired': acquired,
                    'max_connections': max_connections,
                    'usage_percent': usage_percent
                })
        
        # Check leak detector errors
        errors = leak_metrics.get('errors', 0)
        if errors > 0:
            alerts.append({
                'level': 'warning',
                'message': f"Leak detector has {errors} error(s)",
                'error_count': errors
            })
        
        # Check if detector is running
        if not leak_metrics.get('is_running', False):
            alerts.append({
                'level': 'critical',
                'message': "Leak detector is NOT running - leaks won't be detected!",
                'action': "Call start_leak_detector() from flask_app.py"
            })
        
        return jsonify({
            'success': True,
            'pool_stats': pool_stats,
            'leak_detector': leak_metrics,
            'alerts': alerts,
            'timestamp': leak_metrics.get('last_check')
        })
        
    except Exception as e:
        logger.error(f"Failed to get pool health: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pool_health_bp.route('/api/pool-health/force-check', methods=['POST'])
def force_check():
    """
    Force immediate leak detection check.
    
    Useful for:
    - Testing leak detector
    - Debugging connection issues
    - Manual leak cleanup
    
    Returns:
        {
            "success": true,
            "message": "Forced leak check completed",
            "metrics": {...}
        }
    """
    try:
        detector = get_leak_detector()
        
        # Force immediate check
        logger.info("🔍 User requested force leak check")
        metrics = detector.force_check()
        
        return jsonify({
            'success': True,
            'message': 'Forced leak check completed',
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Failed to force leak check: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pool_health_bp.route('/api/pool-health/config', methods=['GET', 'POST'])
def manage_config():
    """
    Get or update leak detector configuration.
    
    GET returns current config:
        {
            "check_interval": 60,
            "idle_timeout": 300,
            "auto_close_enabled": true
        }
    
    POST updates config (requires restart):
        {
            "check_interval": 30,
            "idle_timeout": 180,
            "auto_close_enabled": false
        }
    """
    detector = get_leak_detector()
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'config': {
                'check_interval': detector.check_interval,
                'idle_timeout': detector.idle_timeout,
                'auto_close_enabled': detector.enable_auto_close
            }
        })
    
    else:  # POST
        try:
            data = request.get_json()
            
            # Update config (requires detector restart to take effect)
            if 'check_interval' in data:
                detector.check_interval = int(data['check_interval'])
            
            if 'idle_timeout' in data:
                detector.idle_timeout = int(data['idle_timeout'])
            
            if 'auto_close_enabled' in data:
                detector.enable_auto_close = bool(data['auto_close_enabled'])
            
            logger.info(f"Updated leak detector config: {data}")
            
            return jsonify({
                'success': True,
                'message': 'Config updated (restart detector for changes to take effect)',
                'config': {
                    'check_interval': detector.check_interval,
                    'idle_timeout': detector.idle_timeout,
                    'auto_close_enabled': detector.enable_auto_close
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@pool_health_bp.route('/api/pool-health/stats', methods=['GET'])
def get_detailed_stats():
    """
    Get detailed per-schema connection stats.
    
    Returns breakdown for each schema:
    - sessions
    - ai_infrastructure
    - user_{id}
    - customer_{id}
    
    Useful for identifying which schema is leaking.
    """
    try:
        pool_stats = get_pool_stats()
        
        # Calculate totals across all schemas
        total_acquired = sum(stats.get('acquired', 0) for stats in pool_stats.values())
        total_returned = sum(stats.get('returned', 0) for stats in pool_stats.values())
        total_leaked = sum(stats.get('leaked', 0) for stats in pool_stats.values())
        total_max = sum(stats.get('max_connections', 0) for stats in pool_stats.values())
        
        return jsonify({
            'success': True,
            'schemas': pool_stats,
            'totals': {
                'acquired': total_acquired,
                'returned': total_returned,
                'leaked': total_leaked,
                'max_connections': total_max,
                'usage_percent': (total_acquired / total_max * 100) if total_max > 0 else 0
            },
            'schema_count': len(pool_stats)
        })
        
    except Exception as e:
        logger.error(f"Failed to get detailed stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
