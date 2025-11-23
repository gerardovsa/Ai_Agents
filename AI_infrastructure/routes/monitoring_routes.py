"""
Connection Pool Monitoring Routes

Provides real-time visibility into connection pool health and statistics.
Created: November 22, 2025
Purpose: Monitor Supabase connection pool usage and detect leaks
"""

from flask import Blueprint, jsonify
from shared.database_utils import get_pool_stats, _connection_pools
import time

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/api/pool/stats', methods=['GET'])
def get_connection_pool_stats():
    """
    Get detailed connection pool statistics for all schemas
    
    Returns:
        JSON with per-pool details and aggregate statistics
        
    Example Response:
        {
            "pools": {
                "ai_infrastructure": {
                    "minconn": 5,
                    "maxconn": 20,
                    "active_estimate": 3
                },
                "sessions": { ... }
            },
            "aggregate": {
                "total_acquired": 150,
                "total_returned": 150,
                "leaked": 0,
                "pools_created": 2
            },
            "timestamp": 1732311234
        }
    """
    stats = get_pool_stats()
    
    # Add per-pool details
    pool_details = {}
    for schema_name, pool_obj in _connection_pools.items():
        try:
            # Estimate active connections (maxconn - available slots)
            # Note: ThreadedConnectionPool doesn't expose _used directly
            pool_details[schema_name] = {
                "minconn": pool_obj.minconn,
                "maxconn": pool_obj.maxconn,
                "active_estimate": "N/A (psycopg2 limitation)"
            }
        except Exception as e:
            pool_details[schema_name] = {
                "error": str(e)
            }
    
    return jsonify({
        "pools": pool_details,
        "aggregate": {
            "total_acquired": stats.get('connections_acquired', 0),
            "total_returned": stats.get('connections_returned', 0),
            "leaked": stats.get('connections_acquired', 0) - stats.get('connections_returned', 0),
            "pools_created": stats.get('pools_created', 0),
            "avg_wait_time_ms": round(stats.get('avg_wait_time', 0) * 1000, 2)
        },
        "timestamp": int(time.time())
    })


@monitoring_bp.route('/api/pool/health', methods=['GET'])
def get_pool_health():
    """
    Check connection pool health status
    
    Health Levels:
    - healthy: 0 leaked connections
    - warning: <5% leaked connections
    - critical: >=5% leaked connections
    
    Returns:
        JSON with health status and leak metrics
        
    Example Response:
        {
            "status": "healthy",
            "leaked_connections": 0,
            "leak_percentage": 0.0,
            "total_acquired": 150,
            "total_returned": 150,
            "message": "Connection pool is healthy - no leaks detected"
        }
    """
    stats = get_pool_stats()
    leaked = stats.get('connections_acquired', 0) - stats.get('connections_returned', 0)
    
    # Calculate leak percentage
    if stats.get('connections_acquired', 0) > 0:
        leak_percentage = (leaked / stats['connections_acquired']) * 100
    else:
        leak_percentage = 0.0
    
    # Determine health status
    if leaked == 0:
        status = "healthy"
        message = "Connection pool is healthy - no leaks detected"
    elif leak_percentage < 5:
        status = "warning"
        message = f"{leaked} connections leaked ({leak_percentage:.2f}%) - monitor for issues"
    else:
        status = "critical"
        message = f"{leaked} connections leaked ({leak_percentage:.2f}%) - immediate attention required"
    
    return jsonify({
        "status": status,
        "leaked_connections": leaked,
        "leak_percentage": round(leak_percentage, 2),
        "total_acquired": stats.get('connections_acquired', 0),
        "total_returned": stats.get('connections_returned', 0),
        "message": message,
        "timestamp": int(time.time())
    })


@monitoring_bp.route('/api/pool/reset-stats', methods=['POST'])
def reset_pool_stats():
    """
    Reset connection pool statistics (development/testing only)
    
    WARNING: This does NOT close connections, only resets counters
    
    Returns:
        JSON confirmation
    """
    from shared.database_utils import _pool_stats
    
    # Reset counters (keep pools active)
    _pool_stats['connections_acquired'] = 0
    _pool_stats['connections_returned'] = 0
    _pool_stats['total_wait_time'] = 0
    _pool_stats['avg_wait_time'] = 0
    
    return jsonify({
        "success": True,
        "message": "Pool statistics reset (connections remain active)",
        "timestamp": int(time.time())
    })


# Health check for load balancers
@monitoring_bp.route('/api/pool/ping', methods=['GET'])
def pool_ping():
    """
    Simple ping endpoint for load balancers
    
    Returns 200 OK if Flask app is running
    """
    return jsonify({
        "status": "ok",
        "timestamp": int(time.time())
    }), 200
