# Render API Connection Module - Documentation

## Created: October 16, 2025

## Problem Solved
Streamlit on Render couldn't connect to Flask on Render for the Stock Management Dashboard.

## Root Cause
Flask CORS configuration used wildcard pattern `'https://*.onrender.com'` which **doesn't work** in CORS. 
CORS requires **explicit origin URLs**, not wildcards.

## Files Created

### 1. `G_Folder/tools/render_api_client.py` (550+ lines)
Complete Python client for Render.com REST API with methods for:

**Services:**
- `list_services()` - List all services in account
- `get_service(service_id)` - Get detailed service info
- `get_service_by_name(name)` - Find service by name/slug
- `update_service_env_vars()` - Update environment variables
- `check_service_status()` - Get status (suspended, plan, URL, etc.)
- `get_flask_service()` - Helper for Flask service
- `get_streamlit_service()` - Helper for Streamlit service

**Deploys:**
- `list_deploys()` - Get deploy history
- `get_deploy()` - Get deploy details
- `trigger_deploy()` - Manual deploy
- `restart_service()` - Restart with cache clear

**CLI Interface:**
```bash
# List all services
python render_api_client.py --api-key rnd_xxx --list

# Check Flask service
python render_api_client.py --api-key rnd_xxx --flask

# Check Streamlit service
python render_api_client.py --api-key rnd_xxx --streamlit

# Get service details
python render_api_client.py --api-key rnd_xxx --service srv-xxxxx

# List recent deploys
python render_api_client.py --api-key rnd_xxx --deploys srv-xxxxx

# Trigger manual deploy
python render_api_client.py --api-key rnd_xxx --service srv-xxxxx --deploy --clear-cache

# Restart service
python render_api_client.py --api-key rnd_xxx --restart srv-xxxxx
```

**Environment Variable:**
Set `RENDER_API_KEY` to avoid passing `--api-key` every time.

### 2. `G_Folder/tools/test_render_connection.py` (100+ lines)
Diagnostic script that checks:
- Flask service status (suspended, plan, region, runtime)
- Streamlit service status
- Recent deploy history
- Identifies suspension issues

### 3. `G_Folder/tools/test_flask_connectivity.py` (80+ lines)
Tests actual Flask HTTP connectivity:
- Basic connectivity (GET /)
- Health check endpoint
- Stock API endpoint (/api/stock/master)
- Response headers (CORS inspection)
- Network/timeout diagnostics

### 4. `G_Folder/tools/monitor_flask_deploy.py` (80+ lines)
Real-time deploy monitoring:
- Watches for new deploys
- Shows status updates (building, updating, live)
- Auto-exits when deploy completes or fails
- 5-minute timeout with 10-second polling

## The Fix

### Before (BROKEN):
```python
ALLOWED_ORIGINS = [
    'http://localhost:8501',
    'http://127.0.0.1:8501',
    'https://*.onrender.com',  # ❌ Wildcards don't work in CORS!
]
```

### After (FIXED):
```python
ALLOWED_ORIGINS = [
    'http://localhost:8501',
    'http://127.0.0.1:8501',
    'https://inhouseprint-streamlit.onrender.com',  # ✅ Explicit URL
]

# Add specific Render Streamlit URL if provided via environment variable
if os.environ.get('STREAMLIT_URL'):
    streamlit_url = os.environ.get('STREAMLIT_URL')
    if streamlit_url not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(streamlit_url)
```

## Diagnostic Results

### Flask Service Status:
- ✅ Service ID: `srv-d3oaosbe5dus73aj45pg`
- ✅ Status: `not_suspended` (running)
- ✅ Plan: `standard` (not free tier)
- ✅ URL: https://inhouseprint-flask.onrender.com
- ✅ Region: Singapore
- ✅ Runtime: Docker

### Flask Connectivity Test:
- ✅ Basic connectivity: 200 OK (0.59s response time)
- ✅ Stock API endpoint: 200 OK (9 records returned)
- ✅ Service is live and responding

### CORS Issue Identified:
```
'access-control-allow-origin': 'http://127.0.0.1:8501'
```
Only allowing local Streamlit, not Render Streamlit URL!

## Commit Details
**Commit:** 1358758
**Message:** "Fix CORS: Add explicit Streamlit Render URL + Add Render API client module"
**Files Changed:** 4 files, 745 insertions(+), 7 deletions(-)
**Branch:** v6
**Date:** October 16, 2025

## Deployment Status
Auto-deploy triggered by GitHub push.
Deploy ID: `dep-d3oc8dk9c44c73fq9rg0`
Status: Building...

## Usage After Deploy Completes

### From Python:
```python
from render_api_client import RenderAPIClient

client = RenderAPIClient("rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu")

# Check Flask status
status = client.check_service_status("srv-d3oaosbe5dus73aj45pg")
print(f"Flask Status: {status['status']}")

# List recent deploys
deploys = client.list_deploys("srv-d3oaosbe5dus73aj45pg", limit=5)

# Trigger manual deploy if needed
deploy = client.trigger_deploy("srv-d3oaosbe5dus73aj45pg", clear_cache=True)
```

### From Command Line:
```bash
# Set API key once
export RENDER_API_KEY=rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu

# Check Flask
python G_Folder/tools/render_api_client.py --flask

# Test connectivity
python G_Folder/tools/test_flask_connectivity.py

# Monitor deploy
python G_Folder/tools/monitor_flask_deploy.py
```

## Expected Result
Once deploy completes (~3-5 minutes):
1. Flask will have updated CORS configuration
2. Streamlit on Render can connect to Flask on Render
3. Stock Management Dashboard will work
4. Error message "Flask server is not running" will disappear

## Troubleshooting

### If Still Not Working:
1. **Check STREAMLIT_URL env var in Flask:**
   ```bash
   python render_api_client.py --flask
   # Look for environment variables
   ```

2. **Verify CORS headers:**
   ```bash
   python test_flask_connectivity.py
   # Look for: 'access-control-allow-origin': 'https://inhouseprint-streamlit.onrender.com'
   ```

3. **Check Flask logs on Render:**
   - Visit: https://dashboard.render.com/web/srv-d3oaosbe5dus73aj45pg
   - Click "Logs" tab
   - Look for CORS or connection errors

4. **Verify Streamlit env vars:**
   - FLASK_URL should be: https://inhouseprint-flask.onrender.com
   - Check in Render Dashboard → Streamlit service → Environment

## API Key Security
Current API key: `rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu`

**To revoke after debugging:**
1. Go to: https://dashboard.render.com/u/settings
2. Find "Copilot Debugging" API key
3. Click "Revoke"
4. Create new key if needed for future automation

## Documentation Links
- Render API Docs: https://api-docs.render.com/
- CORS Documentation: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- Flask-CORS: https://flask-cors.readthedocs.io/

## Future Enhancements
1. Add webhook support for deploy notifications
2. Implement log streaming (currently limited by API)
3. Add metrics/monitoring endpoints
4. Create automated health check scripts
5. Add rollback functionality
6. Implement blue-green deployment patterns
