# 🚀 Render Integration Complete Guide

## Overview

This guide documents all available Render integrations and how to implement them for MustCare ValorAISynergySuite and AI_agents platform.

---

## 🎯 Available Integrations

### 1. **Render CLI** (Highest Priority)
- Deploy services programmatically
- View logs in real-time
- Restart services
- Open psql sessions
- List all services

### 2. **Log Streaming** (High Priority)
- Stream logs to Better Stack, Datadog, etc.
- Persistent log storage (7+ days)
- Search and filter capabilities
- Alert on errors

### 3. **Metrics Streaming** (High Priority)
- Push metrics to Grafana, New Relic, Honeycomb
- Monitor CPU, memory, HTTP requests
- Database connection tracking
- Performance insights

### 4. **Render Public API** (Advanced)
- Full programmatic control
- Auto-scaling
- Environment variable management
- Custom deployment workflows

---

## 🔧 Implementation Status

### ✅ Completed

**Render Tools for AI Agent:**
- Location: `C:\Users\gpoli\GIT\AI_agents\tools\`
- Files:
  - `tools/schemas/render_tools.json` (8 tools)
  - `tools/implementations/render.py` (implementation)

**Tools Created:**
1. `render_deploy_service` - Deploy with commits/images
2. `render_get_service_logs` - View/filter logs
3. `render_restart_service` - Restart services
4. `render_list_services` - Inventory
5. `render_get_service_metrics` - Performance data
6. `render_scale_service` - Scale instances (API needed)
7. `render_get_deploys` - Deployment history
8. `render_postgres_backup` - Trigger backups (API needed)

### 🔄 In Progress

**Render Management UI Module:**
- Location: `C:\Users\gpoli\GIT\AI_agents\UI\external\modules\render-management\`
- Purpose: Visual dashboard for Render operations
- Features: Deploy, monitor, logs, metrics visualization

### 📋 Planned

1. **Log Streaming Setup** (Better Stack)
2. **Metrics Dashboard** (Grafana Cloud)
3. **Automatic Deployment Webhook** (MustCare)

---

## 📚 Reference Documentation

### Official Render Docs

**Log Streaming:**
- Endpoint format: `HOST:PORT` (TLS required)
- Protocol: RFC5424 syslog over TCP
- Providers: Better Stack, Datadog, Papertrail, Sumo Logic
- Setup: Dashboard → Integrations → Observability → Log Streams

**Metrics Streaming:**
- Protocol: OpenTelemetry (OTLP)
- Providers: Grafana, New Relic, Honeycomb, Datadog, Better Stack
- Metrics: CPU, memory, HTTP requests, disk usage, DB connections
- Setup: Dashboard → Integrations → Observability → Metrics Stream

**Render CLI:**
- Installation: `brew install render` or direct download
- Auth: `render login` or `RENDER_API_KEY` env var
- Non-interactive: `--output json --confirm` flags
- Commands: `services`, `deploys`, `logs`, `psql`, `ssh`

**Public API:**
- Base URL: `https://api.render.com/v1/`
- Auth: Bearer token in `Authorization` header
- Rate limits: Varies by endpoint
- Docs: `render-public-api-1.json` (in Render_backend/resources/)

---

## 🚀 Quick Start Guides

### Setup 1: Render CLI (5 minutes)

**For Windows:**
```powershell
# Download CLI
curl -L https://github.com/render-oss/cli/releases/latest/download/cli_windows_amd64.zip -o render-cli.zip
Expand-Archive render-cli.zip -DestinationPath C:\Tools\render
$env:PATH += ";C:\Tools\render"

# Login
render login

# Test
render services
```

**For AI Agent Integration:**
```powershell
# Tools already created - just load the registry
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'{len([t for t in r.tools if \"render\" in t])} Render tools loaded')"

# Start AI agent
BISTART

# Use tools
CHAT "Deploy MustCare to Render"
CHAT "Show me the last 50 logs from MustCare service"
CHAT "List all my Render services"
```

---

### Setup 2: Log Streaming to Better Stack (15 minutes)

**Step 1: Create Better Stack Account**
1. Go to https://betterstack.com/logs
2. Sign up (free tier available)
3. Create new source → Select "Render" platform

**Step 2: Get Credentials**
- Endpoint: `in.logs.betterstack.com:6514`
- Token: (shown after creating source)

**Step 3: Configure in Render**
1. Dashboard → Integrations → Observability
2. Scroll to "Log Streams"
3. Click "+ Set default"
4. Enter:
   - Log Endpoint: `in.logs.betterstack.com:6514`
   - Token: `<your-token>`
5. Save Changes

**Step 4: Verify**
- Logs should appear in Better Stack within 1-2 minutes
- Filter by service: Use `service.name:mustcare_valoraisynergysuite`

