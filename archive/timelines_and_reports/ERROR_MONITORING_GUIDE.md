# Error Monitoring Quick Reference Guide

## Where to Find Errors After Fixes

### 1. **Production Logs (Render)**

**How to Access:**
```bash
# Via Render dashboard
1. Go to render.com → Your service
2. Click "Logs" tab
3. Filter by "Error" or search for "❌"

# Via Render CLI
render logs --tail 100 --service ai-agents-v10
```

**What to Look For:**
```
================================================================================
❌ UNCAUGHT EXCEPTION: TimeoutError
================================================================================
Path: /api/agent/stream/prime
Method: GET
Error: Request timeout after 120 seconds
...
```

---

### 2. **Local Development Logs**

**Terminal Output:**
After running `BISTART`, watch for:
```
➡️  POST /api/agent/start/prime
⬅️  500 POST /api/agent/start/prime
❌ UNCAUGHT EXCEPTION: ...
```

**Log Levels:**
- `➡️` = Incoming request
- `⬅️ 4xx/5xx` = Error response
- `❌` = Uncaught exception
- `⚠️` = Warning
- `✅` = Success
- `ℹ️` = Info

---

### 3. **Browser Console (Frontend)**

**How to Access:**
```
F12 → Console tab
```

**What to Look For:**
```javascript
═══════════════════════════════════════════════════
❌ [STREAM ERROR RECEIVED]
═══════════════════════════════════════════════════
Error Type: TimeoutError
Error Category: TIMEOUT
Error Message: Request timeout after 120 seconds
User Message: Request timed out. Try a simpler request.
...
```

---

### 4. **UI Error Display**

Users will now see formatted error boxes in the chat interface:

**Example - Timeout Error:**
```
┌─────────────────────────────────────────┐
│ ⏱️  TIMEOUT                             │
│                                         │
│ Request timed out. The AI service took  │
│ too long to respond. Please try:       │
│ • Simplifying your request              │
│ • Breaking it into smaller parts        │
│ • Trying again in a moment              │
│                                         │
│ Error Type: TimeoutError                │
│ Round: 2                                │
└─────────────────────────────────────────┘
```

**Example - Rate Limit:**
```
┌─────────────────────────────────────────┐
│ 🚦 RATE LIMIT                           │
│                                         │
│ Rate limit exceeded. Please wait a      │
│ moment and try again.                   │
└─────────────────────────────────────────┘
```

---

## Common Error Categories

| Icon | Category | Description | User Action |
|------|----------|-------------|-------------|
| ⏱️ | TIMEOUT | Request took >120s | Try simpler request |
| 🚦 | RATE_LIMIT | Too many requests | Wait and retry |
| 📦 | REQUEST_TOO_LARGE | Message/conversation too big | Shorten message |
| 🔒 | AUTH_ERROR | Authentication failed | Re-login or contact support |
| ❌ | UNKNOWN | Other errors | Report to support |

---

## Monitoring Checklist

### Daily Monitoring (Production)

- [ ] Check Render logs for any ❌ symbols
- [ ] Review error frequency by category
- [ ] Check if any users reported blank screens
- [ ] Verify OAuth connection persistence

### Weekly Monitoring

- [ ] Review error patterns (which endpoints?)
- [ ] Check stream completion rate (target: 98%+)
- [ ] Verify timeout errors are being caught
- [ ] Check OAuth session persistence (target: 95%+)

### Monthly Monitoring

- [ ] Analyze error trends over time
- [ ] Review user-reported vs logged errors
- [ ] Update error messages based on user feedback
- [ ] Optimize timeout thresholds if needed

---

## Debugging Specific Issues

### Issue: "Users still seeing blank screens"

**Check:**
1. **Browser Console**: Are errors being logged?
   ```javascript
   // Should see:
   ═══════════════════════════════════════
   ❌ [STREAM ERROR RECEIVED]
   ```
   
2. **Server Logs**: Is backend sending error events?
   ```
   ❌ UNCAUGHT EXCEPTION: ...
   ```

3. **Network Tab**: Is SSE connection closing prematurely?
   - Check "EventStream" requests
   - Look for early disconnects

**Fix Priority:**
- If backend logs show errors → Frontend not handling them (check prime_ai_chat.js deployed)
- If frontend shows errors → Good! Error visibility achieved
- If neither show errors → Network issue (check CORS, SSE headers)

