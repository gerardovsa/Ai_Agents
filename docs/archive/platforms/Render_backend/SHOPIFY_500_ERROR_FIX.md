# Shopify Dashboard 500 Error Fix

## Date: October 17, 2025

## Problem

Shopify Dashboard endpoint (`/shopify-dashboard`) was returning **500 Internal Server Error** on Render.
- ✅ Worked locally (http://localhost:5000/shopify-dashboard)
- ❌ Failed on Render (https://inhouseprint-flask.onrender.com/shopify-dashboard)

## Root Cause

The Flask app tried to import `Shopify_app` module, but it wasn't in the PYTHONPATH on Render:

```python
# In flask_triple_agent_app.py (line 3955):
shopify_app_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Shopify_app')
sys.path.insert(0, shopify_app_dir)

from dashboard_routes import dashboard_bp  # ❌ ModuleNotFoundError on Render
```

The Dockerfile only had `/app` and `/app/tools` in PYTHONPATH, but not `/app/Shopify_app`.

## Fix Applied

**Updated Dockerfile** to include `Shopify_app` in PYTHONPATH:

### Before (BROKEN):
```dockerfile
ENV PYTHONPATH="/app:/app/tools:${PYTHONPATH}"
```

### After (FIXED):
```dockerfile
# Add parent directories to Python path so imports work
# Includes: /app (G_Folder root), /app/tools (utilities), /app/Shopify_app (Shopify dashboard)
ENV PYTHONPATH="/app:/app/tools:/app/Shopify_app:${PYTHONPATH}"
```

## Files Modified

1. **`G_Folder/Quote_Calculator/AI_Quote_Agent/web_interface/Dockerfile`**
   - Added `/app/Shopify_app` to PYTHONPATH
   - Added comment explaining what each path is for

## Commit Details

**Commit:** 35d5bef
**Message:** "Fix Shopify dashboard 500 error: Add Shopify_app to PYTHONPATH"
**Branch:** v6
**Date:** October 17, 2025

## Deployment Status

**Deploy ID:** dep-d3ogpgur433s73937c4g
**Status:** Building...
**ETA:** ~3-5 minutes

## Expected Result

After deploy completes:

1. **Visit:** https://inhouseprint-flask.onrender.com/shopify-dashboard
2. **Expected:** ✅ 200 OK - Dashboard loads successfully
3. **From Streamlit:** Navigate to "Shopify E-Commerce Dashboard" page → Should load iframe

## Testing

Once deploy is live, run:

```bash
cd G_Folder/Render_backend
python test_shopify_endpoint.py
```

Expected output:
```
✅ Status Code: 200
✅ SUCCESS! Page loaded successfully
   Content Length: 119384 bytes
```

## Related Files

**Shopify App Structure:**
```
G_Folder/Shopify_app/
├── dashboard_routes.py          # API endpoints for dashboard
├── flask_routes.py              # Webhook routes
├── templates/
│   └── shopify_dashboard.html  # Dashboard UI (2732 lines)
└── ...
```

**Quote Calculators:**
```
G_Folder/Quote_Calculator/
├── shopify_calculators/         # Shopify price calculators
│   ├── business_card_calculator_shopify.py
│   ├── corflute_calculator_shopify.py
│   ├── PerfectBound_Shopify_Calculator.py
│   └── ...
└── god_calculators/             # Database-driven calculators
    ├── GOD_flyer_calculator.py
    ├── GOD_perfect_bound_books_calculator.py
    └── ...
```

## Why This Happened

The Flask Dockerfile copies the entire `G_Folder` (`COPY . .`), so all files are present. However, Python couldn't import modules from `Shopify_app` because it wasn't in `sys.path`.

The code in `flask_triple_agent_app.py` tried to add it dynamically:
```python
sys.path.insert(0, shopify_app_dir)
```

But this **didn't work on Render** because the relative path calculation was incorrect in the Docker environment. Setting it in the Dockerfile with absolute paths (`/app/Shopify_app`) ensures it works reliably.

## Prevention

For any new folders that need to be imported in Flask:
1. Add to PYTHONPATH in Dockerfile: `ENV PYTHONPATH="/app:/app/tools:/app/NEW_FOLDER:${PYTHONPATH}"`
2. Test imports locally: `python -c "import NEW_FOLDER; print('✅ Works')"`
3. Verify on Render after deploy

## Monitoring

Monitor script running in background:
```bash
python G_Folder/Render_backend/monitor_flask_deploy.py
```

Will show "✅ LIVE! Deploy complete!" when ready.

## Previous Related Fixes

**October 16, 2025:**
1. Fixed CORS to allow Streamlit Render URL
2. Fixed Streamlit to use FLASK_URL env var instead of localhost
3. Created Render API client module

**Current Fix (October 17, 2025):**
4. Fixed Shopify dashboard import path (PYTHONPATH)

---

## Technical Notes

**PYTHONPATH on Docker:**
- Set at container build time via `ENV` directive
- Applies to all Python processes in the container
- More reliable than runtime `sys.path` manipulation

**Folder Structure in Docker:**
```
/app/                            # G_Folder root (WORKDIR initially)
├── Quote_Calculator/
│   ├── AI_Quote_Agent/
│   │   └── web_interface/      # Flask app location (WORKDIR changed here)
│   ├── shopify_calculators/
│   └── god_calculators/
├── Shopify_app/                # Needed in PYTHONPATH
├── tools/                      # Needed in PYTHONPATH
└── config/
```

**Import Resolution:**
When Flask runs from `/app/Quote_Calculator/AI_Quote_Agent/web_interface`:
- `from dashboard_routes import dashboard_bp` searches PYTHONPATH
- Finds it in `/app/Shopify_app/dashboard_routes.py` ✅

---

**Status:** FIX DEPLOYED - Waiting for build to complete (monitoring in progress)
