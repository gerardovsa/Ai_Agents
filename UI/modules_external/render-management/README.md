# 🚀 Render Management Module

**Version:** 1.0.0  
**Status:** ✅ Ready for Testing  
**Last Updated:** November 10, 2025

---

## Overview

Comprehensive Render cloud management module for the AI_agents platform. Provides visual dashboard for deploying, monitoring, and managing Render services.

---

## Features

### ✅ Implemented

**Services Tab:**
- View all Render services in grid layout
- Filter by service type (web, worker, cron)
- Filter by status (live, suspended, failed)
- Search services by name
- Quick actions: Deploy, View Logs, Restart
- Service status badges with real-time updates

**Deployments Tab:**
- View deployment history per service
- See deployment status, duration, commits
- Track deployment progress
- View commit messages

**Logs Tab:**
- Real-time log viewer
- Filter logs by text
- Auto-refresh mode (5-second intervals)
- Color-coded log levels (INFO, ERROR, WARN, DEBUG)
- Auto-scroll to latest logs

**Metrics Tab:**
- Service status overview
- Placeholder for CPU/Memory metrics
- Integration ready for Grafana/New Relic data

**Databases Tab:**
- Placeholder for PostgreSQL database management
- Future: Trigger backups, view connections

---

## Prerequisites

### 1. Backend API Routes Required

Create `AI_infrastructure/routes/render_routes.py`:

```python
from flask import Blueprint, jsonify, request
from tools.registry_v3 import RegistryV3

render_bp = Blueprint('render', __name__, url_prefix='/api/render')
registry = RegistryV3()

@render_bp.route('/services', methods=['GET'])
def list_services():
    try:
        result = registry.execute_tool('render_list_services', _user_id=1)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/logs', methods=['GET'])
def get_logs():
    service_id = request.args.get('service_id')
    tail = int(request.args.get('tail', 100))
    try:
        result = registry.execute_tool('render_get_service_logs', 
                                      service_id=service_id, 
                                      tail=tail,
                                      _user_id=1)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/deploys', methods=['GET'])
def list_deploys():
    service_id = request.args.get('service_id')
    limit = int(request.args.get('limit', 10))
    try:
        result = registry.execute_tool('render_get_deploys',
                                      service_id=service_id,
                                      limit=limit,
                                      _user_id=1)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/deploy', methods=['POST'])
def deploy_service():
    data = request.json
    try:
        result = registry.execute_tool('render_deploy_service',
                                      service_id=data['service_id'],
                                      commit_sha=data.get('commit_sha'),
                                      wait=data.get('wait', True),
                                      _user_id=1)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/restart', methods=['POST'])
def restart_service():
    data = request.json
    try:
        result = registry.execute_tool('render_restart_service',
                                      service_id=data['service_id'],
                                      _user_id=1)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/metrics', methods=['GET'])
def get_metrics():
    service_id = request.args.get('service_id')
    try:
        result = registry.execute_tool('render_get_service_metrics',
                                      service_id=service_id,
                                      _user_id=1)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Register in `AI_infrastructure/flask_app.py`:**
```python
from routes.render_routes import render_bp
app.register_blueprint(render_bp)
```

### 2. Render CLI Setup

**Install Render CLI:**
```powershell
# Windows
curl -L https://github.com/render-oss/cli/releases/latest/download/cli_windows_amd64.zip -o render-cli.zip
Expand-Archive render-cli.zip -DestinationPath C:\Tools\render
$env:PATH += ";C:\Tools\render"

# Authenticate
render login
```

**Or use API Key:**
```powershell
$env:RENDER_API_KEY = "your-api-key"
```

### 3. Module Registration

**Add to `UI/external/modules/manifest.json`:**
```json
{
  "modules": [
    {
      "id": "render-management",
      "name": "Render Cloud",
      "icon": "fas fa-cloud",
      "color": "#6C5CE7",
      "description": "Manage Render services - deploy, monitor, view logs, and track metrics",
      "manifestPath": "external/modules/render-management/manifest.json",
      "scriptPath": "external/modules/render-management/render-management.js",
      "enabled": true
    }
  ]
}
```

---

## Testing

### 1. Test Module Loading

```powershell
# Start AI agent server
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Open UI
# Navigate to: http://localhost:5001/UI/business-ai-platform-v2.html

