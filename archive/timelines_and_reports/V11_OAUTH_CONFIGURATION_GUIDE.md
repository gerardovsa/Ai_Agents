# V11 OAuth Configuration Guide

**Date:** 2026-01-15
**Purpose:** Configure OAuth credentials for V11 deployment without creating new apps

---

##  Strategy: Reuse Existing Credentials

**You do NOT need to create new Azure/Google/Xero/Shopify apps!**

Simply add the new V11 Render URL as an additional redirect URI in your existing OAuth apps. This allows both V10 and V11 to work simultaneously using the same credentials.

---

##  Step-by-Step Configuration

### 1. Microsoft 365 / Azure AD

**Portal:** https://portal.azure.com

1. Navigate to **Azure Active Directory**  **App registrations**
2. Find your existing **AI Agents** app (the one V10 uses)
3. Click **Authentication** in left menu
4. Under **Redirect URIs**, click **Add URI**
5. Add this new URL:
   \\\
   https://ai-agents-inhouse-v11.onrender.com/oauth/microsoft/callback
   \\\
6. Click **Save**
7. **Keep your existing V10 URL** - Both will work!

**Example Configuration:**
\\\
Redirect URIs:
 https://ai-agents.onrender.com/oauth/microsoft/callback (V10)
 https://ai-agents-inhouse-v11.onrender.com/oauth/microsoft/callback (V11)
 http://localhost:5001/oauth/microsoft/callback (Local development)
\\\

**Environment Variables (Copy from V10):**
\\\ash
MICROSOFT_CLIENT_ID=<same-as-v10>
MICROSOFT_CLIENT_SECRET=<same-as-v10>
MICROSOFT_TENANT_ID=<same-as-v10>
\\\

---

### 2. Google Workspace / Google Cloud

**Portal:** https://console.cloud.google.com

1. Go to **APIs & Services**  **Credentials**
2. Find your existing **OAuth 2.0 Client ID** (the one V10 uses)
3. Click the client name to edit
4. Under **Authorized redirect URIs**, click **ADD URI**
5. Add this new URL:
   \\\
   https://ai-agents-inhouse-v11.onrender.com/oauth/google/callback
   \\\
6. Click **Save**

**Example Configuration:**
\\\
Authorized redirect URIs:
 https://ai-agents.onrender.com/oauth/google/callback (V10)
 https://ai-agents-inhouse-v11.onrender.com/oauth/google/callback (V11)
 http://localhost:5001/oauth/google/callback (Local)
\\\

**Environment Variables (Copy from V10):**
\\\ash
GOOGLE_CLIENT_ID=<same-as-v10>
GOOGLE_CLIENT_SECRET=<same-as-v10>
\\\

---

### 3. Xero Accounting (If Using)

**Portal:** https://developer.xero.com

1. Go to **My Apps**
2. Select your existing **AI Agents** app
3. Click **OAuth 2.0 redirect URIs**
4. Add new URI:
   \\\
   https://ai-agents-inhouse-v11.onrender.com/oauth/xero/callback
   \\\
5. Click **Save**

**Example Configuration:**
\\\
OAuth 2.0 redirect URIs:
 https://ai-agents.onrender.com/oauth/xero/callback (V10)
 https://ai-agents-inhouse-v11.onrender.com/oauth/xero/callback (V11)
\ http://localhost:5001/oauth/xero/callback (Local)
\\\

**Environment Variables (Copy from V10):**
\\\ash
XERO_CLIENT_ID=<same-as-v10>
XERO_CLIENT_SECRET=<same-as-v10>
\\\

---

### 4. Shopify (If Using)

**Portal:** https://partners.shopify.com

1. Go to **Apps**
2. Select your existing app
3. Click **App setup**
4. Under **Allowed redirection URL(s)**, add:
   \\\
   https://ai-agents-inhouse-v11.onrender.com/oauth/shopify/callback
   \\\
5. Click **Save**

**Example Configuration:**
\\\
Allowed redirection URLs:
 https://ai-agents.onrender.com/oauth/shopify/callback (V10)
 https://ai-agents-inhouse-v11.onrender.com/oauth/shopify/callback (V11)
\\\

**Environment Variables (Copy from V10):**
\\\ash
SHOPIFY_API_KEY=<same-as-v10>
SHOPIFY_API_SECRET=<same-as-v10>
\\\

---

##  Render Environment Variables Setup

When creating your V11 Render service, **copy ALL OAuth environment variables from V10**:

