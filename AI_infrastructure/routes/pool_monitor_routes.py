"""
Connection Pool Monitoring Routes
=================================

Real-time monitoring of PostgreSQL connection pool performance

ENDPOINTS:
    GET /api/pool/stats - Get pool statistics
    GET /api/pool/dashboard - HTML dashboard
    POST /api/pool/reset - Reset pool statistics
    GET /api/pool/health - Pool health check
"""

from flask import Blueprint, jsonify, render_template_string
from shared.database_utils import get_pool_stats, _connection_pools, _pool_lock, convert_sql_placeholders
import time

pool_monitor_bp = Blueprint('pool_monitor', __name__, url_prefix='/api/pool')


@pool_monitor_bp.route('/connections/live', methods=['GET'])
def get_live_connections():
    """
    Get real-time active database connections
    
    GET /api/pool/connections/live
    
    Returns:
        {
            "total_connections": 15,
            "active_queries": 3,
            "idle_connections": 12,
            "connections": [
                {
                    "pid": 12345,
                    "user": "postgres",
                    "database": "postgres",
                    "state": "active",
                    "query": "SELECT * FROM...",
                    "wait_event": null,
                    "backend_start": "2025-11-21T20:30:00",
                    "query_start": "2025-11-21T20:30:15",
                    "duration_seconds": 1.5
                }
            ]
        }
    """
    try:
        from shared.database_utils import get_connection
        
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query pg_stat_activity for all connections
        cursor.execute("""
            SELECT 
                pid,
                usename,
                datname,
                state,
                COALESCE(query, '') as query,
                wait_event_type,
                wait_event,
                backend_start,
                query_start,
                state_change,
                EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds,
                client_addr,
                application_name
            FROM pg_stat_activity
            WHERE pid != pg_backend_pid()
            AND datname IS NOT NULL
            ORDER BY query_start DESC NULLS LAST
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        connections = []
        active_queries = 0
        idle_connections = 0
        
        for row in rows:
            state = row[3] or 'unknown'
            if state == 'active':
                active_queries += 1
            elif state == 'idle':
                idle_connections += 1
            
            # Truncate long queries
            query = row[4] or ''
            if len(query) > 200:
                query = query[:200] + '...'
            
            connections.append({
                'pid': row[0],
                'user': row[1],
                'database': row[2],
                'state': state,
                'query': query,
                'wait_event_type': row[5],
                'wait_event': row[6],
                'backend_start': row[7].isoformat() if row[7] else None,
                'query_start': row[8].isoformat() if row[8] else None,
                'state_change': row[9].isoformat() if row[9] else None,
                'duration_seconds': float(row[10]) if row[10] else 0,
                'client_addr': str(row[11]) if row[11] else 'local',
                'application_name': row[12] or 'unknown'
            })
        
        return jsonify({
            'total_connections': len(connections),
            'active_queries': active_queries,
            'idle_connections': idle_connections,
            'connections': connections,
            'timestamp': time.time()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pool_monitor_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get connection pool statistics
    
    GET /api/pool/stats
    
    Returns:
        {
            "pools_created": 3,
            "connections_acquired": 1234,
            "connections_returned": 1230,
            "pool_hits": 1000,
            "pool_misses": 3,
            "total_wait_time": 12.5,
            "avg_wait_time": 0.010,
            "active_connections": 4,
            "pools": {
                "ai_infrastructure": {"min": 2, "max": 20, "active": 3},
                "sessions": {"min": 2, "max": 20, "active": 1}
            }
        }
    """
    try:
        stats = get_pool_stats()
        
        # Get per-pool details
        pool_details = {}
        with _pool_lock:
            for schema_name, pool_instance in _connection_pools.items():
                try:
                    # Get pool stats (if available)
                    pool_details[schema_name] = {
                        'min_connections': pool_instance.minconn,
                        'max_connections': pool_instance.maxconn,
                        'status': 'active'
                    }
                except Exception as e:
                    pool_details[schema_name] = {
                        'error': str(e)
                    }
        
        stats['pools'] = pool_details
        stats['timestamp'] = time.time()
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pool_monitor_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check pool health
    
    GET /api/pool/health
    
    Returns:
        {
            "healthy": true,
            "pools_active": 3,
            "avg_wait_time_ms": 10.5,
            "warnings": []
        }
    """
    try:
        stats = get_pool_stats()
        
        warnings = []
        
        # Check average wait time
        if stats['avg_wait_time'] > 0.5:  # 500ms
            warnings.append(f"High average wait time: {stats['avg_wait_time']*1000:.1f}ms")
        
        # Check connection leak
        leaked = stats['connections_acquired'] - stats['connections_returned']
        if leaked > 10:
            warnings.append(f"Possible connection leak: {leaked} connections not returned")
        
        # Check pool hit rate
        total_requests = stats['pool_hits'] + stats['pool_misses']
        if total_requests > 0:
            hit_rate = stats['pool_hits'] / total_requests
            if hit_rate < 0.8:  # Less than 80% hit rate
                warnings.append(f"Low pool hit rate: {hit_rate*100:.1f}%")
        
        healthy = len(warnings) == 0
        
        return jsonify({
            'healthy': healthy,
            'pools_active': stats['pools_created'],
            'avg_wait_time_ms': stats['avg_wait_time'] * 1000,
            'hit_rate_percent': (stats['pool_hits'] / max(1, total_requests)) * 100,
            'warnings': warnings,
            'timestamp': time.time()
        }), 200
        
    except Exception as e:
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500


@pool_monitor_bp.route('/reset', methods=['POST'])
def reset_stats():
    """
    Reset pool statistics
    
    POST /api/pool/reset
    
    Returns:
        {"success": true, "message": "Statistics reset"}
    """
    try:
        from shared.database_utils import _pool_stats
        
        _pool_stats['connections_acquired'] = 0
        _pool_stats['connections_returned'] = 0
        _pool_stats['pool_hits'] = 0
        _pool_stats['pool_misses'] = 0
        _pool_stats['total_wait_time'] = 0.0
        _pool_stats['avg_wait_time'] = 0.0
        
        return jsonify({
            'success': True,
            'message': 'Pool statistics reset successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pool_monitor_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    HTML dashboard for pool monitoring
    
    GET /api/pool/dashboard
    
    Returns: HTML page with real-time pool stats
    """
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Connection Pool Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .header .subtitle {
            opacity: 0.9;
            font-size: 16px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .card-value {
            font-size: 42px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 8px;
        }
        .card-label {
            font-size: 14px;
            color: #94a3b8;
        }
        .status-good { color: #10b981; }
        .status-warning { color: #f59e0b; }
        .status-danger { color: #ef4444; }
        .pool-list {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }
        .pool-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            background: #0f172a;
            border-radius: 8px;
            margin-bottom: 12px;
            border: 1px solid #334155;
        }
        .pool-item:last-child { margin-bottom: 0; }
        .pool-name {
            font-weight: 600;
            font-size: 16px;
        }
        .pool-stats {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #94a3b8;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-success {
            background: #10b98120;
            color: #10b981;
        }
        .badge-warning {
            background: #f59e0b20;
            color: #f59e0b;
        }
        .chart {
            background: #0f172a;
            border-radius: 8px;
            padding: 16px;
            height: 200px;
            display: flex;
            align-items: flex-end;
            gap: 8px;
            margin-top: 12px;
        }
        .bar {
            flex: 1;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px 4px 0 0;
            transition: height 0.3s ease;
            min-height: 20px;
        }
        .actions {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #334155;
            color: #e2e8f0;
        }
        .btn-secondary:hover {
            background: #475569;
        }
        .timestamp {
            text-align: center;
            color: #64748b;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔷 Connection Pool Monitor</h1>
            <div class="subtitle">Real-time PostgreSQL connection pool performance</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">Pools Created</div>
                <div class="card-value" id="pools-created">-</div>
                <div class="card-label">Total active pools</div>
            </div>

            <div class="card">
                <div class="card-title">Avg Wait Time</div>
                <div class="card-value" id="avg-wait">-</div>
                <div class="card-label">milliseconds</div>
            </div>

            <div class="card">
                <div class="card-title">Pool Hit Rate</div>
                <div class="card-value" id="hit-rate">-</div>
                <div class="card-label">efficiency score</div>
            </div>

            <div class="card">
                <div class="card-title">Active Connections</div>
                <div class="card-value" id="active-conns">-</div>
                <div class="card-label">connections in use</div>
            </div>
        </div>

        <div class="pool-list">
            <div class="card-title">Active Pools</div>
            <div id="pools-container">
                <div style="text-align: center; padding: 40px; color: #64748b;">
                    Loading pool data...
                </div>
            </div>
        </div>

        <div class="pool-list">
            <div class="card-title">Connection Activity</div>
            <div class="chart" id="activity-chart">
                <!-- Bars will be added dynamically -->
            </div>
        </div>

        <div class="actions">
            <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh</button>
            <button class="btn btn-secondary" onclick="resetStats()">🗑️ Reset Stats</button>
        </div>

        <div class="timestamp" id="timestamp">Last updated: Never</div>
    </div>

    <script>
        let activityHistory = [];

        async function fetchStats() {
            try {
                const response = await fetch('/api/pool/stats');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            }
        }

        function updateDashboard(data) {
            // Update main stats
            document.getElementById('pools-created').textContent = data.pools_created || 0;
            
            const avgWait = (data.avg_wait_time * 1000).toFixed(1);
            document.getElementById('avg-wait').textContent = avgWait;
            document.getElementById('avg-wait').className = 'card-value ' + 
                (avgWait < 50 ? 'status-good' : avgWait < 200 ? 'status-warning' : 'status-danger');
            
            const totalRequests = (data.pool_hits || 0) + (data.pool_misses || 0);
            const hitRate = totalRequests > 0 ? (data.pool_hits / totalRequests * 100).toFixed(1) : 0;
            document.getElementById('hit-rate').textContent = hitRate + '%';
            document.getElementById('hit-rate').className = 'card-value ' + 
                (hitRate > 90 ? 'status-good' : hitRate > 70 ? 'status-warning' : 'status-danger');
            
            const activeConns = (data.connections_acquired || 0) - (data.connections_returned || 0);
            document.getElementById('active-conns').textContent = activeConns;
            document.getElementById('active-conns').className = 'card-value ' + 
                (activeConns < 10 ? 'status-good' : activeConns < 50 ? 'status-warning' : 'status-danger');
            
            // Update pool list
            const poolsContainer = document.getElementById('pools-container');
            if (data.pools && Object.keys(data.pools).length > 0) {
                poolsContainer.innerHTML = '';
                Object.entries(data.pools).forEach(([name, pool]) => {
                    const poolItem = document.createElement('div');
                    poolItem.className = 'pool-item';
                    poolItem.innerHTML = `
                        <div>
                            <div class="pool-name">${name}</div>
                            <span class="badge badge-success">${pool.status || 'active'}</span>
                        </div>
                        <div class="pool-stats">
                            <div>Min: ${pool.min_connections || 2}</div>
                            <div>Max: ${pool.max_connections || 20}</div>
                        </div>
                    `;
                    poolsContainer.appendChild(poolItem);
                });
            } else {
                poolsContainer.innerHTML = '<div style="text-align: center; padding: 20px; color: #64748b;">No active pools</div>';
            }
            
            // Update activity chart
            activityHistory.push(data.connections_acquired || 0);
            if (activityHistory.length > 20) activityHistory.shift();
            
            const chartContainer = document.getElementById('activity-chart');
            const maxValue = Math.max(...activityHistory, 1);
            chartContainer.innerHTML = '';
            
            activityHistory.forEach(value => {
                const bar = document.createElement('div');
                bar.className = 'bar';
                bar.style.height = `${(value / maxValue) * 100}%`;
                chartContainer.appendChild(bar);
            });
            
            // Update timestamp
            const now = new Date().toLocaleTimeString();
            document.getElementById('timestamp').textContent = `Last updated: ${now}`;
        }

        async function refreshData() {
            await fetchStats();
        }

        async function resetStats() {
            if (confirm('Reset all pool statistics?')) {
                try {
                    await fetch('/api/pool/reset', { method: 'POST' });
                    await fetchStats();
                    alert('Statistics reset successfully');
                } catch (error) {
                    alert('Failed to reset statistics: ' + error);
                }
            }
        }

        // Auto-refresh every 2 seconds
        setInterval(fetchStats, 2000);
        
        // Initial load
        fetchStats();
    </script>
</body>
</html>
    """
    
    return render_template_string(html)
