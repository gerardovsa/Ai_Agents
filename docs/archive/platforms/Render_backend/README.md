# Render Backend - API Client & Deployment Tools

**Location:** `G_Folder/Render_backend/`  
**Created:** October 16, 2025  
**Purpose:** Programmatic access to Render.com services for deployment management and monitoring

---

## 📁 Files in This Folder

### Core Module
- **`render_api_client.py`** (550+ lines)
  - Complete Python client for Render.com REST API
  - Services management (list, get, update, status)
  - Deploy management (list, trigger, monitor)
  - CLI interface for command-line usage
  - Helper methods for Flask/Streamlit services

### Diagnostic Tools
- **`test_render_connection.py`** (100+ lines)
  - Tests service status via Render API
  - Shows service details (plan, region, runtime, URL)
  - Lists recent deploy history
  - Identifies suspension issues

- **`test_flask_connectivity.py`** (80+ lines)
  - Tests actual HTTP connectivity to Flask service
  - Checks API endpoints (/api/stock/master)
  - Inspects CORS headers
  - Network/timeout diagnostics

- **`monitor_flask_deploy.py`** (80+ lines)
  - Real-time deploy progress monitoring
  - Auto-detects new deploys
  - Shows build/update status
  - Exits on completion or failure

### Documentation
- **`RENDER_API_MODULE_DOCS.md`** (300+ lines)
  - Complete usage documentation
  - API examples and patterns
  - Troubleshooting guide
  - Security notes

---

## 🚀 Quick Start

### Setup
```bash
# Set API key as environment variable (recommended)
export RENDER_API_KEY=rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu

# Or pass as parameter
API_KEY="rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
```

### Command Line Usage

```bash
cd G_Folder/Render_backend

# List all services
python render_api_client.py --api-key $API_KEY --list

# Check Flask service status
python render_api_client.py --api-key $API_KEY --flask

# Check Streamlit service status
python render_api_client.py --api-key $API_KEY --streamlit

# Get specific service details
python render_api_client.py --api-key $API_KEY --service srv-xxxxx

# List recent deploys
python render_api_client.py --api-key $API_KEY --deploys srv-xxxxx

# Trigger manual deploy
python render_api_client.py --api-key $API_KEY --service srv-xxxxx --deploy

# Trigger deploy with cache clear
python render_api_client.py --api-key $API_KEY --service srv-xxxxx --deploy --clear-cache

# Restart service (deploy + cache clear)
python render_api_client.py --api-key $API_KEY --restart srv-xxxxx
```

### Python Usage

```python
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Render_backend')

from render_api_client import RenderAPIClient

# Initialize client
client = RenderAPIClient("rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu")

# List all services
services = client.list_services()

# Get Flask service
flask_service = client.get_flask_service()
print(f"Flask Status: {flask_service['suspended']}")

# Check service status
status = client.check_service_status("srv-d3oaosbe5dus73aj45pg")
print(f"Plan: {status['plan']}")
print(f"URL: {status['url']}")

# List recent deploys
deploys = client.list_deploys("srv-d3oaosbe5dus73aj45pg", limit=5)

# Trigger deploy
deploy = client.trigger_deploy("srv-d3oaosbe5dus73aj45pg", clear_cache=True)
print(f"Deploy ID: {deploy['deploy']['id']}")

# Print formatted summary
client.print_service_summary("srv-d3oaosbe5dus73aj45pg")
```

### Diagnostic Scripts

```bash
# Test Render API connection and service status
python test_render_connection.py

# Test actual Flask HTTP connectivity
python test_flask_connectivity.py

# Monitor deploy in real-time
python monitor_flask_deploy.py
```

---

## 🔑 Service IDs

### InHousePrint Services
- **Flask:** `srv-d3oaosbe5dus73aj45pg`
  - URL: https://inhouseprint-flask.onrender.com
  - Plan: Standard ($21/mo)
  - Region: Singapore
  
- **Streamlit:** `srv-d3oal8bipnbc73fr5lf0`
  - URL: https://inhouseprint-streamlit.onrender.com
  - Plan: Free
  - Region: Singapore

---

## 📊 API Capabilities

### Services
- ✅ List all services in account
- ✅ Get detailed service information
- ✅ Find service by name/slug
- ✅ Update environment variables
- ✅ Check service status

### Deploys
- ✅ List deploy history
- ✅ Get deploy details
- ✅ Trigger manual deploys
- ✅ Clear build cache
- ✅ Monitor deploy progress