**Benefits:**
- ✅ 7+ day log retention (vs Render's instant logs)
- ✅ Full-text search
- ✅ Alerts on errors
- ✅ Multiple service logs in one place

---

### Setup 3: Metrics to Grafana Cloud (20 minutes)

**Step 1: Create Grafana Account**
1. Go to https://grafana.com
2. Sign up for free tier
3. Create new stack (or use existing)

**Step 2: Get OTLP Endpoint**
1. Grafana Portal → Your Stack → Details
2. Find "OpenTelemetry" tile → Configure
3. Copy "Endpoint for sending OTLP signals"
4. Generate new token (Password/API Token section)

**Step 3: Configure in Render**
1. Dashboard → Integrations → Observability
2. Scroll to "Metrics Stream"
3. Click "+ Add destination"
4. Select "Grafana"
5. Enter:
   - Endpoint: `<your-grafana-endpoint>`
   - API Token: `glc_<your-token>`
6. Add destination

**Step 4: Create Dashboard**
1. In Grafana, create new dashboard
2. Add panels for:
   - `render_service_memory_usage_bytes` (memory chart)
   - `render_service_cpu_time` with `rate()` (CPU usage)
   - `render_service_http_requests_total` with `rate()` (request rate)
   - `render_service_http_response_latency` (p95 latency)

**Benefits:**
- ✅ Real-time performance monitoring
- ✅ Historical trends
- ✅ Alert on threshold breaches
- ✅ Beautiful visualizations

---

## 🎯 Recommended Implementation Order

### Phase 1: Core Monitoring (This Week)

**Priority 1: Log Streaming** (15 min)
- Setup: Better Stack
- Impact: Immediate debugging capability
- Cost: Free tier (5GB/month)

**Priority 2: Render CLI** (5 min)
- Setup: Install + authenticate
- Impact: Manual control from terminal
- Cost: Free

**Priority 3: AI Agent Tools** (Already Done! ✅)
- Setup: Tools already created
- Impact: Deploy/restart via chat
- Cost: Free

### Phase 2: Visual Monitoring (Next Week)

**Priority 4: Metrics Dashboard** (20 min)
- Setup: Grafana Cloud
- Impact: Performance insights
- Cost: Free tier

**Priority 5: Render UI Module** (1-2 hours)
- Setup: Create module in AI_agents UI
- Impact: Unified dashboard
- Cost: Free

### Phase 3: Automation (Future)

**Priority 6: Auto-Deploy Webhook** (10 min)
- Already documented in: `RENDER_AUTO_DEPLOY_SETUP.md`
- Impact: Automatic deployments
- Cost: Free

**Priority 7: Smart Monitoring Agent** (2-3 hours)
- Setup: Autonomous error detection + restart
- Impact: Self-healing infrastructure
- Cost: Free

---

## 📊 Cost Analysis

| Integration | Free Tier | Paid (if needed) | Recommended |
|-------------|-----------|------------------|-------------|
| **Render CLI** | Unlimited | N/A | ✅ Free |
| **Better Stack Logs** | 5GB/month | $20/month (20GB) | ✅ Free tier sufficient |
| **Grafana Cloud** | 10k series | $49/month (Std) | ✅ Free tier sufficient |
| **Render API** | Unlimited | N/A | ✅ Free |
| **AI Agent Tools** | Unlimited | N/A | ✅ Free |

**Total Monthly Cost:** $0 (free tiers cover your needs)

---

## 🔗 Related Files

**In this repository (MustCare):**
- `render/RENDER_DEPLOYMENT_COMPLETE.md` - Deployment documentation
- `render/RENDER_AUTO_DEPLOY_SETUP.md` - Auto-deployment guide
- `render/Dockerfile.optimized` - Docker build configuration
- `render/start.sh` - Container startup script

**In AI_agents repository:**
- `tools/schemas/render_tools.json` - Render tool definitions (8 tools)
- `tools/implementations/render.py` - Render tool implementation
- `Render_backend/resources/render-public-api-1.json` - Full API spec
- `UI/external/modules/render-management/` - (To be created) UI module

---

## 🎯 Next Steps

**Immediate (Do Now):**
1. ✅ Install Render CLI on local machine
2. ✅ Test AI agent Render tools with `CHAT` command
3. 📋 Setup Better Stack log streaming (15 min)

**This Week:**
4. 📋 Setup Grafana metrics dashboard (20 min)
5. 📋 Create Render Management UI module (1-2 hours)
6. 📋 Implement auto-deploy webhook for MustCare

**Next Week:**
7. 📋 Build smart monitoring agent (auto-restart on errors)
8. 📋 Create deployment runbooks
9. 📋 Setup alerting rules (Slack/Discord)

---

## 💡 Pro Tips

**Log Streaming:**
- Use separate log streams for dev/staging/prod
- Filter by `service.name` in Better Stack
- Set up alerts for `ERROR` and `CRITICAL` levels

**Metrics:**
- Create separate dashboards per service
- Alert on: Memory > 80%, CPU > 70%, p95 latency > 2s
- Use Grafana variables for service selection

**CLI Usage:**
- Set `RENDER_API_KEY` in `.env` for automation
- Use `--output json` in scripts
- Keep CLI updated: `brew upgrade render`

**AI Agent:**
- Create shortcuts: "deploy mustcare", "show logs", "check status"
- Chain commands: "Deploy and show logs if successful"
- Schedule health checks: "Check MustCare status every hour"

---

## 🆘 Troubleshooting

**Log Streaming Not Working:**
- Check endpoint format: `HOST:PORT` (no `https://`)
- Verify TLS is enabled on provider side
- Check Render Dashboard → service → "Log Stream" section
- Wait 2-3 minutes for first logs to appear

**Metrics Not Appearing:**
- Verify OTLP endpoint is correct
- Check API token has "write" permissions
- Metrics update every 15-60 seconds
- Look for `render_*` metrics in Grafana Explore

**CLI Not Authenticating:**
- Try `render login` again (token may have expired)
- Check `~/.render/cli.yaml` exists
- Set `RENDER_API_KEY` as alternative
- Verify network connectivity

**AI Agent Tools Failing:**
- Ensure Render CLI is in PATH
- Check CLI is authenticated (`render services`)
- Verify tool registry loaded (`python -c "..."` command above)
- Check Flask logs for errors

---

**Last Updated:** November 10, 2025  
**Status:** Phase 1 Complete (CLI + Tools), Phase 2 In Progress (UI Module)  
**Next Milestone:** Log + Metrics Streaming Setup
