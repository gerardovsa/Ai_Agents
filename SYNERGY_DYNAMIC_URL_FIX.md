# Synergy Dynamic URL Detection - December 10, 2025

## Problem Statement

The Synergy tool had **hardcoded URLs** pointing to specific deployment platforms:
- `https://ai-agents-v10.onrender.com` was hardcoded as fallback
- This prevents the tool from working on other platforms (v11, v12, different domains)
- Manual configuration required for each deployment

**User Request:** "The URL should not be hardcoded... it should be globally dynamic based on the URL the platform is loaded on"

---

## Solution: Dynamic Platform Detection

### Implementation

**Files Updated:**
- ✅ `tools/implementations/synergy.py` (2 locations)
- ✅ `tools/implementations/automation.py` (2 locations)
- ✅ `tools/implementations/synergy_smart_internal_doc.py` (4 locations)

**Total:** 8 hardcoded URLs replaced with dynamic detection

---

**Changes Made:**

#### 1. Dynamic API Base URL (Lines 25-31)

**Before:**
```python
SYNERGY_API_BASE = os.getenv('API_BASE_URL', 'https://ai-agents-v10.onrender.com').rstrip('/') + '/api/synergy'
```

**After:**
```python
# Synergy backend URL - dynamically detect deployment platform
# Priority: API_BASE_URL (manual override) > RENDER_EXTERNAL_URL (auto-set by Render) > localhost
SYNERGY_API_BASE = (
    os.getenv('API_BASE_URL') or 
    os.getenv('RENDER_EXTERNAL_URL') or 
    'http://localhost:5001'
).rstrip('/') + '/api/synergy'
```

#### 2. Dynamic Dashboard URL (Lines 256-261)

**Before:**
```python
dashboard_url = os.getenv('API_BASE_URL', 'https://ai-agents-v10.onrender.com').rstrip('/')
```

**After:**
```python
# Build user message - use dynamic URL detection
dashboard_url = (
    os.getenv('API_BASE_URL') or 
    os.getenv('RENDER_EXTERNAL_URL') or 
    'http://localhost:5001'
).rstrip('/')
```

#### 3. Automation Tools Helper (automation.py)

**Before:**
```python
return os.getenv('API_BASE_URL', 'https://ai-agents-backend-singapore.onrender.com')
```

**After:**
```python
return (
    os.getenv('API_BASE_URL') or 
    os.getenv('RENDER_EXTERNAL_URL') or 
    'http://localhost:5001'
)
```

#### 4. Smart Internal Doc Tools (synergy_smart_internal_doc.py)

**Before (4 instances):**
```python
api_base_url = kwargs.get('api_base_url', os.getenv('API_BASE_URL', 'https://ai-agents-backend-singapore.onrender.com'))
```

**After:**
```python
api_base_url = kwargs.get('api_base_url', 
    os.getenv('API_BASE_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'http://localhost:5001')
```

---

## How It Works

### Priority Chain

```
1. API_BASE_URL (manual override)
   ↓
2. RENDER_EXTERNAL_URL (auto-set by Render platform)
   ↓
3. http://localhost:5001 (local development fallback)
```

### Environment Variables

| Variable | Set By | Example Value | Use Case |
|----------|--------|---------------|----------|
| `API_BASE_URL` | Manual (optional) | `https://custom-domain.com` | Override for custom domains |
| `RENDER_EXTERNAL_URL` | Render.com (automatic) | `https://ai-agents-v11.onrender.com` | Auto-detects current Render deployment |
| *(fallback)* | Code default | `http://localhost:5001` | Local development |

---

## Deployment Scenarios

### Scenario 1: Deploy to Render v11
```bash
# No configuration needed!
# Render automatically sets RENDER_EXTERNAL_URL=https://ai-agents-v11.onrender.com
# Synergy tools will use: https://ai-agents-v11.onrender.com/api/synergy
```

### Scenario 2: Deploy to Render v12
```bash
# Still no configuration needed!
# Render sets RENDER_EXTERNAL_URL=https://ai-agents-v12.onrender.com
# Synergy tools will use: https://ai-agents-v12.onrender.com/api/synergy
```

