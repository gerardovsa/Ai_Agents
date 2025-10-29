# MustCare Worker - Complete Documentation

**Last Updated:** October 23, 2025  
**Status:** ✅ Production - Fully Operational

---

## 📋 Overview

The MustCare Worker is a Cloudflare Worker that acts as a **reverse proxy** between `mustcare.valorsynergysuite.com` and the Google Cloud Run backend application. It handles CORS, request forwarding, and provides a health check endpoint.

---

## 🏗️ Architecture

```
User Browser
    ↓
mustcare.valorsynergysuite.com (Cloudflare DNS + Worker Route)
    ↓
Cloudflare Worker (mustcare-worker)
    ↓
Google Cloud Run Backend
    ↓
https://mustcare-38241773079.australia-southeast1.run.app
```

---

## 🔑 Key Configuration

### Cloudflare Account Details
- **Account ID:** `d31a1c9ec65f373f4008216c30b071cc`
- **Account Email:** Gerardo@vetsuccessacademy.com
- **Zone:** valorsynergysuite.com
- **Zone ID:** `d575f903247d1653725514134aedc208`

### Worker Details
- **Worker Name:** `mustcare-worker`
- **Worker File:** `mustcare-worker.js`
- **Workers.dev URL:** https://mustcare-worker.gerardo-d31.workers.dev
- **Custom Domain:** https://mustcare.valorsynergysuite.com

### Backend Configuration
- **Backend Type:** Google Cloud Run
- **Backend URL:** `https://mustcare-38241773079.australia-southeast1.run.app`
- **Application:** MustCare AI Platform (React SPA)
- **Authentication:** None required for Worker → Backend

### DNS Configuration
- **Record Type:** A Record (Placeholder)
- **Name:** `mustcare.valorsynergysuite.com`
- **IP Address:** `192.0.2.1` (RFC 5737 placeholder)
- **Proxy Status:** 🟠 Proxied (Orange Cloud) - **REQUIRED**
- **Record ID:** `670d25c4d426d686ce48870e5b6b0064`

### Worker Routes
- **Pattern:** `mustcare.valorsynergysuite.com/*`
- **Pattern:** `valorsynergysuite.com/*`
- **Zone:** valorsynergysuite.com

---

## 🚀 Deployment

### Prerequisites
- Node.js 14+
- Wrangler CLI installed (`npm install -g wrangler`)
- Cloudflare API Token with permissions:
  - Workers Scripts: Edit
  - Account Settings: Read

### Environment Setup
```bash
# Set API token (use CLOUDFLARE_AI_AGENT_TOKEN)
$env:CLOUDFLARE_API_TOKEN = "rHJOJCYEtkXL7IjcWfcD8mPeyozg8Da3mnLFES9M"
```

### Deploy Command
```bash
cd c:\Users\gpoli\GIT\AI_agents\Cloudflare
wrangler deploy
```

### Expected Output
```
✅ Uploaded mustcare-worker
✅ Deployed mustcare-worker triggers
   https://mustcare-worker.gerardo-d31.workers.dev
```

---

## 📝 Worker Features

### 1. Health Check Endpoint
**Endpoint:** `/health` or `/api/health`

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-23T07:35:53.321Z",
  "worker": "mustcare-api-gateway"
}
```

**Use Case:** Monitoring, uptime checks

### 2. CORS Handling
- Automatically adds CORS headers to all responses
- Handles OPTIONS preflight requests
- Headers:
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type, Authorization`

### 3. Request Proxying
- Forwards all non-health-check requests to backend
- Preserves request method, headers, and body
- Adds proxy headers:
  - `X-Forwarded-Host`
  - `X-Forwarded-Proto`
  - `X-Real-IP`
  - `X-Forwarded-For`

### 4. Error Handling
- Global try-catch wrapper
- Returns JSON error responses
- 30-second request timeout protection

---

## 🔧 Configuration Files

### `wrangler.toml`
```toml
name = "mustcare-worker"
main = "mustcare-worker.js"
compatibility_date = "2025-10-23"
account_id = "d31a1c9ec65f373f4008216c30b071cc"

[vars]
BACKEND_URL = "https://mustcare-38241773079.australia-southeast1.run.app"
ENVIRONMENT = "production"
```