---

### Issue: "OAuth disconnects on browser refresh"

**Check:**
1. **Database**: Are OAuth credentials stored?
   ```sql
   SELECT * FROM ai_infrastructure.user_platform_credentials 
   WHERE user_id = X AND platform = 'google';
   ```

2. **JWT Token**: Does it include oauth_connected?
   ```javascript
   // Decode JWT (jwt.io)
   {
     "oauth_connected": true,
     "google_connected": true
   }
   ```

3. **Session**: Is session.permanent = True?
   ```python
   # In oauth_routes.py line 256
   session.permanent = True  # Should be present
   ```

**Fix Priority:**
- If DB missing credentials → OAuth flow not completing
- If JWT missing flags → Deploy oauth_routes.py fix
- If session not permanent → Deploy session.permanent fix

---

### Issue: "Timeout errors not showing in UI"

**Check:**
1. **Backend Error Event**: Is backend sending error_category?
   ```python
   # combined_agent_worker.py should send:
   {
     'type': 'error',
     'error_category': 'TIMEOUT',
     'user_message': '...'
   }
   ```

2. **Frontend Parsing**: Is frontend checking error_category?
   ```javascript
   // prime_ai_chat.js line ~1580
   const errorCategory = data.error_category || 'Unknown';
   ```

3. **UI Display**: Is error box showing?
   - Check for `<div style="color: #ef4444"...>` in DOM

**Fix Priority:**
- If backend not sending category → Deploy combined_agent_worker.py fix
- If frontend not parsing → Deploy prime_ai_chat.js fix  
- If UI not rendering → Check CSS/DOM manipulation

---

## Quick Commands

### View Live Production Logs
```bash
# Render CLI
render logs --tail 100 --service ai-agents-v10 --follow

# Filter for errors only
render logs --tail 500 --service ai-agents-v10 | grep "❌"

# Count errors by type
render logs --tail 1000 --service ai-agents-v10 | grep "Error Type:" | sort | uniq -c
```

### Local Development Logging
```bash
# Start Flask with verbose logging
cd AI_agents/AI_infrastructure
BISTART

# In separate terminal, monitor logs
tail -f flask_output.log | grep -E "(❌|⚠️|🚦)"
```

### Database Queries for Monitoring
```sql
-- Check OAuth connection status
SELECT 
    user_id, 
    platform, 
    is_active, 
    updated_at 
FROM ai_infrastructure.user_platform_credentials 
WHERE updated_at > NOW() - INTERVAL '24 hours';

-- Check recent error patterns (if implemented)
SELECT 
    error_type, 
    COUNT(*) as count, 
    MAX(timestamp) as last_seen 
FROM ai_infrastructure.error_log 
WHERE timestamp > NOW() - INTERVAL '7 days' 
GROUP BY error_type 
ORDER BY count DESC;
```

---

## Success Indicators

### ✅ Fixes Working Properly When:

1. **Error Visibility**: Every error shows in either:
   - Server logs (backend errors)
   - Browser console (frontend errors)  
   - UI error messages (user-facing)

2. **No Blank Screens**: Users never see:
   - Empty chat with no error message
   - Infinite loading with no feedback
   - Silent failures with no logs

3. **OAuth Persistence**: Users:
   - Remain logged in after browser restart
   - See "Connected to Google" status persist
   - Don't need to re-authenticate daily

4. **Helpful Error Messages**: Errors show:
   - Clear category (Timeout, Rate Limit, etc.)
   - Actionable user message
   - Technical details in console for debugging

---

## Escalation Path

### When to Investigate Further

**Level 1 - User Reports Issue**:
1. Ask user to check browser console (F12)
2. Check server logs for user's session
3. Verify error appears in both places

**Level 2 - Pattern Detected**:
1. Multiple users report same issue
2. Error frequency increases suddenly
3. Specific endpoint consistently failing

**Level 3 - Critical Issue**:
1. All requests failing (>50% error rate)
2. Production deployment broken
3. OAuth completely non-functional

---

## Related Documentation

- [Main Fixes Documentation](./STREAMING_ERROR_FIXES_DEC3_2025.md)
- [Pool Cleanup Fix](./POOL_CLEANUP_FIX_DEC3_2025.md)
- [Flask App Architecture](./AI_infrastructure/README.md)

---

**Last Updated**: December 3, 2025  
**Next Review**: December 10, 2025
