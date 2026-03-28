# Debugging: 400 Error on /api/agent/agent/1/start

## Problem Summary
WooCommerce V4 module's AI-driven tabs (Products, Finance, Customers, Settings) fail with HTTP 400 error when calling `/api/agent/agent/1/start`.

## Affected Code

### Frontend Call
- **File**: `UI/modules_external/woocommerce/woocommerce-v4.js`
- **Function**: `_loadAiTab(tabId, message)` (line 419-441)
- **Request**:
  ```javascript
  const data = await this.api.post('/api/agent/agent/1/start', {
      thread_slug: "woocommerce-{tabId}-user-{userId}",
      message: "Non-empty message string",
      context: { tab: 'woocommerce', action: `load_${tabId}`, tools_enabled: true }
  });
  ```

### Backend Handler
- **File**: `AI_infrastructure/routes/agent_routes_v4.py`
- **Function**: `start_agent(agent_id)` (line 698-1000)
- **Blueprint**: `agent_bp` (registered at `/api/agent` prefix in flask_app.py line 483)
- **Full Path**: `POST /api/agent/agent/<agent_id>/start`

## Validation Logic

### Explicit 400 Errors in Code
Only three places return explicit 400 errors:
1. **Line 759**: `if not thread_slug: return error_response("Missing 'thread_slug' in request", 400)`
2. **Line 762**: `if not message: return error_response("Missing 'message' in request", 400)`
3. **Line 721-723**: FileValidationError from file uploads (not applicable - WooCommerce doesn't send files)

### Request Parsing
```python
if is_form_data:
    thread_slug = request.form.get('thread_slug') or request.form.get('thread_id')
    message = request.form.get('message', '')
else:  # JSON
    data = request.json or {}
    thread_slug = data.get('thread_slug') or data.get('thread_id')
    message = data.get('message', '')
```

## Verified Information

### ✅ Module API Implementation
- `UI/shared/js/module-api.js` correctly sets:
  - `Content-Type: application/json`
  - `Authorization: Bearer {token}` (from localStorage)
  - Proper JSON.stringify() of request body
  - Error handling with message extraction

### ✅ Flask Route Registration
- Blueprint registered: `app.register_blueprint(agent_bp, url_prefix='/api/agent')`
- Route decorator: `@agent_bp.route('/agent/<agent_id>/start', methods=['POST'])`
- Final path: `/api/agent/agent/<agent_id>/start` ✓

### ✅ WooCommerce Payloads
All four AI-driven tabs send correct payloads:
- **Products**: `thread_slug="woocommerce-products-user-{userId}"`, message="Get all WooCommerce products..."
- **Customers**: `thread_slug="woocommerce-customers-user-{userId}"`, message="Get all WooCommerce customers..."
- **Finance**: `thread_slug="woocommerce-finance-user-{userId}"`, message="Get WooCommerce financial summary..."
- **Settings**: `thread_slug="woocommerce-settings-user-{userId}"`, message="Get my WooCommerce store settings..."

### ✅ Message Content
All messages are non-empty strings (verified lines 194-197 in woocommerce-v4.js)

## Likely Causes (In Order of Probability)

### 1. **Request JSON not being parsed** (MOST LIKELY)
- `request.json` might be None, causing `data = {}` and both `thread_slug` and `message` to be empty
- **Symptoms**: "Missing 'thread_slug'" or "Missing 'message'" 400 error
- **Why it could happen**:
  - Flask not recognizing Content-Type header
  - Request body encoding issue
  - Empty request body

### 2. **Module not being loaded/initialized**
- WooCommerce V4 module might not be loading at all
- `this.api` might be undefined
- ModuleAPI constructor might fail
- **Symptoms**: JavaScript error (not HTTP 400) would be logged

### 3. **FlaskJSON parsing error**
- Flask's `request.json` might throw exception that's caught somewhere
- Malformed JSON payload from client
- **Symptoms**: Would return 500 (unhandled exception), not 400

### 4. **Other Middleware Issue**
- Some other route/middleware rejecting the request before it reaches start_agent
- CORS pre-flight request failing
- **Symptoms**: 400 before validation logic runs

## Debug Steps

### Step 1: Add Logging to Agent Endpoint
Edit `AI_infrastructure/routes/agent_routes_v4.py` line 698-760:

```python
@agent_bp.route('/agent/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    """FIXED: Database as source of truth"""
    print(f"\n{'='*80}")
    print(f"[START] Agent {agent_id} - Request received")
    print(f"{'='*80}")
    
    # ADD THIS DEBUG BLOCK:
    print(f"[DEBUG] request.content_type: {request.content_type}")
    print(f"[DEBUG] request.headers: {dict(request.headers)}")
    print(f"[DEBUG] request.method: {request.method}")
    print(f"[DEBUG] request.data (first 500 bytes): {request.data[:500]}")
    print(f"[DEBUG] request.json: {request.json}")
    print(f"[DEBUG] request.form: {request.form}")
    
    try:
        # ... existing code ...
```

### Step 2: Check Flask Logs
```bash
cd AI_infrastructure
python flask_app.py 2>&1 | tee flask_debug.log
# Watch for [START] and [DEBUG] output
```

### Step 3: Test with curl
```bash
curl -X POST http://localhost:5001/api/agent/agent/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "thread_slug": "test-thread",
    "message": "Hello"
  }'
```

### Step 4: Test with Python Script
Run `test_agent_endpoint.py`:
```bash
cd AI_infrastructure
python ../test_agent_endpoint.py
```

### Step 5: Browser Console Debugging
Open browser DevTools (F12) → Network tab:
1. Click on the failing request
2. Check "Request Headers" for Content-Type and Authorization
3. Check "Request Payload" to verify JSON format
4. Check "Response" to see exact error message

## Current Hypothesis

**Most Likely**: `request.json` is returning None because Flask isn't recognizing the Content-Type header or the request body is not being properly sent by the client.

**Test to Verify**:
1. Add debug logging (Step 1)
2. Run Flask server
3. Trigger WooCommerce tab in UI
4. Check Flask logs for `[DEBUG]` output
5. If `request.json` is None, then issue is in request sending
6. If `request.json` has data, then issue is elsewhere

## Related Files
- Backend: `AI_infrastructure/routes/agent_routes_v4.py` (line 698-1000)
- Frontend: `UI/modules_external/woocommerce/woocommerce-v4.js` (line 419-441)
- API Client: `UI/shared/js/module-api.js` (line 50-90 for _request method)
- Flask App: `AI_infrastructure/flask_app.py` (line 483 for blueprint registration)

## Next Steps (If Debug Shows request.json is None)

If the debugging confirms that `request.json` is None:

1. **Check MIME Type**: Ensure ModuleAPI is setting Content-Type correctly
2. **Check Request Body**: Verify JSON.stringify is working
3. **Check Browser Network**: Inspect actual request being sent
4. **Check Flask Configuration**: Verify Flask can parse JSON (should be default)
5. **Add Request Preprocessing**: Add explicit JSON parsing middleware

## Resolution Checklist

- [ ] Add debug logging to agent endpoint
- [ ] Run Flask server and trigger error
- [ ] Capture debug output from Flask logs
- [ ] Identify root cause from debug output
- [ ] Apply appropriate fix
- [ ] Test all 4 AI-driven tabs (products, finance, customers, settings)
- [ ] Verify reports tab still works (direct API, no agent)
- [ ] Verify orders tab still works (direct API, no agent)