### Environment Variables
- **BACKEND_URL:** Google Cloud Run endpoint
- **ENVIRONMENT:** Deployment environment identifier

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Issue 1: Error 1003 - Direct IP Access Not Allowed
**Symptom:** `Error 1003: Direct IP access not allowed`

**Cause:** 
- A record pointing to IP address conflicts with Worker route
- Backend server rejects direct IP connections

**Solution:**
1. Use placeholder A record: `192.0.2.1` with Orange Cloud
2. Ensure Worker route is configured
3. Use proper backend hostname (not IP)

✅ **Fixed:** Changed from `http://34.143.73.2` to `https://mustcare-38241773079.australia-southeast1.run.app`

---

#### Issue 2: Error 1101 - Worker Threw Exception
**Symptom:** `Error 1101: Worker threw exception`

**Cause:**
- Unhandled exceptions in Worker code
- GET requests with body parameter
- Missing error handling

**Solution:**
1. Wrap fetch logic in try-catch
2. Only add body to non-GET/HEAD requests
3. Return JSON error responses

✅ **Fixed:** Added global error handling and conditional body forwarding

---

#### Issue 3: DNS Resolution Failure
**Symptom:** `The remote name could not be resolved`

**Cause:**
- A record deleted without replacement
- DNS propagation delay

**Solution:**
1. Create placeholder A record with Orange Cloud
2. Wait 5-30 minutes for DNS propagation
3. Flush local DNS cache: `ipconfig /flushdns`

✅ **Fixed:** Created placeholder A record `192.0.2.1`

---

#### Issue 4: 404 Not Found on Backend
**Symptom:** Backend returns 404 for all requests

**Cause:**
- Wrong backend URL (using IP instead of Cloud Run URL)
- Missing Host header

**Solution:**
1. Use correct Cloud Run URL
2. Pass through forwarding headers

✅ **Fixed:** Updated to `https://mustcare-38241773079.australia-southeast1.run.app`

---

## 📊 Monitoring

### Health Check
```bash
curl https://mustcare.valorsynergysuite.com/health
```

### Check Worker Status
```bash
cd c:\Users\gpoli\GIT\AI_agents\Cloudflare
node scripts/check-workers.js
```

### Check DNS Configuration
```bash
node scripts/domain-status.js
```

### View Logs
- Cloudflare Dashboard → Workers & Pages → mustcare-worker → Logs
- Real-time logs available in dashboard

---

## 🔐 Security Notes

### API Token Management
- **Token Name:** CLOUDFLARE_AI_AGENT_TOKEN
- **Storage:** `.env` file (gitignored)
- **Permissions:** Workers Scripts Edit, Account Settings Read
- **Rotation:** Recommended every 90 days

### Backend Security
- Backend URL is public (Google Cloud Run default)
- Application handles its own authentication
- Worker does not authenticate requests
- CORS headers allow all origins

---

## 📚 Related Files

### Core Files
- `mustcare-worker.js` - Worker source code
- `wrangler.toml` - Wrangler configuration
- `.env` - Environment variables (gitignored)

### Utility Scripts (in `/scripts`)
- `check-workers.js` - List all deployed Workers
- `domain-status.js` - View DNS records
- `test-live-worker.js` - Test Worker endpoints

### Documentation (in `/docs`)
- `MUSTCARE_WORKER_DOCUMENTATION.md` - This file
- `ERROR_RESOLUTION_LOG.md` - Troubleshooting history
- `DEPLOYMENT_GUIDE.md` - Step-by-step deployment

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Deploy Worker
wrangler deploy

# Test Worker
curl https://mustcare.valorsynergysuite.com/health

# Check logs
wrangler tail mustcare-worker

# List Workers
node scripts/check-workers.js

# Check DNS
node scripts/domain-status.js
```

### Important URLs
- **Production:** https://mustcare.valorsynergysuite.com
- **Workers.dev:** https://mustcare-worker.gerardo-d31.workers.dev
- **Backend:** https://mustcare-38241773079.australia-southeast1.run.app
- **Dashboard:** https://dash.cloudflare.com/d31a1c9ec65f373f4008216c30b071cc

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review `ERROR_RESOLUTION_LOG.md`
3. Check Cloudflare Worker logs in dashboard
4. Test backend directly: `curl https://mustcare-38241773079.australia-southeast1.run.app/`

---

**Document Version:** 1.0  
**Last Verified:** October 23, 2025  
**Status:** Production Ready ✅