### Scenario 3: Custom Domain
```bash
# Set environment variable in Render dashboard:
API_BASE_URL=https://mycompany.ai
# Synergy tools will use: https://mycompany.ai/api/synergy
```

### Scenario 4: Local Development
```bash
# No environment variables set
# Synergy tools will use: http://localhost:5001/api/synergy
```

---

## Testing

### Local Development Test
```powershell
# Should use localhost:5001
python simple_synergy_test.py
```

### Production Test (after deployment)
```powershell
# Should auto-detect Render URL
curl https://ai-agents-v11.onrender.com/api/synergy/list
```

### Custom Domain Test
```bash
# Set custom URL
export API_BASE_URL="https://custom.domain.com"

# Should use custom URL
python simple_synergy_test.py
```

---

## Benefits

✅ **Zero Configuration** - Works on any Render deployment automatically  
✅ **Platform Agnostic** - Works on v10, v11, v12, etc. without code changes  
✅ **Custom Domain Ready** - Easy override with API_BASE_URL  
✅ **Local Development** - Automatic fallback to localhost:5001  
✅ **No Hardcoded URLs** - Truly dynamic platform detection  

---

## Migration Notes

### For Existing Deployments

**No action required!** The change is backward compatible:

- ✅ V10 deployment: `RENDER_EXTERNAL_URL` already set by Render
- ✅ V11 deployment: `RENDER_EXTERNAL_URL` already set by Render
- ✅ Local dev: Falls back to localhost:5001

### For New Deployments

**Zero configuration needed!** Just deploy:

```bash
git push origin v11  # or v12, v13, etc.
# Render auto-deploys
# Synergy tools auto-detect URL
```

---

## Related Files

### Updated Files (8 changes total)
- ✅ `tools/implementations/synergy.py` - 2 URLs updated
- ✅ `tools/implementations/automation.py` - 2 URLs updated  
- ✅ `tools/implementations/synergy_smart_internal_doc.py` - 4 URLs updated

### Documentation
- 📋 `DEPLOYMENT_CHECKLIST_SYNERGY_FIX.md` - Deployment guide (now platform-agnostic)
- 📋 `SYNERGY_BACKEND_FIX_URGENT.md` - Original cursor leak fixes
- 📋 `SYNERGY_DYNAMIC_URL_FIX.md` - This document

---

## Verification Checklist

After deployment, verify:

- [ ] `RENDER_EXTERNAL_URL` environment variable is set (Render dashboard)
- [ ] Health endpoint responds: `curl https://[auto-detected-url]/health`
- [ ] Synergy API responds: `curl https://[auto-detected-url]/api/synergy/list`
- [ ] Dashboard URL in tool responses matches deployment URL
- [ ] No hardcoded v10/v11/v12 URLs in logs

---

## Technical Details

### Why `RENDER_EXTERNAL_URL`?

Render.com automatically sets `RENDER_EXTERNAL_URL` with the **public-facing URL** of the deployment:
- Format: `https://[service-name].onrender.com`
- Always reflects current deployment
- No manual configuration needed

### Why Priority Chain?

1. **API_BASE_URL first** - Allows manual override for custom domains
2. **RENDER_EXTERNAL_URL second** - Auto-detects Render deployment
3. **localhost fallback** - Ensures local development works

### Environment Variable Behavior

Python's `os.getenv()` returns `None` if variable not set, so:
```python
os.getenv('API_BASE_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'http://localhost:5001'
```

Evaluates to:
- First non-None value in chain
- Falls through to localhost if both env vars unset

---

## Success Metrics

✅ **Zero hardcoded URLs** - All URLs dynamically detected  
✅ **Platform agnostic** - Works on any Render deployment  
✅ **No configuration overhead** - Deploy and go  
✅ **Local dev friendly** - Automatic localhost fallback  

---

**Status:** ✅ Complete  
**Date:** December 10, 2025  
**Impact:** All future deployments are platform-agnostic  
**Next Step:** Deploy to any Render platform (v11, v12, etc.) with zero configuration