### Limitations
- ❌ Logs endpoint not fully supported via REST API (use Dashboard/CLI)
- ❌ Cannot create new services via this client (use Dashboard)
- ❌ Cannot delete services (use Dashboard)

---

## 🛠️ Common Tasks

### Restart a Stuck Service
```bash
python render_api_client.py --api-key $API_KEY --restart srv-d3oaosbe5dus73aj45pg
```

### Check Why Service is Down
```bash
# 1. Check service status
python test_render_connection.py

# 2. Check HTTP connectivity
python test_flask_connectivity.py

# 3. Check recent deploys (look for failures)
python render_api_client.py --api-key $API_KEY --deploys srv-d3oaosbe5dus73aj45pg
```

### Monitor a Deploy in Progress
```bash
python monitor_flask_deploy.py
# Watches for new deploys and shows status updates every 10 seconds
```

### Get All Service Information
```bash
python render_api_client.py --api-key $API_KEY --list
```

---

## 🔐 API Key Management

### Current API Key
- **Key:** `rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu`
- **Name:** "Copilot Debugging" (or similar)
- **Created:** October 16, 2025
- **Permissions:** Full access to all workspaces and services

### Security Best Practices
1. **Store in environment variable:**
   ```bash
   export RENDER_API_KEY=rnd_xxxxx
   ```

2. **Never commit to Git:**
   - API key is hardcoded in test scripts (temporary)
   - Remove before committing or use env vars

3. **Revoke when no longer needed:**
   - Go to: https://dashboard.render.com/u/settings
   - Find API key and click "Revoke"

4. **Rotate regularly:**
   - Create new key
   - Update scripts
   - Revoke old key

---

## 📚 Documentation Links

- **Render API Docs:** https://api-docs.render.com/
- **Render Dashboard:** https://dashboard.render.com
- **Account Settings (API Keys):** https://dashboard.render.com/u/settings
- **CORS Documentation:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- **Flask-CORS:** https://flask-cors.readthedocs.io/

---

## 🐛 Troubleshooting

### "404 Not Found" from API
- Check service ID is correct
- Verify API key has access to service
- Ensure service still exists

### "401 Unauthorized"
- API key is invalid or revoked
- Create new API key at: https://dashboard.render.com/u/settings

### Service Status Shows "suspended"
- Free tier services suspend after inactivity
- Visit service URL to wake it up
- Or upgrade to paid plan

### Deploy Stuck in "build_in_progress"
- Check Render Dashboard logs
- Build may have failed (check for errors)
- May need to manually cancel and retry

### CORS Errors in Browser
- Flask CORS configuration issue
- Check `ALLOWED_ORIGINS` in flask_triple_agent_app.py
- Verify Streamlit URL is in allowed list

---

## 🔄 Integration with Main System

### From web_ui.py (Streamlit)
```python
# Import Render client
import sys
sys.path.insert(0, 'Render_backend')
from render_api_client import RenderAPIClient

# Check if Flask is up
client = RenderAPIClient(os.environ.get('RENDER_API_KEY'))
flask_status = client.check_service_status('srv-d3oaosbe5dus73aj45pg')

if flask_status['status'] != 'not_suspended':
    st.warning("Flask service is down. Restarting...")
    client.restart_service('srv-d3oaosbe5dus73aj45pg')
```

### Automated Health Checks
Could create a cron job or GitHub Action to:
1. Ping both services every 5 minutes
2. Check deploy status
3. Auto-restart if suspended
4. Send notifications on failures

---

## 📝 Change Log

### October 16, 2025
- **Created Render API client module** (render_api_client.py)
- **Created diagnostic tools** (3 test scripts)
- **Fixed CORS issue** in Flask service
- **Organized into Render_backend folder**
- All files moved from `tools/` to `Render_backend/`

---

## 🚧 Future Enhancements

1. **Log Streaming**
   - Implement real-time log tailing
   - Parse logs for errors
   - Alert on critical issues

2. **Webhooks**
   - Listen for deploy events
   - Trigger actions on deploy completion
   - Slack/email notifications

3. **Metrics & Monitoring**
   - Track service uptime
   - Monitor response times
   - Resource usage alerts

4. **Automated Rollbacks**
   - Detect failed deploys
   - Auto-rollback to last working version
   - Health check validation

5. **Multi-Environment Support**
   - Manage dev/staging/prod separately
   - Environment-specific configurations
   - Automated promotion pipelines

---

**For detailed API documentation, see:** `RENDER_API_MODULE_DOCS.md`
