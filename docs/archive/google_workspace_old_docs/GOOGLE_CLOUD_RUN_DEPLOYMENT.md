# Google Cloud Run Integration - Render Deployment Guide

## 🚀 What Was Added

### 1. Implementation Files
- **Schema**: `tools/schemas/google_cloud_run_tools.json` (20 tools)
- **Implementation**: `tools/implementations/google_cloud_run.py` (15 functions, 600+ lines)

### 2. Dependencies Added to `requirements.txt`
```bash
google-cloud-run==0.10.5
google-cloud-logging==3.8.0
google-cloud-monitoring==2.16.0
```

### 3. Environment Variables Added to `render.yaml`
```yaml
- key: GOOGLE_APPLICATION_CREDENTIALS
  sync: false  # Path to service account JSON file
- key: GOOGLE_CLOUD_PROJECT
  sync: false  # GCP Project ID
```

---

## 📋 Render Deployment Steps

### Step 1: Push Changes to GitHub
```bash
cd C:\Users\gpoli\GIT\AI_agents
git add .
git commit -m "feat: Add Google Cloud Run tools (15 functions, 296 total tools)"
git push origin main
```

### Step 2: Configure Environment Variables in Render Dashboard

Go to your Render service → **Environment** tab and add:

#### Required for Cloud Run Tools:
```
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/gcp-service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

#### How to Get Service Account JSON:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Create new service account or use existing
5. Grant roles:
   - **Cloud Run Admin** (for service management)
   - **Cloud Run Invoker** (for invoking services)
   - **Logging Viewer** (for logs)
   - **Monitoring Viewer** (for metrics)
6. Create JSON key
7. Add content as **Secret File** in Render

### Step 3: Add Service Account as Secret File in Render

1. In Render dashboard, go to your service
2. Click **Environment** tab
3. Click **Add Secret File**
4. Filename: `/etc/secrets/gcp-service-account.json`
5. Paste the JSON content from Google Cloud
6. Save

### Step 4: Verify Deployment

After deployment completes:

```bash
# Test tools endpoint
curl https://your-app.onrender.com/api/agent/tools | jq '.tools[] | select(.name | contains("cloud_run"))'

# Should show 15 tools:
# - google_cloud_run_deploy_service
# - google_cloud_run_list_services
# - google_cloud_run_get_service
# - google_cloud_run_update_service
# - google_cloud_run_delete_service
# - google_cloud_run_get_service_url
# - google_cloud_run_set_traffic
# - google_cloud_run_list_revisions
# - google_cloud_run_get_service_metrics
# - google_cloud_run_get_service_logs
# - google_cloud_run_set_iam_policy
# - google_cloud_run_create_job
# - google_cloud_run_execute_job
# - google_cloud_run_list_jobs
# - google_cloud_run_get_job_executions
```

---

## 🔧 15 Cloud Run Tools Available

### Service Management (6 tools)
- **deploy_service** - Deploy containers with full config (CPU, memory, env vars, scaling)
- **list_services** - List all services (multi-region support)
- **get_service** - Get detailed service info
- **update_service** - Update image, resources, scaling
- **delete_service** - Delete services
- **get_service_url** - Get public URL endpoint

### Traffic & Revisions (2 tools)
- **set_traffic** - Traffic splitting for blue/green deployments
- **list_revisions** - View revision history

### Monitoring (2 tools)
- **get_service_metrics** - CPU, requests, latency metrics
- **get_service_logs** - Filtered log retrieval

### IAM (1 tool)
- **set_iam_policy** - Grant access permissions

### Cloud Run Jobs (4 tools)
- **create_job** - Create batch jobs
- **execute_job** - Run jobs on demand
- **list_jobs** - List all jobs
- **get_job_executions** - Execution history

---

## 🧪 Testing After Deployment

### Test 1: Tool Availability
```bash
curl -X POST https://your-app.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What Google Cloud Run tools do you have?",
    "context": {"tools_enabled": true}
  }'
```

### Test 2: List Services (requires credentials)
```bash
curl -X POST https://your-app.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List all my Cloud Run services in project my-project-id",
    "context": {"tools_enabled": true}
  }'
```

### Test 3: Deploy Service (requires credentials)
```bash
curl -X POST https://your-app.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Deploy gcr.io/my-project/my-image:latest to Cloud Run as my-service",
    "context": {"tools_enabled": true}
  }'
```

---

## 🔒 Security Notes

### Service Account Permissions (Minimum Required)
```
roles/run.admin           # Manage Cloud Run services
roles/run.invoker         # Invoke services
roles/logging.viewer      # View logs
roles/monitoring.viewer   # View metrics
```

### Best Practices
1. **Never commit** service account JSON to Git
2. **Use Render Secret Files** for credentials
3. **Rotate keys** regularly (every 90 days)
4. **Use least privilege** - only grant necessary roles
5. **Enable audit logging** in GCP Console

---

## 📊 Current Tool Count

| Platform | Tools | Status |
|----------|-------|--------|
| **Total** | **296** | ✅ All loaded |
| Google Cloud Run | 15 | ✅ NEW |
| Google Workspace | 106 | ✅ Complete |
| Gmail | 29 | ✅ Complete |
| Slack | 24 | ✅ Complete |
| WooCommerce | 29 | ✅ Complete |
| Stripe | 25 | ✅ Complete |
| Others | 68 | ✅ Complete |

---

## 🚨 Troubleshooting

### Issue: "Google Cloud Run dependencies not available"
**Solution**: Ensure `requirements.txt` includes:
```
google-cloud-run==0.10.5
google-cloud-logging==3.8.0
google-cloud-monitoring==2.16.0
```

### Issue: "Cloud Run authentication failed"
**Solutions**:
1. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Verify service account JSON is valid
3. Confirm service account has required roles
4. Check `GOOGLE_CLOUD_PROJECT` is set

### Issue: Tools not showing in `/api/agent/tools`
**Solution**: Check `agent_routes.py` priority platforms include:
```python
priority_platforms = ['slack', 'gmail', 'woocommerce', 'google_sheets', 'stripe',
                     'google_cloud_run', 'google_docs', 'google_drive', 'google_forms']
```

### Issue: "Project not found" error
**Solution**: Set `GOOGLE_CLOUD_PROJECT` environment variable to your GCP project ID

---

## 📝 Deployment Checklist

- [ ] Push code to GitHub
- [ ] Add `GOOGLE_APPLICATION_CREDENTIALS` in Render
- [ ] Add `GOOGLE_CLOUD_PROJECT` in Render
- [ ] Upload service account JSON as Secret File
- [ ] Trigger deployment in Render
- [ ] Verify 296 tools loaded (check logs)
- [ ] Test `/api/agent/tools` endpoint
- [ ] Test Cloud Run tool via chat
- [ ] Verify credentials work with actual GCP project

---

## 🎯 Next Steps

### Optional Enhancements
1. **Add more Google Cloud services**:
   - Google Cloud Functions
   - Google Cloud Storage
   - Google Cloud SQL
   - Google Kubernetes Engine

2. **Implement caching**:
   - Cache service lists
   - Cache revision history
   - Reduce API calls

3. **Add monitoring**:
   - Track tool usage
   - Monitor API quotas
   - Alert on failures

---

**Last Updated**: October 26, 2025  
**Version**: 1.0.0  
**Status**: ✅ Ready for Render Deployment