# Check console for:
# "🔧 Initializing Render Management module..."
# "✅ Render Management module initialized"
```

### 2. Test Services List

1. Click Render Cloud icon in sidebar
2. Services should load automatically
3. Filter by type/status
4. Search for service names

### 3. Test Deployments

1. Click "Deployments" tab
2. Select a service from dropdown
3. View deployment history

### 4. Test Logs

1. Click "Logs" tab
2. Select a service
3. Logs should appear in viewer
4. Test filter functionality
5. Enable auto-refresh

### 5. Test Actions

1. Click "Deploy" on any service
2. Confirm deployment starts
3. Check console for progress
4. Test "Restart" button
5. Test "View Logs" quick action

---

## Configuration

**Module Settings (in manifest.json):**
```json
{
  "settings": {
    "refresh_interval": 30,       // Auto-refresh interval (seconds)
    "log_tail_lines": 100,        // Number of log lines to fetch
    "metrics_time_range": "1h"    // Metrics time window
  }
}
```

**Modify in code:**
```javascript
// render-management.js
constructor(moduleId) {
    super(moduleId);
    this.refreshInterval = 30000;  // 30 seconds
    this.logTailLines = 100;
}
```

---

## Service IDs Reference

**Your Render Services:**

| Service | ID | Type |
|---------|----|----- |
| MustCare ValorAISynergySuite | `srv-d48abiripnbc73dce5m0` | Web Service |
| AI Agents Backend | (TBD) | Web Service |

**Get IDs:**
```powershell
render services --output json
```

---

## Troubleshooting

### Module doesn't appear

**Check:**
1. Module registered in `UI/external/modules/manifest.json`
2. `enabled: true` in manifest
3. No console errors (F12)
4. File names match module ID exactly

**Fix:**
```javascript
// Check module registry
console.log(window.ModuleRegistry['render-management']);
```

### API calls fail

**Check:**
1. Flask server running (`BISTART`)
2. Render routes registered in `flask_app.py`
3. Render CLI authenticated (`render login`)
4. Network tab shows API responses

**Fix:**
```powershell
# Test API directly
curl http://localhost:5001/api/render/services

# Check Flask logs
# Look for route registration: "Registered Blueprint: render"
```

### No services loaded

**Check:**
1. Render CLI installed and in PATH
2. Authenticated: `render services` works
3. Backend routes implemented
4. Tool registry loaded

**Fix:**
```python
# Test tool directly
from tools.registry_v3 import RegistryV3
registry = RegistryV3()
result = registry.execute_tool('render_list_services', _user_id=1)
print(result)
```

### Logs not updating

**Check:**
1. Service ID is correct
2. Service is running (has logs)
3. Auto-refresh enabled
4. No console errors

**Fix:**
```javascript
// Check selected service
console.log(this.selectedService);

// Check log update interval
console.log(this.logUpdateInterval);
```

---

## Future Enhancements

### Phase 2 (Planned)
- [ ] Database backup triggers
- [ ] Connection count monitoring
- [ ] Performance graph visualization
- [ ] Custom deployment workflows
- [ ] Service scaling controls

### Phase 3 (Future)
- [ ] Cost tracking dashboard
- [ ] Alert configuration
- [ ] Auto-scaling rules
- [ ] Custom metrics integration
- [ ] Multi-service deployments

---

## Related Documentation

**AI_agents:**
- `tools/schemas/render_tools.json` - Render tool definitions
- `tools/implementations/render.py` - Render tool implementation
- `UI/module_development/Instructions.md` - Module development guide

**MustCare:**
- `render/RENDER_INTEGRATION_GUIDE.md` - Complete integration guide
- `render/RENDER_DEPLOYMENT_COMPLETE.md` - Deployment documentation
- `render/RENDER_AUTO_DEPLOY_SETUP.md` - Auto-deployment setup

**Render Docs:**
- https://render.com/docs
- https://github.com/render-oss/cli - Render CLI

---

## Support

**Issues:**
1. Check console for errors (F12)
2. Verify backend routes working
3. Test Render CLI directly
4. Check Flask logs

**Quick Fixes:**
```powershell
# Reload module
# Just refresh browser (Ctrl+F5)

# Restart Flask
BISTOP
BISTART

# Re-auth Render CLI
render login
```

---

**Created:** November 10, 2025  
**Module Type:** Cloud Management  
**Integration:** Render CLI + Public API  
**Status:** ✅ Ready for backend integration