### Required for All Deployments:
\\\ash
# Database
SUPABASE_URL=<copy-from-v10>
SUPABASE_KEY=<copy-from-v10>
SUPABASE_DB_PASSWORD=<copy-from-v10>
POOL_ENABLED=True

# AI Providers
ANTHROPIC_API_KEY=<copy-from-v10>
OPENAI_API_KEY=<copy-from-v10>

# Microsoft 365
MICROSOFT_CLIENT_ID=<copy-from-v10>
MICROSOFT_CLIENT_SECRET=<copy-from-v10>
MICROSOFT_TENANT_ID=<copy-from-v10>

# Google Workspace
GOOGLE_CLIENT_ID=<copy-from-v10>
GOOGLE_CLIENT_SECRET=<copy-from-v10>
\\\

### Optional (If Using):
\\\ash
# Xero
XERO_CLIENT_ID=<copy-from-v10>
XERO_CLIENT_SECRET=<copy-from-v10>

# Shopify
SHOPIFY_API_KEY=<copy-from-v10>
SHOPIFY_API_SECRET=<copy-from-v10>
SHOPIFY_STORE_NAME=<copy-from-v10>
\\\

---

##  Benefits of This Approach

1. **No New App Reviews**
   - Microsoft/Google apps don't need re-approval
   - Use existing trusted app credentials

2. **Seamless Testing**
   - V10 and V11 work simultaneously
   - Easy comparison between versions
   - Safe rollback if needed

3. **Same User Experience**
   - Users see same OAuth consent screens
   - Same app names and permissions
   - No confusion about "new app"

4. **Quick Setup**
   - Just add redirect URIs (5 minutes)
   - Copy environment variables
   - Deploy immediately

5. **Cost Effective**
   - No additional API quotas needed
   - Single app maintenance
   - Shared OAuth tokens in Supabase

---

##  Testing OAuth After Deployment

### 1. Test Microsoft 365 Login:
\\\
https://ai-agents-inhouse-v11.onrender.com

Click "Sign in with Microsoft"
 Should redirect to Microsoft login
 After auth, redirect back to V11 dashboard
\\\

### 2. Test Google Workspace:
\\\
https://ai-agents-inhouse-v11.onrender.com

Click "Sign in with Google"
 Should redirect to Google login
 After auth, redirect back to V11 dashboard
\\\

### 3. Check Stored Tokens:
Tokens are stored in Supabase table:
\\\sql
SELECT * FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 1 AND platform IN ('microsoft', 'google', 'xero', 'shopify');
\\\

---

##  Troubleshooting

### Error: "Redirect URI mismatch"
**Cause:** V11 URL not added to OAuth app
**Fix:** Double-check you added the exact URL with /oauth/<provider>/callback

### Error: "Invalid client"
**Cause:** Wrong CLIENT_ID or CLIENT_SECRET in Render
**Fix:** Copy exact values from V10 Render environment variables

### Error: "Access denied"
**Cause:** User needs to re-authorize with new redirect URI
**Fix:** Logout and login again, grant permissions

### OAuth works on V10 but not V11:
1. Check Render logs for exact error
2. Verify environment variables are set correctly
3. Confirm redirect URI matches exactly (check for typos)
4. Test localhost:5001 first to isolate Render-specific issues

---

##  Quick Reference: Redirect URI Format

**Pattern:**
\\\
https://<your-render-service-name>.onrender.com/oauth/<provider>/callback
\\\

**For V11:**
\\\
Microsoft: https://ai-agents-inhouse-v11.onrender.com/oauth/microsoft/callback
Google:    https://ai-agents-inhouse-v11.onrender.com/oauth/google/callback
Xero:      https://ai-agents-inhouse-v11.onrender.com/oauth/xero/callback
Shopify:   https://ai-agents-inhouse-v11.onrender.com/oauth/shopify/callback
\\\

---

##  When to Create NEW OAuth Apps

**Only create new apps if:**
-  Deploying for a **different client** (separate company/organization)
-  Need **different API scopes/permissions**
-  Want **isolated OAuth tokens** (don't share with V10)
-  Client requires **their own Azure AD/Google Workspace app**

**For InHouse Print V11:**  **Reuse existing credentials** (same company, same permissions)

---

##  Related Documentation

- **V11 README:** See README_V11.md
- **V10 OAuth Setup:** Check original V10 deployment docs
- **Render Deployment:** See render.yaml configuration

---

**Last Updated:** 2026-01-15
**Maintained By:** InHouse Print Team
